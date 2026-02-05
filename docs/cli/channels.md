---
summary: "CLI reference for `openclaw channels` (accounts, status, login/logout, logs)"
read_when:
  - You want to add/remove channel accounts (WhatsApp/Telegram/Discord/Google Chat/Slack/Mattermost (plugin)/Signal/iMessage)
  - You want to check channel status or tail channel logs
title: "channels"
---
# `openclaw channels`

在网关上管理聊天频道账户及其运行状态。

相关文档：

- 频道指南：[Channels](/channels/index)
- 网关配置：[Configuration](/gateway/configuration)

## 常用命令

```bash
openclaw channels list
openclaw channels status
openclaw channels capabilities
openclaw channels capabilities --channel discord --target channel:123
openclaw channels resolve --channel slack "#general" "@jane"
openclaw channels logs --channel all
```

## 添加/删除账户

```bash
openclaw channels add --channel telegram --token <bot-token>
openclaw channels remove --channel telegram --delete
```

提示：`openclaw channels add --help` 显示每个频道的标志（令牌、应用令牌、signal-cli 路径等）。

## 登录/登出（交互式）

```bash
openclaw channels login --channel whatsapp
openclaw channels logout --channel whatsapp
```

## 故障排除

- 运行 `openclaw status --deep` 进行广泛的探测。
- 使用 `openclaw doctor` 进行引导修复。
- `openclaw channels list` 打印 `Claude: HTTP 403 ... user:profile` → 使用情况快照需要 `user:profile` 范围。使用 `--no-usage`，或提供 claude.ai 会话密钥 (`CLAUDE_WEB_SESSION_KEY` / `CLAUDE_WEB_COOKIE`)，或通过 Claude Code CLI 重新认证。

## 功能探测

获取提供商功能提示（可用时的意图/范围）以及静态功能支持：

```bash
openclaw channels capabilities
openclaw channels capabilities --channel discord --target channel:123
```

说明：

- `--channel` 是可选的；省略它以列出每个频道（包括扩展）。
- `--target` 接受 `channel:<id>` 或原始数字频道 ID 并仅适用于 Discord。
- 探测是特定于提供商的：Discord 意图 + 可选频道权限；Slack 机器人 + 用户范围；Telegram 机器人标志 + 网络钩子；Signal 守护进程版本；MS Teams 应用令牌 + Graph 角色/范围（已知时标注）。没有探测的频道报告 `Probe: unavailable`。

## 解析名称为 ID

使用提供商目录解析频道/用户名称为 ID：

```bash
openclaw channels resolve --channel slack "#general" "@jane"
openclaw channels resolve --channel discord "My Server/#support" "@someone"
openclaw channels resolve --channel matrix "Project Room"
```

说明：

- 使用 `--kind user|group|auto` 强制目标类型。
- 解析优先选择多个条目共享相同名称时的活动匹配。