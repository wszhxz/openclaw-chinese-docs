---
summary: "Runbook for the Gateway service, lifecycle, and operations"
read_when:
  - Running or debugging the gateway process
title: "Gateway Runbook"
---
# Gateway 运行手册

使用此页面进行 Gateway 服务的初始启动和日常运维。

<CardGroup cols={2}>
  <Card title="深入故障排除" icon="siren" href="/gateway/troubleshooting">
    以症状为导向的诊断，包含精确的命令步骤和日志签名。
  </Card>
  <Card title="配置" icon="sliders" href="/gateway/configuration">
    任务导向的设置指南 + 完整的配置参考。
  </Card>
</CardGroup>

## 5分钟本地启动

<Steps>
  <Step title="Start the Gateway">

__CODE_BLOCK_0__

  </Step>

  <Step title="Verify service health">

__CODE_BLOCK_1__

Healthy baseline: __CODE_BLOCK_2__ and __CODE_BLOCK_3__.

  </Step>

  <Step title="Validate channel readiness">

__CODE_BLOCK_4__

  </Step>
</Steps>

<Note>
Gateway config reload watches the active config file path (resolved from profile/state defaults, or __CODE_BLOCK_5__ when set).
Default mode is __CODE_BLOCK_6__.
</Note>

## 运行时模型

- 一个始终运行的进程用于路由、控制平面和通道连接。
- 单个复用端口用于：
  - WebSocket 控制/RPC
  - HTTP API（兼容 OpenAI，响应，工具调用）
  - 控制 UI 和钩子
- 默认绑定模式：`loopback`。
- 默认需要身份验证 (`gateway.auth.token` / `gateway.auth.password`，或 `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`)。

### 端口和绑定优先级

| 设置      | 解析顺序                                              |
| ------------ | ------------------------------------------------------------- |
| Gateway 端口 | `--port` → `OPENCLAW_GATEWAY_PORT` → `gateway.port` → `18789` |
| 绑定模式    | CLI/覆盖 → `gateway.bind` → `loopback`                    |

### 热重载模式

| `gateway.reload.mode` | 行为                                   |
| --------------------- | ------------------------------------------ |
| `off`                 | 不重新加载配置                           |
| `hot`                 | 仅应用热安全更改                |
| `restart`             | 在需要重新加载更改时重启         |
| `hybrid` (默认)    | 当安全时热应用，当需要时重启 |

## 操作员命令集

```bash
openclaw gateway status
openclaw gateway status --deep
openclaw gateway status --json
openclaw gateway install
openclaw gateway restart
openclaw gateway stop
openclaw logs --follow
openclaw doctor
```

## 远程访问

首选：Tailscale/VPN。
备选：SSH 隧道。

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

然后将客户端连接到本地的 `ws://127.0.0.1:18789`。

<Warning>
If gateway auth is configured, clients still must send auth (__CODE_BLOCK_26__/__CODE_BLOCK_27__) even over SSH tunnels.
</Warning>

参见：[远程 Gateway](/gateway/remote)，[身份验证](/gateway/authentication)，[Tailscale](/gateway/tailscale)。

## 监督和服务生命周期

使用受监督的运行以获得类似生产环境的可靠性。

<Tabs>
  <Tab title="macOS (launchd)">

__CODE_BLOCK_28__

LaunchAgent labels are __CODE_BLOCK_29__ (default) or __CODE_BLOCK_30__ (named profile). __CODE_BLOCK_31__ audits and repairs service config drift.

  </Tab>

  <Tab title="Linux (systemd user)">

__CODE_BLOCK_32__

For persistence after logout, enable lingering:

__CODE_BLOCK_33__

  </Tab>

  <Tab title="Linux (system service)">

Use a system unit for multi-user/always-on hosts.

__CODE_BLOCK_34__

  </Tab>
</Tabs>

## 单个主机上的多个网关

大多数设置应运行 **一个** Gateway。
仅在严格的隔离/冗余（例如救援配置文件）时使用多个。

每个实例的检查清单：

- 唯一的 `gateway.port`
- 唯一的 `OPENCLAW_CONFIG_PATH`
- 唯一的 `OPENCLAW_STATE_DIR`
- 唯一的 `agents.defaults.workspace`

示例：

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json OPENCLAW_STATE_DIR=~/.openclaw-a openclaw gateway --port 19001
OPENCLAW_CONFIG_PATH=~/.openclaw/b.json OPENCLAW_STATE_DIR=~/.openclaw-b openclaw gateway --port 19002
```

参见：[多个网关](/gateway/multiple-gateways)。

### 开发配置文件快速路径

```bash
openclaw --dev setup
openclaw --dev gateway --allow-unconfigured
openclaw --dev status
```

默认包括隔离的状态/配置和基础网关端口 `19001`。

## 协议快速参考（操作员视图）

- 第一个客户端帧必须是 `connect`。
- 网关返回 `hello-ok` 快照 (`presence`, `health`, `stateVersion`, `uptimeMs`, 限制/策略)。
- 请求：`req(method, params)` → `res(ok/payload|error)`。
- 常见事件：`connect.challenge`, `agent`, `chat`, `presence`, `tick`, `health`, `heartbeat`, `shutdown`。

代理运行分为两个阶段：

1. 立即接受确认 (`status:"accepted"`)
2. 最终完成响应 (`status:"ok"|"error"`)，中间包含流式的 `agent` 事件。

参见完整协议文档：[网关协议](/gateway/protocol)。

## 运营检查

### 存活性

- 打开 WS 并发送 `connect`。
- 期望带有快照的 `hello-ok` 响应。

### 准备就绪

```bash
openclaw gateway status
openclaw channels status --probe
openclaw health
```

### 缺口恢复

事件不会重放。在序列缺口上，刷新状态 (`health`, `system-presence`) 后再继续。

## 常见故障签名

| 签名                                                      | 可能的问题                             |
| -------------------------------------------------------------- | ---------------------------------------- |
| `refusing to bind gateway ... without auth`                    | 非回环绑定没有令牌/密码 |
| `another gateway instance is already listening` / `EADDRINUSE` | 端口冲突                            |
| `Gateway start blocked: set gateway.mode=local`                | 配置设置为远程模式                |
| `unauthorized` 连接期间                                  | 客户端与网关之间的身份验证不匹配 |

对于完整的诊断步骤，请使用 [网关故障排除](/gateway/troubleshooting)。

## 安全保证

- 当网关不可用时，网关协议客户端会快速失败（没有隐式的直接通道回退）。
- 拒绝并关闭无效/非连接的第一个帧。
- 优雅关闭前发出 `shutdown` 事件。

---

相关：

- [故障排除](/gateway/troubleshooting)
- [后台进程](/gateway/background-process)
- [配置](/gateway/configuration)
- [健康状况](/gateway/health)
- [医生](/gateway/doctor)
- [身份验证](/gateway/authentication)