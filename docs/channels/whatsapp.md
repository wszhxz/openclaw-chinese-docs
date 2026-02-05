---
summary: "WhatsApp (web channel) integration: login, inbox, replies, media, and ops"
read_when:
  - Working on WhatsApp/web channel behavior or inbox routing
title: "WhatsApp"
---
# WhatsApp (web channel)

状态：仅通过 Baileys 使用 WhatsApp Web。网关拥有会话。

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

- 单个网关进程中运行多个 WhatsApp 账户（多账户）。
- 确定性路由：回复返回到 WhatsApp，不进行模型路由。
- 模型有足够的上下文来理解引用回复。

## 配置写入

默认情况下，WhatsApp 允许由 `/config set|unset` 触发的配置更新写入（需要 `commands.config: true`）。

禁用方式：

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

WhatsApp 需要一个真实的移动号码进行验证。VoIP 和虚拟号码通常会被阻止。在 WhatsApp 上运行 OpenClaw 有两种支持的方式：

### 专用号码（推荐）

为 OpenClaw 使用一个**独立的电话号码**。最佳用户体验，清晰的路由，没有自我聊天的奇怪行为。理想设置：**备用/旧 Android 手机 + eSIM**。将其留在 Wi-Fi 和电源开启状态，并通过二维码链接。

**WhatsApp Business:** 您可以在同一设备上使用不同的号码运行 WhatsApp Business。非常适合将您的个人 WhatsApp 与助手分开——安装 WhatsApp Business 并在其中注册 OpenClaw 号码。

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
如果您希望使用配对而不是白名单，将 `channels.whatsapp.dmPolicy` 设置为 `pairing`。未知发送者会收到一个配对代码；通过以下方式批准：
`openclaw pairing approve whatsapp <code>`

### 个人号码（备用）

快速备用方案：在**您自己的号码**上运行 OpenClaw。测试时给自己发送消息（WhatsApp“给自己发送消息”），以免骚扰联系人。在设置和实验期间，预期需要在主手机上读取验证码。**必须启用自我聊天模式。**
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

自我聊天回复默认设置为 `[{identity.name}]` 当设置时（否则 `[openclaw]`）
如果 `messages.responsePrefix` 未设置。显式设置以自定义或禁用
前缀（使用 `""` 移除它）。

### 号码获取提示

- **本地 eSIM** 来自您国家的移动运营商（最可靠）
  - 奥地利: [hot.at](https://www.hot.at)
  - 英国: [giffgaff](https://www.giffgaff.com) — 免费 SIM，无合同
- **预付费 SIM** — 便宜，只需接收一条短信用于验证

**避免:** TextNow, Google Voice, 大多数“免费短信”服务 — WhatsApp 会积极阻止这些服务。

**提示:** 该号码只需要接收一条验证短信。之后，WhatsApp Web 会话通过 `creds.json` 持续。

## 为什么不用 Twilio？

- 早期的 OpenClaw 构建支持 Twilio 的 WhatsApp Business 集成。
- WhatsApp Business 号码不适合个人助理。
- Meta 强制执行 24 小时回复窗口；如果您在过去 24 小时内没有回复，业务号码将无法发起新消息。
- 高流量或“聊天式”使用会触发积极阻止，因为业务账户不打算发送数十条个人助理消息。
- 结果：不可靠的传递和频繁的阻止，因此支持被移除。

## 登录 + 凭证

- 登录命令：`openclaw channels login`（通过已连接设备的 QR）。
- 多账户登录：`openclaw channels login --account <id>` (`<id>` = `accountId`)。
- 默认账户（当省略 `--account` 时）：如果存在则为 `default`，否则为第一个配置的账户 ID（按排序）。
- 凭证存储在 `~/.openclaw/credentials/whatsapp/<accountId>/creds.json`。
- 备份副本在 `creds.json.bak`（损坏时恢复）。
- 向后兼容性：较早的安装直接在 `~/.openclaw/credentials/` 存储 Baileys 文件。
- 登出：`openclaw channels logout`（或 `--account <id>`）删除 WhatsApp 认证状态（但保留共享 `oauth.json`）。
- 已登出套接字 => 错误指示重新链接。

## 入站流程（私信 + 群组）

- WhatsApp 事件来自 `messages.upsert`（Baileys）。
- 关闭时分离收件箱监听器，以避免在测试/重启中累积事件处理程序。
- 忽略状态/广播聊天。
- 直接聊天使用 E.164；群组使用群组 JID。
- **私信策略**：`channels.whatsapp.dmPolicy` 控制直接聊天访问（默认：`pairing`）。
  - 配对：未知发送者会收到一个配对代码（通过 `openclaw pairing approve whatsapp <code>` 批准；代码在一小时后过期）。
  - 开放：需要 `channels.whatsapp.allowFrom` 包含 `"*"`。
  - 您的已连接 WhatsApp 号码隐式受信任，因此自我消息跳过 ⁠`channels.whatsapp.dmPolicy` 和 `channels.whatsapp.allowFrom` 检查。

### 个人号码模式（备用）

如果您在**个人 WhatsApp 号码**上运行 OpenClaw，请启用 `channels.whatsapp.selfChatMode`（见上面的示例）。

行为：

- 发出的私信永远不会触发配对回复（防止骚扰联系人）。
- 收到的未知发送者仍然遵循 `channels.whatsapp.dmPolicy`。
- 自我聊天模式（allowFrom 包含您的号码）避免自动阅读回执并忽略提及 JID。
- 发送非自我聊天私信的阅读回执。

## 阅读回执

默认情况下，网关会在接受传入的 WhatsApp 消息后将其标记为已读（蓝色勾号）。

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

注意：

- 自我聊天模式始终跳过阅读回执。

## WhatsApp 常见问题解答：发送消息 + 配对

**当我链接 WhatsApp 时，OpenClaw 会向随机联系人发送消息吗？**  
不。默认私信策略是**配对**，因此未知发送者只会收到一个配对代码且其消息**不会被处理**。OpenClaw 仅回复收到的聊天，或您明确触发的发送（代理/CLI）。

**WhatsApp 上的配对是如何工作的？**  
配对是对未知发送者的私信门：

- 新发送者的第一次私信会返回一个短代码（消息不会被处理）。
- 通过以下方式批准：`openclaw pairing approve whatsapp <code>`（列表使用 `openclaw pairing list whatsapp`）。
- 代码在一小时后过期；待处理请求每个通道最多 3 个。

**多人是否可以使用同一个 WhatsApp 号码上的不同 OpenClaw 实例？**  
可以，通过将每个发送者路由到不同的代理来实现 `bindings`（对等 `kind: "dm"`，发送者 E.164 如 `+15551234567`）。回复仍然来自**相同的 WhatsApp 账户**，直接聊天合并到每个代理的主要会话中，因此请**每人使用一个代理**。私信访问控制 (`dmPolicy`/`allowFrom`) 对每个 WhatsApp 账户是全局的。参见 [多代理路由](/concepts/multi-agent)。

**为什么向导会要求我的电话号码？**  
向导使用它来设置您的**白名单/所有者**，以便允许您的私信。它不会用于自动发送。如果您在个人 WhatsApp 号码上运行，请使用相同的号码并启用 `channels.whatsapp.selfChatMode`。

## 消息标准化（模型看到的内容）

- `Body` 是当前消息正文及其信封。
- 引用回复上下文**总是附加**：
  ```
  [Replying to +1555 id:ABC123]
  <quoted text or <media:...>>
  [/Replying]
  ```
- 回复元数据也设置：
  - `ReplyToId` = stanzaId
  - `ReplyToBody` = 引用正文或媒体占位符
  - `ReplyToSender` = 已知时为 E.164
- 仅媒体的传入消息使用占位符：
  - `<media:image|video|audio|document|sticker>`

## 群组

- 群组映射到 `agent:<agentId>:whatsapp:group:<jid>` 会话。
- 群组策略：`channels.whatsapp.groupPolicy = open|disabled|allowlist`（默认 `allowlist`）。
- 激活模式：
  - `mention`（默认）：需要 @提及或正则表达式匹配。
  - `always`：总是触发。
- `/activation mention|always` 仅限所有者且必须作为单独消息发送。
- 所有者 = `channels.whatsapp.allowFrom`（或未设置时为自身 E.164）。
- **历史注入**（仅限待处理）：
  - 最近的 _未处理_ 消息（默认 50 条）插入在：
    `[Chat messages since your last reply - for context]`（会话中已有的消息不会重新注入）
  - 当前消息插入在：
    `[Current message - respond to this]`
  - 发送者后缀附加：`[from: Name (+E164)]`
- 群组元数据缓存 5 分钟（主题 + 参与者）。

## 回复传递（线程）

- WhatsApp Web 发送标准消息（当前网关中没有引用回复线程）。
- 此通道忽略回复标签。

## 确认反应（接收时自动反应）

WhatsApp 可以在接收到消息后立即自动发送表情符号反应，在机器人生成回复之前。这为用户提供即时反馈，表明他们的消息已被接收。

**配置：**

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

**选项：**

- `emoji`（字符串）：用于确认的表情符号（例如，“👀”，“✅”，“📨”）。空或省略 = 功能禁用。
- `direct`（布尔值，默认：`true`）：在直接/私信聊天中发送反应。
- `group`（字符串，默认：`"mentions"`）：群组聊天行为：
  - `"always"`：对所有群组消息反应（即使没有 @提及）
  - `"mentions"`：仅在机器人被 @提及时反应
  - `"never"`：从不在群组中反应

**按账户覆盖：**

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

**行为说明：**

- 反应会在**接收到消息后立即**发送，在输入指示器或机器人回复之前。
- 在具有 `requireMention: false`（激活：总是）的群组中，`group: "mentions"` 将对所有消息反应（而不仅仅是 @提及）。
- 一次性操作：反应失败会被记录，但不会阻止机器人回复。
- 参与者 JID 会自动包含在群组反应中。
- WhatsApp 忽略 `messages.ackReaction`；使用 `channels.whatsapp.ackReaction` 代替。

## 代理工具（反应）

- 工具：`whatsapp` 带 `react` 操作 (`chatJid`, `messageId`, `emoji`, 可选 `remove`)。
- 可选：`participant`（群组发送者），`fromMe`（对自己消息的反应），`accountId`（多账户）。
- 反应移除语义：参见 [/tools/reactions](/tools/reactions)。
- 工具门控：`channels.whatsapp.actions.reactions`（默认：启用）。

## 限制

- 发出的文本被分块为 `channels.whatsapp.textChunkLimit`（默认 4000）。
- 可选换行分块：设置 `channels.whatsapp.chunkMode="newline"` 在长度分块前按空白行（段落边界）拆分。
- 传入媒体保存限制为 `channels.whatsapp.mediaMaxMb`（默认 50 MB）。
- 发出的媒体项目限制为 `agents.defaults.mediaMaxMb`（默认 5 MB）。

## 发送消息（文本 + 媒体）

- 使用活动 Web 监听器；如果网关未运行则错误。
- 文本分块：每条消息最多 4k（可通过 `channels.whatsapp.textChunkLimit` 配置，可选 `channels.whatsapp.chunkMode`）。
- 媒体：
  - 支持图像/视频/音频/文档。
  - 音频作为语音消息（PTT）发送；`audio/ogg` => `audio/ogg; codecs=opus`。
  - 仅第一项媒体有标题。
  - 媒体获取支持 HTTP(S) 和本地路径。
  - 动态 GIF：WhatsApp 期望带有 `gifPlayback: true` 的 MP4 以实现内联循环。
    - CLI: `openclaw message send --media <mp4> --gif-playback`
    - 网关: `send` 参数包括 `gifPlayback: true`

## 语音消息（PTT 音频）

WhatsApp 以**语音消息**（PTT 气泡）发送音频。

- 最佳效果：OGG/Opus。OpenClaw 将 `audio/ogg` 重写为 `audio/ogg; codecs=opus`。
- `[[audio_as_voice]]` 对 WhatsApp 无效（音频已经作为语音消息发送）。

## 媒体限制 + 优化

- 默认发出限制：5 MB（每项媒体）。
- 覆盖：`agents.defaults.mediaMaxMb`。
- 图像在限制下自动优化为 JPEG（调整大小 + 质量扫描）。
- 超尺寸媒体 => 错误；媒体回复回退为文本警告。

## 心跳

- **网关心跳** 记录连接健康状况 (`web.heartbeatSeconds`，默认 60 秒）。
- **代理心跳** 可以按代理配置 (`agents.list[].heartbeat`) 或全局
  通过 `agents.defaults.heartbeat` 配置（当没有按代理条目时为后备）。
  - 使用配置的心跳提示（默认：`Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`）+ `HEARTBEAT_OK` 跳过行为。
  - 传递默认为最后使用的通道（或配置的目标）。

## 重新连接行为

- 退避策略：`web.reconnect`：
  - `initialMs`，`maxMs`，`factor`，`jitter`，`maxAttempts`。
- 如果达到 maxAttempts，Web 监控停止（降级）。
- 已登出 => 停止并要求重新链接。

## 配置快速映射

- `channels.whatsapp.dmPolicy`（私信策略：配对/白名单/开放/禁用）。
- `channels.whatsapp.selfChatMode`（同号码设置；机器人使用您的个人 WhatsApp 号码）。
- `channels.whatsapp.allowFrom`（私信白名单）。WhatsApp 使用 E.164 电话号码（无用户名）。
- `channels.whatsapp.mediaMaxMb`（传入媒体保存限制）。
- `channels.whatsapp.ackReaction`（消息接收时自动反应：`{emoji, direct, group}`）。
- `channels.whatsapp.accounts.<accountId>.*`（按账户设置 + 可选 `authDir`）。
- `channels.whatsapp.accounts.<accountId>.mediaMaxMb`（按账户传入媒体限制）。
- `channels.whatsapp.accounts.<accountId>.ackReaction`（按账户确认反应覆盖）。
- `channels.whatsapp.groupAllowFrom`（群组发送者白名单）。
- `channels.whatsapp.groupPolicy`（群组策略）。
- `channels.whatsapp.historyLimit` / `channels.whatsapp.accounts.<accountId>.historyLimit`（群组历史上下文；`0` 禁用）。
- `channels.whatsapp.dmHistoryLimit`（私信历史限制在用户回合）。按用户覆盖：`channels.whatsapp.dms["<phone>"].historyLimit`。
- `channels.whatsapp.groups`（群组白名单 + 提及门控默认；使用 `"*"` 允许全部）
- `channels.whatsapp.actions.reactions`（门控 WhatsApp 工具反应）。
- `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）
- `messages.groupChat.historyLimit`
- `channels.whatsapp.messagePrefix`（传入前缀；按账户：`channels.whatsapp.accounts.<accountId>.messagePrefix`；已弃用：`messages.messagePrefix`）
- `messages.responsePrefix`