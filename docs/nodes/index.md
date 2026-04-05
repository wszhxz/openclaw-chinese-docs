---
summary: "Nodes: pairing, capabilities, permissions, and CLI helpers for canvas/camera/screen/device/notifications/system"
read_when:
  - Pairing iOS/Android nodes to a gateway
  - Using node canvas/camera for agent context
  - Adding new node commands or CLI helpers
title: "Nodes"
---
# 节点

**节点**是一个配套设备（macOS/iOS/Android/headless），它连接到网关 **WebSocket**（与操作符相同的端口），端口为 `role: "node"`，并通过 `node.invoke` 暴露命令接口（例如 `canvas.*`、`camera.*`、`device.*`、`notifications.*`、`system.*`）。协议详情：[网关协议](/gateway/protocol)。

传统传输：[桥接协议](/gateway/bridge-protocol) (TCP JSONL；
仅适用于当前节点的旧版历史)。

macOS 也可以在 **节点模式** 下运行：菜单栏应用连接到网关的 WS 服务器，并将其本地画布/摄像头命令作为节点暴露（因此 `openclaw nodes …` 可针对此 Mac 工作）。

注意：

- 节点是 **外围设备**，而非网关。它们不运行网关服务。
- Telegram/WhatsApp 等消息到达 **网关**，而非节点。
- 故障排查手册：[/nodes/troubleshooting](/nodes/troubleshooting)

## 配对 + 状态

**WS 节点使用设备配对。** 节点在 `connect` 期间呈现设备身份；网关
为 `role: node` 创建设备配对请求。通过 devices CLI（或 UI）批准。

快速 CLI：

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw devices reject <requestId>
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
```

如果节点使用更改的认证详细信息重试（角色/范围/公钥），先前的
挂起请求被取代，并创建新的 `requestId`。批准前重新运行
`openclaw devices list`。

注意：

- `nodes status` 将节点标记为 **已配对**，当其设备配对角色包含 `node` 时。
- 设备配对记录是持久的已批准角色合同。令牌
  轮换保留在该合同内；它无法将已配对的节点升级为配对批准从未授予的不同角色。
- `node.pair.*` (CLI: `openclaw nodes pending/approve/reject/rename`) 是一个独立的网关拥有的
  节点配对存储；它不控制 WS `connect` 握手。
- 批准范围遵循挂起请求中声明的命令：
  - 无命令请求：`operator.pairing`
  - 非执行节点命令：`operator.pairing` + `operator.write`
  - `system.run` / `system.run.prepare` / `system.which`：`operator.pairing` + `operator.admin`

## 远程节点主机 (system.run)

当您的网关在一台机器上运行，而您希望命令在另一台机器上执行时，请使用 **节点主机**。模型仍然与 **网关** 通信；网关
在选中 `host=node` 时将 `exec` 调用转发到 **节点主机**。

### 何处运行什么

- **网关主机**：接收消息，运行模型，路由工具调用。
- **节点主机**：在节点机器上执行 `system.run`/`system.which`。
- **批准**：通过 `~/.openclaw/exec-approvals.json` 在节点主机上强制执行。

批准说明：

- 基于批准的节点运行绑定确切请求上下文。
- 对于直接的 shell/运行时文件执行，OpenClaw 也尽力绑定一个具体的本地
  文件操作数，并在该文件在执行前更改时拒绝运行。
- 如果 OpenClaw 无法识别恰好一个具体的本地文件用于解释器/运行时命令，
  基于批准的执行将被拒绝，而不是假装具有完整的运行时覆盖。使用沙箱、
  独立主机或明确的信任白名单/完整工作流以获得更广泛的解释器语义。

### 启动节点主机（前台）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --display-name "Build Node"
```

### 通过 SSH 隧道远程网关（回环绑定）

如果网关绑定到回环 (`gateway.bind=loopback`，本地模式下的默认值)，
远程节点主机无法直接连接。创建一个 SSH 隧道并将节点主机指向隧道的本地端。

示例（节点主机 -> 网关主机）：

```bash
# Terminal A (keep running): forward local 18790 -> gateway 127.0.0.1:18789
ssh -N -L 18790:127.0.0.1:18789 user@gateway-host

# Terminal B: export the gateway token and connect through the tunnel
export OPENCLAW_GATEWAY_TOKEN="<gateway-token>"
openclaw node run --host 127.0.0.1 --port 18790 --display-name "Build Node"
```

注意：

- `openclaw node run` 支持令牌或密码认证。
- 首选环境变量：`OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`。
- 配置回退是 `gateway.auth.token` / `gateway.auth.password`。
- 在本地模式下，节点主机故意忽略 `gateway.remote.token` / `gateway.remote.password`。
- 在远程模式下，根据远程优先级规则，`gateway.remote.token` / `gateway.remote.password` 符合条件。
- 如果配置了活动的本地 `gateway.auth.*` SecretRefs 但未解析，节点主机认证将失败关闭。
- 节点主机认证解析仅尊重 `OPENCLAW_GATEWAY_*` 环境变量。

### 启动节点主机（服务）

```bash
openclaw node install --host <gateway-host> --port 18789 --display-name "Build Node"
openclaw node restart
```

### 配对 + 命名

在网关主机上：

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw nodes status
```

如果节点使用更改的认证详细信息重试，请重新运行 `openclaw devices list`
并批准当前的 `requestId`。

命名选项：

- `--display-name` 在 `openclaw node run` / `openclaw node install` 上（持久化在节点上的 `~/.openclaw/node.json`）。
- `openclaw nodes rename --node <id|name|ip> --name "Build Node"`（网关覆盖）。

### 允许列表命令

执行批准是 **每个节点主机** 的。从网关添加允许列表条目：

```bash
openclaw approvals allowlist add --node <id|name|ip> "/usr/bin/uname"
openclaw approvals allowlist add --node <id|name|ip> "/usr/bin/sw_vers"
```

批准位于节点主机上的 `~/.openclaw/exec-approvals.json`。

### 将执行指向节点

配置默认值（网关配置）：

```bash
openclaw config set tools.exec.host node
openclaw config set tools.exec.security allowlist
openclaw config set tools.exec.node "<id-or-name>"
```

或者按会话：

```
/exec host=node security=allowlist node=<id-or-name>
```

设置后，任何带有 `host=node` 的 `exec` 调用将在节点主机上运行（受节点
允许列表/批准限制）。

`host=auto` 不会自行隐式选择节点，但允许来自 `auto` 的显式每调用 `host=node` 请求。如果您希望节点执行成为会话的默认值，请显式设置 `tools.exec.host=node` 或 `/exec host=node ...`。

相关：

- [节点主机 CLI](/cli/node)
- [执行工具](/tools/exec)
- [执行批准](/tools/exec-approvals)

## 调用命令

低级（原始 RPC）：

```bash
openclaw nodes invoke --node <idOrNameOrIp> --command canvas.eval --params '{"javaScript":"location.href"}'
```

存在高级辅助程序用于常见的“给代理媒体附件”工作流。

## 屏幕截图（画布快照）

如果节点正在显示画布（WebView），`canvas.snapshot` 返回 `{ format, base64 }`。

CLI 辅助程序（写入临时文件并打印 `MEDIA:<path>`）：

```bash
openclaw nodes canvas snapshot --node <idOrNameOrIp> --format png
openclaw nodes canvas snapshot --node <idOrNameOrIp> --format jpg --max-width 1200 --quality 0.9
```

### 画布控制

```bash
openclaw nodes canvas present --node <idOrNameOrIp> --target https://example.com
openclaw nodes canvas hide --node <idOrNameOrIp>
openclaw nodes canvas navigate https://example.com --node <idOrNameOrIp>
openclaw nodes canvas eval --node <idOrNameOrIp> --js "document.title"
```

注意：

- `canvas present` 接受 URL 或本地文件路径 (`--target`)，以及可选的 `--x/--y/--width/--height` 用于定位。
- `canvas eval` 接受内联 JS (`--js`) 或位置参数。

### A2UI（画布）

```bash
openclaw nodes canvas a2ui push --node <idOrNameOrIp> --text "Hello"
openclaw nodes canvas a2ui push --node <idOrNameOrIp> --jsonl ./payload.jsonl
openclaw nodes canvas a2ui reset --node <idOrNameOrIp>
```

注意：

- 仅支持 A2UI v0.8 JSONL（v0.9/createSurface 被拒绝）。

## 照片 + 视频（节点相机）

照片 (`jpg`)：

```bash
openclaw nodes camera list --node <idOrNameOrIp>
openclaw nodes camera snap --node <idOrNameOrIp>            # default: both facings (2 MEDIA lines)
openclaw nodes camera snap --node <idOrNameOrIp> --facing front
```

视频片段 (`mp4`)：

```bash
openclaw nodes camera clip --node <idOrNameOrIp> --duration 10s
openclaw nodes camera clip --node <idOrNameOrIp> --duration 3000 --no-audio
```

注意：

- 节点必须处于 **前台** 才能进行 `canvas.*` 和 `camera.*`（后台调用返回 `NODE_BACKGROUND_UNAVAILABLE`）。
- 剪辑时长被限制（目前为 `<= 60s`），以避免过大的 base64 负载。
- Android 将尽可能提示 `CAMERA`/`RECORD_AUDIO` 权限；被拒绝的权限将以 `*_PERMISSION_REQUIRED` 失败。

## 屏幕录制（节点）

支持的节点暴露 `screen.record` (mp4)。示例：

```bash
openclaw nodes screen record --node <idOrNameOrIp> --duration 10s --fps 10
openclaw nodes screen record --node <idOrNameOrIp> --duration 10s --fps 10 --no-audio
```

注意：

- `screen.record` 可用性取决于节点平台。
- 屏幕录制被限制为 `<= 60s`。
- `--no-audio` 在支持的平台上禁用麦克风捕获。
- 当有多个屏幕可用时，使用 `--screen <index>` 选择显示器。

## 位置（节点）

当设置中启用位置时，节点暴露 `location.get`。

CLI 辅助程序：

```bash
openclaw nodes location get --node <idOrNameOrIp>
openclaw nodes location get --node <idOrNameOrIp> --accuracy precise --max-age 15000 --location-timeout 10000
```

注意：

- 位置默认为 **关闭**。
- “始终”需要系统权限；后台获取尽最大努力。
- 响应包括经纬度、精度（米）和时间戳。

## 短信（Android 节点）

当用户授予 **SMS** 权限且设备支持电话功能时，Android 节点可以暴露 `sms.send`。

低级调用：

```bash
openclaw nodes invoke --node <idOrNameOrIp> --command sms.send --params '{"to":"+15555550123","message":"Hello from OpenClaw"}'
```

注意：

- 在功能被广播之前，必须在 Android 设备上接受权限提示。
- 没有电话功能的纯 Wi-Fi 设备将不会广播 `sms.send`。

## Android 设备 + 个人数据命令

当启用相应的功能时，Android 节点可以广播额外的命令族。

可用的命令族：

- `device.status`, `device.info`, `device.permissions`, `device.health`
- `notifications.list`, `notifications.actions`
- `photos.latest`
- `contacts.search`, `contacts.add`
- `calendar.events`, `calendar.add`
- `callLog.search`
- `sms.search`
- `motion.activity`, `motion.pedometer`

示例调用：

```bash
openclaw nodes invoke --node <idOrNameOrIp> --command device.status --params '{}'
openclaw nodes invoke --node <idOrNameOrIp> --command notifications.list --params '{}'
openclaw nodes invoke --node <idOrNameOrIp> --command photos.latest --params '{"limit":1}'
```

注意：

- 运动命令受可用传感器的功能限制。

## 系统命令（节点主机 / Mac 节点）

macOS 节点暴露 `system.run`、`system.notify` 和 `system.execApprovals.get/set`。
无头节点主机暴露 `system.run`、`system.which` 和 `system.execApprovals.get/set`。

示例：

```bash
openclaw nodes notify --node <idOrNameOrIp> --title "Ping" --body "Gateway ready"
openclaw nodes invoke --node <idOrNameOrIp> --command system.which --params '{"name":"git"}'
```

注意：

- `system.run` 在载荷中返回 stdout/stderr/exit code。
- Shell 执行现在通过带有 `host=node` 的 `exec` 工具进行；`nodes` 仍保留为显式节点命令的直接 RPC 接口。
- `nodes invoke` 不暴露 `system.run` 或 `system.run.prepare`；它们仅保留在执行路径上。
- 执行路径在批准前准备一个规范的 `systemRunPlan`。一旦获得批准，网关将转发该存储的计划，而不是任何后续由调用者编辑的命令/工作目录/会话字段。
- `system.notify` 遵循 macOS 应用上的通知权限状态。
- 未识别的节点 `platform` / `deviceFamily` 元数据使用保守的默认白名单，排除 `system.run` 和 `system.which`。如果您确实需要这些命令用于未知平台，请通过 `gateway.nodes.allowCommands` 显式添加它们。
- `system.run` 支持 `--cwd`、`--env KEY=VAL`、`--command-timeout` 和 `--needs-screen-recording`。
- 对于 Shell 包装器 (`bash|sh|zsh ... -c/-lc`)，请求范围的 `--env` 值被缩减为明确的白名单 (`TERM`、`LANG`、`LC_*`、`COLORTERM`、`NO_COLOR`、`FORCE_COLOR`)。
- 在白名单模式下允许“始终”决策时，已知的分发包装器 (`env`、`nice`、`nohup`、`stdbuf`、`timeout`) 持久化内部可执行文件路径，而不是包装器路径。如果解包不安全，则不会自动持久化任何白名单条目。
- 在白名单模式下的 Windows 节点主机上，shell 包装器通过 `cmd.exe /c` 运行需要批准（仅白名单条目不能自动允许包装器形式）。
- `system.notify` 支持 `--priority <passive|active|timeSensitive>` 和 `--delivery <system|overlay|auto>`。
- 节点主机忽略 `PATH` 覆盖并剥离危险启动/Shell 键 (`DYLD_*`、`LD_*`、`NODE_OPTIONS`、`PYTHON*`、`PERL*`、`RUBYOPT`、`SHELLOPTS`、`PS4`)。如果您需要额外的 PATH 条目，请配置节点主机服务环境（或在标准位置安装工具），而不是通过 `--env` 传递 `PATH`。
- 在 macOS 节点模式下，`system.run` 受 macOS 应用中的执行批准控制（设置 → 执行批准）。Ask/allowlist/full 的表现与无头节点主机相同；拒绝的提示返回 `SYSTEM_RUN_DENIED`。
- 在无头节点主机上，`system.run` 受执行批准控制 (`~/.openclaw/exec-approvals.json`)。

## 执行节点绑定

当有多个节点可用时，您可以将 exec 绑定到特定节点。
这为 `exec host=node` 设置默认节点（并且可以按代理覆盖）。

全局默认值：

```bash
openclaw config set tools.exec.node "node-id-or-name"
```

按代理覆盖：

```bash
openclaw config get agents.list
openclaw config set agents.list[0].tools.exec.node "node-id-or-name"
```

取消设置以允许任何节点：

```bash
openclaw config unset tools.exec.node
openclaw config unset agents.list[0].tools.exec.node
```

## 权限映射

节点可能在 `node.list` / `node.describe` 中包含一个 `permissions` 映射，按权限名称（例如 `screenRecording`、`accessibility`）索引，值为布尔值 (`true` = granted)。

## 无头节点主机（跨平台）

OpenClaw 可以运行一个 **无头节点主机**（无 UI），它连接到 Gateway WebSocket 并暴露 `system.run` / `system.which`。这在 Linux/Windows 上很有用，或者用于在服务器旁运行最小节点。

启动它：

```bash
openclaw node run --host <gateway-host> --port 18789
```

注意：

- 仍然需要配对（Gateway 将显示设备配对提示）。
- 节点主机将其节点 ID、令牌、显示名称和网关连接信息存储在 `~/.openclaw/node.json` 中。
- 执行批准通过 `~/.openclaw/exec-approvals.json` 在本地强制执行（参见 [执行批准](/tools/exec-approvals)）。
- 在 macOS 上，无头节点主机默认在本地执行 `system.run`。设置 `OPENCLAW_NODE_EXEC_HOST=app` 以通过配套应用执行主机路由 `system.run`；添加 `OPENCLAW_NODE_EXEC_FALLBACK=0` 以要求应用主机并在其不可用时失败关闭。
- 当 Gateway WS 使用 TLS 时，添加 `--tls` / `--tls-fingerprint`。

## Mac 节点模式

- macOS 菜单栏应用作为节点连接到 Gateway WS 服务器（因此 `openclaw nodes …` 适用于此 Mac）。
- 在远程模式下，应用打开 Gateway 端口的 SSH 隧道并连接到 `localhost`。