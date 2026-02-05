---
summary: "How the installer scripts work (install.sh + install-cli.sh), flags, and automation"
read_when:
  - You want to understand `openclaw.ai/install.sh`
  - You want to automate installs (CI / headless)
  - You want to install from a GitHub checkout
title: "Installer Internals"
---
# 安装程序内部

OpenClaw 提供两个安装脚本（托管在 `openclaw.ai`）：

- `https://openclaw.ai/install.sh` — “推荐”安装程序（默认全局 npm 安装；也可以从 GitHub 检出安装）
- `https://openclaw.ai/install-cli.sh` — 非 root 友好的 CLI 安装程序（安装到带有自己的 Node 的前缀）
- `https://openclaw.ai/install.ps1` — Windows PowerShell 安装程序（默认 npm；可选 git 安装）

要查看当前标志/行为，请运行：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --help
```

Windows (PowerShell) 帮助：

```powershell
& ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -?
```

如果安装程序完成但 `openclaw` 在新终端中未找到，通常是 Node/npm PATH 问题。参见：[安装](/install#nodejs--npm-path-sanity)。

## install.sh (推荐)

它做了什么（高层次）：

- 检测操作系统（macOS / Linux / WSL）。
- 确保 Node.js **22+**（macOS 通过 Homebrew；Linux 通过 NodeSource）。
- 选择安装方法：
  - `npm`（默认）：`npm install -g openclaw@latest`
  - `git`：克隆/构建源检出并安装包装脚本
- 在 Linux 上：通过将 npm 的前缀切换到 `~/.npm-global` 来避免全局 npm 权限错误（如有必要）。
- 如果升级现有安装：运行 `openclaw doctor --non-interactive`（尽力而为）。
- 对于 git 安装：在安装/更新后运行 `openclaw doctor --non-interactive`（尽力而为）。
- 默认情况下通过设置 `SHARP_IGNORE_GLOBAL_LIBVIPS=1` 来缓解 `sharp` 原生安装陷阱（避免针对系统 libvips 进行构建）。

如果你 _希望_ `sharp` 链接到全局安装的 libvips（或者你在调试），设置：

```bash
SHARP_IGNORE_GLOBAL_LIBVIPS=0 curl -fsSL https://openclaw.ai/install.sh | bash
```

### 发现性 / “git 安装”提示

如果你在 **已经位于 OpenClaw 源检出** 中运行安装程序（通过检测 `package.json` + `pnpm-workspace.yaml`），它会提示：

- 更新并使用此检出 (`git`)
- 或迁移到全局 npm 安装 (`npm`)

在非交互式上下文中（无 TTY / `--no-prompt`），你必须传递 `--install-method git|npm`（或设置 `OPENCLAW_INSTALL_METHOD`），否则脚本将以代码 `2` 退出。

### 为什么需要 Git

Git 对于 `--install-method git` 路径（克隆 / 拉取）是必需的。

对于 `npm` 安装，通常不需要 Git，但在某些环境中仍然需要它（例如，当通过 git URL 获取包或依赖项时）。安装程序目前确保 Git 存在以避免在全新发行版上出现 `spawn git ENOENT` 意外情况。

### 为什么 npm 在全新 Linux 上命中 `EACCES`

在某些 Linux 设置上（尤其是在通过系统包管理器或 NodeSource 安装 Node 后），npm 的全局前缀指向一个 root 所有的位置。然后 `npm install -g ...` 失败并出现 `EACCES` / `mkdir` 权限错误。

`install.sh` 通过将前缀切换到以下位置来缓解此问题：

- `~/.npm-global`（并在 `~/.bashrc` / `~/.zshrc` 中存在时将其添加到 `PATH`）

## install-cli.sh (非 root CLI 安装程序)

此脚本将 `openclaw` 安装到前缀（默认：`~/.openclaw`），并在该前缀下安装专用的 Node 运行时，因此可以在不想触碰系统 Node/npm 的机器上工作。

帮助：

```bash
curl -fsSL https://openclaw.ai/install-cli.sh | bash -s -- --help
```

## install.ps1 (Windows PowerShell)

它做了什么（高层次）：

- 确保 Node.js **22+**（winget/Chocolatey/Scoop 或手动）。
- 选择安装方法：
  - `npm`（默认）：`npm install -g openclaw@latest`
  - `git`：克隆/构建源检出并安装包装脚本
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
- `OPENCLAW_GIT_DIR=...`

Git 要求：

如果你选择 `-InstallMethod git` 且缺少 Git，安装程序将打印
Git for Windows 链接 (`https://git-scm.com/download/win`) 并退出。

常见的 Windows 问题：

- **npm 错误 spawn git / ENOENT**：安装 Git for Windows 并重新打开 PowerShell，然后重新运行安装程序。
- **"openclaw" 未被识别**：你的 npm 全局 bin 文件夹不在 PATH 中。大多数系统使用
  `%AppData%\\npm`。你也可以运行 `npm config get prefix` 并将 `\\bin` 添加到 PATH，然后重新打开 PowerShell。