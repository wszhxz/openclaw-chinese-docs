---
summary: "CLI reference for `openclaw reset` (reset local state/config)"
read_when:
  - You want to wipe local state while keeping the CLI installed
  - You want a dry-run of what would be removed
title: "reset"
---
# `openclaw reset`

重置本地配置/状态（保留CLI安装）。

```bash
openclaw reset
openclaw reset --dry-run
openclaw reset --scope 配置+凭证+会话 --yes --非交互式
```