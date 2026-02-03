---
summary: "Reference: provider-specific transcript sanitization and repair rules"
read_when:
  - You are debugging provider request rejections tied to transcript shape
  - You are changing transcript sanitization or tool-call repair logic
  - You are investigating tool-call id mismatches across providers
title: "Transcript Hygiene"
---
# 对话记录卫生（提供者修复）

本文档描述了**提供者特定修复措施**，这些措施在运行前（构建模型上下文）应用于对话记录。这些是**内存中**的调整，用于满足严格提供者要求。它们**不会**重写存储在磁盘上的JSONL对话记录。

涵盖范围包括：

- 工具调用ID清理
- 工具结果配对修复
- 回合验证/排序
- 思维签名清理
- 图像负载清理

如需了解对话记录存储细节，请参阅：

- [/reference/session-management-compaction](/reference/session-management-compaction)

---

## 该功能的运行位置

所有对话记录卫生功能均集中于嵌入式运行器中：

- 策略选择：`src/agents/transcript-policy.ts`
- 清理/修复应用：`src/agents/pi-embedded-runner/google.ts` 中的 `sanitizeSessionHistory`

策略使用 `provider`、`modelApi` 和 `modelId` 来决定应用哪些规则。

---

## 全局规则：图像清理

图像负载始终会进行清理，以防止因大小限制导致提供方拒绝（缩放/重新压缩过大Base64图像）。

实现方式：

- `src/agents/pi-embedded-helpers/images.ts` 中的 `sanitizeSessionMessagesImages`
- `src/agents/tool-images.ts` 中的 `sanitizeContentBlocksImages`

---

## 提供者矩阵（当前行为）

**OpenAI / OpenAI Codex**

- 仅图像清理。
- 在切换到OpenAI Responses/Codex模型时，丢弃孤立的推理签名（无后续内容块的独立推理项）。
- 不进行工具调用ID清理。
- 不进行工具结果配对修复。
- 不进行回合验证或重新排序。
- 不生成合成工具结果。
- 不剥离思维签名。

**Google（生成式AI / Gemini CLI / Antigravity）**

- 工具调用ID清理：严格字母数字。
- 工具结果配对修复和合成工具结果。
- 回合验证（Gemini风格的回合交替）。
- Google回合排序修复（如果历史记录以助理开头，则前置一个极小的用户引导）。
- Antigravity Claude：标准化思维签名；丢弃无签名的思维块。

**Anthropic / Minimax（兼容Anthropic）**

- 工具结果配对修复和合成工具结果。
- 回合验证（合并连续用户回合以满足严格交替）。

**Mistral（包括基于模型ID的检测）**

- 工具调用ID清理：严格9（字母数字长度为9）。

**OpenRouter Gemini**

- 思维签名清理：剥离非Base64的 `thought_signature` 值（保留Base64）。

**其他所有情况**

- 仅图像清理。

---

## 历史行为（2026.1.22之前）

在2026.1.22版本发布之前，OpenClaw对对话记录应用了多层清理：

- 一个**对话记录清理扩展**在每次上下文构建时运行，可以：
  - 修复工具使用/结果配对。
  - 清理工具调用ID（包括非严格模式，保留 `_`/`-`）。
- 运行器还执行提供者特定清理，导致重复工作。
- 还有其他在提供者策略之外发生的修改，包括：
  - 在持久化前剥离助理文本中的 `<final>` 标签。
  - 删除空的助理错误回合。
  - 工具调用后修剪助理内容。

这种复杂性导致跨提供者回归（尤其是 `openai-responses` 的 `call_id|fc_id` 配对）。2026.1.22的清理移除了扩展，将逻辑集中到运行器中，并使OpenAI在图像清理之外**不再进行任何操作**。