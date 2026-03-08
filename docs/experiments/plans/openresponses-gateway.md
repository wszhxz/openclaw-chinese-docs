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

OpenClaw Gateway 当前在 `/v1/chat/completions` 暴露了一个最小化的 OpenAI 兼容 Chat Completions 端点（参见 [OpenAI Chat Completions](/gateway/openai-http-api)）。

Open Responses 是一个基于 OpenAI Responses API 的开放推理标准。它专为代理工作流设计，使用基于项目的输入加上语义流式传输事件。OpenResponses 规范定义了 `/v1/responses`，而不是 `/v1/chat/completions`。

## 目标

- 添加一个遵循 OpenResponses 语义的 `/v1/responses` 端点。
- 保留 Chat Completions 作为兼容性层，便于禁用并最终移除。
- 使用隔离的、可重用的模式标准化验证和解析。

## 非目标

- 第一版实现完整的 OpenResponses 功能对等（图像、文件、托管工具）。
- 替换内部代理执行逻辑或工具编排。
- 在第一阶段更改现有的 `/v1/chat/completions` 行为。

## 研究摘要

来源：OpenResponses OpenAPI、OpenResponses 规范站点以及 Hugging Face 博客文章。

提取的关键点：

- `POST /v1/responses` 接受 `CreateResponseBody` 字段，例如 `model`、`input`（字符串或 `ItemParam[]`）、`instructions`、`tools`、`tool_choice`、`stream`、`max_output_tokens` 和 `max_tool_calls`。
- `ItemParam` 是以下内容的区分联合：
  - 具有角色 `system`、`developer`、`user`、`assistant` 的 `message` 项目
  - `function_call` 和 `function_call_output`
  - `reasoning`
  - `item_reference`
- 成功的响应返回一个包含 `object: "response"`、`status` 和 `output` 项目的 `ResponseResource`。
- 流式传输使用语义事件，例如：
  - `response.created`、`response.in_progress`、`response.completed`、`response.failed`
  - `response.output_item.added`、`response.output_item.done`
  - `response.content_part.added`、`response.content_part.done`
  - `response.output_text.delta`、`response.output_text.done`
- 规范要求：
  - `Content-Type: text/event-stream`
  - `event:` 必须匹配 JSON `type` 字段
  - 终端事件必须是字面量 `[DONE]`
- 推理项目可能暴露 `content`、`encrypted_content` 和 `summary`。
- HF 示例在请求中包含 `OpenResponses-Version: latest`（可选头）。

## 建议架构

- 添加仅包含 Zod 模式的 `src/gateway/open-responses.schema.ts`（无网关导入）。
- 为 `/v1/responses` 添加 `src/gateway/openresponses-http.ts`（或 `open-responses-http.ts`）。
- 保持 `src/gateway/openai-http.ts` 完整，作为遗留兼容性适配器。
- 添加配置 `gateway.http.endpoints.responses.enabled`（默认 `false`）。
- 保持 `gateway.http.endpoints.chatCompletions.enabled` 独立；允许分别切换两个端点。
- 启用 Chat Completions 时发出启动警告以指示遗留状态。

## Chat Completions 弃用路径

- 保持严格的模块边界：responses 和 chat completions 之间没有共享的模式类型。
- 使 Chat Completions 通过配置选择加入，以便无需代码更改即可禁用。
- 一旦 `/v1/responses` 稳定，更新文档将 Chat Completions 标记为遗留版本。
- 可选的未来步骤：将 Chat Completions 请求映射到 Responses 处理器，以实现更简单的移除路径。

## 第一阶段支持子集

- 接受 `input` 作为字符串或带有消息角色和 `function_call_output` 的 `ItemParam[]`。
- 将系统和管理员消息提取到 `extraSystemPrompt` 中。
- 使用最新的 `user` 或 `function_call_output` 作为代理运行的当前消息。
- 使用 `invalid_request_error` 拒绝不支持的内容部分（图像/文件）。
- 返回单个助手消息，包含 `output_text` 内容。
- 返回 `usage`，值为零，直到连接令牌计费。

## 验证策略（无 SDK）

- 为支持的子集实现 Zod 模式：
  - `CreateResponseBody`
  - `ItemParam` + 消息内容部分联合
  - `ResponseResource`
  - 网关使用的流式传输事件形状
- 将模式保持在单一、隔离的模块中，以避免漂移并允许未来的代码生成。

## 流式传输实现（第一阶段）

- SSE 行同时包含 `event:` 和 `data:`。
- 必需序列（最低可行）：
  - `response.created`
  - `response.output_item.added`
  - `response.content_part.added`
  - `response.output_text.delta`（根据需要重复）
  - `response.output_text.done`
  - `response.content_part.done`
  - `response.completed`
  - `[DONE]`

## 测试和验证计划

- 为 `/v1/responses` 添加端到端覆盖：
  - 需要身份验证
  - 非流式响应形状
  - 流式事件顺序和 `[DONE]`
  - 带有头部和 `user` 的会话路由
- 保持 `src/gateway/openai-http.test.ts` 不变。
- 手动：使用 `stream: true` curl 到 `/v1/responses` 并验证事件顺序和终端 `[DONE]`。

## 文档更新（后续）

- 为 `/v1/responses` 用法和示例添加新文档页面。
- 更新 `/gateway/openai-http-api`，添加遗留说明并指向 `/v1/responses`。