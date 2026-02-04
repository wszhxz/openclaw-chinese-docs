---
summary: "Harden cron.add input handling, align schemas, and improve cron UI/agent tooling"
owner: "openclaw"
status: "complete"
last_updated: "2026-01-05"
title: "Cron Add Hardening"
---
# Cron Add Hardening & Schema Alignment

## 上下文

最近的网关日志显示重复的 `cron.add` 失败，参数无效（缺少 `sessionTarget`，`wakeMode`，`payload`，以及格式错误的 `schedule`）。这表明至少有一个客户端（可能是代理工具调用路径）正在发送包装或部分指定的任务负载。另外，TypeScript 中的 cron 提供者枚举、网关架构、CLI 标志和 UI 表单类型之间存在差异，此外 `cron.status` 的 UI 不匹配（期望 `jobCount` 而网关返回 `jobs`）。

## 目标

- 通过规范化常见的包装负载并推断缺失的 `kind` 字段来停止 `cron.add` INVALID_REQUEST 垃圾信息。
- 在网关架构、cron 类型、CLI 文档和 UI 表单中对齐 cron 提供者列表。
- 明确代理 cron 工具架构，使 LLM 生成正确的任务负载。
- 修复 Control UI cron 状态作业计数显示。
- 添加测试以涵盖规范化和工具行为。

## 非目标

- 更改 cron 调度语义或作业执行行为。
- 添加新的调度种类或 cron 表达式解析。
- 超出必要的字段修复范围对 cron 的 UI/UX 进行大修。

## 发现（当前差距）

- 网关中的 `CronPayloadSchema` 排除了 `signal` + `imessage`，而 TS 类型包括它们。
- Control UI CronStatus 期望 `jobCount`，但网关返回 `jobs`。
- 代理 cron 工具架构允许任意的 `job` 对象，从而启用格式错误的输入。
- 网关严格验证 `cron.add` 并不进行规范化，因此包装的负载会失败。

## 有何变化

- `cron.add` 和 `cron.update` 现在规范化常见的包装形状并推断缺失的 `kind` 字段。
- 代理 cron 工具架构与网关架构匹配，从而减少了无效负载。
- 提供者枚举在网关、CLI、UI 和 macOS 选择器之间对齐。
- Control UI 使用网关的 `jobs` 计数字段进行状态显示。

## 当前行为

- **规范化：** 包装的 `data`/`job` 负载被解包；当安全时推断 `schedule.kind` 和 `payload.kind`。
- **默认值：** 当缺少时，为 `wakeMode` 和 `sessionTarget` 应用安全默认值。
- **提供者：** Discord/Slack/Signal/iMessage 现在在 CLI/UI 中一致显示。

参见 [Cron jobs](/automation/cron-jobs) 获取规范化的形状和示例。

## 验证

- 监视网关日志以减少 `cron.add` INVALID_REQUEST 错误。
- 确认刷新后 Control UI cron 状态显示作业计数。

## 可选后续操作

- 手动 Control UI 测试：为每个提供者添加一个 cron 作业 + 验证状态作业计数。

## 开放问题

- `cron.add` 是否应接受来自客户端的显式 `state`（目前架构不允许）？
- 我们是否应允许 `webchat` 作为显式的交付提供者（目前在交付解析中被过滤）？