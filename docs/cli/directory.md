---
summary: "CLI reference for `openclaw directory` (self, peers, groups)"
read_when:
  - You want to look up contacts/groups/self ids for a channel
  - You are developing a channel directory adapter
title: "directory"
---
# `openclaw 目录`

支持该功能的频道（联系人/对等节点、群组和“我”）的目录查找。

## 常用标志

- `--channel <名称>`: 频道 ID/别名（当配置了多个频道时为必填项；仅配置一个时自动识别）
- `--account <ID>`: 账户 ID（默认：频道默认值）
- `--json`: 输出 JSON 格式

## 说明

- `directory` 的目的是帮助您找到可以粘贴到其他命令中的 ID（尤其是 `openclaw message send --target ...`）。
- 对于许多频道，结果是基于配置的（允许列表/配置的群组），而不是实时提供者目录。
- 默认输出为 `id`（有时也包括 `name`）用制表符分隔；使用 `--json` 用于脚本操作。

## 使用 `message send` 命令

```bash
openclaw directory peers list --channel slack --query "U0"
openclaw message send --channel slack --target user:U012ABCDEF --message "hello"
```

## ID 格式（按频道）

- WhatsApp: `+15551234567`（单聊），`1234567890-1234567890@g.us`（群组）
- Telegram: `@username` 或数字聊天 ID；群组为数字 ID
- Slack: `user:U…` 和 `channel:C…`
- Discord: `user:<id>` 和 `channel:<id>`
- Matrix（插件）: `user:@user:server`，`room:!roomId:server`，或 `#alias:server`
- Microsoft Teams（插件）: `user:<id>` 和 `conversation:<id>`
- Zalo（插件）: 用户 ID（Bot API）
- Zalo 个人 / `zalouser`（插件）: 从 `zca` 获取的线程 ID（单聊/群组）（`me`，`friend list`，`group list`）

## 自身（“我”）

```bash
openclaw directory self --channel zalouser
```

## 对等节点（联系人/用户）

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