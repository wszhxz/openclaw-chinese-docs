---
summary: "CLI reference for `openclaw security` (audit and fix common security footguns)"
read_when:
  - You want to run a quick security audit on config/state
  - You want to apply safe “fix” suggestions (chmod, tighten defaults)
title: "security"
---
# `openclaw security`

安全工具（审计 + 可选修复）。

相关：

- 安全指南：[Security](/gateway/security)

## 审计

```bash
openclaw security audit
openclaw security audit --deep
openclaw security audit --fix
openclaw security audit --json
```

当多个 DM 发送者共享主会话时，审计会发出警告，并推荐共享收件箱使用 **安全 DM 模式**：`session.dmScope="per-channel-peer"`（或多账户渠道使用 `per-account-channel-peer`）。
这是为了协作/共享收件箱加固。不建议由相互不信任/对立的运营者共享单个 Gateway；应通过独立的 gateway（或独立的 OS 用户/主机）分割信任边界。
当配置表明可能存在共享用户入口时（例如开放的 DM/组策略、配置的组目标或通配符发送者规则），它也会发出 `security.trust_model.multi_user_heuristic`，并提醒您 OpenClaw 默认是个人助手信任模型。
对于有意的共享用户设置，审计指导是对所有会话进行沙箱处理，将文件系统访问限制在工作区范围内，并将个人/私有身份或凭证与该运行时隔离。
当小型模型（`<=300B`）在未使用沙箱且启用了 web/浏览器工具的情况下使用时，它也会发出警告。
对于 webhook 入口，当 `hooks.defaultSessionKey` 未设置、启用了请求 `sessionKey` 覆盖，或在没有 `hooks.allowedSessionKeyPrefixes` 的情况下启用覆盖时，它会发出警告。
当沙箱 Docker 设置已配置但沙箱模式关闭时、当 `gateway.nodes.denyCommands` 使用无效的模式类/未知条目时（仅精确节点命令名称匹配，而非 shell 文本过滤）、当 `gateway.nodes.allowCommands` 显式启用危险节点命令时、当全局 `tools.profile="minimal"` 被代理工具配置文件覆盖时、当开放组在没有沙箱/工作区保护的情况下暴露运行时/文件系统工具时，以及当已安装的扩展插件工具可能在宽松工具策略下被访问时，它也会发出警告。
它还会标记 `gateway.allowRealIpFallback=true`（如果代理配置错误存在头欺骗风险）和 `discovery.mdns.mode="full"`（通过 mDNS TXT 记录泄露元数据）。
当沙箱浏览器使用 Docker `bridge` 网络而没有 `sandbox.browser.cdpSourceRange` 时，它也会发出警告。
它还会标记危险的沙箱 Docker 网络模式（包括 `host` 和 `container:*` 命名空间加入）。
当现有的沙箱浏览器 Docker 容器缺少/过时的 hash 标签时（例如迁移前的容器缺少 `openclaw.browserConfigEpoch`），它也会发出警告并推荐 `openclaw sandbox recreate --browser --all`。
当基于 npm 的插件/hook 安装记录未固定、缺少完整性元数据或与当前安装的包版本不一致时，它也会发出警告。
当渠道允许列表依赖可变的名称/电子邮件/标签而不是稳定的 ID 时（Discord、Slack、Google Chat、MS Teams、Mattermost、IRC 范围，如适用），它会发出警告。
当 `gateway.auth.mode="none"` 使 Gateway HTTP APIs 在没有共享密钥的情况下可访问时（`/tools/invoke` 加上任何启用的 `/v1/*` 端点），它会发出警告。
以 `dangerous`/`dangerously` 为前缀的设置是显式的 break-glass 操作员覆盖；启用其中一个本身并不构成安全漏洞报告。
完整的危险参数清单，请参阅 [Security](/gateway/security) 中的“不安全或危险标志摘要”部分。

## JSON 输出

使用 `--json` 进行 CI/策略检查：

```bash
openclaw security audit --json | jq '.summary'
openclaw security audit --deep --json | jq '.findings[] | select(.severity=="critical") | .checkId'
```

如果组合使用 `--fix` 和 `--json`，输出将包含修复操作和最终报告：

```bash
openclaw security audit --fix --json | jq '{fix: .fix.ok, summary: .report.summary}'
```

## `--fix` 更改的内容

`--fix` 应用安全、确定的补救措施：

- 将常见的 `groupPolicy="open"` 翻转为 `groupPolicy="allowlist"`（包括支持渠道中的账户变体）
- 将 `logging.redactSensitive` 从 `"off"` 设置为 `"tools"`
- 收紧状态/配置和常见敏感文件的权限（`credentials/*.json`、`auth-profiles.json`、`sessions.json`、会话 `*.jsonl`）

`--fix` **不**执行以下操作：

- 轮换令牌/密码/API 密钥
- 禁用工具（`gateway`、`cron`、`exec` 等）
- 更改 gateway 绑定/认证/网络暴露选择
- 移除或重写插件/skills