---
summary: "CLI reference for `openclaw node` (headless node host)"
read_when:
  - Running the headless node host
  - Pairing a non-macOS node for system.run
title: "node"
---
# `openclaw node`

运行一个连接到 **Gateway WebSocket** 的 **headless Node Host** 并在本机上暴露
`system.run` / `system.which`。

## 为什么要使用 Node Host？

当您希望代理在您的网络中的其他机器上 **运行命令**，而无需在那里安装完整的 macOS 配套应用时，请使用 Node Host。

常见用例：

- 在远程 Linux/Windows 机器上运行命令（构建服务器、实验室机器、NAS）。
- 保持 Exec **沙盒化**在 Gateway 上，但将批准的运行委托给其他主机。
- 为自动化或 CI 节点提供轻量级、无头的执行目标。

执行仍然受到 **Exec 审批** 和 Node Host 上的每代理白名单的保护，因此您可以使命令访问范围受限且明确。

## 浏览器代理（零配置）

如果节点上未禁用 `browser.enabled`，Node Host 会自动广播浏览器代理。这允许代理在该节点上使用浏览器自动化，而无需额外配置。

默认情况下，代理暴露节点的常规浏览器配置文件表面。如果您设置 `nodeHost.browserProxy.allowProfiles`，代理将变得严格：
非白名单配置文件目标将被拒绝，并且通过代理的持久化配置文件创建/删除路由将被阻止。

如果需要，请在节点上禁用它：

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

- `--host <host>`: Gateway WebSocket 主机（默认值：`127.0.0.1`）
- `--port <port>`: Gateway WebSocket 端口（默认值：`18789`）
- `--tls`: 为 Gateway 连接使用 TLS
- `--tls-fingerprint <sha256>`: 预期的 TLS 证书指纹 (sha256)
- `--node-id <id>`: 覆盖节点 ID（清除配对令牌）
- `--display-name <name>`: 覆盖节点显示名称

## Node Host 的 Gateway 认证

`openclaw node run` 和 `openclaw node install` 从配置/环境变量解析 Gateway 认证（节点命令上没有 `--token`/`--password` 标志）：

- 首先检查 `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`。
- 然后回退到本地配置：`gateway.auth.token` / `gateway.auth.password`。
- 在本地模式下，Node Host 有意不继承 `gateway.remote.token` / `gateway.remote.password`。
- 如果 `gateway.auth.token` / `gateway.auth.password` 通过 SecretRef 显式配置但未解析，节点认证解析将失败即关闭（无远程回退掩盖）。
- 在 `gateway.mode=remote` 中，远程客户端字段 (`gateway.remote.token` / `gateway.remote.password`) 也根据远程优先级规则适用。
- 节点主机认证解析仅遵循 `OPENCLAW_GATEWAY_*` 环境变量。

## 服务（后台）

将无头 Node Host 安装为用户服务。

```bash
openclaw node install --host <gateway-host> --port 18789
```

选项：

- `--host <host>`: Gateway WebSocket 主机（默认值：`127.0.0.1`）
- `--port <port>`: Gateway WebSocket 端口（默认值：`18789`）
- `--tls`: 为 Gateway 连接使用 TLS
- `--tls-fingerprint <sha256>`: 预期的 TLS 证书指纹 (sha256)
- `--node-id <id>`: 覆盖节点 ID（清除配对令牌）
- `--display-name <name>`: 覆盖节点显示名称
- `--runtime <runtime>`: 服务运行时（`node` 或 `bun`）
- `--force`: 如果已安装则重新安装/覆盖

管理服务：

```bash
openclaw node status
openclaw node stop
openclaw node restart
openclaw node uninstall
```

对于前台 Node Host（无服务），请使用 `openclaw node run`。

服务命令接受 `--json` 用于机器可读输出。

## 配对

首次连接会在 Gateway 上创建一个待处理的设备配对请求 (`role: node`)。
通过以下方式批准：

```bash
openclaw devices list
openclaw devices approve <requestId>
```

如果节点使用更改的认证详细信息（角色/作用域/公钥）重试配对，
先前的待处理请求将被取代，并创建新的 `requestId`。
批准前请再次运行 `openclaw devices list`。

Node Host 将其节点 ID、令牌、显示名称和 Gateway 连接信息存储在
`~/.openclaw/node.json` 中。

## Exec 审批

`system.run` 受本地 Exec 审批限制：

- `~/.openclaw/exec-approvals.json`
- [Exec 审批](/tools/exec-approvals)
- `openclaw approvals --node <id|name|ip>`（从 Gateway 编辑）

对于已批准的异步节点 Exec，OpenClaw 准备一个标准的 `systemRunPlan`
在提示之前。稍后批准的 `system.run` 转发重用该存储的
计划，因此在批准请求创建后对 command/cwd/session 字段的编辑将被拒绝，而不是更改节点执行的內容。