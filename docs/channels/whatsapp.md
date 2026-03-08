---
summary: "WhatsApp channel support, access controls, delivery behavior, and operations"
read_when:
  - Working on WhatsApp/web channel behavior or inbox routing
title: "WhatsApp"
---
# WhatsApp (Web 渠道)

状态：通过 WhatsApp Web (Baileys) 实现生产就绪。网关拥有已链接的会话。

<CardGroup cols={3}>
  <Card title="Pairing" icon="link" href="/channels/pairing">
    默认 DM 策略是对未知发送者进行配对。
  </Card>
  <Card title="Channel troubleshooting" icon="wrench" href="/channels/troubleshooting">
    跨渠道诊断与修复手册。
  </Card>
  <Card title="Gateway configuration" icon="settings" href="/gateway/configuration">
    完整的渠道配置模式和示例。
  </Card>
</CardGroup>

## 快速设置

<Steps>
  <Step title="Configure WhatsApp access policy">

__CODE_BLOCK_0__

  </Step>

  <Step title="Link WhatsApp (QR)">

__CODE_BLOCK_1__

    For a specific account:

__CODE_BLOCK_2__

  </Step>

  <Step title="Start the gateway">

__CODE_BLOCK_3__

  </Step>

  <Step title="Approve first pairing request (if using pairing mode)">

__CODE_BLOCK_4__

    Pairing requests expire after 1 hour. Pending requests are capped at 3 per channel.

  </Step>
</Steps>

<Note>
OpenClaw recommends running WhatsApp on a separate number when possible. (The channel metadata and onboarding flow are optimized for that setup, but personal-number setups are also supported.)
</Note>

## 部署模式

<AccordionGroup>
  <Accordion title="Dedicated number (recommended)">
    This is the cleanest operational mode:

    - separate WhatsApp identity for OpenClaw
    - clearer DM allowlists and routing boundaries
    - lower chance of self-chat confusion

    Minimal policy pattern:

    __CODE_BLOCK_5__

  </Accordion>

  <Accordion title="Personal-number fallback">
    Onboarding supports personal-number mode and writes a self-chat-friendly baseline:

    - __CODE_BLOCK_6__
    - __CODE_BLOCK_7__ includes your personal number
    - __CODE_BLOCK_8__

    In runtime, self-chat protections key off the linked self number and __CODE_BLOCK_9__.

  </Accordion>

  <Accordion title="WhatsApp Web-only channel scope">
    The messaging platform channel is WhatsApp Web-based (__CODE_BLOCK_10__) in current OpenClaw channel architecture.

    There is no separate Twilio WhatsApp messaging channel in the built-in chat-channel registry.

  </Accordion>
</AccordionGroup>

## 运行时模型

- 网关拥有 WhatsApp socket 和重连循环。
- 出站发送需要目标账户的活跃 WhatsApp 监听器。
- 状态和广播聊天被忽略 (`@status`, `@broadcast`)。
- 直接聊天使用 DM 会话规则 (`session.dmScope`; 默认 `main` 将 DM 折叠到代理主会话)。
- 群组会话是隔离的 (`agent:<agentId>:whatsapp:group:<jid>`)。

## 访问控制与激活

<Tabs>
  <Tab title="DM policy">
    __CODE_BLOCK_16__ controls direct chat access:

    - __CODE_BLOCK_17__ (default)
    - __CODE_BLOCK_18__
    - __CODE_BLOCK_19__ (requires __CODE_BLOCK_20__ to include __CODE_BLOCK_21__)
    - __CODE_BLOCK_22__

    __CODE_BLOCK_23__ accepts E.164-style numbers (normalized internally).

    Multi-account override: __CODE_BLOCK_24__ (and __CODE_BLOCK_25__) take precedence over channel-level defaults for that account.

    Runtime behavior details:

    - pairings are persisted in channel allow-store and merged with configured __CODE_BLOCK_26__
    - if no allowlist is configured, the linked self number is allowed by default
    - outbound __CODE_BLOCK_27__ DMs are never auto-paired

  </Tab>

  <Tab title="Group policy + allowlists">
    Group access has two layers:

    1. **Group membership allowlist** (__CODE_BLOCK_28__)
       - if __CODE_BLOCK_29__ is omitted, all groups are eligible
       - if __CODE_BLOCK_30__ is present, it acts as a group allowlist (__CODE_BLOCK_31__ allowed)

    2. **Group sender policy** (__CODE_BLOCK_32__ + __CODE_BLOCK_33__)
       - __CODE_BLOCK_34__: sender allowlist bypassed
       - __CODE_BLOCK_35__: sender must match __CODE_BLOCK_36__ (or __CODE_BLOCK_37__)
       - __CODE_BLOCK_38__: block all group inbound

    Sender allowlist fallback:

    - if __CODE_BLOCK_39__ is unset, runtime falls back to __CODE_BLOCK_40__ when available
    - sender allowlists are evaluated before mention/reply activation

    Note: if no __CODE_BLOCK_41__ block exists at all, runtime group-policy fallback is __CODE_BLOCK_42__ (with a warning log), even if __CODE_BLOCK_43__ is set.

  </Tab>

  <Tab title="Mentions + /activation">
    Group replies require mention by default.

    Mention detection includes:

    - explicit WhatsApp mentions of the bot identity
    - configured mention regex patterns (__CODE_BLOCK_44__, fallback __CODE_BLOCK_45__)
    - implicit reply-to-bot detection (reply sender matches bot identity)

    Security note:

    - quote/reply only satisfies mention gating; it does **not** grant sender authorization
    - with __CODE_BLOCK_46__, non-allowlisted senders are still blocked even if they reply to an allowlisted user's message

    Session-level activation command:

    - __CODE_BLOCK_47__
    - __CODE_BLOCK_48__

    __CODE_BLOCK_49__ updates session state (not global config). It is owner-gated.

  </Tab>
</Tabs>

## 个人号码与自聊行为

当链接的自我号码也存在于 `allowFrom` 中时，WhatsApp 自聊保护机制激活：

- 跳过自聊回合的已读回执
- 忽略提及-JID 自动触发行为，否则这会 ping 你自己
- 如果 `messages.responsePrefix` 未设置，自聊回复默认为 `[{identity.name}]` 或 `[openclaw]`

## 消息标准化与上下文

<AccordionGroup>
  <Accordion title="Inbound envelope + reply context">
    Incoming WhatsApp messages are wrapped in the shared inbound envelope.

    If a quoted reply exists, context is appended in this form:

    __CODE_BLOCK_54__

    Reply metadata fields are also populated when available (__CODE_BLOCK_55__, __CODE_BLOCK_56__, __CODE_BLOCK_57__, sender JID/E.164).

  </Accordion>

  <Accordion title="Media placeholders and location/contact extraction">
    Media-only inbound messages are normalized with placeholders such as:

    - __CODE_BLOCK_58__
    - __CODE_BLOCK_59__
    - __CODE_BLOCK_60__
    - __CODE_BLOCK_61__
    - __CODE_BLOCK_62__

    Location and contact payloads are normalized into textual context before routing.

  </Accordion>

  <Accordion title="Pending group history injection">
    For groups, unprocessed messages can be buffered and injected as context when the bot is finally triggered.

    - default limit: __CODE_BLOCK_63__
    - config: __CODE_BLOCK_64__
    - fallback: __CODE_BLOCK_65__
    - __CODE_BLOCK_66__ disables

    Injection markers:

    - __CODE_BLOCK_67__
    - __CODE_BLOCK_68__

  </Accordion>

  <Accordion title="Read receipts">
    Read receipts are enabled by default for accepted inbound WhatsApp messages.

    Disable globally:

    __CODE_BLOCK_69__

    Per-account override:

    __CODE_BLOCK_70__

    Self-chat turns skip read receipts even when globally enabled.

  </Accordion>
</AccordionGroup>

## 投递、分块与媒体

<AccordionGroup>
  <Accordion title="Text chunking">
    - default chunk limit: __CODE_BLOCK_71__
    - __CODE_BLOCK_72__
    - __CODE_BLOCK_73__ mode prefers paragraph boundaries (blank lines), then falls back to length-safe chunking
  </Accordion>

  <Accordion title="Outbound media behavior">
    - supports image, video, audio (PTT voice-note), and document payloads
    - __CODE_BLOCK_74__ is rewritten to __CODE_BLOCK_75__ for voice-note compatibility
    - animated GIF playback is supported via __CODE_BLOCK_76__ on video sends
    - captions are applied to the first media item when sending multi-media reply payloads
    - media source can be HTTP(S), __CODE_BLOCK_77__, or local paths
  </Accordion>

  <Accordion title="Media size limits and fallback behavior">
    - inbound media save cap: __CODE_BLOCK_78__ (default __CODE_BLOCK_79__)
    - outbound media send cap: __CODE_BLOCK_80__ (default __CODE_BLOCK_81__)
    - per-account overrides use __CODE_BLOCK_82__
    - images are auto-optimized (resize/quality sweep) to fit limits
    - on media send failure, first-item fallback sends text warning instead of dropping the response silently
  </Accordion>
</AccordionGroup>

## 确认反馈

WhatsApp 支持通过 `channels.whatsapp.ackReaction` 在接收回执上立即进行 ack 反馈。

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

- 在接受入站后立即发送（回复前）
- 失败会被记录但不会阻塞正常回复投递
- 群组模式 `mentions` 对提及触发的回合做出反应；群组激活 `always` 作为此检查的绕过
- WhatsApp 使用 `channels.whatsapp.ackReaction`（此处不使用遗留 `messages.ackReaction`）

## 多账号与凭据

<AccordionGroup>
  <Accordion title="Account selection and defaults">
    - account ids come from __CODE_BLOCK_0__
    - default account selection: __CODE_BLOCK_1__ if present, otherwise first configured account id (sorted)
    - account ids are normalized internally for lookup
  </Accordion>

  <Accordion title="Credential paths and legacy compatibility">
    - current auth path: __CODE_BLOCK_2__
    - backup file: __CODE_BLOCK_3__
    - legacy default auth in __CODE_BLOCK_4__ is still recognized/migrated for default-account flows
  </Accordion>

  <Accordion title="Logout behavior">
    __CODE_BLOCK_5__ clears WhatsApp auth state for that account.

    In legacy auth directories, __CODE_BLOCK_6__ is preserved while Baileys auth files are removed.

  </Accordion>
</AccordionGroup>

## 工具、操作与配置写入

- Agent 工具支持包括 WhatsApp 反应操作 (`react`)。
- 操作门控：
  - `channels.whatsapp.actions.reactions`
  - `channels.whatsapp.actions.polls`
- 渠道发起的配置写入默认启用（通过 `channels.whatsapp.configWrites=false` 禁用）。

## 故障排除

<AccordionGroup>
  <Accordion title="Not linked (QR required)">
    Symptom: channel status reports not linked.

    Fix:

    __CODE_BLOCK_11__

  </Accordion>

  <Accordion title="Linked but disconnected / reconnect loop">
    Symptom: linked account with repeated disconnects or reconnect attempts.

    Fix:

    __CODE_BLOCK_12__

    If needed, re-link with __CODE_BLOCK_13__.

  </Accordion>

  <Accordion title="No active listener when sending">
    Outbound sends fail fast when no active gateway listener exists for the target account.

    Make sure gateway is running and the account is linked.

  </Accordion>

  <Accordion title="Group messages unexpectedly ignored">
    Check in this order:

    - __CODE_BLOCK_14__
    - __CODE_BLOCK_15__ / __CODE_BLOCK_16__
    - __CODE_BLOCK_17__ allowlist entries
    - mention gating (__CODE_BLOCK_18__ + mention patterns)
    - duplicate keys in __CODE_BLOCK_19__ (JSON5): later entries override earlier ones, so keep a single __CODE_BLOCK_20__ per scope

  </Accordion>

  <Accordion title="Bun runtime warning">
    WhatsApp gateway runtime should use Node. Bun is flagged as incompatible for stable WhatsApp/Telegram gateway operation.
  </Accordion>
</AccordionGroup>

## 配置参考指引

主要参考：

- [配置参考 - WhatsApp](/gateway/configuration-reference#whatsapp)

关键 WhatsApp 字段：

- access: `dmPolicy`, `allowFrom`, `groupPolicy`, `groupAllowFrom`, `groups`
- delivery: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `sendReadReceipts`, `ackReaction`
- multi-account: `accounts.<id>.enabled`, `accounts.<id>.authDir`, 账户级覆盖
- operations: `configWrites`, `debounceMs`, `web.enabled`, `web.heartbeatSeconds`, `web.reconnect.*`
- session behavior: `session.dmScope`, `historyLimit`, `dmHistoryLimit`, `dms.<id>.historyLimit`

## 相关

- [配对](/channels/pairing)
- [渠道路由](/channels/channel-routing)
- [多智能体路由](/concepts/multi-agent)
- [故障排除](/channels/troubleshooting)