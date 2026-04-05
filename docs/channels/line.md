---
summary: "LINE Messaging API plugin setup, config, and usage"
read_when:
  - You want to connect OpenClaw to LINE
  - You need LINE webhook + credential setup
  - You want LINE-specific message options
title: LINE
---
# LINE

LINE 通过 LINE Messaging API 连接到 OpenClaw。该插件作为网关上的 webhook 接收器运行，并使用您的 channel access token + channel secret 进行身份验证。

状态：捆绑插件。支持直接消息、群聊、媒体、位置、Flex 消息、模板消息和快速回复。不支持反应和线程。

## 捆绑插件

LINE 作为捆绑插件随当前 OpenClaw 版本发布，因此常规打包构建无需单独安装。

如果您使用的是旧版构建或排除了 LINE 的自定义安装，请手动安装：

```bash
openclaw plugins install @openclaw/line
```

本地检出（从 git 仓库运行时）：

```bash
openclaw plugins install ./path/to/local/line-plugin
```

## 设置

1. 创建 LINE Developers 账户并打开 Console：
   [https://developers.line.biz/console/](https://developers.line.biz/console/)
2. 创建（或选择）一个 Provider 并添加一个 **Messaging API** 频道。
3. 从频道设置中复制 **Channel access token** 和 **Channel secret**。
4. 在 Messaging API 设置中启用 **Use webhook**。
5. 将 webhook URL 设置为您的网关端点（需要 HTTPS）：

```
https://gateway-host/line/webhook
```

网关响应 LINE 的 webhook 验证（GET）和传入事件（POST）。
如果需要自定义路径，请设置 `channels.line.webhookPath` 或
`channels.line.accounts.<id>.webhookPath` 并相应更新 URL。

安全说明：

- LINE 签名验证依赖于正文（对原始正文进行 HMAC），因此 OpenClaw 在验证前应用严格的预认证正文限制和超时。
- OpenClaw 处理来自已验证原始请求字节的 webhook 事件。出于签名完整性安全考虑，上游中间件转换的 `req.body` 值将被忽略。

## 配置

最小化配置：

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

环境变量（仅限默认账户）：

- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_CHANNEL_SECRET`

Token/secret 文件：

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

`tokenFile` 和 `secretFile` 必须指向普通文件。符号链接将被拒绝。

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

直接消息默认为配对模式。未知发送者会收到配对码，其消息在被批准前将被忽略。

```bash
openclaw pairing list line
openclaw pairing approve line <CODE>
```

白名单和政策：

- `channels.line.dmPolicy`: `pairing | allowlist | open | disabled`
- `channels.line.allowFrom`: DM 的允许 LINE 用户 ID
- `channels.line.groupPolicy`: `allowlist | open | disabled`
- `channels.line.groupAllowFrom`: 群组的允许 LINE 用户 ID
- 每组覆盖：`channels.line.groups.<groupId>.allowFrom`
- 运行时说明：如果 `channels.line` 完全缺失，运行时将回退到 `groupPolicy="allowlist"` 进行群组检查（即使设置了 `channels.defaults.groupPolicy`）。

LINE ID 区分大小写。有效 ID 如下所示：

- 用户：`U` + 32 个十六进制字符
- 群组：`C` + 32 个十六进制字符
- 房间：`R` + 32 个十六进制字符

## 消息行为

- 文本按 5000 个字符分块。
- Markdown 格式被移除；代码块和表格在可能时转换为 Flex 卡片。
- 流式响应会被缓冲；当代理工作时，LINE 接收带有加载动画的完整块。
- 媒体下载受 `channels.line.mediaMaxMb` 限制（默认 10）。

## 频道数据（富消息）

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

LINE 插件还附带一个用于 Flex 消息预设的 `/card` 命令：

```
/card info "Welcome" "Thanks for joining!"
```

## ACP 支持

LINE 支持 ACP（Agent Communication Protocol）对话绑定：

- `/acp spawn <agent> --bind here` 将当前 LINE 聊天绑定到 ACP 会话，而不会创建子线程。
- 配置的 ACP 绑定和活动的对话绑定 ACP 会话在 LINE 上像其他对话频道一样工作。

详见 [ACP agents](/tools/acp-agents)。

## 出站媒体

LINE 插件支持通过代理消息工具发送图片、视频和音频文件。媒体通过 LINE 特定的交付路径发送，并进行适当的预览和跟踪处理：

- **图片**：作为 LINE 图片消息发送，自动生成预览。
- **视频**：发送时包含明确的预览和内容类型处理。
- **音频**：作为 LINE 音频消息发送。

当没有 LINE 特定路径可用时，通用媒体发送将回退到现有的仅图片路由。

## 故障排除

- **Webhook 验证失败：** 确保 webhook URL 为 HTTPS 且 `channelSecret` 与 LINE Console 匹配。
- **无传入事件：** 确认 webhook 路径与 `channels.line.webhookPath` 匹配，并且网关可从 LINE 访问。
- **媒体下载错误：** 如果媒体超过默认限制，请提高 `channels.line.mediaMaxMb`。

## 相关

- [Channels Overview](/channels) — 所有支持的频道
- [Pairing](/channels/pairing) — DM 身份验证和配对流程
- [Groups](/channels/groups) — 群聊行为和提及门控
- [Channel Routing](/channels/channel-routing) — 消息的会话路由
- [Security](/gateway/security) — 访问模型和加固