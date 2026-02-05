---
summary: "Plan: Add OpenResponses /v1/responses endpoint and deprecate chat completions cleanly"
owner: "openclaw"
status: "draft"
last_updated: "2026-01-19"
title: "OpenResponses Gateway Plan"
---
# OpenResponses 网关集成计划

## 上下文

OpenClaw 网关目前在 `/v1/chat/completions` 暴露了一个最小的 OpenAI 兼容的 Chat Completions 终端（参见 [OpenAI Chat Completions](/gateway/openai-http-api)）。

Open Responses 是一个基于 OpenAI Responses API 的开放推理标准。它专为代理工作流设计，并使用基于项目的输入加上语义流事件。OpenResponses 规范定义了 `/v1/responses`，而不是 `/v1/chat/completions`。

## 目标

- 添加一个符合 OpenResponses 语义的 `/v1/responses` 终端。
- 将 Chat Completions 作为兼容层保留，使其易于禁用并最终移除。
- 使用隔离的、可重用的架构标准化验证和解析。

## 非目标

- 在第一次迭代中实现完整的 OpenResponses 功能对等性（图像、文件、托管工具）。
- 替换内部代理执行逻辑或工具编排。
- 在第一阶段更改现有的 `/v1/chat/completions` 行为。

## 研究总结

来源：OpenResponses OpenAPI、OpenResponses 规范网站以及 Hugging Face 博客文章。

提取的关键点：

- `POST /v1/responses` 接受 `CreateResponseBody` 字段，如 `model`、`input`（字符串或 `ItemParam[]`）、`instructions`、`tools`、`tool_choice`、`stream`、`max_output_tokens` 和 `max_tool_calls`。
- `ItemParam` 是一个判别联合体，包含：
  - 具有角色 `system`、`developer`、`user`、`assistant` 的 `message` 项目
  - `function_call` 和 `function_call_output`
  - `reasoning`
  - `item_reference`
- 成功响应返回一个带有 `object: "response"`、`status` 和 `output` 项目的 `ResponseResource`。
- 流式传输使用语义事件，例如：
  - `response.created`、`response.in_progress`、`response.completed`、`response.failed`
  - `response.output_item.added`、`response.output_item.done`
  - `response.content_part.added`、`response.content_part.done`
  - `response.output_text.delta`、`response.output_text.done`
- 规范要求：
  - `Content-Type: text/event-stream`
  - `event:` 必须与 JSON `type` 字段匹配
  - 终止事件必须是字面量 `[DONE]`
- 推理项目可能暴露 `content`、`encrypted_content` 和 `summary`。
- HF 示例包括请求中的 `OpenResponses-Version: latest`（可选标题）。

## 建议架构

- 添加仅包含 Zod 架构的 `src/gateway/open-responses.schema.ts`（不包含网关导入）。
- 添加 `src/gateway/openresponses-http.ts`（或 `open-responses-http.ts`）用于 `/v1/responses`。
- 保持 `src/gateway/openai-http.ts` 完整作为遗留兼容适配器。
- 添加配置 `gateway.http.endpoints.responses.enabled`（默认 `false`）。
- 保持 `gateway.http.endpoints.chatCompletions.enabled` 独立；允许两个终端分别切换。
- 当启用 Chat Completions 时发出启动警告以指示遗留状态。

## Chat Completions 废弃路径

- 维护严格的模块边界：响应和聊天完成之间没有共享的架构类型。
- 通过配置使 Chat Completions 成为可选功能，以便无需代码更改即可禁用。
- 更新文档以在 `/v1/responses` 稳定后标记 Chat Completions 为遗留。
- 可选的未来步骤：将 Chat Completions 请求映射到响应处理程序以简化移除路径。

## 第一阶段支持子集

- 接受作为字符串或 `ItemParam[]` 的 `input`，具有消息角色和 `function_call_output`。
- 将系统和开发人员消息提取到 `extraSystemPrompt`。
- 使用最近的 `user` 或 `function_call_output` 作为代理运行的当前消息。
- 拒绝不受支持的内容部分（图像/文件）使用 `invalid_request_error`。
- 返回带有 `output_text` 内容的单个助手消息。
- 返回带有零值的 `usage`，直到令牌计数连接。

## 验证策略（无 SDK）

- 实现支持子集的 Zod 架构：
  - `CreateResponseBody`
  - `ItemParam` + 消息内容部分联合体
  - `ResponseResource`
  - 网关使用的流事件形状
- 将架构保留在一个单独的、隔离的模块中以避免漂移并允许未来的代码生成。

## 流式实现（第一阶段）

- 包含 `event:` 和 `data:` 的 SSE 行。
- 所需序列（最小可行）：
  - `response.created`
  - `response.output_item.added`
  - `response.content_part.added`
  - `response.output_text.delta`（按需重复）
  - `response.output_text.done`
  - `response.content_part.done`
  - `response.completed`
  - `[DONE]`

## 测试和验证计划

- 为 `/v1/responses` 添加端到端覆盖：
  - 需要身份验证
  - 非流响应形状
  - 流事件顺序和 `[DONE]`
  - 使用标题和 `user` 的会话路由
- 保持 `src/gateway/openai-http.e2e.test.ts` 不变。
- 手动：使用 `stream: true` 向 `/v1/responses` 发送 curl 并验证事件顺序和终止 `[DONE]`。

## 文档更新（后续）

- 为 `/v1/responses` 使用和示例添加新文档页面。
- 使用遗留说明和指向 `/v1/responses` 的指针更新 `/gateway/openai-http-api`。