---
summary: "Context window + compaction: how OpenClaw keeps sessions under model limits"
read_when:
  - You want to understand auto-compaction and /compact
  - You are debugging long sessions hitting context limits
title: "Compaction"
---
# 上下文窗口与压缩

每个模型都有一个**上下文窗口**（它能看到的最大令牌数）。长时间的对话会累积消息和工具结果；当窗口接近限制时，OpenClaw 会**压缩**较旧的历史记录以保持在限制范围内。

## 压缩是什么

压缩会将较旧的对话**总结为一个紧凑的摘要条目**，并保留最近的消息。摘要会存储在会话历史记录中，因此未来的请求将使用：

- 压缩后的摘要
- 压缩点之后的最近消息

压缩会**持久化**在会话的 JSONL 历史记录中。

## 配置

查看 [压缩配置与模式](/concepts/compaction) 了解 `agents.defaults.compaction` 设置。

## 自动压缩（默认开启）

当会话接近或超过模型的上下文窗口时，OpenClaw 会触发自动压缩，并可能使用压缩后的上下文重新尝试原始请求。

你将看到：

- 在详细模式下显示 `🧹 自动压缩完成`
- `/status` 显示 `🧹 压缩次数: <count>`

在压缩之前，OpenClaw 可以运行一次**静默内存刷新**，以将持久化笔记存储到磁盘。有关详细信息和配置，请参阅 [内存](/concepts/memory)。

## 手动压缩

使用 `/compact`（可选地附带指令）强制执行一次压缩：

```
/compact 聚焦于决策和开放性问题
```

## 上下文窗口来源

上下文窗口是模型特定的。OpenClaw 会使用配置的提供商目录中的模型定义来确定限制。

## 压缩 vs 剪枝

- **压缩**：总结并**持久化**在 JSONL 中。
- **会话剪枝**：仅**修剪内存中**的旧工具结果，按请求进行。

有关剪枝的详细信息，请参阅 [/concepts/session-pruning](/concepts/session-pruning)。

## 提示

- 当会话感觉过时或上下文臃肿时，使用 `/compact`。
- 大型工具输出已截断；剪枝可以进一步减少工具结果的累积。
- 如果你需要一个全新的开始，`/new` 或 `/reset` 会启动一个新的会话 ID。