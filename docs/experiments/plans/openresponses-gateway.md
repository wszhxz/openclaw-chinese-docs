---
summary: "Plan: Add OpenResponses /v1/responses endpoint and deprecate chat completions cleanly"
read_when:
  - Designing or implementing `/v1/responses` gateway support
  - Planning migration from Chat Completions compatibility
owner: "openclaw"
status: "draft"
last_updated: "2026-01-19"
title: "OpenResponses Gateway Plan"
---
# OpenResponses 网关集成计划

## 背景

OpenClaw 网关当前在 `/v1/chat/completions` 暴露一个最小化的、兼容 OpenAI 的 Chat Completions 接口（参见 [OpenAI Chat Completions](/gateway/openai-http-api)）。

Open Responses 是一个基于 OpenAI Responses API 的开放推理标准。它专为智能体（agentic）工作流设计，采用基于项（item-based）的输入以及语义化流式事件（semantic streaming events）。OpenResponses 规范定义了 `/v1/responses`，而非 `/v1/chat/completions`。

## 目标

- 新增一个符合 OpenResponses 语义的 `/v1/responses` 接口。
- 将 Chat Completions 保留为兼容性层，确保其易于禁用并最终移除。
- 使用隔离、可复用的 Schema 对验证与解析进行标准化。

## 非目标

- 首轮实现中不追求完整的 OpenResponses 功能对等（如图像、文件、托管工具支持）。
- 不替换内部智能体执行逻辑或工具编排机制。
- 第一阶段不更改现有 `/v1/chat/completions` 的行为。

## 研究摘要

资料来源：OpenResponses OpenAPI 文档、OpenResponses 规范网站及 Hugging Face 博客文章。

提取的关键要点如下：

- `POST /v1/responses` 接受以下 `CreateResponseBody` 字段：`model`、`input`（字符串或 `ItemParam[]`）、`instructions`、`tools`、`tool_choice`、`stream`、`max_output_tokens` 和 `max_tool_calls`。
- `ItemParam` 是一个带区分标识（discriminated union）的类型，包含：
  - 角色为 `system`、`developer`、`user`、`assistant` 的 `message` 项；
  - `function_call` 和 `function_call_output`；
  - `reasoning`；
  - `item_reference`。
- 成功响应返回一个含 `object: "response"`、`status` 和 `output` 项的 `ResponseResource`。
- 流式传输使用如下语义化事件：
  - `response.created`、`response.in_progress`、`response.completed`、`response.failed`；
  - `response.output_item.added`、`response.output_item.done`；
  - `response.content_part.added`、`response.content_part.done`；
  - `response.output_text.delta`、`response.output_text.done`。
- 规范要求：
  - `Content-Type: text/event-stream`；
  - `event:` 必须与 JSON 中的 `type` 字段一致；
  - 终止事件必须是字面量 `[DONE]`。
- 推理项（Reasoning items）可能暴露 `content`、`encrypted_content` 和 `summary`。
- Hugging Face 示例中包含请求头 `OpenResponses-Version: latest`（可选）。

## 建议架构

- 新增仅含 Zod Schema 的 `src/gateway/open-responses.schema.ts`（不引入任何网关模块）。
- 新增 `src/gateway/openresponses-http.ts`（或 `open-responses-http.ts`）用于 `/v1/responses`。
- 保持 `src/gateway/openai-http.ts` 不变，作为遗留兼容适配器。
- 新增配置项 `gateway.http.endpoints.responses.enabled`（默认值为 `false`）。
- 保持 `gateway.http.endpoints.chatCompletions.enabled` 独立；允许两个接口分别启用或禁用。
- 当启用 Chat Completions 时，在启动时输出警告，以表明其遗留状态。

## Chat Completions 的弃用路径

- 严格维护模块边界：Responses 与 Chat Completions 之间不得共享 Schema 类型。
- 将 Chat Completions 设为按配置启用（opt-in），使其可在不修改代码的前提下被禁用。
- 待 `/v1/responses` 稳定后，在文档中标注 Chat Completions 为遗留功能。
- 可选的后续步骤：将 Chat Completions 请求映射至 Responses 处理器，以简化移除流程。

## 第一阶段支持子集

- 接受 `input`（字符串或 `ItemParam[]`），含消息角色及 `function_call_output`。
- 将 system 和 developer 消息提取至 `extraSystemPrompt`。
- 在智能体运行中，使用最新一条的 `user` 或 `function_call_output` 作为当前消息。
- 对不支持的内容部分（图像/文件）返回 `invalid_request_error` 错误。
- 返回单条 assistant 消息，内容为 `output_text`。
- 返回 `usage`，其中各项暂设为零值，直至接入 token 统计逻辑。

## 验证策略（无 SDK）

- 为以下支持子集实现 Zod Schema：
  - `CreateResponseBody`；
  - `ItemParam` + 消息内容部分联合类型（unions）；
  - `ResponseResource`；
  - 网关所使用的流式事件结构（Streaming event shapes）。
- 将所有 Schema 置于单一、隔离的模块中，避免不一致，并便于未来代码生成（codegen）。

## 流式实现（第一阶段）

- SSE 行同时包含 `event:` 和 `data:`。
- 必需的最简事件序列如下：
  - `response.created`；
  - `response.output_item.added`；
  - `response.content_part.added`；
  - `response.output_text.delta`（按需重复）；
  - `response.output_text.done`；
  - `response.content_part.done`；
  - `response.completed`；
  - `[DONE]`。

## 测试与验证计划

- 为 `/v1/responses` 增加端到端（e2e）覆盖：
  - 需要身份认证；
  - 非流式响应结构；
  - 流式事件顺序及 `[DONE]`；
  - 带请求头与 `user` 的会话路由。
- 保持 `src/gateway/openai-http.test.ts` 不变。
- 手动测试：使用 curl 向 `/v1/responses` 发送含 `stream: true` 的请求，并验证事件顺序及终止事件 `[DONE]`。

## 文档更新（后续）

- 新增一页文档，介绍 `/v1/responses` 的使用方式与示例。
- 在 `/gateway/openai-http-api` 中添加“遗留功能”说明，并指向 `/v1/responses`。