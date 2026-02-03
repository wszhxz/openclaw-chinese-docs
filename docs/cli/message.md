---
summary: "CLI reference for `openclaw message` (send + channel actions)"
read_when:
  - Adding or modifying message CLI actions
  - Changing outbound channel behavior
title: "message"
---
# `openclaw message`

用于发送消息和频道操作的单向出站命令
(Discord/Google Chat/Slack/Mattermost (插件)/Telegram/WhatsApp/Signal/iMessage/MS Teams)

## 使用方式

```
openclaw message <子命令> [标志]
```

频道选择：

- 如果配置了多个频道，必须使用 `--channel`。
- 如果恰好配置了一个频道，它将成为默认频道。
- 可选值：`whatsapp|telegram|discord|googlechat|slack|mattermost|signal|imessage|msteams`（Mattermost 需要插件）

目标格式 (`--target`):

- WhatsApp: E.164 或群组 JID
- Telegram: 聊天 ID 或 `@用户名`
- Discord: `频道:<ID>` 或 `用户:<ID>`（或 `<@ID>` 提及；原始数字 ID 被视为频道）
- Google Chat: `spaces/<spaceId>` 或 `users/<userId>`
- Slack: `频道:<ID>` 或 `用户:<ID>`（原始频道 ID 可接受）
- Mattermost (插件): `频道:<ID>`、`用户:<ID>` 或 `@用户名`（原始 ID 被视为频道）
- Signal: `+E.164`、`群组:<ID>`、`signal:+E.164`、`signal:群组:<ID>` 或 `用户名:<名称>`/`u:<名称>`
- iMessage: 处理程序、`chat_id:<ID>`、`chat_guid:<guid>` 或 `chat_identifier:<ID>`
- MS Teams: 对话 ID (`19:...@thread.tacv2`) 或 `对话:<ID>` 或 `用户:<aad-object-id>`

名称查找：

- 对支持的提供者（Discord/Slack 等），`Help` 或 `#help` 等频道名称会通过目录缓存解析。
- 缓存未命中时，OpenClaw 会在提供者支持时尝试实时目录查找。

## 常用标志

- `--频道 <名称>`
- `--账户 <ID>`
- `--目标 <目标>`（发送/轮询/读取等的目标频道或用户）
- `--目标 <名称>`（重复；仅广播）
- `--json`
- `--模拟运行`
- `--详细`

## 操作

### 核心

- `发送`
  - 频道：WhatsApp/Telegram/Discord/Google Chat/Slack/Mattermost (插件)/Signal/iMessage/MS Teams
  - 必需：`--目标`，加上 `--消息` 或 `--媒体`
  - 可选：`--媒体`、`--回复至`、`--线程ID`、`--GIF播放`
  - 仅 Telegram：`--按钮`（需要 `channels.telegram.capabilities.inlineButtons` 来允许）
  - 仅 Telegram：`--线程ID`（论坛主题 ID）
  - 仅 Slack：`--线程ID`（线程时间戳；`--回复至` 使用相同字段）
  - 仅 WhatsApp：`--GIF播放`

- `轮询`
  - 频道：WhatsApp/Discord/MS Teams
  - 必需：`--目标`、`--轮询问题`、`--轮询选项`（重复）
  - 可选：`--轮询多选`
  - 仅 Discord：`--轮询持续小时数`、`--消息`

- `反应`
  - 频道：Discord/Google Chat/Slack/Telegram/WhatsApp/Signal
  - 必需：`--消息ID`、`--目标`
  - 可选：`--表情符号`、`--移除`、`--参与者`、`--来自我`、`--目标作者`、`--目标作者UUID`
  - 注意：`--移除` 需要 `--表情符号`（省略 `--表情符号` 可清除支持的自己的反应；参见 /tools/reactions）
  - 仅 WhatsApp：`--参与者`、`--来自我`
  - Signal 群组反应：需要 `--目标作者` 或 `--目标作者UUID`

- `反应列表`
  - 频道：Discord/Google Chat/Slack
  - 必需：`--消息ID`、`--目标`
  - 可选：`--限制`

- `读取`
  - 频道：Discord/Slack
  - 必需：`--目标`
  - 可选：`--限制`、`--之前`、`--之后`
  - 仅 Discord：`--周围`

- `编辑`
  - 频道：Discord/Slack
  - 必需：`--消息ID`、`--消息`、`--目标`

- `删除`
  - 频道：Discord/Slack/Telegram
  - 必需：`--消息ID`、`--目标`

- `固定` / `取消固定`
  - 频道：Discord/Slack
  - 必需：`--消息ID`、`--目标`

- `固定列表`（列出）
  - 频道：Discord/Slack
  - 必需：`--目标`

- `权限`
  - 频道：Discord
  - 必需：`--目标`

- `搜索`
  - 频道：Discord
  - 必需：`--公会ID`、`--查询`
  - 可选：`--频道ID`、`--频道IDs`（重复）、`--作者ID`、`--作者IDs`（重复）

## 操作

### 核心

- `发送`
  - 频道：WhatsApp/Telegram/Discord/Google Chat/Slack/Mattermost (插件)/Signal/iMessage/MS Teams
  - 必需：`--目标`，加上 `--消息` 或 `--媒体`
  - 可选：`--媒体`、`--回复至`、`--线程ID`、`--