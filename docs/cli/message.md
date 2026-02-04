---

summary: "CLI reference for `openclaw message` (send + channel actions)"
read_when:
  - Adding or modifying message CLI actions
  - Changing outbound channel behavior
title: "message"

---
# `openclaw message`

发送消息和频道操作的单向命令
(Discord/Google Chat/Slack/Mattermost (插件)/Telegram/WhatsApp/Signal/iMessage/MS Teams).

## 使用方法

```
openclaw message <subcommand> [flags]
```

频道选择:

- `--channel` 需要多个频道配置时必填。
- 如果仅配置一个频道，该频道将成为默认频道。
- 取值: `whatsapp|telegram|discord|googlechat|slack|mattermost|signal|imessage|msteams` (Mattermost 需要插件)

目标格式 (`--target`):

- WhatsApp: E.164 或群组 JID
- Telegram: chat id 或 `@username`
- Discord: `channel:<id>` 或 `user:<id>` (或 `<@id>` 提及; 原始 ID 保留)
- Google Chat: 会话 ID
- Slack: 原始 ID
- MS Teams: 原始 ID

名称查找:

- 使用目录缓存进行快速查找
- 缓存未命中时会进行网络查询

常用标志:

- `--channel <name>` 
- `--account <id>` 
- `--target <dest>` 
- `--targets <name>` 
- `--json` 
- `--dry-run` 
- `--verbose` 

操作:

核心操作:

- `send` 
- `--target` 
- `--message` 
- `--media` 
- `--media` 
- `--reply-to` 
- `--thread-id` 
- `--gif-playback` 
- `--buttons` 
- `channels.telegram.capabilities.inlineButtons` 
- `--thread-id` 
- `--thread-id` 
- `--reply-to` 
- `--gif-playback` 
- `poll` 
- `--target` 
- `--poll-question` 
- `--poll-option` 
- `--poll-multi` 
- `--poll-duration-hours` 
- `--message` 
- `react` 
- `--message-id` 
- `--target` 
- `--emoji` 
- `--remove` 
- `--participant` 
- `--from-me` 
- `--target-author` 
- `--target-author-uuid` 
- `--remove` 
- `--emoji` 
- `--emoji` 
- `--participant` 
- `--from-me` 
- `--target-author` 
- `--target-author-uuid` 
- `reactions` 
- `--message-id` 
- `--target` 
- `--limit` 
- `read` 
- `--target` 
- `--limit` 
- `--before` 
- `--after` 
- `--around` 
- `edit` 
- `--message-id` 
- `--message` 
- `--target` 
- `delete` 
- `--message-id` 
- `--target` 
- `pin` 
- `unpin` 
- `--message-id` 
- `--target` 
- `pins` 
- `--target` 
- `permissions` 
- `--target` 
- `search` 
- `--guild-id` 
- `--query` 
- `--channel-id` 
- `--channel-ids` 
- `--author-id` 
- `--author-ids` 
- `--limit` 
- `thread create` 
- `--thread-name` 
- `--target` 
- `--message-id` 
- `--auto-archive-min` 
- `thread list` 
- `--guild-id` 
- `--channel-id` 
- `--include-archived` 
- `--before` 
- `--limit` 
- `thread reply` 
- `--target` 
- `--message` 
- `--media` 
- `--reply-to` 

线程操作:

- `emoji list` 
- `--guild-id` 
- `emoji upload` 
- `--guild-id` 
- `--emoji-name` 
- `--media` 
- `--role-ids` 
- `sticker send` 
- `--target` 
- `--sticker-id` 
- `--message` 
- `sticker upload` 
- `--guild-id` 
- `--sticker-name` 
- `--sticker-desc` 
- `--sticker-tags` 
- `--media` 
- `role info` 
- `--guild-id` 
- `role add` 
- `role remove` 
- `--guild-id` 
- `--user-id` 
- `--role-id` 
- `channel info` 
- `--target` 
- `channel list` 
- `--guild-id` 
- `member info` 
- `--user-id` (+ `--guild-id` 用于 Discord)
- `voice status` 
- `--guild-id` 
- `--user-id` 

事件操作:

- `event list` 
- `--guild-id` 
- `event create` 
- `--guild-id` 
- `--event-name` 
- `--start-time` 
  - 可选: `--end-time` 
  - 可选: `--desc` 
  - 可选: `--channel-id` 
  - 可选: `--location` 
  - 可选: `--event-type` 

管理 (Discord):

- `timeout` : `--guild-id` , `--user-id` (可选 `--duration-min` 或 `--until` ; 省略两者则清除超时)
- `kick` : `--guild-id` , `--user-id` (+ `--reason` )
- `ban` : `--guild-id` , `--user-id` (+ `--delete-days` , `--reason` )
  - `timeout` 也支持 `--reason` 

广播:

- `broadcast` 
  - 频道: 任意配置的频道; 使用 `--channel all` 指定所有提供方
  - 必填: `--targets` (重复)
  - 可选: `--message` , `--media` , `--dry-run` 

示例

发送 Discord 回复:

```
openclaw message send --channel discord \
  --target channel:123 --message "hi" --reply-to 456
```

创建 Discord 投票:

```
openclaw message poll --channel discord \
  --target channel:123 \
  --poll-question "Snack?" \
  --poll-option Pizza --poll-option Sushi \
  --poll-multi --poll-duration-hours 48
```

发送 Teams 主动消息:

```
openclaw message send --channel msteams \
  --target conversation:19:abc@thread.tacv2 --message "hi"
```

创建 Teams 投票:

```
openclaw message poll --channel msteams \
  --target conversation:19:abc@thread.tacv2 \
  --poll-question "Lunch?" \
  --poll-option Pizza --poll-option Sushi
```

在 Slack 中反应:

```
openclaw message react --channel slack \
  --target C123 --message-id 456 --emoji "✅"
```

在 Signal 群组中反应:

```
openclaw message react --channel signal \
  --target signal:group:abc123 --message-id 1737630212345 \
  --emoji "✅" --target-author-uuid 123e4567-e89b-12d3-a456-426614174000
```

发送 Telegram 内联按钮:

```
openclaw message send --channel telegram --target @mychat --message "Choose:" \
  --buttons '[ [{"text":"Yes","callback_data":"cmd:yes"}], [{"text":"No","callback_data":"cmd:no"}] ]'
```