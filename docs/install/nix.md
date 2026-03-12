---
summary: "Install OpenClaw declaratively with Nix"
read_when:
  - You want reproducible, rollback-able installs
  - You're already using Nix/NixOS/Home Manager
  - You want everything pinned and managed declaratively
title: "Nix"
---
# Nix 安装

使用 Nix 运行 OpenClaw 的推荐方式是通过 **[nix-openclaw](https://github.com/openclaw/nix-openclaw)** —— 一个开箱即用的 Home Manager 模块。

## 快速开始

将以下内容粘贴到您的 AI 助手（Claude、Cursor 等）中：

```text
I want to set up nix-openclaw on my Mac.
Repository: github:openclaw/nix-openclaw

What I need you to do:
1. Check if Determinate Nix is installed (if not, install it)
2. Create a local flake at ~/code/openclaw-local using templates/agent-first/flake.nix
3. Help me create a Telegram bot (@BotFather) and get my chat ID (@userinfobot)
4. Set up secrets (bot token, model provider API key) - plain files at ~/.secrets/ is fine
5. Fill in the template placeholders and run home-manager switch
6. Verify: launchd running, bot responds to messages

Reference the nix-openclaw README for module options.
```

> **📦 完整指南：[github.com/openclaw/nix-openclaw](https://github.com/openclaw/nix-openclaw)**
>
> `nix-openclaw` 仓库是 Nix 安装方式的权威来源。本页仅提供快速概览。

## 您将获得的功能

- 网关 + macOS 应用 + 工具（whisper、spotify、cameras）—— 全部版本固定
- 可在系统重启后持续运行的 launchd 服务
- 支持声明式配置的插件系统
- 即时回滚：`home-manager switch --rollback`

---

## Nix 模式下的运行时行为

当 `OPENCLAW_NIX_MODE=1` 被设置时（`nix-openclaw` 会自动完成该设置）：

OpenClaw 支持一种 **Nix 模式**，该模式使配置具备确定性，并禁用自动安装流程。  
可通过导出以下环境变量启用该模式：

```bash
OPENCLAW_NIX_MODE=1
```

在 macOS 上，GUI 应用不会自动继承 Shell 环境变量。您也可以通过 `defaults` 命令启用 Nix 模式：

```bash
defaults write ai.openclaw.mac openclaw.nixMode -bool true
```

### 配置与状态路径

OpenClaw 从 `OPENCLAW_CONFIG_PATH` 读取 JSON5 格式的配置，并将可变数据存储在 `OPENCLAW_STATE_DIR` 中。  
如有需要，您还可设置 `OPENCLAW_HOME`，以控制内部路径解析所使用的基准主目录。

- `OPENCLAW_HOME`（默认优先级顺序：`HOME` / `USERPROFILE` / `os.homedir()`）
- `OPENCLAW_STATE_DIR`（默认值：`~/.openclaw`）
- `OPENCLAW_CONFIG_PATH`（默认值：`$OPENCLAW_STATE_DIR/openclaw.json`）

在 Nix 环境下运行时，请显式将这些路径设为由 Nix 管理的位置，以确保运行时状态和配置不混入不可变的 Nix 存储区。

### Nix 模式下的运行时行为

- 自动安装及自更新流程被禁用
- 缺失依赖项将触发面向 Nix 的特定修复提示
- 当 Nix 模式启用时，UI 将显示只读的 Nix 模式横幅

## 打包说明（macOS）

macOS 打包流程期望在以下位置存在一个稳定的 `Info.plist` 模板：

```
apps/macos/Sources/OpenClaw/Resources/Info.plist
```

[`scripts/package-mac-app.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-app.sh) 会将该模板复制进应用包，并修补动态字段（Bundle ID、版本/构建号、Git SHA、Sparkle 密钥）。这使得 `plist` 文件对 SwiftPM 打包和 Nix 构建（不依赖完整 Xcode 工具链）保持确定性。

## 相关链接

- [nix-openclaw](https://github.com/openclaw/nix-openclaw) —— 完整设置指南
- [向导](/start/wizard) —— 非 Nix 的 CLI 设置方式
- [Docker](/install/docker) —— 容器化部署方式