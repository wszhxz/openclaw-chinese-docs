---
summary: "Context window + compaction: how OpenClaw keeps sessions under model limits"
read_when:
  - You want to understand auto-compaction and /compact
  - You are debugging long sessions hitting context limits
title: "Compaction"
---
# 上下文窗口与压缩

每个模型都有一个**上下文窗口**（即它所能处理的最大 token 数）。长时间运行的对话会不断累积消息和工具执行结果；当上下文窗口即将填满时，OpenClaw 会**压缩**较早的历史记录，以确保始终处于限制范围内。

## 什么是压缩

压缩会将**较早的对话内容总结为一条精简的摘要条目**，同时保留最近的消息不变。该摘要会被存入会话历史中，因此后续请求将使用：

- 压缩生成的摘要  
- 压缩点之后的近期消息

压缩操作会在会话的 JSONL 历史中**持久化保存**。

## 配置

在您的 `openclaw.json` 中使用 `agents.defaults.compaction` 设置来配置压缩行为（模式、目标 token 数等）。  
默认情况下，压缩摘要会保留不透明标识符（`identifierPolicy: "strict"`）。您可通过 `identifierPolicy: "off"` 覆盖该行为，或通过 `identifierPolicy: "custom"` 和 `identifierInstructions` 提供自定义文本。

## 自动压缩（默认启用）

当会话接近或超出模型的上下文窗口限制时，OpenClaw 将自动触发压缩，并可能使用压缩后的上下文重试原始请求。

您将看到：

- 在详细模式（verbose mode）下输出 `🧹 Auto-compaction complete`  
- `/status` 显示 `🧹 Compactions: <count>`

在压缩之前，OpenClaw 可执行一次**静默内存刷新（silent memory flush）** 轮次，将持久化笔记写入磁盘。详情及配置请参阅 [Memory](/concepts/memory)。

## 手动压缩

使用 `/compact`（可选地附带指令）强制执行一次压缩操作：

```
/compact Focus on decisions and open questions
```

## 上下文窗口来源

上下文窗口是模型特定的。OpenClaw 根据所配置提供方目录中的模型定义来确定其限制。

## 压缩 vs 截断（pruning）

- **压缩**：对历史进行总结，并在 JSONL 中**持久化保存**。  
- **会话截断（session pruning）**：仅在内存中按请求**截去旧的工具执行结果**。

有关截断的详细信息，请参阅 [/concepts/session-pruning](/concepts/session-pruning)。

## OpenAI 服务端压缩

OpenClaw 还支持为兼容的直连 OpenAI 模型提供 OpenAI Responses 的服务端压缩提示（server-side compaction hints）。这与本地 OpenClaw 压缩相互独立，且可并行运行。

- 本地压缩：OpenClaw 执行摘要并将其持久化到会话 JSONL 中。  
- 服务端压缩：当启用 `store` + `context_management` 时，OpenAI 在提供方侧对上下文进行压缩。

有关模型参数与覆盖配置，请参阅 [OpenAI provider](/providers/openai)。

## 使用建议

- 当会话感觉陈旧或上下文过于臃肿时，请使用 `/compact`。  
- 大型工具输出本身已被截断；进一步启用截断（pruning）可减少工具结果的持续堆积。  
- 若需要彻底清空上下文，请使用 `/new` 或 `/reset` 启动一个全新的会话 ID。