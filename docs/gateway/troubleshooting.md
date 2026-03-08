---
summary: "Deep troubleshooting runbook for gateway, channels, automation, nodes, and browser"
read_when:
  - The troubleshooting hub pointed you here for deeper diagnosis
  - You need stable symptom based runbook sections with exact commands
title: "Troubleshooting"
---
# Gateway 故障排查

此页面为深度运行手册。
如果您想先进行快速诊断流程，请从 [/help/troubleshooting](/help/troubleshooting) 开始。

## 命令阶梯

请按以下顺序首先运行这些：

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

预期的健康信号：

- `openclaw gateway status` 显示 `Runtime: running` 和 `RPC probe: ok`。
- `openclaw doctor` 报告无阻塞的配置/服务问题。
- `openclaw channels status --probe` 显示已连接/就绪的通道。

## Anthropic 429 长上下文需额外使用

当日志/错误包含以下内容时使用：
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`。

```bash
openclaw logs --follow
openclaw models status
openclaw config get agents.defaults.models
```

查找：

- 选定的 Anthropic Opus/Sonnet 模型具有 `params.context1m: true`。
- 当前 Anthropic 凭证不符合长上下文使用资格。
- 请求仅在需要 1M beta 路径的长会话/模型运行时失败。

修复选项：

1. 禁用该模型的 `context1m` 以回退到正常上下文窗口。
2. 使用带有计费的 Anthropic API 密钥，或在订阅账户上启用 Anthropic Extra Usage。
3. 配置回退模型，以便在 Anthropic 长上下文请求被拒绝时运行继续。

相关：

- [/providers/anthropic](/providers/anthropic)
- [/reference/token-use](/reference/token-use)
- [/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic](/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic)

## 无回复

如果通道已开启但无响应，请在重新连接任何内容之前检查路由和策略。

```bash
openclaw status
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw config get channels
openclaw logs --follow
```

查找：

- DM 发送者的配对待处理。
- 群组提及门控 (`requireMention`, `mentionPatterns`)。
- 通道/群组白名单不匹配。

常见特征：

- `drop guild message (mention required` → 群消息在提及前被忽略。
- `pairing request` → 发送者需要批准。
- `blocked` / `allowlist` → 发送者/通道被策略过滤。

相关：

- [/channels/troubleshooting](/channels/troubleshooting)
- [/channels/pairing](/channels/pairing)
- [/channels/groups](/channels/groups)

## 仪表盘控制 UI 连接性

当仪表盘/控制 UI 无法连接时，验证 URL、认证模式和安全上下文假设。

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --json
```

查找：

- 正确的探测 URL 和仪表盘 URL。
- 客户端与网关之间的认证模式/令牌不匹配。
- 需要设备身份时的 HTTP 使用。

常见特征：

- `device identity required` → 非安全上下文或缺少设备认证。
- `device nonce required` / `device nonce mismatch` → 客户端未完成基于挑战的设备认证流程 (`connect.challenge` + `device.nonce`)。
- `device signature invalid` / `device signature expired` → 客户端为当前握手签署了错误的负载（或过时的时间戳）。
- `unauthorized` / 重连循环 → 令牌/密码不匹配。
- `gateway connect failed:` → 错误的主机/端口/URL 目标。

设备认证 v2 迁移检查：

```bash
openclaw --version
openclaw doctor
openclaw gateway status
```

如果日志显示 nonce/签名错误，请更新连接的客户端并验证：

1. 等待 `connect.challenge`
2. 签署挑战绑定的负载
3. 发送 `connect.params.device.nonce` 并使用相同的挑战 nonce

相关：

- [/web/control-ui](/web/control-ui)
- [/gateway/authentication](/gateway/authentication)
- [/gateway/remote](/gateway/remote)

## Gateway 服务未运行

当服务已安装但进程无法保持运行时使用此方法。

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --deep
```

查找：

- `Runtime: stopped` 带有退出提示。
- 服务配置不匹配 (`Config (cli)` vs `Config (service)`)。
- 端口/监听器冲突。

常见特征：

- `Gateway start blocked: set gateway.mode=local` → 本地 Gateway 模式未启用。修复：在配置中设置 `gateway.mode="local"`（或运行 `openclaw configure`）。如果您通过 Podman 使用专用 `openclaw` 用户运行 OpenClaw，则配置位于 `~openclaw/.openclaw/openclaw.json`。
- `refusing to bind gateway ... without auth` → 无令牌/密码的非回环绑定。
- `another gateway instance is already listening` / `EADDRINUSE` → 端口冲突。

相关：

- [/gateway/background-process](/gateway/background-process)
- [/gateway/configuration](/gateway/configuration)
- [/gateway/doctor](/gateway/doctor)

## 通道连接消息未流动

如果通道状态已连接但消息流中断，请专注于策略、权限和通道特定的交付规则。

```bash
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw status --deep
openclaw logs --follow
openclaw config get channels
```

查找：

- DM 策略 (`pairing`, `allowlist`, `open`, `disabled`)。
- 群组白名单和提及要求。
- 缺少通道 API 权限/范围。

常见特征：

- `mention required` → 消息被群组提及策略忽略。
- `pairing` / 待批准追踪 → 发送者未获批准。
- `missing_scope`, `not_in_channel`, `Forbidden`, `401/403` → 通道认证/权限问题。

相关：

- [/channels/troubleshooting](/channels/troubleshooting)
- [/channels/whatsapp](/channels/whatsapp)
- [/channels/telegram](/channels/telegram)
- [/channels/discord](/channels/discord)

## Cron 和心跳交付

如果 Cron 或心跳未运行或未交付，请先验证调度器状态，然后验证交付目标。

```bash
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
```

查找：

- Cron 已启用且下次唤醒存在。
- 作业运行历史记录状态 (`ok`, `skipped`, `error`)。
- 心跳跳过原因 (`quiet-hours`, `requests-in-flight`, `alerts-disabled`)。

常见特征：

- `cron: scheduler disabled; jobs will not run automatically` → Cron 已禁用。
- `cron: timer tick failed` → 调度器周期失败；检查文件/日志/运行时错误。
- `heartbeat skipped` 与 `reason=quiet-hours` → 超出活动时间窗口。
- `heartbeat: unknown accountId` → 心跳交付目标无效账户 ID。
- `heartbeat skipped` 与 `reason=dm-blocked` → 心跳目标解析为 DM 风格目的地，而 `agents.defaults.heartbeat.directPolicy`（或每个代理覆盖）设置为 `block`。

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

- 节点在线且具有预期功能。
- 用于相机/麦克风/位置/屏幕的 OS 权限授予。
- 执行批准和白名单状态。

常见特征：

- `NODE_BACKGROUND_UNAVAILABLE` → 节点应用必须在前台。
- `*_PERMISSION_REQUIRED` / `LOCATION_PERMISSION_REQUIRED` → 缺少 OS 权限。
- `SYSTEM_RUN_DENIED: approval required` → 执行批准待处理。
- `SYSTEM_RUN_DENIED: allowlist miss` → 命令被白名单阻止。

相关：

- [/nodes/troubleshooting](/nodes/troubleshooting)
- [/nodes/index](/nodes/index)
- [/tools/exec-approvals](/tools/exec-approvals)

## 浏览器工具失败

即使 Gateway 本身健康，当浏览器工具操作失败时使用此方法。

```bash
openclaw browser status
openclaw browser start --browser-profile openclaw
openclaw browser profiles
openclaw logs --follow
openclaw doctor
```

查找：

- 有效的浏览器可执行文件路径。
- CDP 配置可达性。
- 用于 `profile="chrome"` 的扩展中继标签附件。

常见特征：

- `Failed to start Chrome CDP on port` → 浏览器进程启动失败。
- `browser.executablePath not found` → 配置的路径无效。
- `Chrome extension relay is running, but no tab is connected` → 扩展中继未附加。
- `Browser attachOnly is enabled ... not reachable` → 仅附加配置没有可达目标。

相关：

- [/tools/browser-linux-troubleshooting](/tools/browser-linux-troubleshooting)
- [/tools/chrome-extension](/tools/chrome-extension)
- [/tools/browser](/tools/browser)

## 如果您升级后某物突然损坏

大多数升级后的故障是由于配置漂移或现在强制执行更严格的默认值。

### 1) 认证和 URL 覆盖行为已更改

```bash
openclaw gateway status
openclaw config get gateway.mode
openclaw config get gateway.remote.url
openclaw config get gateway.auth.mode
```

检查什么：

- 如果 `gateway.mode=remote`，CLI 调用可能针对远程，而您的本地服务正常。
- 显式 `--url` 调用不会回退到存储的凭证。

常见特征：

- `gateway connect failed:` → 错误的 URL 目标。
- `unauthorized` → 端点可达但认证错误。

### 2) 绑定和认证护栏更严格

```bash
openclaw config get gateway.bind
openclaw config get gateway.auth.token
openclaw gateway status
openclaw logs --follow
```

检查什么：

- 非回环绑定 (`lan`, `tailnet`, `custom`) 需要配置认证。
- 旧密钥如 `gateway.token` 不能替换 `gateway.auth.token`。

常见特征：

- `refusing to bind gateway ... without auth` → 绑定 + 认证不匹配。
- `RPC probe: failed` 而运行时正在运行 → Gateway 存活但使用当前认证/URL 无法访问。

### 3) 配对和设备身份状态已更改

```bash
openclaw devices list
openclaw pairing list --channel <channel> [--account <id>]
openclaw logs --follow
openclaw doctor
```

检查内容：

- 待处理的 dashboard/nodes 设备审批。
- 策略或身份更改后待处理的 DM pairing 审批。

常见特征：

- `device identity required` → 设备认证未满足。
- `pairing required` → 发送方/设备必须被审批。

如果检查后服务配置和运行时仍然不一致，请从相同的 profile/state 目录重新安装服务元数据：

```bash
openclaw gateway install --force
openclaw gateway restart
```

相关：

- [/gateway/pairing](/gateway/pairing)
- [/gateway/authentication](/gateway/authentication)
- [/gateway/background-process](/gateway/background-process)