---
summary: "Nostr DM channel via NIP-04 encrypted messages"
read_when:
  - You want OpenClaw to receive DMs via Nostr
  - You're setting up decentralized messaging
title: "Nostr"
---
# Nostr

**状态：** 可选插件（默认禁用）。

Nostr 是一种去中心化的社交网络协议。该通道使 OpenClaw 能够通过 NIP-04 接收并响应加密的私信（DM）。

## 安装（按需）

### 入门向导（推荐）

- 入门向导（`openclaw onboard`）和 `openclaw channels add` 列出了可选的通道插件。
- 选择 Nostr 将提示您按需安装该插件。

安装默认行为：

- **开发通道 + 已有 git 仓库：** 使用本地插件路径。
- **稳定版/测试版：** 从 npm 下载。

您始终可以在提示中覆盖该选择。

### 手动安装

```bash
openclaw plugins install @openclaw/nostr
```

使用本地仓库（适用于开发流程）：

```bash
openclaw plugins install --link <path-to-openclaw>/extensions/nostr
```

在安装或启用插件后，请重启 Gateway。

## 快速配置

1. 生成 Nostr 密钥对（如尚未生成）：

```bash
# Using nak
nak key generate
```

2. 添加至配置文件：

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

4. 重启 Gateway。

## 配置参考

| 键          | 类型     | 默认值                                     | 描述                         |
| ------------ | -------- | ------------------------------------------- | ----------------------------------- |
| `privateKey` | 字符串   | 必填                                    | 私钥，格式为 `nsec` 或十六进制字符串 |
| `relays`     | 字符串数组 | `['wss://relay.damus.io', 'wss://nos.lol']` | 中继服务器 URL（WebSocket）              |
| `dmPolicy`   | 字符串   | `pairing`                                   | 私信访问策略                    |
| `allowFrom`  | 字符串数组 | `[]`                                        | 允许发送消息的公钥列表              |
| `enabled`    | 布尔值  | `true`                                      | 启用/禁用该通道              |
| `name`       | 字符串   | -                                           | 显示名称                        |
| `profile`    | 对象   | -                                           | NIP-01 个人资料元数据             |

## 个人资料元数据

个人资料数据以 NIP-01 `kind:0` 事件形式发布。您可通过控制界面（Channels → Nostr → Profile）管理，或直接在配置中设置。

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

注意事项：

- 个人资料 URL 必须使用 `https://`。
- 从中继服务器导入时，字段将被合并，并保留本地覆盖项。

## 访问控制

### 私信策略

- **配对（pairing，默认）：** 未知发送者将收到配对码。
- **白名单（allowlist）：** 仅 `allowFrom` 中列出的公钥可发送私信。
- **开放（open）：** 允许公开入站私信（需启用 `allowFrom: ["*"]`）。
- **禁用（disabled）：** 忽略所有入站私信。

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

支持的格式：

- **私钥：** `nsec...` 或 64 位十六进制字符串
- **公钥（`allowFrom`）：** `npub...` 或十六进制字符串

## 中继服务器

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

- 建议使用 2–3 个中继服务器以实现冗余。
- 避免配置过多中继服务器（会增加延迟、造成重复）。
- 付费中继服务器可提升可靠性。
- 本地中继服务器适合测试（`ws://localhost:7777`）。

## 协议支持

| NIP    | 状态      | 描述                           |
| ------ | --------- | ------------------------------------- |
| NIP-01 | 已支持    | 基础事件格式 + 个人资料元数据 |
| NIP-04 | 已支持    | 加密私信（`kind:4`）              |
| NIP-17 | 计划中    | 礼物包裹式私信                      |
| NIP-44 | 计划中    | 版本化加密                  |

## 测试

### 本地中继服务器

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
2. 打开一个 Nostr 客户端（如 Damus、Amethyst 等）。
3. 向该机器人公钥发送私信。
4. 验证是否收到响应。

## 故障排查

### 未收到消息

- 验证私钥是否有效。
- 确保中继服务器 URL 可达，且使用 `wss://`（或本地环境使用 `ws://`）。
- 确认 `enabled` 不为 `false`。
- 检查 Gateway 日志中是否存在中继连接错误。

### 未发送响应

- 检查中继服务器是否接受写入操作。
- 验证出站网络连接是否正常。
- 注意中继服务器的速率限制。

### 重复响应

- 在使用多个中继服务器时属预期行为。
- 消息按事件 ID 去重；仅首次投递触发响应。

## 安全性

- 切勿提交私钥。
- 使用环境变量存储密钥。
- 生产环境机器人建议考虑 `allowlist`。

## 局限性（MVP 版本）

- 仅支持私信（不支持群聊）。
- 不支持媒体附件。
- 仅支持 NIP-04（NIP-17 礼物包裹功能正在规划中）。