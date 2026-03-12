---
summary: "Slack setup and runtime behavior (Socket Mode + HTTP Events API)"
read_when:
  - Setting up Slack or debugging Slack socket/HTTP mode
title: "Slack"
---
# Slack

状态：已具备生产就绪能力，支持通过 Slack 应用集成实现私信（DM）和频道通信。默认模式为 Socket 模式；同时也支持 HTTP 事件 API 模式。

<CardGroup cols={3}>
  <Card title="配对" icon="link" href="/channels/pairing">
    Slack 私信默认采用配对模式。
  </Card>
  <Card title="斜杠命令" icon="terminal" href="/tools/slash-commands">
    原生命令行为及命令目录。
  </Card>
  <Card title="频道故障排查" icon="wrench" href="/channels/troubleshooting">
    跨频道诊断与修复操作手册。
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

## Token 模型

- `botToken` + `appToken` 是 Socket 模式所必需的。
- HTTP 模式需要 `botToken` + `signingSecret`。
- 配置中的 token 会覆盖环境变量回退值。
- `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` 环境变量回退仅适用于默认账户。
- `userToken` (`xoxp-...`) 仅支持配置方式（不支持环境变量回退），且默认为只读行为（`userTokenReadOnly: true`）。
- 可选：如需使外发消息使用当前代理身份（自定义 `username` 和图标），请添加 `chat:write.customize`。`icon_emoji` 使用 `:emoji_name:` 语法。

<Tip>
For actions/directory reads, user token can be preferred when configured. For writes, bot token remains preferred; user-token writes are only allowed when __CODE_BLOCK_35__ and bot token is unavailable.
</Tip>

## 访问控制与路由

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

## 命令与斜杠命令行为

- Slack 的原生命令自动模式默认为**关闭**（`commands.native: "auto"` 不启用 Slack 原生命令）。
- 使用 `channels.slack.commands.native: true`（或全局 `commands.native: true`）启用原生 Slack 命令处理器。
- 启用原生命令后，需在 Slack 中注册对应的斜杠命令（以 `/<command>` 命名），但有一个例外：
  - 状态命令（status command）应注册为 `/agentstatus`（Slack 已预留 `/status`）
- 若未启用原生命令，可通过 `channels.slack.slashCommand` 运行单个已配置的斜杠命令。
- 原生参数菜单现已适配其渲染策略：
  - 最多 5 个选项：按钮区块（button blocks）
  - 6–100 个选项：静态选择菜单（static select menu）
  - 超过 100 个选项：外部选择菜单（external select），当交互式选项处理器可用时支持异步选项过滤
  - 若编码后的选项值超出 Slack 限制，则流程自动回退至按钮形式
- 对于长选项负载，斜杠命令参数菜单会在分派所选值前弹出确认对话框。

默认斜杠命令设置：

- `enabled: false`
- `name: "openclaw"`
- `sessionPrefix: "slack:slash"`
- `ephemeral: true`

斜杠会话使用独立密钥：

- `agent:<agentId>:slack:slash:<userId>`

但仍将命令执行路由至目标会话（`CommandTargetSessionKey`）。

## 线程、会话与回复标签

- 私信（DM）路由为 `direct`；频道为 `channel`；多人即时消息（MPIM）为 `group`。
- 在默认 `session.dmScope=main` 下，Slack 私信将合并至代理主会话。
- 频道会话：`agent:<agentId>:slack:channel:<channelId>`。
- 在适用情况下，线程回复可创建线程会话后缀（`:thread:<threadTs>`）。
- `channels.slack.thread.historyScope` 默认值为 `thread`；`thread.inheritParent` 默认值为 `false`。
- `channels.slack.thread.initialHistoryLimit` 控制新线程会话启动时获取多少条已有线程消息（默认为 `20`；设为 `0` 可禁用该功能）。

回复线程控制项：

- `channels.slack.replyToMode`：`off|first|all`（默认为 `off`）
- `channels.slack.replyToModeByChatType`：按 `direct|group|channel` 设置
- 直接聊天的旧版回退机制：`channels.slack.dm.replyToMode`

支持手动回复标签：

- `[[reply_to_current]]`
- `[[reply_to:<id>]]`

注意：`replyToMode="off"` 将禁用 Slack 中**所有**回复线程功能，包括显式的 `[[reply_to_*]]` 标签。这与 Telegram 不同——在 Telegram 的 `"off"` 模式下，显式标签仍会被尊重。此差异源于平台线程模型的本质区别：Slack 的线程会将消息从频道中隐藏，而 Telegram 的回复则始终保留在主聊天流中可见。

## 媒体、分块与投递

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

## 动作与门控

Slack 动作由 `channels.slack.actions.*` 控制。

当前 Slack 工具中可用的动作组：

| 组别       | 默认值  |
| ---------- | ------- |
| messages   | 启用    |
| reactions  | 启用    |
| pins       | 启用    |
| memberInfo | 启用    |
| emojiList  | 启用    |

## 事件与运行行为

- 消息编辑/删除/线程广播被映射为系统事件。  
- 表情反应添加/移除事件被映射为系统事件。  
- 成员加入/退出、频道创建/重命名、置顶添加/移除事件被映射为系统事件。  
- 助理线程状态更新（用于线程中“正在输入……”指示器）使用 `assistant.threads.setStatus`，并需要机器人权限范围 `assistant:write`。  
- `channel_id_changed` 可在启用 `configWrites` 时迁移频道配置项。  
- 频道主题/用途元数据被视为不可信上下文，可注入路由上下文。  
- 区块操作和模态框交互会发出结构化的 `Slack interaction: ...` 系统事件，并附带丰富的有效载荷字段：  
  - 区块操作：所选值、标签、选择器值以及 `workflow_*` 元数据  
  - 模态框 `view_submission` 和 `view_closed` 事件，包含已路由的频道元数据及表单输入  

## 确认反应（Ack reactions）

`ackReaction` 在 OpenClaw 处理入站消息期间发送确认表情符号。

解析顺序：

- `channels.slack.accounts.<accountId>.ackReaction`  
- `channels.slack.ackReaction`  
- `messages.ackReaction`  
- 代理身份表情符号回退（`agents.list[].identity.emoji`，否则为 "👀"）

注意事项：

- Slack 期望使用短代码（例如 `"eyes"`）。  
- 使用 `""` 可为该 Slack 账户或全局禁用该反应。  

## 正在输入反应回退（Typing reaction fallback）

`typingReaction` 在 OpenClaw 处理回复期间，为入站 Slack 消息临时添加一个反应；当运行完成时自动移除该反应。此机制在 Slack 原生助手“正在输入”功能不可用（尤其在私信中）时，是一种实用的回退方案。

解析顺序：

- `channels.slack.accounts.<accountId>.typingReaction`  
- `channels.slack.typingReaction`  

注意事项：

- Slack 期望使用短代码（例如 `"hourglass_flowing_sand"`）。  
- 该反应为尽力而为（best-effort），清理操作将在回复完成或失败路径执行完毕后自动尝试。  

## 清单与权限检查表（Manifest and scope checklist）

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

## 故障排查（Troubleshooting）

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

## 文本流式传输（Text streaming）

OpenClaw 通过 Agents 和 AI Apps API 支持 Slack 原生文本流式传输。

`channels.slack.streaming` 控制实时预览行为：

- `off`：禁用实时预览流式传输。  
- `partial`（默认）：用最新的部分输出替换预览文本。  
- `block`：追加分块的预览更新。  
- `progress`：生成过程中显示进度状态文本，完成后发送最终文本。  

`channels.slack.nativeStreaming` 控制 Slack 原生流式传输 API（`chat.startStream` / `chat.appendStream` / `chat.stopStream`），当 `streaming` 为 `partial`（默认值：`true`）时生效。

禁用原生 Slack 流式传输（保留草稿预览行为）：

```yaml
channels:
  slack:
    streaming: partial
    nativeStreaming: false
```  

旧版配置项：

- `channels.slack.streamMode`（`replace | status_final | append`）将自动迁移至 `channels.slack.streaming`。  
- 布尔型 `channels.slack.streaming` 将自动迁移至 `channels.slack.nativeStreaming`。  

### 必要条件（Requirements）

1. 在 Slack 应用设置中启用 **Agents and AI Apps**。  
2. 确保应用具有 `assistant:write` 权限范围。  
3. 该消息必须存在可用的回复线程。线程选择仍遵循 `replyToMode`。  

### 行为说明（Behavior）

- 首个文本片段启动流式传输（`chat.startStream`）。  
- 后续文本片段追加至同一流（`chat.appendStream`）。  
- 回复结束时终结流式传输（`chat.stopStream`）。  
- 媒体内容及非文本有效载荷回退至常规交付方式。  
- 若流式传输在回复中途失败，OpenClaw 将对剩余有效载荷回退至常规交付方式。  

## 配置参考指引（Configuration reference pointers）

主要参考文档：

- [配置参考 - Slack](/gateway/configuration-reference#slack)

高信号 Slack 字段：
- 模式/认证（mode/auth）：`mode`、`botToken`、`appToken`、`signingSecret`、`webhookPath`、`accounts.*`  
- 私信访问（DM access）：`dm.enabled`、`dmPolicy`、`allowFrom`（旧版：`dm.policy`、`dm.allowFrom`）、`dm.groupEnabled`、`dm.groupChannels`  
- 兼容性切换开关（compatibility toggle）：`dangerouslyAllowNameMatching`（应急开关；除非必要，请保持关闭）  
- 频道访问（channel access）：`groupPolicy`、`channels.*`、`channels.*.users`、`channels.*.requireMention`  
- 线程/历史记录（threading/history）：`replyToMode`、`replyToModeByChatType`、`thread.*`、`historyLimit`、`dmHistoryLimit`、`dms.*.historyLimit`  
- 投递（delivery）：`textChunkLimit`、`chunkMode`、`mediaMaxMb`、`streaming`、`nativeStreaming`  
- 运维/功能（ops/features）：`configWrites`、`commands.native`、`slashCommand.*`、`actions.*`、`userToken`、`userTokenReadOnly`  

## 相关文档（Related）

- [配对](/channels/pairing)  
- [频道路由](/channels/channel-routing)  
- [故障排查](/channels/troubleshooting)  
- [配置](/gateway/configuration)  
- [斜杠命令](/tools/slash-commands)