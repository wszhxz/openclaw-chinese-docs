---
summary: "CLI reference for `openclaw node` (headless node host)"
read_when:
  - Running the headless node host
  - Pairing a non-macOS node for system.run
title: "node"
---
# `openclaw node`

运行一个**无头节点主机（headless node host）**，该主机连接至网关 WebSocket，并在此机器上暴露  
`system.run` / `system.which`。

## 为何使用节点主机？

当您希望代理（agents）能够在网络中的**其他机器上执行命令**，而无需在那些机器上安装完整的 macOS 配套应用时，请使用节点主机。

常见使用场景包括：

- 在远程 Linux/Windows 设备（如构建服务器、实验室设备、NAS）上运行命令。
- 将 exec 操作**沙箱化**保留在网关上，但将已批准的执行任务委派给其他主机。
- 为自动化或 CI 节点提供一个轻量级、无头的执行目标。

执行过程仍受 **exec 批准机制** 和节点主机上按代理设置的允许列表（per-agent allowlists）保护，因此您可以将命令访问权限严格限定在明确指定的范围内。

## 浏览器代理（零配置）

若节点上未禁用 `browser.enabled`，节点主机会自动广播一个浏览器代理。这使得代理可在该节点上直接使用浏览器自动化功能，无需额外配置。

如需在节点上禁用该功能，请执行：

```json5
{
  nodeHost: {
    browserProxy: {
      enabled: false,
    },
  },
}
```

## 运行（前台模式）

```bash
openclaw node run --host <gateway-host> --port 18789
```

选项：

- `--host <host>`：网关 WebSocket 主机地址（默认值：`127.0.0.1`）
- `--port <port>`：网关 WebSocket 端口（默认值：`18789`）
- `--tls`：对网关连接启用 TLS
- `--tls-fingerprint <sha256>`：预期的 TLS 证书指纹（sha256）
- `--node-id <id>`：覆盖节点 ID（将清除配对令牌）
- `--display-name <name>`：覆盖节点显示名称

## 节点主机的网关认证

`openclaw node run` 和 `openclaw node install` 通过配置/环境变量解析网关认证信息（节点命令中不使用 `--token`/`--password` 标志）：

- 首先检查 `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`。
- 然后回退至本地配置：`gateway.auth.token` / `gateway.auth.password`。
- 在本地模式下，当 `gateway.auth.*` 未设置时，`gateway.remote.token` / `gateway.remote.password` 同样可作为回退选项。
- 在 `gateway.mode=remote` 模式下，远程客户端字段（`gateway.remote.token` / `gateway.remote.password`）也符合远程优先级规则，可被选用。
- 旧版 `CLAWDBOT_GATEWAY_*` 环境变量在节点主机认证解析过程中将被忽略。

## 服务（后台模式）

将无头节点主机安装为用户级服务。

```bash
openclaw node install --host <gateway-host> --port 18789
```

选项：

- `--host <host>`：网关 WebSocket 主机地址（默认值：`127.0.0.1`）
- `--port <port>`：网关 WebSocket 端口（默认值：`18789`）
- `--tls`：对网关连接启用 TLS
- `--tls-fingerprint <sha256>`：预期的 TLS 证书指纹（sha256）
- `--node-id <id>`：覆盖节点 ID（将清除配对令牌）
- `--display-name <name>`：覆盖节点显示名称
- `--runtime <runtime>`：服务运行时（`node` 或 `bun`）
- `--force`：若已安装，则重新安装/覆盖

管理服务：

```bash
openclaw node status
openclaw node stop
openclaw node restart
openclaw node uninstall
```

使用 `openclaw node run` 启动前台模式的节点主机（不启用服务）。

服务命令支持 `--json` 参数以输出机器可读格式。

## 配对

首次连接将在网关上创建一个待处理的设备配对请求（`role: node`）。  
请通过以下方式批准该请求：

```bash
openclaw devices list
openclaw devices approve <requestId>
```

节点主机将其节点 ID、令牌、显示名称及网关连接信息存储于  
`~/.openclaw/node.json` 中。

## Exec 批准机制

`system.run` 受本地 exec 批准机制管控：

- `~/.openclaw/exec-approvals.json`
- [Exec 批准机制](/tools/exec-approvals)
- `openclaw approvals --node <id|name|ip>`（可从网关端编辑）