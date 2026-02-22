---
summary: "Nodes: pairing, capabilities, permissions, and CLI helpers for canvas/camera/screen/system"
read_when:
  - Pairing iOS/Android nodes to a gateway
  - Using node canvas/camera for agent context
  - Adding new node commands or CLI helpers
title: "Nodes"
---
# 节点

一个 **node** 是一个伴生设备（macOS/iOS/Android/headless），它通过 `role: "node"` 连接到网关 **WebSocket**（与操作员相同的端口），并通过 `node.invoke` 暴露一个命令界面（例如 `canvas.*`, `camera.*`, `system.*`）。协议详情：[网关协议](/gateway/protocol)。

旧版传输：[桥接协议](/gateway/bridge-protocol)（TCP JSONL；已弃用/当前节点中已移除）。

macOS 也可以以 **节点模式** 运行：菜单栏应用程序连接到网关的 WS 服务器，并将其本地画布/相机命令作为节点暴露出来（因此 `openclaw nodes …` 可以针对此 Mac 工作）。

注意事项：

- 节点是 **外设**，而不是网关。它们不运行网关服务。
- Telegram/WhatsApp 等消息发送到 **网关**，而不是节点。
- 故障排除手册：[/nodes/troubleshooting](/nodes/troubleshooting)

## 配对 + 状态

**WS 节点使用设备配对。** 节点在 `connect` 期间展示设备身份；网关
为 `role: node` 创建一个设备配对请求。通过设备的 CLI（或 UI）批准。

快速 CLI：

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw devices reject <requestId>
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
```

注意事项：

- 当节点的设备配对角色包含 `node` 时，`nodes status` 标记该节点为 **已配对**。
- `node.pair.*`（CLI: `openclaw nodes pending/approve/reject`）是一个独立的网关拥有的
  设备配对存储；它 **不** 限制 WS `connect` 握手。

## 远程节点主机 (system.run)

当您的网关运行在一个机器上而您希望命令在另一个机器上执行时，使用 **节点主机**。模型仍然与 **网关** 对话；当选择 `host=node` 时，网关将 `exec` 调用转发到 **节点主机**。

### 什么在哪里运行

- **网关主机**：接收消息，运行模型，路由工具调用。
- **节点主机**：在节点机器上执行 `system.run`/`system.which`。
- **批准**：通过 `~/.openclaw/exec-approvals.json` 在节点主机上强制执行。

### 启动节点主机（前台）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --display-name "Build Node"
```

### 通过 SSH 隧道远程网关（回环绑定）

如果网关绑定到回环 (`gateway.bind=loopback`，本地模式下的默认设置），
远程节点主机无法直接连接。创建一个 SSH 隧道并将节点主机指向隧道的本地端。

示例（节点主机 -> 网关主机）：

```bash
# Terminal A (keep running): forward local 18790 -> gateway 127.0.0.1:18789
ssh -N -L 18790:127.0.0.1:18789 user@gateway-host

# Terminal B: export the gateway token and connect through the tunnel
export OPENCLAW_GATEWAY_TOKEN="<gateway-token>"
openclaw node run --host 127.0.0.1 --port 18790 --display-name "Build Node"
```

注意事项：

- 令牌是网关配置中的 `gateway.auth.token` (`~/.openclaw/openclaw.json` 在网关主机上)。
- `openclaw node run` 读取 `OPENCLAW_GATEWAY_TOKEN` 进行认证。

### 启动节点主机（服务）

```bash
openclaw node install --host <gateway-host> --port 18789 --display-name "Build Node"
openclaw node restart
```

### 配对 + 命名

在网关主机上：

```bash
openclaw nodes pending
openclaw nodes approve <requestId>
openclaw nodes list
```

命名选项：

- `--display-name` 在 `openclaw node run` / `openclaw node install` (在节点上的 `~/.openclaw/node.json` 中持久化)。
- `openclaw nodes rename --node <id|name|ip> --name "Build Node"` (网关覆盖)。

### 允许命令

执行审批是 **按节点主机** 进行的。从网关添加允许列表条目：

```bash
openclaw approvals allowlist add --node <id|name|ip> "/usr/bin/uname"
openclaw approvals allowlist add --node <id|name|ip> "/usr/bin/sw_vers"
```

审批存储在节点主机上的 `~/.openclaw/exec-approvals.json`。

### 指向节点执行

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

一旦设置，任何 `exec` 调用带有 `host=node` 的都会在节点主机上运行（受节点允许列表/审批的限制）。

相关：

- [节点主机 CLI](/cli/node)
- [执行工具](/tools/exec)
- [执行审批](/tools/exec-approvals)

## 调用命令

低级（原始 RPC）：

```bash
openclaw nodes invoke --node <idOrNameOrIp> --command canvas.eval --params '{"javaScript":"location.href"}'
```

对于常见的“给代理一个 MEDIA 附件”工作流，存在更高级的帮助程序。

## 截图（画布快照）

如果节点显示 Canvas (WebView)，`canvas.snapshot` 返回 `{ format, base64 }`。

CLI 帮助程序（写入临时文件并打印 `MEDIA:<path>`）：

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

### A2UI (画布)

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

视频片段 (`mp4`):

```bash
openclaw nodes camera clip --node <idOrNameOrIp> --duration 10s
openclaw nodes camera clip --node <idOrNameOrIp> --duration 3000 --no-audio
```

注意事项:

- 节点必须在前台运行以支持 `canvas.*` 和 `camera.*`（后台调用返回 `NODE_BACKGROUND_UNAVAILABLE`）。
- 视频片段时长被限制为（当前为 `<= 60s`）以避免过大的base64负载。
- 当可能时，Android会提示请求 `CAMERA`/`RECORD_AUDIO` 权限；拒绝权限会导致失败并返回 `*_PERMISSION_REQUIRED`。

## 屏幕录制（节点）

节点暴露 `screen.record`（mp4）。示例：

```bash
openclaw nodes screen record --node <idOrNameOrIp> --duration 10s --fps 10
openclaw nodes screen record --node <idOrNameOrIp> --duration 10s --fps 10 --no-audio
```

注意事项:

- `screen.record` 需要节点应用程序在前台运行。
- 在录制之前，Android会显示系统屏幕捕获提示。
- 屏幕录制被限制为 `<= 60s`。
- `--no-audio` 禁用麦克风捕获（在iOS/Android上受支持；macOS使用系统捕获音频）。
- 使用 `--screen <index>` 在多个屏幕可用时选择一个显示器。

## 位置（节点）

当在设置中启用位置服务时，节点暴露 `location.get`。

CLI 辅助工具:

```bash
openclaw nodes location get --node <idOrNameOrIp>
openclaw nodes location get --node <idOrNameOrIp> --accuracy precise --max-age 15000 --location-timeout 10000
```

注意事项:

- 位置默认是关闭的。
- “始终”需要系统权限；后台获取是尽力而为。
- 响应包括纬度/经度、精度（米）和时间戳。

## 短信（Android节点）

当用户授予 **短信** 权限且设备支持蜂窝通信时，Android节点可以暴露 `sms.send`。

低级调用:

```bash
openclaw nodes invoke --node <idOrNameOrIp> --command sms.send --params '{"to":"+15555550123","message":"Hello from OpenClaw"}'
```

注意事项:

- 必须在Android设备上接受权限提示才能广告该功能。
- 仅支持Wi-Fi且不支持蜂窝通信的设备不会广告 `sms.send`。

## 系统命令（节点主机 / mac节点）

macOS节点暴露 `system.run`，`system.notify` 和 `system.execApprovals.get/set`。
无头节点主机暴露 `system.run`，`system.which` 和 `system.execApprovals.get/set`。

示例:

```bash
openclaw nodes run --node <idOrNameOrIp> -- echo "Hello from mac node"
openclaw nodes notify --node <idOrNameOrIp> --title "Ping" --body "Gateway ready"
```

注意事项:

- `system.run` 在负载中返回 stdout/stderr/退出码。
- `system.notify` 尊重 macOS 应用的通知权限状态。
- `system.run` 支持 `--cwd`，`--env KEY=VAL`，`--command-timeout` 和 `--needs-screen-recording`。
- `system.notify` 支持 `--priority <passive|active|timeSensitive>` 和 `--delivery <system|overlay|auto>`。
- Node 主机忽略 `PATH` 覆盖。如果您需要额外的 PATH 条目，请配置 node 主机服务环境（或将工具安装在标准位置），而不是通过 `--env` 传递 `PATH`。
- 在 macOS node 模式下，`system.run` 受 macOS 应用中的执行批准限制（设置 → 执行批准）。Ask/allowlist/full 的行为与无头 node 主机相同；被拒绝的提示返回 `SYSTEM_RUN_DENIED`。
- 在无头 node 主机上，`system.run` 受执行批准限制 (`~/.openclaw/exec-approvals.json`)。

## 执行节点绑定

当有多个节点可用时，您可以将执行绑定到特定节点。
这会设置 `exec host=node` 的默认节点（并且可以按代理覆盖）。

全局默认：

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

节点可能在 `node.list` / `node.describe` 中包含一个 `permissions` 映射，按权限名称（例如 `screenRecording`，`accessibility`）键入，并具有布尔值 (`true` = 授予）。

## 无头节点主机（跨平台）

OpenClaw 可以运行一个 **无头节点主机**（无界面），它连接到网关 WebSocket 并暴露 `system.run` / `system.which`。这对于 Linux/Windows 或与服务器一起运行最小化节点非常有用。

启动它：

```bash
openclaw node run --host <gateway-host> --port 18789
```

注意：

- 仍然需要配对（网关会显示节点批准提示）。
- 节点主机在其节点 ID、令牌、显示名称和网关连接信息存储在 `~/.openclaw/node.json` 中。
- 通过 `~/.openclaw/exec-approvals.json` 在本地强制执行执行批准
  （参见 [执行批准](/tools/exec-approvals)）。
- 在 macOS 上，无头节点主机优先使用可访问的配套应用执行主机，如果应用不可用则回退到本地执行。设置 `OPENCLAW_NODE_EXEC_HOST=app` 以要求应用，或设置 `OPENCLAW_NODE_EXEC_FALLBACK=0` 以禁用回退。
- 当网关 WS 使用 TLS 时添加 `--tls` / `--tls-fingerprint`。

## Mac 节点模式

- macOS 菜单栏应用作为节点连接到网关 WS 服务器（因此 `openclaw nodes …` 针对此 Mac 有效）。
- 在远程模式下，应用为网关端口打开 SSH 隧道并连接到 `localhost`。