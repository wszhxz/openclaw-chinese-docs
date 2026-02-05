---
summary: "Run multiple OpenClaw Gateways on one host (isolation, ports, and profiles)"
read_when:
  - Running more than one Gateway on the same machine
  - You need isolated config/state/ports per Gateway
title: "Multiple Gateways"
---
# 多个网关（同一主机）

大多数设置应使用一个网关，因为单个网关可以处理多个消息连接和代理。如果您需要更强的隔离或冗余（例如，救援机器人），请使用具有独立配置文件/端口的单独网关。

## 隔离检查表（必需）

- `OPENCLAW_CONFIG_PATH` — 每实例配置文件
- `OPENCLAW_STATE_DIR` — 每实例会话、凭据、缓存
- `agents.defaults.workspace` — 每实例工作区根目录
- `gateway.port` (或 `--port`) — 每实例唯一
- 派生端口（浏览器/画布）不得重叠

如果这些被共享，您将遇到配置竞争和端口冲突。

## 推荐：配置文件 (`--profile`)

配置文件自动限定 `OPENCLAW_STATE_DIR` + `OPENCLAW_CONFIG_PATH` 并后缀服务名称。

```bash
# main
openclaw --profile main setup
openclaw --profile main gateway --port 18789

# rescue
openclaw --profile rescue setup
openclaw --profile rescue gateway --port 19001
```

每配置文件服务：

```bash
openclaw --profile main gateway install
openclaw --profile rescue gateway install
```

## 救援机器人指南

在同一主机上运行第二个网关，并为其提供自己的：

- 配置文件/配置
- 状态目录
- 工作区
- 基础端口（加上派生端口）

这将使救援机器人与主机器人隔离，以便在主机器人宕机时进行调试或应用配置更改。

端口间距：基础端口之间至少留出20个端口，以确保派生的浏览器/画布/CDP端口不会冲突。

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

## 端口映射（派生）

基础端口 = `gateway.port` (或 `OPENCLAW_GATEWAY_PORT` / `--port`)。

- 浏览器控制服务端口 = 基础 + 2（仅限回环）
- `canvasHost.port = base + 4`
- 浏览器配置文件CDP端口从 `browser.controlPort + 9 .. + 108` 自动分配

如果您在配置或环境中覆盖了这些值，则必须确保每个实例都是唯一的。

## 浏览器/CDP 注意事项（常见陷阱）

- 不要将 `browser.cdpUrl` 在多个实例中固定为相同的值。
- 每个实例需要自己的浏览器控制端口和CDP范围（从其网关端口派生）。
- 如果需要显式的CDP端口，请按实例设置 `browser.profiles.<name>.cdpPort`。
- 远程Chrome：使用 `browser.profiles.<name>.cdpUrl`（每个配置文件，每个实例）。

## 手动环境示例

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/main.json \
OPENCLAW_STATE_DIR=~/.openclaw-main \
openclaw gateway --port 18789

OPENCLAW_CONFIG_PATH=~/.openclaw/rescue.json \
OPENCLAW_STATE_DIR=~/.openclaw-rescue \
openclaw gateway --port 19001
```

## 快速检查

```bash
openclaw --profile main status
openclaw --profile rescue status
openclaw --profile rescue browser status
```