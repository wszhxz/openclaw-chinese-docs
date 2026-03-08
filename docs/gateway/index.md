---
summary: "Runbook for the Gateway service, lifecycle, and operations"
read_when:
  - Running or debugging the gateway process
title: "Gateway Runbook"
---
# Gateway 运行手册

本页用于 Gateway 服务的首日启动和次日运营操作。

<CardGroup cols={2}>
  <Card title="深度故障排查" icon="siren" href="/gateway/troubleshooting">
    以症状为先的诊断，包含精确的命令阶梯和日志特征。
  </Card>
  <Card title="配置" icon="sliders" href="/gateway/configuration">
    面向任务的设置指南 + 完整配置参考。
  </Card>
  <Card title="密钥管理" icon="key-round" href="/gateway/secrets">
    SecretRef 契约、运行时快照行为以及迁移/重载操作。
  </Card>
  <Card title="密钥计划契约" icon="shield-check" href="/gateway/secrets-plan-contract">
    精确的 `secrets apply` 目标/路径规则和仅引用的 auth-profile 行为。
  </Card>
</CardGroup>

## 5 分钟本地启动

<Steps>
  <Step title="Start the Gateway">

__CODE_BLOCK_1__

  </Step>

  <Step title="Verify service health">

__CODE_BLOCK_2__

Healthy baseline: __CODE_BLOCK_3__ and __CODE_BLOCK_4__.

  </Step>

  <Step title="Validate channel readiness">

__CODE_BLOCK_5__

  </Step>
</Steps>

<Note>
Gateway config reload watches the active config file path (resolved from profile/state defaults, or __CODE_BLOCK_6__ when set).
Default mode is __CODE_BLOCK_7__.
</Note>

## 运行时模型

- 一个用于路由、控制平面和通道连接的常驻进程。
- 单个复用端口用于：
  - WebSocket control/RPC
  - HTTP APIs（OpenAI 兼容、Responses、tools invoke）
  - 控制 UI 和 hooks
- 默认绑定模式：`loopback`。
- 默认需要认证（`gateway.auth.token` / `gateway.auth.password`，或 `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`）。

### 端口和绑定优先级

| 设置      | 解析顺序                                              |
| ------------ | ------------------------------------------------------------- |
| Gateway 端口 | `--port` → `OPENCLAW_GATEWAY_PORT` → `gateway.port` → `18789` |
| 绑定模式    | CLI/override → `gateway.bind` → `loopback`                    |

### 热重载模式

| `gateway.reload.mode` | 行为                                   |
| --------------------- | ------------------------------------------ |
| `off`                 | 不重载配置                           |
| `hot`                 | 仅应用热安全更改                |
| `restart`             | 需要重载的更改时重启         |
| `hybrid` (默认)    | 安全时热应用，需要时重启 |

## 操作员命令集

```bash
openclaw gateway status
openclaw gateway status --deep
openclaw gateway status --json
openclaw gateway install
openclaw gateway restart
openclaw gateway stop
openclaw secrets reload
openclaw logs --follow
openclaw doctor
```

## 远程访问

首选：Tailscale/VPN。
备选：SSH 隧道。

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

然后在本地将客户端连接到 `ws://127.0.0.1:18789`。

<Warning>
If gateway auth is configured, clients still must send auth (__CODE_BLOCK_27__/__CODE_BLOCK_28__) even over SSH tunnels.
</Warning>

参见：[远程 Gateway](/gateway/remote), [认证](/gateway/authentication), [Tailscale](/gateway/tailscale)。

## 监管和服务生命周期

使用受监管的运行以获得类似生产环境的可靠性。

<Tabs>
  <Tab title="macOS (launchd)">

__CODE_BLOCK_29__

LaunchAgent labels are __CODE_BLOCK_30__ (default) or __CODE_BLOCK_31__ (named profile). __CODE_BLOCK_32__ audits and repairs service config drift.

  </Tab>

  <Tab title="Linux (systemd user)">

__CODE_BLOCK_33__

For persistence after logout, enable lingering:

__CODE_BLOCK_34__

  </Tab>

  <Tab title="Linux (system service)">

Use a system unit for multi-user/always-on hosts.

__CODE_BLOCK_35__

  </Tab>
</Tabs>

## 一台主机上的多个 Gateway

大多数设置应运行 **一个** Gateway。
仅在需要严格隔离/冗余时使用多个（例如救援配置文件）。

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

参见：[多个 Gateway](/gateway/multiple-gateways)。

### 开发配置文件快速路径

```bash
openclaw --dev setup
openclaw --dev gateway --allow-unconfigured
openclaw --dev status
```

默认包括隔离的状态/配置和基础 Gateway 端口 `19001`。

## 协议快速参考（操作员视图）

- 第一个客户端帧必须是 `connect`。
- Gateway 返回 `hello-ok` 快照（`presence`、`health`、`stateVersion`、`uptimeMs`、limits/policy）。
- 请求：`req(method, params)` → `res(ok/payload|error)`。
- 常见事件：`connect.challenge`、`agent`、`chat`、`presence`、`tick`、`health`、`heartbeat`、`shutdown`。

Agent 运行分为两个阶段：

1. 立即接受的 ack (`status:"accepted"`)
2. 最终完成响应 (`status:"ok"|"error"`)，中间流式传输 `agent` 事件。

参见完整协议文档：[Gateway 协议](/gateway/protocol)。

## 操作检查

### 存活状态

- 打开 WS 并发送 `connect`。
- 期望带有快照的 `hello-ok` 响应。

### 就绪状态

```bash
openclaw gateway status
openclaw channels status --probe
openclaw health
```

### 间隙恢复

事件不会重放。出现序列间隙时，在继续之前刷新状态（`health`、`system-presence`）。

## 常见故障特征

| 特征                                                      | 可能的问题                             |
| -------------------------------------------------------------- | ---------------------------------------- |
| `refusing to bind gateway ... without auth`                    | 非回环绑定且无 token/password |
| `another gateway instance is already listening` / `EADDRINUSE` | 端口冲突                            |
| `Gateway start blocked: set gateway.mode=local`                | 配置设置为远程模式                |
| 连接期间 `unauthorized`                                  | 客户端和 Gateway 之间的认证不匹配 |

如需完整诊断阶梯，请使用 [Gateway 故障排查](/gateway/troubleshooting)。

## 安全保证

- 当 Gateway 不可用时，Gateway 协议客户端会快速失败（无隐式直接通道回退）。
- 无效/非连接的第一个帧会被拒绝并关闭。
- 优雅关闭会在 socket 关闭之前发出 `shutdown` 事件。

---

相关内容：

- [故障排查](/gateway/troubleshooting)
- [后台进程](/gateway/background-process)
- [配置](/gateway/configuration)
- [健康状态](/gateway/health)
- [Doctor](/gateway/doctor)
- [认证](/gateway/authentication)