---
read_when: Setting up Slack or debugging Slack socket/HTTP mode
summary: Slack 的 socket 或 HTTP webhook 模式设置
title: Slack
x-i18n:
  generated_at: "2026-02-03T07:45:49Z"
  model: claude-opus-4-6
  provider: pi
  source_hash: 703b4b4333bebfef26b64710ba452bdfc3e7d2115048d4e552e8659425b3609b
  source_path: channels/slack.md
  workflow: 15
---
# Slack

## Socket 模式（默认）

### 快速设置（新手）

1.  创建一个 Slack 应用并启用 **Socket 模式**。
2.  创建一个 **应用令牌**（`xapp-...`）和 **机器人令牌**（`xoxb-...`）。
3.  为 OpenClaw 设置令牌并启动 Gateway 网关。

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

1.  在 https://api.slack.com/apps 创建一个 Slack 应用（从头开始）。
2.  **Socket 模式** → 开启。然后前往 **基本信息** → **应用级令牌** → **生成令牌和范围**，添加 `connections:write` 权限范围。复制 **应用令牌**（`xapp-...`）。
3.  **OAuth 与权限** → 添加机器人令牌权限范围（使用下面的 manifest）。点击 **安装到工作区**。复制 **机器人用户 OAuth 令牌**（`xoxb-...`）。
4.  可选：**OAuth 与权限** → 添加 **用户令牌范围**（参见下面的只读列表）。重新安装应用并复制 **用户 OAuth 令牌**（`xoxp-...`）。
5.  **事件订阅** → 启用事件并订阅：
    -   `message.*`（包括编辑/删除/线程广播）
    -   `app_mention`
    -   `reaction_added`、`reaction_removed`
    -   `member_joined_channel`、`member_left_channel`
    -   `channel_rename`
    -   `pin_added`、`pin_removed`
6.  邀请机器人加入你希望它读取的频道。
7.  斜杠命令 → 如果你使用 `channels.slack.slashCommand`，创建 `/openclaw`。如果启用原生命令，为每个内置命令添加一个斜杠命令（名称与 `/help` 相同）。除非你设置 `channels.slack.commands.native: true`，否则 Slack 默认关闭原生命令（全局 `commands.native` 是 `"auto"`，对 Slack 保持关闭）。
8.  应用主页 → 启用 **消息选项卡** 以便用户可以私信机器人。

使用下面的 manifest 以保持权限范围和事件同步。

多账户支持：使用 `channels.slack.accounts` 配置每个账户的令牌和可选的 `name`。参见 [`gateway/configuration`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 了解共享模式。

### OpenClaw 配置（最小）

通过环境变量设置令牌（推荐）：

-   `SLACK_APP_TOKEN=xapp-...`
-   `SLACK_BOT_TOKEN=xoxb-...`

或通过配置：

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

OpenClaw 可以使用 Slack 用户令牌（`xoxp-...`）进行读取操作（历史记录、置顶、表情回应、表情符号、成员信息）。默认情况下保持只读：当存在用户令牌时，读取优先使用用户令牌，而写入仍然使用机器人令牌，除非你明确选择加入。即使设置了 `userTokenReadOnly: false`，当机器人令牌可用时，写入仍然优先使用机器人令牌。

用户令牌在配置文件中配置（不支持环境变量）。对于多账户，设置 `channels.slack.accounts.<id>.userToken`。

包含机器人 + 应用 + 用户令牌的示例：

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

明确设置 userTokenReadOnly 的示例（允许用户令牌写入）：

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

-   读取操作（历史记录、表情回应列表、置顶列表、表情符号列表、成员信息、搜索）在配置了用户令牌时优先使用用户令牌，否则使用机器人令牌。
-   写入操作（发送/编辑/删除消息、添加/移除表情回应、置顶/取消置顶、文件上传）默认使用机器人令牌。如果 `userTokenReadOnly: false` 且没有可用的机器人令牌，OpenClaw 会回退到用户令牌。

### 历史上下文

-   `channels.slack.historyLimit`（或 `channels.slack.accounts.*.historyLimit`）控制将多少条最近的频道/群组消息包含到提示中。
-   回退到 `messages.groupChat.historyLimit`。设置为 `0` 以禁用（默认 50）。

## HTTP 模式（Events API）

当你的 Gateway 网关可以通过 HTTPS 被 Slack 访问时（服务器部署的典型情况），使用 HTTP webhook 模式。
HTTP 模式使用 Events API + 交互性 + 斜杠命令，共享一个请求 URL。

### 设置

1.  创建一个 Slack 应用并**禁用 Socket 模式**（如果你只使用 HTTP 则可选）。
2.  **基本信息** → 复制 **签名密钥**。
3.  **OAuth 与权限** → 安装应用并复制 **机器人用户 OAuth 令牌**（`xoxb-...`）。
4.  **事件订阅** → 启用事件并将 **请求 URL** 设置为你的 Gateway 网关 webhook 路径（默认 `/slack/events`）。
5.  **交互性与快捷键** → 启用并设置相同的 **请求 URL**。
6.  **斜杠命令** → 为你的命令设置相同的 **请求 URL**。

示例请求 URL：
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

多账户 HTTP 模式：设置 `channels.slack.accounts.<id>.mode = "http"` 并为每个账户提供唯一的 `webhookPath`，以便每个 Slack 应用可以指向自己的 URL。

### Manifest（可选）

使用此 Slack 应用 manifest 快速创建应用（如果需要可以调整名称/命令）。如果你计划配置用户令牌，请包含用户权限范围。

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

如果启用原生命令，为每个要公开的命令添加一个 `slash_commands` 条目（与 `/help` 列表匹配）。使用 `channels.slack.commands.native` 覆盖。

## 权限范围（当前 vs 可选）

Slack 的 Conversations API 是按类型区分的：你只需要你实际接触的会话类型（channels、groups、im、mpim）的权限范围。概述参见 https://docs.slack.dev/apis/web-api/using-the-conversations-api/。

### 机器人令牌权限范围（必需）

-   `chat:write`（通过 `chat.postMessage` 发送/更新/删除消息）
    https://docs.slack.dev/reference/methods/chat.postMessage
-   `im:write`（通过 `conversations.open` 打开私信用于用户私信）
    https://docs.slack.dev/reference/methods/conversations.open
-   `channels:history`、`groups:history`、`im:history`、`mpim:history`
    https://docs.slack.dev/reference/methods/conversations.history
-   `channels:read`、`groups:read`、`im:read`、`mpim:read`
    https://docs.slack.dev/reference/methods/conversations.info
-   `users:read`（用户查询）
    https://docs.slack.dev/reference/methods/users.info
-   `reactions:read`、`reactions:write`（`reactions.get` / `reactions.add`）
    https://docs.slack.dev/reference/methods/reactions.get
    https://docs.slack.dev/reference/methods/reactions.add
-   `pins:read`、`pins:write`（`pins.list` / `pins.add` / `pins.remove`）
    https://docs.slack.dev/reference/scopes/pins.read
    https://docs.slack.dev/reference/scopes/pins.write
-   `emoji:read`（`emoji.list`）
    https://docs.slack.dev/reference/scopes/emoji.read
-   `files:write`（通过 `files.uploadV2` 上传）
    https://docs.slack.dev/messaging/working-with-files/#upload

### 用户令牌权限范围（可选，默认只读）

如果你配置了 `channels.slack.userToken`，在 **用户令牌范围** 下添加这些。

-   `channels:history`、`groups:history`、`im:history`、`mpim:history`
-   `channels:read`、`groups:read`、`im:read`、`mpim:read`
-   `users:read`
-   `reactions:read`
-   `pins:read`
-   `emoji:read`
-   `search:read`

### 目前不需要（但未来可能需要）

-   `mpim:write`（仅当我们添加群组私信打开/私信启动时通过 `conversations.open`）
-   `groups:write`（仅当我们添加私有频道管理时：创建/重命名/邀请/归档）
-   `chat:write.public`（仅当我们想发布到机器人未加入的频道时）
    https://docs.slack.dev/reference/scopes/chat.write.public
-   `users:read.email`（仅当我们需要从 `users.info` 获取邮箱字段时）
    https://docs.slack.dev/changelog/2017-04-narrowing-email-access
-   `files:read`（仅当我们开始列出/读取文件元数据时）

## 配置

Slack 仅使用 Socket 模式（无 HTTP webhook 服务器）。提供两个令牌：

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

-   `SLACK_BOT_TOKEN`
-   `SLACK_APP_TOKEN`

确认表情回应通过 `messages.ackReaction` + `messages.ackReactionScope` 全局控制。使用 `messages.removeAckAfterReply` 在机器人回复后清除确认表情回应。

## 限制

-   出站文本按 `channels.slack.textChunkLimit` 分块（默认 4000）。
-   可选的换行分块：设置 `channels.slack.chunkMode="newline"` 以在长度分块之前按空行（段落边界）分割。
-   媒体上传受 `channels.slack.mediaMaxMb` 限制（默认 20）。

## 回复线程

默认情况下，OpenClaw 在主频道回复。使用 `channels.slack.replyToMode` 控制自动线程：

| 模式    | 行为                                                                                         |
| ------- | -------------------------------------------------------------------------------------------- |
| `off`   | **默认。** 在主频道回复。仅当触发消息已在线程中时才使用线程。                                |
| `first` | 第一条回复进入线程（在触发消息下），后续回复进入主频道。适合保持上下文可见同时避免线程混乱。 |
| `all`   | 所有回复都进入线程。保持对话集中但可能降低可见性。                                           |

该模式适用于自动回复和智能体工具调用（`slack sendMessage`）。

### 按聊天类型的线程

你可以通过设置 `channels.slack.replyToModeByChatType` 为每种聊天类型配置不同的线程行为：

```json5
{
  channels: {
    slack: {
      replyToMode: "off", // 频道的默认值
      replyToModeByChatType: {
        direct: "all", // 私信始终使用线程
        group: "first", // 群组私信/MPIM 第一条回复使用线程
      },
    },
  },
}
```

支持的聊天类型：

-   `direct`：一对一私信（Slack `im`）
-   `group`：群组私信 / MPIM（Slack `mpim`）
-   `channel`：标准频道（公开/私有）

优先级：

1.  `replyToModeByChatType.<chatType>`
2.  `replyToMode`
3.  提供商默认值（`off`）

当未设置聊天类型覆盖时，旧版 `channels.slack.dm.replyToMode` 仍可作为 `direct` 的回退。

示例：

仅对私信使用线程：

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

对群组私信使用线程但保持频道在根级别：

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

让频道使用线程，保持私信在根级别：

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

对于细粒度控制，在智能体响应中使用这些标签：

-   `[[reply_to_current]]` — 回复触发消息（开始/继续线程）。
-   `[[reply_to:<id>]]` — 回复特定的消息 id。

## 会话 + 路由

-   私信共享 `main` 会话（与 WhatsApp/Telegram 相同）。
-   频道映射到 `agent:<agentId>:slack:channel:<channelId>` 会话。
-   斜杠命令使用 `agent:<agentId>:slack:slash:<userId>` 会话（前缀可通过 `channels.slack.slashCommand.sessionPrefix` 配置）。
-   如果 Slack 未提供 `channel_type`，OpenClaw 会从频道 ID 前缀（`D`、`C`、`G`）推断并默认为 `channel` 以保持会话键稳定。
-   原生命令注册使用 `commands.native`（全局默认 `"auto"` → Slack 关闭），可以使用 `channels.slack.commands.native` 按工作空间覆盖。文本命令需要独立的 `/...` 消息，可以使用 `commands.text: false` 禁用。Slack 斜杠命令在 Slack 应用中管理，不会自动移除。使用 `commands.useAccessGroups: false` 绕过命令的访问组检查。
-   完整命令列表 + 配置：[斜杠命令](/tools/slash-commands)

## 私信安全（配对）

-   默认：`channels.slack.dm.policy="pairing"` — 未知的私信发送者会收到配对码（1 小时后过期）。
-   通过以下方式批准：`openclaw pairing approve slack <code>`。
-   要允许任何人：设置 `channels.slack.dm.policy="open"` 和 `channels.slack.dm.allowFrom=["*"]`。
-   `channels.slack.dm.allowFrom` 接受用户 ID、@用户名或邮箱（在令牌允许时启动时解析）。向导在设置期间接受用户名，并在令牌允许时将其解析为 ID。

## 群组策略

-   `channels.slack.groupPolicy` 控制频道处理（`open|disabled|allowlist`）。
-   `allowlist` 要求频道列在 `channels.slack.channels` 中。
-   如果你只设置了 `SLACK_BOT_TOKEN`/`SLACK_APP_TOKEN` 而从未创建 `channels.slack` 部分，运行时默认将 `groupPolicy` 设为 `open`。添加 `channels.slack.groupPolicy`、`channels.defaults.groupPolicy` 或频道白名单来锁定它。
-   配置向导接受 `#channel` 名称，并在可能时（公开 + 私有）将其解析为 ID；如果存在多个匹配，它优先选择活跃的频道。
-   启动时，OpenClaw 将白名单中的频道/用户名解析为 ID（在令牌允许时）并记录映射；未解析的条目按原样保留。
-   要**不允许任何频道**，设置 `channels.slack.groupPolicy: "disabled"`（或保留空白名单）。

频道选项（`channels.slack.channels.<id>`