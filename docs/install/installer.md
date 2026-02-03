---
summary: "How the installer scripts work (install.sh + install-cli.sh), flags, and automation"
read_when:
  - You want to understand `openclaw.ai/install.sh`
  - You want to automate installs (CI / headless)
  - You want to install from a GitHub checkout
title: "Installer Internals"
---
# 安装程序内部机制

OpenClaw 提供两个安装脚本（由 `openclaw.ai` 提供）：

- `https://openclaw.ai/install.sh` — 推荐安装脚本（默认全局 npm 安装；也可从 GitHub 检出安装）
- `https://openclaw.ai/install-cli.sh` — 非 root 友好的 CLI 安装脚本（安装到带有独立 Node 的前缀）
- `https://openclaw.ai/install.ps1` — Windows PowerShell 安装脚本（默认使用 npm；可选 git 安装）

要查看当前的标志/行为，请运行：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --help
```

Windows (PowerShell) 帮助：

```powershell
& ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -?
```

如果安装程序完成但新终端中未找到 `openclaw`，通常是 Node/npm 路径问题。请参阅：[安装](/install#nodejs--npm-path-sanity)。

## install.sh（推荐）

它执行的操作（概要）：

- 检测操作系统（macOS / Linux / WSL）。
- 确保 Node.js **22+**（macOS 通过 Homebrew；Linux 通过 NodeSource）。
- 选择安装方法：
  - `npm`（默认）：`npm install -g openclaw@latest`
  - `git`：克隆/构建源代码检出并安装包装脚本
- 在 Linux 上：通过切换 npm 的前缀到 `~/.npm-global` 来避免全局 npm 权限错误（如需）。
- 如果升级现有安装：运行 `openclaw doctor --non-interactive`（尽力而为）。
- 对于 git 安装：在安装/更新后运行 `openclaw doctor --non-interactive`（尽力而为）。
- 默认通过设置 `SHARP_IGNORE_GLOBAL_LIBVIPS=1` 来缓解 `sharp` 原生安装的陷阱（避免构建系统 libvips）。

如果你**希望** `sharp` 链接到全局安装的 libvips（或你正在调试），请设置：

```bash
SHARP_IGNORE_GLOBAL_LIBVIPS=0 curl -fsSL https://openclaw.ai/install.sh | bash
```

### 可发现性 / “git 安装”提示

如果你在**已经处于 OpenClaw 源代码检出目录内**运行安装程序（通过 `package.json` + `pnpm-workspace.yaml` 检测），它会提示：

- 更新并使用此检出（`git`）
- 或迁移到全局 npm 安装（`npm`）

在非交互式上下文（无 TTY / `--no-prompt`）中，必须传递 `--install-method git|npm`（或设置 `OPENCLAW_INSTALL_METHOD`），否则脚本将退出代码 `2`。

### 为什么需要 Git

Git 是 `--install-method git` 路径（克隆 / 拉取）所需的。

对于 `npm` 安装，Git 通常不是必需的，但某些环境仍可能需要（例如通过 git URL 获取包或依赖项）。安装程序目前确保 Git 存在，以避免在新发行版上出现 `spawn git ENOENT` 的意外情况。

### 为什么 npm 在新 Linux 上会遇到 `EACCES`

在某些 Linux 系统（尤其是通过系统包管理器或 NodeSource 安装 Node 之后），npm 的全局前缀指向 root 所有目录。然后 `npm install -g ...` 会因 `EACCES` / `mkdir` 权限错误而失败。

`install.sh` 通过切换前缀到：

- `~/.npm-global`（并在 `~/.bashrc` / `~/.zshrc` 中添加到 `PATH`）来缓解此问题（当存在时）。

## install-cli.sh（非 root CLI 安装）

此脚本将 `openclaw` 安装到一个前缀（默认：`~/.openclaw`），并在该前缀下安装专用的 Node 运行时，因此可以在不修改系统 Node/npm 的机器上运行。

帮助：

```bash
curl -fsSL https://openclaw.ai/install-cli.sh | bash -s -- --help
```

## install.ps1（Windows PowerShell）

它执行的操作（概要）：

- 确保 Node.js **22+**（通过 winget/Chocolatey/Scoop 或手动安装）。
- 选择安装方法：
  - `npm`（默认）：`npm install -g openclaw@latest`
  - `git`：克隆/构建源代码检出并安装包装脚本
- 在升级和 git 安装时运行 `openclaw doctor --non-interactive`（尽力而为）。

示例：

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex -InstallMethod git
```

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex -InstallMethod git -GitDir "C:\\openclaw"
```

环境变量：

- `OPENCLAW_INSTALL_METHOD=git|npm`
- `OPENCLAW_GIT_DIR=. ..`

Git 要求：

如果你选择 `-InstallMethod git` 且 Git 不存在，安装程序将打印 Git for Windows 链接（`https://git-scm.com/download/win`）并退出。

常见 Windows 问题：

- **npm 错误 spawn git / ENOENT**：安装 Git for Windows 并重新打开 PowerShell，然后重新运行安装程序。
- **"openclaw" 未被识别**：你的 npm 全局 bin 目录不在 PATH 中。大多数系统使用
  `%AppData%\\npm