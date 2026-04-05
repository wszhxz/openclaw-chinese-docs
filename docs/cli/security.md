---
summary: "CLI reference for `openclaw security` (audit and fix common security footguns)"
read_when:
  - You want to run a quick security audit on config/state
  - You want to apply safe “fix” suggestions (permissions, tighten defaults)
title: "security"
---
# `openclaw security`

安全工具（审计 + 可选修复）。

相关：

- 安全指南：[安全](/gateway/security)

## 审计

```bash
openclaw security audit
openclaw security audit --deep
openclaw security audit --deep --password <password>
openclaw security audit --deep --token <token>
openclaw security audit --fix
openclaw security audit --json
```

当多个私信发送者共享主会话时，审计会发出警告，并推荐用于共享收件箱的**安全私信模式**：`session.dmScope="per-channel-peer"`（或针对多账户频道的 `per-account-channel-peer`）。
这是为了协作/共享收件箱的安全加固。由互不信任/敌对的操作员共享单个网关不是推荐的设置；应使用单独的网关（或单独的操作系统用户/主机）来分割信任边界。
当配置表明可能存在共享用户入口时（例如开放私信/群组策略、配置的群组目标或通配符发送者规则），它还会发出 `security.trust_model.multi_user_heuristic`，并提醒您 OpenClaw 默认是个人助手信任模型。
对于有意的共享用户设置，审计指导方针是将所有会话沙箱化，保持文件系统访问范围限于工作区，并将个人/私有身份或凭证与该运行时隔离。
当使用小型模型（`<=300B`）且未进行沙箱化并启用了 Web/浏览器工具时，它也会发出警告。
对于 Webhook 入口，当 `hooks.token` 重用网关令牌时，当 `hooks.token` 过短时，当 `hooks.path="/"` 时，当 `hooks.defaultSessionKey` 未设置时，当 `hooks.allowedAgentIds` 不受限制时，当请求 `sessionKey` 覆盖启用时，以及当启用覆盖但未启用 `hooks.allowedSessionKeyPrefixes` 时，它会发出警告。
当沙箱 Docker 设置在沙箱模式关闭时配置，当 `gateway.nodes.denyCommands` 使用无效的模式类/未知条目（仅精确节点命令名称匹配，而非 Shell 文本过滤），当 `gateway.nodes.allowCommands` 显式启用危险的节点命令，当全局 `tools.profile="minimal"` 被代理工具配置文件覆盖，当开放群组暴露运行时/文件系统工具而没有沙箱/工作区保护，以及当安装扩展插件工具在宽松的工具策略下可能可访问时，它也会发出警告。
它还会标记 `gateway.allowRealIpFallback=true`（如果代理配置错误存在标头欺骗风险）和 `discovery.mdns.mode="full"`（通过 mDNS TXT 记录泄露元数据）。
当沙箱浏览器使用 Docker `bridge` 网络而未使用 `sandbox.browser.cdpSourceRange` 时，它也会发出警告。
它还会标记危险的沙箱 Docker 网络模式（包括 `host` 和 `container:*` 命名空间加入）。
当现有的沙箱浏览器 Docker 容器缺少/过时的哈希标签（例如迁移前容器缺少 `openclaw.browserConfigEpoch`）时，它也会发出警告，并建议 `openclaw sandbox recreate --browser --all`。
当基于 npm 的插件/钩子安装记录未锁定、缺少完整性元数据或与当前安装的软件包版本发生漂移时，它也会发出警告。
当频道白名单依赖可变名称/电子邮件/标签而不是稳定 ID 时（适用于 Discord、Slack、Google Chat、Microsoft Teams、Mattermost、IRC 范围），它会发出警告。
当 `gateway.auth.mode="none"` 使网关 HTTP API 在没有共享密钥的情况下可达（`/tools/invoke` 加上任何启用的 `/v1/*` 端点）时，它会发出警告。
以 `dangerous`/`dangerously` 开头的设置是明确的紧急操作员覆盖；启用其中一个本身并不是安全漏洞报告。
有关完整危险参数清单，请参阅 [安全](/gateway/security) 中的“不安全或危险标志摘要”部分。

SecretRef 行为：

- `security audit` 以其目标路径为对象，以只读模式解析支持的 SecretRefs。
- 如果当前命令路径中不可用 SecretRef，审计将继续并报告 `secretDiagnostics`（而不是崩溃）。
- `--token` 和 `--password` 仅覆盖该命令调用的深度探测认证；它们不会重写配置或 SecretRef 映射。

## JSON 输出

在 CI/策略检查中使用 `--json`：

```bash
openclaw security audit --json | jq '.summary'
openclaw security audit --deep --json | jq '.findings[] | select(.severity=="critical") | .checkId'
```

如果结合使用 `--fix` 和 `--json`，输出将包含修复操作和最终报告：

```bash
openclaw security audit --fix --json | jq '{fix: .fix.ok, summary: .report.summary}'
```

## `--fix` 更改内容

`--fix` 应用安全、确定性的修复措施：

- 将常见的 `groupPolicy="open"` 切换为 `groupPolicy="allowlist"`（包括支持频道中的账户变体）
- 当 WhatsApp 群组策略切换为 `allowlist` 时，如果列表存在且配置尚未定义 `allowFrom`，则从存储的 `allowFrom` 文件填充 `groupAllowFrom`
- 将 `logging.redactSensitive` 从 `"off"` 设置为 `"tools"`
- 收紧状态/配置和常见敏感文件的权限（`credentials/*.json`, `auth-profiles.json`, `sessions.json`, 会话 `*.jsonl`）
- 还收紧从 `openclaw.json` 引用配置包含文件
- 在 POSIX 主机上使用 `chmod`，在 Windows 上使用 `icacls` 重置

`--fix` **不**执行以下操作：

- 轮换令牌/密码/API 密钥
- 禁用工具（`gateway`, `cron`, `exec` 等）
- 更改网关绑定/认证/网络暴露选择
- 移除或重写插件/技能