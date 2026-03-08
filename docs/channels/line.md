---
summary: "LINE Messaging API plugin setup, config, and usage"
read_when:
  - You want to connect OpenClaw to LINE
  - You need LINE webhook + credential setup
  - You want LINE-specific message options
title: LINE
---
# LINE (插件)

LINE 通过 LINE Messaging API 连接到 OpenClaw。该插件在 Gateway 上作为 Webhook 接收器运行，并使用您的 Channel access token + Channel secret 进行身份验证。

状态：通过插件支持。支持 Direct messages、群组聊天、媒体、位置、Flex messages、模板消息和 quick replies。不支持 Reactions 和 threads。

## 需要插件

安装 LINE 插件：

```bash
openclaw plugins install @openclaw/line
```

Local checkout (when running from a git repo):

```bash
openclaw plugins install ./extensions/line
```

## 设置

1. 创建 LINE Developers 账户并打开 Console：
   [https://developers.line.biz/console/](https://developers.line.biz/console/)
2. 创建（或选择）一个 Provider 并添加 **Messaging API** 渠道。
3. 从渠道设置中复制 **Channel access token** 和 **Channel secret**。
4. 在 Messaging API 设置中启用 **Use webhook**。
5. 将 Webhook URL 设置为您的 Gateway 端点（需要 HTTPS）：

```
https://gateway-host/line/webhook
```

Gateway 响应 LINE 的 Webhook 验证（GET）和入站事件（POST）。
如果需要自定义路径，设置 `channels.line.webhookPath` 或
`channels.line.accounts.<id>.webhookPath` 并相应更新 URL。

安全提示：

- LINE 签名验证依赖于主体（基于原始主体的 HMAC），因此 OpenClaw 应用严格的预认证主体限制和超时。

## 配置

最小配置：

```json5
{
  channels: {
    line: {
      enabled: true,
      channelAccessToken: "LINE_CHANNEL_ACCESS_TOKEN",
      channelSecret: "LINE_CHANNEL_SECRET",
      dmPolicy: "pairing",
    },
  },
}
```

Env vars (default account only):

- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_CHANNEL_SECRET`

Token/secret files:

```json5
{
  channels: {
    line: {
      tokenFile: "/path/to/line-token.txt",
      secretFile: "/path/to/line-secret.txt",
    },
  },
}
```

Multiple accounts:

```json5
{
  channels: {
    line: {
      accounts: {
        marketing: {
          channelAccessToken: "...",
          channelSecret: "...",
          webhookPath: "/line/marketing",
        },
      },
    },
  },
}
```

## 访问控制

Direct messages 默认为配对。未知发送者会获得配对码，其消息在批准前会被忽略。

```bash
openclaw pairing list line
openclaw pairing approve line <CODE>
```

Allowlists and policies:

- `channels.line.dmPolicy`: `pairing | allowlist | open | disabled`
- `channels.line.allowFrom`: 用于 DMs 的允许列表 LINE user IDs
- `channels.line.groupPolicy`: `allowlist | open | disabled`
- `channels.line.groupAllowFrom`: 用于群组的允许列表 LINE user IDs
- Per-group overrides: `channels.line.groups.<groupId>.allowFrom`
- Runtime note: if `channels.line` is completely missing, runtime falls back to `groupPolicy="allowlist"` for group checks (even if `channels.defaults.groupPolicy` is set).

LINE IDs are case-sensitive. Valid IDs look like:

- User: `U` + 32 hex chars
- Group: `C` + 32 hex chars
- Room: `R` + 32 hex chars

## 消息行为

- Text is chunked at 5000 characters.
- Markdown formatting is stripped; code blocks and tables are converted into Flex
  cards when possible.
- Streaming responses are buffered; LINE receives full chunks with a loading
  animation while the agent works.
- Media downloads are capped by `channels.line.mediaMaxMb` (default 10).

## Channel data (rich messages)

Use `channelData.line` to send quick replies, locations, Flex cards, or template
messages.

```json5
{
  text: "Here you go",
  channelData: {
    line: {
      quickReplies: ["Status", "Help"],
      location: {
        title: "Office",
        address: "123 Main St",
        latitude: 35.681236,
        longitude: 139.767125,
      },
      flexMessage: {
        altText: "Status card",
        contents: {
          /* Flex payload */
        },
      },
      templateMessage: {
        type: "confirm",
        text: "Proceed?",
        confirmLabel: "Yes",
        confirmData: "yes",
        cancelLabel: "No",
        cancelData: "no",
      },
    },
  },
}
```

The LINE plugin also ships a `/card` command for Flex message presets:

```
/card info "Welcome" "Thanks for joining!"
```

## Troubleshooting

- **Webhook verification fails:** ensure the webhook URL is HTTPS and the
  `channelSecret` matches the LINE console.
- **No inbound events:** confirm the webhook path matches `channels.line.webhookPath`
  and that the gateway is reachable from LINE.
- **Media download errors:** raise `channels.line.mediaMaxMb` if media exceeds the
  default limit.