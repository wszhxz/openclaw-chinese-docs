---
summary: "CLI reference for `openclaw directory` (self, peers, groups)"
read_when:
  - You want to look up contacts/groups/self ids for a channel
  - You are developing a channel directory adapter
title: "directory"
---
# `openclaw directory`

支持的频道目录查找（联系人/对等用户、群组和“我”）。

## 常用标志

- `--channel <name>`: 频道 id/别名（当配置了多个频道时为必需；仅配置一个时自动）
- `--account <id>`: 账户 id（默认：频道默认）
- `--json`: 输出 JSON

## 注意事项

- `directory` 的目的是帮助您找到可以粘贴到其他命令中的 ID（尤其是 `openclaw message send --target ...`）。
- 对于许多频道，结果是基于配置的（允许列表/配置的群组），而不是实时提供商目录。
- 默认输出是 `id`（有时是 `name`），以制表符分隔；使用 `--json` 进行脚本编写。

## 使用结果与 `message send`

```bash
openclaw directory peers list --channel slack --query "U0"
openclaw message send --channel slack --target user:U012ABCDEF --message "hello"
```

## ID 格式（按频道）

- WhatsApp: `+15551234567`（私信），`1234567890-1234567890@g.us`（群组）
- Telegram: `@username` 或数字聊天 id；群组是数字 id
- Slack: `user:U…` 和 `channel:C…`
- Discord: `user:<id>` 和 `channel:<id>`
- Matrix (插件): `user:@user:server`，`room:!roomId:server`，或 `#alias:server`
- Microsoft Teams (插件): `user:<id>` 和 `conversation:<id>`
- Zalo (插件): 用户 id（Bot API）
- Zalo 个人 / `zalouser` (插件): 线程 id（私信/群组）来自 `zca` (`me`，`friend list`，`group list`)

## 自身（“我”）

```bash
openclaw directory self --channel zalouser
```

## 对等用户（联系人/用户）

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