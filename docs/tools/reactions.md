---
summary: "Reaction semantics shared across channels"
read_when:
  - Working on reactions in any channel
title: "Reactions"
---
# Reaction 工具

跨渠道共享的 reaction 语义：

- `emoji` 在添加 reaction 时是必需的。
- `emoji=""` 在支持的情况下会移除机器人的 reaction(s)。
- `remove: true` 在支持的情况下会移除指定的 emoji（需要 `emoji`）。

频道说明：

- **Discord/Slack**: 空的 `emoji` 移除消息上机器人的所有 reaction；`remove: true` 只移除该 emoji。
- **Google Chat**: 空的 `emoji` 移除消息上的应用 reaction；`remove: true` 只移除该 emoji。
- **Telegram**: 空的 `emoji` 移除机器人的 reaction；`remove: true` 也会移除 reaction，但仍然需要非空的 `emoji` 进行工具验证。
- **WhatsApp**: 空的 `emoji` 移除机器人 reaction；`remove: true` 映射为空 emoji（仍然需要 `emoji`）。
- **Signal**: 当启用 `channels.signal.reactionNotifications` 时，传入的 reaction 通知会触发系统事件。