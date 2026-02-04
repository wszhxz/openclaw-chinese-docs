---

summary: "CLI reference for `openclaw channels` (accounts, status, login/logout, logs)"
read_when:
  - You want to add/remove channel accounts (WhatsApp/Telegram/Discord/Google Chat/Slack/Mattermost (plugin)/Signal/iMessage)
  - You want to check channel status or tail channel logs
title: "channels"

---
# `openclaw channels`

管理网关上的聊天频道账户及其运行时状态。

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

## 添加/移除账户

```bash
openclaw channels add --channel telegram --token <bot-token>
openclaw channels remove --channel telegram --delete
```

提示：`openclaw channels add --help` 显示每个频道的标志（令牌、应用令牌、signal-cli路径等）。

## 登录/登出（交互式）

```bash
openclaw channels login --channel whatsapp
openclaw channels logout --channel whatsapp
```

## 故障排除

- 运行 `openclaw status --deep` 进行广泛探测。
- 使用 `openclaw doctor` 进行引导式修复。
- `openclaw channels list` 会打印 `Claude: HTTP 403 ... user:profile` → 使用快照需要 `user:profile` 权限范围。使用 `--no-usage`, 或提供 claude.ai 会话密钥（`CLAUDE_WEB_SESSION_KEY` / `CLAUDE_WEB_COOKIE`），或通过 Claude Code CLI 重新认证。

## 能力探测

获取提供者能力提示（可用的意图/权限）和静态功能支持：

```bash
openclaw channels capabilities
openclaw channels capabilities --channel discord --target channel:123
```

说明：

- `--channel` 是可选的；省略它将列出所有频道（包括扩展）。
- `--target` 接受 `channel:<id>` 或原始数字频道ID，且仅适用于 Discord。
- 探测是提供者特定的：Discord 意图 + 可选频道权限；Slack 机器人 + 用户权限；Telegram 机器人标志 + Webhook；Signal 守护进程版本；MS Teams 应用令牌 + Graph 角色/权限（已知位置会注释）。没有探测的频道会报告 `Probe: unavailable`。

## 解析名称到ID

使用提供者目录将频道/用户名称解析为ID：

```bash
openclaw channels resolve --channel slack "#general" "@jane"
openclaw channels resolve --channel discord "My Server/#support" "@someone"
openclaw channels resolve --channel matrix "Project Room"
```

说明：

- 使用 `--kind user|group|auto` 强制指定目标类型。
- 解析时在多个条目共享相同名称的情况下，优先选择活跃匹配。