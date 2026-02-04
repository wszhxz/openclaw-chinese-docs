---
summary: "CLI reference for `openclaw node` (headless node host)"
read_when:
  - Running the headless node host
  - Pairing a non-macOS node for system.run
title: "node"
---
# `openclaw node`

运行一个 **headless node host**，该主机连接到网关 WebSocket 并在此机器上暴露
`system.run` / `system.which`。

## 为什么使用节点主机？

当您希望代理在您的网络中的其他机器（无需在那里安装完整的 macOS 伴侣应用程序）上**运行命令**时，使用节点主机。

常见用例：

- 在远程 Linux/Windows 机器（构建服务器、实验室机器、NAS）上运行命令。
- 将 exec **沙盒化**保留在网关上，但将批准的运行委托给其他主机。
- 为自动化或 CI 节点提供轻量级、无头的执行目标。

执行仍然受节点主机上的**exec 批准**和每个代理的允许列表保护，因此您可以保持命令访问范围明确且具体。

## 浏览器代理（零配置）

如果节点上未禁用 `browser.enabled`，节点主机会自动发布一个浏览器代理。这使代理能够在该节点上使用浏览器自动化而无需额外配置。

如果需要，可以在节点上禁用它：

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

- `--host <host>`: 网关 WebSocket 主机（默认：`127.0.0.1`）
- `--port <port>`: 网关 WebSocket 端口（默认：`18789`）
- `--tls`: 使用 TLS 进行网关连接
- `--tls-fingerprint <sha256>`: 预期的 TLS 证书指纹（sha256）
- `--node-id <id>`: 覆盖节点 ID（清除配对令牌）
- `--display-name <name>`: 覆盖节点显示名称

## 服务（后台）

将无头节点主机安装为用户服务。

```bash
openclaw node install --host <gateway-host> --port 18789
```

选项：

- `--host <host>`: 网关 WebSocket 主机（默认：`127.0.0.1`）
- `--port <port>`: 网关 WebSocket 端口（默认：`18789`）
- `--tls`: 使用 TLS 进行网关连接
- `--tls-fingerprint <sha256>`: 预期的 TLS 证书指纹（sha256）
- `--node-id <id>`: 覆盖节点 ID（清除配对令牌）
- `--display-name <name>`: 覆盖节点显示名称
- `--runtime <runtime>`: 服务运行时 (`node` 或 `bun`)
- `--force`: 如果已安装则重新安装/覆盖

管理服务：

```bash
openclaw node status
openclaw node stop
openclaw node restart
openclaw node uninstall
```

使用 `openclaw node run` 进行前台节点主机（无服务）。

服务命令接受 `--json` 以获得机器可读输出。

## 配对

第一次连接会在网关上创建一个待处理的节点配对请求。
通过以下方式批准：

```bash
openclaw nodes pending
openclaw nodes approve <requestId>
```

节点主机在其节点 ID、令牌、显示名称和网关连接信息存储在
`~/.openclaw/node.json` 中。

## Exec 批准

`system.run` 受本地 exec 批准的限制：

- `~/.openclaw/exec-approvals.json`
- [Exec 批准](/tools/exec-approvals)
- `openclaw approvals --node <id|name|ip>`（从网关编辑）