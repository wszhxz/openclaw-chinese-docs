---
summary: "Plan: Add OpenResponses /v1/responses endpoint and deprecate chat completions cleanly"
owner: "openclaw"
status: "draft"
last_updated: "2026-01-19"
title: "OpenResponses Gateway Plan"
---
# OpenResponses网关集成计划

## 背景

OpenClaw网关目前在`/v1/chat/completions`端点暴露了一个最小的OpenAI兼容的Chat Completions接口（见[OpenAI Chat Completions](/gateway/openai-http-api)）。

OpenResponses是基于OpenAI Responses API的开放推理标准，专为代理工作流设计，使用基于项目的输入和语义流事件。OpenResponses规范定义了`/v1/responses`端点，而非`/v1/chat/completions`。

## 目标

- 添加符合OpenResponses语义的`/v1/responses`端点。
- 保持Chat Completions作为兼容层，易于禁用并最终移除。
- 使用隔离、可复用的模式统一验证和解析。

## 非目标

- 首次实现OpenResponses的全部功能（图像、文件、托管工具）。
- 替换内部代理执行逻辑或工具编排。
- 在第一阶段不更改现有的`/v1/chat/completions`行为。

## 研究摘要

来源：OpenResponses OpenAPI、OpenResponses规范站点和Hugging Face博客文章。

提取的关键点：

- `POST /v1/responses`接受`CreateResponseBody`字段，如`model`、`input`（字符串或`ItemParam[]`）、`instructions`、`tools`、`tool_choice`、`stream`、`max_output_tokens`和`max_tool_calls`。
- `ItemParam`是以下类型的区分联合：
  - `message`项，角色为`system`、`developer`、`user`、`assistant`
  - `function_call`和`function_call_output`
  - `reasoning`
  - `item_reference`
- 成功响应返回一个`ResponseResource`，包含`object: "response"`、`status`和`output`项。
- 流式传输使用语义事件，如：
  - `response.created`、`response.in_progress`、`response.completed`、`response.failed`
  - `response.output_item.added`、`response.output_item.done`
  - `response.content_part.added`、`response.content_part.done`
  - `response.output_text.delta`、`response.output_text.done`
- 规范要求：
  - `Content-Type: text/event-stream`
  - `event:`必须匹配JSON的`type`字段
  - 终止事件必须为字面量`[DONE]`
- 推理项可能暴露`content`、`encrypted_content`和`summary`。
- HF示例包括在请求中添加`OpenResponses-Version: latest`（可选头部）。

## 建议架构

- 添加`src/gateway/open-responses.schema.ts`，仅包含Zod模式（无网关导入）。
- 添加`src/gateway/openresponses-http.ts`（或`open-responses-http.ts`）用于`/v1/responses`。
- 保持`src/gateway/openai-http.ts`作为遗留兼容适配器。
- 添加配置`gateway.http.endpoints.responses.enabled`（默认`false`）。
- 保持`gateway.http.endpoints.chatCompletions.enabled`独立；允许两个端点分别切换。
- 当启用Chat Completions时发出启动警告以表明遗留状态。

## Chat Completions弃用路径

- 保持严格的模块边界：响应和Chat Completions之间无共享模式类型。
- 通过配置使Chat Completions可选启用，以便无需代码更改即可禁用。
- 在`/v1/responses`稳定后更新文档，将Chat Completions标记为遗留。
- 可选未来步骤：将Chat Completions请求映射到Responses处理程序以简化移除路径。

## 第一阶段支持子集

- 接受`input`作为字符串或包含消息角色和`function_call_output`的`ItemParam[]`。
- 将系统和开发者消息提取到`extraSystemPrompt`。
- 使用最近的`user`或`function_call_output`作为代理运行的当前消息。
- 用`invalid_request_error`拒绝不支持的内容部分（图像/文件）。
- 返回包含`output_text`内容的单个助手消息。
- 在令牌计费连接前返回`usage`且值为零。

## 验证策略（无SDK）

- 为以下支持子集实现Zod模式：
  - `CreateResponseBody`
  - `ItemParam` + 消息内容部分联合
  - `ResponseResource`
  - 网关使用的流式事件形状
- 将模式保留在单一、隔离的模块中以避免漂移并允许未来代码生成。

## 流式传输实现（第一阶段）

- 包含`event:`和`data:`的SSE行。
- 必需序列（最小可行）：
  - `response.created`
  - `response.output_item.added`
  - `response.content_part.added`
  - `response.output_text.delta`（按需重复）
  - `response.output_text.done`
  - `response.content_part.done`
  - `response.completed`
  - `[DONE]`

## 测试和验证计划

- 为`/v1/responses`添加端到端覆盖：
  - 需要认证
  - 非流式响应形状
  - 流式事件顺序和`[DONE]`
  - 使用头部和`user`的会话路由
- 保持`src/gateway/openai-http.e2e.test.ts`不变。
- 手动：使用`stream: true`向`/v1/responses`发送curl请求并验证事件顺序和终止`[DONE]`。

## 文档更新（后续）

- 为`/v1/responses`使用和示例添加新文档页面。
- 更新`/gateway/openai-http-api`添加遗留说明并指向`/v1/responses`。