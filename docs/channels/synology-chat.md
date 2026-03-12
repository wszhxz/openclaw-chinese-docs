---
summary: "Synology Chat webhook setup and OpenClaw config"
read_when:
  - Setting up Synology Chat with OpenClaw
  - Debugging Synology Chat webhook routing
title: "Synology Chat"
---
# Synology Chat（插件）

状态：通过插件支持，作为使用 Synology Chat 网络钩子（webhook）的直接消息（DM）通道。  
该插件接收来自 Synology Chat 外发网络钩子的入站消息，并通过 Synology Chat 的入站网络钩子发送回复。

## 需要安装插件

Synology Chat 基于插件机制，不属于默认核心通道安装的一部分。

从本地代码检出安装：

```bash
openclaw plugins install ./extensions/synology-chat
```

详情参见：[插件](/tools/plugin)

## 快速配置

1. 安装并启用 Synology Chat 插件。  
2. 在 Synology Chat 集成设置中：  
   - 创建一个入站网络钩子，并复制其 URL。  
   - 创建一个外发网络钩子，并设置您的密钥令牌（secret token）。  
3. 将外发网络钩子 URL 指向您的 OpenClaw 网关：  
   - 默认为 `https://gateway-host/webhook/synology`。  
   - 或您自定义的 `channels.synology-chat.webhookPath`。  
4. 在 OpenClaw 中配置 `channels.synology-chat`。  
5. 重启网关，并向 Synology Chat 机器人发送一条直接消息（DM）。

最小化配置示例：

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

对于默认账户，可使用以下环境变量：

- `SYNOLOGY_CHAT_TOKEN`  
- `SYNOLOGY_CHAT_INCOMING_URL`  
- `SYNOLOGY_NAS_HOST`  
- `SYNOLOGY_ALLOWED_USER_IDS`（以逗号分隔）  
- `SYNOLOGY_RATE_LIMIT`  
- `OPENCLAW_BOT_NAME`  

配置值优先级高于环境变量。

## 直接消息（DM）策略与访问控制

- `dmPolicy: "allowlist"` 是推荐的默认策略。  
- `allowedUserIds` 接受 Synology 用户 ID 列表（或以逗号分隔的字符串）。  
- 在 `allowlist` 模式下，若 `allowedUserIds` 列表为空，则视为配置错误，网络钩子路由将无法启动（如需允许全部用户，请使用 `dmPolicy: "open"`）。  
- `dmPolicy: "open"` 允许任意发送者。  
- `dmPolicy: "disabled"` 拒绝所有直接消息（DM）。  
- 配对审批（pairing approvals）支持以下模式：  
  - `openclaw pairing list synology-chat`  
  - `openclaw pairing approve synology-chat <CODE>`  

## 出站投递

目标须使用数字形式的 Synology Chat 用户 ID。

示例：

```bash
openclaw message send --channel synology-chat --target 123456 --text "Hello from OpenClaw"
openclaw message send --channel synology-chat --target synology-chat:123456 --text "Hello again"
```

媒体文件发送支持基于 URL 的文件交付方式。

## 多账户支持

多个 Synology Chat 账户可在 `channels.synology-chat.accounts` 下配置。  
每个账户均可覆盖令牌（token）、入站 URL、网络钩子路径、DM 策略及限制。

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

## 安全注意事项

- 请妥善保管 `token` 并在泄露时及时轮换。  
- 除非您明确信任自签名的本地 NAS 证书，否则请勿启用 `allowInsecureSsl: false`。  
- 所有入站网络钩子请求均经过令牌验证，并按发送方进行速率限制。  
- 生产环境中建议优先使用 `dmPolicy: "allowlist"`。