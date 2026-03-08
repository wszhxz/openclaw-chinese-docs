---
summary: "Gateway WebSocket protocol: handshake, frames, versioning"
read_when:
  - Implementing or updating gateway WS clients
  - Debugging protocol mismatches or connect failures
  - Regenerating protocol schema/models
title: "Gateway Protocol"
---
# 网关协议 (WebSocket)

OpenClaw 的网关 WS 协议是**单一控制平面 + 节点传输**。所有客户端（CLI、web UI、macOS 应用、iOS/Android 节点、无头节点）通过 WebSocket 连接，并在握手时声明其**角色**和**范围**。

## 传输

- WebSocket，带有 JSON 负载的文本帧。
- 第一帧**必须**是 `connect` 请求。

## 握手 (连接)

网关 → 客户端 (预连接挑战):

```json
{
  "type": "event",
  "event": "connect.challenge",
  "payload": { "nonce": "…", "ts": 1737264000000 }
}
```

客户端 → 网关:

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "cli",
      "version": "1.2.3",
      "platform": "macos",
      "mode": "operator"
    },
    "role": "operator",
    "scopes": ["operator.read", "operator.write"],
    "caps": [],
    "commands": [],
    "permissions": {},
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-cli/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

网关 → 客户端:

```json
{
  "type": "res",
  "id": "…",
  "ok": true,
  "payload": { "type": "hello-ok", "protocol": 3, "policy": { "tickIntervalMs": 15000 } }
}
```

当颁发设备令牌时，`hello-ok` 还包括:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

### 节点示例

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "ios-node",
      "version": "1.2.3",
      "platform": "ios",
      "mode": "node"
    },
    "role": "node",
    "scopes": [],
    "caps": ["camera", "canvas", "screen", "location", "voice"],
    "commands": ["camera.snap", "canvas.navigate", "screen.record", "location.get"],
    "permissions": { "camera.capture": true, "screen.record": false },
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-ios/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

## 帧格式

- **请求**: `{type:"req", id, method, params}`
- **响应**: `{type:"res", id, ok, payload|error}`
- **事件**: `{type:"event", event, payload, seq?, stateVersion?}`

副作用方法需要**幂等键**（参见 schema）。

## 角色 + 范围

### 角色

- `operator` = 控制平面客户端 (CLI/UI/自动化)。
- `node` = 能力主机 (相机/屏幕/画布/system.run)。

### 范围 (操作员)

常见范围:

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`

方法范围仅是第一道关卡。某些通过 `chat.send` 访问的斜杠命令在此基础上应用更严格的命令级检查。例如，持久化 `/config set` 和 `/config unset` 写入需要 `operator.admin`。

### 能力/命令/权限 (节点)

节点在连接时声明能力主张:

- `caps`: 高级别能力类别。
- `commands`: 调用的命令白名单。
- `permissions`: 细粒度开关（例如 `screen.record`, `camera.capture`）。

网关将这些视为**主张**并强制执行服务器端白名单。

## 在线状态

- `system-presence` 返回以设备身份为键的条目。
- 在线状态条目包括 `deviceId`, `roles` 和 `scopes`，以便 UI 即使设备同时作为**操作员**和**节点**连接也能显示每设备一行。

### 节点辅助方法

- 节点可以调用 `skills.bins` 获取当前技能可执行文件列表以进行自动允许检查。

### 操作员辅助方法

- 操作员可以调用 `tools.catalog` (`operator.read`) 获取代理的运行时工具目录。响应包括分组的工具和来源元数据:
  - `source`: `core` 或 `plugin`
  - `pluginId`: 插件所有者，当 `source="plugin"` 时
  - `optional`: 插件工具是否为可选

## 执行审批

- 当执行请求需要审批时，网关广播 `exec.approval.requested`。
- 操作员客户端通过调用 `exec.approval.resolve` 解决（需要 `operator.approvals` 范围）。
- 对于 `host=node`, `exec.approval.request` 必须包含 `systemRunPlan`（规范化的 `argv`/`cwd`/`rawCommand`/会话元数据）。缺少 `systemRunPlan` 的请求将被拒绝。

## 版本控制

- `PROTOCOL_VERSION` 位于 `src/gateway/protocol/schema.ts`。
- 客户端发送 `minProtocol` + `maxProtocol`；服务器拒绝不匹配项。
- Schema + 模型由 TypeBox 定义生成:
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`
  - `pnpm protocol:check`

## 认证

- 如果设置了 `OPENCLAW_GATEWAY_TOKEN`（或 `--token`），则 `connect.params.auth.token` 必须匹配，否则套接字将关闭。
- 配对后，网关颁发一个针对连接角色 + 范围的**设备令牌**。它在 `hello-ok.auth.deviceToken` 中返回，应由客户端保存以供将来连接使用。
- 设备令牌可以通过 `device.token.rotate` 和 `device.token.revoke` 轮换/撤销（需要 `operator.pairing` 范围）。

## 设备身份 + 配对

- 节点应包含源自密钥对指纹的稳定设备身份 (`device.id`)。
- 网关按设备 + 角色颁发令牌。
- 除非启用本地自动批准，否则新设备 ID 需要配对批准。
- **本地**连接包括回环和网关主机自己的 tailnet 地址（因此同一主机 tailnet 绑定仍可以自动批准）。
- 所有 WS 客户端必须在 `connect` 期间包含 `device` 身份。Control UI **仅**在启用 `gateway.controlUi.dangerouslyDisableDeviceAuth` 用于紧急模式时可省略它。
- 所有连接必须对服务器提供的 `connect.challenge` nonce 进行签名。

### 设备认证迁移诊断

对于仍然使用预挑战签名行为的旧版客户端，`connect` 现在在 `error.details.code` 下返回 `DEVICE_AUTH_*` 详细代码，并具有稳定的 `error.details.reason`。

常见迁移失败:

| 消息 | details.code | details.reason | 含义 |
| --------------------------- | -------------------------------- | ------------------------ | -------------------------------------------------- |
| `device nonce required`     | `DEVICE_AUTH_NONCE_REQUIRED`     | `device-nonce-missing`   | 客户端省略了 `device.nonce`（或发送了空白）。     |
| `device nonce mismatch`     | `DEVICE_AUTH_NONCE_MISMATCH`     | `device-nonce-mismatch`  | 客户端使用了过期/错误的 nonce 进行签名。            |
| `device signature invalid`  | `DEVICE_AUTH_SIGNATURE_INVALID`  | `device-signature`       | 签名负载与 v2 负载不匹配。       |
| `device signature expired`  | `DEVICE_AUTH_SIGNATURE_EXPIRED`  | `device-signature-stale` | 签名时间戳超出允许的偏差。          |
| `device identity mismatch`  | `DEVICE_AUTH_DEVICE_ID_MISMATCH` | `device-id-mismatch`     | `device.id` 与公钥指纹不匹配。 |
| `device public key invalid` | `DEVICE_AUTH_PUBLIC_KEY_INVALID` | `device-public-key`      | 公钥格式/规范化失败。         |

迁移目标:

- 始终等待 `connect.challenge`。
- 对包含服务器 nonce 的 v2 负载进行签名。
- 在 `connect.params.device.nonce` 中发送相同的 nonce。
- 首选签名负载是 `v3`，除了设备/客户端/角色/范围/令牌/nonce 字段外，它还绑定 `platform` 和 `deviceFamily`。
- 为了兼容性，旧版 `v2` 签名仍被接受，但配对设备元数据锁定仍在重新连接时控制命令策略。

## TLS + 固定

- WS 连接支持 TLS。
- 客户端可以选择固定网关证书指纹（参见 `gateway.tls` 配置以及 `gateway.remote.tlsFingerprint` 或 CLI `--tls-fingerprint`）。

## 范围

此协议暴露了**完整的网关 API**（状态、频道、模型、聊天、代理、会话、节点、审批等）。确切表面由 `src/gateway/protocol/schema.ts` 中的 TypeBox schema 定义。