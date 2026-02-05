---
summary: "Runbook for the Gateway service, lifecycle, and operations"
read_when:
  - Running or debugging the gateway process
title: "Gateway Runbook"
---
# 网关服务运行手册

最后更新时间: 2025-12-09

## 什么是它

- 拥有单个Baileys/Telegram连接和控制/事件平面的常驻进程。
- 替代旧版 `gateway` 命令。CLI入口点: `openclaw gateway`。
- 运行直到停止；在致命错误时退出非零状态码以便监督器重启它。

## 如何运行（本地）

```bash
openclaw gateway --port 18789
# for full debug/trace logs in stdio:
openclaw gateway --port 18789 --verbose
# if the port is busy, terminate listeners then start:
openclaw gateway --force
# dev loop (auto-reload on TS changes):
pnpm gateway:watch
```

- 配置热重载监视 `~/.openclaw/openclaw.json`（或 `OPENCLAW_CONFIG_PATH`）。
  - 默认模式: `gateway.reload.mode="hybrid"`（安全应用更改，关键更改时重启）。
  - 热重载需要时通过 **SIGUSR1** 进行进程内重启。
  - 使用 `gateway.reload.mode="off"` 禁用。
- 将WebSocket控制平面绑定到 `127.0.0.1:<port>`（默认18789）。
- 同一端口还提供HTTP（控制UI、钩子、A2UI）。单端口复用。
  - OpenAI Chat Completions（HTTP）: [`/v1/chat/completions`](/gateway/openai-http-api)。
  - OpenResponses（HTTP）: [`/v1/responses`](/gateway/openresponses-http-api)。
  - Tools Invoke（HTTP）: [`/tools/invoke`](/gateway/tools-invoke-http-api)。
- 默认情况下在 `canvasHost.port`（默认 `18793`）启动Canvas文件服务器，从 `~/.openclaw/workspace/canvas` 提供 `http://<gateway-host>:18793/__openclaw__/canvas/`。使用 `canvasHost.enabled=false` 或 `OPENCLAW_SKIP_CANVAS_HOST=1` 禁用。
- 日志输出到stdout；使用launchd/systemd保持其运行并轮转日志。
- 传递 `--verbose` 以在故障排除时将调试日志（握手、请求/响应、事件）从日志文件镜像到stdio。
- `--force` 使用 `lsof` 在选定端口查找监听器，发送SIGTERM，记录被终止的内容，然后启动网关（如果缺少 `lsof` 则快速失败）。
- 如果在监督器下运行（launchd/systemd/mac应用程序子进程模式），停止/重启通常会发送 **SIGTERM**；较旧的构建可能会将其表现为 `pnpm` `ELIFECYCLE` 退出代码 **143**（SIGTERM），这是正常关闭而不是崩溃。
- **SIGUSR1** 在授权时触发进程内重启（网关工具/配置应用/更新，或启用 `commands.restart` 进行手动重启）。
- 默认情况下需要网关认证：设置 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）或 `gateway.auth.password`。客户端必须发送 `connect.params.auth.token/password` 除非使用Tailscale Serve身份。
- 向导现在默认生成令牌，即使在回环接口上也是如此。
- 端口优先级: `--port` > `OPENCLAW_GATEWAY_PORT` > `gateway.port` > 默认 `18789`。

## 远程访问

- 优先使用Tailscale/VPN；否则使用SSH隧道：
  ```bash
  ssh -N -L 18789:127.0.0.1:18789 user@host
  ```
- 客户端然后通过隧道连接到 `ws://127.0.0.1:18789`。
- 如果配置了令牌，客户端必须在 `connect.params.auth.token` 中包含它，即使通过隧道也是如此。

## 多个网关（同一主机）

通常不需要：一个网关可以服务多个消息通道和代理。仅在冗余或严格隔离的情况下使用多个网关（例如：救援机器人）。

如果隔离状态 + 配置并使用唯一端口，则支持。完整指南：[多个网关](/gateway/multiple-gateways)。

服务名称是配置文件感知的：

- macOS: `bot.molt.<profile>`（旧版 `com.openclaw.*` 可能仍然存在）
- Linux: `openclaw-gateway-<profile>.service`
- Windows: `OpenClaw Gateway (<profile>)`

安装元数据嵌入在服务配置中：

- `OPENCLAW_SERVICE_MARKER=openclaw`
- `OPENCLAW_SERVICE_KIND=gateway`
- `OPENCLAW_SERVICE_VERSION=<version>`

救援机器人模式：保持一个独立的网关，具有自己的配置文件、状态目录、工作区和基本端口间距。完整指南：[救援机器人指南](/gateway/multiple-gateways#rescue-bot-guide)。

### 开发配置文件 (`--dev`)

快速路径：运行一个完全隔离的开发实例（配置/状态/工作区），不干扰您的主要设置。

```bash
openclaw --dev setup
openclaw --dev gateway --allow-unconfigured
# then target the dev instance:
openclaw --dev status
openclaw --dev health
```

默认值（可以通过环境变量/标志/配置覆盖）：

- `OPENCLAW_STATE_DIR=~/.openclaw-dev`
- `OPENCLAW_CONFIG_PATH=~/.openclaw-dev/openclaw.json`
- `OPENCLAW_GATEWAY_PORT=19001`（网关 WS + HTTP）
- 浏览器控制服务端口 = `19003`（派生：`gateway.port+2`，仅限回环）
- `canvasHost.port=19005`（派生：`gateway.port+4`）
- `agents.defaults.workspace` 默认在运行 `setup`/`onboard` 下变为 `~/.openclaw/workspace-dev`。

派生端口（经验法则）：

- 基本端口 = `gateway.port`（或 `OPENCLAW_GATEWAY_PORT` / `--port`）
- 浏览器控制服务端口 = 基本 + 2（仅限回环）
- `canvasHost.port = base + 4`（或 `OPENCLAW_CANVAS_HOST_PORT` / 配置覆盖）
- 浏览器配置文件 CDP 端口从 `browser.controlPort + 9 .. + 108` 自动分配（每个配置文件持久化）。

每个实例的检查清单：

- 唯一的 `gateway.port`
- 唯一的 `OPENCLAW_CONFIG_PATH`
- 唯一的 `OPENCLAW_STATE_DIR`
- 唯一的 `agents.defaults.workspace`
- 分离的 WhatsApp 号码（如果使用 WA）

每个配置文件的服务安装：

```bash
openclaw --profile main gateway install
openclaw --profile rescue gateway install
```

示例：

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json OPENCLAW_STATE_DIR=~/.openclaw-a openclaw gateway --port 19001
OPENCLAW_CONFIG_PATH=~/.openclaw/b.json OPENCLAW_STATE_DIR=~/.openclaw-b openclaw gateway --port 19002
```

## 协议（操作员视图）

- 完整文档：[网关协议](/gateway/protocol) 和 [桥接协议（旧版）](/gateway/bridge-protocol)。
- 客户端必须发送的第一个帧：`req {type:"req", id, method:"connect", params:{minProtocol,maxProtocol,client:{id,displayName?,version,platform,deviceFamily?,modelIdentifier?,mode,instanceId?}, caps, auth?, locale?, userAgent? } }`。
- 网关回复 `res {type:"res", id, ok:true, payload:hello-ok }`（如果有错误则回复 `ok:false`，然后关闭连接）。
- 握手之后：
  - 请求：`{type:"req", id, method, params}` → `{type:"res", id, ok, payload|error}`
  - 事件：`{type:"event", event, payload, seq?, stateVersion?}`
- 结构化在线条目：`{host, ip, version, platform?, deviceFamily?, modelIdentifier?, mode, lastInputSeconds?, ts, reason?, tags?[], instanceId? }`（对于WS客户端，`instanceId` 来自 `connect.client.instanceId`）。
- `agent` 响应是两阶段的：首先 `res` 确认 `{runId,status:"accepted"}`，然后在运行结束后发送最终的 `res` `{runId,status:"ok"|"error",summary}`；流式输出作为 `event:"agent"` 到达。

## 方法（初始集）

- `health` — 完整健康快照（与 `openclaw health --json` 形状相同）。
- `status` — 简短摘要。
- `system-presence` — 当前在线列表。
- `system-event` — 发布一个在线/系统笔记（结构化）。
- `send` — 通过活动通道发送消息。
- `agent` — 运行代理回合（事件通过同一连接流回）。
- `node.list` — 列出配对+当前连接的节点（包括 `caps`，`deviceFamily`，`modelIdentifier`，`paired`，`connected` 和已通告的 `commands`）。
- `node.describe` — 描述一个节点（功能+支持的 `node.invoke` 命令；适用于配对节点和当前连接的未配对节点）。
- `node.invoke` — 在节点上调用命令（例如 `canvas.*`，`camera.*`）。
- `node.pair.*` — 配对生命周期（`request`，`list`，`approve`，`reject`，`verify`）。

另见：[在线状态](/concepts/presence) 了解在线状态的生成/去重以及为什么稳定的 `client.instanceId` 很重要。

## 事件

- `agent` — 代理运行的流式工具/输出事件（带序列标签）。
- `presence` — 在线状态更新（带有 stateVersion 的增量）推送到所有连接的客户端。
- `tick` — 定期心跳/无操作以确认活跃性。
- `shutdown` — 网关正在退出；负载包括 `reason` 和可选的 `restartExpectedMs`。客户端应重新连接。

## WebChat 集成

- WebChat 是一个原生的 SwiftUI UI，直接与网关 WebSocket 通信以获取历史记录、发送、中止和事件。
- 远程使用通过相同的 SSH/Tailscale 隧道进行；如果配置了网关令牌，客户端会在 `connect` 期间包含它。
- macOS 应用程序通过单个 WS（共享连接）连接；它从初始快照中获取在线状态并监听 `presence` 事件以更新 UI。

## 类型和验证

- 服务器使用 AJV 根据协议定义生成的 JSON Schema 验证每个传入的数据帧。
- 客户端（TS/Swift）使用生成的类型（TS 直接使用；Swift 通过仓库的生成器）。
- 协议定义是唯一的真实来源；重新生成 schema/models 使用：
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`

## 连接快照

- `hello-ok` 包含一个 `snapshot`，其中包含 `presence`，`health`，`stateVersion` 和 `uptimeMs` 以及 `policy {maxPayload,maxBufferedBytes,tickIntervalMs}`，以便客户端可以立即渲染而无需额外请求。
- `health`/`system-presence` 仍然可用于手动刷新，但在连接时不是必需的。

## 错误码 (res.error 形状)

- 错误使用 `{ code, message, details?, retryable?, retryAfterMs? }`。
- 标准错误码：
  - `NOT_LINKED` — WhatsApp 未认证。
  - `AGENT_TIMEOUT` — 代理在配置的截止时间之前没有响应。
  - `INVALID_REQUEST` — schema/参数验证失败。
  - `UNAVAILABLE` — 网关正在关闭或依赖项不可用。

## 心跳行为

- 定期发出 `tick` 事件（或 WS ping/pong），以便客户端知道网关即使在没有流量的情况下也是活跃的。
- 发送/代理确认保持为单独的响应；不要用心跳来重载发送。

## 重播 / 缺口

- 事件不会被重播。客户端检测到 seq 缺口并在继续之前应该刷新 (`health` + `system-presence`)。WebChat 和 macOS 客户端现在在出现缺口时会自动刷新。

## 监督 (macOS 示例)

- 使用 launchd 保持服务运行：
  - 程序：`openclaw` 的路径
  - 参数：`gateway`
  - KeepAlive：true
  - StandardOut/Err：文件路径或 `syslog`
- 失败时，launchd 会重启；致命的配置错误应继续退出，以便操作员注意到。
- LaunchAgents 是按用户的，并且需要登录会话；对于无头设置，请使用自定义的 LaunchDaemon（不提供）。
  - `openclaw gateway install` 写入 `~/Library/LaunchAgents/bot.molt.gateway.plist`
    （或 `bot.molt.<profile>.plist`；清理旧版 `com.openclaw.*`）。
  - `openclaw doctor` 审核 LaunchAgent 配置并可以将其更新为当前默认值。

## 网关服务管理 (CLI)

使用网关 CLI 进行安装/启动/停止/重启/状态检查：

```bash
openclaw gateway status
openclaw gateway install
openclaw gateway stop
openclaw gateway restart
openclaw logs --follow
```

注意事项：

- `gateway status` 默认使用服务解析的端口/配置探测网关 RPC（使用 `--url` 覆盖）。
- `gateway status --deep` 添加系统级扫描（LaunchDaemons/system 单元）。
- `gateway status --no-probe` 跳过 RPC 探测（在网络中断时有用）。
- `gateway status --json` 对脚本稳定。
- `gateway status` 分别报告 **supervisor 运行时**（launchd/systemd 运行）和 **RPC 可达性**（WS 连接 + 状态 RPC）。
- `gateway status` 打印配置路径 + 探测目标以避免“localhost 与 LAN 绑定”混淆和配置文件不匹配。
- `gateway status` 当服务看起来正在运行但端口关闭时，包含最后一个网关错误行。
- `logs` 通过 RPC 尾随网关文件日志（无需手动 `tail`/`grep`）。
- 如果检测到其他类似网关的服务，CLI 会警告除非它们是 OpenClaw 配置文件服务。
  我们仍然建议每台机器 **一个网关** 适用于大多数设置；使用隔离的配置文件/端口进行冗余或救援机器人。参见 [多个网关](/gateway/multiple-gateways)。
  - 清理：`openclaw gateway uninstall`（当前服务）和 `openclaw doctor`（旧版迁移）。
- `gateway install` 已安装时为无操作；使用 `openclaw gateway install --force` 重新安装（配置文件/env/路径更改）。

捆绑的 Mac 应用程序：

- OpenClaw.app 可以捆绑基于 Node 的网关中继并安装一个标记为
  `bot.molt.gateway` 的用户 LaunchAgent（或 `bot.molt.<profile>`；旧版 `com.openclaw.*` 标签仍能干净卸载）。
- 要干净停止它，使用 `openclaw gateway stop`（或 `launchctl bootout gui/$UID/bot.molt.gateway`）。
- 要重启，使用 `openclaw gateway restart`（或 `launchctl kickstart -k gui/$UID/bot.molt.gateway`）。
  - `launchctl` 仅在安装了 LaunchAgent 时有效；否则先使用 `openclaw gateway install`。
  - 运行命名配置文件时，将标签替换为 `bot.molt.<profile>`。

## 监督（systemd 用户单元）

OpenClaw 默认在 Linux/WSL2 上安装 **systemd 用户服务**。我们
推荐单用户机器使用用户服务（环境更简单，每个用户的配置）。
使用 **系统服务** 用于多用户或始终在线的服务器（无需保留，共享监督）。

`openclaw gateway install` 写入用户单元。`openclaw doctor` 审核
单元并可以更新以匹配当前推荐的默认值。

创建 `~/.config/systemd/user/openclaw-gateway[-<profile>].service`：

```
[Unit]
Description=OpenClaw Gateway (profile: <profile>, v<version>)
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/openclaw gateway --port 18789
Restart=always
RestartSec=5
Environment=OPENCLAW_GATEWAY_TOKEN=
WorkingDirectory=/home/youruser

[Install]
WantedBy=default.target
```

启用保留（必需使用户服务在注销/空闲时存活）：

```
sudo loginctl enable-linger youruser
```

入站时在 Linux/WSL2 上运行此命令（可能需要 sudo；写入 `/var/lib/systemd/linger`）。
然后启用服务：

```
systemctl --user enable --now openclaw-gateway[-<profile>].service
```

**Alternative (system service)** - 对于始终在线或多用户服务器，您可以安装一个 systemd **system** 单元而不是用户单元（不需要 lingering）。创建 `/etc/systemd/system/openclaw-gateway[-<profile>].service`（复制上面的单元，
切换 `WantedBy=multi-user.target`，设置 `User=` + `WorkingDirectory=`)，然后：

```
sudo systemctl daemon-reload
sudo systemctl enable --now openclaw-gateway[-<profile>].service
```

## Windows (WSL2)

Windows 安装应使用 **WSL2** 并遵循上述 Linux systemd 部分。

## 运营检查

- 存活性：打开 WS 并发送 `req:connect` → 期望收到 `res` 带有 `payload.type="hello-ok"`（带快照）。
- 准备就绪：调用 `health` → 期望收到 `ok: true` 和 `linkChannel` 中的一个链接通道（如果适用）。
- 调试：订阅 `tick` 和 `presence` 事件；确保 `status` 显示链接/认证时间；存在条目显示网关主机和已连接客户端。

## 安全保证

- 默认情况下每个主机一个网关；如果您运行多个配置文件，请隔离端口/状态并针对正确的实例。
- 不会回退到直接的 Baileys 连接；如果网关关闭，发送会立即失败。
- 非首次连接帧或格式错误的 JSON 将被拒绝并且套接字将关闭。
- 优雅关闭：在关闭之前发出 `shutdown` 事件；客户端必须处理关闭和重新连接。

## CLI 辅助工具

- `openclaw gateway health|status` — 通过网关 WS 请求健康/状态。
- `openclaw message send --target <num> --message "hi" [--media ...]` — 通过网关发送（对于 WhatsApp 是幂等的）。
- `openclaw agent --message "hi" --to <num>` — 运行代理轮询（默认等待最终结果）。
- `openclaw gateway call <method> --params '{"k":"v"}'` — 用于调试的原始方法调用器。
- `openclaw gateway stop|restart` — 停止/重启受监督的网关服务（launchd/systemd）。
- 网关辅助子命令假设 `--url` 上有一个正在运行的网关；它们不再自动启动一个。

## 迁移指南

- 停止使用 `openclaw gateway` 和旧版 TCP 控制端口。
- 更新客户端以使用带有强制连接和结构化存在的 WS 协议。