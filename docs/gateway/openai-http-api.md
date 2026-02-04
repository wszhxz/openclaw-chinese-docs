---
summary: "Expose an OpenAI-compatible /v1/chat/completions HTTP endpoint from the Gateway"
read_when:
  - Integrating tools that expect OpenAI Chat Completions
title: "OpenAI Chat Completions"
---
# OpenAI Chat Completions (HTTP)

OpenClaw 的网关可以提供一个小型的与 OpenAI 兼容的 Chat Completions 端点。

此端点默认是**禁用**的。请先在配置中启用它。

- `POST /v1/chat/completions`
- 使用与网关相同的端口（WS + HTTP 复用）：`http://<gateway-host>:<port>/v1/chat/completions`

在内部，请求将以正常的网关代理运行方式执行（与 `openclaw agent` 相同的代码路径），因此路由/权限/配置将与您的网关匹配。

## 认证

使用网关的认证配置。发送一个持有者令牌：

- `Authorization: Bearer <token>`

注意事项：

- 当 `gateway.auth.mode="token"` 时，使用 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）。
- 当 `gateway.auth.mode="password"` 时，使用 `gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。

## 选择代理

不需要自定义头：在 OpenAI 的 `model` 字段中编码代理 ID：

- `model: "openclaw:<agentId>"`（示例：`"openclaw:main"`，`"openclaw:beta"`）
- `model: "agent:<agentId>"`（别名）

或者通过头信息指定特定的 OpenClaw 代理：

- `x-openclaw-agent-id: <agentId>`（默认：`main`）

高级：

- 使用 `x-openclaw-session-key: <sessionKey>` 完全控制会话路由。

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

## 会话行为

默认情况下，该端点是**无状态的每个请求**（每次调用都会生成一个新的会话密钥）。

如果请求中包含 OpenAI 的 `user` 字符串，网关将从中推导出一个稳定的会话密钥，因此重复调用可以共享一个代理会话。

## 流式传输 (SSE)

设置 `stream: true` 以接收服务器发送事件（SSE）：

- `Content-Type: text/event-stream`
- 每个事件行是 `data: <json>`
- 流结束于 `data: [DONE]`

## 示例

非流式传输：

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

流式传输：

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