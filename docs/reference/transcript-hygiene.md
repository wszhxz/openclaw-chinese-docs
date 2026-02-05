---
summary: "Reference: provider-specific transcript sanitization and repair rules"
read_when:
  - You are debugging provider request rejections tied to transcript shape
  - You are changing transcript sanitization or tool-call repair logic
  - You are investigating tool-call id mismatches across providers
title: "Transcript Hygiene"
---
# 转录清洁（提供者修复）

本文档描述了在运行前（构建模型上下文）应用于转录的**特定提供者修复**。
这些是用于满足严格提供者要求的**内存中**调整。这些清洁步骤**不会**重写磁盘上存储的JSONL转录；
但是，单独的会话文件修复过程可能会通过删除无效行来重写格式错误的JSONL文件，
然后加载会话。当发生修复时，原始文件会与会话文件一起备份。

范围包括：

- 工具调用ID清理
- 工具调用输入验证
- 工具结果配对修复
- 轮次验证/排序
- 思考签名清理
- 图像载荷清理

如果您需要转录存储详细信息，请参见：

- [/reference/session-management-compaction](/reference/session-management-compaction)

---

## 运行位置

所有转录清洁都集中在嵌入式运行器中：

- 策略选择：`src/agents/transcript-policy.ts`
- 清理/修复应用：`sanitizeSessionHistory` 在 `src/agents/pi-embedded-runner/google.ts` 中

策略使用 `provider`、`modelApi` 和 `modelId` 来决定应用什么。

与转录清洁分开，会话文件在加载前会被修复（如果需要）：

- `repairSessionFileIfNeeded` 在 `src/agents/session-file-repair.ts` 中
- 从 `run/attempt.ts` 和 `compact.ts` 调用（嵌入式运行器）

---

## 全局规则：图像清理

图像载荷总是被清理以防止由于大小限制而被提供者拒绝
（缩小/重新压缩过大的base64图像）。

实现：

- `sanitizeSessionMessagesImages` 在 `src/agents/pi-embedded-helpers/images.ts` 中
- `sanitizeContentBlocksImages` 在 `src/agents/tool-images.ts` 中

---

## 全局规则：格式错误的工具调用

缺少 `input` 和 `arguments` 的助手工具调用块会在构建模型上下文之前被丢弃。
这可以防止由于部分持久化的工具调用而导致的提供者拒绝
（例如，在速率限制失败后）。

实现：

- `sanitizeToolCallInputs` 在 `src/agents/session-transcript-repair.ts` 中
- 应用于 `sanitizeSessionHistory` 在 `src/agents/pi-embedded-runner/google.ts` 中

---

## 提供者矩阵（当前行为）

**OpenAI / OpenAI Codex**

- 仅图像清理。
- 在切换到OpenAI Responses/Codex时，丢弃孤立的推理签名（没有后续内容块的独立推理项目）。
- 无工具调用ID清理。
- 无工具结果配对修复。
- 无轮次验证或重新排序。
- 无合成工具结果。
- 无思考签名剥离。

**Google (Generative AI / Gemini CLI / Antigravity)**

- 工具调用ID清理：严格的字母数字。
- 工具结果配对修复和合成工具结果。
- 轮次验证（Gemini风格的轮次交替）。
- Google轮次排序修复（如果历史记录以助手开始，则前置一个微小的用户引导）。
- Antigravity Claude：标准化思考签名；丢弃未签名的思考块。

**Anthropic / Minimax (Anthropic兼容)**

- 工具结果配对修复和合成工具结果。
- 轮次验证（合并连续的用户轮次以满足严格交替）。

**Mistral（包括基于模型ID的检测）**

- 工具调用ID清理：strict9（字母数字长度9）。

**OpenRouter Gemini**

- 思考签名清理：剥离非base64的 `thought_signature` 值（保留base64）。

**其他所有**

- 仅图像清理。

---

## 历史行为（2026.1.22之前）

在2026.1.22版本之前，OpenClaw应用了多层转录清洁：

- **转录清理扩展** 在每次上下文构建时运行，可以：
  - 修复工具使用/结果配对。
  - 清理工具调用ID（包括保留 `_`/`-` 的非严格模式）。
- 运行器还执行特定提供者的清理，这重复了工作。
- 在提供者策略之外还发生了额外的变异，包括：
  - 在持久化之前从助手文本中剥离 `<final>` 标签。
  - 丢弃空的助手错误轮次。
  - 在工具调用后修剪助手内容。

这种复杂性导致了跨提供者回归（特别是 `openai-responses`
`call_id|fc_id` 配对）。2026.1.22清理移除了扩展，在运行器中集中了逻辑，
并使OpenAI除了图像清理外保持**不接触**。