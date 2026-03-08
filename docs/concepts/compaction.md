---
summary: "Context window + compaction: how OpenClaw keeps sessions under model limits"
read_when:
  - You want to understand auto-compaction and /compact
  - You are debugging long sessions hitting context limits
title: "Compaction"
---
# 上下文窗口与压缩

每个模型都有一个 **上下文窗口**（它能看到的最大 tokens 数）。长时间运行的聊天会积累消息和工具结果；一旦窗口空间紧张，OpenClaw 会 **压缩** 旧的历史记录以保持在限制范围内。

## 什么是压缩

压缩将 **旧对话总结** 为一个紧凑的摘要条目，并保持最近的消息完整。摘要存储在会话历史中，因此未来的请求会使用：

- 压缩摘要
- 压缩点之后的最近消息

压缩 **持久化** 在会话的 JSONL 历史中。

## 配置

使用 `openclaw.json` 中的 `agents.defaults.compaction` 设置来配置压缩行为（模式、目标 tokens 等）。
压缩摘要默认保留不透明标识符 (`identifierPolicy: "strict"`)。你可以使用 `identifierPolicy: "off"` 覆盖此设置，或使用 `identifierPolicy: "custom"` 和 `identifierInstructions` 提供自定义文本。

## 自动压缩（默认开启）

当会话接近或超过模型的上下文窗口时，OpenClaw 会触发自动压缩，并可能使用压缩后的上下文重试原始请求。

你将看到：

- 详细模式下的 `🧹 Auto-compaction complete`
- 显示 `🧹 Compactions: <count>` 的 `/status`

在压缩之前，OpenClaw 可以运行一个 **静默内存刷新** 回合，将持久化笔记存储到磁盘。详见 [记忆](/concepts/memory) 了解详细信息和配置。

## 手动压缩

使用 `/compact`（可选带指令）来强制进行一轮压缩：

```
/compact Focus on decisions and open questions
```

## 上下文窗口来源

上下文窗口是模型特定的。OpenClaw 使用配置的提供商目录中的模型定义来确定限制。

## 压缩与修剪

- **压缩**：总结并 **持久化** 到 JSONL 中。
- **会话修剪**：仅修剪旧的 **工具结果**，**在内存中**，按请求进行。

参见 [/concepts/session-pruning](/concepts/session-pruning) 了解修剪详情。

## OpenAI 服务器端压缩

OpenClaw 还支持兼容的直接 OpenAI 模型的 OpenAI Responses 服务器端压缩提示。这与本地 OpenClaw 压缩分开，并且可以与其一起运行。

- 本地压缩：OpenClaw 总结并持久化到会话 JSONL 中。
- 服务器端压缩：当启用 `store` + `context_management` 时，OpenAI 在提供商侧压缩上下文。

参见 [OpenAI 提供商](/providers/openai) 了解模型参数和覆盖。

## 提示

- 当会话感觉过时或上下文膨胀时，使用 `/compact`。
- 大型工具输出已被截断；修剪可以进一步减少工具结果积累。
- 如果你需要全新的开始，`/new` 或 `/reset` 启动一个新的 session id。