---
summary: "Nostr DM channel via NIP-04 encrypted messages"
read_when:
  - You want OpenClaw to receive DMs via Nostr
  - You're setting up decentralized messaging
title: "Nostr"
---
# Nostr

**状态:** 可选插件（默认禁用）。

Nostr 是一个去中心化的社交网络协议。此通道使 OpenClaw 能够通过 NIP-04 接收和响应加密的直接消息（DM）。

## 安装（按需）

### 入门（推荐）

- 入门向导 (`openclaw onboard`) 和 `openclaw channels add` 列出可选的通道插件。
- 选择 Nostr 会提示您按需安装插件。

安装默认设置：

- **开发渠道 + git 检出可用:** 使用本地插件路径。
- **稳定/测试版:** 从 npm 下载。

您始终可以覆盖提示中的选择。

### 手动安装

```bash
openclaw plugins install @openclaw/nostr
```

使用本地检出（开发工作流）：

```bash
openclaw plugins install --link <path-to-openclaw>/extensions/nostr
```

安装或启用插件后重启网关。

## 快速设置

1. 生成 Nostr 密钥对（如果需要）：

```bash
# Using nak
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

| 键          | 类型     | 默认                                     | 描述                         |
| ------------ | -------- | ------------------------------------------- | ----------------------------------- |
| `privateKey` | string   | required                                    | 私钥在 `nsec` 或十六进制格式 |
| `relays`     | string[] | `['wss://relay.damus.io', 'wss://nos.lol']` | 中继 URL（WebSocket）              |
| `dmPolicy`   | string   | `pairing`                                   | DM 访问策略                    |
| `allowFrom`  | string[] | `[]`                                        | 允许的发送者公钥              |
| `enabled`    | boolean  | `true`                                      | 启用/禁用通道              |
| `name`       | string   | -                                           | 显示名称                        |
| `profile`    | object   | -                                           | NIP-01 配置文件元数据             |

## 配置文件元数据

配置文件数据作为 NIP-01 `kind:0` 事件发布。您可以从控制界面（通道 -> Nostr -> 配置文件）管理它，或者直接在配置中设置。

示例：

```json
{
  "channels": {
    "nostr": {
      "privateKey": "${NOSTR_PRIVATE_KEY}",
      "profile": {
        "name": "openclaw",
        "displayName": "OpenClaw",
        "about": "Personal assistant DM bot",
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

注意：

- 配置文件 URL 必须使用 `https://`。
- 从中继导入会合并字段并保留本地重写。

## 访问控制

### DM 策略

- **配对**（默认）：未知发送者会收到一个配对码。
- **白名单**：只有 `allowFrom` 中的公钥可以发送 DM。
- **开放**：公共传入 DM（需要 `allowFrom: ["*"]`）。
- **禁用**：忽略传入 DM。

### 白名单示例

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

- **私钥:** `nsec...` 或 64 字符十六进制
- **公钥 (`allowFrom`):** `npub...` 或十六进制

## 中继

默认值: `relay.damus.io` 和 `nos.lol`。

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

- 使用 2-3 个中继以提高冗余性。
- 避免使用过多中继（延迟、重复）。
- 付费中继可以提高可靠性。
- 本地中继适用于测试 (`ws://localhost:7777`)。

## 协议支持

| NIP    | 状态    | 描述                           |
| ------ | --------- | ------------------------------------- |
| NIP-01 | 支持 | 基本事件格式 + 配置文件元数据 |
| NIP-04 | 支持 | 加密的 DM (`kind:4`)              |
| NIP-17 | 计划中   | 礼物包装的 DM                      |
| NIP-44 | 计划中   | 版本化加密                  |

## 测试

### 本地中继

```bash
# Start strfry
docker run -p 7777:7777 ghcr.io/hoytech/strfry
```

```json
{
  "channels": {
    "nostr": {
      "privateKey": "${NOSTR_PRIVATE_KEY}",
      "relays": ["ws://localhost:7777"]
    }
  }
}
```

### 手动测试

1. 从日志中记下机器人的公钥（npub）。
2. 打开一个 Nostr 客户端（Damus, Amethyst 等）。
3. 给机器人公钥发送 DM。
4. 验证响应。

## 故障排除

### 未收到消息

- 验证私钥是否有效。
- 确保中继 URL 可达并使用 `wss://`（或 `ws://` 用于本地）。
- 确认 `enabled` 不是 `false`。
- 检查网关日志中的中继连接错误。

### 未发送响应

- 检查中继是否接受写操作。
- 验证外发连接性。
- 注意中继速率限制。

### 重复响应

- 使用多个中继时预期会出现。
- 消息通过事件 ID 去重；只有第一次传递会触发响应。

## 安全

- 永远不要提交私钥。
- 使用环境变量存储密钥。
- 考虑 `allowlist` 用于生产机器人。

## 限制（MVP）

- 仅直接消息（无群聊）。
- 无媒体附件。
- 仅支持 NIP-04（计划支持 NIP-17 礼物包装）。