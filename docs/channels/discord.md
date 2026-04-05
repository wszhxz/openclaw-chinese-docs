---
summary: "Discord bot support status, capabilities, and configuration"
read_when:
  - Working on Discord channel features
title: "Discord"
---
# Discord (机器人 API)

状态：已通过官方 Discord 网关准备好支持私信和服务器频道。

<CardGroup cols={3}>
  <Card title="配对" icon="link" href="/channels/pairing">
    Discord 私信默认采用配对模式。
  </Card>
  <Card title="斜杠命令" icon="terminal" href="/tools/slash-commands">
    原生命令行为和命令目录。
  </Card>
  <Card title="频道故障排除" icon="wrench" href="/channels/troubleshooting">
    跨频道诊断和修复流程。
  </Card>
</CardGroup>

## 快速设置

您需要创建一个带有机器人的新应用，将机器人添加到您的服务器，并将其与 OpenClaw 配对。我们建议将您的机器人添加到您自己的私人服务器中。如果您还没有，请先[创建一个](https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server)（选择 **创建我自己的 > 我和我的朋友**）。

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

  <Step title="Set your bot token securely (do not send it in chat)">
    Your Discord bot token is a secret (like a password). Set it on the machine running OpenClaw before messaging your agent.

__CODE_BLOCK_2__

    If OpenClaw is already running as a background service, restart it via the OpenClaw Mac app or by stopping and restarting the __CODE_BLOCK_3__ process.

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

        Plaintext __CODE_BLOCK_8__ values are supported. SecretRef values are also supported for __CODE_BLOCK_9__ across env/file/exec providers. See [Secrets Management](/gateway/secrets).

      </Tab>
    </Tabs>

  </Step>

  <Step title="Approve first DM pairing">
    Wait until the gateway is running, then DM your bot in Discord. It will respond with a pairing code.

    <Tabs>
      <Tab title="Ask your agent">
        Send the pairing code to your agent on your existing channel:

        > "Approve this Discord pairing code: __CODE_BLOCK_10__"
      </Tab>
      <Tab title="CLI">

__CODE_BLOCK_11__

      </Tab>
    </Tabs>

    Pairing codes expire after 1 hour.

    You should now be able to chat with your agent in Discord via DM.

  </Step>
</Steps>

<Note>
Token resolution is account-aware. Config token values win over env fallback. __CODE_BLOCK_12__ is only used for the default account.
For advanced outbound calls (message tool/channel actions), an explicit per-call __CODE_BLOCK_13__ is used for that call. This applies to send and read/probe-style actions (for example read/search/fetch/thread/pins/permissions). Account policy/retry settings still come from the selected account in the active runtime snapshot.
</Note>

## 推荐：设置服务器工作区

一旦私信功能正常工作，您可以将 Discord 服务器设置为完整的工作区，其中每个频道都拥有独立的代理会话和上下文。这对于只有您和机器人的私人服务器来说是很推荐的。

<Steps>
  <Step title="Add your server to the guild allowlist">
    This enables your agent to respond in any channel on your server, not just DMs.

    <Tabs>
      <Tab title="Ask your agent">
        > "Add my Discord Server ID __CODE_BLOCK_14__ to the guild allowlist"
      </Tab>
      <Tab title="Config">

__CODE_BLOCK_15__

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
        Set __CODE_BLOCK_16__ in your guild config:

__CODE_BLOCK_17__

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
        If you need shared context in every channel, put the stable instructions in __CODE_BLOCK_18__ or __CODE_BLOCK_19__ (they are injected for every session). Keep long-term notes in __CODE_BLOCK_20__ and access them on demand with memory tools.
      </Tab>
    </Tabs>

  </Step>
</Steps>

现在在您的 Discord 服务器上创建一些频道并开始聊天。您的代理可以看到频道名称，并且每个频道都有自己隔离的会话——因此您可以设置 `#coding`、`#home`、`#research`，或任何适合您工作流程的内容。

## 运行时模型

- 网关拥有 Discord 连接。
- 回复路由是确定性的：Discord 入站消息回复回 Discord。
- 默认情况下 (`session.dmScope=main`)，直接聊天共享代理主会话 (`agent:main:main`)。
- 服务器频道是隔离的会话密钥 (`agent:<agentId>:discord:channel:<channelId>`)。
- 群组私信默认被忽略 (`channels.discord.dm.groupEnabled=false`)。
- 原生斜杠命令在隔离的命令会话中运行 (`agent:<agentId>:discord:slash:<userId>`)，同时仍将 `CommandTargetSessionKey` 携带到路由对话会话中。

## 论坛频道

Discord 论坛和媒体频道仅接受线程帖子。OpenClaw 支持两种创建方式：

- 向论坛父级发送消息 (`channel:<forumId>`) 以自动创建线程。线程标题使用您消息的第一行非空内容。
- 使用 `openclaw message thread create` 直接创建线程。对于论坛频道，请勿传递 `--message-id`。

示例：向论坛父级发送消息以创建线程

```bash
openclaw message send --channel discord --target channel:<forumId> \
  --message "Topic title\nBody of the post"
```

示例：显式创建论坛线程

```bash
openclaw message thread create --channel discord --target channel:<forumId> \
  --thread-name "Topic title" --message "Body of the post"
```

论坛父级不支持 Discord 组件。如果需要组件，请发送到线程本身 (`channel:<threadId>`)。

## 交互式组件

OpenClaw 支持用于代理消息的 Discord 组件 v2 容器。使用带有 `components` 负载的消息工具。交互结果将作为正常的入站消息路由回代理，并遵循现有的 Discord `replyToMode` 设置。

支持的区块：

- `text`, `section`, `separator`, `actions`, `media-gallery`, `file`
- 操作行最多允许 5 个按钮或一个选择菜单
- 选择类型：`string`, `user`, `role`, `mentionable`, `channel`

默认情况下，组件为一次性使用。设置 `components.reusable=true` 以允许按钮、选择和表单在过期前多次使用。

要限制谁可以单击按钮，请在该按钮上设置 `allowedUsers`（Discord 用户 ID、标签或 `*`）。配置后，不匹配的用户将收到临时拒绝通知。

`/model` 和 `/models` 斜杠命令会打开一个交互式模型选择器，包含提供者和模型下拉菜单以及提交步骤。选择器回复是临时的，只有调用用户可以将其使用。

文件附件：

- `file` 区块必须指向附件引用 (`attachment://<filename>`)
- 通过 `media`/`path`/`filePath` 提供附件（单个文件）；对于多个文件请使用 `media-gallery`
- 当需要与附件引用匹配时，使用 `filename` 覆盖上传名称

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
    __CODE_BLOCK_35__ controls DM access (legacy: __CODE_BLOCK_36__):

    - __CODE_BLOCK_37__ (default)
    - __CODE_BLOCK_38__
    - __CODE_BLOCK_39__ (requires __CODE_BLOCK_40__ to include __CODE_BLOCK_41__; legacy: __CODE_BLOCK_42__)
    - __CODE_BLOCK_43__

    If DM policy is not open, unknown users are blocked (or prompted for pairing in __CODE_BLOCK_44__ mode).

    Multi-account precedence:

    - __CODE_BLOCK_45__ applies only to the __CODE_BLOCK_46__ account.
    - Named accounts inherit __CODE_BLOCK_47__ when their own __CODE_BLOCK_48__ is unset.
    - Named accounts do not inherit __CODE_BLOCK_49__.

    DM target format for delivery:

    - __CODE_BLOCK_50__
    - __CODE_BLOCK_51__ mention

    Bare numeric IDs are ambiguous and rejected unless an explicit user/channel target kind is provided.

  </Tab>

  <Tab title="Guild policy">
    Guild handling is controlled by __CODE_BLOCK_52__:

    - __CODE_BLOCK_53__
    - __CODE_BLOCK_54__
    - __CODE_BLOCK_55__

    Secure baseline when __CODE_BLOCK_56__ exists is __CODE_BLOCK_57__.

    __CODE_BLOCK_58__ behavior:

    - guild must match __CODE_BLOCK_59__ (__CODE_BLOCK_60__ preferred, slug accepted)
    - optional sender allowlists: __CODE_BLOCK_61__ (stable IDs recommended) and __CODE_BLOCK_62__ (role IDs only); if either is configured, senders are allowed when they match __CODE_BLOCK_63__ OR __CODE_BLOCK_64__
    - direct name/tag matching is disabled by default; enable __CODE_BLOCK_65__ only as break-glass compatibility mode
    - names/tags are supported for __CODE_BLOCK_66__, but IDs are safer; __CODE_BLOCK_67__ warns when name/tag entries are used
    - if a guild has __CODE_BLOCK_68__ configured, non-listed channels are denied
    - if a guild has no __CODE_BLOCK_69__ block, all channels in that allowlisted guild are allowed

    Example:

__CODE_BLOCK_70__

    If you only set __CODE_BLOCK_71__ and do not create a __CODE_BLOCK_72__ block, runtime fallback is __CODE_BLOCK_73__ (with a warning in logs), even if __CODE_BLOCK_74__ is __CODE_BLOCK_75__.

  </Tab>

  <Tab title="Mentions and group DMs">
    Guild messages are mention-gated by default.

    Mention detection includes:

    - explicit bot mention
    - configured mention patterns (__CODE_BLOCK_76__, fallback __CODE_BLOCK_77__)
    - implicit reply-to-bot behavior in supported cases

    __CODE_BLOCK_78__ is configured per guild/channel (__CODE_BLOCK_79__).
    __CODE_BLOCK_80__ optionally drops messages that mention another user/role but not the bot (excluding @everyone/@here).

    Group DMs:

    - default: ignored (__CODE_BLOCK_81__)
    - optional allowlist via __CODE_BLOCK_82__ (channel IDs or slugs)

  </Tab>
</Tabs>

### 基于角色的代理路由

使用 `bindings[].match.roles` 根据角色 ID 将 Discord 服务器成员路由到不同的代理。基于角色的绑定仅接受角色 ID，并在同级或父级同级绑定之后、仅限服务器绑定之前进行评估。如果绑定还设置了其他匹配字段（例如 `peer` + `guildId` + `roles`），则所有配置的字段都必须匹配。

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

    Presence intent is optional and only required if you want to receive presence updates. Setting bot presence (__CODE_BLOCK_88__) does not require enabling presence updates for members.

  </Accordion>

  <Accordion title="OAuth scopes and baseline permissions">
    OAuth URL generator:

    - scopes: __CODE_BLOCK_89__, __CODE_BLOCK_90__

    Typical baseline permissions:

    - View Channels
    - Send Messages
    - Read Message History
    - Embed Links
    - Attach Files
    - Add Reactions (optional)

    Avoid __CODE_BLOCK_91__ unless explicitly needed.

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

- `commands.native` 默认为 `"auto"` 并已针对 Discord 启用。
- 每频道覆盖：`channels.discord.commands.native`。
- `commands.native=false` 显式清除先前注册的 Discord 原生命令。
- 原生命令认证使用与普通消息处理相同的 Discord 白名单/策略。
- 命令对于未授权的用户可能仍然在 Discord UI 中可见；执行仍强制执行 OpenClaw 认证并返回“未授权”。

有关命令目录和行为，请参阅 [斜杠命令](/tools/slash-commands)。

默认斜杠命令设置：

- `ephemeral: true`

## 功能详情

<AccordionGroup>
  <Accordion title="回复标签和本地回复">
    Discord 支持在代理输出中使用回复标签：

    - `[[reply_to_current]]`
    - `[[reply_to:<id>]]`

    由 `channels.discord.replyToMode` 控制：

    - `off`（默认）
    - `first`
    - `all`

    注意：`off` 禁用隐式回复线程。显式 `[[reply_to_*]]` 标签仍然有效。

    消息 ID 会在上下文/历史中显示，以便代理可以针对特定消息。

  </Accordion>

  <Accordion title="实时流预览">
    OpenClaw 可以通过发送临时消息并在文本到达时编辑它来流式传输草稿回复。

    - `channels.discord.streaming` 控制预览流式传输 (`off` | `partial` | `block` | `progress`，默认：`off`)。
    - 默认保持 `off`，因为 Discord 预览编辑可能会很快达到速率限制，特别是当多个机器人或网关共享同一账户或服务器流量时。
    - 为了跨频道一致性，接受 `progress`，并映射到 Discord 上的 `partial`。
    - `channels.discord.streamMode` 是旧版别名，将自动迁移。
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

    预览流仅支持文本；媒体回复将回退到正常交付。

    注意：预览流与块流是分开的。当为 Discord 显式启用块流时，OpenClaw 会跳过预览流以避免双重流传输。

  </Accordion>

  <Accordion title="历史、上下文和线程行为">
    公会历史记录上下文：

    - `channels.discord.historyLimit` 默认 `20`
    - 回退：`messages.groupChat.historyLimit`
    - `0` 禁用

    私聊历史记录控制：

    - `channels.discord.dmHistoryLimit`
    - `channels.discord.dms["<user_id>"].historyLimit`

    线程行为：

    - Discord 线程被路由为频道会话
    - 父线程元数据可用于父会话链接
    - 除非存在特定于线程的条目，否则线程配置继承父频道配置

    频道主题作为**不受信任**的上下文注入（不作为系统提示）。
    回复和引用消息上下文目前保持接收原样。
    Discord 白名单主要限制谁可以触发代理，而不是完整的补充上下文审查边界。

  </Accordion>

  <Accordion title="子代理的线程绑定会话">
    Discord 可以将线程绑定到会话目标，以便该线程中的后续消息继续路由到同一会话（包括子代理会话）。

    命令：

    - `/focus <target>` 将当前/新线程绑定到子代理/会话目标
    - `/unfocus` 移除当前线程绑定
    - `/agents` 显示活动运行和绑定状态
    - `/session idle <duration|off>` 检查/更新聚焦绑定的不活动自动取消聚焦
    - `/session max-age <duration|off>` 检查/更新聚焦绑定的硬最大年龄

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
    - `spawnAcpSessions` 必须为 true 才能为 ACP（`/acp spawn ... --thread ...` 或 `sessions_spawn({ runtime: "acp", thread: true })`）自动创建/绑定线程。
    - 如果账户禁用了线程绑定，则 `/focus` 和相关线程绑定操作不可用。

    参见 [子代理](/tools/subagents)、[ACP 代理](/tools/acp-agents) 和 [配置参考](/gateway/configuration-reference)。

  </Accordion>

  <Accordion title="持久化 ACP 频道绑定">
    对于稳定的“始终在线”ACP 工作区，请配置针对 Discord 对话的顶层类型化 ACP 绑定。

    配置路径：

    - `bindings[]` 带有 `type: "acp"` 和 `match.channel: "discord"`

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

    - `/acp spawn codex --bind here` 就地绑定当前的 Discord 频道或线程，并将未来消息路由到相同的 ACP 会话。
    - 这仍然可能意味着“启动一个新的 Codex ACP 会话”，但它本身不会创建新的 Discord 线程。现有频道保持为聊天界面。
    - Codex 仍可能在磁盘上自己的 `cwd` 或后端工作区中运行。该工作区是运行时状态，而非 Discord 线程。
    - 线程消息可以继承父频道的 ACP 绑定。
    - 在绑定的频道或线程中，`/new` 和 `/reset` 就地重置相同的 ACP 会话。
    - 临时线程绑定仍然有效，并在激活时可以覆盖目标解析。
    - 仅在 OpenClaw 需要通过 `--thread auto|here` 创建/绑定子线程时才需要 `spawnAcpSessions`。当前频道中的 `/acp spawn ... --bind here` 不需要它。

    有关绑定行为的详细信息，请参阅 [ACP 代理](/tools/acp-agents)。

  </Accordion>

  <Accordion title="反应通知">
    每个公会的反应通知模式：

    - `off`
    - `own`（默认）
    - `all`
    - `allowlist`（使用 `guilds.<id>.users`）

    反应事件转换为系统事件并附加到路由的 Discord 会话。

  </Accordion>

  <Accordion title="确认反应">
    `ackReaction` 在 OpenClaw 处理传入消息时发送确认表情符号。

    解析顺序：

    - `channels.discord.accounts.<accountId>.ackReaction`
    - `channels.discord.ackReaction`
    - `messages.ackReaction`
    - 代理身份表情符号回退（`agents.list[].identity.emoji`，否则为 "👀"）

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
    通过带有 `channels.discord.proxy` 的 HTTP(S) 代理路由 Discord 网关 WebSocket 流量和启动 REST 查找（应用程序 ID + 白名单解析）。

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
    - 仅当 `channels.discord.dangerouslyAllowNameMatching: true` 时，成员显示名称才按名称/别名匹配
    - 查找使用原始消息 ID 并受时间窗口约束
    - 如果查找失败，代理消息将被视为机器人消息并丢弃，除非 `allowBots=true`

  </Accordion>

  <Accordion title="在线状态配置">
    设置状态或活动字段时，或启用自动在线状态时，应用在线状态更新。

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

    流式传输示例：

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

    - 0: 游戏中
    - 1: 直播（需要 `activityUrl`）
    - 2: 收听中
    - 3: 观看中
    - 4: 自定义（使用活动文本作为状态状态；表情符号可选）
    - 5: 竞赛中

    自动在线状态示例（运行时健康信号）：

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

    自动在线状态将运行时可用性映射到 Discord 状态：健康 => 在线，降级或未知 => 空闲，耗尽或不可用 => 请勿打扰。可选文本覆盖：

    - `autoPresence.healthyText`
    - `autoPresence.degradedText`
    - `autoPresence.exhaustedText`（支持 `{reason}` 占位符）

  </Accordion>

  <Accordion title="Discord 中的审批">
    Discord 支持 DM 中的基于按钮的审批处理，并可选择在源频道发布审批提示。

    配置路径：

    - `channels.discord.execApprovals.enabled`
    - `channels.discord.execApprovals.approvers`（可选；在可能时回退到 `commands.ownerAllowFrom`）
    - `channels.discord.execApprovals.target`（`dm` | `channel` | `both`，默认：`dm`）
    - `agentFilter`，`sessionFilter`，`cleanupAfterResolve`

    当 `enabled` 未设置或 `"auto"` 且至少可以解析一名审批人（来自 `execApprovals.approvers` 或 `commands.ownerAllowFrom`）时，Discord 会自动启用原生执行审批。Discord 不会从频道 `allowFrom`、旧版 `dm.allowFrom` 或直接消息 `defaultTo` 推断执行审批人。设置 `enabled: false` 以明确禁用 Discord 作为原生审批客户端。

当 `target` 为 `channel` 或 `both` 时，批准提示在频道中可见。只有已解析的审批人可以使用按钮；其他用户会收到临时拒绝消息。批准提示包含命令文本，因此仅在受信任的频道中启用频道交付。如果无法从会话密钥派生频道 ID，OpenClaw 将回退到 DM 交付。

    Discord 还会渲染其他聊天频道使用的共享批准按钮。原生 Discord 适配器主要添加了审批人 DM 路由和频道扇出功能。
    当这些按钮存在时，它们是主要的批准用户体验；仅当工具结果显示聊天批准不可用或手动批准是唯一路径时，OpenClaw 才应包含手动 `/approve` 命令。

    此处理程序的网关认证使用与其他网关客户端相同的共享凭据解析合约：

    - 优先环境的本地认证 (`OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD` 然后 `gateway.auth.*`)
    - 在本地模式下，仅当 `gateway.auth.*` 未设置时，`gateway.remote.*` 才能用作回退；已配置但未解析的本地 SecretRefs 将失败并关闭
    - 如适用，通过 `gateway.remote.*` 支持远程模式
    - URL 覆盖是安全的：CLI 覆盖不会重用隐式凭据，环境覆盖仅使用环境凭据

    批准解析行为：

    - 以 `plugin:` 开头的 ID 通过 `plugin.approval.resolve` 解析。
    - 其他 ID 通过 `exec.approval.resolve` 解析。
    - Discord 此处不执行额外的 exec-to-plugin 回退跳转；ID 前缀决定调用哪个网关方法。

    Exec 批准默认在 30 分钟后过期。如果批准因未知的批准 ID 而失败，请验证审批人解析、功能启用情况，以及交付的批准 ID 类型是否与待处理请求匹配。

    相关文档：[Exec approvals](/tools/exec-approvals)

  </Accordion>
</AccordionGroup>

## 工具和动作门控

Discord 消息操作包括消息发送、频道管理、审核、在线状态和元数据操作。

核心示例：

- 消息：`sendMessage`, `readMessages`, `editMessage`, `deleteMessage`, `threadReply`
- 反应：`react`, `reactions`, `emojiList`
- 审核：`timeout`, `kick`, `ban`
- 在线状态：`setPresence`

动作门控位于 `channels.discord.actions.*` 下。

默认门控行为：

| 操作组                                                                                                                                                             | 默认   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| 反应、消息、线程、置顶、投票、搜索、成员信息、角色信息、频道信息、频道、语音状态、事件、贴纸、表情上传、贴纸上传、权限 | 启用   |
| 角色                                                                                                                                                                    | 禁用   |
| 审核                                                                                                                                                               | 禁用   |
| 在线状态                                                                                                                                                                 | 禁用   |

## Components v2 界面

OpenClaw 使用 Discord 组件 v2 进行 exec 批准和跨上下文标记。Discord 消息操作也可以接受 `components` 用于自定义 UI（高级；需要通过 discord 工具构建组件负载），而遗留的 `embeds` 仍然可用但不推荐。

- `channels.discord.ui.components.accentColor` 设置 Discord 组件容器使用的强调色（十六进制）。
- 使用 `channels.discord.accounts.<id>.ui.components.accentColor` 按账户设置。
- 当存在组件 v2 时，`embeds` 将被忽略。

示例：

```json5
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
```

## 语音频道

OpenClaw 可以加入 Discord 语音频道进行实时、连续的对话。这与语音消息附件是分开的。

要求：

- 启用原生命令 (`commands.native` 或 `channels.discord.commands.native`)。
- 配置 `channels.discord.voice`。
- 机器人需要在目标语音频道中具有 Connect + Speak 权限。

使用仅限 Discord 的原生命令 `/vc join|leave|status` 来控制会话。该命令使用账户默认代理，并遵循与其他 Discord 命令相同的白名单和组策略规则。

自动加入示例：

```json5
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
```

注意：

- `voice.tts` 仅针对语音播放覆盖 `messages.tts`。
- 语音转录轮次从 Discord `allowFrom`（或 `dm.allowFrom`）派生所有者状态；非所有者说话者无法访问仅限所有者的工具（例如 `gateway` 和 `cron`）。
- 语音默认启用；设置 `channels.discord.voice.enabled=false` 可禁用它。
- `voice.daveEncryption` 和 `voice.decryptionFailureTolerance` 透传至 `@discordjs/voice` 加入选项。
- 如果未设置，`@discordjs/voice` 默认为 `daveEncryption=true` 和 `decryptionFailureTolerance=24`。
- OpenClaw 还会监控接收解密失败，并在短时间内重复失败后通过离开/重新加入语音频道自动恢复。
- 如果接收日志反复显示 `DecryptionFailed(UnencryptedWhenPassthroughDisabled)`，这可能是上游 `@discordjs/voice` 接收错误，跟踪于 [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419)。

## 语音消息

Discord 语音消息显示波形预览，需要 OGG/Opus 音频及元数据。OpenClaw 自动生成波形，但需要在网关主机上提供 `ffmpeg` 和 `ffprobe` 来检查和转换音频文件。

要求和限制：

- 提供 **本地文件路径**（URL 将被拒绝）。
- 省略文本内容（Discord 不允许在同一负载中包含文本 + 语音消息）。
- 接受任何音频格式；OpenClaw 在需要时转换为 OGG/Opus。

示例：

```bash
message(action="send", channel="discord", target="channel:123", path="/path/to/audio.mp3", asVoice=true)
```

## 故障排除

<AccordionGroup>
  <Accordion title="使用了不允许的意图或机器人看不到服务器消息">

    - 启用 Message Content Intent
    - 当您依赖用户/成员解析时，启用 Server Members Intent
    - 更改意图后重启网关

  </Accordion>

  <Accordion title="服务器消息意外被阻止">

    - 验证 `groupPolicy`
    - 验证 `channels.discord.guilds` 下的服务器白名单
    - 如果存在服务器 `channels` 映射，则仅允许列出的频道
    - 验证 `requireMention` 行为和提及模式

    有用的检查：

```bash
openclaw doctor
openclaw channels status --probe
openclaw logs --follow
```

  </Accordion>

  <Accordion title="Require mention 为 false 但仍被阻止">
    常见原因：

    - `groupPolicy="allowlist"` 没有匹配的服务器/频道白名单
    - `requireMention` 配置位置错误（必须在 `channels.discord.guilds` 下或频道条目中）
    - 发送者被服务器/频道 `users` 白名单阻止

  </Accordion>

  <Accordion title="长时间运行的处理器超时或重复回复">

    典型日志：

    - `Listener DiscordMessageListener timed out after 30000ms for event MESSAGE_CREATE`
    - `Slow listener detected ...`
    - `discord inbound worker timed out after ...`

    监听器预算参数：

    - 单账户：`channels.discord.eventQueue.listenerTimeout`
    - 多账户：`channels.discord.accounts.<accountId>.eventQueue.listenerTimeout`

    工作线程运行超时参数：

    - 单账户：`channels.discord.inboundWorker.runTimeoutMs`
    - 多账户：`channels.discord.accounts.<accountId>.inboundWorker.runTimeoutMs`
    - 默认：`1800000`（30 分钟）；设置 `0` 以禁用

    推荐基线：

```json5
{
  channels: {
    discord: {
      accounts: {
        default: {
          eventQueue: {
            listenerTimeout: 120000,
          },
          inboundWorker: {
            runTimeoutMs: 1800000,
          },
        },
      },
    },
  },
}
```

    使用 `eventQueue.listenerTimeout` 进行慢速监听器设置，仅当您希望为排队代理轮次设置单独的安全阀时才使用 `inboundWorker.runTimeoutMs`。

  </Accordion>

  <Accordion title="权限审计不匹配">
    `channels status --probe` 权限检查仅适用于数字频道 ID。

    如果您使用 slug 键，运行时匹配仍然有效，但探针无法完全验证权限。

  </Accordion>

  <Accordion title="DM 和配对问题">

    - DM 已禁用：`channels.discord.dm.enabled=false`
    - DM 策略已禁用：`channels.discord.dmPolicy="disabled"`（旧版：`channels.discord.dm.policy`）
    - 在 `pairing` 模式下等待配对批准

  </Accordion>

  <Accordion title="机器人到机器人的循环">
    默认情况下，机器人创建的消息会被忽略。

    如果您设置了 `channels.discord.allowBots=true`，请使用严格的提及和白名单规则以避免循环行为。
    建议优先使用 `channels.discord.allowBots="mentions"` 以仅接受提及机器人的机器人消息。

  </Accordion>

  <Accordion title="语音 STT 因 DecryptionFailed(...) 而中断">

- 保持 OpenClaw 为当前版本 (`openclaw update`)，以确保存在 Discord 语音接收恢复逻辑
    - 确认 `channels.discord.voice.daveEncryption=true`（默认）
    - 从 `channels.discord.voice.decryptionFailureTolerance=24`（上游默认值）开始，仅在需要时进行调整
    - 监控日志中的以下内容：
      - `discord voice: DAVE decrypt failures detected`
      - `discord voice: repeated decrypt failures; attempting rejoin`
    - 如果自动重连后故障仍然存在，请收集日志并与 [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419) 进行比较

  </Accordion>
</AccordionGroup>

## 配置参考指引

主要参考：

- [配置参考 - Discord](/gateway/configuration-reference#discord)

关键 Discord 字段：

- startup/auth: `enabled`, `token`, `accounts.*`, `allowBots`
- policy: `groupPolicy`, `dm.*`, `guilds.*`, `guilds.*.channels.*`
- command: `commands.native`, `commands.useAccessGroups`, `configWrites`, `slashCommand.*`
- event queue: `eventQueue.listenerTimeout` (listener budget), `eventQueue.maxQueueSize`, `eventQueue.maxConcurrency`
- inbound worker: `inboundWorker.runTimeoutMs`
- reply/history: `replyToMode`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
- delivery: `textChunkLimit`, `chunkMode`, `maxLinesPerMessage`
- streaming: `streaming`（旧版别名：`streamMode`）, `draftChunk`, `blockStreaming`, `blockStreamingCoalesce`
- media/retry: `mediaMaxMb`, `retry`
  - `mediaMaxMb` 限制出站 Discord 上传（默认：`8MB`）
- actions: `actions.*`
- presence: `activity`, `status`, `activityType`, `activityUrl`
- UI: `ui.components.accentColor`
- features: `threadBindings`, 顶层 `bindings[]` (`type: "acp"`), `pluralkit`, `execApprovals`, `intents`, `agentComponents`, `heartbeat`, `responsePrefix`

## 安全与运维

- 将机器人令牌视为机密（在受监管环境中首选 `DISCORD_BOT_TOKEN`）。
- 授予最小权限的 Discord 权限。
- 如果命令部署/状态过时，请重启网关并使用 `openclaw channels status --probe` 重新检查。

## 相关

- [配对](/channels/pairing)
- [群组](/channels/groups)
- [频道路由](/channels/channel-routing)
- [安全](/gateway/security)
- [多智能体路由](/concepts/multi-agent)
- [故障排除](/channels/troubleshooting)
- [斜杠命令](/tools/slash-commands)