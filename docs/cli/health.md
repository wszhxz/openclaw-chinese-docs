---
summary: "CLI reference for `openclaw health` (gateway health snapshot via RPC)"
read_when:
  - You want to quickly check the running Gateway’s health
title: "health"
---
# `openclaw health`

从正在运行的网关获取健康状态。

选项：

- `--json`: 机器可读输出
- `--timeout <ms>`: 连接超时时间（毫秒）（默认值 `10000`）
- `--verbose`: 详细日志记录
- `--debug`: `--verbose` 的别名

示例：

```bash
openclaw health
openclaw health --json
openclaw health --timeout 2500
openclaw health --verbose
openclaw health --debug
```

注意：

- 默认情况下，`openclaw health` 会向正在运行的网关请求其健康快照。当网关已拥有最新缓存的快照时，它可以返回该缓存负载并在后台进行刷新。
- `--verbose` 强制进行实时探测，打印网关连接详情，并扩展人类可读的输出以涵盖所有配置的账户和代理。
- 当配置了多个代理时，输出包含每个代理的会话存储。