---
summary: "WhatsApp (web channel) integration: login, inbox, replies, media, and ops"
read_when:
  - Working on WhatsApp/web channel behavior or inbox routing
title: "WhatsApp"
---
# WhatsApp (web channel)

状态: 仅通过 Baileys 使用 WhatsApp Web。网关拥有会话。

## 快速设置（初学者）

1. 如果可能，请使用一个**独立的电话号码**（推荐）。
2. 在 `~/.openclaw/openclaw.json` 中配置 WhatsApp。
3. 运行 `openclaw channels login` 扫描二维码（已连接设备）。
4. 启动网关。

最小配置：

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "allowlist",
      allowFrom: ["+15551234567"],
    },
  },
}
```

## 目标

- 在一个网关进程中运行多个 WhatsApp 账户（多账户）。
- 确定性路由：回复返回到 WhatsApp，不进行模型路由。
- 模型有足够的上下文来理解引用的回复。

## 配置写入

默认情况下，WhatsApp 允许由 `/config set|unset` 触发的配置更新写入（需要 `commands.config: true`）。

禁用方法：

```json5
{
  channels: { whatsapp: { configWrites: false } },
}
```

## 架构（谁拥有什么）

- **网关** 拥有 Baileys 套接字和收件箱循环。
- **CLI / macOS 应用程序** 与网关通信；不直接使用 Baileys。
- **活动监听器** 对于外发消息是必需的；否则发送会立即失败。

## 获取电话号码（两种模式）

WhatsApp 需要一个真实的移动号码进行验证。VoIP 和虚拟号码通常会被阻止。有两种支持的方式在 WhatsApp 上运行 OpenClaw：

### 专用号码（推荐）

为 OpenClaw 使用一个**独立的电话号码**。最佳用户体验，清晰的路由，没有自我聊天的奇怪行为。理想设置：**备用/旧 Android 手机 + eSIM**。将其连接到 Wi-Fi 并通电，然后通过二维码链接。

**WhatsApp Business:** 您可以在同一设备上使用不同的号码运行 WhatsApp Business。非常适合将您的个人 WhatsApp 与工作分开 — 安装 WhatsApp Business 并在那里注册 OpenClaw 号码。

**示例配置（专用号码，单用户白名单）：**

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "allowlist",
      allowFrom: ["+15551234567"],
    },
  },
}
```

**配对模式（可选）：**
如果您希望使用配对而不是白名单，请将 `channels.whatsapp.dmPolicy` 设置为 `pairing`。未知发送者会收到一个配对代码；批准方法：
`openclaw pairing approve whatsapp <code>`

### 个人号码（备用）

快速备用：在**您自己的号码**上运行 OpenClaw。测试时给自己发消息（WhatsApp“给自己发消息”），以免骚扰联系人。在设置和实验期间，预期会在主手机上阅读验证码。**必须启用自我聊天模式。**
当向导询问您的个人 WhatsApp 号码时，输入您将从中发送消息的电话（所有者/发送者），而不是助手号码。

**示例配置（个人号码，自我聊天）：**

```json
{
  "whatsapp": {
    "selfChatMode": true,
    "dmPolicy": "allowlist",
    "allowFrom": ["+15551234567"]
  }
}
```

自我聊天回复默认为 `[{identity.name}]` 当设置时（否则 `[openclaw]`）
如果 `messages.responsePrefix` 未设置。显式设置以自定义或禁用
前缀（使用 `""` 移除它）。

### 获取号码提示

- **本地eSIM** 由您国家的移动运营商提供（最可靠）
  - 奥地利: [hot.at](https://www.hot.at)
  - 英国: [giffgaff](https://www.giffgaff.com) — 免费SIM卡，无需合同
- **预付费SIM卡** — 便宜，只需接收一条短信进行验证

**避免:** TextNow, Google Voice, 大多数“免费短信”服务 — WhatsApp会积极阻止这些。

**提示:** 该号码只需接收一条验证短信。之后，WhatsApp Web会话通过 `creds.json` 持续。

## 为什么不用Twilio？

- 早期的OpenClaw构建支持Twilio的WhatsApp Business集成。
- WhatsApp Business号码不适合个人助理。
- Meta强制执行24小时回复窗口；如果您在最后24小时内没有回复，业务号码将无法发起新消息。
- 高流量或“聊天式”使用会触发积极阻止，因为业务账户不打算发送数十条个人助理消息。
- 结果：不可靠的传递和频繁阻止，因此支持已被移除。

## 登录 + 凭证

- 登录命令: `openclaw channels login` (通过关联设备的QR码)。
- 多账户登录: `openclaw channels login --account <id>` (`<id>` = `accountId`)。
- 默认账户（当省略 `--account` 时）: 如果存在则为 `default`，否则为第一个配置的账户id（按顺序排列）。
- 凭证存储在 `~/.openclaw/credentials/whatsapp/<accountId>/creds.json`。
- 备份副本位于 `creds.json.bak`（在损坏时恢复）。
- 向后兼容性：较旧的安装直接在 `~/.openclaw/credentials/` 中存储Baileys文件。
- 登出: `openclaw channels logout` (或 `--account <id>`) 删除WhatsApp认证状态（但保留共享的 `oauth.json`）。
- 已登出的套接字 => 错误指示重新关联。

## 入站流程（私信 + 群组）

- WhatsApp事件来自 `messages.upsert` (Baileys)。
- 关闭时分离收件箱监听器，以避免在测试/重启中积累事件处理程序。
- 忽略状态/广播聊天。
- 直接聊天使用E.164；群组使用群组JID。
- **私信策略**: `channels.whatsapp.dmPolicy` 控制直接聊天访问（默认: `pairing`）。
  - 配对: 未知发件人会收到配对代码（通过 `openclaw pairing approve whatsapp <code>` 批准；代码在1小时后过期）。
  - 开放: 需要 `channels.whatsapp.allowFrom` 包含 `"*"`。
  - 您的关联WhatsApp号码会被隐式信任，因此自我消息跳过 ⁠`channels.whatsapp.dmPolicy` 和 `channels.whatsapp.allowFrom` 检查。

### 个人号码模式（备用）

如果您在您的 **个人WhatsApp号码** 上运行OpenClaw，请启用 `channels.whatsapp.selfChatMode`（参见上面的示例）。

行为：

- 发出的私信永远不会触发配对回复（防止骚扰联系人）。
- 接收的未知发件人仍然遵循 `channels.whatsapp.dmPolicy`。
- 自我聊天模式（allowFrom包含您的号码）避免自动读回执并忽略提及的JID。
- 发送非自我聊天私信的读回执。

## 读回执

默认情况下，网关在接收WhatsApp消息后会将其标记为已读（蓝色勾号）。

全局禁用：

```json5
{
  channels: { whatsapp: { sendReadReceipts: false } },
}
```

按账户禁用：

```json5
{
  channels: {
    whatsapp: {
      accounts: {
        personal: { sendReadReceipts: false },
      },
    },
  },
}
```

注意事项：

- 自我聊天模式始终跳过已读回执。

## WhatsApp常见问题：发送消息 + 配对

**当我链接WhatsApp时，OpenClaw会向随机联系人发送消息吗？**  
不。默认的DM策略是**配对**，因此未知发件人只会收到一个配对码，且其消息**不会被处理**。OpenClaw仅回复接收到的聊天，或者你明确触发的发送（代理/CLI）。

**WhatsApp上的配对是如何工作的？**  
配对是未知发件人的DM网关：

- 来自新发件人的第一条DM会返回一个短码（消息不会被处理）。
- 使用以下命令批准：`openclaw pairing approve whatsapp <code>`（列表使用`openclaw pairing list whatsapp`）。
- 码有效期为1小时；每个频道待处理请求最多为3个。

**多人是否可以使用同一个WhatsApp号码的不同OpenClaw实例？**  
可以，通过`bindings`将每个发件人路由到不同的代理（对等`kind: "direct"`，发件人E.164如`+15551234567`）。回复仍然来自**同一个WhatsApp账户**，直接聊天会合并到每个代理的主要会话中，因此请**每人使用一个代理**。DM访问控制（`dmPolicy`/`allowFrom`）对每个WhatsApp账户是全局的。参见[多代理路由](/concepts/multi-agent)。

**为什么向导会要求我的电话号码？**  
向导使用它来设置你的**允许名单/所有者**，以便允许你的DM。它不会用于自动发送。如果你使用个人WhatsApp号码运行，请使用相同的号码并启用`channels.whatsapp.selfChatMode`。

## 消息规范化（模型所见）

- `Body`是当前消息正文及其信封。
- 引用回复上下文**总是附加**：

  ```
  [Replying to +1555 id:ABC123]
  <quoted text or <media:...>>
  [/Replying]
  ```

- 回复元数据也会设置：
  - `ReplyToId` = stanzaId
  - `ReplyToBody` = 引用正文或媒体占位符
  - `ReplyToSender` = 已知时为E.164
- 仅包含媒体的入站消息使用占位符：
  - `<media:image|video|audio|document|sticker>`

## 群组

- Groups map to `agent:<agentId>:whatsapp:group:<jid>` sessions.
- Group policy: `channels.whatsapp.groupPolicy = open|disabled|allowlist` (default `allowlist`).
- Activation modes:
  - `mention` (default): requires @mention or regex match.
  - `always`: always triggers.
- `/activation mention|always` is owner-only and must be sent as a standalone message.
- Owner = `channels.whatsapp.allowFrom` (or self E.164 if unset).
- **History injection** (pending-only):
  - Recent _unprocessed_ messages (default 50) inserted under:
    `[Chat messages since your last reply - for context]` (messages already in the session are not re-injected)
  - Current message under:
    `[Current message - respond to this]`
  - Sender suffix appended: `[from: Name (+E164)]`
- Group metadata cached 5 min (subject + participants).

## Reply delivery (threading)

- WhatsApp Web sends standard messages (no quoted reply threading in the current gateway).
- Reply tags are ignored on this channel.

## Acknowledgment reactions (auto-react on receipt)

WhatsApp can automatically send emoji reactions to incoming messages immediately upon receipt, before the bot generates a reply. This provides instant feedback to users that their message was received.

**Configuration:**

```json
{
  "whatsapp": {
    "ackReaction": {
      "emoji": "👀",
      "direct": true,
      "group": "mentions"
    }
  }
}
```

**Options:**

- `emoji` (string): Emoji to use for acknowledgment (e.g., "👀", "✅", "📨"). Empty or omitted = feature disabled.
- `direct` (boolean, default: `true`): Send reactions in direct/DM chats.
- `group` (string, default: `"mentions"`): Group chat behavior:
  - `"always"`: React to all group messages (even without @mention)
  - `"mentions"`: React only when bot is @mentioned
  - `"never"`: Never react in groups

**Per-account override:**

```json
{
  "whatsapp": {
    "accounts": {
      "work": {
        "ackReaction": {
          "emoji": "✅",
          "direct": false,
          "group": "always"
        }
      }
    }
  }
}
```

**Behavior notes:**

- Reactions are sent **immediately** upon message receipt, before typing indicators or bot replies.
- In groups with `requireMention: false` (activation: always), `group: "mentions"` will react to all messages (not just @mentions).
- Fire-and-forget: reaction failures are logged but don't prevent the bot from replying.
- Participant JID is automatically included for group reactions.
- WhatsApp ignores `messages.ackReaction`; use `channels.whatsapp.ackReaction` instead.

## Agent tool (reactions)

- Tool: `whatsapp` with `react` action (`chatJid`, `messageId`, `emoji`, optional `remove`).
- Optional: `participant` (group sender), `fromMe` (reacting to your own message), `accountId` (multi-account).
- Reaction removal semantics: see [/tools/reactions](/tools/reactions).
- Tool gating: `channels.whatsapp.actions.reactions` (default: enabled).

## Limits

- 出站文本分块为 `channels.whatsapp.textChunkLimit`（默认 4000）。
- 可选换行分块：设置 `channels.whatsapp.chunkMode="newline"` 以在长度分块之前按空白行（段落边界）拆分。
- 入站媒体保存限制为 `channels.whatsapp.mediaMaxMb`（默认 50 MB）。
- 出站媒体项目限制为 `agents.defaults.mediaMaxMb`（默认 5 MB）。

## 出站发送（文本 + 媒体）

- 使用活动 Web 监听器；如果网关未运行则报错。
- 文本分块：每条消息最大 4k（可通过 `channels.whatsapp.textChunkLimit` 配置，可选 `channels.whatsapp.chunkMode`）。
- 媒体：
  - 支持图片/视频/音频/文档。
  - 音频作为 PTT 发送；`audio/ogg` => `audio/ogg; codecs=opus`。
  - 仅第一个媒体项目有标题。
  - 媒体获取支持 HTTP(S) 和本地路径。
  - 动态 GIF：WhatsApp 期望带有 `gifPlayback: true` 的 MP4 以便内联循环。
    - CLI: `openclaw message send --media <mp4> --gif-playback`
    - 网关: `send` 参数包括 `gifPlayback: true`

## 语音消息（PTT 音频）

WhatsApp 将音频作为 **语音消息**（PTT 气泡）发送。

- 最佳效果：OGG/Opus。OpenClaw 将 `audio/ogg` 重写为 `audio/ogg; codecs=opus`。
- WhatsApp 忽略 `[[audio_as_voice]]`（音频已经作为语音消息发送）。

## 媒体限制 + 优化

- 默认出站限制：5 MB（每个媒体项目）。
- 覆盖：`agents.defaults.mediaMaxMb`。
- 图片在限制下自动优化为 JPEG（调整大小 + 质量扫描）。
- 超尺寸媒体 => 错误；媒体回复回退到文本警告。

## 心跳

- **网关心跳** 记录连接健康状况 (`web.heartbeatSeconds`，默认 60 秒）。
- **代理心跳** 可以按代理 (`agents.list[].heartbeat`) 或全局
  通过 `agents.defaults.heartbeat` 配置（当没有按代理的条目时使用）。
  - 使用配置的心跳提示（默认: `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`) + `HEARTBEAT_OK` 跳过行为。
  - 交付默认为最后使用的通道（或配置的目标）。

## 重新连接行为

- 退避策略：`web.reconnect`:
  - `initialMs`, `maxMs`, `factor`, `jitter`, `maxAttempts`。
- 如果达到 maxAttempts，Web 监控停止（降级）。
- 登出 => 停止并要求重新链接。

## 配置快速映射

- `channels.whatsapp.dmPolicy` (DM policy: pairing/allowlist/open/disabled).
- `channels.whatsapp.selfChatMode` (same-phone setup; bot uses your personal WhatsApp number).
- `channels.whatsapp.allowFrom` (DM allowlist). WhatsApp uses E.164 phone numbers (no usernames).
- `channels.whatsapp.mediaMaxMb` (inbound media save cap).
- `channels.whatsapp.ackReaction` (auto-reaction on message receipt: `{emoji, direct, group}`).
- `channels.whatsapp.accounts.<accountId>.*` (per-account settings + optional `authDir`).
- `channels.whatsapp.accounts.<accountId>.mediaMaxMb` (per-account inbound media cap).
- `channels.whatsapp.accounts.<accountId>.ackReaction` (per-account ack reaction override).
- `channels.whatsapp.groupAllowFrom` (group sender allowlist).
- `channels.whatsapp.groupPolicy` (group policy).
- `channels.whatsapp.historyLimit` / `channels.whatsapp.accounts.<accountId>.historyLimit` (group history context; `0` disables).
- `channels.whatsapp.dmHistoryLimit` (DM history limit in user turns). Per-user overrides: `channels.whatsapp.dms["<phone>"].historyLimit`.
- `channels.whatsapp.groups` (group allowlist + mention gating defaults; use `"*"` to allow all)
- `channels.whatsapp.actions.reactions` (gate WhatsApp tool reactions).
- `agents.list[].groupChat.mentionPatterns` (or `messages.groupChat.mentionPatterns`)
- `messages.groupChat.historyLimit`
- `channels.whatsapp.messagePrefix` (inbound prefix; per-account: `channels.whatsapp.accounts.<accountId>.messagePrefix`; deprecated: `messages.messagePrefix`)
- `messages.responsePrefix` (outbound prefix)
- `agents.defaults.mediaMaxMb`
- `agents.defaults.heartbeat.every`
- `agents.defaults.heartbeat.model` (optional override)
- `agents.defaults.heartbeat.target`
- `agents.defaults.heartbeat.to`
- `agents.defaults.heartbeat.session`
- `agents.list[].heartbeat.*` (per-agent overrides)
- `session.*` (scope, idle, store, mainKey)
- `web.enabled` (disable channel startup when false)
- `web.heartbeatSeconds`
- `web.reconnect.*`

## 日志 + 故障排除

- 子系统: `whatsapp/inbound`, `whatsapp/outbound`, `web-heartbeat`, `web-reconnect`.
- 日志文件: `/tmp/openclaw/openclaw-YYYY-MM-DD.log` (可配置).
- 故障排除指南: [网关故障排除](/gateway/troubleshooting).

## 故障排除 (快速)

**未链接 / 需要QR登录**

- 症状: `channels status` 显示 `linked: false` 或警告“未链接”。
- 解决方法: 在网关主机上运行 `openclaw channels login` 并扫描QR码 (WhatsApp → 设置 → 已连接设备).

**已链接但断开 / 重新连接循环**

- 症状: `channels status` 显示 `running, disconnected` 或警告“已链接但断开”。
- 解决方法: `openclaw doctor` (或重启网关). 如果问题持续存在，请通过 `channels login` 重新链接并检查 `openclaw logs --follow`.

**Bun 运行时**

- 不建议使用 **Bun**。WhatsApp (Baileys) 和 Telegram 在 Bun 上不可靠。
  使用 **Node** 运行网关。(参见入门指南中的运行时说明.)