---
summary: "Deep troubleshooting runbook for gateway, channels, automation, nodes, and browser"
read_when:
  - The troubleshooting hub pointed you here for deeper diagnosis
  - You need stable symptom based runbook sections with exact commands
title: "Troubleshooting"
---
# 网关故障排查

本页为深度排障手册。  
如需先执行快速分诊流程，请从 [/help/troubleshooting](/help/troubleshooting) 开始。

## 命令阶梯

请按以下顺序优先运行这些命令：

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

预期的健康信号包括：

- `openclaw gateway status` 显示 `Runtime: running` 和 `RPC probe: ok`。
- `openclaw doctor` 报告无阻塞配置/服务问题。
- `openclaw channels status --probe` 显示已连接/就绪的通道。

## Anthropic 429 错误：长上下文需额外用量

当日志/错误中包含以下内容时使用此节：
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`。

```bash
openclaw logs --follow
openclaw models status
openclaw config get agents.defaults.models
```

请检查：

- 所选 Anthropic Opus/Sonnet 模型具有 `params.context1m: true`。
- 当前 Anthropic 凭据不符合长上下文用量资格。
- 请求仅在需要 1M beta 路径的长会话/模型运行中失败。

修复选项：

1. 为该模型禁用 `context1m`，以回退至常规上下文窗口。
2. 使用已绑定账单的 Anthropic API 密钥，或在订阅账户中启用 Anthropic 额外用量。
3. 配置回退模型，使 Anthropic 长上下文请求被拒绝时仍可继续运行。

相关文档：

- [/providers/anthropic](/providers/anthropic)
- [/reference/token-use](/reference/token-use)
- [/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic](/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic)

## 无响应

若通道已上线但无任何回复，请在重新连接任何组件前，先检查路由与策略。

```bash
openclaw status
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw config get channels
openclaw logs --follow
```

请检查：

- 私信发送方存在配对待处理状态。
- 群组提及门控（`requireMention`、`mentionPatterns`）。
- 通道/群组白名单不匹配。

常见迹象：

- `drop guild message (mention required` → 群组消息在被提及前被忽略。
- `pairing request` → 发送方需获得批准。
- `blocked` / `allowlist` → 发送方/通道已被策略过滤。

相关文档：

- [/channels/troubleshooting](/channels/troubleshooting)
- [/channels/pairing](/channels/pairing)
- [/channels/groups](/channels/groups)

## 控制台控制 UI 连通性

当控制台/控制 UI 无法连接时，请验证 URL、认证模式及安全上下文假设。

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --json
```

请检查：

- 探针 URL 与控制台 URL 是否正确。
- 客户端与网关之间的认证模式/令牌是否不匹配。
- 在需要设备身份的场景下误用了 HTTP。

常见迹象：

- `device identity required` → 非安全上下文或缺少设备认证。
- `device nonce required` / `device nonce mismatch` → 客户端未完成基于挑战的设备认证流程（`connect.challenge` + `device.nonce`）。
- `device signature invalid` / `device signature expired` → 客户端为当前握手签署的载荷错误（或时间戳过期）。
- `unauthorized` / 重连循环 → 令牌/密码不匹配。
- `gateway connect failed:` → 主机/端口/URL 目标错误。

设备认证 v2 迁移检查：

```bash
openclaw --version
openclaw doctor
openclaw gateway status
```

若日志显示 nonce/签名错误，请更新连接客户端并验证其：

1. 等待 `connect.challenge`
2. 对绑定挑战的载荷进行签名
3. 使用相同的挑战 nonce 发送 `connect.params.device.nonce`

相关文档：

- [/web/control-ui](/web/control-ui)
- [/gateway/authentication](/gateway/authentication)
- [/gateway/remote](/gateway/remote)

## 网关服务未运行

当服务已安装但进程无法持续运行时使用此节。

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --deep
```

请检查：

- `Runtime: stopped` 及其退出提示。
- 服务配置不匹配（`Config (cli)` 与 `Config (service)`）。
- 端口/监听器冲突。

常见迹象：

- `Gateway start blocked: set gateway.mode=local` → 本地网关模式未启用。修复方法：在配置中设置 `gateway.mode="local"`（或运行 `openclaw configure`）。若您通过 Podman 运行 OpenClaw，并使用专用的 `openclaw` 用户，则配置文件位于 `~openclaw/.openclaw/openclaw.json`。
- `refusing to bind gateway ... without auth` → 未启用令牌/密码时尝试非环回地址绑定。
- `another gateway instance is already listening` / `EADDRINUSE` → 端口冲突。

相关文档：

- [/gateway/background-process](/gateway/background-process)
- [/gateway/configuration](/gateway/configuration)
- [/gateway/doctor](/gateway/doctor)

## 通道已连接但消息未流通

若通道状态为“已连接”，但消息流中断，请重点关注策略、权限及通道特定投递规则。

```bash
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw status --deep
openclaw logs --follow
openclaw config get channels
```

请检查：

- 私信策略（`pairing`、`allowlist`、`open`、`disabled`）。
- 群组白名单及提及要求。
- 缺失通道 API 权限/作用域。

常见迹象：

- `mention required` → 消息被群组提及策略忽略。
- `pairing` / 待审批痕迹 → 发送方尚未获批。
- `missing_scope`、`not_in_channel`、`Forbidden`、`401/403` → 通道认证/权限问题。

相关文档：

- [/channels/troubleshooting](/channels/troubleshooting)
- [/channels/whatsapp](/channels/whatsapp)
- [/channels/telegram](/channels/telegram)
- [/channels/discord](/channels/discord)

## Cron 与心跳投递

若 Cron 或心跳未运行或未成功投递，请首先验证调度器状态，再检查投递目标。

```bash
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
```

请检查：

- Cron 已启用且下次唤醒时间已设定。
- 作业运行历史状态（`ok`、`skipped`、`error`）。
- 心跳跳过原因（`quiet-hours`、`requests-in-flight`、`alerts-disabled`）。

常见迹象：

- `cron: scheduler disabled; jobs will not run automatically` → Cron 已禁用。
- `cron: timer tick failed` → 调度器 tick 失败；请检查文件/日志/运行时错误。
- `heartbeat skipped` 伴随 `reason=quiet-hours` → 超出活跃时段窗口。
- `heartbeat: unknown accountId` → 心跳投递目标账户 ID 无效。
- `heartbeat skipped` 伴随 `reason=dm-blocked` → 心跳目标解析为私信式目的地，而 `agents.defaults.heartbeat.directPolicy`（或按代理覆盖设置）被设为 `block`。

相关文档：

- [/automation/troubleshooting](/automation/troubleshooting)
- [/automation/cron-jobs](/automation/cron-jobs)
- [/gateway/heartbeat](/gateway/heartbeat)

## 已配对节点工具失败

若节点已配对但工具调用失败，请隔离前台状态、权限及审批状态。

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
openclaw status
```

请检查：

- 节点在线且具备预期能力。
- 操作系统已授予摄像头/麦克风/定位/屏幕共享等权限。
- 已完成执行审批且处于白名单内。

常见迹象：

- `NODE_BACKGROUND_UNAVAILABLE` → 节点应用必须处于前台。
- `*_PERMISSION_REQUIRED` / `LOCATION_PERMISSION_REQUIRED` → 缺少操作系统权限。
- `SYSTEM_RUN_DENIED: approval required` → 执行审批待处理。
- `SYSTEM_RUN_DENIED: allowlist miss` → 命令被白名单阻止。

相关文档：

- [/nodes/troubleshooting](/nodes/troubleshooting)
- [/nodes/index](/nodes/index)
- [/tools/exec-approvals](/tools/exec-approvals)

## 浏览器工具失败

当浏览器工具操作失败，但网关本身运行正常时使用此节。

```bash
openclaw browser status
openclaw browser start --browser-profile openclaw
openclaw browser profiles
openclaw logs --follow
openclaw doctor
```

请检查：

- 浏览器可执行文件路径是否有效。
- CDP 配置文件是否可达。
- 针对 `profile="chrome"` 的扩展中继标签是否已附加。

常见迹象：

- `Failed to start Chrome CDP on port` → 浏览器进程启动失败。
- `browser.executablePath not found` → 配置路径无效。
- `Chrome extension relay is running, but no tab is connected` → 扩展中继未附加。
- `Browser attachOnly is enabled ... not reachable` → 仅附加模式的配置文件无可达目标。

相关文档：

- [/tools/browser-linux-troubleshooting](/tools/browser-linux-troubleshooting)
- [/tools/chrome-extension](/tools/chrome-extension)
- [/tools/browser](/tools/browser)

## 升级后突然出现故障

大多数升级后的故障源于配置漂移或新版本强制执行更严格的默认值。

### 1) 认证与 URL 覆盖行为变更

```bash
openclaw gateway status
openclaw config get gateway.mode
openclaw config get gateway.remote.url
openclaw config get gateway.auth.mode
```

需检查项：

- 若启用了 `gateway.mode=remote`，CLI 调用可能指向远程服务，而您的本地服务实际正常。
- 显式 `--url` 调用不会回退至已存储的凭据。

常见迹象：

- `gateway connect failed:` → URL 目标错误。
- `unauthorized` → 端点可达但认证方式错误。

### 2) 绑定与认证防护机制更严格

```bash
openclaw config get gateway.bind
openclaw config get gateway.auth.token
openclaw gateway status
openclaw logs --follow
```

需检查项：

- 非环回地址绑定（`lan`、`tailnet`、`custom`）必须配置认证。
- 旧密钥（如 `gateway.token`）无法替代 `gateway.auth.token`。

常见迹象：

- `refusing to bind gateway ... without auth` → 绑定与认证不匹配。
- `RPC probe: failed`（运行时正在运行时）→ 网关存活但当前认证/URL 下不可访问。

### 3) 配对与设备身份状态变更

需检查的内容：

- 仪表板/节点的待处理设备审批。
- 策略或身份变更后的待处理设备管理（DM）配对审批。

常见错误签名：

- `device identity required` → 设备认证未满足。
- `pairing required` → 发送方/设备必须经过批准。

如果在完成上述检查后，服务配置与运行时状态仍然不一致，请从同一配置文件/状态目录重新安装服务元数据：

```bash
openclaw gateway install --force
openclaw gateway restart
```

相关链接：

- [/gateway/pairing](/gateway/pairing)
- [/gateway/authentication](/gateway/authentication)
- [/gateway/background-process](/gateway/background-process)