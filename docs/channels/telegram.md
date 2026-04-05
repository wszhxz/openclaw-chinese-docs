---
summary: "Telegram bot support status, capabilities, and configuration"
read_when:
  - Working on Telegram features or webhooks
title: "Telegram"
---
# Telegram (Bot API)

状态：通过 grammY 实现机器人 DM 和群组的 bots 功能，已投入生产环境。长轮询是默认模式；Webhook 模式为可选。

<CardGroup cols={3}>
  <Card title="Pairing" icon="link" href="/channels/pairing">
    Telegram 的默认 DM 策略是配对。
  </Card>
  <Card title="Channel troubleshooting" icon="wrench" href="/channels/troubleshooting">
    跨通道诊断和修复手册。
  </Card>
  <Card title="Gateway configuration" icon="settings" href="/gateway/configuration">
    完整的通道配置模式和示例。
  </Card>
</CardGroup>

## 快速设置

<Steps>
  <Step title="Create the bot token in BotFather">
    Open Telegram and chat with **@BotFather** (confirm the handle is exactly __CODE_BLOCK_0__).

    Run __CODE_BLOCK_1__, follow prompts, and save the token.

  </Step>

  <Step title="Configure token and DM policy">

__CODE_BLOCK_2__

    Env fallback: __CODE_BLOCK_3__ (default account only).
    Telegram does **not** use __CODE_BLOCK_4__; configure token in config/env, then start gateway.

  </Step>

  <Step title="Start gateway and approve first DM">

__CODE_BLOCK_5__

    Pairing codes expire after 1 hour.

  </Step>

  <Step title="Add the bot to a group">
    Add the bot to your group, then set __CODE_BLOCK_6__ and __CODE_BLOCK_7__ to match your access model.
  </Step>
</Steps>

<Note>
Token resolution order is account-aware. In practice, config values win over env fallback, and __CODE_BLOCK_8__ only applies to the default account.
</Note>

## Telegram 端设置

<AccordionGroup>
  <Accordion title="Privacy mode and group visibility">
    Telegram bots default to **Privacy Mode**, which limits what group messages they receive.

    If the bot must see all group messages, either:

    - disable privacy mode via __CODE_BLOCK_9__, or
    - make the bot a group admin.

    When toggling privacy mode, remove + re-add the bot in each group so Telegram applies the change.

  </Accordion>

  <Accordion title="Group permissions">
    Admin status is controlled in Telegram group settings.

    Admin bots receive all group messages, which is useful for always-on group behavior.

  </Accordion>

  <Accordion title="Helpful BotFather toggles">

    - __CODE_BLOCK_10__ to allow/deny group adds
    - __CODE_BLOCK_11__ for group visibility behavior

  </Accordion>
</AccordionGroup>

## 访问控制与激活

<Tabs>
  <Tab title="DM policy">
    __CODE_BLOCK_12__ controls direct message access:

    - __CODE_BLOCK_13__ (default)
    - __CODE_BLOCK_14__ (requires at least one sender ID in __CODE_BLOCK_15__)
    - __CODE_BLOCK_16__ (requires __CODE_BLOCK_17__ to include __CODE_BLOCK_18__)
    - __CODE_BLOCK_19__

    __CODE_BLOCK_20__ accepts numeric Telegram user IDs. __CODE_BLOCK_21__ / __CODE_BLOCK_22__ prefixes are accepted and normalized.
    __CODE_BLOCK_23__ with empty __CODE_BLOCK_24__ blocks all DMs and is rejected by config validation.
    Onboarding accepts __CODE_BLOCK_25__ input and resolves it to numeric IDs.
    If you upgraded and your config contains __CODE_BLOCK_26__ allowlist entries, run __CODE_BLOCK_27__ to resolve them (best-effort; requires a Telegram bot token).
    If you previously relied on pairing-store allowlist files, __CODE_BLOCK_28__ can recover entries into __CODE_BLOCK_29__ in allowlist flows (for example when __CODE_BLOCK_30__ has no explicit IDs yet).

    For one-owner bots, prefer __CODE_BLOCK_31__ with explicit numeric __CODE_BLOCK_32__ IDs to keep access policy durable in config (instead of depending on previous pairing approvals).

    Common confusion: DM pairing approval does not mean "this sender is authorized everywhere".
    Pairing grants DM access only. Group sender authorization still comes from explicit config allowlists.
    If you want "I am authorized once and both DMs and group commands work", put your numeric Telegram user ID in __CODE_BLOCK_33__.

    ### Finding your Telegram user ID

    Safer (no third-party bot):

    1. DM your bot.
    2. Run __CODE_BLOCK_34__.
    3. Read __CODE_BLOCK_35__.

    Official Bot API method:

__CODE_BLOCK_36__

    Third-party method (less private): __CODE_BLOCK_37__ or __CODE_BLOCK_38__.

  </Tab>

  <Tab title="Group policy and allowlists">
    Two controls apply together:

    1. **Which groups are allowed** (__CODE_BLOCK_39__)
       - no __CODE_BLOCK_40__ config:
         - with __CODE_BLOCK_41__: any group can pass group-ID checks
         - with __CODE_BLOCK_42__ (default): groups are blocked until you add __CODE_BLOCK_43__ entries (or __CODE_BLOCK_44__)
       - __CODE_BLOCK_45__ configured: acts as allowlist (explicit IDs or __CODE_BLOCK_46__)

    2. **Which senders are allowed in groups** (__CODE_BLOCK_47__)
       - __CODE_BLOCK_48__
       - __CODE_BLOCK_49__ (default)
       - __CODE_BLOCK_50__

    __CODE_BLOCK_51__ is used for group sender filtering. If not set, Telegram falls back to __CODE_BLOCK_52__.
    __CODE_BLOCK_53__ entries should be numeric Telegram user IDs (__CODE_BLOCK_54__ / __CODE_BLOCK_55__ prefixes are normalized).
    Do not put Telegram group or supergroup chat IDs in __CODE_BLOCK_56__. Negative chat IDs belong under __CODE_BLOCK_57__.
    Non-numeric entries are ignored for sender authorization.
    Security boundary (__CODE_BLOCK_58__): group sender auth does **not** inherit DM pairing-store approvals.
    Pairing stays DM-only. For groups, set __CODE_BLOCK_59__ or per-group/per-topic __CODE_BLOCK_60__.
    If __CODE_BLOCK_61__ is unset, Telegram falls back to config __CODE_BLOCK_62__, not the pairing store.
    Practical pattern for one-owner bots: set your user ID in __CODE_BLOCK_63__, leave __CODE_BLOCK_64__ unset, and allow the target groups under __CODE_BLOCK_65__.
    Runtime note: if __CODE_BLOCK_66__ is completely missing, runtime defaults to fail-closed __CODE_BLOCK_67__ unless __CODE_BLOCK_68__ is explicitly set.

    Example: allow any member in one specific group:

__CODE_BLOCK_69__

    Example: allow only specific users inside one specific group:

__CODE_BLOCK_70__

    <Warning>
      Common mistake: __CODE_BLOCK_71__ is not a Telegram group allowlist.

      - Put negative Telegram group or supergroup chat IDs like __CODE_BLOCK_72__ under __CODE_BLOCK_73__.
      - Put Telegram user IDs like __CODE_BLOCK_74__ under __CODE_BLOCK_75__ when you want to limit which people inside an allowed group can trigger the bot.
      - Use __CODE_BLOCK_76__ only when you want any member of an allowed group to be able to talk to the bot.
    </Warning>

  </Tab>

  <Tab title="Mention behavior">
    Group replies require mention by default.

    Mention can come from:

    - native __CODE_BLOCK_77__ mention, or
    - mention patterns in:
      - __CODE_BLOCK_78__
      - __CODE_BLOCK_79__

    Session-level command toggles:

    - __CODE_BLOCK_80__
    - __CODE_BLOCK_81__

    These update session state only. Use config for persistence.

    Persistent config example:

__CODE_BLOCK_82__

    Getting the group chat ID:

    - forward a group message to __CODE_BLOCK_83__ / __CODE_BLOCK_84__
    - or read __CODE_BLOCK_85__ from __CODE_BLOCK_86__
    - or inspect Bot API __CODE_BLOCK_87__

  </Tab>
</Tabs>

## 运行时行为

- Telegram 由网关进程管理。
- 路由是确定性的：Telegram 入站回复直接返回 Telegram（模型不选择通道）。
- 入站消息标准化到共享通道信封中，包含回复元数据和媒体占位符。
- 群组会话按组 ID 隔离。论坛主题附加 `:topic:<threadId>` 以保持主题隔离。
- DM 消息可以携带 `message_thread_id`；OpenClaw 使用线程感知会话键进行路由，并为回复保留线程 ID。
- 长轮询使用带有每个聊天/每个线程顺序的 grammY runner。整体 runner 接收器并发使用 `agents.defaults.maxConcurrent`。
- Telegram Bot API 不支持已读回执（`sendReadReceipts` 不适用）。

## 功能参考

<AccordionGroup>
  <Accordion title="Live stream preview (message edits)">
    OpenClaw 可以实时流式传输部分回复：

    - 直接聊天：预览消息 + `editMessageText`
    - 群组/主题：预览消息 + `editMessageText`

    要求：

    - `channels.telegram.streaming` 是 `off | partial | block | progress`（默认：`partial`）
    - `progress` 映射到 Telegram 上的 `partial`（兼容跨通道命名）
    - 遗留 `channels.telegram.streamMode` 和布尔值 `streaming` 自动映射

    对于仅文本的回复：

    - DM：OpenClaw 保持相同的预览消息并在原位执行最终编辑（无第二条消息）
    - 群组/主题：OpenClaw 保持相同的预览消息并在原位执行最终编辑（无第二条消息）

    对于复杂回复（例如媒体负载），OpenClaw 回退到正常的最终交付，然后清理预览消息。

    预览流式传输与块流式传输分开。当明确为 Telegram 启用块流式传输时，OpenClaw 跳过预览流以避免双重流式传输。

    如果原生草稿传输不可用/被拒绝，OpenClaw 自动回退到 `sendMessage` + `editMessageText`。

Telegram-only reasoning stream:

    - `/reasoning stream` sends reasoning to the live preview while generating
    - final answer is sent without reasoning text

  </Accordion>

  <Accordion title="Formatting and HTML fallback">
    Outbound text uses Telegram `parse_mode: "HTML"`.

    - Markdown-ish text is rendered to Telegram-safe HTML.
    - Raw model HTML is escaped to reduce Telegram parse failures.
    - If Telegram rejects parsed HTML, OpenClaw retries as plain text.

    Link previews are enabled by default and can be disabled with `channels.telegram.linkPreview: false`.

  </Accordion>

  <Accordion title="Native commands and custom commands">
    Telegram command menu registration is handled at startup with `setMyCommands`.

    Native command defaults:

    - `commands.native: "auto"` enables native commands for Telegram

    Add custom command menu entries:

```json5
{
  channels: {
    telegram: {
      customCommands: [
        { command: "backup", description: "Git backup" },
        { command: "generate", description: "Create an image" },
      ],
    },
  },
}
```

    Rules:

    - names are normalized (strip leading `/`, lowercase)
    - valid pattern: `a-z`, `0-9`, `_`, length `1..32`
    - custom commands cannot override native commands
    - conflicts/duplicates are skipped and logged

    Notes:

    - custom commands are menu entries only; they do not auto-implement behavior
    - plugin/skill commands can still work when typed even if not shown in Telegram menu

    If native commands are disabled, built-ins are removed. Custom/plugin commands may still register if configured.

    Common setup failures:

    - `setMyCommands failed` with `BOT_COMMANDS_TOO_MUCH` means the Telegram menu still overflowed after trimming; reduce plugin/skill/custom commands or disable `channels.telegram.commands.native`.
    - `setMyCommands failed` with network/fetch errors usually means outbound DNS/HTTPS to `api.telegram.org` is blocked.

    ### Device pairing commands (`device-pair` plugin)

    When the `device-pair` plugin is installed:

    1. `/pair` generates setup code
    2. paste code in iOS app
    3. `/pair pending` lists pending requests (including role/scopes)
    4. approve the request:
       - `/pair approve <requestId>` for explicit approval
       - `/pair approve` when there is only one pending request
       - `/pair approve latest` for most recent

    The setup code carries a short-lived bootstrap token. Built-in bootstrap handoff keeps the primary node token at `scopes: []`; any handed-off operator token stays bounded to `operator.approvals`, `operator.read`, `operator.talk.secrets`, and `operator.write`. Bootstrap scope checks are role-prefixed, so that operator allowlist only satisfies operator requests; non-operator roles still need scopes under their own role prefix.

    If a device retries with changed auth details (for example role/scopes/public key), the previous pending request is superseded and the new request uses a different `requestId`. Re-run `/pair pending` before approving.

    More details: [Pairing](/channels/pairing#pair-via-telegram-recommended-for-ios).

  </Accordion>

  <Accordion title="Inline buttons">
    Configure inline keyboard scope:

```json5
{
  channels: {
    telegram: {
      capabilities: {
        inlineButtons: "allowlist",
      },
    },
  },
}
```

    Per-account override:

```json5
{
  channels: {
    telegram: {
      accounts: {
        main: {
          capabilities: {
            inlineButtons: "allowlist",
          },
        },
      },
    },
  },
}
```

    Scopes:

    - `off`
    - `dm`
    - `group`
    - `all`
    - `allowlist` (default)

    Legacy `capabilities: ["inlineButtons"]` maps to `inlineButtons: "all"`.

    Message action example:

```json5
{
  action: "send",
  channel: "telegram",
  to: "123456789",
  message: "Choose an option:",
  buttons: [
    [
      { text: "Yes", callback_data: "yes" },
      { text: "No", callback_data: "no" },
    ],
    [{ text: "Cancel", callback_data: "cancel" }],
  ],
}
```

    Callback clicks are passed to the agent as text:
    `callback_data: <value>`

  </Accordion>

  <Accordion title="Telegram message actions for agents and automation">
    Telegram tool actions include:

    - `sendMessage` (`to`, `content`, optional `mediaUrl`, `replyToMessageId`, `messageThreadId`)
    - `react` (`chatId`, `messageId`, `emoji`)
    - `deleteMessage` (`chatId`, `messageId`)
    - `editMessage` (`chatId`, `messageId`, `content`)
    - `createForumTopic` (`chatId`, `name`, optional `iconColor`, `iconCustomEmojiId`)

    Channel message actions expose ergonomic aliases (`send`, `react`, `delete`, `edit`, `sticker`, `sticker-search`, `topic-create`).

    Gating controls:

    - `channels.telegram.actions.sendMessage`
    - `channels.telegram.actions.deleteMessage`
    - `channels.telegram.actions.reactions`
    - `channels.telegram.actions.sticker` (default: disabled)

    Note: `edit` and `topic-create` are currently enabled by default and do not have separate `channels.telegram.actions.*` toggles.
    Runtime sends use the active config/secrets snapshot (startup/reload), so action paths do not perform ad-hoc SecretRef re-resolution per send.

    Reaction removal semantics: [/tools/reactions](/tools/reactions)

  </Accordion>

  <Accordion title="Reply threading tags">
    Telegram supports explicit reply threading tags in generated output:

    - `[[reply_to_current]]` replies to the triggering message
    - `[[reply_to:<id>]]` replies to a specific Telegram message ID

    `channels.telegram.replyToMode` controls handling:

    - `off` (default)
    - `first`
    - `all`

    Note: `off` disables implicit reply threading. Explicit `[[reply_to_*]]` tags are still honored.

  </Accordion>

  <Accordion title="Forum topics and thread behavior">
    Forum supergroups:

    - topic session keys append `:topic:<threadId>`
    - replies and typing target the topic thread
    - topic config path:
      `channels.telegram.groups.<chatId>.topics.<threadId>`

    General topic (`threadId=1`) special-case:

    - message sends omit `message_thread_id` (Telegram rejects `sendMessage(...thread_id=1)`)
    - typing actions still include `message_thread_id`

    Topic inheritance: topic entries inherit group settings unless overridden (`requireMention`, `allowFrom`, `skills`, `systemPrompt`, `enabled`, `groupPolicy`).
    `agentId` is topic-only and does not inherit from group defaults.

    **Per-topic agent routing**: Each topic can route to a different agent by setting `agentId` in the topic config. This gives each topic its own isolated workspace, memory, and session. Example:

    ```json5
    {
      channels: {
        telegram: {
          groups: {
            "-1001234567890": {
              topics: {
                "1": { agentId: "main" },      // General topic → main agent
                "3": { agentId: "zu" },        // Dev topic → zu agent
                "5": { agentId: "coder" }      // Code review → coder agent
              }
            }
          }
        }
      }
    }
    ```

    Each topic then has its own session key: `agent:zu:telegram:group:-1001234567890:topic:3`

    **Persistent ACP topic binding**: Forum topics can pin ACP harness sessions through top-level typed ACP bindings:

    - `bindings[]` with `type: "acp"` and `match.channel: "telegram"`

    Example:

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
            channel: "telegram",
            accountId: "default",
            peer: { kind: "group", id: "-1001234567890:topic:42" },
          },
        },
      ],
      channels: {
        telegram: {
          groups: {
            "-1001234567890": {
              topics: {
                "42": {
                  requireMention: false,
                },
              },
            },
          },
        },
      },
    }
    ```

    This is currently scoped to forum topics in groups and supergroups.

    **Thread-bound ACP spawn from chat**:

    - `/acp spawn <agent> --thread here|auto` can bind the current Telegram topic to a new ACP session.
    - Follow-up topic messages route to the bound ACP session directly (no `/acp steer` required).
    - OpenClaw pins the spawn confirmation message in-topic after a successful bind.
    - Requires `channels.telegram.threadBindings.spawnAcpSessions=true`.

    Template context includes:

    - `MessageThreadId`
    - `IsForum`

    DM thread behavior:

    - private chats with `message_thread_id` keep DM routing but use thread-aware session keys/reply targets.

  </Accordion>

  <Accordion title="Audio, video, and stickers">
    ### Audio messages

    Telegram distinguishes voice notes vs audio files.

    - default: audio file behavior
    - tag `[[audio_as_voice]]` in agent reply to force voice-note send

    Message action example:

```json5
{
  action: "send",
  channel: "telegram",
  to: "123456789",
  media: "https://example.com/voice.ogg",
  asVoice: true,
}
```

    ### Video messages

    Telegram distinguishes video files vs video notes.

    Message action example:

```json5
{
  action: "send",
  channel: "telegram",
  to: "123456789",
  media: "https://example.com/video.mp4",
  asVideoNote: true,
}
```

    Video notes do not support captions; provided message text is sent separately.

    ### Stickers

    Inbound sticker handling:

    - static WEBP: downloaded and processed (placeholder `<media:sticker>`)
    - animated TGS: skipped
    - video WEBM: skipped

Sticker context fields:

    - `Sticker.emoji`
    - `Sticker.setName`
    - `Sticker.fileId`
    - `Sticker.fileUniqueId`
    - `Sticker.cachedDescription`

    Sticker cache file:

    - `~/.openclaw/telegram/sticker-cache.json`

    Stickers are described once (when possible) and cached to reduce repeated vision calls.

    Enable sticker actions:

```json5
{
  channels: {
    telegram: {
      actions: {
        sticker: true,
      },
    },
  },
}
```

    Send sticker action:

```json5
{
  action: "sticker",
  channel: "telegram",
  to: "123456789",
  fileId: "CAACAgIAAxkBAAI...",
}
```

    Search cached stickers:

```json5
{
  action: "sticker-search",
  channel: "telegram",
  query: "cat waving",
  limit: 5,
}
```

  </Accordion>

  <Accordion title="反应通知">
    Telegram reactions arrive as `message_reaction` updates (separate from message payloads).

    When enabled, OpenClaw enqueues system events like:

    - `Telegram reaction added: 👍 by Alice (@alice) on msg 42`

    Config:

    - `channels.telegram.reactionNotifications`: `off | own | all` (default: `own`)
    - `channels.telegram.reactionLevel`: `off | ack | minimal | extensive` (default: `minimal`)

    Notes:

    - `own` means user reactions to bot-sent messages only (best-effort via sent-message cache).
    - Reaction events still respect Telegram access controls (`dmPolicy`, `allowFrom`, `groupPolicy`, `groupAllowFrom`); unauthorized senders are dropped.
    - Telegram does not provide thread IDs in reaction updates.
      - non-forum groups route to group chat session
      - forum groups route to the group general-topic session (`:topic:1`), not the exact originating topic

    `allowed_updates` for polling/webhook include `message_reaction` automatically.

  </Accordion>

  <Accordion title="确认反馈">
    `ackReaction` sends an acknowledgement emoji while OpenClaw is processing an inbound message.

    Resolution order:

    - `channels.telegram.accounts.<accountId>.ackReaction`
    - `channels.telegram.ackReaction`
    - `messages.ackReaction`
    - agent identity emoji fallback (`agents.list[].identity.emoji`, else "👀")

    Notes:

    - Telegram expects unicode emoji (for example "👀").
    - Use `""` to disable the reaction for a channel or account.

  </Accordion>

  <Accordion title="Config writes from Telegram events and commands">
    Channel config writes are enabled by default (`configWrites !== false`).

    Telegram-triggered writes include:

    - group migration events (`migrate_to_chat_id`) to update `channels.telegram.groups`
    - `/config set` and `/config unset` (requires command enablement)

    Disable:

```json5
{
  channels: {
    telegram: {
      configWrites: false,
    },
  },
}
```

  </Accordion>

  <Accordion title="长轮询与 Webhook">
    Default: long polling.

    Webhook mode:

    - set `channels.telegram.webhookUrl`
    - set `channels.telegram.webhookSecret` (required when webhook URL is set)
    - optional `channels.telegram.webhookPath` (default `/telegram-webhook`)
    - optional `channels.telegram.webhookHost` (default `127.0.0.1`)
    - optional `channels.telegram.webhookPort` (default `8787`)

    Default local listener for webhook mode binds to `127.0.0.1:8787`.

    If your public endpoint differs, place a reverse proxy in front and point `webhookUrl` at the public URL.
    Set `webhookHost` (for example `0.0.0.0`) when you intentionally need external ingress.

  </Accordion>

  <Accordion title="Limits, retry, and CLI targets">
    - `channels.telegram.textChunkLimit` default is 4000.
    - `channels.telegram.chunkMode="newline"` prefers paragraph boundaries (blank lines) before length splitting.
    - `channels.telegram.mediaMaxMb` (default 100) caps inbound and outbound Telegram media size.
    - `channels.telegram.timeoutSeconds` overrides Telegram API client timeout (if unset, grammY default applies).
    - group context history uses `channels.telegram.historyLimit` or `messages.groupChat.historyLimit` (default 50); `0` disables.
    - reply/quote/forward supplemental context is currently passed as received.
    - Telegram allowlists primarily gate who can trigger the agent, not a full supplemental-context redaction boundary.
    - DM history controls:
      - `channels.telegram.dmHistoryLimit`
      - `channels.telegram.dms["<user_id>"].historyLimit`
    - `channels.telegram.retry` config applies to Telegram send helpers (CLI/tools/actions) for recoverable outbound API errors.

    CLI send target can be numeric chat ID or username:

```bash
openclaw message send --channel telegram --target 123456789 --message "hi"
openclaw message send --channel telegram --target @name --message "hi"
```

    Telegram polls use `openclaw message poll` and support forum topics:

```bash
openclaw message poll --channel telegram --target 123456789 \
  --poll-question "Ship it?" --poll-option "Yes" --poll-option "No"
openclaw message poll --channel telegram --target -1001234567890:topic:42 \
  --poll-question "Pick a time" --poll-option "10am" --poll-option "2pm" \
  --poll-duration-seconds 300 --poll-public
```

    Telegram-only poll flags:

    - `--poll-duration-seconds` (5-600)
    - `--poll-anonymous`
    - `--poll-public`
    - `--thread-id` for forum topics (or use a `:topic:` target)

    Telegram send also supports:

    - `--buttons` for inline keyboards when `channels.telegram.capabilities.inlineButtons` allows it
    - `--force-document` to send outbound images and GIFs as documents instead of compressed photo or animated-media uploads

    Action gating:

    - `channels.telegram.actions.sendMessage=false` disables outbound Telegram messages, including polls
    - `channels.telegram.actions.poll=false` disables Telegram poll creation while leaving regular sends enabled

  </Accordion>

  <Accordion title="Telegram 中的执行审批">
    Telegram supports exec approvals in approver DMs and can optionally post approval prompts in the originating chat or topic.

    Config path:

    - `channels.telegram.execApprovals.enabled`
    - `channels.telegram.execApprovals.approvers` (optional; falls back to numeric owner IDs inferred from `allowFrom` and direct `defaultTo` when possible)
    - `channels.telegram.execApprovals.target` (`dm` | `channel` | `both`, default: `dm`)
    - `agentFilter`, `sessionFilter`

    Approvers must be numeric Telegram user IDs. Telegram auto-enables native exec approvals when `enabled` is unset or `"auto"` and at least one approver can be resolved, either from `execApprovals.approvers` or from the account's numeric owner config (`allowFrom` and direct-message `defaultTo`). Set `enabled: false` to disable Telegram as a native approval client explicitly. Approval requests otherwise fall back to other configured approval routes or the exec approval fallback policy.

    Telegram also renders the shared approval buttons used by other chat channels. The native Telegram adapter mainly adds approver DM routing, channel/topic fanout, and typing hints before delivery.
    When those buttons are present, they are the primary approval UX; OpenClaw
    should only include a manual `/approve` command when the tool result says
    chat approvals are unavailable or manual approval is the only path.

    Delivery rules:

    - `target: "dm"` sends approval prompts only to resolved approver DMs
    - `target: "channel"` sends the prompt back to the originating Telegram chat/topic
    - `target: "both"` sends to approver DMs and the originating chat/topic

    Only resolved approvers can approve or deny. Non-approvers cannot use `/approve` and cannot use Telegram approval buttons.

    Approval resolution behavior:

    - IDs prefixed with `plugin:` always resolve through plugin approvals.
    - Other approval IDs try `exec.approval.resolve` first.
    - If Telegram is also authorized for plugin approvals and the gateway says
      the exec approval is unknown/expired, Telegram retries once through
      `plugin.approval.resolve`.
    - Real exec approval denials/errors do not silently fall through to plugin
      approval resolution.

    Channel delivery shows the command text in the chat, so only enable `channel` or `both` in trusted groups/topics. When the prompt lands in a forum topic, OpenClaw preserves the topic for both the approval prompt and the post-approval follow-up. Exec approvals expire after 30 minutes by default.

    Inline approval buttons also depend on `channels.telegram.capabilities.inlineButtons` allowing the target surface (`dm`, `group`, or `all`).

    Related docs: [Exec approvals](/tools/exec-approvals)

  </Accordion>
</AccordionGroup>

## 错误回复控制

When the agent encounters a delivery or provider error, Telegram can either reply with the error text or suppress it. Two config keys control this behavior:

| 键                                 | 值            | 默认值 | 描述                                                                                     |
| ----------------------------------- | ----------------- | ------- | ----------------------------------------------------------------------------------------------- |
| `channels.telegram.errorPolicy`     | `reply`, `silent` | `reply` | `reply` 向聊天发送友好的错误消息。`silent` 完全抑制错误回复。|
| `channels.telegram.errorCooldownMs` | number (ms)       | `60000` | Minimum time between error replies to the same chat. Prevents error spam during outages.        |

Per-account, per-group, and per-topic overrides are supported (same inheritance as other Telegram config keys).

```json5
{
  channels: {
    telegram: {
      errorPolicy: "reply",
      errorCooldownMs: 120000,
      groups: {
        "-1001234567890": {
          errorPolicy: "silent", // suppress errors in this group
        },
      },
    },
  },
}
```

## 故障排除

<AccordionGroup>
  <Accordion title="Bot does not respond to non mention group messages">

    - If __CODE_BLOCK_0__, Telegram privacy mode must allow full visibility.
      - BotFather: __CODE_BLOCK_1__ -> Disable
      - then remove + re-add bot to group
    - __CODE_BLOCK_2__ warns when config expects unmentioned group messages.
    - __CODE_BLOCK_3__ can check explicit numeric group IDs; wildcard __CODE_BLOCK_4__ cannot be membership-probed.
    - quick session test: __CODE_BLOCK_5__.

  </Accordion>

  <Accordion title="Bot not seeing group messages at all">

    - when __CODE_BLOCK_6__ exists, group must be listed (or include __CODE_BLOCK_7__)
    - verify bot membership in group
    - review logs: __CODE_BLOCK_8__ for skip reasons

  </Accordion>

  <Accordion title="Commands work partially or not at all">

    - authorize your sender identity (pairing and/or numeric __CODE_BLOCK_9__)
    - command authorization still applies even when group policy is __CODE_BLOCK_10__
    - __CODE_BLOCK_11__ with __CODE_BLOCK_12__ means the native menu has too many entries; reduce plugin/skill/custom commands or disable native menus
    - __CODE_BLOCK_13__ with network/fetch errors usually indicates DNS/HTTPS reachability issues to __CODE_BLOCK_14__

  </Accordion>

  <Accordion title="Polling or network instability">

    - Node 22+ + custom fetch/proxy can trigger immediate abort behavior if AbortSignal types mismatch.
    - Some hosts resolve __CODE_BLOCK_15__ to IPv6 first; broken IPv6 egress can cause intermittent Telegram API failures.
    - If logs include __CODE_BLOCK_16__ or __CODE_BLOCK_17__, OpenClaw now retries these as recoverable network errors.
    - On VPS hosts with unstable direct egress/TLS, route Telegram API calls through __CODE_BLOCK_18__:

__CODE_BLOCK_19__

    - Node 22+ defaults to __CODE_BLOCK_20__ (except WSL2) and __CODE_BLOCK_21__.
    - If your host is WSL2 or explicitly works better with IPv4-only behavior, force family selection:

__CODE_BLOCK_22__

    - RFC 2544 benchmark-range answers (__CODE_BLOCK_23__) are already allowed
      for Telegram media downloads by default. If a trusted fake-IP or
      transparent proxy rewrites __CODE_BLOCK_24__ to some other
      private/internal/special-use address during media downloads, you can opt
      in to the Telegram-only bypass:

__CODE_BLOCK_25__

    - The same opt-in is available per account at
      __CODE_BLOCK_26__.
    - If your proxy resolves Telegram media hosts into __CODE_BLOCK_27__, leave the
      dangerous flag off first. Telegram media already allows the RFC 2544
      benchmark range by default.

    <Warning>
      __CODE_BLOCK_28__ weakens Telegram
      media SSRF protections. Use it only for trusted operator-controlled proxy
      environments such as Clash, Mihomo, or Surge fake-IP routing when they
      synthesize private or special-use answers outside the RFC 2544 benchmark
      range. Leave it off for normal public internet Telegram access.
    </Warning>

    - Environment overrides (temporary):
      - __CODE_BLOCK_29__
      - __CODE_BLOCK_30__
      - __CODE_BLOCK_31__
    - Validate DNS answers:

__CODE_BLOCK_32__

  </Accordion>
</AccordionGroup>

更多帮助：[频道故障排除](/channels/troubleshooting)。

## Telegram 配置参考指引

主要参考：

- `channels.telegram.enabled`: 启用/禁用频道启动。
- `channels.telegram.botToken`: bot token（BotFather）。
- `channels.telegram.tokenFile`: 从常规文件路径读取令牌。拒绝符号链接。
- `channels.telegram.dmPolicy`: `pairing | allowlist | open | disabled`（默认值：pairing）。
- `channels.telegram.allowFrom`: DM 白名单（数字格式的 Telegram 用户 ID）。`allowlist` 至少需要一个发送者 ID。`open` 需要 `"*"`。`openclaw doctor --fix` 可以将旧的 `@username` 条目解析为 ID，并可以在白名单迁移流程中从 pairing-store 文件中恢复白名单条目。
- `channels.telegram.actions.poll`: 启用或禁用 Telegram 投票创建（默认：已启用；仍需 `sendMessage`）。
- `channels.telegram.defaultTo`: CLI `--deliver` 在未提供显式 `--reply-to` 时使用的默认 Telegram 目标。
- `channels.telegram.groupPolicy`: `open | allowlist | disabled`（默认值：allowlist）。
- `channels.telegram.groupAllowFrom`: 群组发送者白名单（数字格式的 Telegram 用户 ID）。`openclaw doctor --fix` 可以将旧的 `@username` 条目解析为 ID。非数字条目在认证时被忽略。群组认证不使用 DM pairing-store 回退 (`2026.2.25+`)。
- 多账户优先级：
  - 当配置了两个或多个账户 ID 时，设置 `channels.telegram.defaultAccount`（或包含 `channels.telegram.accounts.default`）以明确默认路由。
  - 如果均未设置，OpenClaw 将回退到第一个标准化账户 ID，并且 `openclaw doctor` 发出警告。
  - `channels.telegram.accounts.default.allowFrom` 和 `channels.telegram.accounts.default.groupAllowFrom` 仅适用于 `default` 账户。
  - 当账户级值未设置时，命名账户继承 `channels.telegram.allowFrom` 和 `channels.telegram.groupAllowFrom`。
  - 命名账户不继承 `channels.telegram.accounts.default.allowFrom` / `groupAllowFrom`。
- `channels.telegram.groups`: 按群组默认值 + 白名单（使用 `"*"` 进行全局默认值）。
  - `channels.telegram.groups.<id>.groupPolicy`: 按群组的 groupPolicy 覆盖（`open | allowlist | disabled`）。
  - `channels.telegram.groups.<id>.requireMention`: @提及限制默认值。
  - `channels.telegram.groups.<id>.skills`: 技能过滤器（省略 = 所有技能，空 = 无）。
  - `channels.telegram.groups.<id>.allowFrom`: 按群组发送者白名单覆盖。
  - `channels.telegram.groups.<id>.systemPrompt`: 群组的额外系统提示。
  - `channels.telegram.groups.<id>.enabled`: 当 `false` 时禁用该群组。
  - `channels.telegram.groups.<id>.topics.<threadId>.*`: 按主题覆盖（群组字段 + 仅主题 `agentId`）。
  - `channels.telegram.groups.<id>.topics.<threadId>.agentId`: 将此主题路由到特定代理（覆盖群组级别和绑定路由）。
- `channels.telegram.groups.<id>.topics.<threadId>.groupPolicy`: 按主题的 groupPolicy 覆盖（`open | allowlist | disabled`）。
- `channels.telegram.groups.<id>.topics.<threadId>.requireMention`: 按主题提及限制覆盖。
- 顶级 `bindings[]` 包含 `type: "acp"` 和 `match.peer.id` 中的规范主题 ID `chatId:topic:topicId`：持久化 ACP 主题绑定字段（参见 [ACP Agents](/tools/acp-agents#channel-specific-settings)）。
- `channels.telegram.direct.<id>.topics.<threadId>.agentId`: 将 DM 主题路由到特定代理（与论坛主题行为相同）。
- `channels.telegram.execApprovals.enabled`: 启用 Telegram 作为此账户的基于聊天的执行批准客户端。
- `channels.telegram.execApprovals.approvers`: 允许批准或拒绝执行请求的 Telegram 用户 ID。当 `channels.telegram.allowFrom` 或直接 `channels.telegram.defaultTo` 已标识所有者时为可选。
- `channels.telegram.execApprovals.target`: `dm | channel | both`（默认值：`dm`）。`channel` 和 `both` 保留来源 Telegram 主题（如果存在）。
- `channels.telegram.execApprovals.agentFilter`: 转发批准提示的可选代理 ID 过滤器。
- `channels.telegram.execApprovals.sessionFilter`: 转发批准提示的可选会话密钥过滤器（子字符串或正则表达式）。
- `channels.telegram.accounts.<account>.execApprovals`: 针对 Telegram 执行批准路由和批准者授权的账户级覆盖。
- `channels.telegram.capabilities.inlineButtons`: `off | dm | group | all | allowlist`（默认值：allowlist）。
- `channels.telegram.accounts.<account>.capabilities.inlineButtons`: 账户级覆盖。
- `channels.telegram.commands.nativeSkills`: 启用/禁用 Telegram 原生技能命令。
- `channels.telegram.replyToMode`: `off | first | all`（默认值：`off`）。
- `channels.telegram.textChunkLimit`: 出站分块大小（字符数）。
- `channels.telegram.chunkMode`: `length`（默认值）或 `newline` 以便在长度分块之前在空白行（段落边界）处拆分。
- `channels.telegram.linkPreview`: 切换出站消息的链接预览（默认值：true）。
- `channels.telegram.streaming`: `off | partial | block | progress`（实时流预览；默认值：`partial`；`progress` 映射到 `partial`；`block` 是旧版预览模式兼容性）。Telegram 预览流使用单个预览消息并在原地编辑。
- `channels.telegram.mediaMaxMb`: 入站/出站 Telegram 媒体上限（MB，默认值：100）。
- `channels.telegram.retry`: Telegram 发送助手（CLI/tools/actions）在可恢复的出站 API 错误上的重试策略（尝试次数、最小延迟毫秒、最大延迟毫秒、抖动）。
- `channels.telegram.network.autoSelectFamily`: 覆盖 Node autoSelectFamily（true=启用，false=禁用）。Node 22+ 默认为启用，WSL2 默认为禁用。
- `channels.telegram.network.dnsResultOrder`: 覆盖 DNS 结果顺序（`ipv4first` 或 `verbatim`）。Node 22+ 默认为 `ipv4first`。
- `channels.telegram.network.dangerouslyAllowPrivateNetwork`: 危险的选择加入项，用于受信任的假 IP 或透明代理环境，其中 Telegram 媒体下载将 `api.telegram.org` 解析为私有/内部/特殊用途地址，超出默认 RFC 2544 基准范围允许值。
- `channels.telegram.proxy`: Bot API 调用的代理 URL（SOCKS/HTTP）。
- `channels.telegram.webhookUrl`: 启用 Webhook 模式（需要 `channels.telegram.webhookSecret`）。
- `channels.telegram.webhookSecret`: Webhook 密钥（设置 webhookUrl 时需要）。
- `channels.telegram.webhookPath`: 本地 Webhook 路径（默认值 `/telegram-webhook`）。
- `channels.telegram.webhookHost`: 本地 Webhook 绑定主机（默认值 `127.0.0.1`）。
- `channels.telegram.webhookPort`: 本地 Webhook 绑定端口（默认值 `8787`）。
- `channels.telegram.actions.reactions`: 限制 Telegram 工具反应。
- `channels.telegram.actions.sendMessage`: 限制 Telegram 工具消息发送。
- `channels.telegram.actions.deleteMessage`: 限制 Telegram 工具消息删除。
- `channels.telegram.actions.sticker`: 限制 Telegram 贴纸操作 — 发送和搜索（默认值：false）。
- `channels.telegram.reactionNotifications`: `off | own | all` — 控制哪些反应触发系统事件（未设置时默认值：`own`）。
- `channels.telegram.reactionLevel`: `off | ack | minimal | extensive` — 控制代理的反应能力（未设置时默认值：`minimal`）。
- `channels.telegram.errorPolicy`: `reply | silent` — 控制错误回复行为（默认值：`reply`）。支持账户/群组/主题覆盖。
- `channels.telegram.errorCooldownMs`: 向同一聊天发送错误回复之间的最小毫秒数（默认值：`60000`）。防止中断期间的错误垃圾信息。

- [配置参考 - Telegram](/gateway/configuration-reference#telegram)

Telegram 特定高信号字段：

- 启动/认证：`enabled`, `botToken`, `tokenFile`, `accounts.*` (`tokenFile` 必须指向常规文件；拒绝符号链接)
- 访问控制：`dmPolicy`, `allowFrom`, `groupPolicy`, `groupAllowFrom`, `groups`, `groups.*.topics.*`, 顶级 `bindings[]` (`type: "acp"`)
- 执行批准：`execApprovals`, `accounts.*.execApprovals`
- 命令/菜单：`commands.native`, `commands.nativeSkills`, `customCommands`
- 线程/回复：`replyToMode`
- 流式传输：`streaming`（预览），`blockStreaming`
- 格式/交付：`textChunkLimit`, `chunkMode`, `linkPreview`, `responsePrefix`
- 媒体/网络：`mediaMaxMb`, `timeoutSeconds`, `retry`, `network.autoSelectFamily`, `network.dangerouslyAllowPrivateNetwork`, `proxy`
- Webhook：`webhookUrl`, `webhookSecret`, `webhookPath`, `webhookHost`
- 操作/功能：`capabilities.inlineButtons`, `actions.sendMessage|editMessage|deleteMessage|reactions|sticker`
- 反应：`reactionNotifications`, `reactionLevel`
- 错误：`errorPolicy`, `errorCooldownMs`
- 写入/历史：`configWrites`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`

## 相关

- [配对](/channels/pairing)
- [群组](/channels/groups)
- [安全](/gateway/security)
- [频道路由](/channels/channel-routing)
- [多代理路由](/concepts/multi-agent)
- [故障排除](/channels/troubleshooting)