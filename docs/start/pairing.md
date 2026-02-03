---
summary: "Pairing overview: approve who can DM you + which nodes can join"
read_when:
  - Setting up DM access control
  - Pairing a new iOS/Android node
  - Reviewing OpenClaw security posture
title: "Pairing"
---
# 配对

“配对”是 OpenClaw 的显式 **所有者批准** 步骤。
它用于两个地方：

1. **DM 配对**（允许谁与机器人通信）
2. **节点配对**（允许哪些设备/节点加入网关网络）

安全上下文：[安全](/gateway/security)

## 1) DM 配对（入站聊天访问）

当通道配置为 DM 策略 `pairing` 时，未知发送者会收到一个短代码，其消息在您批准之前 **不会被处理**。

默认的 DM 策略文档见：[安全](/gateway/security)

配对代码：

- 8 个字符，大写，不含易混淆字符（`0O1I`）。
- **1 小时后过期**。机器人仅在新请求创建时发送配对消息（每小时每发送者大致发送一次）。
- 默认情况下，待处理的 DM 配对请求每通道最多 **3 个**；额外请求会被忽略，直到其中一个过期或被批准。

### 批准发送者

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

支持的通道：`telegram`, `whatsapp`, `signal`, `imessage`, `discord`, `slack`。

### 状态存储位置

存储在 `~/.openclaw/credentials/` 下：

- 待处理请求：`<channel>-pairing.json`
- 已批准的允许列表存储：`<channel>-allowFrom.json`

将这些视为敏感信息（它们控制对您助手的访问权限）。

## 2) 节点设备配对（iOS/Android/macOS/无头节点）

节点以 **设备** 的身份连接到网关，`role: node`。网关会创建一个必须被批准的设备配对请求。

### 批准节点设备

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw devices reject <requestId>
```

### 状态存储位置

存储在 `~/.openclaw/devices/` 下：

- `pending.json`（短生命周期；待处理请求会过期）
- `paired.json`（已配对的设备 + 令牌）

### 注意事项

- 遗留的 `node.pair.*` API（CLI: `openclaw nodes pending/approve`）是一个独立的网关所有配对存储。WS 节点仍需要设备配对。

## 相关文档

- 安全模型 + 提示注入：[安全](/gateway/security)
- 安全更新（运行医生）：[更新](/install/updating)
- 通道配置：
  - Telegram：[Telegram](/channels/telegram)
  - WhatsApp：[WhatsApp](/channels/whatsapp)
  - Signal：[Signal](/channels/signal)
  - iMessage：[iMessage](/channels/imessage)
  - Discord：[Discord](/channels/discord)
  - Slack：[Slack](/channels/slack)