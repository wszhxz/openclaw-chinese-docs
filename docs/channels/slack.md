---
summary: "Slack setup for socket or HTTP webhook mode"
read_when: "Setting up Slack or debugging Slack socket/HTTP mode"
title: "Slack"
---
# Slack

## Socket mode (default)

### 快速设置（初学者）

1. 创建一个Slack应用并启用 **Socket Mode**。
2. 创建一个 **App Token** (`xapp-...`) 和 **Bot Token** (`xoxb-...`)。
3. 为OpenClaw设置令牌并启动网关。

最小配置：

```json5
{
  channels: {
    slack: {
      enabled: true,
      appToken: "xapp-...",
      botToken: "xoxb-...",
    },
  },
}
```

### 设置

1. 在 https://api.slack.com/apps 中创建一个Slack应用（从头开始）。
2. **Socket Mode** → 打开。然后进入 **Basic Information** → **App-Level Tokens** → **生成令牌和范围**，使用范围 `connections:write`。复制 **App Token** (`xapp-...`)。
3. **OAuth & Permissions** → 添加机器人令牌范围（使用下面的清单）。点击 **Install to Workspace**。复制 **Bot User OAuth Token** (`xoxb-...`)。
4. 可选：**OAuth & Permissions** → 添加 **User Token Scopes**（参见下面的只读列表）。重新安装应用并复制 **User OAuth Token** (`xoxp-...`)。
5. **Event Subscriptions** → 启用事件并订阅：
   - `message.*`（包括编辑/删除/线程广播）
   - `app_mention`
   - `reaction_added`, `reaction_removed`
   - `member_joined_channel`, `member_left_channel`
   - `channel_rename`
   - `pin_added`, `pin_removed`
6. 邀请机器人加入你希望它阅读的频道。
7. Slash Commands → 如果你使用 `channels.slack.slashCommand`，创建 `/openclaw`。如果你启用了原生命令，请为每个内置命令添加一个斜杠命令（与 `/help` 中的名称相同）。除非你设置了 `channels.slack.commands.native: true`（全局 `commands.native` 是 `"auto"`，这会关闭Slack），否则Slack的原生默认是关闭的。
8. App Home → 启用 **Messages Tab**，以便用户可以私信机器人。

使用下面的清单以保持范围和事件同步。

多账户支持：使用 `channels.slack.accounts` 和每个账户的令牌以及可选的 `name`。参见 [`gateway/configuration`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 了解共享模式。

### OpenClaw配置（最小）

通过环境变量设置令牌（推荐）：

- `SLACK_APP_TOKEN=xapp-...`
- `SLACK_BOT_TOKEN=xoxb-...`

或者通过配置：

```json5
{
  channels: {
    slack: {
      enabled: true,
      appToken: "xapp-...",
      botToken: "xoxb-...",
    },
  },
}
```

### 用户令牌（可选）

OpenClaw可以使用一个Slack用户令牌(`xoxp-...`)进行读取操作（历史记录、固定消息、反应、表情符号、成员信息）。默认情况下，这保持只读：当存在用户令牌时，读取优先使用用户令牌，而写入仍然使用机器人令牌，除非你明确选择使用用户令牌。即使有 `userTokenReadOnly: false`，当机器人令牌可用时，它仍然优先用于写入。

用户令牌在配置文件中进行配置（不支持环境变量）。对于多账户，设置 `channels.slack.accounts.<id>.userToken`。

带有机器人+应用+用户令牌的示例：

```json5
{
  channels: {
    slack: {
      enabled: true,
      appToken: "xapp-...",
      botToken: "xoxb-...",
      userToken: "xoxp-...",
    },
  },
}
```

示例，显式设置userTokenReadOnly（允许用户令牌写操作）：

```json5
{
  channels: {
    slack: {
      enabled: true,
      appToken: "xapp-...",
      botToken: "xoxb-...",
      userToken: "xoxp-...",
      userTokenReadOnly: false,
    },
  },
}
```

#### 令牌使用

- 读取操作（历史记录、反应列表、固定消息列表、表情符号列表、成员信息、搜索）在配置时优先使用用户令牌，否则使用机器人令牌。
- 写入操作（发送/编辑/删除消息、添加/移除反应、固定/取消固定、文件上传）默认使用机器人令牌。如果`userTokenReadOnly: false`且没有可用的机器人令牌，OpenClaw 将回退到用户令牌。

### 历史上下文

- `channels.slack.historyLimit`（或`channels.slack.accounts.*.historyLimit`）控制包装到提示中的最近频道/组消息的数量。
- 回退到`messages.groupChat.historyLimit`。设置`0`以禁用（默认值为50）。

## HTTP 模式（事件API）

当您的网关可以通过HTTPS被Slack访问时使用HTTP Webhook模式（通常适用于服务器部署）。
HTTP模式使用事件API + 交互性 + 斜杠命令，并共享一个请求URL。

### 设置

1. 创建一个Slack应用并**禁用Socket模式**（如果您仅使用HTTP，则可选）。
2. **基本信息** → 复制**签名密钥**。
3. **OAuth & 权限** → 安装应用并复制**机器人用户OAuth令牌** (`xoxb-...`)。
4. **事件订阅** → 启用事件并将**请求URL**设置为您的网关Webhook路径（默认`/slack/events`）。
5. **交互性 & 快捷方式** → 启用并设置相同的**请求URL**。
6. **斜杠命令** → 为您的命令设置相同的**请求URL**。

示例请求URL：
`https://gateway-host/slack/events`

### OpenClaw 配置（最小）

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "http",
      botToken: "xoxb-...",
      signingSecret: "your-signing-secret",
      webhookPath: "/slack/events",
    },
  },
}
```

多账户HTTP模式：设置`channels.slack.accounts.<id>.mode = "http"`并为每个账户提供唯一的
`webhookPath`，以便每个Slack应用可以指向其自己的URL。

### 清单（可选）

使用此Slack应用清单快速创建应用（根据需要调整名称/命令）。如果计划配置用户令牌，请包含用户范围。

```json
{
  "display_information": {
    "name": "OpenClaw",
    "description": "Slack connector for OpenClaw"
  },
  "features": {
    "bot_user": {
      "display_name": "OpenClaw",
      "always_online": false
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/openclaw",
        "description": "Send a message to OpenClaw",
        "should_escape": false
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "chat:write",
        "channels:history",
        "channels:read",
        "groups:history",
        "groups:read",
        "groups:write",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "users:read",
        "app_mentions:read",
        "reactions:read",
        "reactions:write",
        "pins:read",
        "pins:write",
        "emoji:read",
        "commands",
        "files:read",
        "files:write"
      ],
      "user": [
        "channels:history",
        "channels:read",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "mpim:history",
        "mpim:read",
        "users:read",
        "reactions:read",
        "pins:read",
        "emoji:read",
        "search:read"
      ]
    }
  },
  "settings": {
    "socket_mode_enabled": true,
    "event_subscriptions": {
      "bot_events": [
        "app_mention",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "reaction_added",
        "reaction_removed",
        "member_joined_channel",
        "member_left_channel",
        "channel_rename",
        "pin_added",
        "pin_removed"
      ]
    }
  }
}
```

如果启用原生命令，请为每个要暴露的命令添加一个 `slash_commands` 条目（与 `/help` 列表匹配）。使用 `channels.slack.commands.native` 进行覆盖。

## 范围（当前与可选）

Slack 的 Conversations API 是类型范围限定的：您只需要实际使用的会话类型的范围（channels, groups, im, mpim）。参见 https://docs.slack.dev/apis/web-api/using-the-conversations-api/ 以获取概述。

### 机器人令牌范围（必需）

- `chat:write` (send/update/delete messages via `chat.postMessage`)
  https://docs.slack.dev/reference/methods/chat.postMessage
- `im:write` (open DMs via `conversations.open` for user DMs)
  https://docs.slack.dev/reference/methods/conversations.open
- `channels:history`, `groups:history`, `im:history`, `mpim:history`
  https://docs.slack.dev/reference/methods/conversations.history
- `channels:read`, `groups:read`, `im:read`, `mpim:read`
  https://docs.slack.dev/reference/methods/conversations.info
- `users:read` (user lookup)
  https://docs.slack.dev/reference/methods/users.info
- `reactions:read`, `reactions:write` (`reactions.get` / `reactions.add`)
  https://docs.slack.dev/reference/methods/reactions.get
  https://docs.slack.dev/reference/methods/reactions.add
- `pins:read`, `pins:write` (`pins.list` / `pins.add` / `pins.remove`)
  https://docs.slack.dev/reference/scopes/pins.read
  https://docs.slack.dev/reference/scopes/pins.write
- `emoji:read` (`emoji.list`)
  https://docs.slack.dev/reference/scopes/emoji.read
- `files:write` (uploads via `files.uploadV2`)
  https://docs.slack.dev/messaging/working-with-files/#upload

### User token scopes (optional, read-only by default)

Add these under **User Token Scopes** if you configure `channels.slack.userToken`.

- `channels:history`, `groups:history`, `im:history`, `mpim:history`
- `channels:read`, `groups:read`, `im:read`, `mpim:read`
- `users:read`
- `reactions:read`
- `pins:read`
- `emoji:read`
- `search:read`

### Not needed today (but likely future)

- `mpim:write` (only if we add group-DM open/DM start via `conversations.open`)
- `groups:write` (only if we add private-channel management: create/rename/invite/archive)
- `chat:write.public` (only if we want to post to channels the bot isn't in)
  https://docs.slack.dev/reference/scopes/chat.write.public
- `users:read.email` (only if we need email fields from `users.info`)
  https://docs.slack.dev/changelog/2017-04-narrowing-email-access
- `files:read` (only if we start listing/reading file metadata)

## Config

Slack uses Socket Mode only (no HTTP webhook server). Provide both tokens:

```json
{
  "slack": {
    "enabled": true,
    "botToken": "xoxb-...",
    "appToken": "xapp-...",
    "groupPolicy": "allowlist",
    "dm": {
      "enabled": true,
      "policy": "pairing",
      "allowFrom": ["U123", "U456", "*"],
      "groupEnabled": false,
      "groupChannels": ["G123"],
      "replyToMode": "all"
    },
    "channels": {
      "C123": { "allow": true, "requireMention": true },
      "#general": {
        "allow": true,
        "requireMention": true,
        "users": ["U123"],
        "skills": ["search", "docs"],
        "systemPrompt": "Keep answers short."
      }
    },
    "reactionNotifications": "own",
    "reactionAllowlist": ["U123"],
    "replyToMode": "off",
    "actions": {
      "reactions": true,
      "messages": true,
      "pins": true,
      "memberInfo": true,
      "emojiList": true
    },
    "slashCommand": {
      "enabled": true,
      "name": "openclaw",
      "sessionPrefix": "slack:slash",
      "ephemeral": true
    },
    "textChunkLimit": 4000,
    "mediaMaxMb": 20
  }
}
```

令牌也可以通过环境变量提供：

- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`

Ack 反应通过 `messages.ackReaction` +
`messages.ackReactionScope` 全局控制。使用 `messages.removeAckAfterReply` 在机器人回复后清除
ack 反应。

## 限制

- 发送的文本被分块为 `channels.slack.textChunkLimit`（默认 4000）。
- 可选换行符分块：设置 `channels.slack.chunkMode="newline"` 在长度分块之前按空白行（段落边界）拆分。
- 媒体上传限制为 `channels.slack.mediaMaxMb`（默认 20）。

## 回复线程

默认情况下，OpenClaw 在主频道回复。使用 `channels.slack.replyToMode` 控制自动线程：

| 模式    | 行为                                                                                                                                                            |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `off`   | **默认。** 在主频道回复。仅在触发消息已经在某个线程中时才进行线程回复。                                                                  |
| `first` | 第一条回复进入线程（在触发消息下），后续回复进入主频道。适用于保持上下文可见性同时避免线程混乱。 |
| `all`   | 所有回复都进入线程。使对话保持封闭但可能降低可见性。                                                                                  |

该模式适用于自动回复和代理工具调用 (`slack sendMessage`)。

### 按聊天类型线程

您可以通过设置 `channels.slack.replyToModeByChatType` 为每种聊天类型配置不同的线程行为：

```json5
{
  channels: {
    slack: {
      replyToMode: "off", // default for channels
      replyToModeByChatType: {
        direct: "all", // DMs always thread
        group: "first", // group DMs/MPIM thread first reply
      },
    },
  },
}
```

支持的聊天类型：

- `direct`: 1:1 直接消息 (Slack `im`)
- `group`: 群组直接消息 / MPIMs (Slack `mpim`)
- `channel`: 标准频道 (公开/私有)

优先级：

1. `replyToModeByChatType.<chatType>`
2. `replyToMode`
3. 提供程序默认 (`off`)

旧版 `channels.slack.dm.replyToMode` 仍然作为回退选项被接受，当没有设置聊天类型覆盖时用于 `direct`。

示例：

仅线程直接消息：

```json5
{
  channels: {
    slack: {
      replyToMode: "off",
      replyToModeByChatType: { direct: "all" },
    },
  },
}
```

线程群组直接消息但保持频道在根级别：

```json5
{
  channels: {
    slack: {
      replyToMode: "off",
      replyToModeByChatType: { group: "first" },
    },
  },
}
```

使频道成为线程，保持直接消息在根级别：

```json5
{
  channels: {
    slack: {
      replyToMode: "first",
      replyToModeByChatType: { direct: "off", group: "off" },
    },
  },
}
```

### 手动线程标签

为了更精细的控制，在代理响应中使用这些标签：

- `[[reply_to_current]]` — 回复触发消息（开始/继续线程）。
- `[[reply_to:<id>]]` — 回复特定消息ID。

## 会话 + 路由

- 直接消息共享 `main` 会话（类似于 WhatsApp/Telegram）。
- 频道映射到 `agent:<agentId>:slack:channel:<channelId>` 会话。
- 斜杠命令使用 `agent:<agentId>:slack:slash:<userId>` 会话（前缀可通过 `channels.slack.slashCommand.sessionPrefix` 配置）。
- 如果 Slack 没有提供 `channel_type`，OpenClaw 将根据频道ID前缀 (`D`, `C`, `G`) 推断，并默认为 `channel` 以保持会话密钥稳定。
- 原生命令注册使用 `commands.native`（全局默认 `"auto"` → Slack 关闭），并且可以通过工作区进行重写 `channels.slack.commands.native`。文本命令需要独立的 `/...` 消息，并且可以通过 `commands.text: false` 禁用。Slack 斜杠命令在 Slack 应用中管理，并不会自动删除。使用 `commands.useAccessGroups: false` 绕过命令的访问组检查。
- 完整命令列表 + 配置：[斜杠命令](/tools/slash-commands)

## 直接消息安全（配对）

- 默认：`channels.slack.dm.policy="pairing"` — 未知直接消息发送者会收到一个配对码（1小时后过期）。
- 通过以下方式批准：`openclaw pairing approve slack <code>`。
- 允许任何人：设置 `channels.slack.dm.policy="open"` 和 `channels.slack.dm.allowFrom=["*"]`。
- `channels.slack.dm.allowFrom` 接受用户ID、@句柄或电子邮件（在令牌允许的情况下启动时解析）。向导接受用户名并在设置期间解析为ID（在令牌允许的情况下）。

## 群组策略

- `channels.slack.groupPolicy` 控制频道处理 (`open|disabled|allowlist`)。
- `allowlist` 要求频道在 `channels.slack.channels` 中列出。
- 如果你只设置了 `SLACK_BOT_TOKEN`/`SLACK_APP_TOKEN` 而从未创建过 `channels.slack` 部分，
  运行时会默认将 `groupPolicy` 设置为 `open`。添加 `channels.slack.groupPolicy`，
  `channels.defaults.groupPolicy` 或频道白名单以锁定它。
- 配置向导接受 `#channel` 名称并在可能的情况下将其解析为 ID（公开 + 私有）；如果存在多个匹配项，它会优先选择活动频道。
- 启动时，OpenClaw 将允许列表中的频道/用户名解析为 ID（当令牌允许时）
  并记录映射；无法解析的条目将保持原样。
- 要允许**无频道**，设置 `channels.slack.groupPolicy: "disabled"`（或保持空允许列表）。

频道选项 (`channels.slack.channels.<id>` 或 `channels.slack.channels.<name>`)：

- `allow`: 当 `groupPolicy="allowlist"` 时允许/拒绝频道。
- `requireMention`: 为频道设置提及门控。
- `tools`: 可选的每个频道工具策略覆盖 (`allow`/`deny`/`alsoAllow`)。
- `toolsBySender`: 可选的每个发送者在频道内的工具策略覆盖（键是发送者 ID/@句柄/电子邮件；支持 `"*"` 通配符）。
- `allowBots`: 允许此频道中的机器人撰写的消息（默认：false）。
- `users`: 可选的每个频道用户允许列表。
- `skills`: 技能过滤器（省略 = 所有技能，空 = 无）。
- `systemPrompt`: 频道的额外系统提示（与主题/目的结合）。
- `enabled`: 设置 `false` 以禁用频道。

## 交付目标

与 cron/CLI 发送一起使用：

- `user:<id>` 用于直接消息
- `channel:<id>` 用于频道

## 工具操作

Slack 工具操作可以使用 `channels.slack.actions.*` 进行门控：

| 操作组   | 默认值  | 备注                 |
| -------- | ------- | -------------------- |
| reactions| enabled | 反应 + 列出反应      |
| messages | enabled | 读取/发送/编辑/删除  |
| pins     | enabled | 固定/取消固定/列出   |
| memberInfo| enabled| 成员信息             |
| emojiList| enabled| 自定义表情符号列表   |

## 安全注意事项

- 写操作默认使用机器人令牌，因此状态更改操作仅限于应用的机器人权限和身份。
- 设置 `userTokenReadOnly: false` 允许在机器人令牌不可用时使用用户令牌进行写操作，
  这意味着操作将以安装用户的访问权限运行。将用户令牌视为高度特权，并保持操作门控和允许列表紧密。
- 如果启用用户令牌写操作，请确保用户令牌包含预期的写范围 (`chat:write`, `reactions:write`, `pins:write`,
  `files:write`)，否则这些操作将失败。

## 注意事项

- 提及门控通过 `channels.slack.channels` 进行控制（设置 `requireMention` 为 `true`）；`agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）也视为提及。
- 多代理覆盖：在 `agents.list[].groupChat.mentionPatterns` 上设置每个代理的模式。
- 反应通知遵循 `channels.slack.reactionNotifications`（使用 `reactionAllowlist` 模式 `allowlist`）。
- 默认情况下忽略机器人生成的消息；通过 `channels.slack.allowBots` 或 `channels.slack.channels.<id>.allowBots` 启用。
- 警告：如果您允许回复其他机器人 (`channels.slack.allowBots=true` 或 `channels.slack.channels.<id>.allowBots=true`)，请使用 `requireMention`、`channels.slack.channels.<id>.users` 允许列表和/或清除 `AGENTS.md` 和 `SOUL.md` 中的防护措施以防止机器人之间的回复循环。
- 对于 Slack 工具，反应移除语义在 [/tools/reactions](/tools/reactions) 中。
- 当允许且在大小限制内时，附件会下载到媒体存储中。