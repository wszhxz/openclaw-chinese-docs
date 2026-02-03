---
summary: "CLI reference for `openclaw health` (gateway health endpoint via RPC)"
read_when:
  - You want to quickly check the running Gateway’s health
title: "health"
---
# `openclaw health`

从正在运行的网关获取健康状态。

```bash
openclaw health
openclaw health --json
openclaw health --verbose
```

说明：

- `--verbose` 会运行实时探针，并在配置了多个账户时打印每个账户的计时信息。
- 当配置了多个代理时，输出将包含每个代理的会话存储信息。