---
summary: "Discord bot support status, capabilities, and configuration"
read_when:
  - Working on Discord channel features
title: "Discord"
---
# Discord (Bot API)

状态：可通过官方 Discord gateway 使用 DMs 和 guild channels。

<CardGroup cols={3}>
  <Card title="Pairing" icon="link" href="/channels/pairing">
    Discord DMs 默认为 pairing 模式。
  </Card>
  <Card title="Slash commands" icon="terminal" href="/tools/slash-commands">
    原生命令行为和命令目录。
  </Card>
  <Card title="Channel troubleshooting" icon="wrench" href="/channels/troubleshooting">
    跨频道诊断和修复流程。
  </Card>
</CardGroup>

## 快速设置

您需要创建一个带 Bot 的新应用，将 Bot 添加到您的服务器，并将其与 OpenClaw 配对。我们建议将您的 Bot 添加到您自己的私有服务器中。如果您还没有，[请先创建一个](https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server)（选择 **Create My Own > For me and my friends**）。

<Steps>
  <Step title="Create a Discord application and bot">
    Go to the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**. Name it something like "OpenClaw".

    Click **Bot** on the sidebar. Set the **Username** to whatever you call your OpenClaw agent.

  </Step>

  <Step title="Enable privileged intents">
    Still on the **Bot** page, scroll down to **Privileged Gateway Intents** and enable:

    - **Message Content Intent** (required)
    - **Server Members Intent** (recommended; required for role allowlists and name-to-ID matching)
    - **Presence Intent** (optional; only needed for presence updates)

  </Step>

  <Step title="Copy your bot token">
    Scroll back up on the **Bot** page and click **Reset Token**.

    <Note>
    Despite the name, this generates your first token — nothing is being "reset."
    </Note>

    Copy the token and save it somewhere. This is your **Bot Token** and you will need it shortly.

  </Step>

  <Step title="Generate an invite URL and add the bot to your server">
    Click **OAuth2** on the sidebar. You'll generate an invite URL with the right permissions to add the bot to your server.

    Scroll down to **OAuth2 URL Generator** and enable:

    - __CODE_BLOCK_0__
    - __CODE_BLOCK_1__

    A **Bot Permissions** section will appear below. Enable:

    - View Channels
    - Send Messages
    - Read Message History
    - Embed Links
    - Attach Files
    - Add Reactions (optional)

    Copy the generated URL at the bottom, paste it into your browser, select your server, and click **Continue** to connect. You should now see your bot in the Discord server.

  </Step>

  <Step title="Enable Developer Mode and collect your IDs">
    Back in the Discord app, you need to enable Developer Mode so you can copy internal IDs.

    1. Click **User Settings** (gear icon next to your avatar) → **Advanced** → toggle on **Developer Mode**
    2. Right-click your **server icon** in the sidebar → **Copy Server ID**
    3. Right-click your **own avatar** → **Copy User ID**

    Save your **Server ID** and **User ID** alongside your Bot Token — you'll send all three to OpenClaw in the next step.

  </Step>

  <Step title="Allow DMs from server members">
    For pairing to work, Discord needs to allow your bot to DM you. Right-click your **server icon** → **Privacy Settings** → toggle on **Direct Messages**.

    This lets server members (including bots) send you DMs. Keep this enabled if you want to use Discord DMs with OpenClaw. If you only plan to use guild channels, you can disable DMs after pairing.

  </Step>

  <Step title="Step 0: Set your bot token securely (do not send it in chat)">
    Your Discord bot token is a secret (like a password). Set it on the machine running OpenClaw before messaging your agent.

__CODE_BLOCK_2__

    If OpenClaw is already running as a background service, use __CODE_BLOCK_3__ instead.

  </Step>

  <Step title="Configure OpenClaw and pair">

    <Tabs>
      <Tab title="Ask your agent">
        Chat with your OpenClaw agent on any existing channel (e.g. Telegram) and tell it. If Discord is your first channel, use the CLI / config tab instead.

        > "I already set my Discord bot token in config. Please finish Discord setup with User ID __CODE_BLOCK_4__ and Server ID __CODE_BLOCK_5__."
      </Tab>
      <Tab title="CLI / config">
        If you prefer file-based config, set:

__CODE_BLOCK_6__

        Env fallback for the default account:

__CODE_BLOCK_7__

        SecretRef values are also supported for __CODE_BLOCK_8__ (env/file/exec providers). See [Secrets Management](/gateway/secrets).

      </Tab>
    </Tabs>

  </Step>

  <Step title="Approve first DM pairing">
    Wait until the gateway is running, then DM your bot in Discord. It will respond with a pairing code.

    <Tabs>
      <Tab title="Ask your agent">
        Send the pairing code to your agent on your existing channel:

        > "Approve this Discord pairing code: __CODE_BLOCK_9__"
      </Tab>
      <Tab title="CLI">

__CODE_BLOCK_10__

      </Tab>
    </Tabs>

    Pairing codes expire after 1 hour.

    You should now be able to chat with your agent in Discord via DM.

  </Step>
</Steps>

<Note>
Token resolution is account-aware. Config token values win over env fallback. __CODE_BLOCK_11__ is only used for the default account.
</Note>

## 推荐：设置 Guild workspace

一旦 DMs 正常工作，您可以将 Discord 服务器设置为完整的工作空间，其中每个频道都拥有独立的 agent session 及其自身的 context。这适用于只有您和您的 Bot 的私有服务器。

<Steps>
  <Step title="Add your server to the guild allowlist">
    This enables your agent to respond in any channel on your server, not just DMs.

    <Tabs>
      <Tab title="Ask your agent">
        > "Add my Discord Server ID __CODE_BLOCK_12__ to the guild allowlist"
      </Tab>
      <Tab title="Config">

__CODE_BLOCK_13__

      </Tab>
    </Tabs>

  </Step>

  <Step title="Allow responses without @mention">
    By default, your agent only responds in guild channels when @mentioned. For a private server, you probably want it to respond to every message.

    <Tabs>
      <Tab title="Ask your agent">
        > "Allow my agent to respond on this server without having to be @mentioned"
      </Tab>
      <Tab title="Config">
        Set __CODE_BLOCK_14__ in your guild config:

__CODE_BLOCK_15__

      </Tab>
    </Tabs>

  </Step>

  <Step title="Plan for memory in guild channels">
    By default, long-term memory (MEMORY.md) only loads in DM sessions. Guild channels do not auto-load MEMORY.md.

    <Tabs>
      <Tab title="Ask your agent">
        > "When I ask questions in Discord channels, use memory_search or memory_get if you need long-term context from MEMORY.md."
      </Tab>
      <Tab title="Manual">
        If you need shared context in every channel, put the stable instructions in __CODE_BLOCK_16__ or __CODE_BLOCK_17__ (they are injected for every session). Keep long-term notes in __CODE_BLOCK_18__ and access them on demand with memory tools.
      </Tab>
    </Tabs>

  </Step>
</Steps>

现在在您的 Discord 服务器上创建一些频道并开始聊天。您的 agent 可以看到频道名称，且每个频道都有自己独立的隔离会话 —— 因此您可以设置 `#coding`, `#home`, `#research`, 或任何适合您 workflow 的内容。

## Runtime model

- Gateway 拥有 Discord 连接。
- 回复路由是确定性的：Discord 入站回复回 Discord。
- 默认情况下 (`session.dmScope=main`)，直接聊天共享 agent 主会话 (`agent:main:main`)。
- Guild channels 是隔离会话密钥 (`agent:<agentId>:discord:channel:<channelId>`)。
- Group DMs 默认被忽略 (`channels.discord.dm.groupEnabled=false`)。
- 原生 Slash commands 在隔离的命令会话中运行 (`agent:<agentId>:discord:slash:<userId>`)，同时仍将 `CommandTargetSessionKey` 携带到路由对话会话。

## Forum channels

Discord 论坛和媒体频道仅接受 thread 帖子。OpenClaw 支持两种创建方式：

- 向 forum parent 发送消息 (`channel:<forumId>`) 以自动创建 thread。Thread 标题使用您消息中的第一个非空行。
- 使用 `openclaw message thread create` 直接创建 thread。不要为 forum channels 传递 `--message-id`。

示例：发送到 forum parent 以创建 thread

```bash
openclaw message send --channel discord --target channel:<forumId> \
  --message "Topic title\nBody of the post"
```

示例：显式创建论坛 thread

```bash
openclaw message thread create --channel discord --target channel:<forumId> \
  --thread-name "Topic title" --message "Body of the post"
```

Forum parents 不接受 Discord components。如果您需要 components，请发送到 thread 本身 (`channel:<threadId>`)。

## Interactive components

OpenClaw 支持用于 agent 消息的 Discord components v2 容器。使用消息工具并附带 `components` 负载。交互结果作为普通入站消息路由回 agent，并遵循现有的 Discord `replyToMode` 设置。

支持的块：

- `text`, `section`, `separator`, `actions`, `media-gallery`, `file`
- Action rows 最多允许 5 个按钮或单个 select 菜单
- Select types: `string`, `user`, `role`, `mentionable`, `channel`

默认情况下，组件为单次使用。设置 `components.reusable=true` 以允许按钮、选择框和表单在过期前可多次使用。

若要限制谁可以点击按钮，请在该按钮上设置 `allowedUsers`（Discord 用户 ID、标签或 `*`）。配置后，不匹配的用户将收到临时拒绝通知。

`/model` 和 `/models` 斜杠命令会打开一个交互式模型选择器，包含提供商和模型下拉菜单以及提交步骤。选择器的回复是临时的，仅调用者可以使用它。

文件附件：

- `file` 块必须指向附件引用 (`attachment://<filename>`)
- 通过 `media`/`path`/`filePath` 提供附件（单个文件）；使用 `media-gallery` 处理多个文件
- 当上传名称应与附件引用匹配时，使用 `filename` 进行覆盖

模态表单：

- 添加 `components.modal`，最多包含 5 个字段
- 字段类型：`text`, `checkbox`, `radio`, `select`, `role-select`, `user-select`
- OpenClaw 会自动添加触发按钮

示例：

```json5
{
  channel: "discord",
  action: "send",
  to: "channel:123456789012345678",
  message: "Optional fallback text",
  components: {
    reusable: true,
    text: "Choose a path",
    blocks: [
      {
        type: "actions",
        buttons: [
          {
            label: "Approve",
            style: "success",
            allowedUsers: ["123456789012345678"],
          },
          { label: "Decline", style: "danger" },
        ],
      },
      {
        type: "actions",
        select: {
          type: "string",
          placeholder: "Pick an option",
          options: [
            { label: "Option A", value: "a" },
            { label: "Option B", value: "b" },
          ],
        },
      },
    ],
    modal: {
      title: "Details",
      triggerLabel: "Open form",
      fields: [
        { type: "text", label: "Requester" },
        {
          type: "select",
          label: "Priority",
          options: [
            { label: "Low", value: "low" },
            { label: "High", value: "high" },
          ],
        },
      ],
    },
  },
}
```

## 访问控制和路由

<Tabs>
  <Tab title="DM policy">
    __CODE_BLOCK_20__ controls DM access (legacy: __CODE_BLOCK_21__):

    - __CODE_BLOCK_22__ (default)
    - __CODE_BLOCK_23__
    - __CODE_BLOCK_24__ (requires __CODE_BLOCK_25__ to include __CODE_BLOCK_26__; legacy: __CODE_BLOCK_27__)
    - __CODE_BLOCK_28__

    If DM policy is not open, unknown users are blocked (or prompted for pairing in __CODE_BLOCK_29__ mode).

    Multi-account precedence:

    - __CODE_BLOCK_30__ applies only to the __CODE_BLOCK_31__ account.
    - Named accounts inherit __CODE_BLOCK_32__ when their own __CODE_BLOCK_33__ is unset.
    - Named accounts do not inherit __CODE_BLOCK_34__.

    DM target format for delivery:

    - __CODE_BLOCK_35__
    - __CODE_BLOCK_36__ mention

    Bare numeric IDs are ambiguous and rejected unless an explicit user/channel target kind is provided.

  </Tab>

  <Tab title="Guild policy">
    Guild handling is controlled by __CODE_BLOCK_37__:

    - __CODE_BLOCK_38__
    - __CODE_BLOCK_39__
    - __CODE_BLOCK_40__

    Secure baseline when __CODE_BLOCK_41__ exists is __CODE_BLOCK_42__.

    __CODE_BLOCK_43__ behavior:

    - guild must match __CODE_BLOCK_44__ (__CODE_BLOCK_45__ preferred, slug accepted)
    - optional sender allowlists: __CODE_BLOCK_46__ (stable IDs recommended) and __CODE_BLOCK_47__ (role IDs only); if either is configured, senders are allowed when they match __CODE_BLOCK_48__ OR __CODE_BLOCK_49__
    - direct name/tag matching is disabled by default; enable __CODE_BLOCK_50__ only as break-glass compatibility mode
    - names/tags are supported for __CODE_BLOCK_51__, but IDs are safer; __CODE_BLOCK_52__ warns when name/tag entries are used
    - if a guild has __CODE_BLOCK_53__ configured, non-listed channels are denied
    - if a guild has no __CODE_BLOCK_54__ block, all channels in that allowlisted guild are allowed

    Example:

__CODE_BLOCK_55__

    If you only set __CODE_BLOCK_56__ and do not create a __CODE_BLOCK_57__ block, runtime fallback is __CODE_BLOCK_58__ (with a warning in logs), even if __CODE_BLOCK_59__ is __CODE_BLOCK_60__.

  </Tab>

  <Tab title="Mentions and group DMs">
    Guild messages are mention-gated by default.

    Mention detection includes:

    - explicit bot mention
    - configured mention patterns (__CODE_BLOCK_61__, fallback __CODE_BLOCK_62__)
    - implicit reply-to-bot behavior in supported cases

    __CODE_BLOCK_63__ is configured per guild/channel (__CODE_BLOCK_64__).
    __CODE_BLOCK_65__ optionally drops messages that mention another user/role but not the bot (excluding @everyone/@here).

    Group DMs:

    - default: ignored (__CODE_BLOCK_66__)
    - optional allowlist via __CODE_BLOCK_67__ (channel IDs or slugs)

  </Tab>
</Tabs>

### 基于角色的代理路由

使用 `bindings[].match.roles` 按角色 ID 将 Discord 服务器成员路由到不同的代理。基于角色的绑定仅接受角色 ID，并在对等或父级对等绑定之后、仅在服务器绑定之前进行评估。如果绑定还设置了其他匹配字段（例如 `peer` + `guildId` + `roles`），则所有配置的字段都必须匹配。

```json5
{
  bindings: [
    {
      agentId: "opus",
      match: {
        channel: "discord",
        guildId: "123456789012345678",
        roles: ["111111111111111111"],
      },
    },
    {
      agentId: "sonnet",
      match: {
        channel: "discord",
        guildId: "123456789012345678",
      },
    },
  ],
}
```

## 开发者门户设置

<AccordionGroup>
  <Accordion title="Create app and bot">

    1. Discord Developer Portal -> **Applications** -> **New Application**
    2. **Bot** -> **Add Bot**
    3. Copy bot token

  </Accordion>

  <Accordion title="Privileged intents">
    In **Bot -> Privileged Gateway Intents**, enable:

    - Message Content Intent
    - Server Members Intent (recommended)

    Presence intent is optional and only required if you want to receive presence updates. Setting bot presence (__CODE_BLOCK_73__) does not require enabling presence updates for members.

  </Accordion>

  <Accordion title="OAuth scopes and baseline permissions">
    OAuth URL generator:

    - scopes: __CODE_BLOCK_74__, __CODE_BLOCK_75__

    Typical baseline permissions:

    - View Channels
    - Send Messages
    - Read Message History
    - Embed Links
    - Attach Files
    - Add Reactions (optional)

    Avoid __CODE_BLOCK_76__ unless explicitly needed.

  </Accordion>

  <Accordion title="Copy IDs">
    Enable Discord Developer Mode, then copy:

    - server ID
    - channel ID
    - user ID

    Prefer numeric IDs in OpenClaw config for reliable audits and probes.

  </Accordion>
</AccordionGroup>

## 原生命令和命令认证

- `commands.native` 默认为 `"auto"`，并针对 Discord 启用。
- 每通道覆盖：`channels.discord.commands.native`。
- `commands.native=false` 显式清除先前注册的 Discord 原生命令。
- 原生命令认证使用与正常消息处理相同的 Discord 白名单/策略。
- 对于未授权的用户，命令仍可能在 Discord 界面中可见；执行仍然强制执行 OpenClaw 认证并返回“未授权”。

有关命令目录和行为，请参阅 [斜杠命令](/tools/slash-commands)。

默认斜杠命令设置：

- `ephemeral: true`

## 功能详情

<AccordionGroup>
  <Accordion title="回复标签和原生回复">
    Discord 支持在代理输出中使用回复标签：

    - `[[reply_to_current]]`
    - `[[reply_to:<id>]]`

    由 `channels.discord.replyToMode` 控制：

    - `off`（默认）
    - `first`
    - `all`

    注意：`off` 禁用隐式回复线程。显式的 `[[reply_to_*]]` 标签仍然有效。

    消息 ID 会在上下文/历史中显示，以便代理可以定位特定消息。

  </Accordion>

  <Accordion title="实时流预览">
    OpenClaw 可以通过发送临时消息并在文本到达时编辑它来流式传输草稿回复。

    - `channels.discord.streaming` 控制预览流式传输 (`off` | `partial` | `block` | `progress`，默认值：`off`)。
    - `progress` 用于跨通道一致性并被接受，并映射到 Discord 上的 `partial`。
    - `channels.discord.streamMode` 是遗留别名，会自动迁移。
    - `partial` 随着令牌到达编辑单个预览消息。
    - `block` 发出草稿大小的块（使用 `draftChunk` 调整大小和断点）。

    示例：

```json5
{
  channels: {
    discord: {
      streaming: "partial",
    },
  },
}
```

    `block` 模式分块默认值（限制为 `channels.discord.textChunkLimit`）：

```json5
{
  channels: {
    discord: {
      streaming: "block",
      draftChunk: {
        minChars: 200,
        maxChars: 800,
        breakPreference: "paragraph",
      },
    },
  },
}
```

    预览流式传输仅限文本；媒体回复回退到正常交付。

    注意：预览流式传输与块流式传输分开。当明确为 Discord 启用块流式传输时，OpenClaw 跳过预览流以避免双重流式传输。

  </Accordion>

  <Accordion title="历史记录、上下文和线程行为">
    服务器历史记录上下文：

    - `channels.discord.historyLimit` 默认 `20`
    - 回退：`messages.groupChat.historyLimit`
    - `0` 禁用

    DM 历史记录控制：

    - `channels.discord.dmHistoryLimit`
    - `channels.discord.dms["<user_id>"].historyLimit`

Thread 行为：

    - Discord 线程作为频道会话进行路由
    - 父线程元数据可用于父会话链接
    - 除非存在特定线程条目，否则线程配置继承父频道配置

    频道主题作为 **不可信** 上下文注入（而非系统提示词）。

  </Accordion>

  <Accordion title="为子代理绑定的线程会话">
    Discord 可以将线程绑定到会话目标，以便该线程中的后续消息继续路由到同一会话（包括子代理会话）。

    命令：

    - `/focus <target>` 将当前/新线程绑定到子代理/会话目标
    - `/unfocus` 移除当前线程绑定
    - `/agents` 显示活动运行和绑定状态
    - `/session idle <duration|off>` 检查/更新聚焦绑定的非活动自动失焦
    - `/session max-age <duration|off>` 检查/更新聚焦绑定的硬性最大年龄

    配置：

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false, // opt-in
      },
    },
  },
}
```

    注意：

    - `session.threadBindings.*` 设置全局默认值。
    - `channels.discord.threadBindings.*` 覆盖 Discord 行为。
    - `spawnSubagentSessions` 必须为 true 才能为 `sessions_spawn({ thread: true })` 自动创建/绑定线程。
    - `spawnAcpSessions` 必须为 true 才能为 ACP 自动创建/绑定线程（`/acp spawn ... --thread ...` 或 `sessions_spawn({ runtime: "acp", thread: true })`）。
    - 如果账户禁用了线程绑定，则 `/focus` 及相关线程绑定操作不可用。

    请参阅 [子代理](/tools/subagents)、[ACP 代理](/tools/acp-agents) 和 [配置参考](/gateway/configuration-reference)。

  </Accordion>

  <Accordion title="持久化 ACP 频道绑定">
    对于稳定的“始终在线”ACP 工作区，请配置针对 Discord 对话的顶层类型化 ACP 绑定。

    配置路径：

    - `bindings[]` 配合 `type: "acp"` 和 `match.channel: "discord"`

    示例：

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "discord",
        accountId: "default",
        peer: { kind: "channel", id: "222222222222222222" },
      },
      acp: { label: "codex-main" },
    },
  ],
  channels: {
    discord: {
      guilds: {
        "111111111111111111": {
          channels: {
            "222222222222222222": {
              requireMention: false,
            },
          },
        },
      },
    },
  },
}
```

    注意：

    - 线程消息可以继承父频道的 ACP 绑定。
    - 在绑定的频道或线程中，`/new` 和 `/reset` 就地重置相同的 ACP 会话。
    - 临时线程绑定仍然有效，可以在活动期间覆盖目标解析。

    有关绑定行为详情，请参阅 [ACP 代理](/tools/acp-agents)。

  </Accordion>

  <Accordion title="反应通知">
    每服务器反应通知模式：

    - `off`
    - `own`（默认）
    - `all`
    - `allowlist`（使用 `guilds.<id>.users`）

    反应事件转换为系统事件并附加到已路由的 Discord 会话。

  </Accordion>

  <Accordion title="确认反应">
    当 OpenClaw 处理传入消息时，`ackReaction` 会发送一个确认表情符号。

    解析顺序：

    - `channels.discord.accounts.<accountId>.ackReaction`
    - `channels.discord.ackReaction`
    - `messages.ackReaction`
    - 代理身份表情回退（`agents.list[].identity.emoji`，否则 "👀"）

    注意：

    - Discord 接受 Unicode 表情符号或自定义表情符号名称。
    - 使用 `""` 禁用频道或账户的反应。

  </Accordion>

  <Accordion title="配置写入">
    频道发起的配置写入默认启用。

    这会影响 `/config set|unset` 流程（当命令功能启用时）。

    禁用：

```json5
{
  channels: {
    discord: {
      configWrites: false,
    },
  },
}
```

  </Accordion>

  <Accordion title="网关代理">
    通过带有 `channels.discord.proxy` 的 HTTP(S) 代理路由 Discord 网关 WebSocket 流量和启动 REST 查找（应用 ID + 白名单解析）。

```json5
{
  channels: {
    discord: {
      proxy: "http://proxy.example:8080",
    },
  },
}
```

    每账户覆盖：

```json5
{
  channels: {
    discord: {
      accounts: {
        primary: {
          proxy: "http://proxy.example:8080",
        },
      },
    },
  },
}
```

  </Accordion>

  <Accordion title="PluralKit 支持">
    启用 PluralKit 解析以将代理消息映射到系统成员身份：

```json5
{
  channels: {
    discord: {
      pluralkit: {
        enabled: true,
        token: "pk_live_...", // optional; needed for private systems
      },
    },
  },
}
```

    注意：

    - 白名单可以使用 `pk:<memberId>`
    - 成员显示名称仅在 `channels.discord.dangerouslyAllowNameMatching: true` 时按名称/标识符匹配
    - 查找使用原始消息 ID 且受时间窗口限制
    - 如果查找失败，代理消息被视为机器人消息并被丢弃，除非 `allowBots=true`

  </Accordion>

  <Accordion title="状态配置">
    当您设置状态或活动字段，或启用自动状态时，应用状态更新。

    仅状态示例：

```json5
{
  channels: {
    discord: {
      status: "idle",
    },
  },
}
```

    活动示例（自定义状态是默认活动类型）：

```json5
{
  channels: {
    discord: {
      activity: "Focus time",
      activityType: 4,
    },
  },
}
```

    流媒体示例：

```json5
{
  channels: {
    discord: {
      activity: "Live coding",
      activityType: 1,
      activityUrl: "https://twitch.tv/openclaw",
    },
  },
}
```

    活动类型映射：

    - 0: 游戏
    - 1: 直播（需要 `activityUrl`）
    - 2: 聆听
    - 3: 观看
    - 4: 自定义（使用活动文本作为状态状态；表情符号可选）
    - 5: 竞技

    自动状态示例（运行时健康信号）：

```json5
{
  channels: {
    discord: {
      autoPresence: {
        enabled: true,
        intervalMs: 30000,
        minUpdateIntervalMs: 15000,
        exhaustedText: "token exhausted",
      },
    },
  },
}
```

    自动状态将运行时可用性映射到 Discord 状态：健康 => 在线，降级或未知 => 空闲，耗尽或不可用 => 忙碌。可选文本覆盖：

    - `autoPresence.healthyText`
    - `autoPresence.degradedText`
    - `autoPresence.exhaustedText`（支持 `{reason}` 占位符）

  </Accordion>

  <Accordion title="Discord 中的执行审批">
    Discord 支持 DM 中的基于按钮的执行审批，并且可以选择在源频道中发布审批提示。

    配置路径：

    - `channels.discord.execApprovals.enabled`
    - `channels.discord.execApprovals.approvers`
    - `channels.discord.execApprovals.target`（`dm` | `channel` | `both`，默认值：`dm`）
    - `agentFilter`、`sessionFilter`、`cleanupAfterResolve`

    当 `target` 为 `channel` 或 `both` 时，审批提示在频道中可见。只有配置的审批人可以使用按钮；其他用户收到临时拒绝。审批提示包含命令文本，因此仅在可信频道中启用频道传递。如果无法从会话密钥派生频道 ID，OpenClaw 回退到 DM 传递。

    此处理程序的网关认证与其他网关客户端使用相同的共享凭证解析契约：

    - 环境变量优先本地认证（`OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD` 然后 `gateway.auth.*`）
    - 在本地模式下，当 `gateway.auth.*` 未设置时，可使用 `gateway.remote.*` 作为回退
    - 适用时通过 `gateway.remote.*` 支持远程模式
    - URL 覆盖是覆盖安全的：CLI 覆盖不重用隐式凭证，且环境覆盖仅使用环境凭证

    如果审批因未知审批 ID 而失败，请验证审批人列表和功能启用情况。

    相关文档：[执行审批](/tools/exec-approvals)

  </Accordion>
</AccordionGroup>

## 工具和动作门控

Discord 消息操作包括消息、频道管理、审核、状态和元数据操作。

核心示例：

- 消息：`sendMessage`、`readMessages`、`editMessage`、`deleteMessage`、`threadReply`
- 反应：`react`、`reactions`、`emojiList`
- 审核：`timeout`、`kick`、`ban`
- 状态：`setPresence`

动作门控位于 `channels.discord.actions.*` 下。

默认门控行为：

| 操作组                                                                                                                                                             | 默认值  |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| reactions, messages, threads, pins, polls, search, memberInfo, roleInfo, channelInfo, channels, voiceStatus, events, stickers, emojiUploads, stickerUploads, permissions | enabled  |
| roles                                                                                                                                                                    | disabled |
| moderation                                                                                                                                                               | disabled |
| presence                                                                                                                                                                 | disabled |

## 组件 v2 UI

OpenClaw 使用 Discord 组件 v2 进行执行批准和跨上下文标记。Discord 消息操作也可以接受 ``components`` 用于自定义 UI（高级；需要 Carbon 组件实例），而旧的 ``embeds`` 仍然可用但不推荐。

- ``channels.discord.ui.components.accentColor`` 设置 Discord 组件容器使用的强调色（hex）。
- 使用 ``channels.discord.accounts.<id>.ui.components.accentColor`` 按账户设置。
- 当存在组件 v2 时，``embeds`` 将被忽略。

示例：

````json5
{
  channels: {
    discord: {
      ui: {
        components: {
          accentColor: "#5865F2",
        },
      },
    },
  },
}
````

## 语音频道

OpenClaw 可以加入 Discord 语音频道以进行实时、连续的对话。这与语音消息附件是分开的。

要求：

- 启用原生命令（``commands.native`` 或 ``channels.discord.commands.native``）。
- 配置 ``channels.discord.voice``。
- 机器人需要在目标语音频道中拥有连接 + 说话权限。

使用仅限 Discord 的原生命令 ``/vc join|leave|status`` 来控制会话。该命令使用账户默认代理，并遵循与其他 Discord 命令相同的白名单和组策略规则。

自动加入示例：

````json5
{
  channels: {
    discord: {
      voice: {
        enabled: true,
        autoJoin: [
          {
            guildId: "123456789012345678",
            channelId: "234567890123456789",
          },
        ],
        daveEncryption: true,
        decryptionFailureTolerance: 24,
        tts: {
          provider: "openai",
          openai: { voice: "alloy" },
        },
      },
    },
  },
}
````

注意：

- ``voice.tts`` 仅覆盖 ``messages.tts`` 用于语音播放。
- 语音转录发言者从 Discord ``allowFrom``（或 ``dm.allowFrom``）派生所有者状态；非所有者发言者无法访问仅限所有者的工具（例如 ``gateway`` 和 ``cron``）。
- 语音默认启用；设置 ``channels.discord.voice.enabled=false`` 可禁用它。
- ``voice.daveEncryption`` 和 ``voice.decryptionFailureTolerance`` 传递到 ``@discordjs/voice`` 加入选项。
- 如果未设置，``@discordjs/voice`` 的默认值为 ``daveEncryption=true`` 和 ``decryptionFailureTolerance=24``。
- OpenClaw 还会监控接收解密失败，并在短时间内重复失败后通过离开/重新加入语音频道自动恢复。
- 如果接收日志反复显示 ``DecryptionFailed(UnencryptedWhenPassthroughDisabled)``，这可能是上游 ``@discordjs/voice`` 接收错误，追踪于 [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419)。

## 语音消息

Discord 语音消息显示波形预览，需要 OGG/Opus 音频加上元数据。OpenClaw 自动生成波形，但它需要网关主机上可用的 ``ffmpeg`` 和 ``ffprobe`` 来检查和转换音频文件。

要求和限制：

- 提供**本地文件路径**（URL 被拒绝）。
- 省略文本内容（Discord 不允许在同一负载中包含文本 + 语音消息）。
- 接受任何音频格式；OpenClaw 在需要时转换为 OGG/Opus。

示例：

````bash
message(action="send", channel="discord", target="channel:123", path="/path/to/audio.mp3", asVoice=true)
````

## 故障排除

`<AccordionGroup>
  <Accordion title="Used disallowed intents or bot sees no guild messages">

    - enable Message Content Intent
    - enable Server Members Intent when you depend on user/member resolution
    - restart gateway after changing intents

  </Accordion>

  <Accordion title="Guild messages blocked unexpectedly">

    - verify __CODE_BLOCK_29__
    - verify guild allowlist under __CODE_BLOCK_30__
    - if guild __CODE_BLOCK_31__ map exists, only listed channels are allowed
    - verify __CODE_BLOCK_32__ behavior and mention patterns

    Useful checks:

__CODE_BLOCK_33__

  </Accordion>

  <Accordion title="Require mention false but still blocked">
    Common causes:

    - __CODE_BLOCK_34__ without matching guild/channel allowlist
    - __CODE_BLOCK_35__ configured in the wrong place (must be under __CODE_BLOCK_36__ or channel entry)
    - sender blocked by guild/channel __CODE_BLOCK_37__ allowlist

  </Accordion>

  <Accordion title="Long-running handlers time out or duplicate replies">

    Typical logs:

    - __CODE_BLOCK_38__
    - __CODE_BLOCK_39__
    - __CODE_BLOCK_40__

    Listener budget knob:

    - single-account: __CODE_BLOCK_41__
    - multi-account: __CODE_BLOCK_42__

    Worker run timeout knob:

    - single-account: __CODE_BLOCK_43__
    - multi-account: __CODE_BLOCK_44__
    - default: __CODE_BLOCK_45__ (30 minutes); set __CODE_BLOCK_46__ to disable

    Recommended baseline:

__CODE_BLOCK_47__

    Use __CODE_BLOCK_48__ for slow listener setup and __CODE_BLOCK_49__
    only if you want a separate safety valve for queued agent turns.

  </Accordion>

  <Accordion title="Permissions audit mismatches">
    __CODE_BLOCK_50__ permission checks only work for numeric channel IDs.

    If you use slug keys, runtime matching can still work, but probe cannot fully verify permissions.

  </Accordion>

  <Accordion title="DM and pairing issues">

    - DM disabled: __CODE_BLOCK_51__
    - DM policy disabled: __CODE_BLOCK_52__ (legacy: __CODE_BLOCK_53__)
    - awaiting pairing approval in __CODE_BLOCK_54__ mode

  </Accordion>

  <Accordion title="Bot to bot loops">
    By default bot-authored messages are ignored.

    If you set __CODE_BLOCK_55__, use strict mention and allowlist rules to avoid loop behavior.
    Prefer __CODE_BLOCK_56__ to only accept bot messages that mention the bot.

  </Accordion>

  <Accordion title="Voice STT drops with DecryptionFailed(...)">

    - keep OpenClaw current (__CODE_BLOCK_57__) so the Discord voice receive recovery logic is present
    - confirm __CODE_BLOCK_58__ (default)
    - start from __CODE_BLOCK_59__ (upstream default) and tune only if needed
    - watch logs for:
      - __CODE_BLOCK_60__
      - __CODE_BLOCK_61__
    - if failures continue after automatic rejoin, collect logs and compare against [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419)

  </Accordion>
</AccordionGroup>`

## 配置参考指引

主要参考：

- [配置参考 - Discord](/gateway/configuration-reference#discord)

关键 Discord 字段：

- 启动/认证：``enabled``, ``token``, ``accounts.*``, ``allowBots``
- 策略：``groupPolicy``, ``dm.*``, ``guilds.*``, ``guilds.*.channels.*``
- 命令：``commands.native``, ``commands.useAccessGroups``, ``configWrites``, ``slashCommand.*``
- 事件队列：``eventQueue.listenerTimeout``（监听器预算）, ``eventQueue.maxQueueSize``, ``eventQueue.maxConcurrency``
- 入站工作器：``inboundWorker.runTimeoutMs``
- 回复/历史：``replyToMode``, ``historyLimit``, ``dmHistoryLimit``, ``dms.*.historyLimit``
- 发送：``textChunkLimit``, ``chunkMode``, ``maxLinesPerMessage``
- 流媒体：``streaming``（旧别名：``streamMode``）, ``draftChunk``, ``blockStreaming``, ``blockStreamingCoalesce``
- 媒体/重试：``mediaMaxMb``, ``retry``
  - ``mediaMaxMb`` 限制出站 Discord 上传（默认值：``8MB``）
- 操作：``actions.*``
- 在线状态：``activity``, ``status``, ``activityType``, ``activityUrl``
- UI：``ui.components.accentColor``
- 功能：``threadBindings``, 顶级 ``bindings[]`` (``type: "acp"``), ``pluralkit``, ``execApprovals``, ``intents``, ``agentComponents``, ``heartbeat``, ``responsePrefix``

## 安全与操作

- 将机器人令牌视为密钥（在受监督环境中首选 ``DISCORD_BOT_TOKEN``）。
- 授予最小权限 Discord 权限。
- 如果命令部署/状态过时，请重启网关并使用 ``openclaw channels status --probe`` 重新检查。

## 相关

- [配对](/channels/pairing)
- [频道路由](/channels/channel-routing)
- [多代理路由](/concepts/multi-agent)
- [故障排除](/channels/troubleshooting)
- [斜杠命令](/tools/slash-commands)