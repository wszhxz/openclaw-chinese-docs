---
summary: "Reference: provider-specific transcript sanitization and repair rules"
read_when:
  - You are debugging provider request rejections tied to transcript shape
  - You are changing transcript sanitization or tool-call repair logic
  - You are investigating tool-call id mismatches across providers
title: "Transcript Hygiene"
---
# 转录文本卫生（提供方修复）

本文档描述在运行前（构建模型上下文）对转录文本应用的**特定于提供方的修复措施**。这些是用于满足各提供方严格要求的**内存中**调整。此类卫生处理**不会**重写磁盘上存储的 JSONL 格式转录文件；不过，一个独立的会话文件修复流程可能会在加载会话前通过丢弃无效行来重写格式错误的 JSONL 文件。当发生修复时，原始文件将与会话文件一同备份。

涵盖范围包括：

- 工具调用 ID 清洗  
- 工具调用输入验证  
- 工具结果配对修复  
- 对话轮次验证 / 排序  
- 思维签名清理  
- 图像载荷清洗  
- 用户输入来源标记（用于跨会话路由的提示）

如需了解转录文本存储详情，请参阅：

- [/reference/session-management-compaction](/reference/session-management-compaction)

---

## 执行位置

所有转录文本卫生处理均集中于嵌入式运行器（embedded runner）中：

- 策略选择：`src/agents/transcript-policy.ts`  
- 清洗 / 修复应用：`sanitizeSessionHistory` 中的 `src/agents/pi-embedded-runner/google.ts`

该策略使用 `provider`、`modelApi` 和 `modelId` 来决定启用哪些修复项。

与转录文本卫生处理分离的是：会话文件会在加载前（如需）进行修复：

- `repairSessionFileIfNeeded` 中的 `src/agents/session-file-repair.ts`  
- 由 `run/attempt.ts` 和 `compact.ts`（嵌入式运行器）调用  

---

## 全局规则：图像清洗

图像载荷始终被清洗，以防止因尺寸超限而导致提供方拒绝（对过大的 base64 图像执行降采样 / 重新压缩）。

此举亦有助于控制视觉模型所承受的图像驱动型 token 压力。较低的最大边长通常可减少 token 消耗；较高边长则保留更多细节。

实现方式：

- `sanitizeSessionMessagesImages` 中的 `src/agents/pi-embedded-helpers/images.ts`  
- `sanitizeContentBlocksImages` 中的 `src/agents/tool-images.ts`  
- 最大图像边长可通过 `agents.defaults.imageMaxDimensionPx` 配置（默认值：`1200`）

---

## 全局规则：格式错误的工具调用

对于缺失 `input` 和 `arguments` 两者的助手端工具调用块，在构建模型上下文前即被丢弃。此举可避免因部分持久化的工具调用（例如在遭遇速率限制失败后）引发提供方拒绝。

实现方式：

- `sanitizeToolCallInputs` 中的 `src/agents/session-transcript-repair.ts`  
- 在 `sanitizeSessionHistory`（位于 `src/agents/pi-embedded-runner/google.ts` 中）中应用  

---

## 全局规则：跨会话输入来源追踪

当代理通过 `sessions_send`（含代理间回复 / 广播步骤）向另一会话发送提示时，OpenClaw 将创建的用户轮次持久化，并附带以下元数据：

- `message.provenance.kind = "inter_session"`

该元数据在追加转录文本时写入，且不更改角色（为保障提供方兼容性，`role: "user"` 角色保持不变）。转录文本读取器可利用此信息，避免将经路由的内部提示误判为终端用户编写的指令。

在上下文重建过程中，OpenClaw 还会在内存中为这些用户轮次前置一个简短的 `[Inter-session message]` 标记，以便模型区分其与外部终端用户指令。

---

## 提供方矩阵（当前行为）

**OpenAI / OpenAI Codex**

- 仅执行图像清洗。  
- 针对 OpenAI Responses / Codex 转录文本，丢弃孤立的推理签名（即无后续内容块的独立推理项）。  
- 不执行工具调用 ID 清洗。  
- 不执行工具结果配对修复。  
- 不执行轮次验证或重排序。  
- 不生成合成工具结果。  
- 不剥离思维签名。

**Google（Generative AI / Gemini CLI / Antigravity）**

- 工具调用 ID 清洗：严格限定为字母数字字符。  
- 工具结果配对修复及合成工具结果生成。  
- 轮次验证（遵循 Gemini 风格的轮次交替规则）。  
- Google 轮次顺序修复（若历史记录以助手轮次开头，则前置一个极小的用户引导轮次）。  
- Antigravity Claude：标准化思维签名；丢弃无签名的思维块。

**Anthropic / Minimax（兼容 Anthropic 协议）**

- 工具结果配对修复及合成工具结果生成。  
- 轮次验证（合并连续的用户轮次，以满足严格的交替要求）。

**Mistral（含基于 model-id 的检测）**

- 工具调用 ID 清洗：strict9（长度为 9 的字母数字字符串）。

**OpenRouter Gemini**

- 思维签名清理：剔除非 base64 格式的 `thought_signature` 值（保留 base64 格式值）。

**其他所有提供方**

- 仅执行图像清洗。

---

## 历史行为（2026.1.22 版本之前）

在 2026.1.22 版本发布前，OpenClaw 应用了多层转录文本卫生处理：

- **transcript-sanitize 扩展**在每次构建上下文时运行，可执行以下操作：  
  - 修复工具调用与结果的配对关系。  
  - 清洗工具调用 ID（含一种非严格模式，可保留 `_` / `-`）。  
- 运行器本身也执行提供方特定的清洗操作，导致功能重复。  
- 此外，还有若干变更发生在提供方策略之外，包括：  
  - 在持久化前从助手文本中剥离 `<final>` 标签。  
  - 丢弃空的助手错误轮次。  
  - 在工具调用后截断助手内容。

该复杂性曾引发跨提供方回归问题（尤其是 `openai-responses` 与 `call_id|fc_id` 的配对问题）。2026.1.22 版本的清理工作移除了该扩展，将逻辑统一收归运行器管理，并使 OpenAI 成为**除图像清洗外完全免干预**的提供方。