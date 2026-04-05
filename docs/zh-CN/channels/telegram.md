---
read_when:
  - 开发 Telegram 功能或 webhook
summary: Telegram 机器人支持状态、功能和配置
title: Telegram
x-i18n:
  generated_at: "2026-02-03T10:07:32Z"
  model: claude-opus-4-6
  provider: pi
  source_hash: 65da427e5f2383edb674054f8133a5777b2aae8a7c4bd78defa065124090a19c
  source_path: channels/telegram.md
  workflow: 15
---
# Telegram（Bot API）

状态：通过 grammY 支持机器人私信和群组，已可用于生产环境。默认使用长轮询；webhook 可选。

## 快速设置（入门）

1. 通过 **@BotFather**（[直达链接](https://t.me/BotFather)）创建机器人。确认用户名确实是 `@BotFather`，然后复制 token。
2. 设置 token：
   - 环境变量：`TELEGRAM_BOT_TOKEN=...`
   - 或配置：`channels.telegram.botToken: "..."`。
   - 如果两者都设置了，配置优先（环境变量回退仅适用于默认账户）。
3. 启动 Gateway 网关。
4. 私信访问默认使用配对模式；首次联系时需要批准配对码。

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

## 这是什么

- 一个由 Gateway 网关拥有的 Telegram Bot API 渠道。
- 确定性路由：回复返回到 Telegram；模型不会选择渠道。
- 私信共享智能体的主会话；群组保持隔离（`agent:<agentId>:telegram:group:<chatId>`）。

## 设置（快速路径）

### 1）创建机器人 token（BotFather）

1. 打开 Telegram 并与 **@BotFather**（[直达链接](https://t.me/BotFather)）对话。确认用户名确实是 `@BotFather`。
2. 运行 `/newbot`，然后按照提示操作（名称 + 以 `bot` 结尾的用户名）。
3. 复制 token 并安全保存。

可选的 BotFather 设置：

- `/setjoingroups` — 允许/拒绝将机器人添加到群组。
- `/setprivacy` — 控制机器人是否可以看到所有群组消息。

### 2）配置 token（环境变量或配置文件）

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

环境变量选项：`TELEGRAM_BOT_TOKEN=...`（适用于默认账户）。
如果环境变量和配置都设置了，配置优先。

多账户支持：使用 `channels.telegram.accounts`，每个账户有独立的 token 和可选的 `name`。参见 [`gateway/configuration`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 了解共享模式。

3. 启动 Gateway 网关。当 token 解析成功时 Telegram 启动（配置优先，环境变量回退）。
4. 私信访问默认为配对模式。机器人首次被联系时批准配对码。
5. 对于群组：添加机器人，决定隐私/管理员行为（见下文），然后设置 `channels.telegram.groups` 来控制提及门控和允许列表。

## Token + 隐私 + 权限（Telegram 端）

### Token 创建（BotFather）

- `/newbot` 创建机器人并返回 token（请保密）。
- 如果 token 泄露，通过 @BotFather 撤销/重新生成，并更新你的配置。

### 群组消息可见性（隐私模式）

Telegram 机器人默认启用**隐私模式**，这会限制它们接收哪些群组消息。
如果你的机器人必须看到*所有*群组消息，有两个选项：

- 使用 `/setprivacy` 禁用隐私模式**或**
- 将机器人添加为群组**管理员**（管理员机器人可以接收所有消息）。

**注意：** 当你切换隐私模式时，Telegram 要求将机器人从每个群组中移除并重新添加，更改才能生效。

### 群组权限（管理员权限）

管理员状态在群组内设置（Telegram UI）。管理员机器人始终接收所有群组消息，因此如果需要完全可见性，请使用管理员身份。

## 工作原理（行为）

- 入站消息被规范化为共享渠道信封，包含回复上下文和媒体占位符。
- 群组回复默认需要提及（原生 @提及或 `agents.list[].groupChat.mentionPatterns` / `messages.groupChat.mentionPatterns`）。
- 多智能体覆盖：在 `agents.list[].groupChat.mentionPatterns` 上设置每个智能体的模式。
- 回复始终路由回同一个 Telegram 聊天。
- 长轮询使用 grammY runner，每个聊天按顺序处理；总体并发受 `agents.defaults.maxConcurrent` 限制。
- Telegram Bot API 不支持已读回执；没有 `sendReadReceipts` 选项。

## 草稿流式传输

OpenClaw 可以在 Telegram 私信中使用 `sendMessageDraft` 流式传输部分回复。

要求：

- 在 @BotFather 中为机器人启用线程模式（论坛话题模式）。
- 仅限私聊线程（Telegram 在入站消息中包含 `message_thread_id`）。
- `channels.telegram.streamMode` 未设置为 `"off"`（默认：`"partial"`，`"block"` 启用分块草稿更新）。

草稿流式传输仅限私信；Telegram 在群组或频道中不支持此功能。

## 格式化（Telegram HTML）

- 出站 Telegram 文本使用 `parse_mode: "HTML"`（Telegram 支持的标签子集）。
- 类 Markdown 输入被渲染为 **Telegram 安全 HTML**（粗体/斜体/删除线/代码/链接）；块级元素被扁平化为带换行/项目符号的文本。
- 来自模型的原始 HTML 会被转义，以避免 Telegram 解析错误。
- 如果 Telegram 拒绝 HTML 负载，OpenClaw 会以纯文本重试相同的消息。

## 命令（原生 + 自定义）

OpenClaw 在启动时向 Telegram 的机器人菜单注册原生命令（如 `/status`、`/reset`、`/model`）。
你可以通过配置向菜单添加自定义命令：

```json5
{
  channels: {
    telegram: {
      customCommands: [
        { command: "backup", description: "Git 备份" },
        { command: "generate", description: "创建图片" },
      ],
    },
  },
}
```

## 故障排除

- 日志中出现 `setMyCommands failed` 通常意味着到 `api.telegram.org` 的出站 HTTPS/DNS 被阻止。
- 如果你看到 `sendMessage` 或 `sendChatAction` 失败，检查 IPv6 路由和 DNS。

更多帮助：[渠道故障排除](/channels/troubleshooting)。

注意：

- 自定义命令**仅是菜单条目**；除非你在其他地方处理它们，否则 OpenClaw 不会实现它们。
- 命令名称会被规范化（去除前导 `/`，转为小写），必须匹配 `a-z`、`0-9`、`_`（1-32 个字符）。
- 自定义命令**不能覆盖原生命令**。冲突会被忽略并记录日志。
- 如果禁用了 `commands.native`，则只注册自定义命令（如果没有则清空）。

## 限制

- 出站文本按 `channels.telegram.textChunkLimit` 分块（默认 4000）。
- 可选的换行分块：设置 `channels.telegram.chunkMode="newline"` 在长度分块之前按空行（段落边界）分割。
- 媒体下载/上传受 `channels.telegram.mediaMaxMb` 限制（默认 5）。
- Telegram Bot API 请求在 `channels.telegram.timeoutSeconds` 后超时（通过 grammY 默认 500）。设置较低的值以避免长时间挂起。
- 群组历史上下文使用 `channels.telegram.historyLimit`（或 `channels.telegram.accounts.*.historyLimit`），回退到 `messages.groupChat.historyLimit`。设置 `0` 禁用（默认 50）。
- 私信历史可以用 `channels.telegram.dmHistoryLimit`（用户轮次）限制。每用户覆盖：`channels.telegram.dms["<user_id>"].historyLimit`。

## 群组激活模式

默认情况下，机器人只响应群组中的提及（`@botname` 或 `agents.list[].groupChat.mentionPatterns` 中的模式）。要更改此行为：

### 通过配置（推荐）

```json5
{
  channels: {
    telegram: {
      groups: {
        "-1001234567890": { requireMention: false }, // 在此群组中始终响应
      },
    },
  },
}
```

**重要：** 设置 `channels.telegram.groups` 会创建一个**允许列表** - 只有列出的群组（或 `"*"`）会被接受。
论坛话题继承其父群组配置（allowFrom、requireMention、skills、prompts），除非你在 `channels.telegram.groups.<groupId>.topics.<topicId>` 下添加每话题覆盖。

要允许所有群组并始终响应：

```json5
{
  channels: {
    telegram: {
      groups: {
        "*": { requireMention: false }, // 所有群组，始终响应
      },
    },
  },
}
```

要保持所有群组仅提及响应（默认行为）：

```json5
{
  channels: {
    telegram: {
      groups: {
        "*": { requireMention: true }, // 或完全省略 groups
      },
    },
  },
}
```

### 通过命令（会话级别）

在群组中发送：

- `/activation always` - 响应所有消息
- `/activation mention` - 需要提及（默认）

**注意：** 命令只更新会话状态。要在重启后保持持久行为，请使用配置。

### 获取群组聊天 ID

将群组中的任何消息转发给 Telegram 上的 `@userinfobot` 或 `@getidsbot` 以查看聊天 ID（负数，如 `-1001234567890`）。

**提示：** 要获取你自己的用户 ID，私信机器人，它会回复你的用户 ID（配对消息），或者在命令启用后使用 `/whoami`。

**隐私注意：** `@userinfobot` 是第三方机器人。如果你更倾向于其他方式，将机器人添加到群组，发送一条消息，然后使用 `openclaw logs --follow` 读取 `chat.id`，或使用 Bot API `getUpdates`。

## 配置写入

默认情况下，Telegram 允许写入由渠道事件或 `/config set|unset` 触发的配置更新。

这发生在以下情况：

- 群组升级为超级群组，Telegram 发出 `migrate_to_chat_id`（聊天 ID 更改）。OpenClaw 可以自动迁移 `channels.telegram.groups`。
- 你在 Telegram 聊天中运行 `/config set` 或 `/config unset`（需要 `commands.config: true`）。

禁用方式：

```json5
{
  channels: { telegram: { configWrites: false } },
}
```

## 话题（论坛超级群组）

Telegram 论坛话题在每条消息中包含 `message_thread_id`。OpenClaw：

- 将 `:topic:<threadId>` 附加到 Telegram 群组会话键，使每个话题隔离。
- 发送输入指示器和回复时带上 `message_thread_id`，使响应保持在话题内。
- 通用话题（线程 id `1`）是特殊的：消息发送省略 `message_thread_id`（Telegram 会拒绝），但输入指示器仍然包含它。
- 在模板上下文中暴露 `MessageThreadId` + `IsForum` 用于路由/模板。
- 话题特定配置可在 `channels.telegram.groups.<chatId>.topics.<threadId>` 下设置（skills、允许列表、自动回复、系统提示、禁用）。
- 话题配置继承群组设置（requireMention、允许列表、skills、提示、enabled），除非每话题覆盖。

私聊在某些边缘情况下可能包含 `message_thread_id`。OpenClaw 保持私信会话键不变，但在存在线程 id 时仍将其用于回复/草稿流式传输。

## 内联按钮

Telegram 支持带回调按钮的内联键盘。

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

对于每账户配置：

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

作用域：

- `off` — 禁用内联按钮
- `dm` — 仅私信（群组目标被阻止）
- `group` — 仅群组（私信目标被阻止）
- `all` — 私信 + 群组
- `allowlist` — 私信 + 群组，但仅限 `allowFrom`/`groupAllowFrom` 允许的发送者（与控制命令规则相同）

默认：`allowlist`。
旧版：`capabilities: ["inlineButtons"]` = `inlineButtons: "all"`。

### 发送按钮

使用带 `buttons` 参数的消息工具：

```json5
{
  action: "send",
  channel: "telegram",
  to: "123456789",
  message: "选择一个选项：",
  buttons: [
    [
      { text: "是", callback_data: "yes" },
      { text: "否", callback_data: "no" },
    ],
    [{ text: "取消", callback_data: "cancel" }],
  ],
}
```

当用户点击按钮时，回调数据会以以下格式作为消息发送回智能体：
`callback_data: value`

### 配置选项

Telegram 功能可以在两个级别配置（上面显示的对象形式；旧版字符串数组仍然支持）：

- `channels.telegram.capabilities`：应用于所有 Telegram 账户的全局默认功能配置，除非被覆盖。
- `channels.telegram.accounts.<account>.capabilities`：每账户功能，覆盖该特定账户的全局默认值。

当所有 Telegram 机器人/账户应具有相同行为时使用全局设置。当不同机器人需要不同行为时使用每账户配置（例如，一个账户只处理私信，而另一个允许在群组中使用）。

## 访问控制（私信 + 群组）

### 私信访问

- 默认：`channels.telegram.dmPolicy = "pairing"`。未知发送者收到配对码；在批准之前消息被忽略（配对码 1 小时后过期）。
- 批准方式：
  - `openclaw pairing list telegram`
  - `openclaw pairing approve telegram <CODE>`
- 配对是 Telegram 私信使用的默认 token 交换。详情：[配对](/channels/pairing)
- `channels.telegram.allowFrom` 接受数字用户 ID（推荐）或 `@username` 条目。这**不是**机器人用户名；使用人类发送者的 ID。向导接受 `@username` 并在可能时将其解析为数字 ID。

#### 查找你的 Telegram 用户 ID

更安全（无第三方机器人）：

1. 启动 Gateway 网关并私信你的机器人。
2. 运行 `openclaw logs --follow` 并查找 `from.id`。

备选（官方 Bot API）：

1. 私信你的机器人。
2. 使用你的机器人 token 获取更新并读取 `message.from.id`：
   ```bash
   curl "https://api.telegram.org/bot<bot_token>/getUpdates"
   ```

第三方（隐私性较低）：

- 私信 `@userinfobot` 或 `@getidsbot` 并使用返回的用户 id。

### 群组访问

两个独立的控制：

**1. 允许哪些群组**（通过 `channels.telegram.groups` 的群组允许列表）：

- 无 `groups` 配置 = 允许所有群组
- 有 `groups` 配置 = 只允许列出的群组或 `"*"`
- 示例：`"groups": { "-1001234567890": {}, "*": {} }` 允许所有群组

**2. 允许哪些发送者**（通过 `channels.telegram.groupPolicy` 的发送者过滤）：

- `"open"` = 允许群组中的所有发送者发消息
- `"allowlist"` = 只有 `channels.telegram.groupAllowFrom` 中的发送者可以发消息
- `"disabled"` = 不接受任何群组消息
  默认是 `groupPolicy: "allowlist"`（除非添加 `groupAllowFrom` 否则被阻止）。

大多数用户需要：`groupPolicy: "allowlist"` + `groupAllowFrom` + 在 `channels.telegram.groups` 中列出特定群组

## 长轮询 vs webhook

- 默认：长轮询（不需要公共 URL）。
- Webhook 模式：设置 `channels.telegram.webhookUrl` 和 `channels.telegram.webhookSecret`（可选 `channels.telegram.webhookPath`）。
  - 本地监听器绑定到 `0.0.0.0:8787`，默认服务于 `POST /telegram-webhook`。
  - 如果你的公共 URL 不同，使用反向代理并将 `channels.telegram.webhookUrl` 指向公共端点。

## 回复线程

Telegram 通过标签支持可选的线程回复：

- `[[reply_to_current]]` -- 回复触发消息。
- `[[reply_to:<id>]]` -- 回复特定消息 id。

通过 `channels.telegram.replyToMode` 控制：

- `first`（默认）、`all`、`off`