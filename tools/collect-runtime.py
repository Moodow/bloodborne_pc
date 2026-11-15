#!/usr/bin/env python3
"""把 bb-probe.exe 及其**递归**依赖的 MSYS2 DLL 打成一个包。

踩过的坑：只看 exe 的直接导入表不够。libprotobuf.dll 依赖一堆 absl 的 DLL
(libabsl_die_if_null-2608.0.0.dll 之类)，漏掉任何一个都会在启动时弹
"由于找不到 xxx.dll，无法继续执行代码"。所以这里按 BFS 递归解析每个 DLL 的导入。

用法：
  python tools/collect-runtime.py --exe out/gpu/bb-probe.exe --out dist/runtime.zip
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

OBJDUMP = os.environ.get("OBJDUMP", "llvm-objdump")
STRIP = os.environ.get("STRIP", "llvm-strip")
MSYS_BIN = os.environ.get("MSYS_BIN", "/clang64/bin")
if not os.path.isdir(MSYS_BIN):
    # Windows 上的 python 不认 /clang64，换成 C:/msys64/clang64/bin
    _root = os.environ.get("MSYS2_ROOT", "C:/msys64")
    _cand = os.path.join(_root, "clang64", "bin")
    if os.path.isdir(_cand):
        MSYS_BIN = _cand

# 系统 DLL / API Set / 显卡厂商自家二进制：不打包，用目标机自带的
SYSTEM = {
    "kernel32.dll", "user32.dll", "gdi32.dll", "advapi32.dll", "shell32.dll",
    "ole32.dll", "oleaut32.dll", "ws2_32.dll", "winmm.dll", "imm32.dll",
    "comdlg32.dll", "comctl32.dll", "setupapi.dll", "version.dll", "dwmapi.dll",
    "bcrypt.dll", "ncrypt.dll", "crypt32.dll", "secur32.dll", "shlwapi.dll",
    "dbghelp.dll", "powrprof.dll", "wintrust.dll", "d3d11.dll", "d3d12.dll",
    "dxgi.dll", "opengl32.dll", "msvcp140.dll", "vcruntime140.dll",
    "vcruntime140_1.dll", "ntdll.dll", "pdh.dll", "iphlpapi.dll",
    "d3d12core.dll", "d3d12agility.dll", "msvcrt.dll", "ucrtbase.dll",
}


def imports_of(path):
    try:
        out = subprocess.run([OBJDUMP, "-p", path], capture_output=True, text=True).stdout
    except FileNotFoundError:
        sys.exit(f"找不到 {OBJDUMP}，先把 MSYS2 clang64/bin 放进 PATH")
    names = []
    for line in out.splitlines():
        if "DLL Name:" in line:
            names.append(line.split("DLL Name:", 1)[1].strip())
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default="out/gpu/bb-probe.exe")
    ap.add_argument("--out", default="dist/runtime.zip")
    ap.add_argument("--keep", default="", help="额外要带上的文件名，逗号分隔")
    a = ap.parse_args()

    if not os.path.isfile(a.exe):
        sys.exit(f"找不到 {a.exe}")

    tmp = tempfile.mkdtemp(prefix="bbport-runtime-")
    exe_name = os.path.basename(a.exe)
    dst = os.path.join(tmp, exe_name)
    shutil.copy2(a.exe, dst)
    subprocess.run([STRIP, "--strip-unneeded", dst], check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 同一次构建出来的辅助 exe
    for helper in ("bb-gpu-capabilities.exe", "bb-fg401-capabilities.exe", "bb-play.exe"):
        src = os.path.join(os.path.dirname(a.exe), helper)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(tmp, helper))

    seen, queue, copied, missing = set(), [os.path.join(tmp, exe_name)], [], []
    for extra in filter(None, (s.strip() for s in a.keep.split(","))):
        p = os.path.join(tmp, extra)
        if os.path.isfile(p):
            queue.append(p)

    while queue:
        cur = queue.pop()
        for dll in imports_of(cur):
            key = dll.lower()
            if key in seen or key in SYSTEM or key.startswith("api-ms-win-") \
                    or key.startswith("ext-ms-"):
                continue
            seen.add(key)
            src = os.path.join(MSYS_BIN, dll)
            if not os.path.isfile(src):
                # 大小写不敏感地再找一次
                base = MSYS_BIN
                hit = next((f for f in os.listdir(base) if f.lower() == key), None) if os.path.isdir(base) else None
                src = os.path.join(base, hit) if hit else None
            if src and os.path.isfile(src):
                target = os.path.join(tmp, os.path.basename(src))
                shutil.copy2(src, target)
                copied.append(os.path.basename(src))
                queue.append(target)
            else:
                missing.append(dll)

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(os.listdir(tmp)):
            z.write(os.path.join(tmp, name), name)

    print(f"打包 {len(os.listdir(tmp))} 个文件 -> {a.out} "
          f"({os.path.getsize(a.out) / 1048576:.1f} MiB)")
    print("MSYS2 DLL:", ", ".join(sorted(copied)) or "(无)")
    if missing:
        print("未找到（应由安装包原样提供）:", ", ".join(sorted(set(missing))))
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
