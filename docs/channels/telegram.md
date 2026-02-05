---
summary: "Telegram bot support status, capabilities, and configuration"
read_when:
  - Working on Telegram features or webhooks
title: "Telegram"
---
# Telegram (Bot API)

状态：通过 grammY 支持生产环境中的机器人私聊和群组。默认使用长轮询；可选使用 Webhook。

## 快速设置（初学者）

1. 使用 **@BotFather** 创建一个机器人 ([直接链接](https://t.me/BotFather))。确认句柄完全为 `@BotFather`，然后复制令牌。
2. 设置令牌：
   - 环境变量: `TELEGRAM_BOT_TOKEN=...`
   - 或配置文件: `channels.telegram.botToken: "..."`。
   - 如果两者都已设置，则配置文件优先（环境变量仅作为默认账户的后备）。
3. 启动网关。
4. 默认情况下，私聊访问需要配对；在首次联系时批准配对代码。

最小配置：

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "123:abc",
      dmPolicy: "pairing",
    },
  },
}
```

## 什么是它

- 由网关拥有的 Telegram Bot API 通道。
- 确定性路由：回复发送回 Telegram；模型从不选择通道。
- 私聊共享代理的主要会话；群组保持隔离 (`agent:<agentId>:telegram:group:<chatId>`)。

## 设置（快速路径）

### 1) 创建机器人令牌（BotFather）

1. 打开 Telegram 并与 **@BotFather** 聊天 ([直接链接](https://t.me/BotFather))。确认句柄完全为 `@BotFather`。
2. 运行 `/newbot`，然后按照提示操作（名称 + 以 `bot` 结尾的用户名）。
3. 复制令牌并安全存储。

可选的 BotFather 设置：

- `/setjoingroups` — 允许/拒绝将机器人添加到群组。
- `/setprivacy` — 控制机器人是否查看所有群组消息。

### 2) 配置令牌（环境变量或配置文件）

示例：

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "123:abc",
      dmPolicy: "pairing",
      groups: { "*": { requireMention: true } },
    },
  },
}
```

环境变量选项: `TELEGRAM_BOT_TOKEN=...`（适用于默认账户）。
如果同时设置了环境变量和配置文件，则配置文件优先。

多账户支持：使用 `channels.telegram.accounts` 和每个账户的令牌以及可选的 `name`。参见 [`gateway/configuration`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 获取共享模式。

3. 启动网关。当解析到令牌时 Telegram 开始运行（首先检查配置文件，然后是环境变量）。
4. 私聊访问默认需要配对。在机器人首次被联系时批准代码。
5. 对于群组：添加机器人，决定隐私/管理员行为（如下），然后设置 `channels.telegram.groups` 以控制提及门控 + 允许列表。

## 令牌 + 隐私 + 权限（Telegram 端）

### 令牌创建（BotFather）

- `/newbot` 创建机器人并返回令牌（请保密）。
- 如果令牌泄露，请通过 @BotFather 撤销/重新生成令牌并更新您的配置。

### 群组消息可见性（隐私模式）

Telegram 机器人默认处于 **隐私模式**，这限制了它们可以接收的群组消息。
如果您的机器人必须查看 _所有_ 群组消息，您有两个选项：

- 使用 `/setprivacy` 禁用隐私模式 **或**
- 将机器人添加为群组 **管理员**（管理员机器人接收所有消息）。

**注意:** 当您切换隐私模式时，Telegram 要求从每个群组中移除并重新添加机器人以使更改生效。

### 群组权限（管理员权限）

管理员状态在群组内部设置（Telegram 用户界面）。管理员机器人总是接收所有群组消息，因此如果您需要完全可见性，请使用管理员权限。

## 工作原理（行为）

- 入站消息被标准化为共享频道信封，包含回复上下文和媒体占位符。
- 群组回复默认需要提及（原生 @提及 或 `agents.list[].groupChat.mentionPatterns` / `messages.groupChat.mentionPatterns`）。
- 多代理覆盖：在 `agents.list[].groupChat.mentionPatterns` 上为每个代理设置模式。
- 回复总是路由回相同的 Telegram 聊天。
- 长轮询使用 grammY 运行器，并按聊天进行排序；整体并发性由 `agents.defaults.maxConcurrent` 限制。
- Telegram Bot API 不支持已读回执；没有 `sendReadReceipts` 选项。

## 草稿流式传输

OpenClaw 可以使用 `sendMessageDraft` 在 Telegram 私聊中流式传输部分回复。

要求：

- 在 @BotFather 中为机器人启用线程模式（论坛主题模式）。
- 仅限私聊线程（Telegram 在入站消息中包含 `message_thread_id`）。
- `channels.telegram.streamMode` 未设置为 `"off"`（默认：`"partial"`，`"block"` 启用分块草稿更新）。

草稿流式传输仅限私聊；Telegram 不支持在群组或频道中使用。

## 格式化（Telegram HTML）

- 出站 Telegram 文本使用 `parse_mode: "HTML"`（Telegram 支持的标签子集）。
- Markdown 风格的输入会被渲染为 **Telegram 安全的 HTML**（粗体/斜体/删除线/代码/链接）；块级元素会被展平为带有换行符/项目符号的文本。
- 模型中的原始 HTML 会被转义以避免 Telegram 解析错误。
- 如果 Telegram 拒绝 HTML 有效负载，OpenClaw 会将同一消息重试为纯文本。

## 命令（原生 + 自定义）

OpenClaw 在启动时会将原生命令（如 `/status`，`/reset`，`/model`）注册到 Telegram 的机器人菜单。
您可以通过配置向菜单添加自定义命令：

```json5
{
  channels: {
    telegram: {
      customCommands: [
        { command: "backup", description: "Git backup" },
        { command: "generate", description: "Create an image" },
      ],
    },
  },
}
```

## 故障排除

- 日志中的 `setMyCommands failed` 通常意味着出站 HTTPS/DNS 被阻止到 `api.telegram.org`。
- 如果您看到 `sendMessage` 或 `sendChatAction` 失败，请检查 IPv6 路由和 DNS。

更多帮助：[频道故障排除](/channels/troubleshooting)。

注释：

- 自定义命令是 **仅菜单条目**；除非您在其他地方处理它们，否则 OpenClaw 不会实现它们。
- 命令名称会被规范化（去除前导 `/`，转换为小写）并且必须匹配 `a-z`，`0-9`，`_`（1–32 个字符）。
- 自定义命令 **不能覆盖原生命令**。冲突会被忽略并记录日志。
- 如果 `commands.native` 被禁用，则仅注册自定义命令（如果没有自定义命令则清除）。

## 限制

- 出站文本被分块为 `channels.telegram.textChunkLimit`（默认4000）。
- 可选换行分块：设置 `channels.telegram.chunkMode="newline"` 以在长度分块之前按空白行（段落边界）拆分。
- 媒体下载/上传由 `channels.telegram.mediaMaxMb` 限制（默认5）。
- Telegram Bot API 请求在 `channels.telegram.timeoutSeconds` 后超时（通过 grammY 默认500）。设置较低值以避免长时间挂起。
- 群组历史上下文使用 `channels.telegram.historyLimit`（或 `channels.telegram.accounts.*.historyLimit`），回退到 `messages.groupChat.historyLimit`。设置 `0` 以禁用（默认50）。
- 私信历史可以通过 `channels.telegram.dmHistoryLimit` 限制（用户轮次）。每个用户的覆盖：`channels.telegram.dms["<user_id>"].historyLimit`。

## 群组激活模式

默认情况下，机器人仅响应群组中的提及 (`@botname` 或 `agents.list[].groupChat.mentionPatterns` 中的模式)。要更改此行为：

### 通过配置（推荐）

```json5
{
  channels: {
    telegram: {
      groups: {
        "-1001234567890": { requireMention: false }, // always respond in this group
      },
    },
  },
}
```

**重要：** 设置 `channels.telegram.groups` 创建一个**白名单** - 仅接受列出的群组（或 `"*"`）。
论坛主题继承其父群组配置（allowFrom, requireMention, skills, prompts），除非你在 `channels.telegram.groups.<groupId>.topics.<topicId>` 下添加每个主题的覆盖。

允许所有群组始终响应：

```json5
{
  channels: {
    telegram: {
      groups: {
        "*": { requireMention: false }, // all groups, always respond
      },
    },
  },
}
```

保持所有群组仅提及响应（默认行为）：

```json5
{
  channels: {
    telegram: {
      groups: {
        "*": { requireMention: true }, // or omit groups entirely
      },
    },
  },
}
```

### 通过命令（会话级别）

在群组中发送：

- `/activation always` - 响应所有消息
- `/activation mention` - 需要提及（默认）

**注意：** 命令仅更新会话状态。要跨重启保持持久行为，请使用配置。

### 获取群组聊天ID

将群组中的任何消息转发到 Telegram 上的 `@userinfobot` 或 `@getidsbot` 查看聊天ID（负数如 `-1001234567890`）。

**提示：** 要获取自己的用户ID，向机器人发送私信，它将回复你的用户ID（配对消息），或在启用命令后使用 `/whoami`。

**隐私说明：** `@userinfobot` 是第三方机器人。如果你更喜欢，将机器人添加到群组，发送消息并使用 `openclaw logs --follow` 读取 `chat.id`，或使用 Bot API `getUpdates`。

## 配置写入

默认情况下，Telegram 允许写入由频道事件或 `/config set|unset` 触发的配置更新。

这种情况发生在：

- 一个群组升级为超级群组，Telegram 发出 `migrate_to_chat_id`（聊天ID更改）。OpenClaw 可以自动迁移 `channels.telegram.groups`。
- 您在 Telegram 聊天中运行 `/config set` 或 `/config unset`（需要 `commands.config: true`）。

禁用方式：

```json5
{
  channels: { telegram: { configWrites: false } },
}
```

## 主题（论坛超级群组）

Telegram 论坛主题包括每条消息的 `message_thread_id`。OpenClaw：

- 将 `:topic:<threadId>` 追加到 Telegram 群组会话密钥，以便每个主题隔离。
- 发送输入指示并使用 `message_thread_id` 回复，使响应保持在主题内。
- 通用主题（线程ID `1`）是特殊的：发送消息时省略 `message_thread_id`（Telegram 会拒绝它），但输入指示仍然包含它。
- 在模板上下文中暴露 `MessageThreadId` + `IsForum` 用于路由/模板化。
- 主题特定配置可在 `channels.telegram.groups.<chatId>.topics.<threadId>` 下找到（技能、允许列表、自动回复、系统提示、禁用）。
- 主题配置继承群组设置（requireMention、允许列表、技能、提示、启用），除非按主题重写。

私人聊天在某些边缘情况下可能包含 `message_thread_id`。OpenClaw 保持 DM 会话密钥不变，但在存在时仍使用线程ID进行回复/草稿流式传输。

## 内联按钮

Telegram 支持带有回调按钮的内联键盘。

```json5
{
  channels: {
    telegram: {
      capabilities: {
        inlineButtons: "allowlist",
      },
    },
  },
}
```

对于每个账户的配置：

```json5
{
  channels: {
    telegram: {
      accounts: {
        main: {
          capabilities: {
            inlineButtons: "allowlist",
          },
        },
      },
    },
  },
}
```

范围：

- `off` — 内联按钮已禁用
- `dm` — 仅限 DM（阻止群组目标）
- `group` — 仅限群组（阻止 DM 目标）
- `all` — DM + 群组
- `allowlist` — DM + 群组，但仅允许 `allowFrom`/`groupAllowFrom` 中列出的发件人（与控制命令相同的规则）

默认值：`allowlist`。
旧版：`capabilities: ["inlineButtons"]` = `inlineButtons: "all"`。

### 发送按钮

使用带有 `buttons` 参数的消息工具：

```json5
{
  action: "send",
  channel: "telegram",
  to: "123456789",
  message: "Choose an option:",
  buttons: [
    [
      { text: "Yes", callback_data: "yes" },
      { text: "No", callback_data: "no" },
    ],
    [{ text: "Cancel", callback_data: "cancel" }],
  ],
}
```

当用户点击按钮时，回调数据将以以下格式作为消息发送回代理：
`callback_data: value`

### 配置选项

Telegram 功能可以在两个级别进行配置（如上所示的对象形式；仍然支持旧版字符串数组）：

- `channels.telegram.capabilities`: 应用于所有Telegram账户的全局默认功能配置，除非被覆盖。
- `channels.telegram.accounts.<account>.capabilities`: 针对每个账户的功能配置，可以覆盖该特定账户的全局默认设置。

当所有Telegram机器人/账户应具有相同的行为时使用全局设置。当不同的机器人需要不同的行为时使用按账户配置（例如，一个账户仅处理私信，而另一个则允许在群组中使用）。

## 访问控制（私信 + 群组）

### 私信访问

- 默认: `channels.telegram.dmPolicy = "pairing"`。未知发送者会收到配对码；消息会被忽略直到批准（码在1小时后过期）。
- 通过以下方式批准：
  - `openclaw pairing list telegram`
  - `openclaw pairing approve telegram <CODE>`
- 配对是用于Telegram私信的默认令牌交换方式。详情: [配对](/start/pairing)
- `channels.telegram.allowFrom` 接受数字用户ID（推荐）或 `@username` 条目。这不是机器人的用户名；使用人类发送者的ID。向导接受 `@username` 并尽可能将其解析为数字ID。

#### 查找您的Telegram用户ID

更安全（无需第三方机器人）：

1. 启动网关并私信您的机器人。
2. 运行 `openclaw logs --follow` 并查找 `from.id`。

替代方案（官方Bot API）：

1. 私信您的机器人。
2. 使用您的机器人令牌获取更新并读取 `message.from.id`:
   ```bash
   curl "https://api.telegram.org/bot<bot_token>/getUpdates"
   ```

第三方（隐私较低）：

- 私信 `@userinfobot` 或 `@getidsbot` 并使用返回的用户ID。

### 群组访问

两个独立的控制：

**1. 允许哪些群组**（通过 `channels.telegram.groups` 的群组白名单）：

- 没有 `groups` 配置 = 允许所有群组
- 有 `groups` 配置 = 仅允许列出的群组或 `"*"`
- 示例: `"groups": { "-1001234567890": {}, "*": {} }` 允许所有群组

**2. 允许哪些发送者**（通过 `channels.telegram.groupPolicy` 的发送者过滤）：

- `"open"` = 允许的群组中的所有发送者可以发消息
- `"allowlist"` = 仅允许 `channels.telegram.groupAllowFrom` 中的发送者发消息
- `"disabled"` = 完全不接受群组消息
  默认是 `groupPolicy: "allowlist"`（除非您添加 `groupAllowFrom` 否则会被阻止）。

大多数用户想要：`groupPolicy: "allowlist"` + `groupAllowFrom` + 在 `channels.telegram.groups` 中列出的具体群组

## 长轮询与Webhook

- 默认: 长轮询（不需要公共URL）。
- Webhook模式: 设置 `channels.telegram.webhookUrl` 和 `channels.telegram.webhookSecret`（可选 `channels.telegram.webhookPath`）。
  - 本地监听器绑定到 `0.0.0.0:8787` 并默认提供 `POST /telegram-webhook`。
  - 如果您的公共URL不同，请使用反向代理并将 `channels.telegram.webhookUrl` 指向公共端点。

## 回复线程

Telegram支持通过标签进行可选的线程回复：

- `[[reply_to_current]]` -- 回复触发消息。
- `[[reply_to:<id>]]` -- 回复特定消息ID。

由 `channels.telegram.replyToMode` 控制：

- `first` (默认), `all`, `off`.

## 音频消息（语音与文件）

Telegram 区分 **语音留言**（圆形气泡）和 **音频文件**（元数据卡片）。
OpenClaw 默认使用音频文件以保持向后兼容性。

要强制代理回复中的语音留言气泡，请在回复中包含此标签：

- `[[audio_as_voice]]` — 将音频作为语音留言发送而不是文件。

该标签会被从发送的文本中移除。其他渠道会忽略此标签。

对于消息工具发送，请设置 `asVoice: true` 并提供一个与语音兼容的音频 `media` URL
(`message` 在有媒体时是可选的)：

```json5
{
  action: "send",
  channel: "telegram",
  to: "123456789",
  media: "https://example.com/voice.ogg",
  asVoice: true,
}
```

## 贴纸

OpenClaw 支持接收和发送 Telegram 贴纸，并具有智能缓存功能。

### 接收贴纸

当用户发送贴纸时，OpenClaw 根据贴纸类型进行处理：

- **静态贴纸 (WEBP):** 下载并通过视觉处理。贴纸在消息内容中显示为 `<media:sticker>` 占位符。
- **动画贴纸 (TGS):** 跳过（不支持 Lottie 格式进行处理）。
- **视频贴纸 (WEBM):** 跳过（不支持视频格式进行处理）。

接收贴纸时可用的模板上下文字段：

- `Sticker` — 对象包含：
  - `emoji` — 与贴纸关联的表情符号
  - `setName` — 贴纸集名称
  - `fileId` — Telegram 文件 ID（发送相同的贴纸）
  - `fileUniqueId` — 用于缓存查找的稳定 ID
  - `cachedDescription` — 可用时的缓存视觉描述

### 贴纸缓存

贴纸通过 AI 的视觉能力进行处理以生成描述。由于相同的贴纸经常被重复发送，OpenClaw 缓存这些描述以避免冗余的 API 调用。

**工作原理：**

1. **首次遇到：** 贴纸图像被发送到 AI 进行视觉分析。AI 生成描述（例如，“一只热情挥手的卡通猫”）。
2. **缓存存储：** 描述与贴纸的文件 ID、表情符号和集名称一起保存。
3. **后续遇到：** 当再次看到相同的贴纸时，直接使用缓存的描述。图像不会被发送到 AI。

**缓存位置：** `~/.openclaw/telegram/sticker-cache.json`

**缓存条目格式：**

```json
{
  "fileId": "CAACAgIAAxkBAAI...",
  "fileUniqueId": "AgADBAADb6cxG2Y",
  "emoji": "👋",
  "setName": "CoolCats",
  "description": "A cartoon cat waving enthusiastically",
  "cachedAt": "2026-01-15T10:30:00.000Z"
}
```

**优点：**

- 通过避免对相同贴纸进行重复的视觉调用来减少 API 成本
- 对于缓存的贴纸响应更快（没有视觉处理延迟）
- 基于缓存描述启用贴纸搜索功能

缓存会随着接收到的贴纸自动填充。不需要手动管理缓存。

### 发送贴纸

代理可以使用 `sticker` 和 `sticker-search` 动作发送和搜索贴纸。这些默认情况下是禁用的，必须在配置中启用：

```json5
{
  channels: {
    telegram: {
      actions: {
        sticker: true,
      },
    },
  },
}
```

**发送贴纸：**

```json5
{
  action: "sticker",
  channel: "telegram",
  to: "123456789",
  fileId: "CAACAgIAAxkBAAI...",
}
```

参数：

- `fileId` (必需) — 贴纸的 Telegram 文件 ID。在接收贴纸时从 `Sticker.fileId` 获取，或从 `sticker-search` 结果获取。
- `replyTo` (可选) — 回复的消息 ID。
- `threadId` (可选) — 论坛主题的消息线程 ID。

**搜索贴纸：**

代理可以通过描述、表情符号或集合名称搜索缓存中的贴纸：

```json5
{
  action: "sticker-search",
  channel: "telegram",
  query: "cat waving",
  limit: 5,
}
```

从缓存中返回匹配的贴纸：

```json5
{
  ok: true,
  count: 2,
  stickers: [
    {
      fileId: "CAACAgIAAxkBAAI...",
      emoji: "👋",
      description: "A cartoon cat waving enthusiastically",
      setName: "CoolCats",
    },
  ],
}
```

搜索会在描述文本、表情符号字符和集合名称之间进行模糊匹配。

**带线程的示例：**

```json5
{
  action: "sticker",
  channel: "telegram",
  to: "-1001234567890",
  fileId: "CAACAgIAAxkBAAI...",
  replyTo: 42,
  threadId: 123,
}
```

## 流式传输（草案）

当代理生成响应时，Telegram 可以流式传输 **草稿气泡**。
OpenClaw 使用 Bot API `sendMessageDraft`（不是真实消息），然后将最终回复作为正常消息发送。

要求（Telegram Bot API 9.3+）：

- **启用主题的私人聊天**（机器人的论坛主题模式）。
- 入站消息必须包含 `message_thread_id`（私人主题线程）。
- 对于群组/超级群组/频道，忽略流式传输。

配置：

- `channels.telegram.streamMode: "off" | "partial" | "block"` (默认: `partial`)
  - `partial`: 使用最新的流式文本更新草稿气泡。
  - `block`: 以更大的块（分块）更新草稿气泡。
  - `off`: 禁用草稿流式传输。
- 可选（仅适用于 `streamMode: "block"`）：
  - `channels.telegram.draftChunk: { minChars?, maxChars?, breakPreference? }`
    - 默认值: `minChars: 200`, `maxChars: 800`, `breakPreference: "paragraph"`（限制为 `channels.telegram.textChunkLimit`）。

注意：草稿流式传输与 **块流式传输**（频道消息）分开。
块流式传输默认关闭，如果需要早期的 Telegram 消息而不是草稿更新，则需要 `channels.telegram.blockStreaming: true`。

推理流（仅限 Telegram）：

- `/reasoning stream` 在生成回复时将推理流式传输到草稿气泡，然后发送最终答案而不包括推理。
- 如果 `channels.telegram.streamMode` 是 `off`，则禁用推理流。
  更多上下文：[流式传输 + 分块](/concepts/streaming)。

## 重试策略

出站 Telegram API 调用在遇到瞬态网络错误/429 错误时会进行指数退避和抖动重试。通过 `channels.telegram.retry` 进行配置。参见 [重试策略](/concepts/retry)。

## 代理工具（消息 + 反应）

- 工具：`telegram` 带有 `sendMessage` 操作 (`to`, `content`, 可选 `mediaUrl`, `replyToMessageId`, `messageThreadId`)。
- 工具：`telegram` 带有 `react` 操作 (`chatId`, `messageId`, `emoji`)。
- 工具：`telegram` 带有 `deleteMessage` 操作 (`chatId`, `messageId`)。
- 反应移除语义：参见 [/tools/reactions](/tools/reactions)。
- 工具门控：`channels.telegram.actions.reactions`, `channels.telegram.actions.sendMessage`, `channels.telegram.actions.deleteMessage`（默认：启用），以及 `channels.telegram.actions.sticker`（默认：禁用）。

## 反应通知

**反应的工作原理：**
Telegram 反应作为 **单独的 `message_reaction` 事件** 到达，而不是作为消息负载中的属性。当用户添加一个反应时，OpenClaw：

1. 从 Telegram API 接收 `message_reaction` 更新
2. 将其转换为 **系统事件**，格式为：`"Telegram reaction added: {emoji} by {user} on msg {id}"`
3. 使用与常规消息相同的 **会话密钥** 入队系统事件
4. 当该对话中下一条消息到达时，系统事件被排出并前置到代理的上下文中

代理将反应视为对话历史中的 **系统通知**，而不是消息元数据。

**配置：**

- `channels.telegram.reactionNotifications`：控制哪些反应触发通知
  - `"off"` — 忽略所有反应
  - `"own"` — 当用户对机器人消息作出反应时通知（尽力而为；内存中）（默认）
  - `"all"` — 对所有反应通知

- `channels.telegram.reactionLevel`：控制代理的反应能力
  - `"off"` — 代理无法对消息作出反应
  - `"ack"` — 机器人发送确认反应（处理时显示 👀）（默认）
  - `"minimal"` — 代理可以少量反应（指南：每 5-10 次交互一次）
  - `"extensive"` — 代理可以根据情况大量反应

**论坛群组：** 论坛群组中的反应包括 `message_thread_id` 并使用类似 `agent:main:telegram:group:{chatId}:topic:{threadId}` 的会话密钥。这确保了同一主题中的反应和消息保持在一起。

**示例配置：**

```json5
{
  channels: {
    telegram: {
      reactionNotifications: "all", // See all reactions
      reactionLevel: "minimal", // Agent can react sparingly
    },
  },
}
```

**要求：**

- Telegram 机器人必须在 `allowed_updates` 中显式请求 `message_reaction`（由 OpenClaw 自动配置）
- 对于 Webhook 模式，反应包含在 Webhook `allowed_updates` 中
- 对于轮询模式，反应包含在 `getUpdates` `allowed_updates` 中

## 交付目标（CLI/cron）

- 使用聊天 ID (`123456789`) 或用户名 (`@name`) 作为目标。
- 示例：`openclaw message send --channel telegram --target 123456789 --message "hi"`。

## 故障排除

**Bot 不会对群组中的非提及消息做出响应：**

- 如果设置了 `channels.telegram.groups.*.requireMention=false`，Telegram 的 Bot API **隐私模式** 必须被禁用。
  - BotFather: `/setprivacy` → **Disable** (然后移除并重新添加机器人到群组)
- `openclaw channels status` 在配置期望未提及的群组消息时会显示警告。
- `openclaw channels status --probe` 还可以检查显式数字群组ID的成员身份（它不能审核通配符 `"*"` 规则）。
- 快速测试: `/activation always` (仅限会话；使用配置以实现持久性)

**Bot 完全看不到群组消息：**

- 如果设置了 `channels.telegram.groups`，群组必须被列出或使用 `"*"`
- 检查 @BotFather 中的隐私设置 → "Group Privacy" 应该是 **OFF**
- 验证机器人实际上是群组成员（而不仅仅是没有读取权限的管理员）
- 检查网关日志: `openclaw logs --follow` (查找 "skipping group message")

**Bot 对提及做出响应但不对 `/activation always` 做出响应：**

- `/activation` 命令更新会话状态但不会持久化到配置
- 为了持久化行为，将群组添加到 `channels.telegram.groups` 使用 `requireMention: false`

**像 `/status` 这样的命令不起作用：**

- 确保您的 Telegram 用户ID已授权（通过配对或 `channels.telegram.allowFrom`）
- 即使在具有 `groupPolicy: "open"` 的群组中，命令也需要授权

**Node 22+ 上的长轮询立即中止（通常与代理/自定义获取一起使用）：**

- Node 22+ 对 `AbortSignal` 实例更加严格；外部信号可以立即中止 `fetch` 调用。
- 升级到一个 OpenClaw 构建以规范化中止信号，或者在升级之前在 Node 20 上运行网关。

**Bot 启动后，然后静默停止响应（或记录 `HttpError: Network request ... failed`）：**

- 某些主机首先将 `api.telegram.org` 解析为 IPv6。如果您的服务器没有工作的 IPv6 出站连接，grammY 可能会在仅 IPv6 请求上卡住。
- 通过启用 IPv6 出站 **或** 强制 `api.telegram.org` 的 IPv4 解析来修复（例如，使用 IPv4 A 记录添加一个 `/etc/hosts` 条目，或在操作系统 DNS 栈中优先使用 IPv4），然后重启网关。
- 快速检查: `dig +short api.telegram.org A` 和 `dig +short api.telegram.org AAAA` 以确认 DNS 返回的内容。

## 配置参考 (Telegram)

完整配置: [Configuration](/gateway/configuration)

提供商选项：

- `channels.telegram.enabled`: 启用/禁用频道启动。 - `channels.telegram.botToken`: 机器人令牌 (BotFather)。 - `channels.telegram.tokenFile`: 从文件路径读取令牌。 - `channels.telegram.dmPolicy`: `pairing | allowlist | open | disabled` (默认: pairing)。 - `channels.telegram.allowFrom`: 直接消息白名单 (ids/用户名)。`open` 需要 `"*"`。 - `channels.telegram.groupPolicy`: `open | allowlist | disabled` (默认: allowlist)。 - `channels.telegram.groupAllowFrom`: 群组发送者白名单 (ids/用户名)。 - `channels.telegram.groups`: 每群组默认设置 + 白名单 (使用 `"*"` 进行全局默认设置)。 - `channels.telegram.groups.<id>.requireMention`: 提及门控默认设置。 - `channels.telegram.groups.<id>.skills`: 技能过滤器 (省略 = 所有技能, 空 = 无)。 - `channels.telegram.groups.<id>.allowFrom`: 每群组发送者白名单覆盖。 - `channels.telegram.groups.<id>.systemPrompt`: 群组的额外系统提示。 - `channels.telegram.groups.<id>.enabled`: 当 `false` 时禁用群组。 - `channels.telegram.groups.<id>.topics.<threadId>.*`: 每主题覆盖 (与群组相同的字段)。 - `channels.telegram.groups.<id>.topics.<threadId>.requireMention`: 每主题提及门控覆盖。 - `channels.telegram.capabilities.inlineButtons`: `off | dm | group | all | allowlist` (默认: allowlist)。 - `channels.telegram.accounts.<account>.capabilities.inlineButtons`: 每账户覆盖。 - `channels.telegram.replyToMode`: `off | first | all` (默认: `first`)。 - `channels.telegram.textChunkLimit`: 出站块大小 (字符数)。 - `channels.telegram.chunkMode`: `length` (默认) 或 `newline` 在长度分块之前按空白行 (段落边界) 分割。 - `channels.telegram.linkPreview`: 切换出站消息的链接预览 (默认: true)。 - `channels.telegram.streamMode`: `off | partial | block` (草稿流式传输)。 - `channels.telegram.mediaMaxMb`: 入站/出站媒体限制 (MB)。 - `channels.telegram.retry`: 出站 Telegram API 调用的重试策略 (尝试次数, minDelayMs, maxDelayMs, jitter)。 - `channels.telegram.network.autoSelectFamily`: 覆盖 Node autoSelectFamily (true=启用, false=禁用)。默认在 Node 22 上禁用以避免 Happy Eyeballs 超时。 - `channels.telegram.proxy`: 机器人 API 调用的代理 URL (SOCKS/HTTP)。 - `channels.telegram.webhookUrl`: 启用 Webhook 模式 (需要 `channels.telegram.webhookSecret`)。 - `channels.telegram.webhookSecret`: Webhook 密钥 (当设置 webhookUrl 时需要)。 - `channels.telegram.webhookPath`: 本地 Webhook 路径 (默认 `/telegram-webhook`)。 - `channels.telegram.actions.reactions`: 门控 Telegram 工具反应。 - `channels.telegram.actions.sendMessage`: 门控 Telegram 工具消息发送。 - `channels.telegram.actions.deleteMessage`: 门控 Telegram 工具消息删除。 - `channels.telegram.actions.sticker`: 门控 Telegram 贴纸操作 — 发送和搜索 (默认: false)。

- `channels.telegram.reactionNotifications`: `off | own | all` — 控制哪些反应会触发系统事件（默认：未设置时为 `own`）。 - `channels.telegram.reactionLevel`: `off | ack | minimal | extensive` — 控制代理的反应能力（默认：未设置时为 `minimal`）。

相关全局选项：

- `agents.list[].groupChat.mentionPatterns` (mention gating patterns).
- `messages.groupChat.mentionPatterns` (global fallback).
- `commands.native` (默认为 `"auto"` → Telegram/Discord 上为开启，Slack 上为关闭), `commands.text`, `commands.useAccessGroups` (命令行为). 使用 `channels.telegram.commands.native` 覆盖。
- `messages.responsePrefix`, `messages.ackReaction`, `messages.ackReactionScope`, `messages.removeAckAfterReply`.