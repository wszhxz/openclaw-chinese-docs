---
summary: "Expose an OpenAI-compatible /v1/chat/completions HTTP endpoint from the Gateway"
read_when:
  - Integrating tools that expect OpenAI Chat Completions
title: "OpenAI Chat Completions"
---
# OpenAI Chat Completions (HTTP)

OpenClaw 的 Gateway 可以提供一个小型的 OpenAI 兼容 Chat Completions 端点。

此端点默认 **禁用**。请先在配置中启用它。

- `POST /v1/chat/completions`
- 与 Gateway 相同的端口（WS + HTTP 复用）：`http://<gateway-host>:<port>/v1/chat/completions`

在底层，请求作为正常的 Gateway agent 运行执行（与 `openclaw agent` 相同的代码路径），因此路由/权限/配置与您的 Gateway 匹配。

## 认证

使用 Gateway 认证配置。发送 bearer token：

- `Authorization: Bearer <token>`

注意：

- 当 `gateway.auth.mode="token"` 时，使用 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）。
- 当 `gateway.auth.mode="password"` 时，使用 `gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。
- 如果配置了 `gateway.auth.rateLimit` 且发生过多认证失败，端点将返回 `429` 并带有 `Retry-After`。

## 安全边界（重要）

将此端点视为 gateway 实例的 **完全操作员访问** 表面。

- 此处的 HTTP bearer 认证不是狭窄的每用户范围模型。
- 此端点的有效 Gateway token/password 应被视为所有者/操作员凭证。
- 请求通过与可信操作员操作相同的 control-plane agent 路径运行。
- 此端点上没有单独的非所有者/每用户工具边界；一旦调用者通过此处的 Gateway 认证，OpenClaw 即将该调用者视为此 gateway 的可信操作员。
- 如果目标 agent 策略允许敏感工具，此端点可以使用它们。
- 仅将此端点保留在 loopback/tailnet/private ingress 上；不要将其直接暴露给公共互联网。

参见 [安全](/gateway/security) 和 [远程访问](/gateway/remote)。

## 选择 agent

无需自定义 header：在 OpenAI `model` 字段中编码 agent id：

- `model: "openclaw:<agentId>"`（示例：`"openclaw:main"`，`"openclaw:beta"`）
- `model: "agent:<agentId>"`（别名）

或通过 header 定位特定的 OpenClaw agent：

- `x-openclaw-agent-id: <agentId>`（默认：`main`）

高级：

- `x-openclaw-session-key: <sessionKey>` 以完全控制 session 路由。

## 启用端点

将 `gateway.http.endpoints.chatCompletions.enabled` 设置为 `true`：

```json5
{
  gateway: {
    http: {
      endpoints: {
        chatCompletions: { enabled: true },
      },
    },
  },
}
```

## 禁用端点

将 `gateway.http.endpoints.chatCompletions.enabled` 设置为 `false`：

```json5
{
  gateway: {
    http: {
      endpoints: {
        chatCompletions: { enabled: false },
      },
    },
  },
}
```

## Session 行为

默认情况下，端点是 **每请求无状态** 的（每次调用都会生成一个新的 session key）。

如果请求包含 OpenAI `user` 字符串，Gateway 将从中派生出一个稳定的 session key，因此重复调用可以共享一个 agent session。

## 流式传输 (SSE)

设置 `stream: true` 以接收 Server-Sent Events (SSE)：

- `Content-Type: text/event-stream`
- 每个事件行是 `data: <json>`
- 流以 `data: [DONE]` 结束

## 示例

非流式：

```bash
curl -sS http://127.0.0.1:18789/v1/chat/completions \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'x-openclaw-agent-id: main' \
  -d '{
    "model": "openclaw",
    "messages": [{"role":"user","content":"hi"}]
  }'
```

流式：

```bash
curl -N http://127.0.0.1:18789/v1/chat/completions \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'x-openclaw-agent-id: main' \
  -d '{
    "model": "openclaw",
    "stream": true,
    "messages": [{"role":"user","content":"hi"}]
  }'
```