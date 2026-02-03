---
summary: "LINE Messaging API plugin setup, config, and usage"
read_when:
  - You want to connect OpenClaw to LINE
  - You need LINE webhook + credential setup
  - You want LINE-specific message options
title: LINE
---
# LINE（插件）

LINE 通过 LINE 消息 API 与 OpenClaw 连接。该插件作为网关上的 Webhook 接收器运行，并使用您的频道访问令牌 + 频道密钥进行身份验证。

状态：通过插件支持。支持直接消息、群聊、媒体、位置、Flex 消息、模板消息和快速回复。不支持反应和线程。

## 必需插件

安装 LINE 插件：

```bash
openclaw plugins install @openclaw/line
```

本地检出（当从 git 仓库运行时）：

```bash
openclaw plugins install ./extensions/line
```

## 配置

1. 创建 LINE 开发者账户并打开控制台：
   https://developers.line.biz/console/
2. 创建（或选择）一个提供者并添加一个 **消息 API** 频道。
3. 从频道设置中复制 **频道访问令牌** 和 **频道密钥**。
4. 在消息 API 设置中启用 **使用 Webhook**。
5. 将 Webhook URL 设置为您的网关端点（需要 HTTPS）：

```
https://gateway-host/line/webhook
```

网关响应 LINE 的 Webhook 验证（GET）和入站事件（POST）。如果需要自定义路径，请设置 `channels.line.webhookPath` 或
`channels.line.accounts.<id>.webhookPath`，并相应更新 URL。

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

环境变量（仅默认账户）：

- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_CHANNEL_SECRET`

令牌/密钥文件：

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

多个账户：

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

直接消息默认使用配对。未知发送者会收到配对码，其消息在批准前将被忽略。

```bash
openclaw pairing list line
openclaw pairing approve line <CODE>
```

允许列表和策略：

- `channels.line.dmPolicy`: `pairing | allowlist | open | disabled`
- `channels.line.allowFrom`: 允许的 LINE 用户 ID 用于直接消息
- `channels.line.groupPolicy`: `allowlist | open | disabled`
- `channels.line.groupAllowFrom`: 允许的 LINE 用户 ID 用于群组
- 每个群组的覆盖：`channels.line.groups.<groupId>.allowFrom`

LINE ID 是大小写敏感的。有效的 ID 格式如下：

- 用户: `U` + 32 个十六进制字符
- 群组: `C` + 32 个十六进制字符
- 房间: `R` + 32 个十六进制字符

## 消息行为

- 文本在 5000 个字符处分块。
- Markdown 格式化被剥离；代码块和表格在可能的情况下转换为 Flex 卡片。
- 流式响应会被缓冲；LINE 在代理工作期间会收到完整的分块并显示加载动画。
- 媒体下载受 `channels.line.mediaMaxMb` 限制（默认为 10 MB）。

## 频道数据（丰富消息）

使用 `channelData.line` 发送快速回复、位置、Flex 卡片或模板消息。

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

LINE 插件还提供一个 `/card` 命令用于 Flex 消息预设：

```
/card info "Welcome" "Thanks for joining!"
```

## 故障排除

- **Webhook 验证失败：** 确保 Webhook URL 是 HTTPS 并且 `channelSecret` 与 LINE 控制台匹配。
- **没有入站事件：** 确认 Webhook 路径与 `channels.line.webhookPath` 匹配，并且网关可以从 LINE 访问。
- **媒体下载错误：** 如果媒体超过默认限制，请提高 `channels.line.mediaMaxMb`。