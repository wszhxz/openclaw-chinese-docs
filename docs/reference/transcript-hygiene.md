---
summary: "Reference: provider-specific transcript sanitization and repair rules"
read_when:
  - You are debugging provider request rejections tied to transcript shape
  - You are changing transcript sanitization or tool-call repair logic
  - You are investigating tool-call id mismatches across providers
title: "Transcript Hygiene"
---
# 转录卫生（提供商修复）

本文档描述了在运行之前（构建模型上下文）应用于转录的**提供商特定修复**。这些是**内存中**的调整，用于满足严格的提供商要求。这些卫生步骤**不会**重写磁盘上的存储JSONL转录；但是，单独的会话文件修复传递可能会通过在加载会话之前丢弃无效行来重写格式错误的JSONL文件。当发生修复时，原始文件会与会话文件一起备份。

范围包括：

- 工具调用ID清理
- 工具调用输入验证
- 工具结果配对修复
- 回合验证/排序
- 思考签名清理
- 图像负载清理

如果需要转录存储详细信息，请参阅：

- [/reference/session-management-compaction](/reference/session-management-compaction)

---

## 运行位置

所有转录卫生都集中在嵌入式运行器中：

- 策略选择：`src/agents/transcript-policy.ts`
- 清理/修复应用：`sanitizeSessionHistory` 在 `src/agents/pi-embedded-runner/google.ts`

该策略使用 `provider`，`modelApi` 和 `modelId` 来决定应用什么。

独立于转录卫生，会话文件在加载前（如果需要）会被修复：

- `repairSessionFileIfNeeded` 在 `src/agents/session-file-repair.ts`
- 从 `run/attempt.ts` 和 `compact.ts` 调用（嵌入式运行器）

---

## 全局规则：图像清理

图像负载始终被清理以防止由于大小限制导致的提供商端拒绝（缩小/重新压缩过大的base64图像）。

实现：

- `sanitizeSessionMessagesImages` 在 `src/agents/pi-embedded-helpers/images.ts`
- `sanitizeContentBlocksImages` 在 `src/agents/tool-images.ts`

---

## 全局规则：格式错误的工具调用

缺少 `input` 和 `arguments` 的辅助工具调用块在构建模型上下文之前被丢弃。这可以防止部分持久化工具调用导致的提供商拒绝（例如，在速率限制失败后）。

实现：

- `sanitizeToolCallInputs` 在 `src/agents/session-transcript-repair.ts`
- 在 `sanitizeSessionHistory` 中 `src/agents/pi-embedded-runner/google.ts` 应用

---

## 提供商矩阵（当前行为）

**OpenAI / OpenAI Codex**

- 仅图像清理。
- 切换到OpenAI响应/Codex模型时，丢弃孤立的推理签名（没有后续内容块的独立推理项）。
- 无工具调用ID清理。
- 无工具结果配对修复。
- 无回合验证或重新排序。
- 无合成工具结果。
- 无思考签名剥离。

**Google (生成式AI / Gemini CLI / Antigravity)**

- 工具调用ID清理：严格的字母数字。
- 工具结果配对修复和合成工具结果。
- 回合验证（Gemini风格的回合交替）。
- Google回合排序修复（如果历史记录以助手开始，则前置一个微小的用户引导）。
- Antigravity Claude：规范化思考签名；丢弃未签名的思考块。

**Anthropic / Minimax (Anthropic兼容)**

- 工具结果配对修复和合成工具结果。
- 回合验证（合并连续的用户回合以满足严格的交替）。

**Mistral（包括基于model-id的检测）**

- 工具调用ID清理：严格的9位字母数字。

**OpenRouter Gemini**

- 思考签名清理：剥离非base64 `thought_signature` 值（保留base64）。

**其他所有**

- 仅图像清理。

---

## 历史行为（2026.1.22之前）

在2026.1.22发布之前，OpenClaw应用了多层转录卫生：

- 一个**transcript-sanitize扩展**在每次上下文构建时运行，并且可以：
  - 修复工具使用/结果配对。
  - 清理工具调用ID（包括一个非严格的模式，保留`_`/`-`）。
- 运行器还执行了提供商特定的清理，这重复了工作。
- 在提供商策略之外发生了额外的变异，包括：
  - 在持久化之前从助手文本中剥离`<final>`标签。
  - 丢弃空的助手错误回合。
  - 在工具调用后修剪助手内容。

这种复杂性导致跨提供商的退步（特别是`openai-responses` `call_id|fc_id` 配对）。2026.1.22清理移除了扩展，将逻辑集中到运行器中，并使OpenAI在图像清理之外**无需操作**。