---
summary: "Reaction semantics shared across channels"
read_when:
  - Working on reactions in any channel
title: "Reactions"
---
# 反应工具

跨渠道共享的反应语义：

- `emoji` 在添加反应时是必需的。
- `emoji=""` 在支持的情况下移除机器人的反应。
- `remove: true` 在支持的情况下移除指定的表情符号（需要 `emoji`）。

渠道说明：

- **Discord/Slack**: 空的 `emoji` 会移除消息上所有机器人的反应；`remove: true` 仅移除该表情符号。
- **Google Chat**: 空的 `emoji` 会移除应用在消息上的反应；`remove: true` 仅移除该表情符号。
- **Telegram**: 空的 `emoji` 会移除机器人的反应；`remove: true` 也会移除反应，但仍然需要非空的 `emoji` 以进行工具验证。
- **WhatsApp**: 空的 `emoji` 会移除机器人的反应；`remove: true` 映射到空表情符号（仍然需要 `emoji`）。
- **Zalo Personal (`zalouser`)**: 需要非空的 `emoji`；`remove: true` 会移除特定的表情符号反应。
- **Signal**: 当启用 `channels.signal.reactionNotifications` 时，传入的反应通知会发出系统事件。