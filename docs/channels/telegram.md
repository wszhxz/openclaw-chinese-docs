---
summary: "Telegram bot support status, capabilities, and configuration"
read_when:
  - Working on Telegram features or webhooks
title: "Telegram"
---
# Telegram (Bot API)

状态：通过 grammY 实现的 bot 私聊 + 群组功能已生产就绪。默认模式为长轮询；Webhook 模式可选。

<CardGroup cols={3}>
  <Card title="配对" icon="link" href="/channels/pairing">
    Telegram 的默认私聊策略为配对。
  </Card>
  <Card title="频道故障排除" icon="wrench" href="/channels/troubleshooting">
    跨频道诊断和修复指南。
  </Card>
  <Card title="网关配置" icon="settings" href="/gateway/configuration">
    完整的频道配置模式和示例。
  </Card>
</CardGroup>

## 快速设置

<Steps>
  <Step title="Create the bot token in BotFather">
    Open Telegram and chat with **@BotFather** (confirm the handle is exactly __CODE_BLOCK_0__).

    Run __CODE_BLOCK_1__, follow prompts, and save the token.

  </Step>

  <Step title="Configure token and DM policy">

__CODE_BLOCK_2__

    Env fallback: __CODE_BLOCK_3__ (default account only).

  </Step>

  <Step title="Start gateway and approve first DM">

__CODE_BLOCK_4__

    Pairing codes expire after 1 hour.

  </Step>

  <Step title="Add the bot to a group">
    Add the bot to your group, then set __CODE_BLOCK_5__ and __CODE_BLOCK_6__ to match your access model.
  </Step>
</Steps>

<Note>
Token resolution order is account-aware. In practice, config values win over env fallback, and __CODE_BLOCK_7__ only applies to the default account.
</Note>

## Telegram 端设置

<AccordionGroup>
  <Accordion title="Privacy mode and group visibility">
    Telegram bots default to **Privacy Mode**, which limits what group messages they receive.

    If the bot must see all group messages, either:

    - disable privacy mode via __CODE_BLOCK_8__, or
    - make the bot a group admin.

    When toggling privacy mode, remove + re-add the bot in each group so Telegram applies the change.

  </Accordion>

  <Accordion title="Group permissions">
    Admin status is controlled in Telegram group settings.

    Admin bots receive all group messages, which is useful for always-on group behavior.

  </Accordion>

  <Accordion title="Helpful BotFather toggles">

    - __CODE_BLOCK_9__ to allow/deny group adds
    - __CODE_BLOCK_10__ for group visibility behavior

  </Accordion>
</AccordionGroup>

## 访问控制和激活

<Tabs>
  <Tab title="私聊策略">
    `channels.telegram.dmPolicy` 控制私聊访问：

    - `pairing`（默认）
    - `allowlist`
    - `open`（需要 `allowFrom` 包含 `"*"`）
    - `disabled`

`channels.telegram.allowFrom` 接受数字的 Telegram 用户 ID。`telegram:` / `tg:` 前缀会被接受并标准化。
欢迎向导接受 `@username` 输入并将其解析为数字 ID。
如果您升级并且您的配置包含 `@username` 允许列表条目，请运行 `openclaw doctor --fix` 来解析它们（尽力而为；需要 Telegram 机器人令牌）。

### 查找您的 Telegram 用户 ID

更安全的方法（无需第三方机器人）：

1. 私信您的机器人。
2. 运行 `openclaw logs --follow`。
3. 阅读 `from.id`。

官方 Bot API 方法：

```bash
curl "https://api.telegram.org/bot<bot_token>/getUpdates"
```

第三方方法（隐私性较低）：`@userinfobot` 或 `@getidsbot`。

  </Tab>

  <Tab title="群组策略和允许列表">
    有两个独立的控制：

    1. **哪些群组被允许** (`channels.telegram.groups`)
       - 没有 `groups` 配置：所有群组都被允许
       - 配置了 `groups`：作为允许列表（显式 ID 或 `"*"`）

    2. **哪些发送者在群组中被允许** (`channels.telegram.groupPolicy`)
       - `open`
       - `allowlist`（默认）
       - `disabled`

    `groupAllowFrom` 用于群组发送者过滤。如果没有设置，Telegram 将回退到 `allowFrom`。
    `groupAllowFrom` 条目必须是数字的 Telegram 用户 ID。

    示例：允许一个特定群组中的任何成员：

```json5
{
  channels: {
    telegram: {
      groups: {
        "-1001234567890": {
          groupPolicy: "open",
          requireMention: false,
        },
      },
    },
  },
}
```

  </Tab>

  <Tab title="提及行为">
    群组回复默认需要提及。

    提及可以来自：

    - 原生 `@botusername` 提及，或
    - 提及模式在：
      - `agents.list[].groupChat.mentionPatterns`
      - `messages.groupChat.mentionPatterns`

    会话级别的命令切换：

    - `/activation always`
    - `/activation mention`

    这些仅更新会话状态。使用配置以实现持久化。

    持久化配置示例：

```json5
{
  channels: {
    telegram: {
      groups: {
        "*": { requireMention: false },
      },
    },
  },
}
```

    获取群组聊天 ID：

    - 将群组消息转发到 `@userinfobot` / `@getidsbot`
    - 或从 `openclaw logs --follow` 读取 `chat.id`
    - 或检查 Bot API `getUpdates`

  </Tab>
</Tabs>

## 运行时行为

- Telegram 由网关进程拥有。
- 路由是确定性的：Telegram 入站消息回复给 Telegram（模型不选择频道）。
- 入站消息规范化为共享频道信封，包含回复元数据和媒体占位符。
- 群组会话通过群组 ID 隔离。论坛主题附加 `:topic:<threadId>` 以保持主题隔离。
- 私人消息可以携带 `message_thread_id`；OpenClaw 使用线程感知会话密钥路由它们，并保留回复的线程 ID。
- 长轮询使用 grammY 运行器，每个聊天/每个线程进行排序。整体运行器接收并发使用 `agents.defaults.maxConcurrent`。
- Telegram Bot API 不支持已读回执 (`sendReadReceipts` 不适用)。

## 功能参考

<AccordionGroup>
  <Accordion title="实时流预览（消息编辑）">
    OpenClaw 可以通过发送临时 Telegram 消息并随着文本到达进行编辑来流式传输部分回复。

    要求：

    - `channels.telegram.streaming` 是 `off | partial | block | progress`（默认：`off`）
    - `progress` 映射到 Telegram 上的 `partial`（兼容跨频道命名）
    - 旧版 `channels.telegram.streamMode` 和布尔值 `streaming` 自动映射

    这在直接聊天和群组/主题中都适用。

    对于仅文本的回复，OpenClaw 保持相同的预览消息并在原地进行最终编辑（没有第二条消息）。

    对于复杂的回复（例如媒体负载），OpenClaw 回退到正常的最终交付，然后清理预览消息。

    预览流与块流分开。当显式为 Telegram 启用块流时，OpenClaw 跳过预览流以避免双重流式传输。

    仅 Telegram 的推理流：

    - `/reasoning stream` 在生成时将推理发送到实时预览
    - 最终答案发送时不带推理文本

  </Accordion>

  <Accordion title="格式化和 HTML 回退">
    出站文本使用 Telegram `parse_mode: "HTML"`。

    - 类似 Markdown 的文本渲染为 Telegram 安全的 HTML。
    - 原始模型 HTML 被转义以减少 Telegram 解析失败。
    - 如果 Telegram 拒绝解析的 HTML，OpenClaw 将重试为纯文本。

    链接预览默认启用，可以通过 `channels.telegram.linkPreview: false` 禁用。

  </Accordion>

  <Accordion title="本机命令和自定义命令">
    Telegram 命令菜单注册在启动时由 `setMyCommands` 处理。

    本机命令默认设置：

    - `commands.native: "auto"` 为 Telegram 启用本机命令

    添加自定义命令菜单项：

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

    规则：

- 名称已规范化（去除前导 `/`，转为小写）
    - 有效模式：`a-z`，`0-9`，`_`，长度 `1..32`
    - 自定义命令不能覆盖原生命令
    - 冲突/重复项会被跳过并记录

    注意事项：

    - 自定义命令仅是菜单项；它们不会自动实现行为
    - 即使在Telegram菜单中未显示，插件/技能命令仍可正常工作

    如果禁用了原生命令，内置命令将被移除。自定义/插件命令如果已配置，仍可注册。

    常见设置失败原因：

    - `setMyCommands failed` 通常意味着对外DNS/HTTPS到 `api.telegram.org` 被阻止。

    ### 设备配对命令 (`device-pair` 插件)

    当安装了 `device-pair` 插件时：

    1. `/pair` 生成设置码
    2. 将代码粘贴到iOS应用中
    3. `/pair approve` 批准最新的待处理请求

    更多详情：[配对](/channels/pairing#pair-via-telegram-recommended-for-ios).

  </Accordion>

  <Accordion title="内联按钮">
    配置内联键盘范围：

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

    按账户覆盖：

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

    - `off`
    - `dm`
    - `group`
    - `all`
    - `allowlist` (默认)

    旧版 `capabilities: ["inlineButtons"]` 映射到 `inlineButtons: "all"`。

    消息操作示例：

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

    回调点击会以文本形式传递给代理：
    `callback_data: <value>`

  </Accordion>

  <Accordion title="Telegram消息操作用于代理和自动化">
    Telegram工具操作包括：

    - `sendMessage` (`to`，`content`，可选 `mediaUrl`，`replyToMessageId`，`messageThreadId`)
    - `react` (`chatId`，`messageId`，`emoji`)
    - `deleteMessage` (`chatId`，`messageId`)
    - `editMessage` (`chatId`，`messageId`，`content`)

    频道消息操作暴露人体工程学别名 (`send`，`react`，`delete`，`edit`，`sticker`，`sticker-search`)。

    网关控制：

    - `channels.telegram.actions.sendMessage`
    - `channels.telegram.actions.editMessage`
    - `channels.telegram.actions.deleteMessage`
    - `channels.telegram.actions.reactions`
    - `channels.telegram.actions.sticker` (默认：禁用)

    反应移除语义：[/tools/reactions](/tools/reactions)

  </Accordion>

  <Accordion title="回复线程标签">
    Telegram支持在生成的输出中使用显式回复线程标签：

- `[[reply_to_current]]` 回复触发消息
- `[[reply_to:<id>]]` 回复特定的 Telegram 消息 ID

`channels.telegram.replyToMode` 控制处理：

- `off`（默认）
- `first`
- `all`

注意：`off` 禁用隐式回复线程。显式的 `[[reply_to_*]]` 标签仍然有效。

</Accordion>

<Accordion title="论坛主题和线程行为">
论坛超级群组：

- 主题会话密钥附加 `:topic:<threadId>`
- 回复和输入目标为主题线程
- 主题配置路径：
  `channels.telegram.groups.<chatId>.topics.<threadId>`

通用主题 (`threadId=1`) 特殊情况：

- 发送消息省略 `message_thread_id`（Telegram 拒绝 `sendMessage(...thread_id=1)`）
- 输入操作仍然包括 `message_thread_id`

主题继承：主题条目继承群组设置，除非被覆盖 (`requireMention`, `allowFrom`, `skills`, `systemPrompt`, `enabled`, `groupPolicy`)。

模板上下文包括：

- `MessageThreadId`
- `IsForum`

DM 线程行为：

- 与 `message_thread_id` 的私人聊天保持 DM 路由但使用线程感知的会话密钥/回复目标。

</Accordion>

<Accordion title="音频、视频和贴纸">
### 音频消息

Telegram 区分语音留言和音频文件。

- 默认：音频文件行为
- 在代理回复中使用标签 `[[audio_as_voice]]` 强制发送语音留言

消息操作示例：

```json5
{
  action: "send",
  channel: "telegram",
  to: "123456789",
  media: "https://example.com/voice.ogg",
  asVoice: true,
}
```

### 视频消息

Telegram 区分视频文件和视频留言。

消息操作示例：

```json5
{
  action: "send",
  channel: "telegram",
  to: "123456789",
  media: "https://example.com/video.mp4",
  asVideoNote: true,
}
```

视频留言不支持标题；提供的消息文本将单独发送。

### 贴纸

入站贴纸处理：

- 静态 WEBP：下载并处理（占位符 `<media:sticker>`）
- 动画 TGS：跳过
- 视频 WEBM：跳过

贴纸上下文字段：

- `Sticker.emoji`
- `Sticker.setName`
- `Sticker.fileId`
- `Sticker.fileUniqueId`
- `Sticker.cachedDescription`

贴纸缓存文件：

- `~/.openclaw/telegram/sticker-cache.json`

贴纸描述一次（如果可能），并缓存以减少重复的视觉调用。

启用贴纸操作：

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

发送贴纸操作：

```json5
{
  action: "sticker",
  channel: "telegram",
  to: "123456789",
  fileId: "CAACAgIAAxkBAAI...",
}
```

搜索缓存贴纸：

```json5
{
  action: "sticker-search",
  channel: "telegram",
  query: "cat waving",
  limit: 5,
}
```

</Accordion>

<Accordion title="Reaction notifications">
    Telegram reactions arrive as `message_reaction` updates (separate from message payloads).

    当启用时，OpenClaw 入队系统事件，例如：

    - `Telegram reaction added: 👍 by Alice (@alice) on msg 42`

    配置:

    - `channels.telegram.reactionNotifications`: `off | own | all` (默认: `own`)
    - `channels.telegram.reactionLevel`: `off | ack | minimal | extensive` (默认: `minimal`)

    注意事项:

    - `own` 表示仅对机器人发送的消息的用户反应（通过已发送消息缓存尽力实现）。
    - Telegram 在反应更新中不提供线程 ID。
      - 非论坛群组路由到群聊会话
      - 论坛群组路由到群组通用主题会话 (`:topic:1`)，而不是确切的原始主题

    `allowed_updates` 对于轮询/网络钩子包括 `message_reaction` 自动。

  </Accordion>

  <Accordion title="Ack reactions">
    `ackReaction` 发送一个确认表情符号，当 OpenClaw 正在处理传入消息时。

    解析顺序:

    - `channels.telegram.accounts.<accountId>.ackReaction`
    - `channels.telegram.ackReaction`
    - `messages.ackReaction`
    - 代理身份表情符号回退 (`agents.list[].identity.emoji`，否则 "👀")

    注意事项:

    - Telegram 期望 Unicode 表情符号（例如 "👀"）。
    - 使用 `""` 禁用某个频道或账户的反应。

  </Accordion>

  <Accordion title="Config writes from Telegram events and commands">
    频道配置写入默认启用 (`configWrites !== false`)。

    Telegram 触发的写入包括:

    - 群组迁移事件 (`migrate_to_chat_id`) 以更新 `channels.telegram.groups`
    - `/config set` 和 `/config unset` (需要命令启用)

    禁用:

```json5
{
  channels: {
    telegram: {
      configWrites: false,
    },
  },
}
```

  </Accordion>

  <Accordion title="Long polling vs webhook">
    默认: 长轮询。

    Webhook 模式:

    - 设置 `channels.telegram.webhookUrl`
    - 设置 `channels.telegram.webhookSecret` (设置 webhook URL 时必需)
    - 可选 `channels.telegram.webhookPath` (默认 `/telegram-webhook`)
    - 可选 `channels.telegram.webhookHost` (默认 `127.0.0.1`)

    Webhook 模式的默认本地监听器绑定到 `127.0.0.1:8787`。

    如果您的公共端点不同，请在前面放置反向代理，并将 `webhookUrl` 指向公共 URL。
    当您有意需要外部入口时，设置 `webhookHost` (例如 `0.0.0.0`)。

  </Accordion>

<Accordion title="限制、重试和CLI目标">
    - `channels.telegram.textChunkLimit` 默认值为4000。
    - `channels.telegram.chunkMode="newline"` 倾向于在长度分割前使用段落边界（空白行）。
    - `channels.telegram.mediaMaxMb`（默认值为5）限制传入的Telegram媒体下载/处理大小。
    - `channels.telegram.timeoutSeconds` 覆盖Telegram API客户端超时设置（如果未设置，则应用grammY默认值）。
    - 群组上下文历史记录使用 `channels.telegram.historyLimit` 或 `messages.groupChat.historyLimit`（默认值为50）；`0` 禁用。
    - 私聊历史记录控制：
      - `channels.telegram.dmHistoryLimit`
      - `channels.telegram.dms["<user_id>"].historyLimit`
    - 外发Telegram API重试可以通过 `channels.telegram.retry` 进行配置。

    CLI发送目标可以是数字聊天ID或用户名：

```bash
openclaw message send --channel telegram --target 123456789 --message "hi"
openclaw message send --channel telegram --target @name --message "hi"
```

  </Accordion>
</AccordionGroup>

## 故障排除

<AccordionGroup>
  <Accordion title="Bot does not respond to non mention group messages">

    - If __CODE_BLOCK_11__, Telegram privacy mode must allow full visibility.
      - BotFather: __CODE_BLOCK_12__ -> Disable
      - then remove + re-add bot to group
    - __CODE_BLOCK_13__ warns when config expects unmentioned group messages.
    - __CODE_BLOCK_14__ can check explicit numeric group IDs; wildcard __CODE_BLOCK_15__ cannot be membership-probed.
    - quick session test: __CODE_BLOCK_16__.

  </Accordion>

  <Accordion title="Bot not seeing group messages at all">

    - when __CODE_BLOCK_17__ exists, group must be listed (or include __CODE_BLOCK_18__)
    - verify bot membership in group
    - review logs: __CODE_BLOCK_19__ for skip reasons

  </Accordion>

  <Accordion title="Commands work partially or not at all">

    - authorize your sender identity (pairing and/or numeric __CODE_BLOCK_20__)
    - command authorization still applies even when group policy is __CODE_BLOCK_21__
    - __CODE_BLOCK_22__ usually indicates DNS/HTTPS reachability issues to __CODE_BLOCK_23__

  </Accordion>

  <Accordion title="Polling or network instability">

    - Node 22+ + custom fetch/proxy can trigger immediate abort behavior if AbortSignal types mismatch.
    - Some hosts resolve __CODE_BLOCK_24__ to IPv6 first; broken IPv6 egress can cause intermittent Telegram API failures.
    - Validate DNS answers:

__CODE_BLOCK_25__

  </Accordion>
</AccordionGroup>

更多帮助：[频道故障排除](/channels/troubleshooting)。

## Telegram配置参考指针

主要参考：

- `channels.telegram.enabled`: 启用/禁用频道启动。 - `channels.telegram.botToken`: 机器人令牌 (BotFather)。 - `channels.telegram.tokenFile`: 从文件路径读取令牌。 - `channels.telegram.dmPolicy`: `pairing | allowlist | open | disabled` (默认: pairing)。 - `channels.telegram.allowFrom`: 直接消息白名单 (数字Telegram用户ID)。`open` 需要 `"*"`。`openclaw doctor --fix` 可以将旧的 `@username` 条目解析为ID。 - `channels.telegram.groupPolicy`: `open | allowlist | disabled` (默认: allowlist)。 - `channels.telegram.groupAllowFrom`: 群组发送者白名单 (数字Telegram用户ID)。`openclaw doctor --fix` 可以将旧的 `@username` 条目解析为ID。 - `channels.telegram.groups`: 每个群组的默认设置 + 白名单 (使用 `"*"` 进行全局默认设置)。 - `channels.telegram.groups.<id>.groupPolicy`: 群组策略的每个群组覆盖 (`open | allowlist | disabled`)。 - `channels.telegram.groups.<id>.requireMention`: 提及门控默认设置。 - `channels.telegram.groups.<id>.skills`: 技能过滤器 (省略 = 所有技能, 空 = 无)。 - `channels.telegram.groups.<id>.allowFrom`: 每个群组发送者白名单覆盖。 - `channels.telegram.groups.<id>.systemPrompt`: 群组的额外系统提示。 - `channels.telegram.groups.<id>.enabled`: 当 `false` 时禁用群组。 - `channels.telegram.groups.<id>.topics.<threadId>.*`: 每个主题的覆盖 (与群组相同的字段)。 - `channels.telegram.groups.<id>.topics.<threadId>.groupPolicy`: 群组策略的每个主题覆盖 (`open | allowlist | disabled`)。 - `channels.telegram.groups.<id>.topics.<threadId>.requireMention`: 每个主题提及门控覆盖。 - `channels.telegram.capabilities.inlineButtons`: `off | dm | group | all | allowlist` (默认: allowlist)。 - `channels.telegram.accounts.<account>.capabilities.inlineButtons`: 每个账户覆盖。 - `channels.telegram.replyToMode`: `off | first | all` (默认: `off`)。 - `channels.telegram.textChunkLimit`: 出站块大小 (字符)。 - `channels.telegram.chunkMode`: `length` (默认) 或 `newline` 在长度分块之前按空白行 (段落边界) 分割。 - `channels.telegram.linkPreview`: 切换出站消息的链接预览 (默认: true)。 - `channels.telegram.streaming`: `off | partial | block | progress` (直播流预览; 默认: `off`; `progress` 映射到 `partial`)。 - `channels.telegram.mediaMaxMb`: 入站/出站媒体限制 (MB)。 - `channels.telegram.retry`: 出站Telegram API调用的重试策略 (尝试次数, minDelayMs, maxDelayMs, jitter)。 - `channels.telegram.network.autoSelectFamily`: 覆盖Node autoSelectFamily (true=启用, false=禁用)。默认在Node 22上禁用以避免Happy Eyeballs超时。 - `channels.telegram.proxy`: Bot API调用的代理URL (SOCKS/HTTP)。 - `channels.telegram.webhookUrl`: 启用Webhook模式 (需要 `channels.telegram.webhookSecret`)。 - `channels.telegram.webhookSecret`: Webhook密钥 (当设置webhookUrl时需要)。

- `channels.telegram.webhookPath`: 本地 webhook 路径（默认 `/telegram-webhook`）。 - `channels.telegram.webhookHost`: 本地 webhook 绑定主机（默认 `127.0.0.1`）。 - `channels.telegram.actions.reactions`: 控制 Telegram 工具反应。 - `channels.telegram.actions.sendMessage`: 控制 Telegram 工具消息发送。 - `channels.telegram.actions.deleteMessage`: 控制 Telegram 工具消息删除。 - `channels.telegram.actions.sticker`: 控制 Telegram 贴纸操作 — 发送和搜索（默认: false）。 - `channels.telegram.reactionNotifications`: `off | own | all` — 控制哪些反应会触发系统事件（默认: `own` 当未设置时）。 - `channels.telegram.reactionLevel`: `off | ack | minimal | extensive` — 控制代理的反应能力（默认: `minimal` 当未设置时）。

- [配置参考 - Telegram](/gateway/configuration-reference#telegram)

Telegram特定的高信号字段：

- startup/auth: `enabled`, `botToken`, `tokenFile`, `accounts.*`
- 访问控制: `dmPolicy`, `allowFrom`, `groupPolicy`, `groupAllowFrom`, `groups`, `groups.*.topics.*`
- 命令/菜单: `commands.native`, `customCommands`
- 线程/回复: `replyToMode`
- 流式传输: `streaming` (预览), `blockStreaming`
- 格式化/传递: `textChunkLimit`, `chunkMode`, `linkPreview`, `responsePrefix`
- 媒体/网络: `mediaMaxMb`, `timeoutSeconds`, `retry`, `network.autoSelectFamily`, `proxy`
- webhook: `webhookUrl`, `webhookSecret`, `webhookPath`, `webhookHost`
- 操作/功能: `capabilities.inlineButtons`, `actions.sendMessage|editMessage|deleteMessage|reactions|sticker`
- 反应: `reactionNotifications`, `reactionLevel`
- 写入/历史记录: `configWrites`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`

## 相关

- [配对](/channels/pairing)
- [通道路由](/channels/channel-routing)
- [多代理路由](/concepts/multi-agent)
- [故障排除](/channels/troubleshooting)