---
summary: "Expose an OpenResponses-compatible /v1/responses HTTP endpoint from the Gateway"
read_when:
  - Integrating clients that speak the OpenResponses API
  - You want item-based inputs, client tool calls, or SSE events
title: "OpenResponses API"
---
# OpenResponses API (HTTP)

OpenClaw 的网关可以提供一个与 OpenResponses 兼容的 `POST /v1/responses` 端点。

此端点默认是**禁用**的。请先在配置中启用它。

- `POST /v1/responses`
- 使用与网关相同的端口（WS + HTTP 复用）：`http://<gateway-host>:<port>/v1/responses`

在内部，请求作为正常的网关代理运行执行（与 `openclaw agent` 相同的代码路径），因此路由/权限/配置与您的网关匹配。

## 认证

使用网关的认证配置。发送一个持有者令牌：

- `Authorization: Bearer <token>`

注意事项：

- 当 `gateway.auth.mode="token"` 时，使用 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）。
- 当 `gateway.auth.mode="password"` 时，使用 `gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。
- 如果 `gateway.auth.rateLimit` 配置且认证失败次数过多，端点将返回 `429` 并附带 `Retry-After`。

## 选择代理

不需要自定义头：在 OpenResponses 的 `model` 字段中编码代理 ID：

- `model: "openclaw:<agentId>"`（示例：`"openclaw:main"`，`"openclaw:beta"`）
- `model: "agent:<agentId>"`（别名）

或者通过头信息指定特定的 OpenClaw 代理：

- `x-openclaw-agent-id: <agentId>`（默认：`main`）

高级：

- 使用 `x-openclaw-session-key: <sessionKey>` 完全控制会话路由。

## 启用端点

设置 `gateway.http.endpoints.responses.enabled` 为 `true`：

```json5
{
  gateway: {
    http: {
      endpoints: {
        responses: { enabled: true },
      },
    },
  },
}
```

## 禁用端点

设置 `gateway.http.endpoints.responses.enabled` 为 `false`：

```json5
{
  gateway: {
    http: {
      endpoints: {
        responses: { enabled: false },
      },
    },
  },
}
```

## 会话行为

默认情况下，端点是**无状态的每个请求**（每次调用都会生成一个新的会话密钥）。

如果请求包含一个 OpenResponses `user` 字符串，网关将从中推导出一个稳定的会话密钥，因此重复调用可以共享一个代理会话。

## 请求形状（支持）

请求遵循基于项目的 OpenResponses API。当前支持：

- `input`：字符串或项目对象数组。
- `instructions`：合并到系统提示中。
- `tools`：客户端工具定义（函数工具）。
- `tool_choice`：过滤或要求客户端工具。
- `stream`：启用 SSE 流式传输。
- `max_output_tokens`：最佳努力输出限制（提供商相关）。
- `user`：稳定会话路由。

已接受但**目前忽略**：

- `max_tool_calls`
- `reasoning`
- `metadata`
- `store`
- `previous_response_id`
- `truncation`

## 项目（输入）

### `message`

角色：`system`，`developer`，`user`，`assistant`。

- `system` 和 `developer` 被附加到系统提示中。
- 最近的 `user` 或 `function_call_output` 项目成为“当前消息”。
- 较早的用户/助手消息被包含在历史记录中以供上下文参考。

### `function_call_output`（回合制工具）

将工具结果发回给模型：

```json
{
  "type": "function_call_output",
  "call_id": "call_123",
  "output": "{\"temperature\": \"72F\"}"
}
```

### `reasoning` 和 `item_reference`

为了模式兼容性而接受，但在构建提示时被忽略。

## 工具（客户端函数工具）

通过 `tools: [{ type: "function", function: { name, description?, parameters? } }]` 提供工具。

如果代理决定调用一个工具，响应将返回一个 `function_call` 输出项目。
然后您发送一个带有 `function_call_output` 的后续请求以继续回合。

## 图像 (`input_image`)

支持 base64 或 URL 源：

```json
{
  "type": "input_image",
  "source": { "type": "url", "url": "https://example.com/image.png" }
}
```

允许的 MIME 类型（当前）：`image/jpeg`，`image/png`，`image/gif`，`image/webp`。
最大大小（当前）：10MB。

## 文件 (`input_file`)

支持 base64 或 URL 源：

```json
{
  "type": "input_file",
  "source": {
    "type": "base64",
    "media_type": "text/plain",
    "data": "SGVsbG8gV29ybGQh",
    "filename": "hello.txt"
  }
}
```

允许的 MIME 类型（当前）：`text/plain`，`text/markdown`，`text/html`，`text/csv`，
`application/json`，`application/pdf`。

最大大小（当前）：5MB。

当前行为：

- 文件内容被解码并添加到**系统提示**中，而不是用户消息中，
  因此它是临时的（不会保留在会话历史中）。
- PDF 被解析以提取文本。如果没有找到很多文本，则将前几页光栅化为图像并传递给模型。

PDF 解析使用 Node 友好的 `pdfjs-dist` 旧版构建（没有工作线程）。现代的 PDF.js 构建需要浏览器工作线程/DOM 全局变量，因此在网关中未使用。

URL 获取默认值：

- `files.allowUrl`：`true`
- `images.allowUrl`：`true`
- `maxUrlParts`：`8`（每个请求基于 URL 的 `input_file` + `input_image` 部分总数）
- 请求受到保护（DNS 解析，私有 IP 阻止，重定向限制，超时）。
- 支持按输入类型可选的主机名白名单 (`files.urlAllowlist`，`images.urlAllowlist`)。
  - 精确主机：`"cdn.example.com"`
  - 通配符子域：`"*.assets.example.com"`（不匹配顶级域）

## 文件 + 图像限制（配置）

默认值可以在 `gateway.http.endpoints.responses` 下进行调整：

```json5
{
  gateway: {
    http: {
      endpoints: {
        responses: {
          enabled: true,
          maxBodyBytes: 20000000,
          maxUrlParts: 8,
          files: {
            allowUrl: true,
            urlAllowlist: ["cdn.example.com", "*.assets.example.com"],
            allowedMimes: [
              "text/plain",
              "text/markdown",
              "text/html",
              "text/csv",
              "application/json",
              "application/pdf",
            ],
            maxBytes: 5242880,
            maxChars: 200000,
            maxRedirects: 3,
            timeoutMs: 10000,
            pdf: {
              maxPages: 4,
              maxPixels: 4000000,
              minTextChars: 200,
            },
          },
          images: {
            allowUrl: true,
            urlAllowlist: ["images.example.com"],
            allowedMimes: ["image/jpeg", "image/png", "image/gif", "image/webp"],
            maxBytes: 10485760,
            maxRedirects: 3,
            timeoutMs: 10000,
          },
        },
      },
    },
  },
}
```

省略时的默认值：

- `maxBodyBytes`：20MB
- `maxUrlParts`：8
- `files.maxBytes`：5MB
- `files.maxChars`：200k
- `files.maxRedirects`：3
- `files.timeoutMs`：10s
- `files.pdf.maxPages`：4
- `files.pdf.maxPixels`：4,000,000
- `files.pdf.minTextChars`：200
- `images.maxBytes`：10MB
- `images.maxRedirects`：3
- `images.timeoutMs`：10s

安全说明：

- URL 白名单在获取之前和重定向跳转时强制执行。
- 白名单主机名不会绕过私有/内部 IP 阻止。
- 对于面向互联网的网关，请在应用级防护之外应用网络出口控制。
  请参阅[安全性](/gateway/security)。

## 流式传输（SSE）

设置 `stream: true` 以接收服务器发送事件（SSE）：

- `Content-Type: text/event-stream`
- 每个事件行是 `event: <type>` 和 `data: <json>`
- 流结束于 `data: [DONE]`

当前发出的事件类型：

- `response.created`
- `response.in_progress`
- `response.output_item.added`
- `response.content_part.added`
- `response.output_text.delta`
- `response.output_text.done`
- `response.content_part.done`
- `response.output_item.done`
- `response.completed`
- `response.failed`（发生错误时）

## 使用

当底层提供商报告标记计数时，`usage` 将被填充。

## 错误

错误使用如下 JSON 对象表示：

```json
{ "error": { "message": "...", "type": "invalid_request_error" } }
```

常见情况：

- `401` 缺少/无效的认证
- `400` 无效的请求体
- `405` 错误的方法

## 示例

非流式传输：

```bash
curl -sS http://127.0.0.1:18789/v1/responses \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'x-openclaw-agent-id: main' \
  -d '{
    "model": "openclaw",
    "input": "hi"
  }'
```

流式传输：

```bash
curl -N http://127.0.0.1:18789/v1/responses \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'x-openclaw-agent-id: main' \
  -d '{
    "model": "openclaw",
    "stream": true,
    "input": "hi"
  }'
```