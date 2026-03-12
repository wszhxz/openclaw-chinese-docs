---
summary: "Run multiple OpenClaw Gateways on one host (isolation, ports, and profiles)"
read_when:
  - Running more than one Gateway on the same machine
  - You need isolated config/state/ports per Gateway
title: "Multiple Gateways"
---
# 多网关（同一主机）

大多数部署应仅使用一个网关，因为单个网关即可处理多个消息连接和代理。如果您需要更强的隔离性或冗余能力（例如：救援机器人），请运行多个相互隔离的网关实例（各自使用独立的配置文件/端口）。

## 隔离性检查清单（必需）

- `OPENCLAW_CONFIG_PATH` — 每实例配置文件  
- `OPENCLAW_STATE_DIR` — 每实例会话、凭据、缓存  
- `agents.defaults.workspace` — 每实例工作区根目录  
- `gateway.port`（或 `--port`）— 每实例唯一  
- 衍生端口（浏览器/画布）不得重叠  

若上述项被共享，将导致配置竞争与端口冲突。

## 推荐方式：使用配置档案（profiles，`--profile`）

配置档案可自动限定 `OPENCLAW_STATE_DIR` 和 `OPENCLAW_CONFIG_PATH` 的作用域，并为服务名称添加后缀。

```bash
# main
openclaw --profile main setup
openclaw --profile main gateway --port 18789

# rescue
openclaw --profile rescue setup
openclaw --profile rescue gateway --port 19001
```

按档案划分的服务：

```bash
openclaw --profile main gateway install
openclaw --profile rescue gateway install
```

## 救援机器人指南

在同一主机上运行第二个网关实例，该实例需拥有其专属的：

- 配置档案 / 配置文件  
- 状态目录（state dir）  
- 工作区（workspace）  
- 基础端口（base port，含其衍生端口）  

此举可确保救援机器人与主机器人完全隔离，从而在主机器人宕机时仍能执行调试或应用配置变更。

端口间隔建议：各实例的基础端口之间至少保留 20 个端口的间隔，以避免衍生的浏览器/画布/CDP 端口发生冲突。

### 如何安装（救援机器人）

```bash
# Main bot (existing or fresh, without --profile param)
# Runs on port 18789 + Chrome CDC/Canvas/... Ports
openclaw onboard
openclaw gateway install

# Rescue bot (isolated profile + ports)
openclaw --profile rescue onboard
# Notes:
# - workspace name will be postfixed with -rescue per default
# - Port should be at least 18789 + 20 Ports,
#   better choose completely different base port, like 19789,
# - rest of the onboarding is the same as normal

# To install the service (if not happened automatically during onboarding)
openclaw --profile rescue gateway install
```

## 端口映射（衍生端口）

基础端口 = `gateway.port`（或 `OPENCLAW_GATEWAY_PORT` / `--port`）。

- 浏览器控制服务端口 = 基础端口 + 2（仅限回环地址）  
- 画布（canvas）主机由网关 HTTP 服务器提供服务（端口与 `gateway.port` 相同）  
- 浏览器配置文件的 CDP 端口从 `browser.controlPort + 9 .. + 108` 开始自动分配  

若您通过配置或环境变量显式覆盖了其中任一端口，则必须确保其在每个实例中均保持唯一。

## 浏览器/CDP 注意事项（常见陷阱）

- **切勿** 在多个实例中将 `browser.cdpUrl` 固定为相同值。  
- 每个实例均需拥有独立的浏览器控制端口及 CDP 端口范围（由该实例的网关端口推导得出）。  
- 若需显式指定 CDP 端口，请为每个实例单独设置 `browser.profiles.<name>.cdpPort`。  
- 远程 Chrome：请使用 `browser.profiles.<name>.cdpUrl`（按配置档案、按实例设置）。

## 手动环境变量示例

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/main.json \
OPENCLAW_STATE_DIR=~/.openclaw-main \
openclaw gateway --port 18789

OPENCLAW_CONFIG_PATH=~/.openclaw/rescue.json \
OPENCLAW_STATE_DIR=~/.openclaw-rescue \
openclaw gateway --port 19001
```

## 快速检查项

```bash
openclaw --profile main status
openclaw --profile rescue status
openclaw --profile rescue browser status
```