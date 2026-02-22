---
summary: "Deep troubleshooting runbook for gateway, channels, automation, nodes, and browser"
read_when:
  - The troubleshooting hub pointed you here for deeper diagnosis
  - You need stable symptom based runbook sections with exact commands
title: "Troubleshooting"
---
# 网关故障排除

本页面是深入运行手册。
如果您想先进行快速排查流程，请从[/help/troubleshooting](/help/troubleshooting)开始。

## 命令梯度

按顺序运行这些命令：

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

预期的健康信号：

- `openclaw gateway status` 显示 `Runtime: running` 和 `RPC probe: ok`。
- `openclaw doctor` 报告没有阻止配置/服务问题。
- `openclaw channels status --probe` 显示已连接/就绪的通道。

## 没有回复

如果通道已启动但没有任何响应，请在重新连接之前检查路由和策略。

```bash
openclaw status
openclaw channels status --probe
openclaw pairing list <channel>
openclaw config get channels
openclaw logs --follow
```

查找：

- 待配对的DM发送者。
- 群组提及门控 (`requireMention`, `mentionPatterns`)。
- 通道/群组允许列表不匹配。

常见迹象：

- `drop guild message (mention required` → 群组消息被忽略直到提及。
- `pairing request` → 发送者需要批准。
- `blocked` / `allowlist` → 发送者/通道被策略过滤。

相关：

- [/channels/troubleshooting](/channels/troubleshooting)
- [/channels/pairing](/channels/pairing)
- [/channels/groups](/channels/groups)

## 仪表盘控制UI连接性

当仪表盘/控制UI无法连接时，请验证URL、认证模式和安全上下文假设。

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --json
```

查找：

- 正确的探测URL和仪表盘URL。
- 客户端和网关之间的认证模式/令牌不匹配。
- 在需要设备身份的情况下使用HTTP。

常见迹象：

- `device identity required` → 非安全上下文或缺少设备认证。
- `unauthorized` / 重新连接循环 → 令牌/密码不匹配。
- `gateway connect failed:` → 错误的目标主机/端口/URL。

相关：

- [/web/control-ui](/web/control-ui)
- [/gateway/authentication](/gateway/authentication)
- [/gateway/remote](/gateway/remote)

## 网关服务未运行

当服务已安装但进程未保持运行时使用此方法。

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --deep
```

查找：

- 带退出提示的 `Runtime: stopped`。
- 服务配置不匹配 (`Config (cli)` 对比 `Config (service)`)。
- 端口/监听器冲突。

常见迹象：

- `Gateway start blocked: set gateway.mode=local` → 本地网关模式未启用。解决方法：在配置中设置 `gateway.mode="local"`（或运行 `openclaw configure`）。如果您通过Podman使用专用的 `openclaw` 用户运行OpenClaw，配置文件位于 `~openclaw/.openclaw/openclaw.json`。
- `refusing to bind gateway ... without auth` → 非回环绑定且没有令牌/密码。
- `another gateway instance is already listening` / `EADDRINUSE` → 端口冲突。

相关：

- [/gateway/background-process](/gateway/background-process)
- [/gateway/configuration](/gateway/configuration)
- [/gateway/doctor](/gateway/doctor)

## 通道连接消息未流动

如果通道状态已连接但消息流中断，请关注策略、权限和特定于通道的传递规则。

```bash
openclaw channels status --probe
openclaw pairing list <channel>
openclaw status --deep
openclaw logs --follow
openclaw config get channels
```

查找：

- DM策略 (`pairing`, `allowlist`, `open`, `disabled`)。
- 群组允许列表和提及要求。
- 缺少通道API权限/范围。

常见迹象：

- `mention required` → 消息被群组提及策略忽略。
- `pairing` / 待批处理跟踪 → 发送者未获批准。
- `missing_scope`, `not_in_channel`, `Forbidden`, `401/403` → 通道认证/权限问题。

相关：

- [/channels/troubleshooting](/channels/troubleshooting)
- [/channels/whatsapp](/channels/whatsapp)
- [/channels/telegram](/channels/telegram)
- [/channels/discord](/channels/discord)

## Cron和心跳传递

如果cron或心跳未运行或未传递，请首先验证调度器状态，然后验证传递目标。

```bash
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
```

查找：

- Cron已启用且存在下次唤醒时间。
- 作业运行历史状态 (`ok`, `skipped`, `error`)。
- 心跳跳过原因 (`quiet-hours`, `requests-in-flight`, `alerts-disabled`)。

常见迹象：

- `cron: scheduler disabled; jobs will not run automatically` → cron已禁用。
- `cron: timer tick failed` → 调度器滴答失败；检查文件/日志/运行时错误。
- `heartbeat skipped` 与 `reason=quiet-hours` → 处于非活动时间窗口之外。
- `heartbeat: unknown accountId` → 心跳传递目标的无效账户ID。

相关：

- [/automation/troubleshooting](/automation/troubleshooting)
- [/automation/cron-jobs](/automation/cron-jobs)
- [/gateway/heartbeat](/gateway/heartbeat)

## 节点配对工具失败

如果节点已配对但工具失败，请隔离前台、权限和批准状态。

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
openclaw status
```

查找：

- 具有预期功能的在线节点。
- 操作系统对摄像头/麦克风/位置/屏幕的权限授予。
- 执行批准和允许列表状态。

常见迹象：

- `NODE_BACKGROUND_UNAVAILABLE` → 节点应用程序必须在前台。
- `*_PERMISSION_REQUIRED` / `LOCATION_PERMISSION_REQUIRED` → 缺少操作系统权限。
- `SYSTEM_RUN_DENIED: approval required` → 执行批准待处理。
- `SYSTEM_RUN_DENIED: allowlist miss` → 命令被允许列表阻止。

相关：

- [/nodes/troubleshooting](/nodes/troubleshooting)
- [/nodes/index](/nodes/index)
- [/tools/exec-approvals](/tools/exec-approvals)

## 浏览器工具失败

当网关本身正常但浏览器工具操作失败时使用此方法。

```bash
openclaw browser status
openclaw browser start --browser-profile openclaw
openclaw browser profiles
openclaw logs --follow
openclaw doctor
```

查找：

- 有效的浏览器可执行路径。
- CDP配置文件可达性。
- 对于 `profile="chrome"` 的扩展中继标签附加。

常见迹象：

- `Failed to start Chrome CDP on port` → 浏览器进程启动失败。
- `browser.executablePath not found` → 配置的路径无效。
- `Chrome extension relay is running, but no tab is connected` → 扩展中继未附加。
- `Browser attachOnly is enabled ... not reachable` → 仅附加配置文件没有可到达的目标。

相关：

- [/tools/browser-linux-troubleshooting](/tools/browser-linux-troubleshooting)
- [/tools/chrome-extension](/tools/chrome-extension)
- [/tools/browser](/tools/browser)

## 如果升级后某些东西突然出错

大多数升级后的故障是配置漂移或现在强制执行更严格的默认值。

### 1) 认证和URL覆盖行为已更改

```bash
openclaw gateway status
openclaw config get gateway.mode
openclaw config get gateway.remote.url
openclaw config get gateway.auth.mode
```

要检查的内容：

- 如果 `gateway.mode=remote`，CLI调用可能针对远程而您的本地服务正常。
- 明确的 `--url` 调用不会回退到存储的凭据。

常见迹象：

- `gateway connect failed:` → 错误的目标URL。
- `unauthorized` → 终端可达但认证错误。

### 2) 绑定和认证护栏更严格

```bash
openclaw config get gateway.bind
openclaw config get gateway.auth.token
openclaw gateway status
openclaw logs --follow
```

要检查的内容：

- 非回环绑定 (`lan`, `tailnet`, `custom`) 需要配置认证。
- 旧密钥如 `gateway.token` 不会替换 `gateway.auth.token`。

常见迹象：

- `refusing to bind gateway ... without auth` → 绑定+认证不匹配。
- `RPC probe: failed` 当运行时正在运行 → 网关存活但无法使用当前认证/URL访问。

### 3) 配对和设备身份状态已更改

```bash
openclaw devices list
openclaw pairing list <channel>
openclaw logs --follow
openclaw doctor
```

要检查的内容：

- 仪表盘/节点的待处理设备批准。
- 策略或身份更改后的待处理DM配对批准。

常见迹象：

- `device identity required` → 设备认证不满足。
- `pairing required` → 发送者/设备必须获得批准。

如果检查后服务配置和运行时仍然存在分歧，请从同一配置文件/状态目录重新安装服务元数据：

```bash
openclaw gateway install --force
openclaw gateway restart
```

相关：

- [/gateway/pairing](/gateway/pairing)
- [/gateway/authentication](/gateway/authentication)
- [/gateway/background-process](/gateway/background-process)