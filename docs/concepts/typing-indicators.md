---
summary: "When OpenClaw shows typing indicators and how to tune them"
read_when:
  - Changing typing indicator behavior or defaults
title: "Typing Indicators"
---
# 输入状态指示

在运行过程中，输入状态指示会发送到聊天频道。使用 `agents.defaults.typingMode` 来控制**何时**开始输入状态，使用 `typingIntervalSeconds` 来控制**多久刷新一次**。

## 默认行为

当 `agents.defaults.typingMode` 未设置时，OpenClaw 保持传统行为：

- **直接聊天**：模型循环开始时立即开始输入状态。
- **提及的群聊**：立即开始输入状态。
- **未提及的群聊**：仅在消息文本开始流式传输时才开始输入状态。
- **心跳运行**：禁用输入状态。

## 模式

将 `agents.defaults.typingMode` 设置为以下之一：

- `never` — 永不显示输入状态。
- `instant` — 模型循环开始时**立即**开始输入状态，即使后续仅返回静默回复标记。
- `thinking` — 在**第一个推理增量**时开始输入状态（需要运行的 `reasoningLevel: "stream"`）。
- `message` — 在**第一个非静默文本增量**时开始输入状态（忽略 `NO_REPLY` 静默标记）。

输入状态触发的“早起顺序”：
`never` → `message` → `thinking` → `instant`

## 配置

```json5
{
  agent: {
    typingMode: "thinking",
    typingIntervalSeconds: 6,
  },
}
```

你可以在每个会话中覆盖模式或刷新频率：

```json5
{
  session: {
    typingMode: "message",
    typingIntervalSeconds: 4,
  },
}
```

## 说明

- `message` 模式不会在仅静默回复（例如 `NO_REPLY` 标记用于抑制输出）时显示输入状态。
- `thinking` 仅在运行流式传输推理（`reasoningLevel: "stream"`）时触发。如果模型未发出推理增量，输入状态不会开始。
- 无论模式如何，心跳运行都不会显示输入状态。
- `typingIntervalSeconds` 控制的是**刷新频率**，而不是开始时间。默认值为 6 秒。