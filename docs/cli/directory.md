---
summary: "CLI reference for `openclaw directory` (self, peers, groups)"
read_when:
  - You want to look up contacts/groups/self ids for a channel
  - You are developing a channel directory adapter
title: "directory"
---
# `openclaw directory`

针对支持该功能的频道执行目录查找（联系人/对端、群组以及“我”）。

## 常用标志

- `--channel <name>`: 频道 ID / 别名（当配置了多个频道时为必需项；仅配置一个频道时自动填充）
- `--account <id>`: 账户 ID（默认值：频道默认值）
- `--json`: 以 JSON 格式输出

## 注意事项

- `directory` 旨在帮助您查找可粘贴到其他命令（尤其是 `openclaw message send --target ...`）中的 ID。
- 对于许多频道，结果基于配置（允许列表 / 已配置的群组），而非实时提供方目录。
- 默认输出为以制表符分隔的 `id`（有时还包括 `name`）；如需用于脚本，请使用 `--json`。

## 将结果与 `message send` 配合使用

```bash
openclaw directory peers list --channel slack --query "U0"
openclaw message send --channel slack --target user:U012ABCDEF --message "hello"
```

## ID 格式（按频道分类）

- WhatsApp：`+15551234567`（单聊）、`1234567890-1234567890@g.us`（群组）
- Telegram：`@username` 或数字聊天 ID；群组均为数字 ID
- Slack：`user:U…` 和 `channel:C…`
- Discord：`user:<id>` 和 `channel:<id>`
- Matrix（插件）：`user:@user:server`、`room:!roomId:server` 或 `#alias:server`
- Microsoft Teams（插件）：`user:<id>` 和 `conversation:<id>`
- Zalo（插件）：用户 ID（Bot API）
- Zalo 个人版 / `zalouser`（插件）：来自 `zca` 的会话 ID（单聊 / 群组）（`me`、`friend list`、`group list`）

## 自身（“我”）

```bash
openclaw directory self --channel zalouser
```

## 对端（联系人 / 用户）

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