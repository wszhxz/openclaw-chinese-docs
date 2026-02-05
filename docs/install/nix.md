---
summary: "Install OpenClaw declaratively with Nix"
read_when:
  - You want reproducible, rollback-able installs
  - You're already using Nix/NixOS/Home Manager
  - You want everything pinned and managed declaratively
title: "Nix"
---
# Nix 安装

使用 Nix 运行 OpenClaw 的推荐方法是通过 **[nix-openclaw](https://github.com/openclaw/nix-openclaw)** — 一个包含所有功能的 Home Manager 模块。

## 快速开始

将以下内容粘贴到您的 AI 代理（Claude、Cursor 等）中：

```text
I want to set up nix-openclaw on my Mac.
Repository: github:openclaw/nix-openclaw

What I need you to do:
1. Check if Determinate Nix is installed (if not, install it)
2. Create a local flake at ~/code/openclaw-local using templates/agent-first/flake.nix
3. Help me create a Telegram bot (@BotFather) and get my chat ID (@userinfobot)
4. Set up secrets (bot token, Anthropic key) - plain files at ~/.secrets/ is fine
5. Fill in the template placeholders and run home-manager switch
6. Verify: launchd running, bot responds to messages

Reference the nix-openclaw README for module options.
```

> **📦 完整指南：[github.com/openclaw/nix-openclaw](https://github.com/openclaw/nix-openclaw)**
>
> nix-openclaw 仓库是 Nix 安装的权威来源。此页面仅是一个快速概述。

## 您将获得的内容

- Gateway + macOS 应用程序 + 工具（whisper, spotify, cameras）—— 所有版本都已固定
- 能够在重启后继续运行的 Launchd 服务
- 声明式配置的插件系统
- 即时回滚：`home-manager switch --rollback`

---

## Nix 模式运行时行为

当 `OPENCLAW_NIX_MODE=1` 设置为（使用 nix-openclaw 时自动设置）：

OpenClaw 支持一种 **Nix 模式**，该模式使配置具有确定性并禁用自动安装流程。
通过导出以下内容启用它：

```bash
OPENCLAW_NIX_MODE=1
```

在 macOS 上，GUI 应用程序不会自动继承 shell 环境变量。您也可以通过 defaults 启用 Nix 模式：

```bash
defaults write bot.molt.mac openclaw.nixMode -bool true
```

### 配置 + 状态路径

OpenClaw 从 `OPENCLAW_CONFIG_PATH` 读取 JSON5 配置，并将可变数据存储在 `OPENCLAW_STATE_DIR` 中。

- `OPENCLAW_STATE_DIR`（默认：`~/.openclaw`）
- `OPENCLAW_CONFIG_PATH`（默认：`$OPENCLAW_STATE_DIR/openclaw.json`）

在使用 Nix 运行时，显式地将这些设置为由 Nix 管理的位置，以确保运行时状态和配置不进入不可变存储。

### Nix 模式下的运行时行为

- 禁用自动安装和自我变异流程
- 缺少的依赖项会显示特定于 Nix 的补救消息
- 当存在时，UI 显示一个只读的 Nix 模式横幅

## 打包说明（macOS）

macOS 打包流程期望在以下位置有一个稳定的 Info.plist 模板：

```
apps/macos/Sources/OpenClaw/Resources/Info.plist
```

[`scripts/package-mac-app.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-app.sh) 将此模板复制到应用程序包中并修补动态字段
（bundle ID、版本/构建、Git SHA、Sparkle 密钥）。这使得 plist 对于 SwiftPM 打包和 Nix 构建（这些构建不依赖完整的 Xcode 工具链）保持确定性。

## 相关

- [nix-openclaw](https://github.com/openclaw/nix-openclaw) — 完整设置指南
- [Wizard](/start/wizard) — 非 Nix CLI 设置
- [Docker](/install/docker) — 容器化设置