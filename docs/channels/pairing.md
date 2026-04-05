---
summary: "Pairing overview: approve who can DM you + which nodes can join"
read_when:
  - Setting up DM access control
  - Pairing a new iOS/Android node
  - Reviewing OpenClaw security posture
title: "Pairing"
---
# 配对

“配对”是 OpenClaw 明确的**所有者审批**步骤。
它用于以下两个位置：

1. **DM 配对**（允许与机器人对话的对象）
2. **节点配对**（哪些设备/节点被允许加入网关网络）

安全上下文：[安全](/gateway/security)

## 1) DM 配对（入站聊天访问）

当频道配置为 DM 策略 `pairing` 时，未知发送者会获得一个短代码，且他们的消息在您批准之前**不会被处理**。

默认 DM 策略记录在：[安全](/gateway/security)

配对代码：

- 8 个字符，大写，无歧义字符 (`0O1I`)。
- **1 小时后过期**。机器人仅在创建新请求时发送配对消息（每个发送者每小时约一次）。
- 默认的待处理 DM 配对请求上限为 **每个频道 3 个**；额外的请求将被忽略，直到其中一个过期或被批准。

### 批准发送者

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

支持的频道：`bluebubbles`, `discord`, `feishu`, `googlechat`, `imessage`, `irc`, `line`, `matrix`, `mattermost`, `msteams`, `nextcloud-talk`, `nostr`, `openclaw-weixin`, `signal`, `slack`, `synology-chat`, `telegram`, `twitch`, `whatsapp`, `zalo`, `zalouser`。

### 状态存储位置

存储在 `~/.openclaw/credentials/` 下：

- 待处理请求：`<channel>-pairing.json`
- 已批准白名单存储：
  - 默认账户：`<channel>-allowFrom.json`
  - 非默认账户：`<channel>-<accountId>-allowFrom.json`

账户范围行为：

- 非默认账户仅读取/写入其范围白名单文件。
- 默认账户使用频道范围的未限定白名单文件。

将其视为敏感信息（它们控制对您助手的访问权限）。

重要提示：此存储用于 DM 访问。群组授权是分开的。
批准 DM 配对代码不会自动允许该发送者在群组中运行群组命令或控制机器人在群组中的操作。对于群组访问，请配置频道的显式群组白名单（例如 `groupAllowFrom`, `groups`, 或根据频道进行每组/每主题的覆盖）。

## 2) 节点设备配对（iOS/Android/macOS/无头节点）

节点作为**设备**通过 `role: node` 连接到网关。网关创建一个必须批准的配对请求。

### 通过 Telegram 配对（推荐用于 iOS）

如果您使用 `device-pair` 插件，您可以完全从 Telegram 进行首次设备配对：

1. 在 Telegram 中，向您的机器人发送消息：`/pair`
2. 机器人回复两条消息：一条指令消息和一条单独的**设置代码**消息（在 Telegram 中易于复制/粘贴）。
3. 在手机上，打开 OpenClaw iOS 应用 → 设置 → 网关。
4. 粘贴设置代码并连接。
5. 回到 Telegram：`/pair pending`（审查请求 ID、角色和范围），然后批准。

设置代码是一个 base64 编码的 JSON 负载，包含：

- `url`：网关 WebSocket URL (`ws://...` 或 `wss://...`)
- `bootstrapToken`：用于初始配对握手的短期单设备引导令牌

该引导令牌携带内置的配对引导配置文件：

- 主要移交的 `node` 令牌保持 `scopes: []`
- 任何移交的 `operator` 令牌保持绑定到引导白名单：
  `operator.approvals`, `operator.read`, `operator.talk.secrets`, `operator.write`
- 引导范围检查是按角色前缀的，而不是一个扁平的范围池：
  操作员范围条目仅满足操作员请求，非操作员角色仍必须在其自己的角色前缀下请求范围

在有效期间，将设置代码视为密码。

### 批准节点设备

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw devices reject <requestId>
```

如果同一设备使用不同的认证详细信息重试（例如不同的角色/范围/公钥），之前的待处理请求将被取代，并创建一个新的 `requestId`。

### 节点配对状态存储

存储在 `~/.openclaw/devices/` 下：

- `pending.json`（短期有效；待处理请求过期）
- `paired.json`（配对的设备 + 令牌）

### 注意事项

- 旧的 `node.pair.*` API（CLI: `openclaw nodes pending|approve|reject|rename`）是一个独立的网关拥有的配对存储。WS 节点仍然需要设备配对。
- 配对记录是已批准角色的持久化事实来源。活动设备令牌保持绑定到该已批准角色集；超出已批准角色的孤立令牌条目不会创建新的访问权限。

## 相关文档

- 安全模型 + 提示注入：[安全](/gateway/security)
- 安全更新（运行 doctor）：[更新](/install/updating)
- 频道配置：
  - Telegram: [Telegram](/channels/telegram)
  - WhatsApp: [WhatsApp](/channels/whatsapp)
  - Signal: [Signal](/channels/signal)
  - BlueBubbles (iMessage): [BlueBubbles](/channels/bluebubbles)
  - iMessage (legacy): [iMessage](/channels/imessage)
  - Discord: [Discord](/channels/discord)
  - Slack: [Slack](/channels/slack)