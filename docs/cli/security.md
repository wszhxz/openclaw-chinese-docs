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
```

当多个DM发送者共享主会话时，审计会发出警告，并建议使用`session.dmScope="per-channel-peer"`（或`per-account-channel-peer`用于多账户频道）以供共享收件箱使用。
它还会在未使用沙盒且启用web/浏览器工具的情况下使用小型模型(`<=300B`)时发出警告。