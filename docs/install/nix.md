---
summary: "Install OpenClaw declaratively with Nix"
read_when:
  - You want reproducible, rollback-able installs
  - You're already using Nix/NixOS/Home Manager
  - You want everything pinned and managed declaratively
title: "Nix"
---
服务<think>
Okay, I need to translate this English text into Chinese. Let me start by reading through the entire content to understand the context and technical terms involved. The text is about installing OpenClaw using Nix, with specific instructions for macOS and some configuration details.

First, I'll translate the main headings and sections. Terms like "Nix Installation" become "Nix 安装". The mention of "nix-openclaw" should remain as is since it's a project name, but I'll add the Chinese translation in parentheses for clarity. 

Next, the "Quick Start" section has a code block with instructions. I need to ensure that the commands and placeholders are accurately translated. For example, "I want to set up nix-openclaw on my Mac." becomes "我想在我的Mac上设置nix-openclaw。" 

I should be careful with technical terms like "Home Manager module" which translates to "Home Manager 模块". Also, terms like "launchd" and "Telegram bot" should stay in English as they are specific to the tools mentioned. 

In the "What you get" section, phrases like "Gateway + macOS app + tools" need to be translated while maintaining the list structure. Terms like "whisper, spotify, cameras" are proper nouns, so they remain in English. 

The "Nix Mode Runtime Behavior" section has some specific commands and environment variables. I'll make sure to translate the explanations but keep the variable names in English. For example, "OPENCLAW_NIX_MODE=1" stays the same, but the surrounding text is translated. 

The "Packaging note (macOS)" section has file paths and scripts. I need to ensure that the file paths are correctly translated, but the actual file names and paths remain in English. 

I'll also check for consistency in terminology throughout the translation. For instance, "Home Manager" should be consistently translated as "Home Manager" in Chinese. 

Finally, I'll review the entire translated text to ensure that it flows naturally in Chinese while preserving the technical accuracy. Making sure that all instructions are clear and that the structure mirrors the original English text.
</think>

# Nix 安装

推荐通过 **[nix-openclaw](https://github.com/openclaw/nix-openclaw)** —— 一个包含所有依赖项的 Home Manager 模块 —— 来运行 OpenClaw。

## 快速入门

将以下内容粘贴到您的 AI 代理（Claude、Cursor 等）中：

```text
我想在我的 Mac 上设置 nix-openclaw。
仓库：github:openclaw/nix-openclaw

您需要执行以下操作：
1. 检查是否安装了 Determinate Nix（如果没有，请安装）
2. 使用 templates/agent-first/flake.nix 模板在 ~/code/openclaw-local 创建本地 flake
3. 帮助我创建一个 Telegram 机器人（@BotFather）并获取我的聊天 ID（@userinfobot）
4. 设置密钥（bot token、Anthropic 密钥）- 将 plain 文件存放在 ~/.secrets/ 即可
5. 填充模板占位符并运行 home-manager switch
6. 验证：launchd 正在运行，机器人能响应消息

参考 nix-openclaw 的 README 了解模块选项。
``
>
> **📦 完整指南：[github.com/openclaw/nix-openclaw](https://github.com/openclaw/nix-openclaw)**
>
> nix-openclaw 仓库是 Nix 安装的权威来源。本页面仅是快速概览。

## 您将获得

- 网关 + macOS 应用 + 工具（whisper、spotify、摄像头）—— 所有内容均固定版本
- 可跨重启存活的 launchd 服务
- 声明式配置的插件系统
- 即时回滚：`home-manager switch --rollback`

---

## Nix 模式运行时行为

当 `OPENCLAW_NIX_MODE=1` 被设置（通过 nix-openclaw 自动设置）：

OpenClaw 支持一种 **Nix 模式**，该模式使配置确定化并禁用自动安装流程。
通过导出以下内容启用它：

```bash
OPENCLAW_NIX_MODE=1
``
```

在 macOS 上，GUI 应用不会自动继承 shell 环境变量。您也可以通过 defaults 启用 Nix 模式：

```bash
defaults write bot.molt.mac openclaw.nixMode -bool true
``
```

### 配置 + 状态路径

OpenClaw 从 `OPENCLAW_CONFIG_PATH` 读取 JSON5 配置，并将可变数据存储在 `OPENCLAW_STATE_DIR`。

- `OPENCLAW_STATE_DIR`（默认：`~/.openclaw`）
- `OPEN,CLAW_CONFIG_PATH`（默认：`$OPENCLAW_STATE_DIR/openclaw.json`）

在 Nix 环境下运行时，请显式将这些路径设置为 Nix 管理的路径，以确保运行时状态和配置不会进入不可变存储。

### Nix 模式下的运行时行为

- 自动安装和自变异流程被禁用
- 缺失依赖项会显示 Nix 特定的修复信息
- UI 在存在时显示只读的 Nix 模式横幅

## 包装说明（macOS）

macOS 包装流程期望在以下路径有一个稳定的 Info.plist 模板：

```
apps/macos/Sources/OpenClaw/Resources/Info.plist
```

[`scripts/package-mac-app.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-app.sh) 会将此模板复制到应用包中，并修补动态字段
（包 ID、版本/构建号、Git SHA、Sparkle 密钥）。这确保了 plist 在 SwiftPM 包装和 Nix 构建中是确定性的（它们不依赖完整的 Xcode 工具链）。

## 相关内容

- [nix-openclaw](https://github.com/openclaw/nix-openclaw) —— 完整设置指南
- [Wizard](/start/wizard) —— 非 Nix CLI 设置
- [Docker](/install/docker) —— 容器化设置