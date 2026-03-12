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
- WhatsApp（网页渠道）
- Discord
- MS Teams（自适应卡片）

## 命令行界面（CLI）

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

- `--channel`: `whatsapp`（默认值）、`telegram`、`discord` 或 `msteams`
- `--poll-multi`: 允许选择多个选项
- `--poll-duration-hours`: 仅限 Discord（省略时默认为 24）
- `--poll-duration-seconds`: 仅限 Telegram（5–600 秒）
- `--poll-anonymous` / `--poll-public`: 仅限 Telegram 的投票可见性设置

## 网关 RPC

方法：`poll`

参数：

- `to`（字符串，必需）
- `question`（字符串，必需）
- `options`（字符串数组，必需）
- `maxSelections`（数字，可选）
- `durationHours`（数字，可选）
- `durationSeconds`（数字，可选，仅限 Telegram）
- `isAnonymous`（布尔值，可选，仅限 Telegram）
- `channel`（字符串，可选，默认值：`whatsapp`）
- `idempotencyKey`（字符串，必需）

## 各渠道差异

- Telegram：支持 2–10 个选项。可通过 `threadId` 或 `:topic:` 目标支持论坛主题。使用 `durationSeconds` 而非 `durationHours`，时限限制为 5–600 秒。支持匿名投票与公开投票。
- WhatsApp：支持 2–12 个选项，`maxSelections` 必须在选项总数范围内，忽略 `durationHours`。
- Discord：支持 2–10 个选项，`durationHours` 被限制在 1–768 小时之间（默认为 24）。启用 `maxSelections > 1` 可实现多选；Discord 不支持严格限定选择数量的模式。
- MS Teams：采用自适应卡片形式的投票（由 OpenClaw 管理）。无原生投票 API；`durationHours` 将被忽略。

## Agent 工具（消息）

使用 `message` 工具配合 `poll` 动作（`to`、`pollQuestion`、`pollOption`，可选 `pollMulti`、`pollDurationHours`、`channel`）。

对于 Telegram，该工具还接受 `pollDurationSeconds`、`pollAnonymous` 和 `pollPublic`。

使用 `action: "poll"` 创建投票。通过 `action: "send"` 传递的投票字段将被拒绝。

注意：Discord 不支持“精确选择 N 项”的模式；`pollMulti` 映射为多选模式。  
Teams 投票以自适应卡片形式渲染，且网关需保持在线状态，以便在 `~/.openclaw/msteams-polls.json` 中记录投票。