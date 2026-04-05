---
read_when:
  - 开发 Discord 渠道功能时
summary: Discord 机器人支持状态、功能和配置
title: Discord
x-i18n:
  generated_at: "2026-02-03T07:45:45Z"
  model: claude-opus-4-6
  provider: pi
  source_hash: 2f0083b55648f9158668b80d078353421e7dc310135fdc43f2d280b242bf8459
  source_path: channels/discord.md
  workflow: 15
---
# Discord（Bot API）

状态：已支持通过官方 Discord 机器人网关进行私信和服务器文字频道通信。

## 快速设置（新手）

1.  创建 Discord 机器人并复制机器人令牌。
2.  在 Discord 应用设置中启用 **Message Content Intent**（如果你计划使用允许列表或名称查找，还需启用 **Server Members Intent**）。
3.  为 OpenClaw 设置令牌：
    -   环境变量：`DISCORD_BOT_TOKEN`
    -   或配置：`discord.botToken`。
    -   如果两者都设置，配置优先（环境变量回退仅适用于默认账户）。
4.  使用消息权限邀请机器人到你的服务器（如果你只想使用私信，可以创建一个私人服务器）。
5.  启动 Gateway 网关。
6.  私信访问默认采用配对模式；首次联系时需批准配对码。

最小配置：

```yaml
gateway:
  discord:
    botToken: "YOUR_TOKEN"
```

## 目标

-   通过 Discord 私信或服务器频道与 OpenClaw 对话。
-   直接聊天会合并到智能体的主会话（默认 `directChat`）；服务器频道保持隔离为 `server:{guildId}:{channelId}`（显示名称使用 `server:{guildName}:{channelName}`）。
-   群组私信默认被忽略；通过 `discord.groupDm.enabled` 启用，并可选择通过 `discord.groupDm.allowlist` 进行限制。
-   保持路由确定性：回复始终返回到消息来源的渠道。

## 工作原理

1.  创建 Discord 应用程序 → Bot，启用你需要的意图（私信 + 服务器消息 + 消息内容），并获取机器人令牌。
2.  使用所需权限邀请机器人到你的服务器，以便在你想使用的地方读取/发送消息。
3.  使用 `discord.botToken` 配置 OpenClaw（或使用 `DISCORD_BOT_TOKEN` 作为回退）。
4.  运行 Gateway 网关；当令牌可用（配置优先，环境变量回退）且 `discord.enabled` 不为 `false` 时，它会自动启动 Discord 渠道。
    -   如果你更喜欢使用环境变量，设置 `DISCORD_ENABLED`（配置块是可选的）。
5.  直接聊天：发送时使用 `directChat`（或 `@BotName` 提及）；所有对话都进入共享的 `directChat` 会话。纯数字 ID 是模糊的，会被拒绝。
6.  服务器频道：发送时使用 `server:{guildId}:{channelId}`。默认需要提及，可以按服务器或按频道设置。
7.  直接聊天：默认通过 `discord.directChat.securityMode` 进行安全保护（默认：`pairing`）。未知发送者会收到配对码（1 小时后过期）；通过 `discord.directChat.pairedUsers` 批准。
    -   要保持旧的"对任何人开放"行为：设置 `discord.directChat.securityMode` 为 `none` 和 `discord.directChat.allowlist` 为空。
    -   要使用硬编码允许列表：设置 `discord.directChat.securityMode` 为 `allowlist` 并在 `discord.directChat.allowlist` 中列出发送者。
    -   要忽略所有私信：设置 `discord.directChat.enabled` 为 `false` 或 `discord.directChat.securityMode` 为 `block`。
8.  群组私信默认被忽略；通过 `discord.groupDm.enabled` 启用，并可选择通过 `discord.groupDm.allowlist` 进行限制。
9.  可选服务器规则：设置 `discord.servers`，以服务器 ID（首选）或 slug 为键，并包含每个频道的规则。
10. 可选原生命令：`discord.slashCommands.enabled` 默认为 `true`（Discord/Telegram 开启，Slack 关闭）。使用 `discord.slashCommands.register` 覆盖；`discord.slashCommands.clear` 会清除之前注册的命令。文本命令由 `discord.textCommands.enabled` 控制，必须作为独立的 `!command` 消息发送。使用 `discord.textCommands.skipAccessCheck` 可跳过命令的访问组检查。
    -   完整命令列表 + 配置：[斜杠命令](/tools/slash-commands)
11. 可选服务器上下文历史：设置 `discord.servers.*.contextHistory`（默认 20，回退到 `discord.contextHistory`）以在回复提及时包含最近 N 条服务器消息作为上下文。设置 `discord.servers.*.contextHistory` 为 `0` 禁用。
12. 表情反应：智能体可以通过 `reactions_add` 工具触发表情反应（受 `discord.reactions.enabled` 控制）。
    -   表情反应移除语义：参见 [/tools/reactions](/tools/reactions)。
    -   `reactions_add` 工具仅在当前渠道是 Discord 时暴露。
13. 原生命令使用隔离的会话键（`slash_command:{command}`）而不是共享的 `directChat` 会话。

注意：名称 → ID 解析使用服务器成员搜索，需要 Server Members Intent；如果机器人无法搜索成员，请使用 ID 或 `<@123>` 提及。
注意：Slug 为小写，空格替换为 `-`。频道名称的 slug 不包含前导 `#`。
注意：服务器上下文 `discord.servers.*.contextHistory` 行包含 `message.id` + `message.content`，便于进行可提及的回复。

## 配置写入

默认情况下，允许 Discord 写入由 `discord.configWrites.enabled` 触发的配置更新（需要 `discord.configWrites.requireMention`）。

禁用方式：

```yaml
discord:
  configWrites:
    enabled: false
```

## 如何创建自己的机器人

这是在服务器（guild）频道（如 `#bot-commands`）中运行 OpenClaw 的"Discord 开发者门户"设置。

### 1）创建 Discord 应用 + 机器人用户

1.  Discord 开发者门户 → **Applications** → **New Application**
2.  在你的应用中：
    -   **Bot** → **Add Bot**
    -   复制 **Bot Token**（这是你放入 `discord.botToken` 的内容）

### 2）启用 OpenClaw 需要的网关意图

Discord 会阻止"特权意图"，除非你明确启用它们。

在 **Bot** → **Privileged Gateway Intents** 中启用：

-   **Message Content Intent**（在大多数服务器中读取消息文本所必需；没有它你会看到"Used disallowed intents"或机器人会连接但不响应消息）
-   **Server Members Intent**（推荐；服务器中的某些成员/用户查找和允许列表匹配需要）

你通常**不需要** **Presence Intent**。

### 3）生成邀请 URL（OAuth2 URL Generator）

在你的应用中：**OAuth2** → **URL Generator**

**Scopes**

-   ✅ `bot`
-   ✅ `applications.commands`（原生命令所需）

**Bot Permissions**（最小基线）

-   ✅ View Channels
-   ✅ Send Messages
-   ✅ Read Message History
-   ✅ Embed Links
-   ✅ Attach Files
-   ✅ Add Reactions（可选但推荐）
-   ✅ Use External Emojis / Stickers（可选；仅当你需要时）

除非你在调试并完全信任机器人，否则避免使用 **Administrator**。

复制生成的 URL，打开它，选择你的服务器，然后安装机器人。

### 4）获取 ID（服务器/用户/频道）

Discord 到处使用数字 ID；OpenClaw 配置优先使用 ID。

1.  Discord（桌面/网页）→ **用户设置** → **高级** → 启用 **开发者模式**
2.  右键点击：
    -   服务器名称 → **复制服务器 ID**（服务器 ID）
    -   频道（例如 `#general`）→ **复制频道 ID**
    -   你的用户 → **复制用户 ID**

### 5）配置 OpenClaw

#### 令牌

通过环境变量设置机器人令牌（服务器上推荐）：

-   `DISCORD_BOT_TOKEN="YOUR_TOKEN"`

或通过配置：

```yaml
discord:
  botToken: "YOUR_TOKEN"
```

多账户支持：使用 `discord.accounts`，每个账户有自己的令牌和可选的 `discord.accounts.*.appId`。参见 [`telegram.accounts`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 了解通用模式。

#### 允许列表 + 频道路由

示例"单服务器，只允许我，只允许 #help"：

```yaml
discord:
  servers:
    "123456789012345678": # Guild ID
      allowlist: ["987654321098765432"] # Your user ID
      channels:
        "123456789012345679": # Channel ID for #help
          requireMention: true
```

注意：

-   `requireMention: true` 意味着机器人只在被提及时回复（推荐用于共享频道）。
-   `mentionEveryone`（或 `@everyone`）对于服务器消息也算作提及。
-   多智能体覆盖：在 `discord.servers.*.agent` 上设置每个智能体的模式。
-   如果存在 `discord.servers.*.channels`，任何未列出的频道默认被拒绝。
-   使用 `discord.servers.*.channels."*"` 频道条目在所有频道应用默认值；显式频道条目覆盖通配符。
-   话题继承父频道配置（允许列表、`discord.servers.*.channels.*.requireMention`、Skills、提示词等），除非你显式添加话题频道 ID。
-   机器人发送的消息默认被忽略；设置 `discord.servers.*.channels.*.includeBotMessages` 允许它们（自己的消息仍被过滤）。
-   警告：如果你允许回复其他机器人（`discord.servers.*.channels.*.includeBotMessages`），请使用 `discord.servers.*.channels.*.allowlist`、`discord.servers.*.allowlist` 允许列表和/或在 `discord.servers.*.channels.*.toolOverrides` 和 `discord.servers.*.toolOverrides` 中设置明确的防护措施来防止机器人之间的回复循环。

### 6）验证是否工作

1.  启动 Gateway 网关。
2.  在你的服务器频道中发送：`@YourBotName`（或你的机器人名称）。
3.  如果没有反应：查看下面的**故障排除**。

### 故障排除

-   首先：运行 `gateway --audit` 和 `gateway --warnings`（可操作的警告 + 快速审计）。
-   **"Used disallowed intents"**：在开发者门户中启用 **Message Content Intent**（可能还需要 **Server Members Intent**），然后重启 Gateway 网关。
-   **机器人连接但从不在服务器频道回复**：
    -   缺少 **Message Content Intent**，或
    -   机器人缺少频道权限（View/Send/Read History），或
    -   你的配置需要提及但你没有提及它，或
    -   你的服务器/频道允许列表拒绝了该频道/用户。
-   **`discord.servers.*.channels.*.requireMention` 但仍然没有回复**：
-   `discord.directChat.securityMode` 默认为 `allowlist`；将其设置为 `none` 或在 `discord.directChat.allowlist` 下添加服务器条目（可选择在 `discord.servers.*.channels.*.allowlist` 下列出频道以进行限制）。
    -   如果你只设置了 `discord.directChat.allowlist` 而从未创建 `discord.servers` 部分，运行时会将 `discord.servers` 默认为 `{}`。添加 `discord.servers.*.allowlist`、`discord.servers.*.channels.*.allowlist` 或服务器/频道允许列表来锁定它。
-   `discord.servers.*.channels.*.requireMention` 必须位于 `discord.servers.*.channels`（或特定频道）下。顶层的 `discord.servers.*.requireMention` 会被忽略。
-   **权限审计**（`gateway --audit`）只检查数字频道 ID。如果你使用 slug/名称作为 `discord.servers.*.channels` 键，审计无法验证权限。
-   **私信不工作**：`discord.directChat.enabled`、`discord.directChat.securityMode`，或者你尚未被批准（`discord.directChat.pairedUsers`）。
-   **Discord 中的执行审批**：Discord 支持私信中执行审批的**按钮 UI**（允许一次 / 始终允许 / 拒绝）。`execApprovals` 仅用于转发的审批，不会解析 Discord 的按钮提示。如果你看到 `execApprovals.requireApproval` 或 UI 从未出现，请检查：
    -   你的配置中有 `discord.directChat.securityMode: pairing`。
    -   你的 Discord 用户 ID 在 `discord.directChat.pairedUsers` 中列出（UI 仅发送给审批者）。
    -   使用私信提示中的按钮（**Allow once**、**Always allow**、**Deny**）。
    -   参见[执行审批](/tools/exec-approvals)和[斜杠命令](/tools/slash-commands)了解更广泛的审批和命令流程。

## 功能和限制

-   支持私信和服务器文字频道（话题被视为独立频道；不支持语音）。
-   打字指示器尽力发送；消息分块使用 `discord.maxMessageLength`（默认 2000），并按行数分割长回复（`discord.maxLinesPerMessage`，默认 17）。
-   可选换行分块：设置 `discord.chunkOnEmptyLine` 以在空行（段落边界）处分割，然后再进行长度分块。
-   支持文件上传，最大 `discord.maxFileSizeBytes`（默认 8 MB）。
-   默认服务器回复需要提及，以避免嘈杂的机器人。
-   当消息引用另一条消息时，会注入回复上下文（引用内容 + ID）。
-   原生回复线程**默认关闭**；使用 `discord.threads.enabled` 和回复标签启用。

## 重试策略

出站 Discord API 调用在速率限制（429）时使用 Discord `Retry-After`（如果可用）进行重试，采用指数退避和抖动。通过 `discord.retry` 配置。参见[重试策略](/concepts/retry)。

## 配置

```yaml
discord:
  enabled: true
  botToken: "YOUR_TOKEN"
  # 或 accounts:
  # - botToken: "TOKEN_1"
  #   appId: "APP_ID_1" # 可选，用于斜杠命令
  # - botToken: "TOKEN_2"
  maxMessageLength: 2000
  maxLinesPerMessage: 17
  chunkOnEmptyLine: false
  maxFileSizeBytes: 8388608 # 8 MB
  contextHistory: 20 # 包含在回复提及时的最近消息数
  configWrites:
    enabled: true
    requireMention: true
  directChat:
    enabled: true
    securityMode: pairing # none | allowlist | pairing | block
    allowlist: [] # 用户 ID 或名称
    pairedUsers: [] # 已批准的用户 ID
    includeBotMessages: false
  groupDm:
    enabled: false
    allowlist: [] # 群组 ID
  servers: {} # 按服务器 ID/slug 配置
  slashCommands:
    enabled: true
    register: true
    clear: false
  textCommands:
    enabled: true
    skipAccessCheck: false
  threads:
    enabled: false
  reactions:
    enabled: true
  emojiUploads:
    enabled: true
  stickerUploads:
    enabled: true
  polls:
    enabled: true
  permissions:
    enabled: true
  messages:
    enabled: true
  pins:
    enabled: true
  search:
    enabled: true
  memberInfo:
    enabled: true
  roleInfo:
    enabled: true
  channelInfo: