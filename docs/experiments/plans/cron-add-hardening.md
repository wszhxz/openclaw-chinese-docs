---
summary: "Harden cron.add input handling, align schemas, and improve cron UI/agent tooling"
owner: "openclaw"
status: "complete"
last_updated: "2026-01-05"
title: "Cron Add Hardening"
---
# Cron Add 加固与模式对齐

## 背景

最近网关日志显示重复的 `cron.add` 失败，原因包括无效参数（缺少 `sessionTarget`、`wakeMode`、`payload`，以及格式错误的 `schedule`）。这表明至少有一个客户端（很可能是代理工具调用路径）正在发送包装或部分指定的任务负载。此外，TypeScript 中的 cron 提供者枚举、网关模式、CLI 标志和 UI 表单类型之间存在差异，同时 `cron.status` 的 UI 存在不匹配（期望 `jobCount`，而网关返回 `jobs`）。

## 目标

- 通过规范化常见包装负载并推断缺失的 `kind` 字段，停止 `cron.add` 的 INVALID_REQUEST 垃圾日志。
- 在网关模式、cron 类型、CLI 文档和 UI 表单之间对齐 cron 提供者列表。
- 明确代理 cron 工具模式，使 LLM 生成正确的任务负载。
- 修复控制台 UI 的 cron 状态任务计数显示。
- 添加测试以覆盖规范化和工具行为。

## 非目标

- 不改变 cron 调度语义或任务执行行为。
- 不添加新的调度类型或 cron 表达式解析。
- 不对 cron 的 UI/UX 进行超出必要字段修复的全面改版。

## 发现（当前差距）

- 网关中的 `CronPayloadSchema` 排除 `signal` + `imessage`，而 TS 类型包含它们。
- 控制台 UI 的 CronStatus 期望 `jobCount`，但网关返回 `jobs`。
- 代理 cron 工具模式允许任意 `job` 对象，导致格式错误的输入。
- 网关严格验证 `cron.add` 且不进行规范化，因此包装的负载会失败。

## 已更改内容

- `cron.add` 和 `cron.update` 现在会规范化常见包装形状并推断缺失的 `kind` 字段。
- 代理 cron 工具模式与网关模式一致，从而减少无效负载。
- 提供者枚举在网关、CLI、UI 和 macOS 选择器之间对齐。
- 控制台 UI 使用网关的 `jobs` 计数字段显示状态。

## 当前行为

- **规范化：** 包装的 `data`/`job` 负载被解包；当安全时，`schedule.kind` 和 `payload.kind` 会被推断。
- **默认值：** 当缺失时，`wakeMode` 和 `sessionTarget` 会应用安全默认值。
- **提供者：** Discord/Slack/Signal/iMessage 现在在 CLI/UI 中一致展示。

查看 [Cron 任务](/automation/cron-jobs) 了解规范化后的形状和示例。

## 验证

- 监控网关日志，确认 `cron.add` 的 INVALID_REQUEST 错误减少。
- 确认控制台 UI 的 cron 状态在刷新后显示任务计数。

## 可选后续操作

- 手动控制台 UI 测试：为每个提供者添加 cron 任务 + 验证状态任务计数。

## 开放问题

- 是否应允许 `cron.add` 从客户端接收显式的 `state`（当前模式禁止）？
- 是否应允许 `webchat` 作为显式的交付提供者（当前在交付解析中被过滤）？