---
summary: "Synology Chat webhook setup and OpenClaw config"
read_when:
  - Setting up Synology Chat with OpenClaw
  - Debugging Synology Chat webhook routing
title: "Synology Chat"
---
# Synology Chat (plugin)

状态：通过 plugin 支持，作为使用 Synology Chat webhooks 的 DM 通道。
该 plugin 接受来自 Synology Chat outgoing webhooks 的入站消息并发送回复
通过 Synology Chat incoming webhook。

## 需要 Plugin

Synology Chat 基于 plugin，不属于默认 core channel 安装的一部分。

从本地 checkout 安装：

```bash
openclaw plugins install ./extensions/synology-chat
```

详情：[Plugins](/tools/plugin)

## 快速设置

1. 安装并启用 Synology Chat plugin。
2. 在 Synology Chat integrations 中：
   - 创建一个 incoming webhook 并复制其 URL。
   - 创建一个带有 secret token 的 outgoing webhook。
3. 将 outgoing webhook URL 指向您的 OpenClaw gateway：
   - 默认为 `https://gateway-host/webhook/synology`。
   - 或您的自定义 `channels.synology-chat.webhookPath`。
4. 在 OpenClaw 中配置 `channels.synology-chat`。
5. 重启 gateway 并向 Synology Chat bot 发送 DM。

最小配置：

```json5
{
  channels: {
    "synology-chat": {
      enabled: true,
      token: "synology-outgoing-token",
      incomingUrl: "https://nas.example.com/webapi/entry.cgi?api=SYNO.Chat.External&method=incoming&version=2&token=...",
      webhookPath: "/webhook/synology",
      dmPolicy: "allowlist",
      allowedUserIds: ["123456"],
      rateLimitPerMinute: 30,
      allowInsecureSsl: false,
    },
  },
}
```

## 环境变量

对于默认账户，您可以使用 env vars：

- `SYNOLOGY_CHAT_TOKEN`
- `SYNOLOGY_CHAT_INCOMING_URL`
- `SYNOLOGY_NAS_HOST`
- `SYNOLOGY_ALLOWED_USER_IDS` (comma-separated)
- `SYNOLOGY_RATE_LIMIT`
- `OPENCLAW_BOT_NAME`

Config 值覆盖 env vars。

## DM 策略和访问控制

- `dmPolicy: "allowlist"` 是推荐的默认值。
- `allowedUserIds` 接受 Synology user IDs 列表（或逗号分隔的字符串）。
- 在 `allowlist` 模式下，空的 `allowedUserIds` 列表被视为配置错误，webhook 路由将不会启动（使用 `dmPolicy: "open"` 表示 allow-all）。
- `dmPolicy: "open"` 允许任何发送者。
- `dmPolicy: "disabled"` 阻止 DMs。
- 配对批准适用于：
  - `openclaw pairing list synology-chat`
  - `openclaw pairing approve synology-chat <CODE>`

## 出站发送

使用数字 Synology Chat user IDs 作为目标。

示例：

```bash
openclaw message send --channel synology-chat --target 123456 --text "Hello from OpenClaw"
openclaw message send --channel synology-chat --target synology-chat:123456 --text "Hello again"
```

媒体发送支持基于 URL 的文件交付。

## 多账户

在 `channels.synology-chat.accounts` 下支持多个 Synology Chat 账户。
每个账户可以覆盖 token、incoming URL、webhook path、DM 策略和 limits。

```json5
{
  channels: {
    "synology-chat": {
      enabled: true,
      accounts: {
        default: {
          token: "token-a",
          incomingUrl: "https://nas-a.example.com/...token=...",
        },
        alerts: {
          token: "token-b",
          incomingUrl: "https://nas-b.example.com/...token=...",
          webhookPath: "/webhook/synology-alerts",
          dmPolicy: "allowlist",
          allowedUserIds: ["987654"],
        },
      },
    },
  },
}
```

## 安全说明

- 保持 `token` 机密，如果泄露则轮换它。
- 保持 `allowInsecureSsl: false` 除非您明确信任自签名的本地 NAS cert。
- 入站 webhook 请求经过 token 验证并按发送者进行 rate-limited。
- 生产环境推荐使用 `dmPolicy: "allowlist"`。