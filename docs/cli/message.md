---
summary: "CLI reference for `openclaw message` (send + channel actions)"
read_when:
  - Adding or modifying message CLI actions
  - Changing outbound channel behavior
title: "message"
---
# `openclaw message`

用于发送消息及频道操作的单一出站命令  
（Discord / Google Chat / Slack / Mattermost（插件）/ Telegram / WhatsApp / Signal / iMessage / MS Teams）。

## 使用方法

```
openclaw message <subcommand> [flags]
```

频道选择：

- 若配置了多个频道，则必须指定 `--channel`。
- 若仅配置了一个频道，则该频道自动成为默认频道。
- 可选值：`whatsapp|telegram|discord|googlechat|slack|mattermost|signal|imessage|msteams`（Mattermost 需要插件支持）

目标格式（`--target`）：

- WhatsApp：E.164 格式号码或群组 JID  
- Telegram：聊天 ID 或 `@username`  
- Discord：`channel:<id>` 或 `user:<id>`（或 `<@id>` 提及；原始数字 ID 被视为频道）  
- Google Chat：`spaces/<spaceId>` 或 `users/<userId>`  
- Slack：`channel:<id>` 或 `user:<id>`（接受原始频道 ID）  
- Mattermost（插件）：`channel:<id>`、`user:<id>` 或 `@username`（裸 ID 被视为频道）  
- Signal：`+E.164`、`group:<id>`、`signal:+E.164`、`signal:group:<id>` 或 `username:<name>`/`u:<name>`  
- iMessage：句柄（handle）、`chat_id:<id>`、`chat_guid:<guid>` 或 `chat_identifier:<id>`  
- MS Teams：会话 ID（`19:...@thread.tacv2`）、`conversation:<id>` 或 `user:<aad-object-id>`

名称查找：

- 对于受支持的平台（Discord / Slack 等），类似 `Help` 或 `#help` 的频道名将通过目录缓存解析。  
- 若缓存未命中，且平台支持，OpenClaw 将尝试实时目录查找。

## 常用标志

- `--channel <name>`  
- `--account <id>`  
- `--target <dest>`（用于 send/poll/read 等操作的目标频道或用户）  
- `--targets <name>`（重复；仅限广播）  
- `--json`  
- `--dry-run`  
- `--verbose`  

## 操作

### 核心操作

- `send`  
  - 支持频道：WhatsApp / Telegram / Discord / Google Chat / Slack / Mattermost（插件）/ Signal / iMessage / MS Teams  
  - 必需参数：`--target`，以及 `--message` 或 `--media`  
  - 可选参数：`--media`、`--reply-to`、`--thread-id`、`--gif-playback`  
  - Telegram 专属：`--buttons`（需启用 `channels.telegram.capabilities.inlineButtons` 才允许使用）  
  - Telegram 专属：`--thread-id`（论坛主题 ID）  
  - Slack 专属：`--thread-id`（线程时间戳；`--reply-to` 使用同一字段）  
  - WhatsApp 专属：`--gif-playback`  

- `poll`  
  - 支持频道：WhatsApp / Telegram / Discord / Matrix / MS Teams  
  - 必需参数：`--target`、`--poll-question`、`--poll-option`（可重复）  
  - 可选参数：`--poll-multi`  
  - Discord 专属：`--poll-duration-hours`、`--silent`、`--message`  
  - Telegram 专属：`--poll-duration-seconds`（取值范围 5–600）、`--silent`、`--poll-anonymous` / `--poll-public`、`--thread-id`  

- `react`  
  - 支持频道：Discord / Google Chat / Slack / Telegram / WhatsApp / Signal  
  - 必需参数：`--message-id`、`--target`  
  - 可选参数：`--emoji`、`--remove`、`--participant`、`--from-me`、`--target-author`、`--target-author-uuid`  
  - 注意：`--remove` 需要 `--emoji`（如需清除自身反应，请省略 `--emoji`；详见 /tools/reactions）  
  - WhatsApp 专属：`--participant`、`--from-me`  
  - Signal 群组反应：必须指定 `--target-author` 或 `--target-author-uuid`  

- `reactions`  
  - 支持频道：Discord / Google Chat / Slack  
  - 必需参数：`--message-id`、`--target`  
  - 可选参数：`--limit`  

- `read`  
  - 支持频道：Discord / Slack  
  - 必需参数：`--target`  
  - 可选参数：`--limit`、`--before`、`--after`  
  - Discord 专属：`--around`  

- `edit`  
  - 支持频道：Discord / Slack  
  - 必需参数：`--message-id`、`--message`、`--target`  

- `delete`  
  - 支持频道：Discord / Slack / Telegram  
  - 必需参数：`--message-id`、`--target`  

- `pin` / `unpin`  
  - 支持频道：Discord / Slack  
  - 必需参数：`--message-id`、`--target`  

- `pins`（列表）  
  - 支持频道：Discord / Slack  
  - 必需参数：`--target`  

- `permissions`  
  - 支持频道：Discord  
  - 必需参数：`--target`  

- `search`  
  - 支持频道：Discord  
  - 必需参数：`--guild-id`、`--query`  
  - 可选参数：`--channel-id`、`--channel-ids`（可重复）、`--author-id`、`--author-ids`（可重复）、`--limit`  

### 线程操作

- `thread create`  
  - 支持频道：Discord  
  - 必需参数：`--thread-name`、`--target`（频道 ID）  
  - 可选参数：`--message-id`、`--message`、`--auto-archive-min`  

- `thread list`  
  - 支持频道：Discord  
  - 必需参数：`--guild-id`  
  - 可选参数：`--channel-id`、`--include-archived`、`--before`、`--limit`  

- `thread reply`  
  - 支持频道：Discord  
  - 必需参数：`--target`（线程 ID）、`--message`  
  - 可选参数：`--media`、`--reply-to`  

### 表情符号

- `emoji list`  
  - Discord：`--guild-id`  
  - Slack：无需额外标志  

- `emoji upload`  
  - 支持频道：Discord  
  - 必需参数：`--guild-id`、`--emoji-name`、`--media`  
  - 可选参数：`--role-ids`（可重复）  

### 贴纸

- `sticker send`  
  - 支持频道：Discord  
  - 必需参数：`--target`、`--sticker-id`（可重复）  
  - 可选参数：`--message`  

- `sticker upload`  
  - 支持频道：Discord  
  - 必需参数：`--guild-id`、`--sticker-name`、`--sticker-desc`、`--sticker-tags`、`--media`  

### 角色 / 频道 / 成员 / 语音

- `role info`（Discord）：`--guild-id`  
- `role add` / `role remove`（Discord）：`--guild-id`、`--user-id`、`--role-id`  
- `channel info`（Discord）：`--target`  
- `channel list`（Discord）：`--guild-id`  
- `member info`（Discord / Slack）：`--user-id`（+ Discord 需配合 `--guild-id`）  
- `voice status`（Discord）：`--guild-id`、`--user-id`  

### 事件

- `event list`（Discord）：`--guild-id`  
- `event create`（Discord）：`--guild-id`、`--event-name`、`--start-time`  
  - 可选参数：`--end-time`、`--desc`、`--channel-id`、`--location`、`--event-type`  

### 审核管理（Discord）

- `timeout`：`--guild-id`、`--user-id`（可选 `--duration-min` 或 `--until`；两者均省略则清除超时）  
- `kick`：`--guild-id`、`--user-id`（+ `--reason`）  
- `ban`：`--guild-id`、`--user-id`（+ `--delete-days`、`--reason`）  
  - `timeout` 同样支持 `--reason`  

### 广播

- `broadcast`  
  - 支持频道：任意已配置频道；使用 `--channel all` 可向所有平台广播  
  - 必需参数：`--targets`（可重复）  
  - 可选参数：`--message`、`--media`、`--dry-run`  

## 示例

发送一条 Discord 回复：

```
openclaw message send --channel discord \
  --target channel:123 --message "hi" --reply-to 456
```

发送一条带组件的 Discord 消息：

```
openclaw message send --channel discord \
  --target channel:123 --message "Choose:" \
  --components '{"text":"Choose a path","blocks":[{"type":"actions","buttons":[{"label":"Approve","style":"success"},{"label":"Decline","style":"danger"}]}]}'
```

完整组件模式请参阅 [Discord 组件](/channels/discord#interactive-components)。

创建一个 Discord 投票：

```
openclaw message poll --channel discord \
  --target channel:123 \
  --poll-question "Snack?" \
  --poll-option Pizza --poll-option Sushi \
  --poll-multi --poll-duration-hours 48
```

创建一个 Telegram 投票（2 分钟后自动关闭）：

```
openclaw message poll --channel telegram \
  --target @mychat \
  --poll-question "Lunch?" \
  --poll-option Pizza --poll-option Sushi \
  --poll-duration-seconds 120 --silent
```

发送一条 Teams 主动消息：

```
openclaw message send --channel msteams \
  --target conversation:19:abc@thread.tacv2 --message "hi"
```

创建一个 Teams 投票：

```
openclaw message poll --channel msteams \
  --target conversation:19:abc@thread.tacv2 \
  --poll-question "Lunch?" \
  --poll-option Pizza --poll-option Sushi
```

在 Slack 中添加反应：

```
openclaw message react --channel slack \
  --target C123 --message-id 456 --emoji "✅"
```

在 Signal 群组中添加反应：

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