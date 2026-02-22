---
summary: "Overview of OpenClaw onboarding options and flows"
read_when:
  - Choosing an onboarding path
  - Setting up a new environment
title: "Onboarding Overview"
sidebarTitle: "Onboarding Overview"
---
# 入门概述

OpenClaw 支持多种入门路径，具体取决于 Gateway 的运行位置以及您希望如何配置提供商。

## 选择您的入门路径

- **CLI 向导** 适用于 macOS、Linux 和 Windows（通过 WSL2）。
- **macOS 应用程序** 适用于 Apple 芯片或 Intel Mac 上的引导式首次运行。

## CLI 入门向导

在终端中运行向导：

```bash
openclaw onboard
```

当您希望完全控制 Gateway、工作区、通道和技能时，请使用 CLI 向导。文档：

- [入门向导 (CLI)](/start/wizard)
- [`openclaw onboard` 命令](/cli/onboard)

## macOS 应用程序入门

当您希望在 macOS 上进行完全引导式设置时，请使用 OpenClaw 应用程序。文档：

- [入门 (macOS 应用程序)](/start/onboarding)

## 自定义提供商

如果您需要一个未列出的端点，包括暴露标准 OpenAI 或 Anthropic API 的托管提供商，请在 CLI 向导中选择 **自定义提供商**。您将被要求：

- 选择 OpenAI 兼容、Anthropic 兼容或 **未知**（自动检测）。
- 输入基础 URL 和 API 密钥（如果提供商需要）。
- 提供模型 ID 和可选别名。
- 选择一个 Endpoint ID 以便多个自定义端点可以共存。

有关详细步骤，请参阅上述 CLI 入门文档。