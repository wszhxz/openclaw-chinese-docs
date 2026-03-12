---
summary: "CLI reference for `openclaw security` (audit and fix common security footguns)"
read_when:
  - You want to run a quick security audit on config/state
  - You want to apply safe “fix” suggestions (chmod, tighten defaults)
title: "security"
---
# `openclaw security`

安全工具（审计 + 可选修复）。

相关文档：

- 安全指南：[Security](/gateway/security)

## 审计

```bash
openclaw security audit
openclaw security audit --deep
openclaw security audit --fix
openclaw security audit --json
```

当多个 DM 发送方共享主会话时，审计会发出警告，并推荐启用**安全 DM 模式**：`session.dmScope="per-channel-peer"`（或针对多账户频道的 `per-account-channel-peer`），以用于共享收件箱。  
此建议旨在强化协作式/共享收件箱的安全性。由互不信任或存在对抗关系的运营方共用单个网关，并非推荐部署方式；应通过独立网关（或独立操作系统用户/主机）划分信任边界。  
当配置暗示可能存在共享用户入口（例如开放 DM/群组策略、已配置的群组目标，或通配符发送方规则）时，审计还会输出 `security.trust_model.multi_user_heuristic`，并提醒您：OpenClaw 默认采用个人助理型信任模型。  
对于有意设计的共享用户场景，审计建议对所有会话进行沙箱隔离，将文件系统访问限制在工作区范围内，并避免在该运行时环境中存放个人/私有身份信息或凭据。  
当使用小型模型（`<=300B`）且未启用沙箱、同时启用了 Web/浏览器工具时，审计也会发出警告。  
对于 Webhook 入口，当 `hooks.defaultSessionKey` 未设置、请求 `sessionKey` 覆盖功能被启用、或在未启用 `hooks.allowedSessionKeyPrefixes` 的情况下启用覆盖功能时，审计均会发出警告。  
当沙箱 Docker 设置已配置但沙箱模式处于关闭状态时，审计也会发出警告；当 `gateway.nodes.denyCommands` 使用了无效的类模式/未知条目（仅支持精确匹配节点命令名称，不支持 shell 文本过滤）时；当 `gateway.nodes.allowCommands` 显式启用了危险的节点命令时；当全局 `tools.profile="minimal"` 被代理工具配置文件覆盖时；当开放群组在缺乏沙箱/工作区防护的情况下暴露了运行时/文件系统工具时；以及当已安装的扩展插件工具可能在宽松的工具策略下被调用时，审计同样会发出警告。  
审计还会标记 `gateway.allowRealIpFallback=true`（若代理配置错误，存在请求头伪造风险）和 `discovery.mdns.mode="full"`（通过 mDNS TXT 记录泄露元数据）。  
当沙箱浏览器使用 Docker `bridge` 网络但未启用 `sandbox.browser.cdpSourceRange` 时，审计也会发出警告。  
审计还会标记危险的沙箱 Docker 网络模式（包括 `host` 和 `container:*` 命名空间挂载）。  
当现有沙箱浏览器 Docker 容器缺少/哈希标签过期（例如迁移前容器缺失 `openclaw.browserConfigEpoch`）时，审计会发出警告，并推荐执行 `openclaw sandbox recreate --browser --all`。  
当基于 npm 的插件/钩子安装记录未固定版本、缺少完整性元数据，或与当前已安装包版本不一致时，审计也会发出警告。  
当频道白名单依赖于可变名称/邮箱/标签而非稳定 ID（适用于 Discord、Slack、Google Chat、MS Teams、Mattermost、IRC 等作用域）时，审计会发出警告。  
当 `gateway.auth.mode="none"` 导致网关 HTTP API 在无共享密钥（`/tools/invoke` 加上任意已启用的 `/v1/*` 端点）保护下仍可被访问时，审计会发出警告。  
以 `dangerous`/`dangerously` 开头的配置项是明确的“紧急绕过”操作员覆盖项；单独启用其中任一项本身并不构成安全漏洞报告。  
有关全部危险参数的完整清单，请参阅 [Security](/gateway/security) 中的“Insecure or dangerous flags summary”（不安全或危险标志汇总）章节。

## JSON 输出

使用 `--json` 进行 CI/策略检查：

```bash
openclaw security audit --json | jq '.summary'
openclaw security audit --deep --json | jq '.findings[] | select(.severity=="critical") | .checkId'
```

若同时使用 `--fix` 和 `--json`，输出将同时包含修复操作与最终报告：

```bash
openclaw security audit --fix --json | jq '{fix: .fix.ok, summary: .report.summary}'
```

## `--fix` 所做的更改

`--fix` 应用安全、确定性的修复措施：

- 将常见 `groupPolicy="open"` 切换为 `groupPolicy="allowlist"`（包括在所支持频道中对应账户的变体）  
- 将 `logging.redactSensitive` 从 `"off"` 设置为 `"tools"`  
- 收紧状态/配置及常见敏感文件的权限（`credentials/*.json`、`auth-profiles.json`、`sessions.json`、会话 `*.jsonl`）

`--fix` **不会**：

- 轮换令牌/密码/API 密钥  
- 禁用工具（`gateway`、`cron`、`exec` 等）  
- 更改网关绑定/认证/网络暴露策略  
- 删除或重写插件/技能