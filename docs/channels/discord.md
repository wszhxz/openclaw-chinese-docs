---
summary: "Discord bot support status, capabilities, and configuration"
read_when:
  - Working on Discord channel features
title: "Discord"
---
# Discord (Bot API)

状态：通过官方Discord网关已准备好处理私信和服务器频道。

<CardGroup cols={3}>
  <Card title="配对" icon="link" href="/channels/pairing">
    Discord私信默认为配对模式。
  </Card>
  <Card title="斜杠命令" icon="terminal" href="/tools/slash-commands">
    原生命令行为和命令目录。
  </Card>
  <Card title="频道故障排除" icon="wrench" href="/channels/troubleshooting">
    跨频道诊断和修复流程。
  </Card>
</CardGroup>

## 快速设置

您需要创建一个带有机器人的新应用程序，将机器人添加到您的服务器，并将其与OpenClaw配对。我们建议将机器人添加到您自己的私人服务器。如果您还没有，请先[创建一个](https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server)（选择 **Create My Own > For me and my friends**）。

<Steps>
  <Step title="创建Discord应用程序和机器人">
    访问[Discord开发者门户](https://discord.com/developers/applications)，点击**New Application**。命名为类似“OpenClaw”的名称。

    在侧边栏点击**Bot**。将**Username**设置为您为OpenClaw代理选择的名称。

  </Step>

  <Step title="启用特权意图">
    仍在**Bot**页面上，向下滚动到**Privileged Gateway Intents**并启用：

    - **Message Content Intent**（必需）
    - **Server Members Intent**（推荐；角色白名单和名称到ID匹配所需）
    - **Presence Intent**（可选；仅在需要状态更新时需要）

  </Step>

  <Step title="复制您的机器人令牌">
    向上滚动到**Bot**页面并点击**Reset Token**。

    <Note>
    Despite the name, this generates your first token — nothing is being "reset."
    </Note>

    复制令牌并保存它。这是您的**Bot Token**，您稍后会用到它。

  </Step>

  <Step title="生成邀请URL并将机器人添加到您的服务器">
    点击侧边栏上的**OAuth2**。您将生成一个具有正确权限的邀请URL以将机器人添加到您的服务器。

    向下滚动到**OAuth2 URL Generator**并启用：

    - `bot`
    - `applications.commands`

    下方会出现一个**Bot Permissions**部分。启用：

    - 查看频道
    - 发送消息
    - 读取消息历史记录
    - 嵌入链接
    - 附加文件
    - 添加反应（可选）

    复制底部生成的URL，将其粘贴到浏览器中，选择您的服务器，然后点击**Continue**以连接。现在您应该能在Discord服务器中看到您的机器人。

  </Step>

  <Step title="启用开发者模式并收集您的ID">
    回到Discord应用，您需要启用开发者模式以便复制内部ID。

    1. 点击**用户设置**（您头像旁边的齿轮图标）→ **高级** → 切换打开**开发者模式**
    2. 右键点击侧边栏中的**服务器图标** → **复制服务器ID**
    3. 右键点击**您自己的头像** → **复制用户ID**

保存您的 **Server ID** 和 **User ID** 与您的 Bot Token 一起 — 您将在下一步中将这三者发送给 OpenClaw。

  </Step>

  <Step title="允许来自服务器成员的私信">
    为了使配对功能正常工作，Discord 需要允许您的机器人向您发送私信。右键点击您的 **服务器图标** → **隐私设置** → 打开 **直接消息**。

    这将允许服务器成员（包括机器人）向您发送私信。如果您打算使用 Discord 私信与 OpenClaw，建议保持此选项开启。如果您仅计划使用服务器频道，可以在配对后禁用私信。

  </Step>

  <Step title="步骤 0: 安全设置您的机器人令牌（勿在聊天中发送）">
    您的 Discord 机器人令牌是一个机密信息（类似于密码）。在向代理发送消息之前，请在运行 OpenClaw 的机器上设置它。

```bash
openclaw config set channels.discord.token '"YOUR_BOT_TOKEN"' --json
openclaw config set channels.discord.enabled true --json
openclaw gateway
```

    如果 OpenClaw 已经作为后台服务运行，请改用 `openclaw gateway restart`。

  </Step>

  <Step title="配置 OpenClaw 并进行配对">

    <Tabs>
      <Tab title="Ask your agent">
        Chat with your OpenClaw agent on any existing channel (e.g. Telegram) and tell it. If Discord is your first channel, use the CLI / config tab instead.

        > "I already set my Discord bot token in config. Please finish Discord setup with User ID __CODE_BLOCK_2__ and Server ID __CODE_BLOCK_3__."
      </Tab>
      <Tab title="CLI / config">
        If you prefer file-based config, set:

__CODE_BLOCK_4__

        Env fallback for the default account:

__CODE_BLOCK_5__

      </Tab>
    </Tabs>

  </Step>

  <Step title="批准首次私信配对">
    等待网关运行后，在 Discord 中向您的机器人发送私信。它将回复一个配对码。

    <Tabs>
      <Tab title="Ask your agent">
        Send the pairing code to your agent on your existing channel:

        > "Approve this Discord pairing code: __CODE_BLOCK_6__"
      </Tab>
      <Tab title="CLI">

__CODE_BLOCK_7__

      </Tab>
    </Tabs>

    配对码在 1 小时后过期。

    您现在应该能够通过 Discord 私信与您的代理聊天。

  </Step>
</Steps>

<Note>
Token resolution is account-aware. Config token values win over env fallback. __CODE_BLOCK_8__ is only used for the default account.
</Note>

## 建议：设置一个服务器工作区

一旦私信功能正常工作，您可以将您的 Discord 服务器设置为一个完整的工作区，其中每个频道都有自己的代理会话和自己的上下文。这对于只有您和机器人的私人服务器来说是推荐的。

<Steps>
  <Step title="将您的服务器添加到服务器白名单">
    这将使您的代理能够在服务器的任何频道中响应，而不仅仅是私信。

<Tabs>
      <Tab title="Ask your agent">
        > "Add my Discord Server ID __CODE_BLOCK_0__ to the guild allowlist"
      </Tab>
      <Tab title="Config">

__CODE_BLOCK_1__

      </Tab>
    </Tabs>

  </Step>

  <Step title="允许无@提及的响应">
    默认情况下，您的代理仅在被@提及时才会在服务器频道中响应。对于私人服务器，您可能希望它对每条消息都作出响应。

    <Tabs>
      <Tab title="Ask your agent">
        > "Allow my agent to respond on this server without having to be @mentioned"
      </Tab>
      <Tab title="Config">
        Set __CODE_BLOCK_2__ in your guild config:

__CODE_BLOCK_3__

      </Tab>
    </Tabs>

  </Step>

  <Step title="规划服务器频道中的内存">
    默认情况下，长期记忆（MEMORY.md）仅在直接消息会话中加载。服务器频道不会自动加载MEMORY.md。

    <Tabs>
      <Tab title="Ask your agent">
        > "When I ask questions in Discord channels, use memory_search or memory_get if you need long-term context from MEMORY.md."
      </Tab>
      <Tab title="Manual">
        If you need shared context in every channel, put the stable instructions in __CODE_BLOCK_4__ or __CODE_BLOCK_5__ (they are injected for every session). Keep long-term notes in __CODE_BLOCK_6__ and access them on demand with memory tools.
      </Tab>
    </Tabs>

  </Step>
</Steps>

现在在您的Discord服务器上创建一些频道并开始聊天。您的代理可以看到频道名称，并且每个频道都有自己的独立会话——因此您可以设置`#coding`，`#home`，`#research`，或者根据您的工作流程设置其他内容。

## 运行时模型

- 网关拥有Discord连接。
- 回复路由是确定性的：来自Discord的传入回复将返回到Discord。
- 默认情况下 (`session.dmScope=main`)，直接聊天共享代理主会话 (`agent:main:main`)。
- 服务器频道具有独立的会话密钥 (`agent:<agentId>:discord:channel:<channelId>`)。
- 默认情况下忽略群组直接消息 (`channels.discord.dm.groupEnabled=false`)。
- 原生斜杠命令在隔离的命令会话 (`agent:<agentId>:discord:slash:<userId>`) 中运行，同时仍然携带 `CommandTargetSessionKey` 到路由的对话会话。

## 论坛频道

Discord论坛和媒体频道仅接受线程帖子。OpenClaw支持两种创建它们的方法：

- 向论坛父频道 (`channel:<forumId>`) 发送消息以自动创建线程。线程标题使用您消息中的第一行非空文本。
- 使用 `openclaw message thread create` 直接创建线程。不要为论坛频道传递 `--message-id`。

示例：发送到论坛父频道以创建线程

```bash
openclaw message send --channel discord --target channel:<forumId> \
  --message "Topic title\nBody of the post"
```

示例: 创建一个论坛线程

```bash
openclaw message thread create --channel discord --target channel:<forumId> \
  --thread-name "Topic title" --message "Body of the post"
```

论坛父级不接受Discord组件。如果需要组件，请发送到线程本身 (`channel:<threadId>`)。

## 交互式组件

OpenClaw支持代理消息的Discord组件v2容器。使用带有`components`负载的消息工具。交互结果作为正常的传入消息路由回代理，并遵循现有的Discord `replyToMode`设置。

支持的块：

- `text`, `section`, `separator`, `actions`, `media-gallery`, `file`
- 动作行最多允许5个按钮或单个选择菜单
- 选择类型：`string`, `user`, `role`, `mentionable`, `channel`

默认情况下，组件是一次性使用的。设置`components.reusable=true`以允许多次使用按钮、选择和表单，直到它们过期。

要限制谁可以点击按钮，请在该按钮上设置`allowedUsers`（Discord用户ID、标签或`*`）。当配置后，未匹配的用户会收到临时拒绝消息。

`/model`和`/models`斜杠命令打开一个交互式模型选择器，包含提供商和模型下拉菜单以及提交步骤。选择器回复是临时的，只有调用用户可以使用它。

文件附件：

- `file`块必须指向附件引用 (`attachment://<filename>`)
- 通过`media`/`path`/`filePath`（单个文件）提供附件；使用`media-gallery`进行多个文件
- 使用`filename`覆盖上传名称，使其与附件引用匹配

模态表单：

- 添加最多5个字段的`components.modal`
- 字段类型：`text`, `checkbox`, `radio`, `select`, `role-select`, `user-select`
- OpenClaw会自动添加触发按钮

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
  <Tab title="DM 策略">
    `channels.discord.dmPolicy` 控制 DM 访问（旧版：`channels.discord.dm.policy`）：

    - `pairing`（默认）
    - `allowlist`
    - `open`（需要 `channels.discord.allowFrom` 包含 `"*"`；旧版：`channels.discord.dm.allowFrom`）
    - `disabled`

    如果 DM 策略未开启，未知用户将被阻止（或在 `pairing` 模式下提示配对）。

    DM 目标格式用于传递：

    - `user:<id>`
    - 提及 `<@id>`

    仅数字 ID 是模糊的，除非提供了明确的用户/频道目标类型，否则会被拒绝。

  </Tab>

  <Tab title="服务器策略">
    服务器处理由 `channels.discord.groupPolicy` 控制：

    - `open`
    - `allowlist`
    - `disabled`

    当存在 `channels.discord` 时的安全基线是 `allowlist`。

    `allowlist` 行为：

    - 服务器必须匹配 `channels.discord.guilds` (`id` 优先，接受 slug)
    - 可选的发件人白名单：`users`（ID 或名称）和 `roles`（仅角色 ID）；如果任一已配置，当发件人匹配 `users` 或 `roles` 时允许发送
    - 支持 `users` 的名称/标签，但 ID 更安全；`openclaw security audit` 在使用名称/标签条目时发出警告
    - 如果服务器配置了 `channels`，未列出的频道将被拒绝
    - 如果服务器没有配置 `channels` 阻止，则允许该白名单服务器中的所有频道

    示例：

```json5
{
  channels: {
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        "123456789012345678": {
          requireMention: true,
          users: ["987654321098765432"],
          roles: ["123456789012345678"],
          channels: {
            general: { allow: true },
            help: { allow: true, requireMention: true },
          },
        },
      },
    },
  },
}
```</Tab>
</Tabs>

如果仅设置 `DISCORD_BOT_TOKEN` 而不创建 `channels.discord` 块，则运行时回退为 `groupPolicy="open"`（日志中有警告）。

  </Tab>

  <Tab title="提及和群组直接消息">
    频道消息默认是通过提及来触发的。

    提及检测包括：

    - 明确的机器人提及
    - 配置的提及模式 (`agents.list[].groupChat.mentionPatterns`，回退 `messages.groupChat.mentionPatterns`)
    - 支持情况下的隐式回复机器人行为

    `requireMention` 是按频道/子频道配置的 (`channels.discord.guilds...`)。

    群组直接消息：

    - 默认：忽略 (`dm.groupEnabled=false`)
    - 可选白名单通过 `dm.groupChannels`（频道ID或别名）

  </Tab>
</Tabs>

### 基于角色的代理路由

使用 `bindings[].match.roles` 根据角色ID将Discord频道成员路由到不同的代理。基于角色的绑定仅接受角色ID，并在对等或父对等绑定之后评估，在仅频道绑定之前评估。如果绑定还设置了其他匹配字段（例如 `peer` + `guildId` + `roles`），则所有配置的字段必须匹配。

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

    Presence intent is optional and only required if you want to receive presence updates. Setting bot presence (__CODE_BLOCK_14__) does not require enabling presence updates for members.

  </Accordion>

  <Accordion title="OAuth scopes and baseline permissions">
    OAuth URL generator:

    - scopes: __CODE_BLOCK_15__, __CODE_BLOCK_16__

    Typical baseline permissions:

    - View Channels
    - Send Messages
    - Read Message History
    - Embed Links
    - Attach Files
    - Add Reactions (optional)

    Avoid __CODE_BLOCK_17__ unless explicitly needed.

  </Accordion>

  <Accordion title="Copy IDs">
    Enable Discord Developer Mode, then copy:

    - server ID
    - channel ID
    - user ID

    Prefer numeric IDs in OpenClaw config for reliable audits and probes.

  </Accordion>
</AccordionGroup>

## 原生命令和命令授权

- `commands.native` 默认为 `"auto"` 并且在 Discord 上启用。
- 按频道覆盖：`channels.discord.commands.native`。
- `commands.native=false` 明确清除之前注册的 Discord 原生命令。
- 原生命令授权使用与正常消息处理相同的 Discord 允许列表/策略。
- 对于未授权的用户，命令可能仍然在 Discord UI 中可见；执行时仍然强制 OpenClaw 授权并返回“未授权”。

请参阅 [Slash 命令](/tools/slash-commands) 获取命令目录和行为。

默认 slash 命令设置：

- `ephemeral: true`

## 功能详情

<AccordionGroup>
  <Accordion title="回复标签和原生回复">
    Discord 支持代理输出中的回复标签：

    - `[[reply_to_current]]`
    - `[[reply_to:<id>]]`

    由 `channels.discord.replyToMode` 控制：

    - `off`（默认）
    - `first`
    - `all`

    注意：`off` 禁用隐式回复线程。显式的 `[[reply_to_*]]` 标签仍然有效。

    消息 ID 在上下文/历史记录中公开，以便代理可以针对特定消息。

  </Accordion>

  <Accordion title="直播预览">
    OpenClaw 可以通过发送临时消息并在文本到达时编辑它来流式传输草稿回复。

    - `channels.discord.streaming` 控制预览流式传输 (`off` | `partial` | `block` | `progress`，默认：`off`)。
    - `progress` 用于跨频道一致性，并映射到 Discord 上的 `partial`。
    - `channels.discord.streamMode` 是一个旧别名，并会自动迁移。
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

    注意：预览流式传输与块流式传输分开。当 Discord 显式启用块流式传输时，OpenClaw 会跳过预览流以避免双重流式传输。

  </Accordion>

  <Accordion title="历史记录、上下文和线程行为">
    服务器历史记录上下文：

    - `channels.discord.historyLimit` 默认 `20`
    - 备用：`messages.groupChat.historyLimit`
    - `0` 禁用

    私信历史记录控制：

    - `channels.discord.dmHistoryLimit`
    - `channels.discord.dms["<user_id>"].historyLimit`

    线程行为：

    - Discord 线程作为频道会话路由
    - 父线程元数据可用于父会话链接
    - 线程配置继承自父频道配置，除非存在特定于线程的条目

    频道主题作为 **不受信任** 的上下文注入（而不是系统提示）。

</Accordion>

  <Accordion title="子代理的线程绑定会话">
    Discord 可以将一个线程绑定到一个会话目标，因此该线程中的后续消息将继续路由到相同的会话（包括子代理会话）。

    命令：

    - `/focus <target>` 将当前/新线程绑定到子代理/会话目标
    - `/unfocus` 移除当前线程绑定
    - `/agents` 显示活动运行和绑定状态
    - `/session ttl <duration|off>` 检查/更新聚焦绑定的自动失焦 TTL

    配置：

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      ttlHours: 24,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        ttlHours: 24,
        spawnSubagentSessions: false, // opt-in
      },
    },
  },
}
```

    注意事项：

    - `session.threadBindings.*` 设置全局默认值。
    - `channels.discord.threadBindings.*` 覆盖 Discord 行为。
    - `spawnSubagentSessions` 必须为 true 才能为 `sessions_spawn({ thread: true })` 自动创建/绑定线程。
    - 如果某个账户禁用了线程绑定，`/focus` 和相关的线程绑定操作将不可用。

    参见 [子代理](/tools/subagents) 和 [配置参考](/gateway/configuration-reference)。

  </Accordion>

  <Accordion title="反应通知">
    每个服务器的反应通知模式：

    - `off`
    - `own` （默认）
    - `all`
    - `allowlist` （使用 `guilds.<id>.users`）

    反应事件会被转换为系统事件并附加到路由的 Discord 会话中。

  </Accordion>

  <Accordion title="确认反应">
    `ackReaction` 在 OpenClaw 处理传入消息时发送确认表情符号。

    解析顺序：

    - `channels.discord.accounts.<accountId>.ackReaction`
    - `channels.discord.ackReaction`
    - `messages.ackReaction`
    - 代理身份表情符号回退 (`agents.list[].identity.emoji`，否则为 "👀")

    注意事项：

    - Discord 接受 Unicode 表情符号或自定义表情符号名称。
    - 使用 `""` 禁用某个频道或账户的反应。

  </Accordion>

  <Accordion title="配置写入">
    默认情况下启用由频道发起的配置写入。

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
    通过 `channels.discord.proxy` 将 Discord 网关 WebSocket 流量和启动 REST 查找（应用程序 ID + 允许列表解析）路由到 HTTP(S) 代理。

```json5
{
  channels: {
    discord: {
      proxy: "http://proxy.example:8080",
    },
  },
}
```

    按账户覆盖：

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

    注意事项：

    - 允许列表可以使用 `pk:<memberId>`
    - 成员显示名称按名称/别名匹配
    - 查找使用原始消息 ID 并且时间窗口受限
    - 如果查找失败，代理消息被视为机器人消息并丢弃除非 `allowBots=true`

  </Accordion>

  <Accordion title="状态配置">
    状态更新仅在您设置状态或活动字段时应用。

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

    - 0: 正在玩
    - 1: 正在直播（需要 `activityUrl`）
    - 2: 正在听
    - 3: 正在看
    - 4: 自定义（使用活动文本作为状态；表情符号可选）
    - 5: 正在竞争

  </Accordion>

  <Accordion title="Discord 中的执行审批">
    Discord 支持基于按钮的执行审批，并且可以选择在源频道发布审批提示。

    配置路径：

    - `channels.discord.execApprovals.enabled`
    - `channels.discord.execApprovals.approvers`
    - `channels.discord.execApprovals.target` (`dm` | `channel` | `both`, 默认: `dm`)
    - `agentFilter`, `sessionFilter`, `cleanupAfterResolve`

    当 `target` 是 `channel` 或 `both` 时，审批提示在频道中可见。只有配置的审批者可以使用按钮；其他用户会收到临时拒绝消息。审批提示包括命令文本，因此仅在受信任的频道启用频道传递。如果无法从会话密钥推导出频道 ID，OpenClaw 将回退到直接消息传递。

    如果审批失败且审批 ID 未知，请验证审批者列表和功能启用情况。

    相关文档：[执行审批](/tools/exec-approvals)

  </Accordion>
</AccordionGroup>

## 工具和操作门

Discord 消息操作包括消息传递、频道管理、审核、状态和元数据操作。

核心示例：

- 消息传递: `sendMessage`, `readMessages`, `editMessage`, `deleteMessage`, `threadReply`
- 反应: `react`, `reactions`, `emojiList`
- 审核: `timeout`, `kick`, `ban`
- 状态: `setPresence`

操作门位于 `channels.discord.actions.*` 下。

默认门行为：

| 动作组                                                                                                                                                             | 默认值   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| reactions, messages, threads, pins, polls, search, memberInfo, roleInfo, channelInfo, channels, voiceStatus, events, stickers, emojiUploads, stickerUploads, permissions | enabled  |
| roles                                                                                                                                                                    | disabled |
| moderation                                                                                                                                                               | disabled |
| presence                                                                                                                                                                 | disabled |

## Components v2 UI

OpenClaw 使用 Discord components v2 进行执行审批和跨上下文标记。Discord 消息操作也可以接受 `components` 用于自定义 UI（高级；需要 Carbon 组件实例），而传统的 `embeds` 仍然可用但不推荐使用。

- `channels.discord.ui.components.accentColor` 设置 Discord 组件容器使用的强调颜色（十六进制）。
- 使用 `channels.discord.accounts.<id>.ui.components.accentColor` 按账户设置。
- 当存在 components v2 时，`embeds` 被忽略。

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

OpenClaw 可以加入 Discord 语音频道进行实时连续对话。这与语音消息附件是分开的。

要求：

- 启用原生命令 (`commands.native` 或 `channels.discord.commands.native`)。
- 配置 `channels.discord.voice`。
- 机器人需要在目标语音频道中具有连接和发言权限。

使用仅限 Discord 的原生命令 `/vc join|leave|status` 来控制会话。该命令使用账户默认代理，并遵循与其他 Discord 命令相同的允许列表和组策略规则。

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

- `voice.tts` 仅在语音播放时覆盖 `messages.tts`。
- 语音默认启用；设置 `channels.discord.voice.enabled=false` 以禁用它。

## 语音消息

Discord语音消息显示波形预览，并需要OGG/Opus音频加上元数据。OpenClaw会自动生成波形，但需要`ffmpeg`和`ffprobe`在网关主机上可用以检查和转换音频文件。

要求和限制：

- 提供一个**本地文件路径**（拒绝URL）。
- 省略文本内容（Discord不允许在同一负载中同时包含文本和语音消息）。
- 接受任何音频格式；OpenClaw在需要时会转换为OGG/Opus。

示例：

```bash
message(action="send", channel="discord", target="channel:123", path="/path/to/audio.mp3", asVoice=true)
```

## 故障排除

<AccordionGroup>
  <Accordion title="Used disallowed intents or bot sees no guild messages">

    - enable Message Content Intent
    - enable Server Members Intent when you depend on user/member resolution
    - restart gateway after changing intents

  </Accordion>

  <Accordion title="Guild messages blocked unexpectedly">

    - verify __CODE_BLOCK_3__
    - verify guild allowlist under __CODE_BLOCK_4__
    - if guild __CODE_BLOCK_5__ map exists, only listed channels are allowed
    - verify __CODE_BLOCK_6__ behavior and mention patterns

    Useful checks:

__CODE_BLOCK_7__

  </Accordion>

  <Accordion title="Require mention false but still blocked">
    Common causes:

    - __CODE_BLOCK_8__ without matching guild/channel allowlist
    - __CODE_BLOCK_9__ configured in the wrong place (must be under __CODE_BLOCK_10__ or channel entry)
    - sender blocked by guild/channel __CODE_BLOCK_11__ allowlist

  </Accordion>

  <Accordion title="Permissions audit mismatches">
    __CODE_BLOCK_12__ permission checks only work for numeric channel IDs.

    If you use slug keys, runtime matching can still work, but probe cannot fully verify permissions.

  </Accordion>

  <Accordion title="DM and pairing issues">

    - DM disabled: __CODE_BLOCK_13__
    - DM policy disabled: __CODE_BLOCK_14__ (legacy: __CODE_BLOCK_15__)
    - awaiting pairing approval in __CODE_BLOCK_16__ mode

  </Accordion>

  <Accordion title="Bot to bot loops">
    By default bot-authored messages are ignored.

    If you set __CODE_BLOCK_17__, use strict mention and allowlist rules to avoid loop behavior.

  </Accordion>
</AccordionGroup>

## 配置参考指针

主要参考：

- [配置参考 - Discord](/gateway/configuration-reference#discord)

高信号Discord字段：

- startup/auth: `enabled`, `token`, `accounts.*`, `allowBots`
- policy: `groupPolicy`, `dm.*`, `guilds.*`, `guilds.*.channels.*`
- command: `commands.native`, `commands.useAccessGroups`, `configWrites`, `slashCommand.*`
- reply/history: `replyToMode`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
- delivery: `textChunkLimit`, `chunkMode`, `maxLinesPerMessage`
- streaming: `streaming` (legacy alias: `streamMode`), `draftChunk`, `blockStreaming`, `blockStreamingCoalesce`
- media/retry: `mediaMaxMb`, `retry`
- actions: `actions.*`
- presence: `activity`, `status`, `activityType`, `activityUrl`
- UI: `ui.components.accentColor`
- features: `pluralkit`, `execApprovals`, `intents`, `agentComponents`, `heartbeat`, `responsePrefix`

## 安全与操作

- 将机器人令牌视为机密信息（在受监督环境中推荐使用`DISCORD_BOT_TOKEN`）。
- 授予最低权限的Discord权限。
- 如果command deploy/state过期，请重启网关并使用`openclaw channels status --probe`重新检查。

## 相关

- [配对](/channels/pairing)
- [频道路由](/channels/channel-routing)
- [多代理路由](/concepts/multi-agent)
- [故障排除](/channels/troubleshooting)
- [斜杠命令](/tools/slash-commands)