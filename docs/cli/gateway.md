---
summary: "OpenClaw Gateway CLI (`openclaw gateway`) — run, query, and discover gateways"
read_when:
  - Running the Gateway from the CLI (dev or servers)
  - Debugging Gateway auth, bind modes, and connectivity
  - Discovering gateways via Bonjour (LAN + tailnet)
title: "gateway"
---
# Gateway CLI

Gateway 是 OpenClaw 的 WebSocket 服务器（通道、节点、会话、钩子）。

本页中的子命令位于 `openclaw gateway …` 下。

相关文档：

- [/gateway/bonjour](/gateway/bonjour)
- [/gateway/discovery](/gateway/discovery)
- [/gateway/configuration](/gateway/configuration)

## 运行 Gateway

运行本地 Gateway 进程：

```bash
openclaw gateway
```

前台别名：

```bash
openclaw gateway run
```

注意事项：

- 默认情况下，除非在 `~/.openclaw/openclaw.json` 中设置了 `gateway.mode=local`，否则 Gateway 拒绝启动。使用 `--allow-unconfigured` 进行临时/开发运行。
- 未经身份验证绑定到回环之外被阻止（安全防护措施）。
- 当授权时，`SIGUSR1` 触发进程内重启（启用 `commands.restart` 或使用网关工具/config apply/update）。
- `SIGINT`/`SIGTERM` 处理程序停止网关进程，但不会恢复任何自定义终端状态。如果您用 TUI 或原始模式输入包装 CLI，请在退出前恢复终端。

### 选项

- `--port <port>`: WebSocket 端口（默认来自配置/环境；通常是 `18789`）。
- `--bind <loopback|lan|tailnet|auto|custom>`: 监听绑定模式。
- `--auth <token|password>`: 身份验证模式覆盖。
- `--token <token>`: 令牌覆盖（也设置进程的 `OPENCLAW_GATEWAY_TOKEN`）。
- `--password <password>`: 密码覆盖（也设置进程的 `OPENCLAW_GATEWAY_PASSWORD`）。
- `--tailscale <off|serve|funnel>`: 通过 Tailscale 暴露 Gateway。
- `--tailscale-reset-on-exit`: 关机时重置 Tailscale serve/funnel 配置。
- `--allow-unconfigured`: 允许网关在配置中没有 `gateway.mode=local` 的情况下启动。
- `--dev`: 如果缺少，则创建开发配置 + 工作区（跳过 BOOTSTRAP.md）。
- `--reset`: 重置开发配置 + 凭据 + 会话 + 工作区（需要 `--dev`）。
- `--force`: 启动前终止选定端口上的任何现有监听器。
- `--verbose`: 详细日志。
- `--claude-cli-logs`: 仅在控制台显示 claude-cli 日志（并启用其 stdout/stderr）。
- `--ws-log <auto|full|compact>`: websocket 日志样式（默认 `auto`）。
- `--compact`: `--ws-log compact` 的别名。
- `--raw-stream`: 将原始模型流事件记录到 jsonl。
- `--raw-stream-path <path>`: 原始流 jsonl 路径。

## 查询正在运行的 Gateway

所有查询命令使用 WebSocket RPC。

输出模式：

- 默认：人类可读（TTY 中彩色）。
- `--json`: 机器可读 JSON（无样式/旋转器）。
- `--no-color`（或 `NO_COLOR=1`）：禁用 ANSI 而保持人类布局。

共享选项（如果支持）：

- `--url <url>`: Gateway WebSocket URL。
- `--token <token>`: Gateway 令牌。
- `--password <password>`: Gateway 密码。
- `--timeout <ms>`: 超时/预算（每个命令不同）。
- `--expect-final`: 等待“最终”响应（代理调用）。

### `gateway health`

```bash
openclaw gateway health --url ws://127.0.0.1:18789
```

### `gateway status`

`gateway status` 显示 Gateway 服务（launchd/systemd/schtasks）加上一个可选的 RPC 探测。

```bash
openclaw gateway status
openclaw gateway status --json
```

选项：

- `--url <url>`: 覆盖探测 URL。
- `--token <token>`: 探测的令牌认证。
- `--password <password>`: 探测的密码认证。
- `--timeout <ms>`: 探测超时（默认 `10000`）。
- `--no-probe`: 跳过 RPC 探测（仅服务视图）。
- `--deep`: 扫描系统级服务。

### `gateway probe`

`gateway probe` 是“调试一切”命令。它总是探测：

- 您配置的远程网关（如果已设置），以及
- 本地主机（回环）**即使远程已配置**。

如果有多个网关可达，它会打印所有网关。当您使用隔离的配置文件/端口（例如，救援机器人）时，支持多个网关，但大多数安装仍然只运行一个网关。

```bash
openclaw gateway probe
openclaw gateway probe --json
```

#### 通过 SSH 远程（与 Mac 应用一致）

macOS 应用的“通过 SSH 远程”模式使用本地端口转发，因此远程网关（可能仅绑定到回环）可以在 `ws://127.0.0.1:<port>` 处访问。

CLI 等效：

```bash
openclaw gateway probe --ssh user@gateway-host
```

选项：

- `--ssh <target>`: `user@host` 或 `user@host:port`（端口默认为 `22`）。
- `--ssh-identity <path>`: 标识文件。
- `--ssh-auto`: 选择第一个发现的网关主机作为 SSH 目标（仅 LAN/WAB）。

配置（可选，用作默认值）：

- `gateway.remote.sshTarget`
- `gateway.remote.sshIdentity`

### `gateway call <method>`

低级 RPC 辅助工具。

```bash
openclaw gateway call status
openclaw gateway call logs.tail --params '{"sinceMs": 60000}'
```

## 管理 Gateway 服务

```bash
openclaw gateway install
openclaw gateway start
openclaw gateway stop
openclaw gateway restart
openclaw gateway uninstall
```

注意事项：

- `gateway install` 支持 `--port`，`--runtime`，`--token`，`--force`，`--json`。
- 生命周期命令接受 `--json` 用于脚本编写。

## 发现网关（Bonjour）

`gateway discover` 扫描 Gateway 广播 (`_openclaw-gw._tcp`)。

- 多播 DNS-SD: `local.`
- 单播 DNS-SD（广域 Bonjour）：选择一个域（示例：`openclaw.internal.`）并设置拆分 DNS + DNS 服务器；参见 [/gateway/bonjour](/gateway/bonjour)

仅启用了 Bonjour 发现（默认）的网关才会广播。

广域发现记录包括（TXT）：

- `role`（网关角色提示）
- `transport`（传输提示，例如 `gateway`）
- `gatewayPort`（WebSocket 端口，通常是 `18789`）
- `sshPort`（SSH 端口；如果不存在则默认为 `22`）
- `tailnetDns`（MagicDNS 主机名，如果可用）
- `gatewayTls` / `gatewayTlsSha256`（启用 TLS + 证书指纹）
- `cliPath`（远程安装的可选提示）

### `gateway discover`

```bash
openclaw gateway discover
```

选项：

- `--timeout <ms>`: 每个命令超时（浏览/解析）；默认 `2000`。
- `--json`: 机器可读输出（也禁用样式/旋转器）。

示例：

```bash
openclaw gateway discover --timeout 4000
openclaw gateway discover --json | jq '.beacons[].wsUrl'
```