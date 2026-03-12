---
summary: "Runbook for the Gateway service, lifecycle, and operations"
read_when:
  - Running or debugging the gateway process
title: "Gateway Runbook"
---
# 网关运行手册

使用本页面进行网关服务的首日启动（day-1）和日常运维（day-2）。

<CardGroup cols={2}>
  <Card title="深度排障" icon="siren" href="/gateway/troubleshooting">
    基于症状的诊断流程，含精确的命令执行序列与日志特征标识。
  </Card>
  <Card title="配置" icon="sliders" href="/gateway/configuration">
    面向任务的配置指南 + 完整配置项参考。
  </Card>
  <Card title="密钥管理" icon="key-round" href="/gateway/secrets">
    SecretRef 协议约定、运行时快照行为，以及迁移/重载操作。
  </Card>
  <Card title="密钥计划协议" icon="shield-check" href="/gateway/secrets-plan-contract">
    精确的 `secrets apply` 目标/路径规则，以及仅引用（ref-only）认证配置文件的行为。
  </Card>
</CardGroup>

## 5 分钟本地快速启动

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

- 一个常驻进程，负责路由、控制平面及通道连接。
- 单一复用端口承载以下全部功能：
  - WebSocket 控制/RPC
  - HTTP API（兼容 OpenAI、响应、工具调用）
  - 控制 UI 与钩子（hooks）
- 默认绑定模式：`loopback`。
- 默认启用认证（需提供 `gateway.auth.token` / `gateway.auth.password`，或 `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`）。

### 端口与绑定优先级

| 设置         | 解析顺序                                                      |
| ------------ | ------------------------------------------------------------- |
| 网关端口     | `--port` → `OPENCLAW_GATEWAY_PORT` → `gateway.port` → `18789` |
| 绑定模式     | CLI/覆盖参数 → `gateway.bind` → `loopback`                    |

### 热重载模式

| `gateway.reload.mode` | 行为                                   |
| --------------------- | ------------------------------------------ |
| `off`                 | 不重新加载配置                           |
| `hot`                 | 仅应用热安全（hot-safe）变更                |
| `restart`             | 在需重启的变更发生时执行重启               |
| `hybrid`（默认）    | 安全时热应用，必要时重启                   |

## 运维人员命令集

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

首选方式：Tailscale / VPN。  
备用方式：SSH 隧道。

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

然后在本地将客户端连接至 `ws://127.0.0.1:18789`。

<Warning>
If gateway auth is configured, clients still must send auth (__CODE_BLOCK_27__/__CODE_BLOCK_28__) even over SSH tunnels.
</Warning>

参见：[远程网关](/gateway/remote)、[认证](/gateway/authentication)、[Tailscale](/gateway/tailscale)。

## 监控与服务生命周期管理

请使用受监控（supervised）方式运行，以获得类生产环境的可靠性。

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

## 单主机部署多个网关

大多数场景应仅运行 **一个** 网关。  
仅在需要严格隔离或冗余（例如救援配置文件）时才部署多个网关。

每个实例须满足以下检查清单：

- 独一无二的 `gateway.port`
- 独一无二的 `OPENCLAW_CONFIG_PATH`
- 独一无二的 `OPENCLAW_STATE_DIR`
- 独一无二的 `agents.defaults.workspace`

示例：

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json OPENCLAW_STATE_DIR=~/.openclaw-a openclaw gateway --port 19001
OPENCLAW_CONFIG_PATH=~/.openclaw/b.json OPENCLAW_STATE_DIR=~/.openclaw-b openclaw gateway --port 19002
```

参见：[多个网关](/gateway/multiple-gateways)。

### 开发配置快速路径

```bash
openclaw --dev setup
openclaw --dev gateway --allow-unconfigured
openclaw --dev status
```

默认包含隔离的状态/配置，以及基础网关端口 `19001`。

## 协议速查表（运维视角）

- 客户端首个帧必须为 `connect`。
- 网关返回 `hello-ok` 快照（含 `presence`、`health`、`stateVersion`、`uptimeMs` 及配额/策略）。
- 请求流程：`req(method, params)` → `res(ok/payload|error)`。
- 常见事件：`connect.challenge`、`agent`、`chat`、`presence`、`tick`、`health`、`heartbeat`、`shutdown`。

Agent 执行分为两个阶段：

1. 即时接受确认（ack）(`status:"accepted"`)
2. 最终完成响应 (`status:"ok"|"error"`)，其间流式传输 `agent` 类型事件。

详见完整协议文档：[网关协议](/gateway/protocol)。

## 运维检查项

### 存活性（Liveness）

- 建立 WebSocket 连接并发送 `connect`。
- 期望收到含快照的 `hello-ok` 响应。

### 就绪性（Readiness）

```bash
openclaw gateway status
openclaw channels status --probe
openclaw health
```

### 断连恢复（Gap recovery）

事件不可重放。若检测到序列断连，请先刷新状态（`health`、`system-presence`），再继续后续操作。

## 常见故障特征

| 特征                                                      | 最可能的问题                             |
| -------------------------------------------------------------- | ---------------------------------------- |
| `refusing to bind gateway ... without auth`                    | 非回环地址绑定但未提供 token/password     |
| `another gateway instance is already listening` / `EADDRINUSE` | 端口冲突                                |
| `Gateway start blocked: set gateway.mode=local`                | 配置误设为远程模式                        |
| `unauthorized` 在连接期间发生                                  | 客户端与网关间认证不匹配                  |

如需完整的诊断流程，请查阅 [网关排障指南](/gateway/troubleshooting)。

## 安全保障

- 当网关不可用时，网关协议客户端会快速失败（无隐式直连通道回退）。
- 对无效或无法建立连接的首帧，网关将拒绝并关闭连接。
- 优雅关闭前会发出 `shutdown` 事件，随后关闭 socket。

---

相关文档：

- [排障指南](/gateway/troubleshooting)
- [后台进程](/gateway/background-process)
- [配置](/gateway/configuration)
- [健康检查](/gateway/health)
- [诊断工具（Doctor）](/gateway/doctor)
- [认证](/gateway/authentication)