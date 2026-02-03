---
summary: "CLI reference for `openclaw security` (audit and fix common security footguns)"
read_when:
  - You want to run a quick security audit on config/state
  - You want to apply safe “fix” suggestions (chmod, tighten defaults)
title: "security"
---
# `openclaw 安全性`

安全工具（审计 + 可选修复）。

相关：

- 安全指南：[安全](/gateway/security)

## 审计

```bash
openclaw security audit
openclaw security audit --deep
openclaw security audit --fix
```

审计会在多个 DM 发送者共享主会话时发出警告，并推荐设置 `session.dmScope="per-channel-peer"`（或 `per-account-channel-peer` 用于多账户通道）以实现共享收件箱。它还会在未启用沙箱化且启用了网页/浏览器工具的情况下使用小型模型（`<=300B`）时发出警告。