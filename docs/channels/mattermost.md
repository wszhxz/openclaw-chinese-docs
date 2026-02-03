---
summary: "Mattermost bot setup and OpenClaw config"
read_when:
  - Setting up Mattermost
  - Debugging Mattermost routing
title: "Mattermost"
---
共<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context. The content is about setting up Mattermost as a plugin for OpenClaw, including installation steps, configuration options, environment variables, chat modes, access control, and troubleshooting.

First, I'll translate the headers and section titles. Terms like "Mattermost (plugin)" should be "Mattermost（插件）". The status line mentions "supported via plugin (bot token + WebSocket events)", which I'll translate to "通过插件支持（机器人令牌 + WebSocket 事件）". 

Next, the paragraph about Mattermost being a self-hostable platform. I need to make sure technical terms like "self-hostable" are accurately translated. "Self-hostable" could be "可自行托管" and "team messaging platform" becomes "团队消息平台".

The "Plugin required" section has instructions on installation via CLI. I'll translate the commands, ensuring that the syntax remains correct. For example, "openclaw plugins install @openclaw/mattermost" becomes "openclaw plugins install @openclaw/mattermost".

In the "Quick setup" section, the steps are numbered. I'll maintain the numbering and translate each step. Terms like "bot token" are "机器人令牌" and "base URL" is "基础 URL".

The "Environment variables (default account)" part needs careful translation of variable names and their descriptions. For instance, "MATTERMOST_BOT_TOKEN" stays as is but with Chinese labels. 

For "Chat modes", the different modes like "oncall", "onmessage", and "onchar" should be translated but kept in English as they are specific terms. The explanation for each mode should be clear in Chinese.

The "Access control (DMs)" section discusses policies like "pairing" and "open". I'll translate these terms appropriately, ensuring that the meaning is preserved. For example, "pairing code" becomes "配对码".

In the "Channels (groups)" section, terms like "allowlist" and "open channels" need accurate translation. "Allowlist" could be "白名单" and "open channels" as "公开频道".

The "Targets for outbound delivery" part has specific formats like "channel:<id>" and "user:<id>". These should be translated but kept in their original format for clarity. 

The "Multi-account" section involves configuration examples. I'll ensure that the JSON structure is correctly translated and that terms like "accounts" and "default" are appropriately rendered.

Finally, the "Troubleshooting" section lists common issues. I'll translate each point, making sure that the solutions are clear. For example, "No replies in channels" becomes "频道中没有回复".

Throughout the translation, I'll maintain technical accuracy, use proper terminology, and ensure that the structure and formatting (like code blocks and lists) are preserved. I'll also check for consistency in terms and ensure that the translated text flows naturally in Chinese while retaining all the original information.
</think>

# Mattermost（插件）

状态：通过插件支持（机器人令牌 + WebSocket 事件）。支持频道、群组和私聊。
Mattermost 是一个可自行托管的团队消息平台；请访问 [mattermost.com](https://mattermost.com) 查看产品详情和下载信息。

## 所需插件

Mattermost 作为插件提供，不包含在核心安装中。

通过 CLI（npm 注册表）安装：

```bash
openclaw plugins install @openclaw/mattermost
```

本地检查（当从 git 仓库运行时）：

```bash
openclaw plugins install ./extensions/mattermost
```

如果在配置/引导过程中选择 Mattermost 并检测到 git 检出，OpenClaw 将自动提供本地安装路径。

详情：[插件](/plugin)

## 快速设置

1. 安装 Mattermost 插件。
2. 创建 Mattermost 机器人账户并复制 **机器人令牌**。
3. 复制 Mattermost **基础 URL**（例如，`https://chat.example.com`）。
4. 配置 OpenClaw 并启动网关。

最小配置：

```json5
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token",
      baseUrl: "https://chat.example.com",
      dmPolicy: "pairing",
    },
  },
}
```

## 环境变量（默认账户）

如果偏好使用环境变量，请在网关主机上设置以下内容：

- `MATTERMOST_BOT_TOKEN=...`
- `MATTERMOST_URL=https://chat.example.com`

环境变量仅适用于 **默认** 账户（`default`）。其他账户必须使用配置值。

## 聊天模式

Mattermost 会自动响应私聊。频道行为由 `chatmode` 控制：

- `oncall`（默认）：仅在频道中被 @ 提及时响应。
- `onmessage`：响应每个频道消息。
- `onchar`：当消息以触发前缀开头时响应。

配置示例：

```json5
{
  channels: {
    mattermost: {
      chatmode: "onchar",
      oncharPrefixes: [">", "!"],
    },
  },
}
```

说明：

- `onchar` 仍会响应显式的 @ 提及。
- `channels.mattermost.requireMention` 对于旧配置有效，但优先使用 `chatmode`。

## 访问控制（私聊）

- 默认：`channels.mattermost.dmPolicy = "pairing"`（未知发送者会收到配对码）。
- 通过以下方式批准：
  - `openclaw pairing list mattermost`
  - `openclaw pairing approve mattermost <CODE>`
- 公开私聊：`channels.mattermost.dmPolicy="open"` 加上 `channels.mattermost.allowFrom=["*"]`。

## 频道（群组）

- 默认：`channels.mattermost.groupPolicy = "allowlist"`（需提及）。
- 通过 `channels.mattermost.groupAllowFrom` 允许发送者（用户 ID 或 `@username`）。
- 公开频道：`channels.mattermost.groupPolicy="open"`（需提及）。

## 出站消息目标

使用以下目标格式与 `openclaw message send` 或 cron/webhooks 一起使用：

- `channel:<id>` 表示频道
- `user:<id>` 表示私聊
- `@username` 表示私聊（通过 Mattermost API 解析）

纯 ID 被视为频道。

## 多账户

Mattermost 支持在 `channels.mattermost.accounts` 下的多个账户：

```json5
{
  channels: {
    mattermost: {
      accounts: {
        default: { name: "Primary", botToken: "mm-token", baseUrl: "https://chat.example.com" },
        alerts: { name: "Alerts", botToken: "mm-token-2", baseUrl: "https://alerts.example.com" },
      },
    },
  },
}
```

## 故障排除

- 频道中没有回复：确保机器人在频道中并被提及（oncall），使用触发前缀（onchar），或设置 `chatmode: "onmessage"`。
- 认证错误：检查机器人令牌、基础 URL 和账户是否启用。
- 多账户问题：环境变量仅适用于 `default` 账户。