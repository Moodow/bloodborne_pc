# Bloodborne for Windows（个人构建）

[English](README.en.md) · [上游项目](https://github.com/Supermedo/bloodborne_pc) · [下载](../../releases)

> **本仓库是 [Supermedo/bloodborne_pc](https://github.com/Supermedo/bloodborne_pc) 的个人 fork**，
> 由个人维护，不是官方发行版。其中部分改动针对特定场景，未必适用于所有人。

## 源项目

Bloodborne 原生运行在 Windows 10 / 11 上。PS4 原版游戏的 x86-64 代码直接在本机执行，图形翻译为
Vulkan 呈现——不是模拟器，没有模拟器窗口，也不需要配置脚本：解压、启动 `Bloodborne.exe`、选择游戏
目录、按下 **PLAY**。

项目由 [Supermedo](https://github.com/Supermedo)（Mohammed Albarghouthi）开发，构建在
[bbport](https://github.com/deadinside28/bloodborne_pc)（deadinside28 的 Bloodborne Linux 原生移植）
与 [shadPS4](https://github.com/shadps4-emu/shadPS4) 渲染器之上。

**不含任何游戏文件。** 需要自备解密后的游戏转储（任意零售版本：美版 CUSA00900、欧版 CUSA00207、
年度版 CUSA03173 等），格式为 SELF 或纯 ELF。社区补丁（60/90/解锁帧率、分辨率、特效）需要
**1.09** 版本，其他版本以 30 FPS 运行。

本项目与 Sony Interactive Entertainment 及 FromSoftware 无隶属关系。

上游的完整功能说明见 [Supermedo/bloodborne_pc 的 README](https://github.com/Supermedo/bloodborne_pc#features)，
包括 13 语言启动器、DLSS / FSR 3.1 / FSR 4、ML 帧生成、作弊页、画质与视场角调节、键鼠映射、
存档导入、游戏内测试与更新器等。

## 这个 fork 做了什么

### 1. 修复中文补丁导致的联机失效

零售版的血源要显示中文，只能通过 **Unlock Game Region** 补丁。该补丁把游戏 region 改为 5，超出
游戏内四条目服务器 URL 表的索引范围，取到空字符串。随后 `sceHttpCreateConnectionWithURL` 收到空
URL，连接被拒，游戏提示「无法获取 Bloodborne 服务器信息」，联机永远无法启动。

服务器上每个 `/bb-xx/` 路径返回同一份文档，因此当 URL 不带 scheme 时，回退到游戏自身 host 的 EU
端点（`https://ss4.scej-network.jp:20443/bb-eu/ss.info`）。`run.py` 写入的 host 覆盖仍会把它重定向到
社区服务器，自定义服务器不受影响。

可用 `BB_SERVER_INFO_URL` 指定其他地址，设为 `0` 则关闭该回退。

一句话：**用中文补丁也能联机。**

### 2. 构建与发布流水线

上游的 CI 在本仓库环境中无法跑通（`msys2-env.sh` 会把 runner 预装的旧版 MSYS2 注入 PATH，导致
`cp` 等 coreutils exec 失败并返回 127）。本 fork 重建了这条流水线：

- push 时只编 `bb-probe.exe` 做快速编译验证，约 5 分钟
- 打 `windows-v*` 标签时全量构建并自动发布两个包
- 并行度按实际核数、ccache 复用、失败时导出可诊断的日志

### 3. 自动更新指向本仓库

启动器的更新检查原本写死上游仓库，点「更新」会把 `bin\` 整个换成官方构建，上面那个修复随之失效。
本仓库的构建改为向本仓库取最新发行版：更新是更新到**这个**版本，不会退回官方版。

代价是这条通道要自己维持：上游发版后同步、递增 `FORK_REV`、打标签，才会产生下一次更新。规则见
[wiki 的 Release 页](https://github.com/Moodow/bloodborne_pc/wiki/Release)。装着上游启动器的安装
不会自己切过来，需要手动解压一次本仓库的完整包。

### 4. 文本输入：粘贴与剪贴板

地牢搜索要在祭坛里手打 8 位 glyph，而端口原来的输入框只接受键盘敲击，剪贴板里的内容进不去。

- **Ctrl+V 粘贴**：任意输入框（角色名、留言、glyph）都能把剪贴板粘进来。输入框是单行的，换行与制表符被丢掉，中文等 UTF-8 字符原样保留。
- **glyph 自动填充**：启动器 **Controls** 页的 `Fill the text box from the clipboard (Chalice Glyphs)`，等价于 `bbport.ini` 的 `ime_clipboard=1`。当剪贴板恰好是 8 位字母数字时，glyph 框一弹出就带着内容，回车确认；其它文本框不受影响。

这两项只改变输入方式，不碰游戏内容：填入的 glyph 仍要过游戏自己的「Search using Chalice Glyph」确认框。

以上四类改动是本仓库与上游的全部差异。游戏功能仍全部来自上游，本仓库新增的只有输入方式这一层。

## 下载

到 [Releases](../../releases) 挑选：

| 文件 | 说明 |
| --- | --- |
| `bbport-windows.zip` | **完整包**，与上游发行版同构：含启动器、四个可执行文件、FSR 各版本运行库与许可文件。解压即用。 |
| `bb-probe-only.zip` | **精简包**，仅主程序 `bb-probe.exe`，依赖已静态链接。需要自行准备游戏目录与启动方式，没有图形启动器。 |

## 系统要求

- Windows 10（1903 或更高）或 Windows 11，64 位
- Intel 第 4 代（Haswell，2013）及以上的 Core，或 AMD Ryzen。游戏使用了 PS4 处理器的指令集
  （AVX、BMI1、MOVBE、LZCNT）；Intel 第 2、3 代可借助指令翻译运行（尽力而为）；不支持 AVX 的
  处理器（多数 Pentium、Celeron）无法运行
- 支持 Vulkan 1.3 的显卡与较新的驱动
- 约 6 GB 可用内存（物理内存 + 页面文件），1440p 或 4K 输出需要 10 GB
- DLSS 需要 NVIDIA GeForce RTX 20 系及以上

完整包无需另装任何东西，游戏需要的一切都在压缩包里。

## 开始游戏

1. 从 [Releases](../../releases) 下载并解压到任意目录
2. 启动 `Bloodborne.exe`。首次运行会引导检查游戏目录（含 `eboot.bin` 的那个）与硬件，并按硬件设定画质
3. 按下 **PLAY**

游戏内按 **Insert**（手柄 **L3+R3**）打开设置菜单。

**DLC**：年度版已含《老猎人》。基础版转储需另外导出附加内容——每个附加内容是一个形如
`SPEXPANSIONDLC03` 的文件夹，内部只有 `sce_sys`。把它们放进同一目录，在**游戏文件**页选择该目录
作为 **DLC 文件夹**，或复制到 `user\addcont\<title id>\`。

**联机**：在启动器**联机**页勾选、填入 shadNet 账号，先按**测试连接**确认三行均可达，再进游戏。
所有参与者需使用 1.09 版本与同一联机服务器。使用中文补丁时，联机依赖上文所述的 URL 回退修复。

## 已知问题

- 部分 AMD 显卡在游戏世界加载时仍可能崩溃，可提交 `user\last_run.log`
- 联机功能较新，默认服务器上的留言、血迹、幻影与召唤已可用
- 建议帧率上限保持在 120 及以下
- Intel 第 2、3 代处理器依赖指令翻译，少数指令尚未覆盖

更多排查方法见上游的 [docs/WINDOWS_TROUBLESHOOTING.md](docs/WINDOWS_TROUBLESHOOTING.md)。
若只有黑屏，先试**高级 → 清除着色器缓存**。

## 从源码构建

需要 MSYS2 CLANG64 环境：

```bash
bash build.sh                              # 生成 out/gpu/ 下的可执行文件
bash packaging/windows/package.sh          # 生成 dist/bbport-windows.zip 完整包
```

完整说明见 [packaging/windows/README.md](packaging/windows/README.md)。DLSS 需单独用
`packaging/windows/build_dlss.sh` 构建（依赖 Visual Studio 2022）。

本仓库的发布流程：`bash packaging/windows/package.sh --zip-only` 只产出 zip，不刷新 `dist/` 下的可玩
副本，适合 CI。打标签后由 `.github/workflows/release.yml` 自动完成构建与发布。

## 致谢

建立在 [bbport](https://github.com/deadinside28/bloodborne_pc)（deadinside28 的 Bloodborne Linux
原生移植）与 [shadPS4](https://github.com/shadps4-emu/shadPS4) 渲染器之上。原始 README 见
[docs/original-readme](docs/original-readme/README.md)。

联机功能使用 [shadPS4](https://github.com/shadps4-emu/shadPS4) 0.20 的网络、NP 与 shadNet 代码，
以及 [shadPS4](https://shadps4.net) 团队的 shadNet 服务器，由 **Awaken**
（[BloodBorneButPc](https://github.com/Awakenchan/BloodBorneButPc)）为本移植整合。感谢 Wozzardman 的
[shadp2p](https://github.com/Wozzardman/shadp2p)，bbport 的首个联机版本建立在其之上。

无缝联机为 **CLSAMG22** 的 **BBSC: Yharnam Together**（[CLSAMG22/BBSC](https://github.com/CLSAMG22/BBSC)，
GPL-2.0）：本移植以其自有引擎运行 BBSC 的游戏文件、联机事件补丁与 HUD。本移植对 BBSC 文件的改动列在
发布包的 `seamless\bbport-seamless.txt` 中。

4 GB 显卡的低显存配置文件来自 **fixdag** 与 **bashiku** 的 4 GB 模组。

其他组件：[FSR-Vulkan](https://github.com/FireBurn/FSR-Vulkan) 与 AMD FidelityFX SDK（FSR），FSR 4
资源来自 [FireBurn/Q2RTX](https://github.com/FireBurn/Q2RTX)，DLSS 桥接改编自
[IFreemz/shadPS4-Bloodborne-DLSS-FSR](https://github.com/IFreemz/shadPS4-Bloodborne-DLSS-FSR)，
[NVIDIA DLSS SDK](https://github.com/NVIDIA/DLSS)、[LibAtrac9](https://github.com/Thealexbarney/LibAtrac9)、
[SDL3](https://github.com/libsdl-org/SDL)、[FFmpeg](https://ffmpeg.org)、
[Dear ImGui](https://github.com/ocornut/imgui)、[sirit](https://github.com/shadps4-emu/sirit)、
[magic_enum](https://github.com/Neargye/magic_enum)、[miniz](https://github.com/richgel999/miniz)、
[xbyak](https://github.com/herumi/xbyak)、[wepoll](https://github.com/piscisaureus/wepoll)、
[cpp-httplib](https://github.com/yhirose/cpp-httplib)、[Protocol Buffers](https://protobuf.dev)、
[OpenSSL](https://www.openssl.org)、[miniupnpc](https://miniupnp.tuxfamily.org)、
[JSON for Modern C++](https://github.com/nlohmann/json)、
[Vulkan Memory Allocator](https://github.com/GPUOpen-LibrariesAndSDKs/VulkanMemoryAllocator)、
[MSYS2](https://www.msys2.org) / [LLVM](https://llvm.org)、[PyInstaller](https://pyinstaller.org)、
[Pillow](https://python-pillow.org)。游戏补丁来自 Kyo、Lance McDonald、auser1337、illusion、emoose
以及血源社区。

NVIDIA、GeForce RTX 与 DLSS 是 NVIDIA Corporation 的商标。图标为原创作品。

## 许可

本移植自有代码采用 GNU GPL v2 或更高版本（[LICENSE](LICENSE)）。部分代码为 GPL v3 或更高版本：
FSR 4.1 启动器文件（`launcher/bbport_fsr41*.py`、`launcher/bbport_fsr412.py`、
`launcher/bbport_driver_runtime.py`）。由它们共同构建的完整程序因此以 GNU GPL v3 或更高版本分发
（发布包内 `licenses\GPL-3.0.txt`）。第三方组件保持各自的许可（见发布包内 `licenses\`）。
