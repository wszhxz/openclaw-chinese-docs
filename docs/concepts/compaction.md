---
summary: "Context window + compaction: how OpenClaw keeps sessions under model limits"
read_when:
  - You want to understand auto-compaction and /compact
  - You are debugging long sessions hitting context limits
title: "Compaction"
---
# 上下文窗口与压缩

每个模型都有一个**上下文窗口**（它可以处理的最大标记数）。长时间的对话会积累消息和工具结果；一旦窗口接近满载，OpenClaw会**压缩**较早的历史记录以保持在限制范围内。

## 什么是压缩

压缩会将**较早的对话**总结成一个紧凑的摘要条目，并保持最近的消息不变。摘要存储在会话历史中，因此未来的请求会使用：

- 压缩摘要
- 压缩点之后的最近消息

压缩会在会话的JSONL历史中**持久化**。

## 配置

有关`agents.defaults.compaction`设置，请参阅[压缩配置与模式](/concepts/compaction)。

## 自动压缩（默认开启）

当会话接近或超过模型的上下文窗口时，OpenClaw会触发自动压缩，并可能使用压缩后的上下文重试原始请求。

你会看到：

- 在详细模式下的`🧹 Auto-compaction complete`
- 显示`🧹 Compactions: <count>`的`/status`

在压缩之前，OpenClaw可以运行一个**静默内存刷新**轮次，将持久性笔记存储到磁盘。有关详细信息和配置，请参阅[内存](/concepts/memory)。

## 手动压缩

使用`/compact`（可选带指令）强制进行一次压缩操作：

```
/compact Focus on decisions and open questions
```

## 上下文窗口来源

上下文窗口是特定于模型的。OpenClaw使用配置提供商目录中的模型定义来确定限制。

## 压缩与修剪

- **压缩**：总结并**持久化**到JSONL。
- **会话修剪**：仅修剪旧的**工具结果**，**内存中**，按请求进行。

有关修剪的详细信息，请参阅[/concepts/session-pruning](/concepts/session-pruning)。

## 提示

- 当会话感觉陈旧或上下文膨胀时，使用`/compact`。
- 大型工具输出已经截断；修剪可以进一步减少工具结果的累积。
- 如果需要一个新的起点，`/new`或`/reset`会启动一个新的会话ID。