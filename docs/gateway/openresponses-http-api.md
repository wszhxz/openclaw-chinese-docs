---
summary: "Expose an OpenResponses-compatible /v1/responses HTTP endpoint from the Gateway"
read_when:
  - Integrating clients that speak the OpenResponses API
  - You want item-based inputs, client tool calls, or SSE events
title: "OpenResponses API"
---
# OpenResponses API（HTTP）

OpenClaw 的网关可提供一个兼容 OpenResponses 的 `POST /v1/responses` 端点。

该端点**默认处于禁用状态**。请先在配置中启用它。

- `POST /v1/responses`
- 与网关使用同一端口（WS + HTTP 复用）：`http://<gateway-host>:<port>/v1/responses`

底层实现上，请求将作为一次常规的网关代理运行来执行（与 `openclaw agent` 使用相同的代码路径），因此路由、权限和配置均与您的网关保持一致。

## 认证

使用网关的认证配置。请发送 Bearer Token：

- `Authorization: Bearer <token>`

注意事项：

- 当 `gateway.auth.mode="token"` 时，请使用 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）。
- 当 `gateway.auth.mode="password"` 时，请使用 `gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。
- 如果配置了 `gateway.auth.rateLimit` 且发生过多认证失败，则该端点将返回 `429`，并附带 `Retry-After`。

## 安全边界（重要）

请将此端点视为网关实例的**完整操作员访问面**。

- 此处的 HTTP Bearer 认证并非面向用户的细粒度作用域模型。
- 对于此端点有效的网关 Token/密码，应被视为所有者/操作员凭证。
- 请求通过与受信任操作员操作相同的控制平面代理路径执行。
- 此端点上不存在独立的非所有者/普通用户工具边界；一旦调用方在此处通过网关认证，OpenClaw 即视该调用方为该网关的受信任操作员。
- 若目标代理策略允许敏感工具，此端点亦可调用它们。
- 请仅将此端点部署于回环地址（loopback）、Tailnet 或私有入口（private ingress）之上；切勿直接将其暴露于公共互联网。

参见 [安全性](/gateway/security) 和 [远程访问](/gateway/remote)。

## 选择代理

无需自定义请求头：在 OpenResponses 的 `model` 字段中编码代理 ID：

- `model: "openclaw:<agentId>"`（示例：`"openclaw:main"`、`"openclaw:beta"`）
- `model: "agent:<agentId>"`（别名）

或通过请求头指定特定 OpenClaw 代理：

- `x-openclaw-agent-id: <agentId>`（默认值：`main`）

高级用法：

- 使用 `x-openclaw-session-key: <sessionKey>` 可完全控制会话路由。

## 启用端点

将 `gateway.http.endpoints.responses.enabled` 设置为 `true`：

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

将 `gateway.http.endpoints.responses.enabled` 设置为 `false`：

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

默认情况下，该端点对每次请求均为**无状态**（每次调用均生成新的会话密钥）。

若请求中包含 OpenResponses 的 `user` 字符串，网关将从中派生出稳定的会话密钥，从而允许多次调用共享同一个代理会话。

## 请求结构（支持项）

请求遵循 OpenResponses API 规范，采用基于条目的输入格式。当前支持：

- `input`：字符串或条目对象数组。
- `instructions`：合并至系统提示词（system prompt）中。
- `tools`：客户端工具定义（函数工具）。
- `tool_choice`：筛选或限定客户端工具。
- `stream`：启用 SSE 流式传输。
- `max_output_tokens`：尽力而为的输出长度限制（取决于提供商）。
- `user`：稳定会话路由。

已接受但**当前被忽略**的字段：

- `max_tool_calls`
- `reasoning`
- `metadata`
- `store`
- `previous_response_id`
- `truncation`

## 条目（输入）

### `message`

角色包括：`system`、`developer`、`user`、`assistant`。

- `system` 和 `developer` 将追加至系统提示词。
- 最近的一个 `user` 或 `function_call_output` 条目将成为“当前消息”。
- 更早的用户/助手消息将作为上下文历史一并包含。

### `function_call_output`（回合制工具）

将工具执行结果返回给模型：

```json
{
  "type": "function_call_output",
  "call_id": "call_123",
  "output": "{\"temperature\": \"72F\"}"
}
```

### `reasoning` 和 `item_reference`

为保证 Schema 兼容性而接受，但在构建提示词时被忽略。

## 工具（客户端函数工具）

通过 `tools: [{ type: "function", function: { name, description?, parameters? } }]` 提供工具。

若代理决定调用某个工具，响应将返回一个 `function_call` 输出条目。随后您需发送一个后续请求，并在其中携带 `function_call_output`，以继续当前回合。

## 图像（`input_image`）

支持 base64 编码或 URL 源：

```json
{
  "type": "input_image",
  "source": { "type": "url", "url": "https://example.com/image.png" }
}
```

允许的 MIME 类型（当前）：`image/jpeg`、`image/png`、`image/gif`、`image/webp`、`image/heic`、`image/heif`。  
最大尺寸（当前）：10MB。

## 文件（`input_file`）

支持 base64 编码或 URL 源：

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

允许的 MIME 类型（当前）：`text/plain`、`text/markdown`、`text/html`、`text/csv`、  
`application/json`、`application/pdf`。

最大尺寸（当前）：5MB。

当前行为：

- 文件内容将被解码并添加至**系统提示词**（而非用户消息），因此其为临时性内容（不会保留在会话历史中）。
- PDF 文件将被解析提取文本；若文本量极少，则将前几页光栅化为图像并传入模型。

PDF 解析使用 Node.js 兼容的 `pdfjs-dist` 旧版构建（不依赖 Worker）。现代版 PDF.js 构建依赖浏览器 Worker/DOM 全局变量，因此未在网关中使用。

URL 获取默认设置：

- `files.allowUrl`：`true`
- `images.allowUrl`：`true`
- `maxUrlParts`：`8`（每个请求中基于 URL 的 `input_file` 和 `input_image` 部分总数上限）
- 所有请求均受到保护（DNS 解析、私有 IP 地址拦截、重定向次数限制、超时机制）。
- 支持按输入类型（`files.urlAllowlist`、`images.urlAllowlist`）配置可选的主机名白名单。
  - 精确匹配主机名：`"cdn.example.com"`
  - 通配符子域名：`"*.assets.example.com"`（不匹配根域名）

## 文件与图像限制（配置）

默认值可在 `gateway.http.endpoints.responses` 下进行调整：

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
            allowedMimes: [
              "image/jpeg",
              "image/png",
              "image/gif",
              "image/webp",
              "image/heic",
              "image/heif",
            ],
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
- HEIC/HEIF 格式 `input_image` 源被接受，并在交付给提供商前标准化为 JPEG。

安全说明：

- 主机名白名单在发起 fetch 前及每次重定向跳转时均被强制执行。
- 白名单中加入某主机名，并不能绕过私有/内部 IP 地址的拦截。
- 对于面向互联网暴露的网关，除应用层防护外，还应施加网络出口控制。  
  参见 [安全性](/gateway/security)。

## 流式传输（SSE）

设置 `stream: true` 以接收服务端事件（SSE）：

- `Content-Type: text/event-stream`
- 每个事件行均为 `event: <type>` 和 `data: <json>`
- 流式传输以 `data: [DONE]` 结束

当前发出的事件类型包括：

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

## 使用情况

当底层提供商报告 token 数量时，`usage` 将被填充。

## 错误

错误使用如下 JSON 对象格式：

```json
{ "error": { "message": "...", "type": "invalid_request_error" } }
```

常见情形：

- `401`：缺少或无效认证
- `400`：请求体无效
- `405`：HTTP 方法错误

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