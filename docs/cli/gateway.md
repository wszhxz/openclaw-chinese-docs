---
summary: "OpenClaw Gateway CLI (`openclaw gateway`) — run, query, and discover gateways"
read_when:
  - Running the Gateway from the CLI (dev or servers)
  - Debugging Gateway auth, bind modes, and connectivity
  - Discovering gateways via Bonjour (LAN + tailnet)
title: "gateway"
---
# 网关 CLI

网关是 OpenClaw 的 WebSocket 服务器（用于频道、节点、会话和钩子）。

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

- 默认情况下，除非在 `~/.openclaw/openclaw.json` 中设置了 `gateway.mode=local`，否则网关拒绝启动。可使用 `--allow-unconfigured` 进行临时/开发用途的运行。
- 在未启用认证的情况下绑定到回环地址以外的地址将被阻止（安全防护措施）。
- `SIGUSR1` 在获得授权时触发进程内重启（默认启用 `commands.restart`；设置 `commands.restart: false` 可禁止手动重启，但网关工具/配置应用/更新仍被允许）。
- `SIGINT`/`SIGTERM` 处理器会终止网关进程，但不会恢复任何自定义终端状态。如果您使用 TUI 或原始模式输入封装了 CLI，请在退出前恢复终端状态。

### 选项

- `--port <port>`：WebSocket 端口（默认值来自配置/环境变量；通常为 `18789`）。
- `--bind <loopback|lan|tailnet|auto|custom>`：监听器绑定模式。
- `--auth <token|password>`：认证模式覆盖。
- `--token <token>`：令牌覆盖（同时为该进程设置 `OPENCLAW_GATEWAY_TOKEN`）。
- `--password <password>`：密码覆盖。警告：内联密码可能在本地进程列表中暴露。
- `--password-file <path>`：从文件读取网关密码。
- `--tailscale <off|serve|funnel>`：通过 Tailscale 暴露网关。
- `--tailscale-reset-on-exit`：关闭时重置 Tailscale serve/funnel 配置。
- `--allow-unconfigured`：允许在配置中缺少 `gateway.mode=local` 的情况下启动网关。
- `--dev`：若缺失则创建开发配置 + 工作区（跳过 BOOTSTRAP.md）。
- `--reset`：重置开发配置 + 凭据 + 会话 + 工作区（需要 `--dev`）。
- `--force`：启动前先终止选定端口上已存在的任何监听器。
- `--verbose`：详细日志。
- `--claude-cli-logs`：仅在控制台中显示 claude-cli 日志（并启用其 stdout/stderr）。
- `--ws-log <auto|full|compact>`：WebSocket 日志样式（默认为 `auto`）。
- `--compact`：`--ws-log compact` 的别名。
- `--raw-stream`：将原始模型流事件记录为 jsonl 格式。
- `--raw-stream-path <path>`：原始流 jsonl 文件路径。

## 查询正在运行的网关

所有查询命令均使用 WebSocket RPC。

输出模式：

- 默认：人类可读格式（在 TTY 中带颜色）。
- `--json`：机器可读 JSON 格式（无样式/进度指示器）。
- `--no-color`（或 `NO_COLOR=1`）：禁用 ANSI 转义序列，但保留人类可读布局。

共享选项（在支持处）：

- `--url <url>`：网关 WebSocket URL。
- `--token <token>`：网关令牌。
- `--password <password>`：网关密码。
- `--timeout <ms>`：超时/预算（因命令而异）。
- `--expect-final`：等待“最终”响应（代理调用）。

注意：当您设置了 `--url` 后，CLI 不会回退至配置或环境变量中的凭据。  
请显式传入 `--token` 或 `--password`。缺少显式凭据将报错。

### `gateway health`

```bash
openclaw gateway health --url ws://127.0.0.1:18789
```

### `gateway status`

`gateway status` 显示网关服务（launchd/systemd/schtasks）以及一个可选的 RPC 探测。

```bash
openclaw gateway status
openclaw gateway status --json
```

选项：

- `--url <url>`：覆盖探测 URL。
- `--token <token>`：探测使用的令牌认证。
- `--password <password>`：探测使用的密码认证。
- `--timeout <ms>`：探测超时（默认为 `10000`）。
- `--no-probe`：跳过 RPC 探测（仅显示服务视图）。
- `--deep`：也扫描系统级服务。

注意事项：

- `gateway status` 在可能时解析已配置的认证 SecretRefs 以用于探测认证。
- 如果在此命令路径中某个必需的认证 SecretRef 未能解析，则探测认证可能失败；请显式传入 `--token`/`--password`，或先解析密钥源。
- 在 Linux systemd 安装中，服务认证漂移检查会从单元文件中读取 `Environment=` 和 `EnvironmentFile=` 的值（包括 `%h`、带引号的路径、多个文件，以及可选的 `-` 文件）。

### `gateway probe`

`gateway probe` 是“调试一切”的命令。它始终执行以下探测：

- 您所配置的远程网关（如果已设置），以及  
- 本地主机（回环）**即使已配置远程网关**。

如果可访问多个网关，它将全部打印出来。当您使用隔离的配置文件/端口（例如救援机器人）时，支持多个网关，但大多数安装仍只运行单个网关。

```bash
openclaw gateway probe
openclaw gateway probe --json
```

#### 通过 SSH 远程连接（与 macOS 应用功能对等）

macOS 应用的“通过 SSH 远程连接”模式使用本地端口转发，使远程网关（可能仅绑定到回环地址）可在 `ws://127.0.0.1:<port>` 访问。

CLI 等效命令：

```bash
openclaw gateway probe --ssh user@gateway-host
```

选项：

- `--ssh <target>`：`user@host` 或 `user@host:port`（端口默认为 `22`）。
- `--ssh-identity <path>`：身份验证文件。
- `--ssh-auto`：选取首个发现的网关主机作为 SSH 目标（仅限局域网/WAB）。

配置（可选，用作默认值）：

- `gateway.remote.sshTarget`
- `gateway.remote.sshIdentity`

### `gateway call <method>`

底层 RPC 辅助命令。

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
openclaw gateway uninstall
```

注意事项：

- `gateway install` 支持 `--port`、`--runtime`、`--token`、`--force`、`--json`。
- 当令牌认证需要令牌且 `gateway.auth.token` 由 SecretRef 管理时，`gateway install` 将验证该 SecretRef 是否可解析，但不会将已解析的令牌持久化到服务环境元数据中。
- 若令牌认证需要令牌，而所配置的令牌 SecretRef 无法解析，则安装将失败（而非持久化回退的明文令牌）。
- 对于 `gateway run` 上的密码认证，建议优先使用 `OPENCLAW_GATEWAY_PASSWORD`、`--password-file`，或由 SecretRef 支持的 `gateway.auth.password`，而非内联的 `--password`。
- 在推断认证模式下，仅限 shell 的 `OPENCLAW_GATEWAY_PASSWORD`/`CLAWDBOT_GATEWAY_PASSWORD` 并不会放宽安装令牌要求；在安装托管服务时，请使用持久化配置（`gateway.auth.password` 或配置中的 `env`）。
- 若同时配置了 `gateway.auth.token` 和 `gateway.auth.password`，且未设置 `gateway.auth.mode`，则安装将被阻塞，直至显式设置模式。
- 生命周期命令接受 `--json` 以支持脚本编写。

## 发现网关（Bonjour）

`gateway discover` 扫描网关信标（`_openclaw-gw._tcp`）。

- 组播 DNS-SD：`local.`  
- 单播 DNS-SD（广域 Bonjour）：选择一个域名（示例：`openclaw.internal.`），并设置分隔 DNS + DNS 服务器；参见 [/gateway/bonjour](/gateway/bonjour)

仅启用 Bonjour 发现（默认启用）的网关才会广播该信标。

广域发现记录包含（TXT）：

- `role`（网关角色提示）  
- `transport`（传输提示，例如 `gateway`）  
- `gatewayPort`（WebSocket 端口，通常为 `18789`）  
- `sshPort`（SSH 端口；若未提供则默认为 `22`）  
- `tailnetDns`（MagicDNS 主机名，如可用）  
- `gatewayTls` / `gatewayTlsSha256`（启用 TLS + 证书指纹）  
- `cliPath`（远程安装的可选提示）

### `gateway discover`

```bash
openclaw gateway discover
```

选项：

- `--timeout <ms>`：每个命令的超时（浏览/解析）；默认为 `2000`。  
- `--json`：机器可读输出（同时也禁用样式/进度指示器）。

示例：

```bash
openclaw gateway discover --timeout 4000
openclaw gateway discover --json | jq '.beacons[].wsUrl'
```