---
summary: "Sign in to GitHub Copilot from OpenClaw using the device flow"
read_when:
  - You want to use GitHub Copilot as a model provider
  - You need the `openclaw models auth login-github-copilot` flow
title: "GitHub Copilot"
---
# GitHub Copilot

## 什么是 GitHub Copilot？

GitHub Copilot 是 GitHub 的 AI 编码助手。它为您的 GitHub 账户和计划提供对 Copilot 模型的访问权限。OpenClaw 可以通过两种不同的方式使用 Copilot 作为模型提供者。

## 在 OpenClaw 中使用 Copilot 的两种方式

### 1) 内置的 GitHub Copilot 提供者 (`github-copilot`)

使用原生的设备登录流程获取 GitHub 令牌，然后在 OpenClaw 运行时将其兑换为 Copilot API 令牌。这是 **默认** 且最简单的路径，因为它不需要 VS Code。

### 2) Copilot 代理插件 (`copilot-proxy`)

使用 **Copilot 代理** VS Code 插件作为本地桥接器。OpenClaw 与代理的 `/v1` 端点通信，并使用您在该位置配置的模型列表。当您已经在 VS Code 中运行 Copilot 代理或需要通过它进行路由时，请选择此方式。您必须启用该插件并保持 VS Code 插件运行。

使用 GitHub Copilot 作为模型提供者 (`github-copilot`)。登录命令运行 GitHub 设备流程，保存一个认证配置文件，并更新您的配置以使用该配置文件。

## CLI 设置

```bash
openclaw models auth login-github-copilot
```

您将被提示访问一个 URL 并输入一次性代码。请保持终端打开，直到操作完成。

### 可选标志

```bash
openclaw models auth login-github-copilot --profile-id github-copilot:work
openclaw models auth login-github-copilot --yes
```

## 设置默认模型

```bash
openclaw models set github-copilot/gpt-4o
```

### 配置片段

```json5
{
  agents: { defaults: { model: { primary: "github-copilot/gpt-4o" } } },
}
```

## 注意事项

- 需要交互式终端；请直接在终端中运行。
- Copilot 模型的可用性取决于您的计划；如果某个模型被拒绝，请尝试另一个 ID（例如 `github-copilot/gpt-4.1`）。
- 登录会将 GitHub 令牌存储在认证配置文件存储中，并在 OpenClaw 运行时将其兑换为 Copilot API 令牌。