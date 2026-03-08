---
summary: "CLI reference for `openclaw node` (headless node host)"
read_when:
  - Running the headless node host
  - Pairing a non-macOS node for system.run
title: "node"
---
# `openclaw node`

运行一个 **无头节点主机**，它连接到网关 WebSocket 并暴露
`system.run` / `system.which` 在此机器上。

## 为什么使用节点主机？

当您希望代理在您的网络中的其他机器上 **运行命令** 时使用节点主机，
而无需在那里安装完整的 macOS 配套应用。

常见用例：

- 在远程 Linux/Windows 机器上运行命令（构建服务器、实验室机器、NAS）。
- 保持执行在网关上 **沙箱化**，但将批准的运行委托给其他主机。
- 为自动化或 CI 节点提供轻量级、无头的执行目标。

执行仍然受 **执行审批** 和节点主机上每个代理的允许列表保护，
因此您可以保持命令访问范围受限且明确。

## 浏览器代理（零配置）

如果节点上未禁用 `browser.enabled`，节点主机会自动通告浏览器代理。这允许代理在该节点上使用浏览器自动化，
无需额外配置。

如有需要，可在节点上禁用它：

```json5
{
  nodeHost: {
    browserProxy: {
      enabled: false,
    },
  },
}
```

## 运行（前台）

```bash
openclaw node run --host <gateway-host> --port 18789
```

选项：

- `--host <host>`：网关 WebSocket 主机（默认：`127.0.0.1`）
- `--port <port>`：网关 WebSocket 端口（默认：`18789`）
- `--tls`：用于网关连接的 TLS
- `--tls-fingerprint <sha256>`：预期的 TLS 证书指纹 (sha256)
- `--node-id <id>`：覆盖节点 ID（清除配对令牌）
- `--display-name <name>`：覆盖节点显示名称

## 节点主机的网关认证

`openclaw node run` 和 `openclaw node install` 从配置/环境变量解析网关认证（节点命令上没有 `--token`/`--password` 标志）：

- 首先检查 `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`。
- 然后是本地配置回退：`gateway.auth.token` / `gateway.auth.password`。
- 在本地模式下，当 `gateway.auth.*` 未设置时，`gateway.remote.token` / `gateway.remote.password` 也可作为回退。
- 在 `gateway.mode=remote` 中，远程客户端字段（`gateway.remote.token` / `gateway.remote.password`）根据远程优先级规则也可用。
- 传统的 `CLAWDBOT_GATEWAY_*` 环境变量在节点主机认证解析中被忽略。

## 服务（后台）

将无头节点主机安装为用户服务。

```bash
openclaw node install --host <gateway-host> --port 18789
```

选项：

- `--host <host>`：网关 WebSocket 主机（默认：`127.0.0.1`）
- `--port <port>`：网关 WebSocket 端口（默认：`18789`）
- `--tls`：用于网关连接的 TLS
- `--tls-fingerprint <sha256>`：预期的 TLS 证书指纹 (sha256)
- `--node-id <id>`：覆盖节点 ID（清除配对令牌）
- `--display-name <name>`：覆盖节点显示名称
- `--runtime <runtime>`：服务运行时（`node` 或 `bun`）
- `--force`：如果已安装则重新安装/覆盖

管理服务：

```bash
openclaw node status
openclaw node stop
openclaw node restart
openclaw node uninstall
```

使用 `openclaw node run` 运行前台节点主机（无服务）。

服务命令接受 `--json` 以获取机器可读输出。

## 配对

首次连接会在网关上创建一个待处理的设备配对请求（`role: node`）。
通过以下方式批准：

```bash
openclaw devices list
openclaw devices approve <requestId>
```

节点主机将其节点 ID、令牌、显示名称和网关连接信息存储在
`~/.openclaw/node.json` 中。

## 执行审批

`system.run` 受本地执行审批限制：

- `~/.openclaw/exec-approvals.json`
- [执行审批](/tools/exec-approvals)
- `openclaw approvals --node <id|name|ip>`（从网关编辑）