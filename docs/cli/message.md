---
summary: "CLI reference for `openclaw message` (send + channel actions)"
read_when:
  - Adding or modifying message CLI actions
  - Changing outbound channel behavior
title: "message"
---
# `openclaw message`

用于发送消息和频道操作的单一出站命令
(Discord/Google Chat/Slack/Mattermost (插件)/Telegram/WhatsApp/Signal/iMessage/MS Teams)。

## 使用方法

```
openclaw message <subcommand> [flags]
```

频道选择：

- 如果配置了多个频道，则需要`--channel`。
- 如果恰好配置了一个频道，则该频道成为默认频道。
- 值：`whatsapp|telegram|discord|googlechat|slack|mattermost|signal|imessage|msteams` (Mattermost 需要插件)

目标格式 (`--target`)：

- WhatsApp: E.164 或群组 JID
- Telegram: 聊天 ID 或 `@username`
- Discord: `channel:<id>` 或 `user:<id>` (或 `<@id>` 提及；纯数字 ID 视为频道)
- Google Chat: `spaces/<spaceId>` 或 `users/<userId>`
- Slack: `channel:<id>` 或 `user:<id>` (接受纯频道 ID)
- Mattermost (插件): `channel:<id>`, `user:<id>`, 或 `@username` (裸 ID 视为频道)
- Signal: `+E.164`, `group:<id>`, `signal:+E.164`, `signal:group:<id>`, 或 `username:<name>`/`u:<name>`
- iMessage: 处理程序, `chat_id:<id>`, `chat_guid:<guid>`, 或 `chat_identifier:<id>`
- MS Teams: 对话 ID (`19:...@thread.tacv2`) 或 `conversation:<id>` 或 `user:<aad-object-id>`

名称查找：

- 对于支持的提供商（Discord/Slack 等），通过目录缓存解析类似 `Help` 或 `#help` 的频道名称。
- 在缓存未命中时，OpenClaw 将尝试进行实时目录查找（如果提供商支持）。

## 常见标志

- `--channel <name>`
- `--account <id>`
- `--target <dest>` (发送/轮询/读取等的目标频道或用户)
- `--targets <name>` (重复；仅限广播)
- `--json`
- `--dry-run`
- `--verbose`

## 操作

### 核心

- `send`
  - 频道: WhatsApp/Telegram/Discord/Google Chat/Slack/Mattermost (插件)/Signal/iMessage/MS Teams
  - 必需: `--target`, 加上 `--message` 或 `--media`
  - 可选: `--media`, `--reply-to`, `--thread-id`, `--gif-playback`
  - 仅 Telegram: `--buttons` (需要 `channels.telegram.capabilities.inlineButtons` 允许)
  - 仅 Telegram: `--thread-id` (论坛主题 ID)
  - 仅 Slack: `--thread-id` (线程时间戳；`--reply-to` 使用同一字段)
  - 仅 WhatsApp: `--gif-playback`

- `poll`
  - 频道: WhatsApp/Discord/MS Teams
  - 必需: `--target`, `--poll-question`, `--poll-option` (重复)
  - 可选: `--poll-multi`
  - 仅 Discord: `--poll-duration-hours`, `--message`

- `react`
  - 频道: Discord/Google Chat/Slack/Telegram/WhatsApp/Signal
  - 必需: `--message-id`, `--target`
  - 可选: `--emoji`, `--remove`, `--participant`, `--from-me`, `--target-author`, `--target-author-uuid`
  - 注意: `--remove` 需要 `--emoji` (省略 `--emoji` 以清除自己的反应（如受支持）；参见 /tools/reactions)
  - 仅 WhatsApp: `--participant`, `--from-me`
  - Signal 群组反应: 需要 `--target-author` 或 `--target-author-uuid`

- `reactions`
  - 频道: Discord/Google Chat/Slack
  - 必需: `--message-id`, `--target`
  - 可选: `--limit`

- `read`
  - 频道: Discord/Slack
  - 必需: `--target`
  - 可选: `--limit`, `--before`, `--after`
  - 仅 Discord: `--around`

- `edit`
  - 频道: Discord/Slack
  - 必需: `--message-id`, `--message`, `--target`

- `delete`
  - 频道: Discord/Slack/Telegram
  - 必需: `--message-id`, `--target`

- `pin` / `unpin`
  - 频道: Discord/Slack
  - 必需: `--message-id`, `--target`

- `pins` (列表)
  - 频道: Discord/Slack
  - 必需: `--target`

- `permissions`
  - 频道: Discord
  - 必需: `--target`

- `search`
  - 频道: Discord
  - 必需: `--guild-id`, `--query`
  - 可选: `--channel-id`, `--channel-ids` (重复), `--author-id`, `--author-ids` (重复), `--limit`

### 线程

- `thread create`
  - 频道: Discord
  - 必需: `--thread-name`, `--target` (频道 ID)
  - 可选: `--message-id`, `--message`, `--auto-archive-min`

- `thread list`
  - 频道: Discord
  - 必需: `--guild-id`
  - 可选: `--channel-id`, `--include-archived`, `--before`, `--limit`

- `thread reply`
  - 频道: Discord
  - 必需: `--target` (线程 ID), `--message`
  - 可选: `--media`, `--reply-to`

### 表情符号

- `emoji list`
  - Discord: `--guild-id`
  - Slack: 无需额外标志

- `emoji upload`
  - 频道: Discord
  - 必需: `--guild-id`, `--emoji-name`, `--media`
  - 可选: `--role-ids` (重复)

### 贴纸

- `sticker send`
  - 频道: Discord
  - 必需: `--target`, `--sticker-id` (重复)
  - 可选: `--message`

- `sticker upload`
  - 频道: Discord
  - 必需: `--guild-id`, `--sticker-name`, `--sticker-desc`, `--sticker-tags`, `--media`

### 角色 / 频道 / 成员 / 语音

- `role info` (Discord): `--guild-id`
- `role add` / `role remove` (Discord): `--guild-id`, `--user-id`, `--role-id`
- `channel info` (Discord): `--target`
- `channel list` (Discord): `--guild-id`
- `member info` (Discord/Slack): `--user-id` (+ `--guild-id` 用于 Discord)
- `voice status` (Discord): `--guild-id`, `--user-id`

### 事件

- `event list` (Discord): `--guild-id`
- `event create` (Discord): `--guild-id`, `--event-name`, `--start-time`
  - 可选: `--end-time`, `--desc`, `--channel-id`, `--location`, `--event-type`

### 管理 (Discord)

- `timeout`: `--guild-id`, `--user-id` (可选 `--duration-min` 或 `--until`；省略两者以清除超时)
- `kick`: `--guild-id`, `--user-id` (+ `--reason`)
- `ban`: `--guild-id`, `--user-id` (+ `--delete-days`, `--reason`)
  - `timeout` 还支持 `--reason`

### 广播

- `broadcast`
  - 频道: 任何已配置的频道；使用 `--channel all` 目标所有提供商
  - 必需: `--targets` (重复)
  - 可选: `--message`, `--media`, `--dry-run`

## 示例

发送 Discord 回复：

```
openclaw message send --channel discord \
  --target channel:123 --message "hi" --reply-to 456
```

创建 Discord 投票：

```
openclaw message poll --channel discord \
  --target channel:123 \
  --poll-question "Snack?" \
  --poll-option Pizza --poll-option Sushi \
  --poll-multi --poll-duration-hours 48
```

发送 Teams 主动消息：

```
openclaw message send --channel msteams \
  --target conversation:19:abc@thread.tacv2 --message "hi"
```

创建 Teams 投票：

```
openclaw message poll --channel msteams \
  --target conversation:19:abc@thread.tacv2 \
  --poll-question "Lunch?" \
  --poll-option Pizza --poll-option Sushi
```

在 Slack 中反应：

```
openclaw message react --channel slack \
  --target C123 --message-id 456 --emoji "✅"
```

在 Signal 群组中反应：

```
openclaw message react --channel signal \
  --target signal:group:abc123 --message-id 1737630212345 \
  --emoji "✅" --target-author-uuid 123e4567-e89b-12d3-a456-426614174000
```

发送 Telegram 内联按钮：

```
openclaw message send --channel telegram --target @mychat --message "Choose:" \
  --buttons '[ [{"text":"Yes","callback_data":"cmd:yes"}], [{"text":"No","callback_data":"cmd:no"}] ]'
```