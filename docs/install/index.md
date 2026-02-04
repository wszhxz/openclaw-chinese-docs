---
summary: "Install OpenClaw (recommended installer, global install, or from source)"
read_when:
  - Installing OpenClaw
  - You want to install from GitHub
title: "Install"
---
# 安装

除非你有不使用安装程序的理由，否则请使用安装程序。它会设置CLI并运行入站引导。

## 快速安装（推荐）

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

Windows (PowerShell):

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

下一步（如果你跳过了入站引导）：

```bash
openclaw onboard --install-daemon
```

## 系统要求

- **Node >=22**
- macOS, Linux, 或通过WSL2的Windows
- 仅当你从源代码构建时需要 `pnpm`

## 选择安装路径

### 1) 安装程序脚本（推荐）

通过npm全局安装 `openclaw` 并运行入站引导。

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

安装程序标志：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --help
```

详情：[安装程序内部](/install/installer)。

非交互式（跳过入站引导）：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard
```

### 2) 全局安装（手动）

如果你已经安装了Node：

```bash
npm install -g openclaw@latest
```

如果你全局安装了libvips（在macOS上通过Homebrew很常见），而 `sharp` 安装失败，请强制使用预构建的二进制文件：

```bash
SHARP_IGNORE_GLOBAL_LIBVIPS=1 npm install -g openclaw@latest
```

如果你看到 `sharp: Please add node-gyp to your dependencies`，要么安装构建工具（macOS: Xcode CLT + `npm install -g node-gyp`），或者使用上述 `SHARP_IGNORE_GLOBAL_LIBVIPS=1` 工作区绕过本地构建。

或者使用pnpm：

```bash
pnpm add -g openclaw@latest
pnpm approve-builds -g                # approve openclaw, node-llama-cpp, sharp, etc.
pnpm add -g openclaw@latest           # re-run to execute postinstall scripts
```

pnpm需要对带有构建脚本的包进行显式批准。在第一次安装显示“Ignored build scripts”警告后，运行 `pnpm approve-builds -g` 并选择列出的包，然后重新运行安装以执行postinstall脚本。

然后：

```bash
openclaw onboard --install-daemon
```

### 3) 从源代码安装（贡献者/开发人员）

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build # auto-installs UI deps on first run
pnpm build
openclaw onboard --install-daemon
```

提示：如果你还没有全局安装，通过 `pnpm openclaw ...` 运行仓库命令。

### 4) 其他安装选项

- Docker: [Docker](/install/docker)
- Nix: [Nix](/install/nix)
- Ansible: [Ansible](/install/ansible)
- Bun (仅CLI): [Bun](/install/bun)

## 安装后

- 运行入站引导：`openclaw onboard --install-daemon`
- 快速检查：`openclaw doctor`
- 检查网关健康状况：`openclaw status` + `openclaw health`
- 打开仪表板：`openclaw dashboard`

## 安装方法：npm vs git（安装程序）

安装程序支持两种方法：

- `npm`（默认）：`npm install -g openclaw@latest`
- `git`：从GitHub克隆/构建并从源代码检出运行

### CLI 标志

```bash
# Explicit npm
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method npm

# Install from GitHub (source checkout)
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
```

常用标志：

- `--install-method npm|git`
- `--git-dir <path>`（默认：`~/openclaw`）
- `--no-git-update`（使用现有检出时跳过 `git pull`）
- `--no-prompt`（禁用提示；CI/自动化中必需）
- `--dry-run`（打印将要发生的情况；不进行更改）
- `--no-onboard`（跳过入站引导）

### 环境变量

等效的环境变量（适用于自动化）：

- `OPENCLAW_INSTALL_METHOD=git|npm`
- `OPENCLAW_GIT_DIR=...`
- `OPENCLAW_GIT_UPDATE=0|1`
- `OPENCLAW_NO_PROMPT=1`
- `OPENCLAW_DRY_RUN=1`
- `OPENCLAW_NO_ONBOARD=1`
- `SHARP_IGNORE_GLOBAL_LIBVIPS=0|1`（默认：`1`；避免 `sharp` 使用系统libvips进行构建）

## 故障排除：未找到 `openclaw`（PATH）

快速诊断：

```bash
node -v
npm -v
npm prefix -g
echo "$PATH"
```

如果 `$(npm prefix -g)/bin`（macOS/Linux）或 `$(npm prefix -g)`（Windows）不在 `echo "$PATH"` 内，你的shell无法找到全局npm二进制文件（包括 `openclaw`）。

修复：将其添加到你的shell启动文件（zsh: `~/.zshrc`，bash: `~/.bashrc`）：

```bash
# macOS / Linux
export PATH="$(npm prefix -g)/bin:$PATH"
```

在Windows上，将 `npm prefix -g` 的输出添加到你的PATH。

然后打开一个新的终端（或在zsh中 `rehash` / 在bash中 `hash -r`）。

## 更新 / 卸载

- 更新：[更新](/install/updating)
- 迁移到新机器：[迁移](/install/migrating)
- 卸载：[卸载](/install/uninstall)