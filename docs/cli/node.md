---
summary: "CLI reference for `openclaw node` (headless node host)"
read_when:
  - Running the headless node host
  - Pairing a non-macOS node for system.run
title: "node"
---
# `openclaw 节点`

运行一个**无头节点主机**，该主机连接到网关 WebSocket 并在此机器上暴露 `system.run` / `system.which` 功能。

## 为何使用节点主机？

当您希望代理在**网络中的其他机器上运行命令**，而无需在这些机器上安装完整的 macOS 伴侣应用时，使用节点主机。

常见使用场景：

- 在远程 Linux/Windows 机器（构建服务器、实验室机器、NAS）上运行命令。
- 在网关上保持执行**沙盒化**，但将已批准的运行委托给其他主机。
- 为自动化或 CI 节点提供一个轻量级、无头的执行目标。

执行仍受**执行审批**和节点主机上的每个代理允许列表保护，因此您可以将命令访问权限限制并明确化。

## 浏览器代理（零配置）

如果节点未禁用 `browser.enabled`，节点主机将自动发布一个浏览器代理。这使得代理可以在该节点上使用浏览器自动化，而无需额外配置。

如需禁用它：

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
openclaw node run --host <网关主机> --port 18789
```

选项：

- `--host <主机>`：网关 WebSocket 主机（默认：`127.0.0.1`）
- `--port <端口>`：网关 WebSocket 端口（默认：`18789`）
- `--tls`：使用 TLS 连接网关
- `--tls-fingerprint <sha256>`：预期的 TLS 证书指纹（sha256）
- `--node-id <ID>`：覆盖节点 ID（清除配对令牌）
- `--display-name <名称>`：覆盖节点显示名称

## 服务（后台）

将无头节点主机安装为用户服务。

```bash
openclaw node install --host <网关主机> --port 18789
```

选项：

- `--host <主机>`：网关 WebSocket 主机（默认：`127.0.0.1`）
- `--port <端口>`：网关 WebSocket 端口（默认：`18789`）
- `--tls`：使用 TLS 连接网关
- `--tls-fingerprint <sha256>`：预期的 TLS 证书指纹（sha256）
- `--node-id <ID>`：覆盖节点 ID（清除配对令牌）
- `--display-name <名称>`：覆盖节点显示名称
- `--runtime <运行时>`：服务运行时（`node` 或 `bun`）
- `--force`：如果已安装则重新安装/覆盖

管理服务：

```bash
openclaw node status
openclaw node stop
openclaw node restart
openclaw node uninstall
```

使用 `openclaw node run` 运行前台节点主机（无服务）。

服务命令支持 `--json` 参数以获取机器可读的输出。

## 配对

首次连接会在网关上创建一个待审批的节点配对请求。通过以下命令批准：

```bash
openclaw nodes pending
openclaw nodes approve <请求ID>
```

节点主机将节点 ID、令牌、显示名称和网关连接信息存储在 `~/.openclaw/node.json` 中。

## 执行审批

`system.run` 由本地执行审批控制：

- `~/.openclaw/exec-approvals.json`
- [执行审批](/tools/exec-approvals)
- `openclaw approvals --node <ID|名称|IP>`（从网关编辑）