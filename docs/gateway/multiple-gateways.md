---
summary: "Run multiple OpenClaw Gateways on one host (isolation, ports, and profiles)"
read_when:
  - Running more than one Gateway on the same machine
  - You need isolated config/state/ports per Gateway
title: "Multiple Gateways"
---
# 多网关（同一主机）

大多数设置应使用一个网关，因为单个网关可以处理多个消息连接和代理。如果需要更强的隔离或冗余（例如救援机器人），则运行具有隔离配置文件/端口的独立网关。

## 隔离检查清单（必需）

- `OPENCLAW_CONFIG_PATH` — 每个实例的配置文件
- `OPENCLAW_STATE_DIR` — 每个实例的会话、凭证、缓存
- `agents.defaults.workspace` — 每个实例的工作区根目录
- `gateway.port`（或 `--port`）— 每个实例唯一
- 派生端口（浏览器/画布）不得重叠

如果这些共享，则会出现配置冲突和端口冲突。

## 推荐：配置文件（`--profile`）

配置文件会自动作用域 `OPENCLAW_STATE_DIR` + `OPENCLAW_CONFIG_PATH` 并后缀服务名称。

```bash
# 主配置
openclaw --profile main setup
openclaw --
```