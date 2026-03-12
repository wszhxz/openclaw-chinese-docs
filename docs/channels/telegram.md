---
summary: "Telegram bot support status, capabilities, and configuration"
read_when:
  - Working on Telegram features or webhooks
title: "Telegram"
---
# Telegram（Bot API）

状态：已具备生产就绪能力，支持通过 grammY 与机器人进行私聊（DM）及群组通信。长轮询为默认模式；Webhook 模式为可选。

<CardGroup cols={3}>
  <Card title="配对" icon="link" href="/channels/pairing">
    Telegram 的默认私聊策略为配对。
  </Card>
  <Card title="频道故障排查" icon="wrench" href="/channels/troubleshooting">
    跨频道诊断与修复操作手册。
  </Card>
  <Card title="网关配置" icon="settings" href="/gateway/configuration">
    完整的频道配置模式与示例。
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

## 访问控制与启用

<Tabs>
  <Tab title="DM policy">
    __CODE_BLOCK_12__ controls direct message access:

    - __CODE_BLOCK_13__ (default)
    - __CODE_BLOCK_14__ (requires at least one sender ID in __CODE_BLOCK_15__)
    - __CODE_BLOCK_16__ (requires __CODE_BLOCK_17__ to include __CODE_BLOCK_18__)
    - __CODE_BLOCK_19__

    __CODE_BLOCK_20__ accepts numeric Telegram user IDs. __CODE_BLOCK_21__ / __CODE_BLOCK_22__ prefixes are accepted and normalized.
    __CODE_BLOCK_23__ with empty __CODE_BLOCK_24__ blocks all DMs and is rejected by config validation.
    The onboarding wizard accepts __CODE_BLOCK_25__ input and resolves it to numeric IDs.
    If you upgraded and your config contains __CODE_BLOCK_26__ allowlist entries, run __CODE_BLOCK_27__ to resolve them (best-effort; requires a Telegram bot token).
    If you previously relied on pairing-store allowlist files, __CODE_BLOCK_28__ can recover entries into __CODE_BLOCK_29__ in allowlist flows (for example when __CODE_BLOCK_30__ has no explicit IDs yet).

    For one-owner bots, prefer __CODE_BLOCK_31__ with explicit numeric __CODE_BLOCK_32__ IDs to keep access policy durable in config (instead of depending on previous pairing approvals).

    ### Finding your Telegram user ID

    Safer (no third-party bot):

    1. DM your bot.
    2. Run __CODE_BLOCK_33__.
    3. Read __CODE_BLOCK_34__.

    Official Bot API method:

__CODE_BLOCK_35__

    Third-party method (less private): __CODE_BLOCK_36__ or __CODE_BLOCK_37__.

  </Tab>

  <Tab title="Group policy and allowlists">
    Two controls apply together:

    1. **Which groups are allowed** (__CODE_BLOCK_38__)
       - no __CODE_BLOCK_39__ config:
         - with __CODE_BLOCK_40__: any group can pass group-ID checks
         - with __CODE_BLOCK_41__ (default): groups are blocked until you add __CODE_BLOCK_42__ entries (or __CODE_BLOCK_43__)
       - __CODE_BLOCK_44__ configured: acts as allowlist (explicit IDs or __CODE_BLOCK_45__)

    2. **Which senders are allowed in groups** (__CODE_BLOCK_46__)
       - __CODE_BLOCK_47__
       - __CODE_BLOCK_48__ (default)
       - __CODE_BLOCK_49__

    __CODE_BLOCK_50__ is used for group sender filtering. If not set, Telegram falls back to __CODE_BLOCK_51__.
    __CODE_BLOCK_52__ entries should be numeric Telegram user IDs (__CODE_BLOCK_53__ / __CODE_BLOCK_54__ prefixes are normalized).
    Non-numeric entries are ignored for sender authorization.
    Security boundary (__CODE_BLOCK_55__): group sender auth does **not** inherit DM pairing-store approvals.
    Pairing stays DM-only. For groups, set __CODE_BLOCK_56__ or per-group/per-topic __CODE_BLOCK_57__.
    Runtime note: if __CODE_BLOCK_58__ is completely missing, runtime defaults to fail-closed __CODE_BLOCK_59__ unless __CODE_BLOCK_60__ is explicitly set.

    Example: allow any member in one specific group:

__CODE_BLOCK_61__

  </Tab>

  <Tab title="Mention behavior">
    Group replies require mention by default.

    Mention can come from:

    - native __CODE_BLOCK_62__ mention, or
    - mention patterns in:
      - __CODE_BLOCK_63__
      - __CODE_BLOCK_64__

    Session-level command toggles:

    - __CODE_BLOCK_65__
    - __CODE_BLOCK_66__

    These update session state only. Use config for persistence.

    Persistent config example:

__CODE_BLOCK_67__

    Getting the group chat ID:

    - forward a group message to __CODE_BLOCK_68__ / __CODE_BLOCK_69__
    - or read __CODE_BLOCK_70__ from __CODE_BLOCK_71__
    - or inspect Bot API __CODE_BLOCK_72__

  </Tab>
</Tabs>

## 运行时行为

- Telegram 由网关进程托管。
- 路由具有确定性：Telegram 入站回复将原路返回至 Telegram（模型不参与通道选择）。
- 入站消息被标准化为共享通道信封格式，包含回复元数据和媒体占位符。
- 群组会话按群组 ID 隔离。论坛主题附加 `:topic:<threadId>` 以保持主题隔离。
- 私聊消息可携带 `message_thread_id`；OpenClaw 使用线程感知的会话密钥对其进行路由，并在回复中保留线程 ID。
- 长轮询使用 grammY runner，并支持每聊天/每线程序列化。整体 runner sink 并发度使用 `agents.defaults.maxConcurrent`。
- Telegram Bot API 不支持已读回执（`sendReadReceipts` 不适用）。

## 功能参考

<AccordionGroup>
  <Accordion title="实时流预览（原生草稿 + 消息编辑）">
    OpenClaw 可实时流式传输部分回复：

    - 私聊：通过 `sendMessageDraft` 实现 Telegram 原生草稿流式传输
    - 群组/主题：预览消息 + `editMessageText`

    要求：

    - `channels.telegram.streaming` 为 `off | partial | block | progress`（默认值：`partial`）
    - `progress` 映射为 Telegram 上的 `partial`（兼容跨频道命名）
    - 旧版 `channels.telegram.streamMode` 及布尔型 `streaming` 值将自动映射

    Telegram 已于 Bot API 9.5（2026 年 3 月 1 日）为所有机器人启用 `sendMessageDraft`。

    对于纯文本回复：

    - 私聊：OpenClaw 就地更新草稿（不额外发送预览消息）
    - 群组/主题：OpenClaw 复用同一预览消息，并最终就地编辑（不发送第二条消息）

    对于复杂回复（例如含媒体载荷），OpenClaw 回退至常规最终投递，随后清理预览消息。

    预览流式传输与分块流式传输相互独立。当显式为 Telegram 启用分块流式传输时，OpenClaw 将跳过预览流，避免双重流式传输。

    若原生草稿传输不可用或被拒绝，OpenClaw 将自动回退至 `sendMessage` + `editMessageText`。

    Telegram 专属推理流：

    - `/reasoning stream` 在生成过程中将推理内容发送至实时预览
    - 最终答案不含推理文本

  </Accordion>

  <Accordion title="格式化与 HTML 回退">
    出站文本使用 Telegram 的 `parse_mode: "HTML"`。

    - 类 Markdown 文本将渲染为 Telegram 安全的 HTML。
    - 模型原始 HTML 将被转义，以降低 Telegram 解析失败概率。
    - 若 Telegram 拒绝解析后的 HTML，OpenClaw 将重试发送纯文本。

    链接预览默认启用，可通过 `channels.telegram.linkPreview: false` 禁用。

  </Accordion>

  <Accordion title="原生命令与自定义命令">
    Telegram 命令菜单注册在启动时通过 `setMyCommands` 完成。

    原生命令默认设置：

    - `commands.native: "auto"` 启用 Telegram 的原生命令

    添加自定义命令菜单项：

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

    规则：

    - 名称将被规范化（去除前导 `/`，转为小写）
    - 有效模式：`a-z`、`0-9`、`_`，长度为 `1..32`
    - 自定义命令不可覆盖原生命令
    - 冲突/重复项将被跳过并记录日志

    注意事项：

- 自定义命令仅为菜单项；它们不会自动实现行为  
- 即使未在 Telegram 菜单中显示，插件/技能命令在手动输入时仍可正常工作  

如果禁用了原生命令，则内置命令将被移除。若已配置，自定义/插件命令仍可能注册。  

常见设置失败情况：  

- `setMyCommands failed` 通常表示到 `api.telegram.org` 的出站 DNS/HTTPS 被阻止。  

### 设备配对命令（`device-pair` 插件）  

当安装了 `device-pair` 插件时：  

1. `/pair` 生成设置代码  
2. 将代码粘贴至 iOS 应用  
3. `/pair approve` 批准最新的待处理请求  

更多详情：[配对](/channels/pairing#pair-via-telegram-recommended-for-ios)。  

</Accordion>  

<Accordion title="内联按钮">  
配置内联键盘作用域：  

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

按账号覆盖：  

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

作用域：  

- `off`  
- `dm`  
- `group`  
- `all`  
- `allowlist`（默认）  

旧版 `capabilities: ["inlineButtons"]` 映射至 `inlineButtons: "all"`。  

消息操作示例：  

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

回调点击以文本形式传递给代理：  
`callback_data: <value>`  

</Accordion>  

<Accordion title="面向代理与自动化的 Telegram 消息操作">  
Telegram 工具操作包括：  

- `sendMessage`（`to`、`content`、可选的 `mediaUrl`、`replyToMessageId`、`messageThreadId`）  
- `react`（`chatId`、`messageId`、`emoji`）  
- `deleteMessage`（`chatId`、`messageId`）  
- `editMessage`（`chatId`、`messageId`、`content`）  
- `createForumTopic`（`chatId`、`name`、可选的 `iconColor`、`iconCustomEmojiId`）  

频道消息操作提供便捷别名（`send`、`react`、`delete`、`edit`、`sticker`、`sticker-search`、`topic-create`）。  

门控控制：  

- `channels.telegram.actions.sendMessage`  
- `channels.telegram.actions.deleteMessage`  
- `channels.telegram.actions.reactions`  
- `channels.telegram.actions.sticker`（默认：禁用）  

注意：`edit` 和 `topic-create` 当前默认启用，且无单独的 `channels.telegram.actions.*` 开关。  

反应移除语义：[/tools/reactions](/tools/reactions)  

</Accordion>  

<Accordion title="回复线程标签">  
Telegram 在生成的输出中支持显式回复线程标签：  

- `[[reply_to_current]]` 回复触发该消息的原始消息  
- `[[reply_to:<id>]]` 回复特定的 Telegram 消息 ID  

`channels.telegram.replyToMode` 控制处理方式：  

- `off`（默认）  
- `first`  
- `all`  

注意：`off` 禁用隐式回复线程。显式的 `[[reply_to_*]]` 标签仍会被遵守。  

</Accordion>  

<Accordion title="论坛主题与线程行为">  
论坛超级群：  

- 主题会话密钥附加 `:topic:<threadId>`  
- 回复与输入状态均针对主题线程  
- 主题配置路径：  
  `channels.telegram.groups.<chatId>.topics.<threadId>`  

通用主题（`threadId=1`）特殊情形：  

- 发送消息时省略 `message_thread_id`（Telegram 拒绝含 `sendMessage(...thread_id=1)` 的消息）  
- 输入状态操作仍包含 `message_thread_id`  

主题继承：主题条目继承群组设置，除非被覆盖（`requireMention`、`allowFrom`、`skills`、`systemPrompt`、`enabled`、`groupPolicy`）。  
`agentId` 仅适用于主题，不从群组默认值继承。  

**按主题的代理路由**：每个主题可通过在主题配置中设置 `agentId`，路由至不同代理。这为每个主题提供独立的工作区、记忆与会话。示例：  

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

此后每个主题拥有其专属会话密钥：`agent:zu:telegram:group:-1001234567890:topic:3`  

**持久化 ACP 主题绑定**：论坛主题可通过顶层键入式 ACP 绑定固定 ACP 支撑会话：  

- `bindings[]` 配合 `type: "acp"` 和 `match.channel: "telegram"`  

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

当前此功能仅限于群组与超级群中的论坛主题。  

**从聊天发起线程绑定的 ACP 实例**：  

- `/acp spawn <agent> --thread here|auto` 可将当前 Telegram 主题绑定至新的 ACP 会话。  
- 后续主题消息将直接路由至已绑定的 ACP 会话（无需 `/acp steer`）。  
- OpenClaw 在成功绑定后，将启动确认消息置顶于主题内。  
- 需启用 `channels.telegram.threadBindings.spawnAcpSessions=true`。  

模板上下文包含：  

- `MessageThreadId`  
- `IsForum`  

私聊线程行为：  

- 与 `message_thread_id` 的私聊保留私聊路由，但使用线程感知的会话密钥/回复目标。  

</Accordion>  

<Accordion title="音频、视频与贴纸">  
### 音频消息  

Telegram 区分语音备忘录与音频文件。  

- 默认：音频文件行为  
- 在代理回复中添加标签 `[[audio_as_voice]]` 强制发送语音备忘录  

消息操作示例：  

```json5
{
  action: "send",
  channel: "telegram",
  to: "123456789",
  media: "https://example.com/voice.ogg",
  asVoice: true,
}
```  

### 视频消息  

Telegram 区分视频文件与视频备忘录。  

消息操作示例：  

```json5
{
  action: "send",
  channel: "telegram",
  to: "123456789",
  media: "https://example.com/video.mp4",
  asVideoNote: true,
}
```  

视频备忘录不支持字幕；提供的消息文本将单独发送。  

### 贴纸  

入站贴纸处理：  

- 静态 WEBP：下载并处理（占位符 `<media:sticker>`）  
- 动画 TGS：跳过  
- 视频 WEBM：跳过  

贴纸上下文字段：  

- `Sticker.emoji`  
- `Sticker.setName`  
- `Sticker.fileId`  
- `Sticker.fileUniqueId`  
- `Sticker.cachedDescription`  

贴纸缓存文件：  

- `~/.openclaw/telegram/sticker-cache.json`  

贴纸仅描述一次（如可行），并缓存以减少重复视觉调用。  

启用贴纸操作：  

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

发送贴纸操作：  

```json5
{
  action: "sticker",
  channel: "telegram",
  to: "123456789",
  fileId: "CAACAgIAAxkBAAI...",
}
```  

搜索已缓存贴纸：  

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
Telegram 反应作为 `message_reaction` 更新到达（与消息载荷分离）。  

启用后，OpenClaw 将排队系统事件，例如：  

- `Telegram reaction added: 👍 by Alice (@alice) on msg 42`  

配置：  

- `channels.telegram.reactionNotifications`：`off | own | all`（默认：`own`）  
- `channels.telegram.reactionLevel`：`off | ack | minimal | extensive`（默认：`minimal`）  

注意事项：  

- `own` 表示仅处理用户对机器人所发消息的反应（通过已发送消息缓存尽力实现）。  
- 反应事件仍受 Telegram 访问控制约束（`dmPolicy`、`allowFrom`、`groupPolicy`、`groupAllowFrom`）；未授权发送者将被丢弃。  
- Telegram 在反应更新中不提供线程 ID。  
  - 非论坛群组路由至群组聊天会话  
  - 论坛群组路由至群组通用主题会话（`:topic:1`），而非确切的原始主题  

`allowed_updates` 的轮询/网络钩子自动包含 `message_reaction`。  

</Accordion>  

<Accordion title="确认反应">  
`ackReaction` 在 OpenClaw 处理入站消息期间发送确认表情符号。  

解析顺序：  

- `channels.telegram.accounts.<accountId>.ackReaction`  
- `channels.telegram.ackReaction`  
- `messages.ackReaction`  
- 代理身份表情符号回退（`agents.list[].identity.emoji`，否则为 "👀"）  

注意事项：  

- Telegram 期望使用 Unicode 表情符号（例如 "👀"）。  
- 使用 `""` 可为频道或账号禁用该反应。  

</Accordion>  

<Accordion title="来自 Telegram 事件与命令的配置写入">  
频道配置写入默认启用（`configWrites !== false`）。  

由 Telegram 触发的写入包括：

- 将迁移事件（``migrate_to_chat_id``）分组，以更新 ``channels.telegram.groups``  
- ``/config set`` 和 ``/config unset``（需启用对应命令）

禁用：

````json5
{
  channels: {
    telegram: {
      configWrites: false,
    },
  },
}
````

  </Accordion>

  <Accordion title="长轮询 vs Webhook">
    默认：长轮询。

    Webhook 模式：

    - 设置 ``channels.telegram.webhookUrl``  
    - 设置 ``channels.telegram.webhookSecret``（当设置了 Webhook URL 时为必需项）  
    - 可选配置 ``channels.telegram.webhookPath``（默认值为 ``/telegram-webhook``）  
    - 可选配置 ``channels.telegram.webhookHost``（默认值为 ``127.0.0.1``）  
    - 可选配置 ``channels.telegram.webhookPort``（默认值为 ``8787``）

    Webhook 模式下，默认本地监听器绑定到 ``127.0.0.1:8787``。

    若您的公网端点与此不同，请在其前方部署反向代理，并将 ``webhookUrl`` 指向公网 URL。  
    当您明确需要外部入口时，请设置 ``webhookHost``（例如 ``0.0.0.0``）。

  </Accordion>

  <Accordion title="限制、重试与 CLI 目标">
    - ``channels.telegram.textChunkLimit`` 默认值为 4000。  
    - ``channels.telegram.chunkMode="newline"`` 在按长度切分前优先考虑段落边界（空行）。  
    - ``channels.telegram.mediaMaxMb``（默认值为 100）限制 Telegram 收发媒体文件的大小上限。  
    - ``channels.telegram.timeoutSeconds`` 覆盖 Telegram API 客户端超时时间（若未设置，则采用 grammY 默认值）。  
    - 群组上下文历史记录使用 ``channels.telegram.historyLimit`` 或 ``messages.groupChat.historyLimit``（默认值为 50）；``0`` 可禁用该功能。  
    - 私聊（DM）历史记录控制项：  
      - ``channels.telegram.dmHistoryLimit``  
      - ``channels.telegram.dms["<user_id>"].historyLimit``  
    - ``channels.telegram.retry`` 配置适用于 Telegram 发送辅助工具（CLI/工具/操作），用于处理可恢复的出站 API 错误。

    CLI 发送目标可以是数字形式的聊天 ID 或用户名：

````bash
openclaw message send --channel telegram --target 123456789 --message "hi"
openclaw message send --channel telegram --target @name --message "hi"
````

    Telegram 投票使用 ``openclaw message poll``，并支持论坛主题：

````bash
openclaw message poll --channel telegram --target 123456789 \
  --poll-question "Ship it?" --poll-option "Yes" --poll-option "No"
openclaw message poll --channel telegram --target -1001234567890:topic:42 \
  --poll-question "Pick a time" --poll-option "10am" --poll-option "2pm" \
  --poll-duration-seconds 300 --poll-public
````

    仅限 Telegram 的投票标志：

    - ``--poll-duration-seconds``（取值范围：5–600）  
    - ``--poll-anonymous``  
    - ``--poll-public``  
    - ``--thread-id``（用于论坛主题；或使用 ``:topic:`` 目标）

    操作门控（Action gating）：

    - ``channels.telegram.actions.sendMessage=false`` 禁用所有出站 Telegram 消息（包括投票）  
    - ``channels.telegram.actions.poll=false`` 禁用 Telegram 投票创建功能，但保留常规消息发送能力

  </Accordion>
</AccordionGroup>

## 故障排除

`<AccordionGroup>
  <Accordion title="Bot does not respond to non mention group messages">

    - If __CODE_BLOCK_37__, Telegram privacy mode must allow full visibility.
      - BotFather: __CODE_BLOCK_38__ -> Disable
      - then remove + re-add bot to group
    - __CODE_BLOCK_39__ warns when config expects unmentioned group messages.
    - __CODE_BLOCK_40__ can check explicit numeric group IDs; wildcard __CODE_BLOCK_41__ cannot be membership-probed.
    - quick session test: __CODE_BLOCK_42__.

  </Accordion>

  <Accordion title="Bot not seeing group messages at all">

    - when __CODE_BLOCK_43__ exists, group must be listed (or include __CODE_BLOCK_44__)
    - verify bot membership in group
    - review logs: __CODE_BLOCK_45__ for skip reasons

  </Accordion>

  <Accordion title="Commands work partially or not at all">

    - authorize your sender identity (pairing and/or numeric __CODE_BLOCK_46__)
    - command authorization still applies even when group policy is __CODE_BLOCK_47__
    - __CODE_BLOCK_48__ usually indicates DNS/HTTPS reachability issues to __CODE_BLOCK_49__

  </Accordion>

  <Accordion title="Polling or network instability">

    - Node 22+ + custom fetch/proxy can trigger immediate abort behavior if AbortSignal types mismatch.
    - Some hosts resolve __CODE_BLOCK_50__ to IPv6 first; broken IPv6 egress can cause intermittent Telegram API failures.
    - If logs include __CODE_BLOCK_51__ or __CODE_BLOCK_52__, OpenClaw now retries these as recoverable network errors.
    - On VPS hosts with unstable direct egress/TLS, route Telegram API calls through __CODE_BLOCK_53__:

__CODE_BLOCK_54__

    - Node 22+ defaults to __CODE_BLOCK_55__ (except WSL2) and __CODE_BLOCK_56__.
    - If your host is WSL2 or explicitly works better with IPv4-only behavior, force family selection:

__CODE_BLOCK_57__

    - Environment overrides (temporary):
      - __CODE_BLOCK_58__
      - __CODE_BLOCK_59__
      - __CODE_BLOCK_60__
    - Validate DNS answers:

__CODE_BLOCK_61__

  </Accordion>
</AccordionGroup>`

获取更多帮助：[频道故障排除](/channels/troubleshooting)。

## Telegram 配置参考指引

主要参考文档：

- `channels.telegram.enabled`: 启用/禁用频道启动。
- `channels.telegram.botToken`: 机器人令牌（BotFather）。
- `channels.telegram.tokenFile`: 从文件路径读取令牌。
- `channels.telegram.dmPolicy`: `pairing | allowlist | open | disabled`（默认值：pairing）。
- `channels.telegram.allowFrom`: 私信（DM）允许列表（数值型 Telegram 用户 ID）。`allowlist` 要求至少指定一个发送者 ID。`open` 要求配置 `"*"`。`openclaw doctor --fix` 可将旧版 `@username` 条目解析为 ID，并可在允许列表迁移流程中从 pairing-store 文件恢复允许列表条目。
- `channels.telegram.actions.poll`: 启用或禁用 Telegram 投票创建（默认启用；但仍需满足 `sendMessage`）。
- `channels.telegram.defaultTo`: CLI `--deliver` 在未显式提供 `--reply-to` 时所使用的默认 Telegram 目标。
- `channels.telegram.groupPolicy`: `open | allowlist | disabled`（默认值：allowlist）。
- `channels.telegram.groupAllowFrom`: 群组发送者允许列表（数值型 Telegram 用户 ID）。`openclaw doctor --fix` 可将旧版 `@username` 条目解析为 ID。非数值型条目在认证时会被忽略。群组认证不使用私信（DM）配对存储（pairing-store）回退机制（`2026.2.25+`）。
- 多账号优先级：
  - 当配置了两个或更多账号 ID 时，需设置 `channels.telegram.defaultAccount`（或包含 `channels.telegram.accounts.default`），以明确指定默认路由。
  - 若两者均未设置，OpenClaw 将回退至首个标准化的账号 ID，且 `openclaw doctor` 将发出警告。
  - `channels.telegram.accounts.default.allowFrom` 和 `channels.telegram.accounts.default.groupAllowFrom` 仅适用于 `default` 账号。
  - 命名账号在账号级配置未设置时，会继承 `channels.telegram.allowFrom` 和 `channels.telegram.groupAllowFrom`。
  - 命名账号不会继承 `channels.telegram.accounts.default.allowFrom` / `groupAllowFrom`。
- `channels.telegram.groups`: 每个群组的默认配置 + 允许列表（如需全局默认值，请使用 `"*"`）。
  - `channels.telegram.groups.<id>.groupPolicy`: 群组级 groupPolicy（`open | allowlist | disabled`）的覆盖配置。
  - `channels.telegram.groups.<id>.requireMention`: 提及（mention）门控默认值。
  - `channels.telegram.groups.<id>.skills`: 技能过滤器（省略 = 所有技能，空值 = 无技能）。
  - `channels.telegram.groups.<id>.allowFrom`: 每个群组的发送者允许列表覆盖配置。
  - `channels.telegram.groups.<id>.systemPrompt`: 该群组的额外系统提示词。
  - `channels.telegram.groups.<id>.enabled`: 当满足 `false` 时禁用该群组。
  - `channels.telegram.groups.<id>.topics.<threadId>.*`: 每主题覆盖配置（群组字段 + 仅限主题的 `agentId`）。
  - `channels.telegram.groups.<id>.topics.<threadId>.agentId`: 将该主题路由至特定代理（覆盖群组级和绑定路由）。
  - `channels.telegram.groups.<id>.topics.<threadId>.groupPolicy`: 每主题对 groupPolicy（`open | allowlist | disabled`）的覆盖配置。
  - `channels.telegram.groups.<id>.topics.<threadId>.requireMention`: 每主题对提及（mention）门控的覆盖配置。
  - 顶层 `bindings[]` 中含 `type: "acp"` 和规范主题 ID `chatId:topic:topicId` 的 `match.peer.id`：持久化 ACP 主题绑定字段（参见 [ACP Agents](/tools/acp-agents#channel-specific-settings)）。
  - `channels.telegram.direct.<id>.topics.<threadId>.agentId`: 将私信（DM）主题路由至特定代理（行为与论坛主题相同）。
- `channels.telegram.capabilities.inlineButtons`: `off | dm | group | all | allowlist`（默认值：allowlist）。
- `channels.telegram.accounts.<account>.capabilities.inlineButtons`: 每账号覆盖配置。
- `channels.telegram.commands.nativeSkills`: 启用/禁用 Telegram 原生技能命令。
- `channels.telegram.replyToMode`: `off | first | all`（默认值：`off`）。
- `channels.telegram.textChunkLimit`: 出站消息分块大小（字符数）。
- `channels.telegram.chunkMode`: `length`（默认）或 `newline`，表示在按长度分块前先按空行（段落边界）分割。
- `channels.telegram.linkPreview`: 切换出站消息的链接预览功能（默认：true）。
- `channels.telegram.streaming`: `off | partial | block | progress`（实时流预览；默认：`partial`；`progress` 映射至 `partial`；`block` 是旧版预览模式兼容性支持）。在私信（DM）中，`partial` 在可用时使用原生 `sendMessageDraft`。
- `channels.telegram.mediaMaxMb`: Telegram 入站/出站媒体容量限制（MB，默认：100）。
- `channels.telegram.retry`: Telegram 发送辅助工具（CLI/工具/操作）在可恢复的出站 API 错误上的重试策略（尝试次数、最小延迟毫秒数、最大延迟毫秒数、抖动）。
- `channels.telegram.network.autoSelectFamily`: 覆盖 Node 的 autoSelectFamily 设置（true=启用，false=禁用）。Node 22+ 默认启用，WSL2 默认禁用。
- `channels.telegram.network.dnsResultOrder`: 覆盖 DNS 查询结果顺序（`ipv4first` 或 `verbatim`）。Node 22+ 默认为 `ipv4first`。
- `channels.telegram.proxy`: Bot API 调用所用代理 URL（SOCKS/HTTP）。
- `channels.telegram.webhookUrl`: 启用 Webhook 模式（需配置 `channels.telegram.webhookSecret`）。
- `channels.telegram.webhookSecret`: Webhook 密钥（当设置了 webhookUrl 时为必填项）。
- `channels.telegram.webhookPath`: 本地 Webhook 路径（默认为 `/telegram-webhook`）。
- `channels.telegram.webhookHost`: 本地 Webhook 绑定主机（默认为 `127.0.0.1`）。
- `channels.telegram.webhookPort`: 本地 Webhook 绑定端口（默认为 `8787`）。
- `channels.telegram.actions.reactions`: 控制 Telegram 工具反应（reactions）的门控。
- `channels.telegram.actions.sendMessage`: 控制 Telegram 工具消息发送的门控。
- `channels.telegram.actions.deleteMessage`: 控制 Telegram 工具消息删除的门控。
- `channels.telegram.actions.sticker`: 控制 Telegram 贴纸操作（发送与搜索）的门控（默认：false）。
- `channels.telegram.reactionNotifications`: `off | own | all` — 控制触发系统事件的反应类型（未设置时默认为 `own`）。
- `channels.telegram.reactionLevel`: `off | ack | minimal | extensive` — 控制代理的反应能力（未设置时默认为 `minimal`）。

- [配置参考 - Telegram](/gateway/configuration-reference#telegram)

Telegram 特有的高信号字段：

- 启动/认证：`enabled`、`botToken`、`tokenFile`、`accounts.*`
- 访问控制：`dmPolicy`、`allowFrom`、`groupPolicy`、`groupAllowFrom`、`groups`、`groups.*.topics.*`、顶层 `bindings[]`（`type: "acp"`）
- 命令/菜单：`commands.native`、`commands.nativeSkills`、`customCommands`
- 线程/回复：`replyToMode`
- 流式传输：`streaming`（预览）、`blockStreaming`
- 格式化/投递：`textChunkLimit`、`chunkMode`、`linkPreview`、`responsePrefix`
- 媒体/网络：`mediaMaxMb`、`timeoutSeconds`、`retry`、`network.autoSelectFamily`、`proxy`
- Webhook：`webhookUrl`、`webhookSecret`、`webhookPath`、`webhookHost`
- 操作/能力：`capabilities.inlineButtons`、`actions.sendMessage|editMessage|deleteMessage|reactions|sticker`
- 反应（Reactions）：`reactionNotifications`、`reactionLevel`
- 写入/历史记录：`configWrites`、`historyLimit`、`dmHistoryLimit`、`dms.*.historyLimit`

## 相关文档

- [配对（Pairing）](/channels/pairing)
- [频道路由（Channel routing）](/channels/channel-routing)
- [多代理路由（Multi-agent routing）](/concepts/multi-agent)
- [故障排除（Troubleshooting）](/channels/troubleshooting)