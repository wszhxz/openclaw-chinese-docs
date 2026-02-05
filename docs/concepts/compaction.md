---
summary: "Context window + compaction: how OpenClaw keeps sessions under model limits"
read_when:
  - You want to understand auto-compaction and /compact
  - You are debugging long sessions hitting context limits
title: "Compaction"
---
# 上下文窗口与压缩

每个模型都有一个**上下文窗口**（可查看的最大令牌数）。长时间运行的聊天会累积消息和工具结果；一旦窗口变紧，OpenClaw 会**压缩**较旧的历史记录以保持在限制范围内。

## 压缩是什么

压缩会**总结较早的对话**并将其转换为紧凑的摘要条目，同时保持最近的消息完整。摘要存储在会话历史中，因此未来的请求会使用：

- 压缩摘要
- 压缩点之后的最近消息

压缩在会话的 JSONL 历史中**持久存在**。

## 配置

有关 `agents.defaults.compaction` 设置，请参见[压缩配置和模式](/concepts/compaction)。

## 自动压缩（默认开启）

当会话接近或超过模型的上下文窗口时，OpenClaw 会触发自动压缩，并可能使用压缩后的上下文重试原始请求。

您会看到：

- 在详细模式下的 `🧹 Auto-compaction complete`
- 显示 `🧹 Compactions: <count>` 的 `/status`

在压缩之前，OpenClaw 可以运行一个**静默内存刷新**回合，将持久笔记存储到磁盘。详情和配置请参见[内存](/concepts/memory)。

## 手动压缩

使用 `/compact`（可选择性地附带指令）来强制执行压缩操作：

```
/compact Focus on decisions and open questions
```

## 上下文窗口来源

上下文窗口是模型特定的。OpenClaw 使用来自配置提供程序目录中的模型定义来确定限制。

## 压缩与修剪

- **压缩**：总结并在 JSONL 中**持久保存**。
- **会话修剪**：仅修剪旧的**工具结果**，按请求在**内存中**进行。

修剪详情请参见 [/concepts/session-pruning](/concepts/session-pruning)。

## 提示

- 当会话感觉陈旧或上下文膨胀时，使用 `/compact`。
- 大型工具输出已经被截断；修剪可以进一步减少工具结果的积累。
- 如果需要全新的开始，`/new` 或 `/reset` 会启动一个新的会话 ID。