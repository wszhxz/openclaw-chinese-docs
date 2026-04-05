---
summary: "Nostr DM channel via NIP-04 encrypted messages"
read_when:
  - You want OpenClaw to receive DMs via Nostr
  - You're setting up decentralized messaging
title: "Nostr"
---
# Nostr

**状态：** 可选捆绑插件（默认禁用，直至配置）。

Nostr 是一种去中心化的社交网络协议。此通道使 OpenClaw 能够通过 NIP-04 接收和响应加密的直接消息 (DM)。

## 捆绑插件

当前 OpenClaw 版本将 Nostr 作为捆绑插件提供，因此常规打包构建无需单独安装。

### 旧版/自定义安装

- 入门引导 (`openclaw onboard`) 和 `openclaw channels add` 仍从共享通道目录中显示 Nostr。
- 如果您的构建排除了捆绑的 Nostr，请手动安装。

```bash
openclaw plugins install @openclaw/nostr
```

使用本地检出（开发工作流）：

```bash
openclaw plugins install --link <path-to-local-nostr-plugin>
```

安装或启用插件后重启网关。

### 非交互式设置

```bash
openclaw channels add --channel nostr --private-key "$NOSTR_PRIVATE_KEY"
openclaw channels add --channel nostr --private-key "$NOSTR_PRIVATE_KEY" --relay-urls "wss://relay.damus.io,wss://relay.primal.net"
```

使用 `--use-env` 将 `NOSTR_PRIVATE_KEY` 保留在环境中，而不是将密钥存储在配置中。

## 快速设置

1. 生成 Nostr 密钥对（如果需要）：

```bash
# Using nak
nak key generate
```

2. 添加到配置：

```json5
{
  channels: {
    nostr: {
      privateKey: "${NOSTR_PRIVATE_KEY}",
    },
  },
}
```

3. 导出密钥：

```bash
export NOSTR_PRIVATE_KEY="nsec1..."
```

4. 重启网关。

## 配置参考

| 键          | 类型     | 默认值                                     | 描述                         |
| ------------ | -------- | ------------------------------------------- | ----------------------------------- |
| `privateKey` | string   | 必填                                    | 私钥，格式为 `nsec` 或十六进制 |
| `relays`     | string[] | `['wss://relay.damus.io', 'wss://nos.lol']` | 中继 URL (WebSocket)              |
| `dmPolicy`   | string   | `pairing`                                   | DM 访问策略                    |
| `allowFrom`  | string[] | `[]`                                        | 允许的发送者公钥              |
| `enabled`    | boolean  | `true`                                      | 启用/禁用通道              |
| `name`       | string   | -                                           | 显示名称                        |
| `profile`    | object   | -                                           | NIP-01 个人资料元数据             |

## 个人资料元数据

个人资料数据作为 NIP-01 `kind:0` 事件发布。您可以从 Control UI（通道 -> Nostr -> 个人资料）进行管理，或直接设置在配置中。

示例：

```json5
{
  channels: {
    nostr: {
      privateKey: "${NOSTR_PRIVATE_KEY}",
      profile: {
        name: "openclaw",
        displayName: "OpenClaw",
        about: "Personal assistant DM bot",
        picture: "https://example.com/avatar.png",
        banner: "https://example.com/banner.png",
        website: "https://example.com",
        nip05: "openclaw@example.com",
        lud16: "openclaw@example.com",
      },
    },
  },
}
```

注意：

- 个人资料 URL 必须使用 `https://`。
- 从中继导入会合并字段并保留本地覆盖。

## 访问控制

### DM 策略

- **配对**（默认）：未知发送者会收到配对码。
- **白名单**：只有 `allowFrom` 中的公钥可以发送 DM。
- **开放**：公共入站 DM（需要 `allowFrom: ["*"]`）。
- **禁用**：忽略入站 DM。

执行说明：

- 入站事件签名在发送者策略和 NIP-04 解密之前进行验证，因此伪造的事件会被早期拒绝。
- 配对回复在不处理原始 DM 正文的情况下发送。
- 入站 DM 受到速率限制，过大的负载会在解密前被丢弃。

### 白名单示例

```json5
{
  channels: {
    nostr: {
      privateKey: "${NOSTR_PRIVATE_KEY}",
      dmPolicy: "allowlist",
      allowFrom: ["npub1abc...", "npub1xyz..."],
    },
  },
}
```

## 密钥格式

接受的格式：

- **私钥：** `nsec...` 或 64 位十六进制
- **公钥 (`allowFrom`)：** `npub...` 或十六进制

## 中继

默认值：`relay.damus.io` 和 `nos.lol`。

```json5
{
  channels: {
    nostr: {
      privateKey: "${NOSTR_PRIVATE_KEY}",
      relays: ["wss://relay.damus.io", "wss://relay.primal.net", "wss://nostr.wine"],
    },
  },
}
```

提示：

- 使用 2-3 个中继以实现冗余。
- 避免过多中继（延迟、重复）。
- 付费中继可以提高可靠性。
- 本地中继适合测试 (`ws://localhost:7777`)。

## 协议支持

| NIP    | 状态    | 描述                           |
| ------ | --------- | ------------------------------------- |
| NIP-01 | 已支持 | 基本事件格式 + 个人资料元数据 |
| NIP-04 | 已支持 | 加密 DM (`kind:4`)              |
| NIP-17 | 计划中   | 礼品包装 DM                      |
| NIP-44 | 计划中   | 版本化加密                  |

## 测试

### 本地中继

```bash
# Start strfry
docker run -p 7777:7777 ghcr.io/hoytech/strfry
```

```json5
{
  channels: {
    nostr: {
      privateKey: "${NOSTR_PRIVATE_KEY}",
      relays: ["ws://localhost:7777"],
    },
  },
}
```

### 手动测试

1. 从日志中记下机器人公钥 (npub)。
2. 打开 Nostr 客户端（Damus, Amethyst 等）。
3. 向机器人公钥发送 DM。
4. 验证响应。

## 故障排除

### 未收到消息

- 验证私钥是否有效。
- 确保中继 URL 可访问并使用 `wss://`（或本地使用 `ws://`）。
- 确认 `enabled` 不是 `false`。
- 检查网关日志以查找中继连接错误。

### 未发送响应

- 检查中继是否接受写入。
- 验证出站连接性。
- 注意中继速率限制。

### 重复响应

- 使用多个中继时预期会发生。
- 消息通过事件 ID 去重；只有第一次投递会触发响应。

## 安全

- 切勿提交私钥。
- 使用环境变量存储密钥。
- 对于生产环境机器人，考虑 `allowlist`。
- 签名在发送者策略之前验证，发送者策略在解密之前执行，因此伪造的事件会被早期拒绝，未知发送者无法强制进行完整的加密工作。

## 限制 (MVP)

- 仅限直接消息（无群聊）。
- 无媒体附件。
- 仅 NIP-04（计划支持 NIP-17 礼品包装）。

## 相关

- [通道概述](/channels) — 所有支持的通道
- [配对](/channels/pairing) — DM 身份验证和配对流程
- [群组](/channels/groups) — 群聊行为和提及门控
- [通道路由](/channels/channel-routing) — 消息会话路由
- [安全](/gateway/security) — 访问模型和加固