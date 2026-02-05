---
summary: "When OpenClaw shows typing indicators and how to tune them"
read_when:
  - Changing typing indicator behavior or defaults
title: "Typing Indicators"
---
# 输入指示器

输入指示器在运行期间发送到聊天频道。使用 `agents.defaults.typingMode` 来控制**何时**开始输入，使用 `typingIntervalSeconds` 来控制**刷新频率**。

## 默认设置

当 `agents.defaults.typingMode` 未设置时，OpenClaw 保持旧的行为：

- **直接聊天**：模型循环开始后立即开始输入。
- **带有提及的群组聊天**：立即开始输入。
- **不带提及的群组聊天**：仅在消息文本开始流式传输时才开始输入。
- **心跳运行**：禁用输入。

## 模式

将 `agents.defaults.typingMode` 设置为以下之一：

- `never` — 从不显示输入指示器。
- `instant` — 一旦模型循环开始就立即开始输入，即使运行最终只返回静默回复令牌。
- `thinking` — 在**第一个推理增量**时开始输入（需要运行中的 `reasoningLevel: "stream"`）。
- `message` — 在**第一个非静默文本增量**时开始输入（忽略 `NO_REPLY` 静默令牌）。

“触发时机”的顺序：
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

您可以按会话覆盖模式或频率：

```json5
{
  session: {
    typingMode: "message",
    typingIntervalSeconds: 4,
  },
}
```

## 注意事项

- `message` 模式不会为仅静默回复显示输入（例如用于抑制输出的 `NO_REPLY` 令牌）。
- `thinking` 仅在运行流式传输推理时触发 (`reasoningLevel: "stream"`)。
  如果模型没有发出推理增量，则不会开始输入。
- 心跳从不显示输入，无论模式如何。
- `typingIntervalSeconds` 控制**刷新频率**，而不是开始时间。
  默认值为6秒。