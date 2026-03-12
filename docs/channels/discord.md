---
summary: "Discord bot support status, capabilities, and configuration"
read_when:
  - Working on Discord channel features
title: "Discord"
---
# Discord（机器人 API）

状态：已准备好通过官方 Discord 网关接收私信（DM）和服务器频道消息。

<CardGroup cols={3}>
  <Card title="配对" icon="link" href="/channels/pairing">
    Discord 私信默认启用配对模式。
  </Card>
  <Card title="斜杠命令" icon="terminal" href="/tools/slash-commands">
    原生命令行为与命令目录。
  </Card>
  <Card title="频道故障排查" icon="wrench" href="/channels/troubleshooting">
    跨频道诊断与修复流程。
  </Card>
</CardGroup>

## 快速设置

您需要创建一个带机器人的新应用，将该机器人添加到您的服务器中，并将其与 OpenClaw 配对。我们建议将您的机器人添加到您自己的私人服务器中。如果您尚无私人服务器，请先[创建一个](https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server)（选择 **Create My Own > For me and my friends**）。

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

## 推荐：设置服务器工作区

当私信功能正常运行后，您可以将 Discord 服务器配置为完整工作区，使每个频道拥有独立的智能体会话及专属上下文。此配置适用于仅包含您和您的机器人的私人服务器。

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

现在，在您的 Discord 服务器中创建若干频道并开始聊天。您的智能体可识别频道名称，且每个频道均拥有隔离的会话——因此您可以设置 `#coding`、`#home`、`#research`，或任何符合您工作流的配置。

## 运行时模型

- 网关负责管理 Discord 连接。
- 回复路由是确定性的：Discord 入站消息的回复将原路返回至 Discord。
- 默认情况下（`session.dmScope=main`），直接聊天共享智能体主会话（`agent:main:main`）。
- 服务器频道使用隔离的会话密钥（`agent:<agentId>:discord:channel:<channelId>`）。
- 群组私信默认被忽略（`channels.discord.dm.groupEnabled=false`）。
- 原生斜杠命令在隔离的命令会话（`agent:<agentId>:discord:slash:<userId>`）中运行，但仍会将 `CommandTargetSessionKey` 传递至目标对话会话。

## 论坛频道

Discord 论坛频道与媒体频道仅接受线程（thread）形式的帖子。OpenClaw 支持两种创建方式：

- 向论坛父频道（`channel:<forumId>`）发送消息，自动创建线程。线程标题取自您消息中首个非空行。
- 使用 `openclaw message thread create` 直接创建线程。请勿为论坛频道传入 `--message-id`。

示例：向论坛父频道发送消息以创建线程

```bash
openclaw message send --channel discord --target channel:<forumId> \
  --message "Topic title\nBody of the post"
```

示例：显式创建论坛线程

```bash
openclaw message thread create --channel discord --target channel:<forumId> \
  --thread-name "Topic title" --message "Body of the post"
```

论坛父频道不支持 Discord 组件（components）。如需使用组件，请直接向线程本身（`channel:<threadId>`）发送。

## 交互式组件

OpenClaw 支持为智能体消息使用 Discord v2 组件容器。请使用消息工具并携带 `components` 有效载荷。交互结果将作为常规入站消息路由回智能体，并遵循现有的 Discord `replyToMode` 设置。

支持的组件类型：

- `text`、`section`、`separator`、`actions`、`media-gallery`、`file`
- 操作行（Action Row）最多支持 5 个按钮，或单个选择菜单
- 支持的选择类型：`string`、`user`、`role`、`mentionable`、`channel`

默认情况下，组件为单次使用。设置 ``components.reusable=true`` 可允许多次使用按钮、下拉选择框和表单，直至其过期。

若要限制可点击按钮的用户范围，请在该按钮上设置 ``allowedUsers``（支持 Discord 用户 ID、用户标签或 ``*``）。配置生效后，不匹配的用户将收到临时性的拒绝提示。

``/model`` 和 ``/models`` 斜杠命令将打开一个交互式模型选择器，其中包含提供方与模型的下拉菜单，以及一个“提交”步骤。该选择器的回复为临时性消息，且仅调用者本人可使用。

文件附件：

- ``file`` 块必须指向一个附件引用（``attachment://<filename>``）；
- 通过 ``media`` / ``path`` / ``filePath`` 提供单个附件；多个附件请使用 ``media-gallery``；
- 使用 ``filename`` 可在上传名称需与附件引用保持一致时覆盖默认上传名称。

模态表单（Modal forms）：

- 添加 ``components.modal``，最多支持 5 个字段；
- 字段类型包括：``text``、``checkbox``、``radio``、``select``、``role-select``、``user-select``；
- OpenClaw 将自动添加触发按钮。

示例：

````json5
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
````

## 访问控制与路由

`<Tabs>
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
</Tabs>`

### 基于角色的智能体路由

使用 ``bindings[].match.roles`` 可根据角色 ID 将 Discord 服务器成员路由至不同智能体。基于角色的绑定仅接受角色 ID，并在对等绑定（peer）或父-对等绑定（parent-peer）之后、仅限服务器绑定（guild-only）之前进行评估。若某绑定同时设置了其他匹配字段（例如 ``peer`` + ``guildId`` + ``roles``），则所有已配置字段均须满足匹配条件。

````json5
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
````

## 开发者门户设置

`<AccordionGroup>
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
</AccordionGroup>`

## 原生命令与命令鉴权

- ``commands.native`` 默认为 ``"auto"``，且已在 Discord 中启用；
- 按频道覆盖：``channels.discord.commands.native``；
- ``commands.native=false`` 显式清除此前已注册的所有 Discord 原生命令；
- 原生命令鉴权机制与常规消息处理所使用的 Discord 白名单/策略完全一致；
- 即使未获授权的用户在 Discord UI 中仍可能看到相关命令，但执行时仍将强制执行 OpenClaw 鉴权，并返回“未授权”响应。

有关命令目录及行为说明，请参阅 [斜杠命令](/tools/slash-commands)。

默认斜杠命令设置：

- ``ephemeral: true``

## 功能详情

<AccordionGroup>
  <Accordion title="回复标签与原生回复">
    Discord 支持在智能体输出中使用回复标签：

    - ``[[reply_to_current]]``
    - ``[[reply_to:<id>]]``

    此行为由 ``channels.discord.replyToMode`` 控制：

    - ``off``（默认）
    - ``first``
    - ``all``

    注意：``off`` 将禁用隐式回复线程功能；显式的 ``[[reply_to_*]]`` 标签仍会被识别并生效。

    消息 ID 将在上下文/历史记录中暴露，以便智能体可精准定位特定消息。

  </Accordion>

  <Accordion title="实时流式预览">
    OpenClaw 可通过发送一条临时消息并在文本逐步到达时持续编辑该消息，实现草稿回复的流式预览。

    - ``channels.discord.streaming`` 控制预览流式传输（可选值：``off`` | ``partial`` | ``block`` | ``progress``，默认为 ``off``）；
    - ``progress`` 为保障跨频道一致性而保留，其在 Discord 上映射为 ``partial``；
    - ``channels.discord.streamMode`` 是一个遗留别名，系统将自动迁移；
    - ``partial`` 在 token 到达时持续编辑单条预览消息；
    - ``block`` 发送按草稿大小分块的内容（可使用 ``draftChunk`` 调整分块大小与断点）。

    示例：

````json5
{
  channels: {
    discord: {
      streaming: "partial",
    },
  },
}
````

    ``block`` 模式下的分块默认值（上限为 ``channels.discord.textChunkLimit``）：

````json5
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
````

    预览流式传输仅支持纯文本；含媒体内容的回复将回退至常规交付方式。

    注意：预览流式传输与区块流式传输（block streaming）相互独立。当明确为 Discord 启用区块流式传输时，OpenClaw 将跳过预览流式传输，以避免重复流式传输。

  </Accordion>

  <Accordion title="历史记录、上下文与线程行为">
    服务器（Guild）历史记录上下文：

    - ``channels.discord.historyLimit`` 默认为 ``20``
    - 回退方案：``messages.groupChat.historyLimit``
    - ``0`` 将禁用该功能

    私信（DM）历史记录控制：

    - ``channels.discord.dmHistoryLimit``
    - ``channels.discord.dms["<user_id>"].historyLimit``

线程行为：

    - Discord 线程被路由为频道会话  
    - 父线程元数据可用于父会话关联  
    - 线程配置继承父频道配置，除非存在特定于该线程的配置项  

    频道主题作为**不可信**上下文注入（而非系统提示词）。

  </Accordion>

  <Accordion title="面向子代理的线程绑定会话">
    Discord 可将线程绑定到会话目标，使该线程中的后续消息持续路由至同一会话（包括子代理会话）。

    命令：

    - `/focus <target>` 将当前/新建线程绑定至子代理/会话目标  
    - `/unfocus` 移除当前线程绑定  
    - `/agents` 显示活跃运行任务及绑定状态  
    - `/session idle <duration|off>` 检查/更新聚焦绑定的非活动自动失焦设置  
    - `/session max-age <duration|off>` 检查/更新聚焦绑定的硬性最大存活时长  

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

    注意事项：

    - `session.threadBindings.*` 设置全局默认值。  
    - `channels.discord.threadBindings.*` 覆盖 Discord 默认行为。  
    - `spawnSubagentSessions` 必须为 true，才能为 `sessions_spawn({ thread: true })` 自动创建/绑定线程。  
    - `spawnAcpSessions` 必须为 true，才能为 ACP（`/acp spawn ... --thread ...` 或 `sessions_spawn({ runtime: "acp", thread: true })`）自动创建/绑定线程。  
    - 若某账户已禁用线程绑定，则 `/focus` 及相关线程绑定操作不可用。

    参见 [子代理](/tools/subagents)、[ACP 代理](/tools/acp-agents) 和 [配置参考](/gateway/configuration-reference)。

  </Accordion>

  <Accordion title="持久化 ACP 频道绑定">
    对于稳定的“常驻”ACP 工作区，请配置顶层类型化 ACP 绑定，使其指向 Discord 对话。

    配置路径：

    - `bindings[]`，配合 `type: "acp"` 和 `match.channel: "discord"`

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

    注意事项：

    - 线程消息可继承父频道的 ACP 绑定。  
    - 在已绑定的频道或线程中，`/new` 和 `/reset` 将就地重置同一 ACP 会话。  
    - 临时线程绑定仍有效，并可在激活期间覆盖目标解析逻辑。

    有关绑定行为详情，请参阅 [ACP 代理](/tools/acp-agents)。

  </Accordion>

  <Accordion title="反应通知">
    按服务器划分的反应通知模式：

    - `off`  
    - `own`（默认）  
    - `all`  
    - `allowlist`（使用 `guilds.<id>.users`）

    反应事件将被转换为系统事件，并附加至所路由的 Discord 会话。

  </Accordion>

  <Accordion title="确认反应">
    `ackReaction` 在 OpenClaw 处理入站消息期间发送确认表情符号。

    解析顺序：

    - `channels.discord.accounts.<accountId>.ackReaction`  
    - `channels.discord.ackReaction`  
    - `messages.ackReaction`  
    - 代理身份表情符号回退（`agents.list[].identity.emoji`，否则为 "👀"）

    注意事项：

    - Discord 支持 Unicode 表情符号或自定义表情符号名称。  
    - 使用 `""` 可在频道或账户级别禁用该反应。

  </Accordion>

  <Accordion title="配置写入">
    默认启用由频道发起的配置写入功能。

    此设置影响 `/config set|unset` 流程（当启用命令功能时）。

    禁用方式：

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
    通过 HTTP(S) 代理（需配置 `channels.discord.proxy`）路由 Discord 网关 WebSocket 流量及启动阶段的 REST 查询（应用 ID + 白名单解析）。

```json5
{
  channels: {
    discord: {
      proxy: "http://proxy.example:8080",
    },
  },
}
```

    每账户覆盖配置：

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
    启用 PluralKit 解析，以将代理消息映射至系统成员身份：

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

    注意事项：

    - 白名单可使用 `pk:<memberId>`  
    - 成员显示名称仅在 `channels.discord.dangerouslyAllowNameMatching: true` 时按名称/短标识符匹配  
    - 查找使用原始消息 ID，且受时间窗口限制  
    - 若查找失败，代理消息将被视为机器人消息并被丢弃，除非启用 `allowBots=true`

  </Accordion>

  <Accordion title="在线状态配置">
    当您设置状态或活动字段，或启用自动在线状态时，将应用在线状态更新。

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

    活动示例（自定义状态为默认活动类型）：

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

    直播示例：

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

    - 0：正在游玩  
    - 1：直播（需配置 `activityUrl`）  
    - 2：正在收听  
    - 3：正在观看  
    - 4：自定义（使用活动文本作为状态内容；表情符号为可选）  
    - 5：正在竞技  

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

    自动在线状态将运行时可用性映射至 Discord 状态：健康 => 在线，降级或未知 => 空闲，耗尽或不可用 => 忙碌。可选文本覆盖项：

    - `autoPresence.healthyText`  
    - `autoPresence.degradedText`  
    - `autoPresence.exhaustedText`（支持 `{reason}` 占位符）

  </Accordion>

  <Accordion title="Discord 中的执行审批">
    Discord 支持在私信中基于按钮的执行审批，并可选择在原始频道中发布审批提示。

    配置路径：

    - `channels.discord.execApprovals.enabled`  
    - `channels.discord.execApprovals.approvers`  
    - `channels.discord.execApprovals.target`（`dm` | `channel` | `both`，默认：`dm`）  
    - `agentFilter`、`sessionFilter`、`cleanupAfterResolve`

    当 `target` 为 `channel` 或 `both` 时，审批提示将在频道中可见。仅已配置的审批人可使用按钮；其他用户将收到临时性拒绝提示。审批提示包含命令文本，因此请仅在可信频道中启用频道投递。若无法从会话密钥推导出频道 ID，OpenClaw 将回退至私信投递。

    此处理器的网关认证采用与其他网关客户端相同的共享凭据解析契约：

    - 优先使用环境变量的本地认证（先检查 `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`，再检查 `gateway.auth.*`）  
    - 在本地模式下，当 `gateway.auth.*` 未设置时，可使用 `gateway.remote.*` 作为回退方案  
    - 在适用情况下，可通过 `gateway.remote.*` 提供远程模式支持  
    - URL 覆盖是安全的：CLI 覆盖不会复用隐式凭据，而环境变量覆盖仅使用环境变量凭据  

    若审批因未知审批 ID 失败，请验证审批人列表及功能启用状态。

    相关文档：[执行审批](/tools/exec-approvals)

  </Accordion>
</AccordionGroup>

## 工具与动作门控

Discord 消息动作包括消息收发、频道管理、内容审核、在线状态及元数据操作。

核心示例：

- 消息收发：`sendMessage`、`readMessages`、`editMessage`、`deleteMessage`、`threadReply`  
- 反应：`react`、`reactions`、`emojiList`  
- 内容审核：`timeout`、`kick`、`ban`  
- 在线状态：`setPresence`

动作门控位于 `channels.discord.actions.*` 下。

默认门控行为：

| 操作组                                                                                                                                                             | 默认值   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| reactions（表情反应）、messages（消息）、threads（主题）、pins（置顶）、polls（投票）、search（搜索）、memberInfo（成员信息）、roleInfo（角色信息）、channelInfo（频道信息）、channels（频道列表）、voiceStatus（语音状态）、events（事件）、stickers（贴纸）、emojiUploads（表情上传）、stickerUploads（贴纸上传）、permissions（权限） | 启用     |
| roles（角色）                                                                                                                                                                    | 禁用     |
| moderation（审核）                                                                                                                                                               | 禁用     |
| presence（在线状态）                                                                                                                                                                 | 禁用     |

## 组件 v2 用户界面

OpenClaw 使用 Discord 组件 v2 实现执行审批和跨上下文标记。Discord 消息操作也可接受 `components` 以实现自定义 UI（高级功能；需配置 Carbon 组件实例），而旧版 `embeds` 仍可用，但不推荐使用。

- `channels.discord.ui.components.accentColor` 设置 Discord 组件容器所用的强调色（十六进制格式）。
- 使用 `channels.discord.accounts.<id>.ui.components.accentColor` 按账号单独设置。
- 当启用组件 v2 时，`embeds` 将被忽略。

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

OpenClaw 可加入 Discord 语音频道，以支持实时、持续的对话。此功能与语音消息附件相互独立。

前提条件：

- 启用原生命令（`commands.native` 或 `channels.discord.commands.native`）。
- 配置 `channels.discord.voice`。
- 机器人需在目标语音频道中拥有 Connect（连接）和 Speak（发言）权限。

使用仅限 Discord 的原生命令 `/vc join|leave|status` 控制会话。该命令使用账号默认代理，并遵循与其他 Discord 命令相同的白名单及分组策略规则。

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

注意事项：

- `voice.tts` 仅对语音播放覆盖 `messages.tts`。
- 语音转录结果的所有者身份源自 Discord 的 `allowFrom`（或 `dm.allowFrom`）；非所有者发言者无法访问仅限所有者的工具（例如 `gateway` 和 `cron`）。
- 语音功能默认启用；设置 `channels.discord.voice.enabled=false` 可将其禁用。
- `voice.daveEncryption` 和 `voice.decryptionFailureTolerance` 将透传至 `@discordjs/voice` 的加入选项。
- 若未设置，`@discordjs/voice` 的默认值为 `daveEncryption=true` 和 `decryptionFailureTolerance=24`。
- OpenClaw 还会监控接收解密失败情况，并在短时间内连续失败时，通过主动退出并重新加入语音频道实现自动恢复。
- 若接收日志反复显示 `DecryptionFailed(UnencryptedWhenPassthroughDisabled)`，这可能是上游 `@discordjs/voice` 接收 Bug 所致，该问题已在 [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419) 中追踪。

## 语音消息

Discord 语音消息显示波形预览图，且要求音频格式为 OGG/Opus 并附带元数据。OpenClaw 自动生成波形图，但网关主机上必须安装并可用 `ffmpeg` 和 `ffprobe`，以便检查和转换音频文件。

要求与限制：

- 提供 **本地文件路径**（URL 将被拒绝）。
- 不得包含文本内容（Discord 不允许在同一载荷中同时发送文本与语音消息）。
- 支持任意音频格式；OpenClaw 在必要时自动转换为 OGG/Opus。

示例：

```bash
message(action="send", channel="discord", target="channel:123", path="/path/to/audio.mp3", asVoice=true)
```

## 故障排查

<AccordionGroup>
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
</AccordionGroup>

## 配置参考指引

主要参考文档：

- [配置参考 - Discord](/gateway/configuration-reference#discord)

高相关性 Discord 配置字段：

- 启动/认证：`enabled`、`token`、`accounts.*`、`allowBots`
- 策略：`groupPolicy`、`dm.*`、`guilds.*`、`guilds.*.channels.*`
- 命令：`commands.native`、`commands.useAccessGroups`、`configWrites`、`slashCommand.*`
- 事件队列：`eventQueue.listenerTimeout`（监听器配额）、`eventQueue.maxQueueSize`、`eventQueue.maxConcurrency`
- 入站工作线程：`inboundWorker.runTimeoutMs`
- 回复/历史记录：`replyToMode`、`historyLimit`、`dmHistoryLimit`、`dms.*.historyLimit`
- 投递：`textChunkLimit`、`chunkMode`、`maxLinesPerMessage`
- 流式传输：`streaming`（旧版别名：`streamMode`）、`draftChunk`、`blockStreaming`、`blockStreamingCoalesce`
- 媒体/重试：`mediaMaxMb`、`retry`
  - `mediaMaxMb` 限制外发 Discord 上传大小（默认值：`8MB`）
- 操作：`actions.*`
- 在线状态：`activity`、`status`、`activityType`、`activityUrl`
- 用户界面：`ui.components.accentColor`
- 功能特性：`threadBindings`、顶层 `bindings[]`（`type: "acp"`）、`pluralkit`、`execApprovals`、`intents`、`agentComponents`、`heartbeat`、`responsePrefix`

## 安全与运维

- 将机器人令牌视为敏感信息（在受监管环境中首选使用 `DISCORD_BOT_TOKEN`）。
- 仅授予最小必要权限的 Discord 权限。
- 若命令部署/状态已过期，请重启网关，并使用 `openclaw channels status --probe` 重新验证。

## 相关文档

- [配对](/channels/pairing)
- [频道路由](/channels/channel-routing)
- [多代理路由](/concepts/multi-agent)
- [故障排查](/channels/troubleshooting)
- [斜杠命令](/tools/slash-commands)