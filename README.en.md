# Bloodborne for Windows (personal build)

[简体中文](README.md) · [Upstream](https://github.com/Supermedo/bloodborne_pc) · [Downloads](../../releases)

> **This is a personal fork of [Supermedo/bloodborne_pc](https://github.com/Supermedo/bloodborne_pc)**,
> maintained by an individual, not an official release. Some changes target specific situations
> and are not necessarily useful to everyone.

## The upstream project

Bloodborne running natively on Windows 10 / 11. The original PlayStation 4 game's own x86-64 code
runs directly on your PC and its graphics are translated to Vulkan — no emulator, no emulator
window, no setup scripts: unpack the zip, start `Bloodborne.exe`, pick your game folder and press
**PLAY**.

The port is by [Supermedo](https://github.com/Supermedo) (Mohammed Albarghouthi), built on
[bbport](https://github.com/deadinside28/bloodborne_pc) — deadinside28's native Linux port of
Bloodborne — and on the [shadPS4](https://github.com/shadps4-emu/shadPS4) renderer.

**No game files are included.** You need your own decrypted dump of Bloodborne, any retail edition
(US CUSA00900, EU CUSA00207, the Game of the Year editions such as CUSA03173, ...), as SELF or
plain ELF files. The community patches (60/90/unlocked FPS, resolution, effects) need version
**1.09**; other versions run at 30 FPS.

This project is not affiliated with Sony Interactive Entertainment or FromSoftware.

See the [upstream README](https://github.com/Supermedo/bloodborne_pc#features) for the full feature
set: a 13-language launcher, DLSS / FSR 3.1 / FSR 4, ML frame generation, cheats, graphics and FOV
options, keyboard and mouse mapping, save import, in-game benchmarks and launcher updates.

## What this fork changes

### 1. Online play works with the Chinese-text patch

Retail builds only produce Chinese text through the **Unlock Game Region** patch. That patch sets
the game's region to 5, indexing one past the four-entry server URL table and yielding the empty
string. `sceHttpCreateConnectionWithURL` then receives an empty URL, the connection is rejected,
and the game reports that it cannot obtain the Bloodborne server information — online play never
starts.

Every `/bb-xx/` path on the server answers the same document, so when the URL arrives without a
scheme the code falls back to the EU endpoint of the game's own host
(`https://ss4.scej-network.jp:20443/bb-eu/ss.info`). The host overrides written by `run.py` still
redirect it to the community server, so custom servers keep working.

`BB_SERVER_INFO_URL` overrides the fallback; set it to `0` to disable it.

In short: **Chinese text and online play at the same time.**

### 2. Build and release pipeline

The upstream CI does not run in this environment — `msys2-env.sh` prepends the runner's preinstalled
old MSYS2 to `PATH`, so `cp` and other coreutils resolve to binaries that fail to exec and return
127. This fork rebuilds the pipeline:

- pushes compile only `bb-probe.exe` as a fast compile check, about 5 minutes
- a `windows-v*` tag builds everything and publishes two packages automatically
- parallelism follows the real core count, ccache is reused, and failures leave diagnosable logs

Those two areas are the complete difference from upstream. Every feature comes from upstream; this
fork adds no game features.

## Downloads

Pick from [Releases](../../releases):

| File | Contents |
| --- | --- |
| `bbport-windows.zip` | **Full package**, same layout as an upstream release: launcher, four executables, all FSR runtimes and the licence files. Unpack and play. |
| `bb-probe-only.zip` | **Minimal package**: `bb-probe.exe` alone, dependencies statically linked. You supply the game folder and the way to start it; there is no graphical launcher. |

## Requirements

- Windows 10 (1903 or later) or Windows 11, 64-bit
- An Intel Core 4th generation (Haswell, 2013) or newer, or an AMD Ryzen. The game uses instructions
  of the PS4's processor (AVX, BMI1, MOVBE, LZCNT); Intel 2nd and 3rd generation run with
  translated instructions, best effort; processors without AVX (many Pentium and Celeron models)
  cannot run it
- A graphics card with Vulkan 1.3 and a current driver
- About 6 GB of free memory (RAM + page file), 10 GB for 1440p or 4K output
- DLSS: NVIDIA GeForce RTX 20 series or newer

The full package needs nothing else installed; everything the game needs is in the zip.

## How to play

1. Download from [Releases](../../releases) and unpack it anywhere
2. Start `Bloodborne.exe`. The first time, a short guide checks your game folder (the one with
   `eboot.bin`) and your PC, and sets the picture for your hardware
3. Press **PLAY**

In game, **Insert** (or **L3+R3** on a controller) opens the settings menu.

**DLC.** The Game of the Year editions already have The Old Hunters. With a base-game dump, also
dump your add-ons: each is a folder named like `SPEXPANSIONDLC03` with only `sce_sys` inside. Put
them in one folder and choose it as **DLC folder** on **Game files**, or copy them to
`user\addcont\<title id>\`.

**Online play.** On the launcher's **Online play** page, tick the option and enter your shadNet
account, press **Test connection** until all three lines are reachable, then start the game.
Everyone you play with needs version 1.09 and the same server. With the Chinese-text patch, online
play relies on the URL fallback described above.

## Known issues

- Some AMD graphics cards may still crash when the game world loads; `user\last_run.log` helps
- Online play is new; messages, bloodstains, ghosts and summons work on the default server
- Keep the frame cap at 120 or lower
- Intel 2nd and 3rd generation processors run with translated instructions (best effort)

See upstream's [docs/WINDOWS_TROUBLESHOOTING.md](docs/WINDOWS_TROUBLESHOOTING.md) for more. If the
game shows only a black screen, try **Advanced → Clear shader cache** first.

## Building from source

Requires an MSYS2 CLANG64 environment:

```bash
bash build.sh                              # builds the executables into out/gpu/
bash packaging/windows/package.sh          # builds dist/bbport-windows.zip
```

See [packaging/windows/README.md](packaging/windows/README.md) for the details. DLSS is built
separately with `packaging/windows/build_dlss.sh` (needs Visual Studio 2022).

In this repository, `bash packaging/windows/package.sh --zip-only` produces the zip without
refreshing the playable copy under `dist/`, which suits CI. A tag triggers
`.github/workflows/release.yml`, which builds and publishes both packages.

## Credits

Built on [bbport](https://github.com/deadinside28/bloodborne_pc), the native Linux port of
Bloodborne by deadinside28, and on the [shadPS4](https://github.com/shadps4-emu/shadPS4) renderer.
The original README is in [docs/original-readme](docs/original-readme/README.md).

Online play uses the network, NP and shadNet code of [shadPS4](https://github.com/shadps4-emu/shadPS4)
0.20 and the shadNet server of the [shadPS4](https://shadps4.net) team, put together for this port
by **Awaken** ([BloodBorneButPc](https://github.com/Awakenchan/BloodBorneButPc)). Thanks to
Wozzardman's [shadp2p](https://github.com/Wozzardman/shadp2p), which bbport's first online version
was built on.

Seamless co-op is **BBSC: Yharnam Together** by **CLSAMG22**
([CLSAMG22/BBSC](https://github.com/CLSAMG22/BBSC), GPL-2.0): this port runs BBSC's game files,
co-op event patcher and HUD with its own engine and launcher. This port's change to BBSC's files is
listed in the package's `seamless\bbport-seamless.txt`.

The low-VRAM profile for 4 GB graphics cards comes from the 4 GB mod by **fixdag** and **bashiku**.

Also used: [FSR-Vulkan](https://github.com/FireBurn/FSR-Vulkan) and the AMD FidelityFX SDK (FSR),
FSR 4 assets from [FireBurn/Q2RTX](https://github.com/FireBurn/Q2RTX), the DLSS bridge adapted from
[IFreemz/shadPS4-Bloodborne-DLSS-FSR](https://github.com/IFreemz/shadPS4-Bloodborne-DLSS-FSR), the
[NVIDIA DLSS SDK](https://github.com/NVIDIA/DLSS) (`nvngx_dlss.dll` under NVIDIA's license),
[LibAtrac9](https://github.com/Thealexbarney/LibAtrac9), [SDL3](https://github.com/libsdl-org/SDL),
[FFmpeg](https://ffmpeg.org), [Dear ImGui](https://github.com/ocornut/imgui),
[sirit](https://github.com/shadps4-emu/sirit), [magic_enum](https://github.com/Neargye/magic_enum),
[miniz](https://github.com/richgel999/miniz), [xbyak](https://github.com/herumi/xbyak),
[wepoll](https://github.com/piscisaureus/wepoll), [cpp-httplib](https://github.com/yhirose/cpp-httplib),
[Protocol Buffers](https://protobuf.dev), [OpenSSL](https://www.openssl.org),
[miniupnpc](https://miniupnp.tuxfamily.org), [JSON for Modern C++](https://github.com/nlohmann/json),
[Vulkan Memory Allocator](https://github.com/GPUOpen-LibrariesAndSDKs/VulkanMemoryAllocator),
[MSYS2](https://www.msys2.org) / [LLVM](https://llvm.org), [PyInstaller](https://pyinstaller.org)
and [Pillow](https://python-pillow.org). Game patches by Kyo, Lance McDonald, auser1337, illusion,
emoose and the Bloodborne community.

NVIDIA, GeForce RTX and DLSS are trademarks of NVIDIA Corporation. The icon is original artwork.

## License

The port's own code is GNU GPL v2 or later ([LICENSE](LICENSE)). Some parts are GPL v3 or later:
the FSR 4.1 launcher files (`launcher/bbport_fsr41*.py`, `launcher/bbport_fsr412.py`,
`launcher/bbport_driver_runtime.py`). The program built from them together is therefore distributed
under the GNU GPL v3 or later (`licenses\GPL-3.0.txt` in the download). Third-party components keep
their own licenses (see `licenses\` in the download).
