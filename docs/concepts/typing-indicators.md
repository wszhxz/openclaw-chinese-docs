---
summary: "When OpenClaw shows typing indicators and how to tune them"
read_when:
  - Changing typing indicator behavior or defaults
title: "Typing Indicators"
---
# 输入提示符

在运行过程中，输入提示符会发送到聊天频道。使用 `agents.defaults.typingMode` 控制**何时**开始显示输入提示，使用 `typingIntervalSeconds` 控制**刷新频率**。

## 默认行为

当 `agents.defaults.typingMode` **未设置**时，OpenClaw 保持原有行为：

- **单聊**：模型循环一开始即立即显示输入提示。
- **带提及的群聊**：立即显示输入提示。
- **不带提及的群聊**：仅当消息文本开始流式传输时才显示输入提示。
- **心跳运行（heartbeat runs）**：禁用输入提示。

## 模式

将 `agents.defaults.typingMode` 设置为以下值之一：

- `never` — 永远不显示输入提示。
- `instant` — **模型循环一开始即立即显示输入提示**，即使该运行后续仅返回静默回复标记（silent reply token）。
- `thinking` — 在**首个推理增量（reasoning delta）**时开始显示输入提示（该运行需启用 `reasoningLevel: "stream"`）。
- `message` — 在**首个非静默文本增量（non-silent text delta）**时开始显示输入提示（忽略 `NO_REPLY` 静默标记）。

按“触发时机早到晚”排序：
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

您可针对每个会话单独覆盖模式或刷新频率：

```json5
{
  session: {
    typingMode: "message",
    typingIntervalSeconds: 4,
  },
}
```

## 注意事项

- 在 `message` 模式下，纯静默回复（例如用于抑制输出的 `NO_REPLY` 标记）不会显示输入提示。
- `thinking` 仅在运行流式输出推理内容（`reasoningLevel: "stream"`）时触发。若模型未输出推理增量，则不会开始显示输入提示。
- 心跳运行（heartbeats）无论设置为何种模式，均永不显示输入提示。
- `typingIntervalSeconds` 控制的是**刷新频率**，而非起始时间。默认值为 6 秒。