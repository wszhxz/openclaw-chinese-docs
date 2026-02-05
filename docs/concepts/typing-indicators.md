---
summary: "When OpenClaw shows typing indicators and how to tune them"
read_when:
  - Changing typing indicator behavior or defaults
title: "Typing Indicators"
---
# 打字指示器

在运行期间，打字指示器会发送到聊天频道。使用
`agents.defaults.typingMode` 来控制打字**何时**开始，使用 `typingIntervalSeconds`
来控制其刷新**频率**。

## 默认行为

当 `agents.defaults.typingMode` **未设置**时，OpenClaw 保持传统行为：

- **直接聊天**：一旦模型循环开始，打字立即开始。
- **带有提及的群聊**：打字立即开始。
- **没有提及的群聊**：仅当消息文本开始流式传输时才开始打字。
- **心跳运行**：禁用打字。

## 模式

将 `agents.defaults.typingMode` 设置为以下之一：

- `never` — 永远不显示打字指示器。
- `instant` — 在模型循环**开始时立即**开始打字，即使运行
  后来只返回静默回复标记。
- `thinking` — 在**第一个推理增量**时开始打字（需要
  运行中的 `reasoningLevel: "stream"`）。
- `message` — 在**第一个非静默文本增量**时开始打字（忽略
  `NO_REPLY` 静默标记）。

"触发时间早晚"的顺序：
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

您可以覆盖每个会话的模式或节拍：

```json5
{
  session: {
    typingMode: "message",
    typingIntervalSeconds: 4,
  },
}
```

## 注意事项

- `message` 模式不会为仅静默回复显示打字（例如用于抑制输出的 `NO_REPLY`
  标记）。
- `thinking` 仅在运行流式推理时触发（`reasoningLevel: "stream"`）。
  如果模型不发出推理增量，则不会开始打字。
- 心跳从不显示打字，无论模式如何。
- `typingIntervalSeconds` 控制**刷新节拍**，而不是开始时间。
  默认值为 6 秒。