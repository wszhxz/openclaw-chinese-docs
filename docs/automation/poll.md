---
summary: "Poll sending via gateway + CLI"
read_when:
  - Adding or modifying poll support
  - Debugging poll sends from the CLI or gateway
title: "Polls"
---
# 投票

## 支持的渠道

- WhatsApp (网页渠道)
- Discord
- MS Teams (自适应卡片)

## 命令行界面

```bash
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

选项:

- `--channel`: `whatsapp` (默认), `discord`, 或 `msteams`
- `--poll-multi`: 允许多选
- `--poll-duration-hours`: 仅限Discord（省略时默认为24）

## 网关RPC

方法: `poll`

参数:

- `to` (字符串, 必需)
- `question` (字符串, 必需)
- `options` (字符串数组, 必需)
- `maxSelections` (数字, 可选)
- `durationHours` (数字, 可选)
- `channel` (字符串, 可选, 默认: `whatsapp`)
- `idempotencyKey` (字符串, 必需)

## 渠道差异

- WhatsApp: 2-12个选项, `maxSelections` 必须在选项数量范围内, 忽略 `durationHours`。
- Discord: 2-10个选项, `durationHours` 限制在1-768小时之间 (默认24)。`maxSelections > 1` 启用多选; Discord不支持严格的选项计数。
- MS Teams: 自适应卡片投票 (由OpenClaw管理)。没有原生投票API; `durationHours` 被忽略。

## 代理工具 (消息)

使用 `message` 工具与 `poll` 操作 (`to`, `pollQuestion`, `pollOption`, 可选 `pollMulti`, `pollDurationHours`, `channel`)。

注意: Discord没有“精确选择N个”模式; `pollMulti` 映射到多选。
Teams投票以自适应卡片形式呈现，并需要网关保持在线以记录 `~/.openclaw/msteams-polls.json` 中的投票。