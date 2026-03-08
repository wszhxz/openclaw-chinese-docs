---
summary: "Poll sending via gateway + CLI"
read_when:
  - Adding or modifying poll support
  - Debugging poll sends from the CLI or gateway
title: "Polls"
---
# 投票

## 支持的渠道

- Telegram
- WhatsApp (web 渠道)
- Discord
- MS Teams (Adaptive Cards)

## CLI

```bash
# Telegram
openclaw message poll --channel telegram --target 123456789 \
  --poll-question "Ship it?" --poll-option "Yes" --poll-option "No"
openclaw message poll --channel telegram --target -1001234567890:topic:42 \
  --poll-question "Pick a time" --poll-option "10am" --poll-option "2pm" \
  --poll-duration-seconds 300

# WhatsApp
openclaw message poll --target +15555550123 \
  --poll-question "Lunch today?" --poll-option "Yes" --poll-option "No" --poll-option "Maybe"
openclaw message poll --target 123456789@g.us \
  --poll-question "Meeting time?" --poll-option "10am" --poll-option "2pm" --poll-option "4pm" --poll-multi

# Discord
openclaw message poll --channel discord --target channel:123456789 \
  --poll-question "Snack?" --poll-option "Pizza" --poll-option "Sushi"
openclaw message poll --channel discord --target channel:123456789 \
  --poll-question "Plan?" --poll-option "A" --poll-option "B" --poll-duration-hours 48

# MS Teams
openclaw message poll --channel msteams --target conversation:19:abc@thread.tacv2 \
  --poll-question "Lunch?" --poll-option "Pizza" --poll-option "Sushi"
```

选项：

- `--channel`: `whatsapp` (默认), `telegram`, `discord`, 或 `msteams`
- `--poll-multi`: 允许选择多个选项
- `--poll-duration-hours`: 仅 Discord（省略时默认为 24）
- `--poll-duration-seconds`: 仅 Telegram（5-600 秒）
- `--poll-anonymous` / `--poll-public`: 仅 Telegram 投票可见性

## Gateway RPC

方法：`poll`

参数：

- `to` (string, 必填)
- `question` (string, 必填)
- `options` (string[], 必填)
- `maxSelections` (number, 可选)
- `durationHours` (number, 可选)
- `durationSeconds` (number, 可选，仅 Telegram)
- `isAnonymous` (boolean, 可选，仅 Telegram)
- `channel` (string, 可选，默认：`whatsapp`)
- `idempotencyKey` (string, 必填)

## 渠道差异

- Telegram：2-10 个选项。支持通过 `threadId` 或 `:topic:` 目标使用论坛主题。使用 `durationSeconds` 而不是 `durationHours`，限制为 5-600 秒。支持匿名和公开投票。
- WhatsApp：2-12 个选项，`maxSelections` 必须在选项数量范围内，忽略 `durationHours`。
- Discord：2-10 个选项，`durationHours` 限制在 1-768 小时（默认 24）。`maxSelections > 1` 启用多选；Discord 不支持严格的选定数量。
- MS Teams：Adaptive Card 投票（OpenClaw 管理）。无原生投票 API；`durationHours` 被忽略。

## Agent 工具 (Message)

使用 `message` 工具配合 `poll` 动作 (`to`, `pollQuestion`, `pollOption`, 可选 `pollMulti`, `pollDurationHours`, `channel`)。

对于 Telegram，该工具还接受 `pollDurationSeconds`、`pollAnonymous` 和 `pollPublic`。

使用 `action: "poll"` 进行投票创建。通过 `action: "send"` 传递的投票字段将被拒绝。

注意：Discord 没有"pick exactly N"模式；`pollMulti` 映射为多选。
Teams 投票渲染为 Adaptive Cards，并要求网关保持在线
以在 `~/.openclaw/msteams-polls.json` 中记录投票。