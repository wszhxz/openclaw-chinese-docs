---
summary: "Reaction semantics shared across channels"
read_when:
  - Working on reactions in any channel
title: "Reactions"
---
# 反应工具

跨渠道共享的反应语义：

- 添加反应时需要 `emoji`。
- `emoji=""` 在支持的情况下会移除机器人的反应（如果有）。
- `remove: true` 在支持的情况下移除指定的 emoji（需要 `emoji`）。

渠道说明：

- **Discord/Slack**：空 `emoji` 会移除消息中所有机器人的反应；`remove: true` 仅移除该特定 emoji。
- **Google Chat**：空 `emoji` 会移除消息中应用的反应；`remove: true` 仅移除该特定 emoji。
- **Telegram**：空 `emoji` 会移除机器人的反应；`remove: true` 也会移除反应，但工具验证仍需要非空的 `emoji`。
- **WhatsApp**：空 `emoji` 会移除机器人的反应；`remove: true` 映射为空 emoji（仍需要 `emoji`）。
- **Signal**：当 `channels.signal.reactionNotifications` 启用时，入站反应通知会触发系统事件。