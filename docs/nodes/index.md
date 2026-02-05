---
summary: "Nodes: pairing, capabilities, permissions, and CLI helpers for canvas/camera/screen/system"
read_when:
  - Pairing iOS/Android nodes to a gateway
  - Using node canvas/camera for agent context
  - Adding new node commands or CLI helpers
title: "Nodes"
---
# 节点

**节点**是一个配套设备（macOS/iOS/Android/无头设备），通过 `role: "node"` 连接到网关的 **WebSocket**（与操作员相同的端口），并通过 `node.invoke` 暴露命令表面（例如 `canvas.*`、`camera.*`、`system.*`）。协议详情：[网关协议](/gateway/protocol)。

传统传输：[桥接协议](/gateway/bridge-protocol)（TCP JSONL；当前节点已弃用/移除）。

macOS 也可以以**节点模式**运行：菜单栏应用程序连接到网关的WS服务器，并将其本地canvas/camera命令作为节点暴露（因此 `openclaw nodes …` 对此Mac有效）。

注意事项：

- 节点是**外设**，不是网关。它们不运行网关服务。
- Telegram/WhatsApp/等消息到达**网关**，而不是节点。

## 配对 + 状态

**WS节点使用设备配对。** 节点在 `connect` 期间呈现设备身份；网关
为 `role: node` 创建设备配对请求。通过设备CLI（或UI）批准。

快速CLI：

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw devices reject <requestId>
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
```

注意事项：

- 当设备配对角色包含 `node` 时，`nodes status` 将节点标记为**已配对**。
- `node.pair.*`（CLI：`openclaw nodes pending/approve/reject`）是独立的网关拥有的
  节点配对存储；它**不**控制WS `connect` 握手。

## 远程节点主机（system.run）

当您的网关运行在一台机器上而您希望命令在另一台机器上执行时，请使用**节点主机**。模型仍然与**网关**通信；当选择 `host=node` 时，网关将 `exec` 调用转发到**节点主机**。

### 各部分运行位置

- **网关主机**：接收消息，运行模型，路由工具调用。
- **节点主机**：在节点机器上执行 `system.run`/`system.which`。
- **审批**：通过 `~/.openclaw/exec-approvals.json` 在节点主机上强制执行。

### 启动节点主机（前台）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --display-name "Build Node"
```

### 通过SSH隧道的远程网关（回环绑定）

如果网关绑定到回环（`gateway.bind=loopback`，本地模式下的默认值），
远程节点主机无法直接连接。创建SSH隧道并将
节点主机指向隧道的本地端。

示例（节点主机 -> 网关主机）：

```bash
# Terminal A (keep running): forward local 18790 -> gateway 127.0.0.1:18789
ssh -N -L 18790:127.0.0.1:18789 user@gateway-host

# Terminal B: export the gateway token and connect through the tunnel
export OPENCLAW_GATEWAY_TOKEN="<gateway-token>"
openclaw node run --host 127.0.0.1 --port 18790 --display-name "Build Node"
```

注意事项：

- 令牌来自网关配置中的 `gateway.auth.token`（网关主机上的 `~/.openclaw/openclaw.json`）。
- `openclaw node run` 读取 `OPENCLAW_GATEWAY_TOKEN` 进行认证。

### 启动节点主机（服务）

```bash
openclaw node install --host <gateway-host> --port 18789 --display-name "Build Node"
openclaw node restart
```

### 配对 + 名称

在网关主机上：

```bash
openclaw nodes pending
openclaw nodes approve <requestId>
openclaw nodes list
```

命名选项：

- `--display-name` 在 `openclaw node run` / `openclaw node install` 上（持久化存储在节点上的 `~/.openclaw/node.json` 中）。
- `openclaw nodes rename --node <id|name|ip> --name "Build Node"`（网关覆盖）。

### 允许列表命令

执行批准是**按节点主机**的。从网关添加允许列表条目：

```bash
openclaw approvals allowlist add --node <id|name|ip> "/usr/bin/uname"
openclaw approvals allowlist add --node <id|name|ip> "/usr/bin/sw_vers"
```

批准信息存储在节点主机的 `~/.openclaw/exec-approvals.json` 处。

### 指向节点的执行

配置默认值（网关配置）：

```bash
openclaw config set tools.exec.host node
openclaw config set tools.exec.security allowlist
openclaw config set tools.exec.node "<id-or-name>"
```

或者按会话配置：

```
/exec host=node security=allowlist node=<id-or-name>
```

设置后，任何带有 `exec` 的调用与 `host=node` 都将在节点主机上运行（受节点允许列表/批准限制）。

相关：

- [节点主机 CLI](/cli/node)
- [执行工具](/tools/exec)
- [执行批准](/tools/exec-approvals)

## 调用命令

低级别（原始 RPC）：

```bash
openclaw nodes invoke --node <idOrNameOrIp> --command canvas.eval --params '{"javaScript":"location.href"}'
```

对于常见的"给代理提供媒体附件"工作流程，存在更高级别的辅助工具。

## 截图（画布快照）

如果节点正在显示画布（WebView），`canvas.snapshot` 返回 `{ format, base64 }`。

CLI 辅助工具（写入临时文件并打印 `MEDIA:<path>`）：

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

注意事项：

- `canvas present` 接受 URL 或本地文件路径（`--target`），以及可选的 `--x/--y/--width/--height` 进行定位。
- `canvas eval` 接受内联 JS（`--js`）或位置参数。

### A2UI（画布）

```bash
openclaw nodes canvas a2ui push --node <idOrNameOrIp> --text "Hello"
openclaw nodes canvas a2ui push --node <idOrNameOrIp> --jsonl ./payload.jsonl
openclaw nodes canvas a2ui reset --node <idOrNameOrIp>
```

注意事项：

- 仅支持 A2UI v0.8 JSONL（v0.9/createSurface 被拒绝）。

## 照片 + 视频（节点摄像头）

照片（`jpg`）：

```bash
openclaw nodes camera list --node <idOrNameOrIp>
openclaw nodes camera snap --node <idOrNameOrIp>            # default: both facings (2 MEDIA lines)
openclaw nodes camera snap --node <idOrNameOrIp> --facing front
```

视频剪辑 (`mp4`):

```bash
openclaw nodes camera clip --node <idOrNameOrIp> --duration 10s
openclaw nodes camera clip --node <idOrNameOrIp> --duration 3000 --no-audio
```

注意事项：

- 节点必须处于**前台**才能使用 `canvas.*` 和 `camera.*`（后台调用会返回 `NODE_BACKGROUND_UNAVAILABLE`）。
- 剪辑时长会被限制（当前为 `<= 60s`）以避免过大的base64负载。
- Android会在可能的情况下提示用户授予 `CAMERA`/`RECORD_AUDIO` 权限；拒绝权限会导致 `*_PERMISSION_REQUIRED` 错误。

## 屏幕录制（节点）

节点提供 `screen.record`（mp4）。示例：

```bash
openclaw nodes screen record --node <idOrNameOrIp> --duration 10s --fps 10
openclaw nodes screen record --node <idOrNameOrIp> --duration 10s --fps 10 --no-audio
```

注意事项：

- `screen.record` 需要节点应用处于前台。
- Android会在录制前显示系统屏幕捕获提示。
- 屏幕录制被限制为 `<= 60s`。
- `--no-audio` 禁用麦克风捕获（iOS/Android支持；macOS使用系统捕获音频）。
- 当有多个屏幕可用时，使用 `--screen <index>` 选择显示器。

## 位置（节点）

当在设置中启用位置服务时，节点提供 `location.get`。

CLI辅助工具：

```bash
openclaw nodes location get --node <idOrNameOrIp>
openclaw nodes location get --node <idOrNameOrIp> --accuracy precise --max-age 15000 --location-timeout 10000
```

注意事项：

- 位置服务**默认关闭**。
- "始终"需要系统权限；后台获取是尽力而为的。
- 响应包括纬度/经度、精度（米）和时间戳。

## 短信（Android节点）

当用户授予**短信**权限且设备支持电话功能时，Android节点可以提供 `sms.send`。

底层调用：

```bash
openclaw nodes invoke --node <idOrNameOrIp> --command sms.send --params '{"to":"+15555550123","message":"Hello from OpenClaw"}'
```

注意事项：

- 必须在Android设备上接受权限提示后才能公布该功能。
- 不支持电话功能的纯Wi-Fi设备不会公布 `sms.send`。

## 系统命令（节点主机/ Mac节点）

macOS节点提供 `system.run`、`system.notify` 和 `system.execApprovals.get/set`。
无头节点主机提供 `system.run`、`system.which` 和 `system.execApprovals.get/set`。

示例：

```bash
openclaw nodes run --node <idOrNameOrIp> -- echo "Hello from mac node"
openclaw nodes notify --node <idOrNameOrIp> --title "Ping" --body "Gateway ready"
```

注意事项：

- `system.run` 在有效载荷中返回标准输出/标准错误/退出代码。
- `system.notify` 尊重 macOS 应用中的通知权限状态。
- `system.run` 支持 `--cwd`、`--env KEY=VAL`、`--command-timeout` 和 `--needs-screen-recording`。
- `system.notify` 支持 `--priority <passive|active|timeSensitive>` 和 `--delivery <system|overlay|auto>`。
- macOS 节点会丢弃 `PATH` 覆盖；无头节点主机仅在它前置到节点主机 PATH 时接受 `PATH`。
- 在 macOS 节点模式下，`system.run` 受 macOS 应用中执行批准的限制（设置 → 执行批准）。
  询问/允许列表/完全模式的行为与无头节点主机相同；被拒绝的提示会返回 `SYSTEM_RUN_DENIED`。
- 在无头节点主机上，`system.run` 受执行批准的限制（`~/.openclaw/exec-approvals.json`）。

## 执行节点绑定

当多个节点可用时，您可以将执行绑定到特定节点。
这会设置 `exec host=node` 的默认节点（并且可以按代理进行覆盖）。

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

节点可以在 `node.list` / `node.describe` 中包含一个 `permissions` 映射，按键名为权限名称（例如 `screenRecording`、`accessibility`）并带有布尔值（`true` = 已授予）。

## 无头节点主机（跨平台）

OpenClaw 可以运行一个连接到网关 WebSocket 并公开 `system.run` / `system.which` 的**无头节点主机**（无 UI）。这对于 Linux/Windows 或在服务器旁边运行最小节点很有用。

启动它：

```bash
openclaw node run --host <gateway-host> --port 18789
```

注意事项：

- 仍需要配对（网关将显示节点批准提示）。
- 节点主机会将其节点 ID、令牌、显示名称和网关连接信息存储在 `~/.openclaw/node.json` 中。
- 执行批准通过 `~/.openclaw/exec-approvals.json` 在本地强制执行
  （参见 [执行批准](/tools/exec-approvals)）。
- 在 macOS 上，无头节点主机在可访问时优先使用配套应用执行主机，如果应用不可用则回退到本地执行。设置 `OPENCLAW_NODE_EXEC_HOST=app` 以要求
  应用，或设置 `OPENCLAW_NODE_EXEC_FALLBACK=0` 以禁用回退。
- 当网关 WS 使用 TLS 时添加 `--tls` / `--tls-fingerprint`。

## Mac 节点模式

- macOS 菜单栏应用作为节点连接到网关 WS 服务器（因此 `openclaw nodes …` 针对此 Mac 工作）。
- 在远程模式下，应用会为网关端口打开一个 SSH 隧道并连接到 `localhost`。