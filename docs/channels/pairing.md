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
它用于两个地方：

1. **DM 配对**（谁被允许与机器人交谈）
2. **节点配对**（哪些设备/节点被允许加入网关网络）

安全上下文：[安全](/gateway/security)

## 1) DM 配对（入站聊天访问）

当通道配置为 DM 策略 `pairing` 时，未知发送者会获得一个短代码，且他们的消息在您批准之前**不会被处理**。

默认 DM 策略记录在：[安全](/gateway/security)

配对代码：

- 8 个字符，大写，无歧义字符 (`0O1I`)。
- **1 小时后过期**。机器人仅在创建新请求时发送配对消息（每个发送者大约每小时一次）。
- 默认的待处理 DM 配对请求上限为**每个通道 3 个**；额外的请求将被忽略，直到其中一个过期或被批准。

### 批准发送者

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

支持的通道：`telegram`, `whatsapp`, `signal`, `imessage`, `discord`, `slack`, `feishu`。

### 状态存储位置

存储在 `~/.openclaw/credentials/` 下：

- 待处理请求：`<channel>-pairing.json`
- 已批准白名单存储：
  - 默认账户：`<channel>-allowFrom.json`
  - 非默认账户：`<channel>-<accountId>-allowFrom.json`

账户范围行为：

- 非默认账户仅读写其作用域内的白名单文件。
- 默认账户使用通道作用域的未作用域白名单文件。

将这些视为敏感信息（它们控制对您助手的访问权限）。

## 2) 节点设备配对（iOS/Android/macOS/headless 节点）

节点作为**设备**连接到网关，使用 `role: node`。网关创建一个必须批准的配对请求。

### 通过 Telegram 配对（推荐用于 iOS）

如果您使用 `device-pair` 插件，您可以完全从 Telegram 进行首次设备配对：

1. 在 Telegram 中，向您的机器人发送消息：`/pair`
2. 机器人回复两条消息：一条指令消息和一条单独的**设置代码**消息（在 Telegram 中易于复制/粘贴）。
3. 在您的手机上，打开 OpenClaw iOS 应用 → 设置 → 网关。
4. 粘贴设置代码并连接。
5. 回到 Telegram：`/pair approve`

设置代码是一个 base64 编码的 JSON 负载，包含：

- `url`：网关 WebSocket URL (`ws://...` 或 `wss://...`)
- `token`：短期配对令牌

在有效期间，将设置代码视为密码。

### 批准节点设备

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw devices reject <requestId>
```

### 节点配对状态存储

存储在 `~/.openclaw/devices/` 下：

- `pending.json`（短期有效；待处理请求会过期）
- `paired.json`（已配对设备 + 令牌）

### 注意

- 遗留的 `node.pair.*` API（CLI: `openclaw nodes pending/approve`）是一个独立的网关拥有的配对存储。WS 节点仍然需要设备配对。

## 相关文档

- 安全模型 + 提示注入：[安全](/gateway/security)
- 安全更新（运行 doctor）：[更新](/install/updating)
- 通道配置：
  - Telegram: [Telegram](/channels/telegram)
  - WhatsApp: [WhatsApp](/channels/whatsapp)
  - Signal: [Signal](/channels/signal)
  - BlueBubbles (iMessage): [BlueBubbles](/channels/bluebubbles)
  - iMessage (legacy): [iMessage](/channels/imessage)
  - Discord: [Discord](/channels/discord)
  - Slack: [Slack](/channels/slack)