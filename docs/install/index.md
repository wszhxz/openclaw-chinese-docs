---
summary: "Install OpenClaw (recommended installer, global install, or from source)"
read_when:
  - Installing OpenClaw
  - You want to install from GitHub
title: "Install"
---
# 安装

除非有特殊原因，否则使用安装程序。它会设置 CLI 并运行引导流程。

## 快速安装（推荐）

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

Windows（PowerShell）：

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

下一步（如果跳过了引导流程）：

```bash
openclaw onboard --install-daemon
```

## 系统要求

- **Node >=22**
- macOS、Linux 或通过 WSL2 的 Windows
- 仅在从源代码构建时需要 `pnpm`

## 选择安装路径

### 1) 安装脚本（推荐）

通过 npm 全局安装 `openclaw` 并运行引导流程。

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

安装脚本标志：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --help
```

详情：[安装程序内部机制](/install/installer)。

非交互式（跳过引导流程）：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard
```

### 2) 全局安装（手动）

如果你已经安装了 Node：

```bash
npm install -g openclaw@latest
```

如果你全局安装了 libvips（在 macOS 上常见于 Homebrew）且 `sharp` 安装失败，强制使用预编译二进制文件：

```bash
SHARP_IGNORE_GLOBAL_LIBVIPS=1 npm install -g openclaw@latest
```

如果你看到 `sharp: Please add node-gyp to your dependencies`，可以安装构建工具（macOS：Xcode CLT + `npm install -g node-gyp`），或者使用上述 `SHARP_IGNORE_GLOBAL_LIBVIPS=1` 的方法跳过原生构建。

或使用 pnpm：

```bash
pnpm add -g openclaw@latest
pnpm approve-builds -g                # 批准 openclaw、node-llama-cpp、sharp 等
pnpm add -g openclaw@latest           # 重新运行以执行 postinstall 脚本
```

pnpm 需要显式批准带有构建脚本的包。在首次安装时显示 "Ignored build scripts" 警告后，运行 `pnpm approve-builds -g` 并选择列出的包，然后重新运行安装以执行 postinstall 脚本。

然后：

```bash
openclaw onboard --install-daemon
```

### 3) 从源代码安装（贡献者/开发者）

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build # 第一次运行时自动安装 UI 依赖
pnpm build
openclaw onboard --install-daemon
```

提示：如果你尚未进行全局安装，可通过 `pnpm openclaw ...` 运行仓库命令。

### 4) 其他安装选项

- Docker: [Docker](/install/docker)
- Nix: [Nix](/install/nix)
- Ansible: [Ansible](/install/ansible)
- Bun（仅 CLI）: [Bun](/install/bun)

## 安装后

- 运行引导流程：`openclaw onboard --install-daemon`
- 快速检查：`openclaw doctor`
- 检查网关健康状态：`openclaw status` + `openclaw health`
- 打开仪表盘：`openclaw dashboard`

## 安装方法：npm vs git（安装程序）

安装程序支持两种方法：

- `npm`（默认）：`npm install -g openclaw@latest`
- `git`：从 GitHub 克隆/构建并从源代码检出运行

### CLI 标志

```bash
# 显式 npm
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method npm

# 从 GitHub 安装（源代码检出）
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
```

常见标志：

- `--install-method npm|git`
- `--git-dir <路径>`（默认：`~/openclaw`）
- `--no-git-update`（使用现有检出时跳过 `git pull`）
- `--no-prompt`（禁用提示；在 CI/自动化中必需）
- `--dry-run`（打印将会发生什么；不进行任何更改）
- `--no-onboard`（跳过引导流程）

### 环境变量

等效的环境变量（适用于自动化）：

- `OPENCLAW_INSTALL_METHOD=git|npm`
- `OPENCLAW_GIT_DIR=...`
- `OPENCLAW_GIT_UPDATE=0|1`
- `OPENCLAW_NO_PROMPT=1`
- `OPENCLAW_DRY_RUN=1`
- `OPENCLAW_NO_ONBOARD=1`
- `SHARP_IGNORE_GLOBAL_LIBVIPS=0|1`（默认：`1`；避免 `sharp` 构建到系统 libvips）

## 故障排除：`openclaw` 未找到（PATH）

快速诊断：

```bash
node -v
npm -v
npm prefix -g
echo "$PATH"
```

如果 `$(npm prefix -g)/bin`（macOS/Linux）或 `$(npm prefix -g)`（Windows）不在 `echo "$PATH"` 中，你的 shell 将无法找到全局 npm 二进制文件（包括 `openclaw`）。

修复：将它添加到你的 shell 启动文件（zsh: `~/.zshrc`，bash: `~/.bashrc`）：

```bash
# macOS / Linux
export PATH="$(npm prefix -g)/bin:$PATH"
```

在 Windows 上，将 `npm prefix -g` 的输出添加到你的 PATH。

然后打开一个新的终端（或在 z