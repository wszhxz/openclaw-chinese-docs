---
summary: "Slack setup and runtime behavior (Socket Mode + HTTP Events API)"
read_when:
  - Setting up Slack or debugging Slack socket/HTTP mode
title: "Slack"
---
# Slack

状态：通过 Slack 应用集成，DM（直接消息）和频道已具备生产就绪条件。默认模式为 Socket Mode；也支持 HTTP Events API 模式。

<CardGroup cols={3}>
  <Card title="配对" icon="link" href="/channels/pairing">
    Slack DM 默认为配对模式。
  </Card>
  <Card title="斜杠命令" icon="terminal" href="/tools/slash-commands">
    原生命令行为和命令目录。
  </Card>
  <Card title="频道故障排除" icon="wrench" href="/channels/troubleshooting">
    跨频道诊断和修复操作手册。
  </Card>
</CardGroup>

## 快速设置

<Tabs>
  <Tab title="Socket Mode (default)">
    <Steps>
      <Step title="Create Slack app and tokens">
        In Slack app settings:

        - enable **Socket Mode**
        - create **App Token** (__CODE_BLOCK_0__) with __CODE_BLOCK_1__
        - install app and copy **Bot Token** (__CODE_BLOCK_2__)
      </Step>

      <Step title="Configure OpenClaw">

__CODE_BLOCK_3__

        Env fallback (default account only):

__CODE_BLOCK_4__

      </Step>

      <Step title="Subscribe app events">
        Subscribe bot events for:

        - __CODE_BLOCK_5__
        - __CODE_BLOCK_6__, __CODE_BLOCK_7__, __CODE_BLOCK_8__, __CODE_BLOCK_9__
        - __CODE_BLOCK_10__, __CODE_BLOCK_11__
        - __CODE_BLOCK_12__, __CODE_BLOCK_13__
        - __CODE_BLOCK_14__
        - __CODE_BLOCK_15__, __CODE_BLOCK_16__

        Also enable App Home **Messages Tab** for DMs.
      </Step>

      <Step title="Start gateway">

__CODE_BLOCK_17__

      </Step>
    </Steps>

  </Tab>

  <Tab title="HTTP Events API mode">
    <Steps>
      <Step title="Configure Slack app for HTTP">

        - set mode to HTTP (__CODE_BLOCK_18__)
        - copy Slack **Signing Secret**
        - set Event Subscriptions + Interactivity + Slash command Request URL to the same webhook path (default __CODE_BLOCK_19__)

      </Step>

      <Step title="Configure OpenClaw HTTP mode">

__CODE_BLOCK_20__

      </Step>

      <Step title="Use unique webhook paths for multi-account HTTP">
        Per-account HTTP mode is supported.

        Give each account a distinct __CODE_BLOCK_21__ so registrations do not collide.
      </Step>
    </Steps>

  </Tab>
</Tabs>

## 清单和范围检查表

<AccordionGroup>
  <Accordion title="Slack app manifest example" defaultOpen>

__CODE_BLOCK_22__

  </Accordion>

  <Accordion title="Optional user-token scopes (read operations)">
    If you configure __CODE_BLOCK_23__, typical read scopes are:

    - __CODE_BLOCK_24__, __CODE_BLOCK_25__, __CODE_BLOCK_26__, __CODE_BLOCK_27__
    - __CODE_BLOCK_28__, __CODE_BLOCK_29__, __CODE_BLOCK_30__, __CODE_BLOCK_31__
    - __CODE_BLOCK_32__
    - __CODE_BLOCK_33__
    - __CODE_BLOCK_34__
    - __CODE_BLOCK_35__
    - __CODE_BLOCK_36__ (if you depend on Slack search reads)

  </Accordion>
</AccordionGroup>

## Token 模型

- Socket Mode 需要 `botToken` + `appToken`。
- HTTP 模式需要 `botToken` + `signingSecret`。
- `botToken`、`appToken`、`signingSecret` 和 `userToken` 接受纯文本字符串或 SecretRef 对象。
- 配置 Token 覆盖环境变量回退。
- `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` 环境变量回退仅适用于默认账户。
- `userToken` (`xoxp-...`) 仅限配置（无环境变量回退），默认行为为只读 (`userTokenReadOnly: true`)。
- 可选：如果您希望发出的消息使用活动代理身份（自定义 `username` 和图标），请添加 `chat:write.customize`。`icon_emoji` 使用 `:emoji_name:` 语法。

状态快照行为：

- Slack 账户检查跟踪每个凭据的 `*Source` 和 `*Status` 字段 (`botToken`、`appToken`、`signingSecret`、`userToken`)。
- 状态为 `available`、`configured_unavailable` 或 `missing`。
- `configured_unavailable` 表示账户已通过 SecretRef 或其他非内联秘密源配置，但当前命令/运行时路径无法解析实际值。
- 在 HTTP 模式中，包含 `signingSecretStatus`；在 Socket Mode 中，所需的对是 `botTokenStatus` + `appTokenStatus`。

<Tip>
For actions/directory reads, user token can be preferred when configured. For writes, bot token remains preferred; user-token writes are only allowed when __CODE_BLOCK_67__ and bot token is unavailable.
</Tip>

## 操作和门控

Slack 操作由 `channels.slack.actions.*` 控制。

当前 Slack 工具中可用的操作组：

| 组      | 默认 |
| ---------- | ------- |
| messages   | 启用 |
| reactions  | 启用 |
| pins       | 启用 |
| memberInfo | 启用 |
| emojiList  | 启用 |

当前 Slack 消息操作包括 `send`、`upload-file`、`download-file`、`read`、`edit`、`delete`、`pin`、`unpin`、`list-pins`、`member-info` 和 `emoji-list`。

## 访问控制和路由

<Tabs>
  <Tab title="DM policy">
    __CODE_BLOCK_80__ controls DM access (legacy: __CODE_BLOCK_81__):

    - __CODE_BLOCK_82__ (default)
    - __CODE_BLOCK_83__
    - __CODE_BLOCK_84__ (requires __CODE_BLOCK_85__ to include __CODE_BLOCK_86__; legacy: __CODE_BLOCK_87__)
    - __CODE_BLOCK_88__

    DM flags:

    - __CODE_BLOCK_89__ (default true)
    - __CODE_BLOCK_90__ (preferred)
    - __CODE_BLOCK_91__ (legacy)
    - __CODE_BLOCK_92__ (group DMs default false)
    - __CODE_BLOCK_93__ (optional MPIM allowlist)

    Multi-account precedence:

    - __CODE_BLOCK_94__ applies only to the __CODE_BLOCK_95__ account.
    - Named accounts inherit __CODE_BLOCK_96__ when their own __CODE_BLOCK_97__ is unset.
    - Named accounts do not inherit __CODE_BLOCK_98__.

    Pairing in DMs uses __CODE_BLOCK_99__.

  </Tab>

  <Tab title="Channel policy">
    __CODE_BLOCK_100__ controls channel handling:

    - __CODE_BLOCK_101__
    - __CODE_BLOCK_102__
    - __CODE_BLOCK_103__

    Channel allowlist lives under __CODE_BLOCK_104__ and should use stable channel IDs.

    Runtime note: if __CODE_BLOCK_105__ is completely missing (env-only setup), runtime falls back to __CODE_BLOCK_106__ and logs a warning (even if __CODE_BLOCK_107__ is set).

    Name/ID resolution:

    - channel allowlist entries and DM allowlist entries are resolved at startup when token access allows
    - unresolved channel-name entries are kept as configured but ignored for routing by default
    - inbound authorization and channel routing are ID-first by default; direct username/slug matching requires __CODE_BLOCK_108__

  </Tab>

  <Tab title="Mentions and channel users">
    Channel messages are mention-gated by default.

    Mention sources:

    - explicit app mention (__CODE_BLOCK_109__)
    - mention regex patterns (__CODE_BLOCK_110__, fallback __CODE_BLOCK_111__)
    - implicit reply-to-bot thread behavior

    Per-channel controls (__CODE_BLOCK_112__; names only via startup resolution or __CODE_BLOCK_113__):

    - __CODE_BLOCK_114__
    - __CODE_BLOCK_115__ (allowlist)
    - __CODE_BLOCK_116__
    - __CODE_BLOCK_117__
    - __CODE_BLOCK_118__
    - __CODE_BLOCK_119__, __CODE_BLOCK_120__
    - __CODE_BLOCK_121__ key format: __CODE_BLOCK_122__, __CODE_BLOCK_123__, __CODE_BLOCK_124__, __CODE_BLOCK_125__, or __CODE_BLOCK_126__ wildcard
      (legacy unprefixed keys still map to __CODE_BLOCK_127__ only)

  </Tab>
</Tabs>

## 线程、会话和回复标签

- DM 路由为 `direct`；频道为 `channel`；MPIM 为 `group`。
- 使用默认 `session.dmScope=main`，Slack DM 会折叠到代理主会话。
- 频道会话：`agent:<agentId>:slack:channel:<channelId>`。
- 当适用时，线程回复可以创建线程会话后缀 (`:thread:<threadTs>`)。
- `channels.slack.thread.historyScope` 默认为 `thread`；`thread.inheritParent` 默认为 `false`。
- `channels.slack.thread.initialHistoryLimit` 控制新线程会话开始时获取多少现有线程消息（默认 `20`；设置 `0` 以禁用）。

回复线程控制：

- `channels.slack.replyToMode`：`off|first|all`（默认 `off`）
- `channels.slack.replyToModeByChatType`：按 `direct|group|channel`
- 直接聊天的旧版回退：`channels.slack.dm.replyToMode`

支持手动回复标签：

- `[[reply_to_current]]`
- `[[reply_to:<id>]]`

注意：`replyToMode="off"` 会禁用 Slack 中的**所有**回复线程，包括显式的 `[[reply_to_*]]` 标签。这与 Telegram 不同，在 Telegram 中，显式标签在 `"off"` 模式下仍然有效。这种差异反映了平台的线程模型：Slack 线程会将消息从频道中隐藏，而 Telegram 回复则保留在主聊天流中可见。

## 确认反应

`ackReaction` 在 OpenClaw 处理传入消息时发送一个确认表情符号。

解析顺序：

- `channels.slack.accounts.<accountId>.ackReaction`
- `channels.slack.ackReaction`
- `messages.ackReaction`
- 代理身份表情符号回退（`agents.list[].identity.emoji`，否则为 "👀"）

注意：

- Slack 期望使用简码（例如 `"eyes"`）。
- 使用 `""` 可为 Slack 账户或全局禁用该反应。

## 文本流式传输

`channels.slack.streaming` 控制实时预览行为：

- `off`：禁用实时预览流。
- `partial`（默认）：用最新的部分输出替换预览文本。
- `block`：追加分块预览更新。
- `progress`：生成时显示进度状态文本，然后发送最终文本。

`channels.slack.nativeStreaming` 控制当 `streaming` 为 `partial` 时的 Slack 原生文本流式传输（默认：`true`）。

- 必须存在回复线程才能显示原生文本流式传输。线程选择仍遵循 `replyToMode`。如果没有，则使用普通草稿预览。
- 媒体和非文本负载将回退到正常交付。
- 如果流式传输在回复中途失败，OpenClaw 将对剩余负载回退到正常交付。

使用草稿预览代替 Slack 原生文本流式传输：

```json5
{
  channels: {
    slack: {
      streaming: "partial",
      nativeStreaming: false,
    },
  },
}
```

旧版键：

- `channels.slack.streamMode` (`replace | status_final | append`) 会自动迁移到 `channels.slack.streaming`。
- 布尔值 `channels.slack.streaming` 会自动迁移到 `channels.slack.nativeStreaming`。

## 输入中反应回退

`typingReaction` 在 OpenClaw 处理回复时，会在传入的 Slack 消息上添加一个临时反应，然后在运行结束后移除它。这在非线程回复中最有用，因为线程回复使用默认的“正在输入..."状态指示器。

解析顺序：

- `channels.slack.accounts.<accountId>.typingReaction`
- `channels.slack.typingReaction`

注意：

- Slack 期望使用简码（例如 `"hourglass_flowing_sand"`）。
- 该反应是尽力而为的，并且在回复或失败路径完成后会尝试自动清理。

## 媒体、分块和交付

<AccordionGroup>
  <Accordion title="Inbound attachments">
    Slack file attachments are downloaded from Slack-hosted private URLs (token-authenticated request flow) and written to the media store when fetch succeeds and size limits permit.

    Runtime inbound size cap defaults to __CODE_BLOCK_32__ unless overridden by __CODE_BLOCK_33__.

  </Accordion>

  <Accordion title="Outbound text and files">
    - text chunks use __CODE_BLOCK_34__ (default 4000)
    - __CODE_BLOCK_35__ enables paragraph-first splitting
    - file sends use Slack upload APIs and can include thread replies (__CODE_BLOCK_36__)
    - outbound media cap follows __CODE_BLOCK_37__ when configured; otherwise channel sends use MIME-kind defaults from media pipeline
  </Accordion>

  <Accordion title="Delivery targets">
    Preferred explicit targets:

    - __CODE_BLOCK_38__ for DMs
    - __CODE_BLOCK_39__ for channels

    Slack DMs are opened via Slack conversation APIs when sending to user targets.

  </Accordion>
</AccordionGroup>

## 命令和斜杠行为

- Slack 的原生命令自动模式为**关闭**（`commands.native: "auto"` 不会启用 Slack 原生命令）。
- 使用 `channels.slack.commands.native: true` 启用原生 Slack 命令处理器（或全局 `commands.native: true`）。
- 启用原生命令后，请在 Slack 中注册匹配的斜杠命令（`/<command>` 名称），有一个例外：
  - 为状态命令注册 `/agentstatus`（Slack 保留了 `/status`）
- 如果未启用原生命令，您可以通过 `channels.slack.slashCommand` 运行单个配置的斜杠命令。
- 原生参数菜单现在会调整其渲染策略：
  - 最多 5 个选项：按钮块
  - 6-100 个选项：静态选择菜单
  - 超过 100 个选项：外部选择，当可用交互选项处理器时进行异步选项过滤
  - 如果编码的选项值超过 Slack 限制，流程将回退到按钮
- 对于长选项负载，斜杠命令参数菜单在分发选定值之前会使用确认对话框。

默认斜杠命令设置：

- `enabled: false`
- `name: "openclaw"`
- `sessionPrefix: "slack:slash"`
- `ephemeral: true`

斜杠会话使用隔离的键：

- `agent:<agentId>:slack:slash:<userId>`

并且仍将命令执行路由到目标对话会话（`CommandTargetSessionKey`）。

## 交互式回复

Slack 可以渲染代理创建的交互式回复控件，但此功能默认处于禁用状态。

全局启用它：

```json5
{
  channels: {
    slack: {
      capabilities: {
        interactiveReplies: true,
      },
    },
  },
}
```

或者仅为一个 Slack 账户启用它：

```json5
{
  channels: {
    slack: {
      accounts: {
        ops: {
          capabilities: {
            interactiveReplies: true,
          },
        },
      },
    },
  },
}
```

启用后，代理可以发出仅限 Slack 的回复指令：

- `[[slack_buttons: Approve:approve, Reject:reject]]`
- `[[slack_select: Choose a target | Canary:canary, Production:production]]`

这些指令编译为 Slack Block Kit，并通过现有的 Slack 交互事件路径将点击或选择路由回来。

注意：

- 这是 Slack 特定的 UI。其他渠道不会将 Slack Block Kit 指令转换为它们自己的按钮系统。
- 交互式回调值是 OpenClaw 生成的不透明令牌，而不是原始的代理创建的值。
- 如果生成的交互块将超过 Slack Block Kit 限制，OpenClaw 将回退到原始文本回复，而不是发送无效的块负载。

## Slack 中的执行审批

Slack 可以作为具有交互式按钮和交互的原生审批客户端，而不是回退到 Web UI 或终端。

- 执行审批使用 `channels.slack.execApprovals.*` 进行原生 DM/频道路由。
- 当请求已经到达 Slack 且审批 ID 类型为 `plugin:` 时，插件审批仍然可以通过相同的 Slack 原生按钮界面解决。
- 审批人授权仍然强制执行：只有被识别为审批人的用户才能通过 Slack 批准或拒绝请求。

这与其他渠道使用相同的共享审批按钮界面。当在您的 Slack 应用设置中启用 `interactivity` 时，审批提示将作为 Block Kit 按钮直接在对话中渲染。
当这些按钮存在时，它们是主要的审批用户体验；仅当工具结果表示聊天审批不可用或手动审批是唯一途径时，OpenClaw 才应包含手动 `/approve` 命令。

配置路径：

- `channels.slack.execApprovals.enabled`
- `channels.slack.execApprovals.approvers`（可选；在可能时回退到 `commands.ownerAllowFrom`）
- `channels.slack.execApprovals.target` (`dm` | `channel` | `both`，默认：`dm`)
- `agentFilter`，`sessionFilter`

当 `enabled` 未设置或为 `"auto"` 且至少有一个审批人解析成功时，Slack 会自动启用原生执行审批。设置 `enabled: false` 以明确禁用 Slack 作为原生审批客户端。
设置 `enabled: true` 以在审批人解析时强制启用原生审批。

没有明确的 Slack 执行审批配置时的默认行为：

```json5
{
  commands: {
    ownerAllowFrom: ["slack:U12345678"],
  },
}
```

仅当您想要覆盖审批人、添加过滤器或选择源聊天交付时，才需要明确的 Slack 原生配置：

```json5
{
  channels: {
    slack: {
      execApprovals: {
        enabled: true,
        approvers: ["U12345678"],
        target: "both",
      },
    },
  },
}
```

共享 `approvals.exec` 转发是独立的。仅当执行审批提示也必须路由到其他聊天或明确的带外目标时使用它。共享 `approvals.plugin` 转发也是独立的；当这些请求已经到达 Slack 时，Slack 原生按钮仍然可以解决插件审批。

同一聊天 `/approve` 也适用于已支持命令的 Slack 频道和 DM。有关完整的审批转发模型，请参阅 [执行审批](/tools/exec-approvals)。

## 事件和操作行为

- 消息编辑/删除/线程广播映射为系统事件。
- 反应添加/删除事件映射为系统事件。
- 成员加入/离开、频道创建/重命名以及置顶添加/删除事件映射为系统事件。
- 当启用 `configWrites` 时，`channel_id_changed` 可以迁移频道配置键。
- 频道主题/目的元数据被视为不受信任的上下文，可以注入到路由上下文中。
- 线程发起者和初始线程历史上下文播种在适用时会由配置的发送者白名单过滤。
- 块操作和模态交互发出带有丰富负载字段的结构化 `Slack interaction: ...` 系统事件：
  - 块操作：选定值、标签、选择器值和 `workflow_*` 元数据
  - 带有路由频道元数据和表单输入的模态 `view_submission` 和 `view_closed` 事件

## 配置参考指针

主要参考：

- [配置参考 - Slack](/gateway/configuration-reference#slack)

高信号 Slack 字段：
  - 模式/认证：`mode`, `botToken`, `appToken`, `signingSecret`, `webhookPath`, `accounts.*`
  - DM 访问：`dm.enabled`, `dmPolicy`, `allowFrom` (旧版：`dm.policy`, `dm.allowFrom`), `dm.groupEnabled`, `dm.groupChannels`
  - 兼容性开关：`dangerouslyAllowNameMatching` (紧急启用；除非需要否则保持关闭)
  - 频道访问：`groupPolicy`, `channels.*`, `channels.*.users`, `channels.*.requireMention`
  - 线程/历史：`replyToMode`, `replyToModeByChatType`, `thread.*`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
  - 投递：`textChunkLimit`, `chunkMode`, `mediaMaxMb`, `streaming`, `nativeStreaming`
  - 运维/功能：`configWrites`, `commands.native`, `slashCommand.*`, `actions.*`, `userToken`, `userTokenReadOnly`

## 故障排除

<AccordionGroup>
  <Accordion title="No replies in channels">
    Check, in order:

    - __CODE_BLOCK_35__
    - channel allowlist (__CODE_BLOCK_36__)
    - __CODE_BLOCK_37__
    - per-channel __CODE_BLOCK_38__ allowlist

    Useful commands:

__CODE_BLOCK_39__

  </Accordion>

  <Accordion title="DM messages ignored">
    Check:

    - __CODE_BLOCK_40__
    - __CODE_BLOCK_41__ (or legacy __CODE_BLOCK_42__)
    - pairing approvals / allowlist entries

__CODE_BLOCK_43__

  </Accordion>

  <Accordion title="Socket mode not connecting">
    Validate bot + app tokens and Socket Mode enablement in Slack app settings.

    If __CODE_BLOCK_44__ shows __CODE_BLOCK_45__ or
    __CODE_BLOCK_46__, the Slack account is
    configured but the current runtime could not resolve the SecretRef-backed
    value.

  </Accordion>

  <Accordion title="HTTP mode not receiving events">
    Validate:

    - signing secret
    - webhook path
    - Slack Request URLs (Events + Interactivity + Slash Commands)
    - unique __CODE_BLOCK_47__ per HTTP account

    If __CODE_BLOCK_48__ appears in account
    snapshots, the HTTP account is configured but the current runtime could not
    resolve the SecretRef-backed signing secret.

  </Accordion>

  <Accordion title="Native/slash commands not firing">
    Verify whether you intended:

    - native command mode (__CODE_BLOCK_49__) with matching slash commands registered in Slack
    - or single slash command mode (__CODE_BLOCK_50__)

    Also check __CODE_BLOCK_51__ and channel/user allowlists.

  </Accordion>
</AccordionGroup>

## 相关

- [配对](/channels/pairing)
- [群组](/channels/groups)
- [安全](/gateway/security)
- [频道路由](/channels/channel-routing)
- [故障排除](/channels/troubleshooting)
- [配置](/gateway/configuration)
- [斜杠命令](/tools/slash-commands)