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

当多个DM发送者共享主会话时，审计会发出警告，并推荐使用**安全DM模式**：`session.dmScope="per-channel-peer"`（或`per-account-channel-peer`用于多账户频道）以供共享收件箱使用。
这是为了加强合作/共享收件箱的安全性。由相互不信任/对抗的操作员共享的单个网关不是一个推荐的设置；通过单独的网关（或单独的操作系统用户/主机）来划分信任边界。
当未使用沙盒且启用Web/浏览器工具时，它还会对使用小型模型(`<=300B`)发出警告。
对于Webhook入口，当`hooks.defaultSessionKey`未设置时，当请求`sessionKey`覆盖被启用时，以及当没有`hooks.allowedSessionKeyPrefixes`时启用覆盖时，它会发出警告。
当沙盒Docker设置在沙盒模式关闭时被配置，当`gateway.nodes.denyCommands`使用无效的模式类/未知条目时，当全局`tools.profile="minimal"`被代理工具配置文件覆盖时，以及当已安装的扩展插件工具可能在宽松的工具策略下可访问时，它也会发出警告。
当沙盒浏览器使用Docker `bridge`网络而没有`sandbox.browser.cdpSourceRange`时，它也会发出警告。
当现有的沙盒浏览器Docker容器缺少/过时的哈希标签（例如迁移前的容器缺少`openclaw.browserConfigEpoch`）时，它也会发出警告并推荐`openclaw sandbox recreate --browser --all`。
当基于npm的插件/钩子安装记录未固定，缺少完整性元数据或与当前安装的软件包版本存在差异时，它也会发出警告。
当Discord白名单(`channels.discord.allowFrom`, `channels.discord.guilds.*.users`, 配对存储)使用名称或标签条目而不是稳定ID时，它会发出警告。
当`gateway.auth.mode="none"`在没有共享密钥(`/tools/invoke`加上任何启用的`/v1/*`端点)的情况下使Gateway HTTP API可访问时，它会发出警告。

## JSON输出

使用`--json`进行CI/策略检查：

```bash
openclaw security audit --json | jq '.summary'
openclaw security audit --deep --json | jq '.findings[] | select(.severity=="critical") | .checkId'
```

如果结合使用`--fix`和`--json`，输出将包括修复操作和最终报告：

```bash
openclaw security audit --fix --json | jq '{fix: .fix.ok, summary: .report.summary}'
```

## `--fix`更改了什么

`--fix`应用安全、确定性的补救措施：

- 将常见的`groupPolicy="open"`切换到`groupPolicy="allowlist"`（包括支持频道中的账户变体）
- 将`logging.redactSensitive`从`"off"`设置为`"tools"`
- 加强状态/配置和常见敏感文件的权限(`credentials/*.json`, `auth-profiles.json`, `sessions.json`, 会话`*.jsonl`)

`--fix`不会：

- 旋转令牌/密码/API密钥
- 禁用工具(`gateway`, `cron`, `exec`等)
- 更改网关绑定/身份验证/网络暴露选择
- 删除或重写插件/技能