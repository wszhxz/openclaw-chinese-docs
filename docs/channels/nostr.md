---
summary: "Nostr DM channel via NIP-04 encrypted messages"
read_when:
  - You want OpenClaw to receive DMs via Nostr
  - You're setting up decentralized messaging
title: "Nostr"
---
# Nostr

**状态：** 可选插件（默认禁用）。

Nostr 是一个去中心化的社交网络协议。此频道使 OpenClaw 能够通过 NIP-04 接收和回复加密的直接消息（DM）。

## 安装（按需）

### 入门（推荐）

- 入门向导（`openclaw onboard`）和 `openclaw channels add` 列出可选的频道插件。
- 选择 Nostr 会提示您按需安装插件。

安装默认值：

- **开发频道 + git 检出可用：** 使用本地插件路径。
- **稳定版/测试版：** 从 npm 下载。

您始终可以在提示中覆盖选择。

### 手动安装

```bash
openclaw plugins install @openclaw/nostr
```

使用本地检出（开发工作流程）：

```bash
openclaw plugins install --link <path-to-openclaw>/extensions/nostr
```

安装或启用插件后重启网关。

## 快速设置

1. 生成 Nostr 密钥对（如需）：

```bash
# 使用 nak
nak key generate
```

2. 添加到配置：

```json
{
  "channels": {
    "nostr": {
      "privateKey": "${NOSTR_PRIVATE_KEY}"
    }
  }
}
```

3. 导出密钥：

```bash
export NOSTR_PRIVATE_KEY="nsec1..."
```

4. 重启网关。

## 配置参考

| 键         | 类型     | 默认值                                       | 描述                         |
|------------|----------|--------------------------------------------|------------------------------|
| `privateKey` | 字符串   | 必填                                       | `nsec` 或 hex 格式的私钥     |
| `relays`     | 字符串[] | `['wss://relay.damus.io', 'wss://nos.lol']` | 中继 URL（WebSocket）        |
| `dmPolicy`   | 字符串   | `pairing`                                  | DM 访问策略                  |
| `allowFrom`  | 字符串[] | `[]`                                        | 允许的发送方公钥             |
| `enabled`    | 布尔值   | `true`                                      | 启用/禁用频道                |
| `name`       | 字符串   | -                                           | 显示名称                     |
| `profile`    | 对象     | -                                           | NIP-01 配置元数据            |

## 配置元数据

配置元数据作为 NIP-01 `kind:0` 事件发布。您可以通过控制界面（频道 -> Nostr -> 配置）进行管理，或直接在配置中设置。

示例：

```json
{
  "channels": {
    "nostr": {
      "privateKey": "${NOSTR_PRIVATE_KEY}",
      "profile": {
        "name": "openclaw",
        "displayName": "OpenClaw",
        "about": "个人助理 DM 机器人",
        "picture": "https://example.com/avatar.png",
        "banner": "https://example.com/banner.png",
        "website": "https://example.com",
        "nip05": "openclaw@example.com",
        "lud16": "openclaw@example.com"
      }
    }
  }
}
```

说明：

- 配置 URL 必须使用 `https://`。
- 从中继导入会合并字段并保留本地覆盖。

## 访问控制

### DM 策略

- **配对**（默认）：未知发送者会收到配对码。
- **允许列表**：只有 `allowFrom` 中的公钥可以发送 DM。
- **公开**：公共入站 DM（需要 `allowFrom: ["*"]`）。
- **禁用**：忽略入站 DM。

### 允许列表示例

```json
{
  "channels": {
    "nostr": {
      "privateKey": "${NOSTR_PRIVATE_KEY}",
      "dmPolicy": "allowlist",
      "allowFrom": ["npub1abc...", "npub1xyz..."]
    }
  }
}
```

## 密钥格式

接受的格式：

- **私钥：** `nsec...` 或 64 字符 hex
- **公钥（`allowFrom`）：** `npub...` 或 hex

## 中继

默认值：`relay.damus.io` 和 `nos.lol`。

```json
{
  "channels": {
    "nostr": {
      "privateKey": "${NOSTR_PRIVATE_KEY}",
      "relays": ["wss://relay.damus.io", "wss://relay.primal.net", "wss://nostr.wine"]
    }
  }
}
```

提示：

- 使用 2-3 个中继以实现冗余。
- 避免使用过多中继（延迟、重复）。
- 支付的中继可以提高可靠性。
- 本地中继适合测试（`ws://localhost:7777`）。

## 协议支持

| NIP    | 状态    | 描述                           |
|--------|---------|--------------------------------|
| NIP-01 | 支持    | 基本事件格式 + 配置元数据      |
| NIP-04 | 支持    | 加密的 DM（`kind:4`）           |
| NIP-17 | 计划    |