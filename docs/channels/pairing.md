---
summary: "Pairing overview: approve who can DM you + which nodes can join"
read_when:
  - Setting up DM access control
  - Pairing a new iOS/Android node
  - Reviewing OpenClaw security posture
title: "Pairing"
---
# 配对

“配对”是OpenClaw的显式**所有者批准**步骤。
它在两个地方使用：

1. **DM配对**（谁被允许与机器人对话）
2. **节点配对**（哪些设备/节点被允许加入网关网络）

安全上下文：[Security](/gateway/security)

## 1) DM配对（入站聊天访问）

当一个频道配置了DM策略`pairing`，未知发送者会收到一个短码，他们的消息在你批准之前**不会被处理**。

默认的DM策略记录在：[Security](/gateway/security)

配对码：

- 8个字符，大写，无歧义字符 (`0O1I`)。
- **1小时后过期**。机器人仅在创建新请求时发送配对消息（大约每小时每个发送者一次）。
- 待处理的DM配对请求默认限制为**每个频道3个**；额外的请求会被忽略，直到其中一个过期或被批准。

### 批准发送者

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

支持的频道：`telegram`，`whatsapp`，`signal`，`imessage`，`discord`，`slack`。

### 状态存储位置

存储在`~/.openclaw/credentials/`下：

- 待处理请求：`<channel>-pairing.json`
- 已批准的白名单存储：`<channel>-allowFrom.json`

将这些视为敏感信息（它们控制对你助手的访问）。

## 2) 节点设备配对（iOS/Android/macOS/无头节点）

节点以**设备**身份使用`role: node`连接到网关。网关
创建一个设备配对请求，必须获得批准。

### 通过Telegram配对（推荐用于iOS）

如果你使用`device-pair`插件，你可以完全从Telegram进行首次设备配对：

1. 在Telegram中，向你的机器人发送消息：`/pair`
2. 机器人回复两条消息：一条指令消息和一条单独的**设置码**消息（在Telegram中易于复制/粘贴）。
3. 在你的手机上，打开OpenClaw iOS应用 → 设置 → 网关。
4. 粘贴设置码并连接。
5. 回到Telegram：`/pair approve`

设置码是一个包含以下内容的base64编码JSON负载：

- `url`：网关WebSocket URL (`ws://...` 或 `wss://...`)
- `token`：短期配对令牌

在有效期内将设置码视为密码。

### 批准节点设备

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw devices reject <requestId>
```

### 节点配对状态存储

存储在`~/.openclaw/devices/`下：

- `pending.json`（短期；待处理请求过期）
- `paired.json`（已配对的设备+令牌）

### 注意事项

- 旧版`node.pair.*` API（CLI: `openclaw nodes pending/approve`) 是一个
  独立的网关拥有的配对存储。WS节点仍然需要设备配对。

## 相关文档

- 安全模型 + 提示注入：[Security](/gateway/security)
- 安全更新（运行doctor）：[Updating](/install/updating)
- 频道配置：
  - Telegram: [Telegram](/channels/telegram)
  - WhatsApp: [WhatsApp](/channels/whatsapp)
  - Signal: [Signal](/channels/signal)
  - BlueBubbles (iMessage): [BlueBubbles](/channels/bluebubbles)
  - iMessage (旧版): [iMessage](/channels/imessage)
  - Discord: [Discord](/channels/discord)
  - Slack: [Slack](/channels/slack)