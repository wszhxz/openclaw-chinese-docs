---
summary: "CLI reference for `openclaw channels` (accounts, status, login/logout, logs)"
read_when:
  - You want to add/remove channel accounts (WhatsApp/Telegram/Discord/Google Chat/Slack/Mattermost (plugin)/Signal/iMessage)
  - You want to check channel status or tail channel logs
title: "channels"
---
# `openclaw channels`

在网关上管理聊天通道账号及其运行时状态。

相关文档：

- 通道指南：[通道](/channels/index)  
- 网关配置：[配置](/gateway/configuration)

## 常用命令

```bash
openclaw channels list
openclaw channels status
openclaw channels capabilities
openclaw channels capabilities --channel discord --target channel:123
openclaw channels resolve --channel slack "#general" "@jane"
openclaw channels logs --channel all
```

## 添加 / 删除账号

```bash
openclaw channels add --channel telegram --token <bot-token>
openclaw channels remove --channel telegram --delete
```

提示：`openclaw channels add --help` 显示每个通道的标志（令牌、应用令牌、signal-cli 路径等）。

当您在不带任何标志的情况下运行 `openclaw channels add` 时，交互式向导将提示您输入以下信息：

- 所选通道对应的账号 ID  
- 这些账号的可选显示名称  
- `Bind configured channel accounts to agents now?`

若您确认立即绑定，向导将询问每个已配置通道账号应归属哪个代理，并写入作用于账号范围的路由绑定。

您之后也可使用 `openclaw agents bindings`、`openclaw agents bind` 和 `openclaw agents unbind`（参见 [agents](/cli/agents)）来管理相同的路由规则。

当您向一个仍使用单账号顶层设置（尚无 `channels.<channel>.accounts` 条目）的通道添加非默认账号时，OpenClaw 会将账号作用域内的单账号顶层值迁移至 `channels.<channel>.accounts.default`，然后写入新账号。此举可在转向多账号结构的同时，保持原始账号的行为不变。

路由行为保持一致：

- 已存在的仅通道级绑定（不含 `accountId`）将继续匹配默认账号。  
- `channels add` 在非交互模式下不会自动创建或重写绑定。  
- 交互式设置可选择性地添加账号作用域绑定。

如果您的配置已处于混合状态（存在命名账号、缺少 `default`，且顶层单账号值仍被设置），请运行 `openclaw doctor --fix`，将账号作用域值迁移至 `accounts.default`。

## 登录 / 注销（交互式）

```bash
openclaw channels login --channel whatsapp
openclaw channels logout --channel whatsapp
```

## 故障排查

- 运行 `openclaw status --deep` 进行广泛探测。  
- 使用 `openclaw doctor` 获取引导式修复建议。  
- `openclaw channels list` 输出 `Claude: HTTP 403 ... user:profile` → 使用快照需具备 `user:profile` 权限范围。请使用 `--no-usage`，或提供 claude.ai 会话密钥（`CLAUDE_WEB_SESSION_KEY` / `CLAUDE_WEB_COOKIE`），或通过 Claude Code CLI 重新认证。  
- 当网关不可达时，`openclaw channels status` 将退回到仅基于配置的摘要。若某受支持通道的凭据通过 SecretRef 配置，但在当前命令路径中不可用，则该账号将被报告为“已配置”，但附带降级说明，而非显示为“未配置”。

## 能力探测

获取提供商能力提示（在可用时包括意图/权限范围）以及静态功能支持：

```bash
openclaw channels capabilities
openclaw channels capabilities --channel discord --target channel:123
```

说明：

- `--channel` 为可选参数；省略该参数将列出所有通道（包括扩展通道）。  
- `--target` 接受 `channel:<id>` 或原始数字通道 ID，且仅适用于 Discord。  
- 探测具有提供商特异性：Discord 意图 + 可选通道权限；Slack 机器人 + 用户权限范围；Telegram 机器人标志 + Webhook；Signal 守护进程版本；Microsoft Teams 应用令牌 + Graph 角色/权限范围（在已知处标注）。不支持探测的通道将报告为 `Probe: unavailable`。

## 将名称解析为 ID

使用提供商目录将通道/用户名解析为 ID：

```bash
openclaw channels resolve --channel slack "#general" "@jane"
openclaw channels resolve --channel discord "My Server/#support" "@someone"
openclaw channels resolve --channel matrix "Project Room"
```

说明：

- 使用 `--kind user|group|auto` 强制指定目标类型。  
- 当多个条目共享相同名称时，解析优先选择活跃匹配项。  
- `channels resolve` 为只读操作。若所选账号通过 SecretRef 配置，但该凭据在当前命令路径中不可用，则命令将返回降级的未解析结果并附带说明，而不会中止整个执行流程。