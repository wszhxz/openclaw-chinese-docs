---
summary: "CLI reference for `openclaw channels` (accounts, status, login/logout, logs)"
read_when:
  - You want to add/remove channel accounts (WhatsApp/Telegram/Discord/Google Chat/Slack/Mattermost (plugin)/Signal/iMessage/Matrix)
  - You want to check channel status or tail channel logs
title: "channels"
---
# `openclaw channels`

在网关上管理聊天频道账户及其运行时状态。

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

## 状态 / 功能 / 解析 / 日志

- `channels status`: `--probe`, `--timeout <ms>`, `--json`
- `channels capabilities`: `--channel <name>`, `--account <id>` (仅配合 `--channel` 使用), `--target <dest>`, `--timeout <ms>`, `--json`
- `channels resolve`: `<entries...>`, `--channel <name>`, `--account <id>`, `--kind <auto|user|group>`, `--json`
- `channels logs`: `--channel <name|all>`, `--lines <n>`, `--json`

`channels status --probe` 是实时路径：在可访问的网关上，它按账户运行
`probeAccount` 和可选的 `auditAccount` 检查，因此输出可以包含传输
状态以及探测结果，例如 `works`, `probe failed`, `audit ok` 或 `audit failed`。
如果网关无法访问，`channels status` 回退到仅配置的摘要
而不是实时探测输出。

## 添加 / 删除账户

```bash
openclaw channels add --channel telegram --token <bot-token>
openclaw channels add --channel nostr --private-key "$NOSTR_PRIVATE_KEY"
openclaw channels remove --channel telegram --delete
```

提示：`openclaw channels add --help` 显示每个频道的标志（令牌、私钥、应用令牌、signal-cli 路径等）。

常见的非交互式添加方式包括：

- bot-token 频道：`--token`, `--bot-token`, `--app-token`, `--token-file`
- Signal/iMessage 传输字段：`--signal-number`, `--cli-path`, `--http-url`, `--http-host`, `--http-port`, `--db-path`, `--service`, `--region`
- Google Chat 字段：`--webhook-path`, `--webhook-url`, `--audience-type`, `--audience`
- Matrix 字段：`--homeserver`, `--user-id`, `--access-token`, `--password`, `--device-name`, `--initial-sync-limit`
- Nostr 字段：`--private-key`, `--relay-urls`
- Tlon 字段：`--ship`, `--url`, `--code`, `--group-channels`, `--dm-allowlist`, `--auto-discover-channels`
- `--use-env` 用于受支持时的默认账户基于环境的认证

当不带标志运行 `openclaw channels add` 时，交互式向导可能会提示：

- 每个选定频道的账户 ID
- 这些账户的可选显示名称
- `Bind configured channel accounts to agents now?`

如果您确认立即绑定，向导会询问哪个代理应拥有每个配置的频道账户，并写入账户范围的路由绑定。

您也可以稍后使用 `openclaw agents bindings`, `openclaw agents bind` 和 `openclaw agents unbind` 管理相同的路由规则（参见 [agents](/cli/agents)）。

当您向仍使用单账户顶层设置的频道添加非默认账户时，OpenClaw 会在写入新账户之前将账户范围的顶层值提升到频道的账户映射中。大多数频道将这些值置于 `channels.<channel>.accounts.default`，但捆绑频道可以选择保留现有的匹配提升账户。
Matrix 是当前的示例：如果已存在一个命名账户，或者 `defaultAccount` 指向一个现有的命名账户，则提升操作会保留该账户，而不是创建新的 `accounts.default`。

路由行为保持一致：

- 现有的仅频道绑定（无 `accountId`）继续匹配默认账户。
- `channels add` 在非交互模式下不会自动创建或重写绑定。
- 交互式设置可以选择性地添加账户范围绑定。

如果您的配置已经处于混合状态（存在命名账户且顶层单账户值仍然设置），请运行 `openclaw doctor --fix` 将账户范围的值移动到为该频道选择的提升账户中。大多数频道提升到 `accounts.default`；Matrix 可以选择保留现有的命名/默认目标。

## 登录 / 登出（交互）

```bash
openclaw channels login --channel whatsapp
openclaw channels logout --channel whatsapp
```

注意：

- `channels login` 支持 `--verbose`。
- `channels login` / `logout` 在仅配置了一个支持的登录目标时可以推断频道。

## 故障排除

- 运行 `openclaw status --deep` 进行广泛探测。
- 使用 `openclaw doctor` 进行引导修复。
- `openclaw channels list` 打印 `Claude: HTTP 403 ... user:profile` → 用法快照需要 `user:profile` 范围。请使用 `--no-usage`，或提供 claude.ai 会话密钥（`CLAUDE_WEB_SESSION_KEY` / `CLAUDE_WEB_COOKIE`），或通过 Claude CLI 重新认证。
- 当网关无法访问时，`openclaw channels status` 回退到仅配置的摘要。如果通过 SecretRef 配置了支持的频道凭据但在当前命令路径中不可用，它将报告该账户为已配置但带有降级说明，而不是显示为未配置。

## 功能探测

获取提供商功能提示（可用时的意图/范围）以及静态功能支持：

```bash
openclaw channels capabilities
openclaw channels capabilities --channel discord --target channel:123
```

注意：

- `--channel` 是可选的；省略它以列出所有频道（包括扩展）。
- `--account` 仅在 `--channel` 下有效。
- `--target` 接受 `channel:<id>` 或原始数字频道 ID，且仅适用于 Discord。
- 探测因提供商而异：Discord 意图 + 可选频道权限；Slack 机器人 + 用户范围；Telegram 机器人标志 + Webhook；Signal 守护进程版本；Microsoft Teams 应用令牌 + Graph 角色/范围（已知处有注释）。没有探测的频道报告 `Probe: unavailable`。

## 将名称解析为 ID

使用提供商目录将频道/用户名解析为 ID：

```bash
openclaw channels resolve --channel slack "#general" "@jane"
openclaw channels resolve --channel discord "My Server/#support" "@someone"
openclaw channels resolve --channel matrix "Project Room"
```

注意：

- 使用 `--kind user|group|auto` 强制目标类型。
- 当多个条目共享同一名称时，解析优先选择活动匹配项。
- `channels resolve` 是只读的。如果选定的账户通过 SecretRef 配置但该凭据在当前命令路径中不可用，则该命令返回带有说明的降级未解析结果，而不是中止整个运行。