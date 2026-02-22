---
summary: "WhatsApp channel support, access controls, delivery behavior, and operations"
read_when:
  - Working on WhatsApp/web channel behavior or inbox routing
title: "WhatsApp"
---
# WhatsApp (Web channel)

状态：通过WhatsApp Web (Baileys) 已生产就绪。网关拥有链接的会话。

<CardGroup cols={3}>
  <Card title="配对" icon="link" href="/channels/pairing">
    默认DM策略是未知发送者的配对。
  </Card>
  <Card title="通道故障排除" icon="wrench" href="/channels/troubleshooting">
    跨通道诊断和修复指南。
  </Card>
  <Card title="网关配置" icon="settings" href="/gateway/configuration">
    完整的通道配置模式和示例。
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

- Gateway 拥有 WhatsApp socket 和重连循环。
- 发送外发消息需要目标账户的活动 WhatsApp 监听器。
- 状态和广播聊天被忽略 (`@status`, `@broadcast`)。
- 直接聊天使用 DM 会话规则 (`session.dmScope`; 默认 `main` 将 DM 合并到代理主会话)。
- 群组会话是隔离的 (`agent:<agentId>:whatsapp:group:<jid>`)。

## 访问控制和激活

<Tabs>
  <Tab title="DM policy">
    __CODE_BLOCK_5__ controls direct chat access:

    - __CODE_BLOCK_6__ (default)
    - __CODE_BLOCK_7__
    - __CODE_BLOCK_8__ (requires __CODE_BLOCK_9__ to include __CODE_BLOCK_10__)
    - __CODE_BLOCK_11__

    __CODE_BLOCK_12__ accepts E.164-style numbers (normalized internally).

    Multi-account override: __CODE_BLOCK_13__ (and __CODE_BLOCK_14__) take precedence over channel-level defaults for that account.

    Runtime behavior details:

    - pairings are persisted in channel allow-store and merged with configured __CODE_BLOCK_15__
    - if no allowlist is configured, the linked self number is allowed by default
    - outbound __CODE_BLOCK_16__ DMs are never auto-paired

  </Tab>

  <Tab title="Group policy + allowlists">
    Group access has two layers:

    1. **Group membership allowlist** (__CODE_BLOCK_17__)
       - if __CODE_BLOCK_18__ is omitted, all groups are eligible
       - if __CODE_BLOCK_19__ is present, it acts as a group allowlist (__CODE_BLOCK_20__ allowed)

    2. **Group sender policy** (__CODE_BLOCK_21__ + __CODE_BLOCK_22__)
       - __CODE_BLOCK_23__: sender allowlist bypassed
       - __CODE_BLOCK_24__: sender must match __CODE_BLOCK_25__ (or __CODE_BLOCK_26__)
       - __CODE_BLOCK_27__: block all group inbound

    Sender allowlist fallback:

    - if __CODE_BLOCK_28__ is unset, runtime falls back to __CODE_BLOCK_29__ when available
    - sender allowlists are evaluated before mention/reply activation

    Note: if no __CODE_BLOCK_30__ block exists at all, runtime group-policy fallback is effectively __CODE_BLOCK_31__.

  </Tab>

  <Tab title="Mentions + /activation">
    Group replies require mention by default.

    Mention detection includes:

    - explicit WhatsApp mentions of the bot identity
    - configured mention regex patterns (__CODE_BLOCK_32__, fallback __CODE_BLOCK_33__)
    - implicit reply-to-bot detection (reply sender matches bot identity)

    Security note:

    - quote/reply only satisfies mention gating; it does **not** grant sender authorization
    - with __CODE_BLOCK_34__, non-allowlisted senders are still blocked even if they reply to an allowlisted user's message

    Session-level activation command:

    - __CODE_BLOCK_35__
    - __CODE_BLOCK_36__

    __CODE_BLOCK_37__ updates session state (not global config). It is owner-gated.

  </Tab>
</Tabs>

## 个人号码和自我聊天行为

当链接的自我号码也存在于 `allowFrom` 中时，WhatsApp 自我聊天保护功能将被激活：

- 跳过自我聊天回合的已读回执
- 忽略提及-JID自动触发行为，否则会ping自己
- 如果 `messages.responsePrefix` 未设置，自我聊天回复默认为 `[{identity.name}]` 或 `[openclaw]`

## 消息规范化和上下文

<AccordionGroup>
  <Accordion title="Inbound envelope + reply context">
    Incoming WhatsApp messages are wrapped in the shared inbound envelope.

    If a quoted reply exists, context is appended in this form:

    __CODE_BLOCK_3__

    Reply metadata fields are also populated when available (__CODE_BLOCK_4__, __CODE_BLOCK_5__, __CODE_BLOCK_6__, sender JID/E.164).

  </Accordion>

  <Accordion title="Media placeholders and location/contact extraction">
    Media-only inbound messages are normalized with placeholders such as:

    - __CODE_BLOCK_7__
    - __CODE_BLOCK_8__
    - __CODE_BLOCK_9__
    - __CODE_BLOCK_10__
    - __CODE_BLOCK_11__

    Location and contact payloads are normalized into textual context before routing.

  </Accordion>

  <Accordion title="Pending group history injection">
    For groups, unprocessed messages can be buffered and injected as context when the bot is finally triggered.

    - default limit: __CODE_BLOCK_12__
    - config: __CODE_BLOCK_13__
    - fallback: __CODE_BLOCK_14__
    - __CODE_BLOCK_15__ disables

    Injection markers:

    - __CODE_BLOCK_16__
    - __CODE_BLOCK_17__

  </Accordion>

  <Accordion title="Read receipts">
    Read receipts are enabled by default for accepted inbound WhatsApp messages.

    Disable globally:

    __CODE_BLOCK_18__

    Per-account override:

    __CODE_BLOCK_19__

    Self-chat turns skip read receipts even when globally enabled.

  </Accordion>
</AccordionGroup>

## 传递、分块和媒体

<AccordionGroup>
  <Accordion title="文本分块">
    - 默认分块限制: `channels.whatsapp.textChunkLimit = 4000`
    - `channels.whatsapp.chunkMode = "length" | "newline"`
    - `newline` 模式优先使用段落边界（空白行），然后回退到长度安全的分块
  </Accordion>

  <Accordion title="外发媒体行为">
    - 支持图像、视频、音频（PTT语音消息）和文档负载
    - `audio/ogg` 重写为 `audio/ogg; codecs=opus` 以兼容语音消息
    - 动态GIF播放通过 `gifPlayback: true` 在视频发送时支持
    - 发送多媒体回复负载时，标题应用于第一个媒体项
    - 媒体源可以是HTTP(S)、`file://` 或本地路径
  </Accordion>

<Accordion title="媒体大小限制和回退行为">
    - 入站媒体保存上限: `channels.whatsapp.mediaMaxMb` (默认 `50`)
    - 自动回复的出站媒体上限: `agents.defaults.mediaMaxMb` (默认 `5MB`)
    - 图像会自动优化（调整大小/质量扫描）以适应限制
    - 在媒体发送失败时，第一个项目的回退会发送文本警告而不是静默丢弃响应
  </Accordion>
</AccordionGroup>

## 确认反应

WhatsApp 支持通过 `channels.whatsapp.ackReaction` 对入站接收进行即时确认反应。

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

- 在入站被接受后立即发送（预回复）
- 失败会被记录但不会阻止正常回复的发送
- 群组模式 `mentions` 对提及触发的回合做出反应；群组激活 `always` 作为此检查的绕过
- WhatsApp 使用 `channels.whatsapp.ackReaction` (旧版 `messages.ackReaction` 在此处不使用)

## 多账户和凭据

<AccordionGroup>
  <Accordion title="Account selection and defaults">
    - account ids come from __CODE_BLOCK_10__
    - default account selection: __CODE_BLOCK_11__ if present, otherwise first configured account id (sorted)
    - account ids are normalized internally for lookup
  </Accordion>

  <Accordion title="Credential paths and legacy compatibility">
    - current auth path: __CODE_BLOCK_12__
    - backup file: __CODE_BLOCK_13__
    - legacy default auth in __CODE_BLOCK_14__ is still recognized/migrated for default-account flows
  </Accordion>

  <Accordion title="Logout behavior">
    __CODE_BLOCK_15__ clears WhatsApp auth state for that account.

    In legacy auth directories, __CODE_BLOCK_16__ is preserved while Baileys auth files are removed.

  </Accordion>
</AccordionGroup>

## 工具、操作和配置写入

- 代理工具支持包括 WhatsApp 反应操作 (`react`)。
- 操作门控：
  - `channels.whatsapp.actions.reactions`
  - `channels.whatsapp.actions.polls`
- 默认启用通道发起的配置写入（通过 `channels.whatsapp.configWrites=false` 禁用）。

## 故障排除

<AccordionGroup>
  <Accordion title="未链接（需要 QR 码）">
    症状：通道状态报告未链接。

    解决方法：

    ```bash
    openclaw channels login --channel whatsapp
    openclaw channels status
    ```

  </Accordion>

  <Accordion title="已链接但断开连接 / 重新连接循环">
    症状：链接账户出现重复断开连接或重新连接尝试。

    解决方法：

    ```bash
    openclaw doctor
    openclaw logs --follow
    ```

    如有必要，使用 `channels login` 重新链接。

  </Accordion>

<Accordion title="发送时没有活动监听器">
    当目标账户没有活动网关监听器时，外发消息会快速失败。

    确保网关正在运行并且账户已链接。

  </Accordion>

  <Accordion title="群组消息意外被忽略">
    按照以下顺序检查：

    - `groupPolicy`
    - `groupAllowFrom` / `allowFrom`
    - `groups` 允许列表条目
    - 提及门控 (`requireMention` + 提及模式)
    - `openclaw.json` 中的重复键 (JSON5): 后续条目会覆盖之前的条目，因此每个作用域保持单个 `groupPolicy`

  </Accordion>

  <Accordion title="Bun 运行时警告">
    WhatsApp 网关运行时应使用 Node。Bun 被标记为与稳定的 WhatsApp/Telegram 网关操作不兼容。
  </Accordion>
</AccordionGroup>

## 配置参考指针

主要参考：

- [配置参考 - WhatsApp](/gateway/configuration-reference#whatsapp)

高信号 WhatsApp 字段：

- access: `dmPolicy`, `allowFrom`, `groupPolicy`, `groupAllowFrom`, `groups`
- delivery: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `sendReadReceipts`, `ackReaction`
- multi-account: `accounts.<id>.enabled`, `accounts.<id>.authDir`, 账户级别重写
- operations: `configWrites`, `debounceMs`, `web.enabled`, `web.heartbeatSeconds`, `web.reconnect.*`
- session behavior: `session.dmScope`, `historyLimit`, `dmHistoryLimit`, `dms.<id>.historyLimit`

## 相关

- [配对](/channels/pairing)
- [通道路由](/channels/channel-routing)
- [多代理路由](/concepts/multi-agent)
- [故障排除](/channels/troubleshooting)