---
summary: "OpenClaw Gateway CLI (`openclaw gateway`) — run, query, and discover gateways"
read_when:
  - Running the Gateway from the CLI (dev or servers)
  - Debugging Gateway auth, bind modes, and connectivity
  - Discovering gateways via Bonjour (LAN + tailnet)
title: "gateway"
---
# 网关 CLI

网关是 OpenClaw 的 WebSocket 服务器（通道、节点、会话、钩子）。

本页中的子命令位于 `openclaw gateway …` 下。

相关文档：

- [/gateway/bonjour](/gateway/bonjour)
- [/gateway/discovery](/gateway/discovery)
- [/gateway/configuration](/gateway/configuration)

## 运行网关

运行本地网关进程：

```bash
openclaw gateway
```

前台别名：

```bash
openclaw gateway run
```

注意事项：

- 默认情况下，除非在 `~/.openclaw/openclaw.json` 中设置了 `gateway.mode=local`，否则网关拒绝启动。使用 `--allow-unconfigured` 用于临时/开发运行。
- 未授权的绑定到环回接口以外的地址会被阻止（安全护栏）。
- `SIGUSR1` 在授权后会触发进程内重启（启用 `commands.restart` 或使用网关工具/配置应用/更新）。
- `SIGINT`/`SIGTERM` 处理程序会停止网关进程，但不会恢复任何自定义终端状态。如果你用 TUI 或原始模式输入包装 CLI，请在退出前恢复终端。

### 选项

- `--port <端口>`：WebSocket 端口（默认来自配置/环境；通常为 `18789`）。
- `--bind <loopback|lan|tailnet|auto|custom>`：监听绑定模式。
- `--auth <token|password>`：认证模式覆盖。
- `--token <token>`：令牌覆盖（同时设置进程的 `OPENCLAW_GATEWAY_TOKEN`）。
- `--password <password>`：密码覆盖（同时设置进程的 `OPENCLAW_GATEWAY_PASSWORD`）。
- `--tailscale <off|serve|funnel>`：通过 Tailscale 暴露网关。
- `--tailscale-reset-on-exit`：在关闭时重置 Tailscale serve/funnel 配置。
- `--allow-unconfigured`：允许在配置中不设置 `gateway.mode=local` 时启动网关。
- `--dev`：如果缺失则创建开发配置 + 工作区（跳过 BOOTSTRAP.md）。
- `--reset`：重置开发配置 + 凭据 + 会话 + 工作区（需要 `--dev`）。
- `--force`：在启动前强制终止选定端口上的任何现有监听器。
- `--verbose`：详细日志。
- `--claude-cli-logs`：仅在控制台显示 claude-cli 日志（并启用其 stdout/stderr）。
- `--ws-log <auto|full|compact>`：WebSocket 日志样式（默认 `auto`）。
- `--compact`：`--ws-log compact` 的别名。
- `--raw-stream`：将原始模型流事件记录到 jsonl。
- `--raw-stream-path <路径>`：原始流 jsonl 路径。

## 查询正在运行的网关

所有查询命令均使用 WebSocket RPC。

输出模式：

- 默认：人类可读（TTY 中带颜色）。
- `--json`：机器可读 JSON（无样式/加载动画）。
- `--no-color`（或 `NO_COLOR=1`）：禁用 ANSI 而保留人类布局。

支持的共享选项（如适用）：

- `--url <url>`：网关 WebSocket URL。
- `--token <token>`：网关令牌。
- `--password <password>`：网关密码。
- `--timeout <ms>`：超时/预算（因命令而异）。
- `--expect-final`：等待“最终”响应（代理调用）。

### `gateway health`

```bash
openclaw gateway health --url ws://127.0.0.1:18789
```

### `gateway status`

`gateway status` 显示网关服务（launchd/systemd/schtasks）以及一个可选的 RPC 探针。

```bash
openclaw gateway status
openclaw gateway status --json
```

选项：

- `--url <url>`：覆盖探针 URL。
- `--token <token>`：探针的令牌认证。
- `--password <password>`：探针的密码认证。
- `--timeout <ms>`：探针超时（默认 `10000`）。
- `--no-probe`：跳过 RPC 探针（仅服务视图）。
- `--deep`：扫描系统级服务。

### `gateway probe`

`gateway probe` 是“调试一切”的命令。它始终会探测：

- 您配置的远程网关（如果设置），以及
- 本地主机（环回）**即使远程已配置**。

如果多个网关可达，它会打印所有。当使用隔离的配置文件/端口（例如救援机器人）时，支持多个网关，但大多数安装仍运行单个网关。

```bash
openclaw gateway probe
openclaw gateway probe --json
```

#### 通过 SSH 远程（Mac 应用对齐）

macOS 应用“通过 SSH 远程”模式使用本地端口转发，使得可能仅绑定到环回的远程网关在 `ws://127.0.0.1:<端口>` 可达。

CLI 等效命令：

```bash
openclaw gateway probe --ssh user@gateway-host
```

选项：

- `--ssh <目标>`：`user@host` 或 `user@host:port`（端口默认为 `22`）。
- `--ssh-identity <路径>`：身份文件。
- `--ssh-auto`：选择第一个发现的网关主机作为 SSH 目标（仅限 LAN/WAB）。

配置（可选，用作默认值）：

- `gateway.remote.sshTarget`
- `gateway.remote.sshIdentity`

### `gateway call <方法>`

低级 RPC 辅助工具。

```bash
openclaw gateway call status
openclaw gateway call logs.tail --params '{"sinceMs": 60000}'
```

## 管理网关服务

```bash
openclaw gateway install
openclaw gateway start
openclaw gateway stop
openclaw gateway restart