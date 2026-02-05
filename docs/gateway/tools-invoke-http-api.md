---
summary: "Invoke a single tool directly via the Gateway HTTP endpoint"
read_when:
  - Calling tools without running a full agent turn
  - Building automations that need tool policy enforcement
title: "Tools Invoke API"
---
# 工具调用 (HTTP)

OpenClaw 的网关提供了一个简单的 HTTP 端点，用于直接调用单个工具。它始终启用，但受网关认证和工具策略的限制。

- `POST /tools/invoke`
- 与网关相同的端口（WS + HTTP 复用）：`http://<gateway-host>:<port>/tools/invoke`

默认最大负载大小为 2 MB。

## 认证

使用网关认证配置。发送一个持有者令牌：

- `Authorization: Bearer <token>`

注意事项：

- 当 `gateway.auth.mode="token"` 时，使用 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）。
- 当 `gateway.auth.mode="password"` 时，使用 `gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。

## 请求体

```json
{
  "tool": "sessions_list",
  "action": "json",
  "args": {},
  "sessionKey": "main",
  "dryRun": false
}
```

字段：

- `tool` (string, 必需)：要调用的工具名称。
- `action` (string, 可选)：如果工具架构支持 `action` 且 args 负载中省略了该项，则映射到 args。
- `args` (object, 可选)：特定于工具的参数。
- `sessionKey` (string, 可选)：目标会话密钥。如果省略或 `"main"`，网关将使用配置的主要会话密钥（尊重 `session.mainKey` 和默认代理，或全局范围内的 `global`）。
- `dryRun` (boolean, 可选)：保留用于未来使用；当前忽略。

## 策略 + 路由行为

工具可用性通过与网关代理相同的策略链进行过滤：

- `tools.profile` / `tools.byProvider.profile`
- `tools.allow` / `tools.byProvider.allow`
- `agents.<id>.tools.allow` / `agents.<id>.tools.byProvider.allow`
- 组策略（如果会话密钥映射到组或频道）
- 子代理策略（使用子代理会话密钥调用时）

如果策略不允许某个工具，则该端点返回 **404**。

为了帮助组策略解析上下文，您可以选择设置：

- `x-openclaw-message-channel: <channel>`（示例：`slack`，`telegram`）
- `x-openclaw-account-id: <accountId>`（当存在多个账户时）

## 响应

- `200` → `{ ok: true, result }`
- `400` → `{ ok: false, error: { type, message } }`（无效请求或工具错误）
- `401` → 未授权
- `404` → 工具不可用（未找到或不在白名单中）
- `405` → 方法不被允许

## 示例

```bash
curl -sS http://127.0.0.1:18789/tools/invoke \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "tool": "sessions_list",
    "action": "json",
    "args": {}
  }'
```