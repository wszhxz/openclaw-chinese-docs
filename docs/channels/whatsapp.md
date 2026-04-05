---
summary: "WhatsApp channel support, access controls, delivery behavior, and operations"
read_when:
  - Working on WhatsApp/web channel behavior or inbox routing
title: "WhatsApp"
---
# WhatsApp（Web 渠道）

状态：通过 WhatsApp Web (Baileys) 实现生产就绪。网关拥有关联的会话。

## 安装（按需）

- 引导流程 (`openclaw onboard`) 和 `openclaw channels add --channel whatsapp`
  在您首次选择时会提示安装 WhatsApp 插件。
- `openclaw channels login --channel whatsapp` 在插件尚未存在时也提供安装流程。
- 开发通道 + git checkout：默认为本地插件路径。
- 稳定版/Beta 版：默认为 npm 包 `@openclaw/whatsapp`。

手动安装方式仍然可用：

```bash
openclaw plugins install @openclaw/whatsapp
```

<CardGroup cols={3}>
  <Card title="Pairing" icon="link" href="/channels/pairing">
    Default DM policy is pairing for unknown senders.
  </Card>
  <Card title="Channel troubleshooting" icon="wrench" href="/channels/troubleshooting">
    Cross-channel diagnostics and repair playbooks.
  </Card>
  <Card title="Gateway configuration" icon="settings" href="/gateway/configuration">
    Full channel config patterns and examples.
  </Card>
</CardGroup>

## 快速设置

<Steps>
  <Step title="Configure WhatsApp access policy">

__CODE_BLOCK_5__

  </Step>

  <Step title="Link WhatsApp (QR)">

__CODE_BLOCK_6__

    For a specific account:

__CODE_BLOCK_7__

  </Step>

  <Step title="Start the gateway">

__CODE_BLOCK_8__

  </Step>

  <Step title="Approve first pairing request (if using pairing mode)">

__CODE_BLOCK_9__

    Pairing requests expire after 1 hour. Pending requests are capped at 3 per channel.

  </Step>
</Steps>

<Note>
OpenClaw recommends running WhatsApp on a separate number when possible. (The channel metadata and setup flow are optimized for that setup, but personal-number setups are also supported.)
</Note>

## 部署模式

<AccordionGroup>
  <Accordion title="Dedicated number (recommended)">
    This is the cleanest operational mode:

    - separate WhatsApp identity for OpenClaw
    - clearer DM allowlists and routing boundaries
    - lower chance of self-chat confusion

    Minimal policy pattern:

    __CODE_BLOCK_10__

  </Accordion>

  <Accordion title="Personal-number fallback">
    Onboarding supports personal-number mode and writes a self-chat-friendly baseline:

    - __CODE_BLOCK_11__
    - __CODE_BLOCK_12__ includes your personal number
    - __CODE_BLOCK_13__

    In runtime, self-chat protections key off the linked self number and __CODE_BLOCK_14__.

  </Accordion>

  <Accordion title="WhatsApp Web-only channel scope">
    The messaging platform channel is WhatsApp Web-based (__CODE_BLOCK_15__) in current OpenClaw channel architecture.

    There is no separate Twilio WhatsApp messaging channel in the built-in chat-channel registry.

  </Accordion>
</AccordionGroup>

## 运行时模型

- 网关拥有 WhatsApp 套接字和重连循环。
- 出站发送需要目标账户具有活动的 WhatsApp 监听器。
- 状态和广播聊天将被忽略 (`@status`, `@broadcast`)。
- 直接聊天使用 DM 会话规则 (`session.dmScope`; 默认 `main` 将 DM 折叠到代理主会话)。
- 群组会话相互隔离 (`agent:<agentId>:whatsapp:group:<jid>`)。

## 访问控制和激活

<Tabs>
  <Tab title="DM policy">
    __CODE_BLOCK_21__ controls direct chat access:

    - __CODE_BLOCK_22__ (default)
    - __CODE_BLOCK_23__
    - __CODE_BLOCK_24__ (requires __CODE_BLOCK_25__ to include __CODE_BLOCK_26__)
    - __CODE_BLOCK_27__

    __CODE_BLOCK_28__ accepts E.164-style numbers (normalized internally).

    Multi-account override: __CODE_BLOCK_29__ (and __CODE_BLOCK_30__) take precedence over channel-level defaults for that account.

    Runtime behavior details:

    - pairings are persisted in channel allow-store and merged with configured __CODE_BLOCK_31__
    - if no allowlist is configured, the linked self number is allowed by default
    - outbound __CODE_BLOCK_32__ DMs are never auto-paired

  </Tab>

  <Tab title="Group policy + allowlists">
    Group access has two layers:

    1. **Group membership allowlist** (__CODE_BLOCK_33__)
       - if __CODE_BLOCK_34__ is omitted, all groups are eligible
       - if __CODE_BLOCK_35__ is present, it acts as a group allowlist (__CODE_BLOCK_36__ allowed)

    2. **Group sender policy** (__CODE_BLOCK_37__ + __CODE_BLOCK_38__)
       - __CODE_BLOCK_39__: sender allowlist bypassed
       - __CODE_BLOCK_40__: sender must match __CODE_BLOCK_41__ (or __CODE_BLOCK_42__)
       - __CODE_BLOCK_43__: block all group inbound

    Sender allowlist fallback:

    - if __CODE_BLOCK_44__ is unset, runtime falls back to __CODE_BLOCK_45__ when available
    - sender allowlists are evaluated before mention/reply activation

    Note: if no __CODE_BLOCK_46__ block exists at all, runtime group-policy fallback is __CODE_BLOCK_47__ (with a warning log), even if __CODE_BLOCK_48__ is set.

  </Tab>

  <Tab title="Mentions + /activation">
    Group replies require mention by default.

    Mention detection includes:

    - explicit WhatsApp mentions of the bot identity
    - configured mention regex patterns (__CODE_BLOCK_49__, fallback __CODE_BLOCK_50__)
    - implicit reply-to-bot detection (reply sender matches bot identity)

    Security note:

    - quote/reply only satisfies mention gating; it does **not** grant sender authorization
    - with __CODE_BLOCK_51__, non-allowlisted senders are still blocked even if they reply to an allowlisted user's message

    Session-level activation command:

    - __CODE_BLOCK_52__
    - __CODE_BLOCK_53__

    __CODE_BLOCK_54__ updates session state (not global config). It is owner-gated.

  </Tab>
</Tabs>

## 个人号码和自我聊天行为

当链接的自我号码也存在于 `allowFrom` 中时，WhatsApp 自我聊天保护机制会激活：

- 跳过自我聊天回合的已读回执
- 忽略提及 JID 的自动触发行为，否则该行为会向您发送提醒
- 如果 `messages.responsePrefix` 未设置，自我聊天回复默认为 `[{identity.name}]` 或 `[openclaw]`

## 消息归一化和上下文

<AccordionGroup>
  <Accordion title="Inbound envelope + reply context">
    Incoming WhatsApp messages are wrapped in the shared inbound envelope.

    If a quoted reply exists, context is appended in this form:

    __CODE_BLOCK_59__

    Reply metadata fields are also populated when available (__CODE_BLOCK_60__, __CODE_BLOCK_61__, __CODE_BLOCK_62__, sender JID/E.164).

  </Accordion>

  <Accordion title="Media placeholders and location/contact extraction">
    Media-only inbound messages are normalized with placeholders such as:

    - __CODE_BLOCK_63__
    - __CODE_BLOCK_64__
    - __CODE_BLOCK_65__
    - __CODE_BLOCK_66__
    - __CODE_BLOCK_67__

    Location and contact payloads are normalized into textual context before routing.

  </Accordion>

  <Accordion title="Pending group history injection">
    For groups, unprocessed messages can be buffered and injected as context when the bot is finally triggered.

    - default limit: __CODE_BLOCK_68__
    - config: __CODE_BLOCK_69__
    - fallback: __CODE_BLOCK_70__
    - __CODE_BLOCK_71__ disables

    Injection markers:

    - __CODE_BLOCK_72__
    - __CODE_BLOCK_73__

  </Accordion>

  <Accordion title="Read receipts">
    Read receipts are enabled by default for accepted inbound WhatsApp messages.

    Disable globally:

    __CODE_BLOCK_74__

    Per-account override:

    __CODE_BLOCK_75__

    Self-chat turns skip read receipts even when globally enabled.

  </Accordion>
</AccordionGroup>

## 交付、分块和媒体

<AccordionGroup>
  <Accordion title="Text chunking">
    - default chunk limit: __CODE_BLOCK_76__
    - __CODE_BLOCK_77__
    - __CODE_BLOCK_78__ mode prefers paragraph boundaries (blank lines), then falls back to length-safe chunking
  </Accordion>

  <Accordion title="Outbound media behavior">
    - supports image, video, audio (PTT voice-note), and document payloads
    - __CODE_BLOCK_79__ is rewritten to __CODE_BLOCK_80__ for voice-note compatibility
    - animated GIF playback is supported via __CODE_BLOCK_81__ on video sends
    - captions are applied to the first media item when sending multi-media reply payloads
    - media source can be HTTP(S), __CODE_BLOCK_82__, or local paths
  </Accordion>

  <Accordion title="Media size limits and fallback behavior">
    - inbound media save cap: __CODE_BLOCK_83__ (default __CODE_BLOCK_84__)
    - outbound media send cap: __CODE_BLOCK_85__ (default __CODE_BLOCK_86__)
    - per-account overrides use __CODE_BLOCK_87__
    - images are auto-optimized (resize/quality sweep) to fit limits
    - on media send failure, first-item fallback sends text warning instead of dropping the response silently
  </Accordion>
</AccordionGroup>

## 反应级别

`channels.whatsapp.reactionLevel` 控制代理在 WhatsApp 上使用表情符号反应的广泛程度：

| 级别 | 确认反应 | 代理发起的反应 | 描述 |
| ------------- | ------------- | ------------------------- | ------------------------------------------------ |
| `"off"` | 否 | 否 | 无反应 |
| `"ack"` | 是 | 否 | 仅确认反应（回复前回执） |
| `"minimal"` | 是 | 是（保守） | 确认 + 代理反应，带有保守指导 |
| `"extensive"` | 是 | 是（鼓励） | 确认 + 代理反应，带有鼓励指导 |

默认值：`"minimal"`。

每个账户的覆盖设置使用 `channels.whatsapp.accounts.<id>.reactionLevel`。

```json5
{
  channels: {
    whatsapp: {
      reactionLevel: "ack",
    },
  },
}
```

## 确认反应

WhatsApp 支持通过 `channels.whatsapp.ackReaction` 在接收传入消息时立即发送确认反应。
确认反应受 `reactionLevel` 控制——当 `reactionLevel` 为 `"off"` 时，它们会被抑制。

```json5
{
  channels: {
    whatsapp: {
      ackReaction: {
        emoji: "👀",
        direct: true,
        group: "mentions", // always | mentions | never
      },
    },
  },
}
```

行为说明：

- 在传入消息被接受后立即发送（回复前）
- 失败会被记录但不会阻塞正常回复的发送
- 群组模式 `mentions` 会对提及触发的回合做出反应；群组激活 `always` 作为此检查的绕过方式
- WhatsApp 使用 `channels.whatsapp.ackReaction`（此处不使用旧版 `messages.ackReaction`）

## 多账户和凭证

<AccordionGroup>
  <Accordion title="Account selection and defaults">
    - account ids come from __CODE_BLOCK_16__
    - default account selection: __CODE_BLOCK_17__ if present, otherwise first configured account id (sorted)
    - account ids are normalized internally for lookup
  </Accordion>

  <Accordion title="Credential paths and legacy compatibility">
    - current auth path: __CODE_BLOCK_18__
    - backup file: __CODE_BLOCK_19__
    - legacy default auth in __CODE_BLOCK_20__ is still recognized/migrated for default-account flows
  </Accordion>

  <Accordion title="Logout behavior">
    __CODE_BLOCK_21__ clears WhatsApp auth state for that account.

    In legacy auth directories, __CODE_BLOCK_22__ is preserved while Baileys auth files are removed.

  </Accordion>
</AccordionGroup>

## 工具、操作和配置写入

- 代理工具支持包括 WhatsApp 反应操作（`react`）。
- 操作门控：
  - `channels.whatsapp.actions.reactions`
  - `channels.whatsapp.actions.polls`
- 通道发起的配置写入默认启用（通过 `channels.whatsapp.configWrites=false` 禁用）。

## 故障排除

<AccordionGroup>
  <Accordion title="Not linked (QR required)">
    Symptom: channel status reports not linked.

    Fix:

    __CODE_BLOCK_27__

  </Accordion>

  <Accordion title="Linked but disconnected / reconnect loop">
    Symptom: linked account with repeated disconnects or reconnect attempts.

    Fix:

    __CODE_BLOCK_28__

    If needed, re-link with __CODE_BLOCK_29__.

  </Accordion>

  <Accordion title="No active listener when sending">
    Outbound sends fail fast when no active gateway listener exists for the target account.

    Make sure gateway is running and the account is linked.

  </Accordion>

  <Accordion title="Group messages unexpectedly ignored">
    Check in this order:

    - __CODE_BLOCK_30__
    - __CODE_BLOCK_31__ / __CODE_BLOCK_32__
    - __CODE_BLOCK_33__ allowlist entries
    - mention gating (__CODE_BLOCK_34__ + mention patterns)
    - duplicate keys in __CODE_BLOCK_35__ (JSON5): later entries override earlier ones, so keep a single __CODE_BLOCK_36__ per scope

  </Accordion>

  <Accordion title="Bun runtime warning">
    WhatsApp gateway runtime should use Node. Bun is flagged as incompatible for stable WhatsApp/Telegram gateway operation.
  </Accordion>
</AccordionGroup>

## 配置参考指引

主要参考：

- [配置参考 - WhatsApp](/gateway/configuration-reference#whatsapp)

关键 WhatsApp 字段：

- 访问：`dmPolicy`, `allowFrom`, `groupPolicy`, `groupAllowFrom`, `groups`
- 投递：`textChunkLimit`, `chunkMode`, `mediaMaxMb`, `sendReadReceipts`, `ackReaction`, `reactionLevel`
- 多账户：`accounts.<id>.enabled`, `accounts.<id>.authDir`, account-level overrides
- 操作：`configWrites`, `debounceMs`, `web.enabled`, `web.heartbeatSeconds`, `web.reconnect.*`
- 会话行为：`session.dmScope`, `historyLimit`, `dmHistoryLimit`, `dms.<id>.historyLimit`

## 相关

- [配对](/channels/pairing)
- [群组](/channels/groups)
- [安全](/gateway/security)
- [通道路由](/channels/channel-routing)
- [多代理路由](/concepts/multi-agent)
- [故障排除](/channels/troubleshooting)