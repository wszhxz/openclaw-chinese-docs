---
summary: "Slack setup and runtime behavior (Socket Mode + HTTP Events API)"
read_when:
  - Setting up Slack or debugging Slack socket/HTTP mode
title: "Slack"
---
# Slack

状态：通过 Slack 应用集成支持 DM 和频道的生产就绪版本。默认模式为 Socket Mode；HTTP Events API 模式也受支持。

<CardGroup cols={3}>
  <Card title="配对" icon="link" href="/channels/pairing">
    Slack DM 默认为配对模式。
  </Card>
  <Card title="斜杠命令" icon="terminal" href="/tools/slash-commands">
    原生命令行为和命令目录。
  </Card>
  <Card title="频道故障排查" icon="wrench" href="/channels/troubleshooting">
    跨频道诊断和修复手册。
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

## 令牌模型

- ``botToken`` + ``appToken`` 是 Socket Mode 所必需的。
- HTTP 模式需要 ``botToken`` + ``signingSecret``。
- 配置令牌覆盖环境变量回退。
- ``SLACK_BOT_TOKEN`` / ``SLACK_APP_TOKEN`` 环境变量回退仅适用于默认账户。
- ``userToken`` (``xoxp-...``) 仅限配置（无环境变量回退），默认行为为只读（``userTokenReadOnly: true``）。
- 可选：如果您希望发出的消息使用活动的代理身份（自定义 ``username`` 和图标），请添加 ``chat:write.customize``。``icon_emoji`` 使用 ``:emoji_name:`` 语法。

<Tip>
For actions/directory reads, user token can be preferred when configured. For writes, bot token remains preferred; user-token writes are only allowed when __CODE_BLOCK_35__ and bot token is unavailable.
</Tip>

## 访问控制和路由

<Tabs>
  <Tab title="DM policy">
    __CODE_BLOCK_36__ controls DM access (legacy: __CODE_BLOCK_37__):

    - __CODE_BLOCK_38__ (default)
    - __CODE_BLOCK_39__
    - __CODE_BLOCK_40__ (requires __CODE_BLOCK_41__ to include __CODE_BLOCK_42__; legacy: __CODE_BLOCK_43__)
    - __CODE_BLOCK_44__

    DM flags:

    - __CODE_BLOCK_45__ (default true)
    - __CODE_BLOCK_46__ (preferred)
    - __CODE_BLOCK_47__ (legacy)
    - __CODE_BLOCK_48__ (group DMs default false)
    - __CODE_BLOCK_49__ (optional MPIM allowlist)

    Multi-account precedence:

    - __CODE_BLOCK_50__ applies only to the __CODE_BLOCK_51__ account.
    - Named accounts inherit __CODE_BLOCK_52__ when their own __CODE_BLOCK_53__ is unset.
    - Named accounts do not inherit __CODE_BLOCK_54__.

    Pairing in DMs uses __CODE_BLOCK_55__.

  </Tab>

  <Tab title="Channel policy">
    __CODE_BLOCK_56__ controls channel handling:

    - __CODE_BLOCK_57__
    - __CODE_BLOCK_58__
    - __CODE_BLOCK_59__

    Channel allowlist lives under __CODE_BLOCK_60__.

    Runtime note: if __CODE_BLOCK_61__ is completely missing (env-only setup), runtime falls back to __CODE_BLOCK_62__ and logs a warning (even if __CODE_BLOCK_63__ is set).

    Name/ID resolution:

    - channel allowlist entries and DM allowlist entries are resolved at startup when token access allows
    - unresolved entries are kept as configured
    - inbound authorization matching is ID-first by default; direct username/slug matching requires __CODE_BLOCK_64__

  </Tab>

  <Tab title="Mentions and channel users">
    Channel messages are mention-gated by default.

    Mention sources:

    - explicit app mention (__CODE_BLOCK_65__)
    - mention regex patterns (__CODE_BLOCK_66__, fallback __CODE_BLOCK_67__)
    - implicit reply-to-bot thread behavior

    Per-channel controls (__CODE_BLOCK_68__):

    - __CODE_BLOCK_69__
    - __CODE_BLOCK_70__ (allowlist)
    - __CODE_BLOCK_71__
    - __CODE_BLOCK_72__
    - __CODE_BLOCK_73__
    - __CODE_BLOCK_74__, __CODE_BLOCK_75__
    - __CODE_BLOCK_76__ key format: __CODE_BLOCK_77__, __CODE_BLOCK_78__, __CODE_BLOCK_79__, __CODE_BLOCK_80__, or __CODE_BLOCK_81__ wildcard
      (legacy unprefixed keys still map to __CODE_BLOCK_82__ only)

  </Tab>
</Tabs>

## 命令和斜杠行为

- Slack 的原生命令自动模式处于 **关闭** 状态（``commands.native: "auto"`` 不会启用 Slack 原生命令）。
- 使用 ``channels.slack.commands.native: true`` 启用原生 Slack 命令处理器（或全局 ``commands.native: true``）。
- 当启用原生命令时，在 Slack 中注册匹配的斜杠命令（``/<command>`` 名称），但有一个例外：
  - 为状态命令注册 ``/agentstatus``（Slack 保留 ``/status``）
- 如果未启用原生命令，您可以通过 ``channels.slack.slashCommand`` 运行单个配置的斜杠命令。
- 原生参数菜单现在调整其渲染策略：
  - 最多 5 个选项：按钮区块
  - 6-100 个选项：静态选择菜单
  - 超过 100 个选项：外部选择，当可用交互选项处理器时使用异步选项过滤
  - 如果编码选项值超出 Slack 限制，流程将回退到按钮
- 对于长选项负载，斜杠命令参数菜单在分发选定值之前会使用确认对话框。

默认斜杠命令设置：

- ``enabled: false``
- ``name: "openclaw"``
- ``sessionPrefix: "slack:slash"``
- ``ephemeral: true``

斜杠会话使用隔离密钥：

- ``agent:<agentId>:slack:slash:<userId>``

并且仍然针对目标对话会话路由命令执行（``CommandTargetSessionKey``）。

## 线程、会话和回复标签

- DM 路由为 ``direct``；频道路由为 ``channel``；MPIM 路由为 ``group``。
- 使用默认 ``session.dmScope=main``，Slack DM 折叠到代理主会话。
- 频道会话：``agent:<agentId>:slack:channel:<channelId>``。
- 线程回复可以在适用时创建线程会话后缀（``:thread:<threadTs>``）。
- ``channels.slack.thread.historyScope`` 默认为 ``thread``；``thread.inheritParent`` 默认为 ``false``。
- ``channels.slack.thread.initialHistoryLimit`` 控制新线程会话启动时获取多少现有线程消息（默认 ``20``；设置 ``0`` 以禁用）。

回复线程控制：

- ``channels.slack.replyToMode``: ``off|first|all``（默认 ``off``）
- ``channels.slack.replyToModeByChatType``: 每个 ``direct|group|channel``
- 直接聊天的传统回退：``channels.slack.dm.replyToMode``

支持手动回复标签：

- ``[[reply_to_current]]``
- ``[[reply_to:<id>]]``

注意：``replyToMode="off"`` 会禁用 Slack 中的 **所有** 回复线程，包括显式 ``[[reply_to_*]]`` 标签。这与 Telegram 不同，在 Telegram 中，显式标签在 ``"off"`` 模式下仍被尊重。这种差异反映了平台线程模型：Slack 线程将消息从频道隐藏，而 Telegram 回复在主聊天流中保持可见。

## 媒体、分块和交付

<AccordionGroup>
  <Accordion title="Inbound attachments">
    Slack file attachments are downloaded from Slack-hosted private URLs (token-authenticated request flow) and written to the media store when fetch succeeds and size limits permit.

    Runtime inbound size cap defaults to __CODE_BLOCK_120__ unless overridden by __CODE_BLOCK_121__.

  </Accordion>

  <Accordion title="Outbound text and files">
    - text chunks use __CODE_BLOCK_122__ (default 4000)
    - __CODE_BLOCK_123__ enables paragraph-first splitting
    - file sends use Slack upload APIs and can include thread replies (__CODE_BLOCK_124__)
    - outbound media cap follows __CODE_BLOCK_125__ when configured; otherwise channel sends use MIME-kind defaults from media pipeline
  </Accordion>

  <Accordion title="Delivery targets">
    Preferred explicit targets:

    - __CODE_BLOCK_126__ for DMs
    - __CODE_BLOCK_127__ for channels

    Slack DMs are opened via Slack conversation APIs when sending to user targets.

  </Accordion>
</AccordionGroup>

## 操作和门控

Slack 操作由 ``channels.slack.actions.*`` 控制。

当前 Slack 工具中可用的操作组：

| 组      | 默认 |
| ---------- | ------- |
| messages   | enabled |
| reactions  | enabled |
| pins       | enabled |
| memberInfo | enabled |
| emojiList  | enabled |

## 事件和操作行为

- 消息编辑/删除/线程广播被映射为系统事件。
- 反应添加/移除事件被映射为系统事件。
- 成员加入/离开、频道创建/重命名以及置顶添加/移除事件被映射为系统事件。
- 助手线程状态更新（用于线程中的“正在输入..."指示器）使用 `assistant.threads.setStatus` 并需要机器人权限范围 `assistant:write`。
- 当启用 `configWrites` 时，`channel_id_changed` 可以迁移频道配置键。
- 频道主题/用途元数据被视为不可信上下文，并可注入到路由上下文中。
- 块操作和模态交互会发出结构化的 `Slack interaction: ...` 系统事件，包含丰富的负载字段：
  - 块操作：选中的值、标签、选择器值和 `workflow_*` 元数据
  - 模态 `view_submission` 和 `view_closed` 事件，带有路由频道元数据和表单输入

## 确认反应

当 OpenClaw 处理传入消息时，`ackReaction` 会发送一个确认表情符号。

解析顺序：

- `channels.slack.accounts.<accountId>.ackReaction`
- `channels.slack.ackReaction`
- `messages.ackReaction`
- 代理身份表情符号回退 (`agents.list[].identity.emoji`，否则 "👀")

注意：

- Slack 期望短代码（例如 `"eyes"`）。
- 使用 `""` 禁用该 Slack 账户或全局的反应。

## 输入反应回退

`typingReaction` 在 OpenClaw 处理回复期间向传入的 Slack 消息添加临时反应，然后在运行结束时将其移除。当 Slack 原生助手输入不可用时，这是一个有用的回退方案，特别是在私聊中。

解析顺序：

- `channels.slack.accounts.<accountId>.typingReaction`
- `channels.slack.typingReaction`

注意：

- Slack 期望短代码（例如 `"hourglass_flowing_sand"`）。
- 反应尽最大努力，清理会在回复或失败路径完成后自动尝试。

## 清单和权限范围检查表

<AccordionGroup>
  <Accordion title="Slack app manifest example">

__CODE_BLOCK_19__

  </Accordion>

  <Accordion title="Optional user-token scopes (read operations)">
    If you configure __CODE_BLOCK_20__, typical read scopes are:

    - __CODE_BLOCK_21__, __CODE_BLOCK_22__, __CODE_BLOCK_23__, __CODE_BLOCK_24__
    - __CODE_BLOCK_25__, __CODE_BLOCK_26__, __CODE_BLOCK_27__, __CODE_BLOCK_28__
    - __CODE_BLOCK_29__
    - __CODE_BLOCK_30__
    - __CODE_BLOCK_31__
    - __CODE_BLOCK_32__
    - __CODE_BLOCK_33__ (if you depend on Slack search reads)

  </Accordion>
</AccordionGroup>

## 故障排除

<AccordionGroup>
  <Accordion title="No replies in channels">
    Check, in order:

    - __CODE_BLOCK_34__
    - channel allowlist (__CODE_BLOCK_35__)
    - __CODE_BLOCK_36__
    - per-channel __CODE_BLOCK_37__ allowlist

    Useful commands:

__CODE_BLOCK_38__

  </Accordion>

  <Accordion title="DM messages ignored">
    Check:

    - __CODE_BLOCK_39__
    - __CODE_BLOCK_40__ (or legacy __CODE_BLOCK_41__)
    - pairing approvals / allowlist entries

__CODE_BLOCK_42__

  </Accordion>

  <Accordion title="Socket mode not connecting">
    Validate bot + app tokens and Socket Mode enablement in Slack app settings.
  </Accordion>

  <Accordion title="HTTP mode not receiving events">
    Validate:

    - signing secret
    - webhook path
    - Slack Request URLs (Events + Interactivity + Slash Commands)
    - unique __CODE_BLOCK_43__ per HTTP account

  </Accordion>

  <Accordion title="Native/slash commands not firing">
    Verify whether you intended:

    - native command mode (__CODE_BLOCK_44__) with matching slash commands registered in Slack
    - or single slash command mode (__CODE_BLOCK_45__)

    Also check __CODE_BLOCK_46__ and channel/user allowlists.

  </Accordion>
</AccordionGroup>

## 文本流式传输

OpenClaw 通过 Agents and AI Apps API 支持 Slack 原生文本流式传输。

`channels.slack.streaming` 控制实时预览行为：

- `off`：禁用实时预览流式传输。
- `partial`（默认）：用最新的部分输出替换预览文本。
- `block`：追加分块预览更新。
- `progress`：生成时显示进度状态文本，然后发送最终文本。

当 `streaming` 为 `partial`（默认：`true`）时，`channels.slack.nativeStreaming` 控制 Slack 的原生流式传输 API（`chat.startStream` / `chat.appendStream` / `chat.stopStream`）。

禁用 Slack 原生流式传输（保留草稿预览行为）：

```yaml
channels:
  slack:
    streaming: partial
    nativeStreaming: false
```

遗留键：

- `channels.slack.streamMode`（`replace | status_final | append`）将自动迁移到 `channels.slack.streaming`。
- 布尔值 `channels.slack.streaming` 将自动迁移到 `channels.slack.nativeStreaming`。

### 要求

1. 在您的 Slack 应用设置中启用 **Agents and AI Apps**。
2. 确保应用具有 `assistant:write` 权限范围。
3. 必须为该消息提供回复线程。线程选择仍遵循 `replyToMode`。

### 行为

- 第一个文本块启动流（`chat.startStream`）。
- 后续文本块追加到同一流（`chat.appendStream`）。
- 回复结束完成流（`chat.stopStream`）。
- 媒体和非文本负载回退到正常交付。
- 如果流式传输在回复中途失败，OpenClaw 将为剩余负载回退到正常交付。

## 配置参考指针

主要参考：

- [配置参考 - Slack](/gateway/configuration-reference#slack)

  关键 Slack 字段：
  - 模式/认证：`mode`, `botToken`, `appToken`, `signingSecret`, `webhookPath`, `accounts.*`
  - DM 访问：`dm.enabled`, `dmPolicy`, `allowFrom`（遗留：`dm.policy`, `dm.allowFrom`），`dm.groupEnabled`, `dm.groupChannels`
  - 兼容性切换：`dangerouslyAllowNameMatching`（break-glass；除非需要请保持关闭）
  - 频道访问：`groupPolicy`, `channels.*`, `channels.*.users`, `channels.*.requireMention`
  - 线程/历史：`replyToMode`, `replyToModeByChatType`, `thread.*`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
  - 交付：`textChunkLimit`, `chunkMode`, `mediaMaxMb`, `streaming`, `nativeStreaming`
  - 运营/功能：`configWrites`, `commands.native`, `slashCommand.*`, `actions.*`, `userToken`, `userTokenReadOnly`

## 相关

- [配对](/channels/pairing)
- [频道路由](/channels/channel-routing)
- [故障排除](/channels/troubleshooting)
- [配置](/gateway/configuration)
- [斜杠命令](/tools/slash-commands)