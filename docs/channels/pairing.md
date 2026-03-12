---
summary: "Pairing overview: approve who can DM you + which nodes can join"
read_when:
  - Setting up DM access control
  - Pairing a new iOS/Android node
  - Reviewing OpenClaw security posture
title: "Pairing"
---
# 配对（Pairing）

“配对”是 OpenClaw 中明确的**所有者审批**步骤。  
它在以下两个场景中使用：

1. **私信配对**（允许哪些用户与机器人对话）  
2. **节点配对**（允许哪些设备/节点加入网关网络）

安全上下文：[安全](/gateway/security)

## 1) 私信配对（入站聊天访问）

当某个频道配置了私信策略 `pairing` 时，未知发送者会收到一个短代码，且其消息在您批准前**不会被处理**。

默认私信策略详见：[安全](/gateway/security)

配对代码：

- 共 8 个字符，全部为大写字母，不含易混淆字符（`0O1I`）。  
- **1 小时后过期**。机器人仅在创建新请求时发送配对消息（每个发送者约每小时一次）。  
- 默认情况下，每个频道最多允许 **3 个待处理的私信配对请求**；超出数量的新请求将被忽略，直至已有请求过期或获得批准。

### 批准发送者

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

支持的频道：`telegram`、`whatsapp`、`signal`、`imessage`、`discord`、`slack`、`feishu`。

### 状态存储位置

存储于 `~/.openclaw/credentials/` 下：

- 待处理请求：`<channel>-pairing.json`  
- 已批准白名单存储：  
  - 默认账户：`<channel>-allowFrom.json`  
  - 非默认账户：`<channel>-<accountId>-allowFrom.json`  

账户作用域行为说明：

- 非默认账户仅读写其作用域内的白名单文件。  
- 默认账户使用频道作用域下的无作用域白名单文件。

请将这些文件视为敏感信息（它们控制着对您助手的访问权限）。

## 2) 节点设备配对（iOS / Android / macOS / 无头节点）

节点以带有 `role: node` 的**设备**身份连接至网关。网关会生成一条设备配对请求，该请求必须经您批准。

### 通过 Telegram 配对（推荐用于 iOS）

若您使用 `device-pair` 插件，则可完全在 Telegram 中完成首次设备配对：

1. 在 Telegram 中向您的机器人发送消息：`/pair`  
2. 机器人将回复两条消息：一条操作说明消息，以及一条单独的**设置代码**消息（Telegram 中便于复制粘贴）。  
3. 在您的手机上，打开 OpenClaw iOS 应用 → 设置 → 网关。  
4. 粘贴设置代码并连接。  
5. 返回 Telegram：`/pair approve`  

该设置代码是一个 base64 编码的 JSON 负载，其中包含：

- `url`：网关 WebSocket 地址（`ws://...` 或 `wss://...`）  
- `token`：短期有效的配对令牌  

在有效期内，请将设置代码视同密码妥善保管。

### 批准节点设备

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw devices reject <requestId>
```

### 节点配对状态存储

存储于 `~/.openclaw/devices/` 下：

- `pending.json`（短期有效；待处理请求会过期）  
- `paired.json`（已配对设备及其令牌）

### 补充说明

- 已废弃的 `node.pair.*` API（命令行工具：`openclaw nodes pending/approve`）使用一个独立的、由网关管理的配对存储。WebSocket 节点仍需进行设备配对。

## 相关文档

- 安全模型 + 提示注入防护：[安全](/gateway/security)  
- 安全更新（运行 doctor）：[更新](/install/updating)  
- 频道配置：  
  - Telegram：[Telegram](/channels/telegram)  
  - WhatsApp：[WhatsApp](/channels/whatsapp)  
  - Signal：[Signal](/channels/signal)  
  - BlueBubbles（iMessage）：[BlueBubbles](/channels/bluebubbles)  
  - iMessage（旧版）：[iMessage](/channels/imessage)  
  - Discord：[Discord](/channels/discord)  
  - Slack：[Slack](/channels/slack)