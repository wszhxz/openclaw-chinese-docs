---
summary: "Holy grail refactor plan for one unified runtime streaming pipeline across main, subagent, and ACP"
owner: "onutc"
status: "draft"
last_updated: "2026-02-25"
title: "Unified Runtime Streaming Refactor Plan"
---
# 统一运行时流式处理重构计划

## 目标

为 `main`、`subagent` 和 `acp` 提供一条共享的流式处理流水线，确保所有运行时在文本合并（coalescing）、分块（chunking）、投递顺序（delivery ordering）以及崩溃恢复（crash recovery）行为上完全一致。

## 此计划存在的原因

- 当前行为分散在多条面向不同运行时的整形路径中。
- 格式化/合并类缺陷可能在一个路径中被修复，却仍存在于其他路径中。
- 投递一致性、重复抑制（duplicate suppression）和恢复语义更难进行统一推理。

## 目标架构

单一流水线 + 运行时专用适配器：

1. 运行时适配器仅输出规范事件（canonical events）。
2. 共享流式组装器（shared stream assembler）负责合并与最终化文本/工具/状态事件。
3. 共享通道投影器（shared channel projector）仅执行一次通道专属的分块/格式化操作。
4. 共享投递账本（shared delivery ledger）强制实施幂等发送/重放语义。
5. 出站通道适配器（outbound channel adapter）执行实际发送并记录投递检查点。

规范事件契约（Canonical event contract）：

- `turn_started`
- `text_delta`
- `block_final`
- `tool_started`
- `tool_finished`
- `status`
- `turn_completed`
- `turn_failed`
- `turn_cancelled`

## 工作流

### 1) 规范流式处理契约

- 在核心模块中明确定义严格的事件 Schema 并加入校验逻辑。
- 增加适配器契约测试（adapter contract tests），确保每个运行时均能输出兼容的事件。
- 尽早拒绝格式错误的运行时事件，并输出结构化的诊断信息。

### 2) 共享流式处理器

- 用单一处理器替代各运行时专用的合并器（coalescer）/投影器（projector）逻辑。
- 该处理器负责文本增量缓冲（text delta buffering）、空闲刷新（idle flush）、最大分块切分（max-chunk splitting）及完成刷新（completion flush）。
- 将 ACP/主代理/子代理配置解析逻辑统一移入一个辅助模块，防止逻辑漂移（drift）。

### 3) 共享通道投影

- 保持通道适配器“无脑”：仅接收已最终化的数据块并执行发送。
- 将 Discord 专用的分块异常行为（quirks）仅保留在通道投影器中。
- 在投影之前，整个流水线对通道保持不可知（channel-agnostic）。

### 4) 投递账本 + 重放机制

- 为每轮对话（per-turn）及每个分块（per-chunk）添加唯一投递 ID。
- 在物理发送前后均记录检查点（checkpoints）。
- 发生重启时，以幂等方式重放待处理分块，并避免重复投递。

### 5) 迁移与切换

- 第一阶段：影子模式（shadow mode）—— 新流水线计算输出，但由旧路径执行发送；对比两者结果。
- 第二阶段：按运行时逐个切换（`acp` → `subagent` → `main`，或依风险等级反向切换）。
- 第三阶段：删除所有遗留的运行时专用流式处理代码。

## 非目标事项（Non-goals）

- 本次重构不涉及 ACP 策略/权限模型的任何变更。
- 不在投影兼容性修复之外扩展任何通道专属功能。
- 不重构传输层/后端（acpx 插件契约维持现状，除非为实现事件一致性所必需）。

## 风险与缓解措施

- 风险：现有主代理/子代理路径出现行为退化（behavioral regressions）。  
  缓解措施：影子模式差异比对 + 适配器契约测试 + 通道端到端测试。
- 风险：崩溃恢复期间发生重复发送。  
  缓解措施：持久化投递 ID + 在投递适配器中实现幂等重放。
- 风险：运行时适配器再次出现逻辑分歧。  
  缓解措施：强制所有适配器必须通过统一的共享契约测试套件。

## 验收标准

- 所有运行时均通过共享流式处理契约测试。
- Discord ACP/主代理/子代理对微小增量（tiny deltas）生成完全一致的间距与分块行为。
- 崩溃/重启后的重放机制不会对同一投递 ID 发送重复分块。
- 遗留 ACP 投影器/合并器路径已被彻底移除。
- 流式处理配置解析逻辑已统一共享，且与运行时无关。