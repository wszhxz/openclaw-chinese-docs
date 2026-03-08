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

## 添加 / 移除账户

```bash
openclaw channels add --channel telegram --token <bot-token>
openclaw channels remove --channel telegram --delete
```

提示：`openclaw channels add --help` 显示每个频道的 flags（token、app token、signal-cli 路径等）。

当你在不带 flags 的情况下运行 `openclaw channels add` 时，交互式向导可能会提示：

- 每个选定频道的账户 id
- 这些账户的可选显示名称
- `Bind configured channel accounts to agents now?`

如果你确认现在绑定，向导会询问哪个代理应该拥有每个已配置的频道账户，并写入账户范围的路由绑定。

你也可以稍后使用 `openclaw agents bindings`、`openclaw agents bind` 和 `openclaw agents unbind` 管理相同的路由规则（参见 [agents](/cli/agents)）。

当你向仍在使用单账户顶层设置（尚无 `channels.<channel>.accounts` 条目）的频道添加非默认账户时，OpenClaw 会将账户范围的单账户顶层值移动到 `channels.<channel>.accounts.default`，然后写入新账户。这在切换到多账户结构的同时保留了原始账户行为。

路由行为保持一致：

- 现有的仅频道绑定（无 `accountId`）继续匹配默认账户。
- `channels add` 在非交互模式下不会自动创建或重写绑定。
- 交互式设置可以选择性地添加账户范围的绑定。

如果你的配置已经处于混合状态（存在命名账户，缺少 `default`，且仍设置了顶层单账户值），运行 `openclaw doctor --fix` 将账户范围的值移动到 `accounts.default`。

## 登录 / 注销（交互式）

```bash
openclaw channels login --channel whatsapp
openclaw channels logout --channel whatsapp
```

## 故障排除

- 运行 `openclaw status --deep` 进行广泛探测。
- 使用 `openclaw doctor` 进行引导式修复。
- `openclaw channels list` 打印 `Claude: HTTP 403 ... user:profile` → 使用快照需要 `user:profile` scope。使用 `--no-usage`，或提供 claude.ai 会话密钥（`CLAUDE_WEB_SESSION_KEY` / `CLAUDE_WEB_COOKIE`），或通过 Claude Code CLI 重新认证。
- 当网关不可达时，`openclaw channels status` 会回退到仅配置摘要。如果支持的频道凭证是通过 SecretRef 配置的但在当前命令路径中不可用，它会将该账户报告为已配置但带有降级说明，而不是显示为未配置。

## 能力探测

获取提供者能力提示（可用的 intents/scopes）以及静态功能支持：

```bash
openclaw channels capabilities
openclaw channels capabilities --channel discord --target channel:123
```

注意：

- `--channel` 是可选的；省略它以列出每个频道（包括扩展）。
- `--target` 接受 `channel:<id>` 或原始数字频道 id，仅适用于 Discord。
- 探测是提供者特定的：Discord intents + 可选频道权限；Slack bot + user scopes；Telegram bot flags + webhook；Signal daemon 版本；MS Teams app token + Graph roles/scopes（已知处已标注）。没有探测的频道报告 `Probe: unavailable`。

## 将名称解析为 ID

使用提供者目录将频道/用户名称解析为 ID：

```bash
openclaw channels resolve --channel slack "#general" "@jane"
openclaw channels resolve --channel discord "My Server/#support" "@someone"
openclaw channels resolve --channel matrix "Project Room"
```

注意：

- 使用 `--kind user|group|auto` 强制目标类型。
- 当多个条目共享相同名称时，解析优先选择活跃匹配项。
- `channels resolve` 是只读的。如果选定的账户是通过 SecretRef 配置的但该凭证在当前命令路径中不可用，命令将返回带有说明的降级未解析结果，而不是中止整个运行。