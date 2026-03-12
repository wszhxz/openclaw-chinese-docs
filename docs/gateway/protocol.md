---
summary: "Gateway WebSocket protocol: handshake, frames, versioning"
read_when:
  - Implementing or updating gateway WS clients
  - Debugging protocol mismatches or connect failures
  - Regenerating protocol schema/models
title: "Gateway Protocol"
---
# 网关协议（WebSocket）

网关 WebSocket 协议是 OpenClaw 的 **单一控制平面 + 节点传输通道**。所有客户端（CLI、Web UI、macOS 应用、iOS/Android 节点、无头节点）均通过 WebSocket 连接，并在握手阶段声明其 **角色（role）** 和 **作用域（scope）**。

## 传输层

- 使用 WebSocket，以文本帧承载 JSON 有效载荷。
- 首帧 **必须** 是一个 `connect` 请求。

## 握手（连接）

网关 → 客户端（预连接挑战）：

```json
{
  "type": "event",
  "event": "connect.challenge",
  "payload": { "nonce": "…", "ts": 1737264000000 }
}
```

客户端 → 网关：

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

网关 → 客户端：

```json
{
  "type": "res",
  "id": "…",
  "ok": true,
  "payload": { "type": "hello-ok", "protocol": 3, "policy": { "tickIntervalMs": 15000 } }
}
```

当颁发设备令牌时，`hello-ok` 还额外包含：

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

- **请求**：`{type:"req", id, method, params}`
- **响应**：`{type:"res", id, ok, payload|error}`
- **事件**：`{type:"event", event, payload, seq?, stateVersion?}`

具有副作用的方法要求提供 **幂等性密钥（idempotency keys）**（参见 schema）。

## 角色与作用域

### 角色

- `operator` = 控制平面客户端（CLI/UI/自动化工具）。
- `node` = 能力宿主（摄像头/屏幕/画布/system.run）。

### 作用域（操作员）

常见作用域：

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`

方法级作用域仅为第一道访问控制门。某些通过 `chat.send` 触达的斜杠命令，还会在此基础上施加更严格的命令级校验。例如，持久化写入 `/config set` 和 `/config unset` 需要 `operator.admin`。

### 能力 / 命令 / 权限（节点）

节点在连接时声明其能力声明（capability claims）：

- `caps`：高层级能力类别。
- `commands`：用于 `invoke` 的命令白名单。
- `permissions`：细粒度开关（例如 `screen.record`、`camera.capture`）。

网关将这些视为 **声明（claims）**，并在服务端强制执行白名单策略。

## 在线状态（Presence）

- `system-presence` 返回以设备身份为键的条目列表。
- 在线状态条目包含 `deviceId`、`roles` 和 `scopes`，使 UI 可对每个设备仅显示一行，即使该设备同时以 **操作员（operator）** 和 **节点（node）** 身份连接。

### 节点辅助方法

- 节点可调用 `skills.bins` 获取当前可用技能可执行文件列表，用于自动许可检查。

### 操作员辅助方法

- 操作员可调用 `tools.catalog`（`operator.read`）获取代理的运行时工具目录。响应中包含分组后的工具及其来源元数据：
  - `source`：`core` 或 `plugin`
  - `pluginId`：当 `source="plugin"` 时，插件所有者
  - `optional`：插件工具是否为可选

## 执行审批（Exec approvals）

- 当执行请求需要审批时，网关广播 `exec.approval.requested`。
- 操作员客户端通过调用 `exec.approval.resolve`（需具备 `operator.approvals` 作用域）完成审批。
- 对于 `host=node`，`exec.approval.request` 必须包含 `systemRunPlan`（标准的 `argv`/`cwd`/`rawCommand`/会话元数据）。缺失 `systemRunPlan` 的请求将被拒绝。

## 版本控制

- `PROTOCOL_VERSION` 位于 `src/gateway/protocol/schema.ts` 中。
- 客户端发送 `minProtocol` 与 `maxProtocol`；服务器将拒绝版本不匹配的连接。
- Schema 与模型由 TypeBox 定义生成：
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`
  - `pnpm protocol:check`

## 认证（Auth）

- 若设置了 `OPENCLAW_GATEWAY_TOKEN`（或 `--token`），则 `connect.params.auth.token` 必须匹配，否则连接将被关闭。
- 配对完成后，网关将颁发一个 **设备令牌（device token）**，其作用域限定于本次连接的角色与作用域。该令牌在 `hello-ok.auth.deviceToken` 中返回，客户端应将其持久化保存，供后续连接复用。
- 设备令牌可通过 `device.token.rotate` 和 `device.token.revoke`（需具备 `operator.pairing` 作用域）进行轮换或撤销。

## 设备身份与配对

- 节点应包含一个稳定的设备身份（`device.id`），该身份派生自密钥对指纹。
- 网关按设备 + 角色分别颁发令牌。
- 新设备 ID 首次接入需经配对审批，除非启用了本地自动审批。
- **本地（Local）** 连接包括回环地址（loopback）及网关主机自身的 Tailnet 地址（因此同主机的 Tailnet 绑定仍可自动批准）。
- 所有 WebSocket 客户端在 `connect`（操作员 + 节点）阶段均须提供 `device` 身份。仅当启用 `gateway.controlUi.dangerouslyDisableDeviceAuth` 时，控制 UI 才可省略此字段（用于紧急破窗场景）。
- 所有连接必须对服务器提供的 `connect.challenge` 随机数进行签名。

### 设备认证迁移诊断

针对仍使用预挑战签名行为的旧版客户端，`connect` 现在在 `error.details.code` 下返回 `DEVICE_AUTH_*` 详细错误码，并附带稳定的 `error.details.reason`。

常见迁移失败情形：

| Message                     | details.code                     | details.reason           | Meaning                                            |
| --------------------------- | -------------------------------- | ------------------------ | -------------------------------------------------- |
| `device nonce required`     | `DEVICE_AUTH_NONCE_REQUIRED`     | `device-nonce-missing`   | 客户端未提供 `device.nonce`（或传入空值）。     |
| `device nonce mismatch`     | `DEVICE_AUTH_NONCE_MISMATCH`     | `device-nonce-mismatch`  | 客户端使用过期/错误的随机数进行了签名。            |
| `device signature invalid`  | `DEVICE_AUTH_SIGNATURE_INVALID`  | `device-signature`       | 签名载荷与 v2 载荷不匹配。                       |
| `device signature expired`  | `DEVICE_AUTH_SIGNATURE_EXPIRED`  | `device-signature-stale` | 签名时间戳超出允许的时间偏移范围。               |
| `device identity mismatch`  | `DEVICE_AUTH_DEVICE_ID_MISMATCH` | `device-id-mismatch`     | `device.id` 与公钥指纹不匹配。             |
| `device public key invalid` | `DEVICE_AUTH_PUBLIC_KEY_INVALID` | `device-public-key`      | 公钥格式/规范化失败。                            |

迁移目标：

- 始终等待 `connect.challenge`。
- 对包含服务器随机数的 v2 载荷进行签名。
- 在 `connect.params.device.nonce` 中发送相同的随机数。
- 推荐的签名载荷为 `v3`，它除绑定设备/客户端/角色/作用域/令牌/随机数字段外，还额外绑定 `platform` 和 `deviceFamily`。
- 为兼容性，旧版 `v2` 签名仍被接受，但重连时命令策略仍由配对设备元数据绑定控制。

## TLS 与证书固定（pinning）

- WebSocket 连接支持 TLS。
- 客户端可选择性地固定网关证书指纹（参见 `gateway.tls` 配置项，以及 `gateway.remote.tlsFingerprint` 或 CLI `--tls-fingerprint`）。

## 作用域（Scope）

本协议暴露 **完整的网关 API**（状态、频道、模型、聊天、代理、会话、节点、审批等）。确切的接口表面由 `src/gateway/protocol/schema.ts` 中的 TypeBox schema 定义。