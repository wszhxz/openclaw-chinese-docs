---
summary: "CLI reference for `openclaw directory` (self, peers, groups)"
read_when:
  - You want to look up contacts/groups/self ids for a channel
  - You are developing a channel directory adapter
title: "directory"
---
# `openclaw directory`

支持该功能的频道目录查找（联系人/对等方、群组和“我”）。

## 通用参数

- `--channel <name>`: 频道 ID/别名（配置多个频道时为必填项；仅配置一个时自动识别）
- `--account <id>`: 账户 ID（默认值：频道默认值）
- `--json`: 输出 JSON

## 说明

- `directory` 旨在帮助您查找可粘贴到其他命令中的 ID（尤其是 `openclaw message send --target ...`）。
- 对于许多频道，结果基于配置（允许列表/配置的组），而非实时提供者目录。
- 默认输出为 `id`（有时为 `name`），以制表符分隔；脚本处理请使用 `--json`。

## 在 `message send` 中使用结果

```bash
openclaw directory peers list --channel slack --query "U0"
openclaw message send --channel slack --target user:U012ABCDEF --message "hello"
```

## ID 格式（按频道）

- WhatsApp: `+15551234567` (DM), `1234567890-1234567890@g.us` (群组)
- Telegram: `@username` 或数字聊天 ID；群组为数字 ID
- Slack: `user:U…` 和 `channel:C…`
- Discord: `user:<id>` 和 `channel:<id>`
- Matrix (插件): `user:@user:server`, `room:!roomId:server` 或 `#alias:server`
- Microsoft Teams (插件): `user:<id>` 和 `conversation:<id>`
- Zalo (插件): 用户 ID (Bot API)
- Zalo Personal / `zalouser` (插件): 线程 ID (DM/群组)，来自 `zca` (`me`, `friend list`, `group list`)

## 自身 ("我")

```bash
openclaw directory self --channel zalouser
```

## 对等方 (联系人/用户)

```bash
openclaw directory peers list --channel zalouser
openclaw directory peers list --channel zalouser --query "name"
openclaw directory peers list --channel zalouser --limit 50
```

## 群组

```bash
openclaw directory groups list --channel zalouser
openclaw directory groups list --channel zalouser --query "work"
openclaw directory groups members --channel zalouser --group-id <id>
```