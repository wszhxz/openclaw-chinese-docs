---
summary: "Nodes: pairing, capabilities, permissions, and CLI helpers for canvas/camera/screen/device/notifications/system"
read_when:
  - Pairing iOS/Android nodes to a gateway
  - Using node canvas/camera for agent context
  - Adding new node commands or CLI helpers
title: "Nodes"
---
# 节点（Nodes）

**节点** 是一种配套设备（macOS/iOS/Android/无头模式），通过 `role: "node"` 连接到网关（Gateway）的 **WebSocket**（与操作员使用的端口相同），并借助 `node.invoke` 暴露一组命令接口（例如：`canvas.*`、`camera.*`、`device.*`、`notifications.*`、`system.*`）。协议详情参见：[网关协议](/gateway/protocol)。

旧版传输方式：[桥接协议](/gateway/bridge-protocol)（基于 TCP 的 JSONL；当前节点已弃用/移除此协议）。

macOS 还可运行于 **节点模式**：菜单栏应用连接至网关的 WebSocket 服务，并将其本地画布（canvas）/摄像头（camera）命令作为节点暴露出来（因此 `openclaw nodes …` 可作用于该 Mac）。

注意事项：

- 节点属于 **外围设备**，而非网关。它们不运行网关服务。
- Telegram/WhatsApp 等消息送达 **网关**，而非节点。
- 故障排查手册：[/nodes/troubleshooting](/nodes/troubleshooting)

## 配对与状态

**WebSocket 节点使用设备配对机制。** 节点在 `connect` 过程中出示其设备身份；网关为 `role: node` 创建一条设备配对请求。请通过设备 CLI（或 UI）批准该请求。

快速 CLI 示例：

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw devices reject <requestId>
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
```

注意事项：

- 当某节点的设备配对角色包含 `node` 时，`nodes status` 将其标记为 **已配对**。
- `node.pair.*`（CLI：`openclaw nodes pending/approve/reject`）是网关独立维护的节点配对存储；它 **不干预** WebSocket 的 `connect` 握手过程。

## 远程节点主机（system.run）

当您的网关运行于一台机器上，而您希望命令在另一台机器上执行时，请使用 **节点主机（node host）**。模型仍与 **网关** 通信；当选择 `host=node` 时，网关会将 `exec` 调用转发至 **节点主机**。

### 各组件运行位置

- **网关主机**：接收消息、运行模型、路由工具调用。
- **节点主机**：在节点机器上执行 `system.run`/`system.which`。
- **审批机制**：在节点主机上通过 `~/.openclaw/exec-approvals.json` 强制执行。

### 启动节点主机（前台运行）

在节点机器上执行：

```bash
openclaw node run --host <gateway-host> --port 18789 --display-name "Build Node"
```

### 通过 SSH 隧道连接远程网关（回环绑定）

若网关绑定至回环地址（`gateway.bind=loopback`，本地模式下的默认行为），远程节点主机将无法直接连接。此时需建立 SSH 隧道，并将节点主机指向该隧道的本地端点。

示例（节点主机 → 网关主机）：

```bash
# Terminal A (keep running): forward local 18790 -> gateway 127.0.0.1:18789
ssh -N -L 18790:127.0.0.1:18789 user@gateway-host

# Terminal B: export the gateway token and connect through the tunnel
export OPENCLAW_GATEWAY_TOKEN="<gateway-token>"
openclaw node run --host 127.0.0.1 --port 18790 --display-name "Build Node"
```

注意事项：

- `openclaw node run` 支持令牌（token）或密码认证。
- 推荐使用环境变量：`OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`。
- 配置回退路径为 `gateway.auth.token` / `gateway.auth.password`；在远程模式下，`gateway.remote.token` / `gateway.remote.password` 同样有效。
- 旧版 `CLAWDBOT_GATEWAY_*` 环境变量在节点主机认证解析过程中被**有意忽略**。

### 启动节点主机（作为系统服务）

```bash
openclaw node install --host <gateway-host> --port 18789 --display-name "Build Node"
openclaw node restart
```

### 配对并命名

在网关主机上执行：

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw nodes status
```

命名选项：

- 在 `openclaw node run` / `openclaw node install` 上设置 `--display-name`（该名称将持久化保存于节点上的 `~/.openclaw/node.json` 中）。
- `openclaw nodes rename --node <id|name|ip> --name "Build Node"`（网关级覆盖命名）。

### 命令白名单

执行审批（exec approvals）按 **节点主机** 独立管理。请从网关添加白名单条目：

```bash
openclaw approvals allowlist add --node <id|name|ip> "/usr/bin/uname"
openclaw approvals allowlist add --node <id|name|ip> "/usr/bin/sw_vers"
```

审批记录保存在节点主机的 `~/.openclaw/exec-approvals.json` 路径下。

### 将 exec 指向节点

配置默认值（网关配置）：

```bash
openclaw config set tools.exec.host node
openclaw config set tools.exec.security allowlist
openclaw config set tools.exec.node "<id-or-name>"
```

或按会话单独配置：

```
/exec host=node security=allowlist node=<id-or-name>
```

一旦设定，任何带有 `host=node` 的 `exec` 调用均将在节点主机上执行（受节点白名单/审批规则约束）。

相关文档：

- [节点主机 CLI](/cli/node)
- [Exec 工具](/tools/exec)
- [Exec 审批机制](/tools/exec-approvals)

## 调用命令

底层（原始 RPC）调用：

```bash
openclaw nodes invoke --node <idOrNameOrIp> --command canvas.eval --params '{"javaScript":"location.href"}'
```

针对常见的“向智能体提供媒体附件（MEDIA attachment）”工作流，也提供了更高级别的辅助函数。

## 截图（画布快照）

若节点正在显示画布（Canvas，即 WebView），则 `canvas.snapshot` 将返回 `{ format, base64 }`。

CLI 辅助命令（写入临时文件并打印 `MEDIA:<path>`）：

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

- `canvas present` 接受 URL 或本地文件路径（`--target`），并支持可选的 `--x/--y/--width/--height` 参数用于定位。
- `canvas eval` 接受内联 JavaScript（`--js`）或一个位置参数。

### A2UI（画布）

```bash
openclaw nodes canvas a2ui push --node <idOrNameOrIp> --text "Hello"
openclaw nodes canvas a2ui push --node <idOrNameOrIp> --jsonl ./payload.jsonl
openclaw nodes canvas a2ui reset --node <idOrNameOrIp>
```

注意事项：

- 仅支持 A2UI v0.8 JSONL 格式（v0.9/createSurface 将被拒绝）。

## 拍照与录像（节点摄像头）

拍照（`jpg`）：

```bash
openclaw nodes camera list --node <idOrNameOrIp>
openclaw nodes camera snap --node <idOrNameOrIp>            # default: both facings (2 MEDIA lines)
openclaw nodes camera snap --node <idOrNameOrIp> --facing front
```

录制视频片段（`mp4`）：

```bash
openclaw nodes camera clip --node <idOrNameOrIp> --duration 10s
openclaw nodes camera clip --node <idOrNameOrIp> --duration 3000 --no-audio
```

注意事项：

- 对于 `canvas.*` 和 `camera.*`，节点必须处于 **前台运行状态**（后台调用将返回 `NODE_BACKGROUND_UNAVAILABLE`）。
- 视频片段时长受到限制（当前为 `<= 60s`），以避免生成过大的 base64 负载。
- Android 设备在可能的情况下会提示用户授予 `CAMERA`/`RECORD_AUDIO` 权限；若权限被拒绝，则调用失败并返回 `*_PERMISSION_REQUIRED`。

## 屏幕录制（节点）

节点提供 `screen.record`（MP4 格式）。示例：

```bash
openclaw nodes screen record --node <idOrNameOrIp> --duration 10s --fps 10
openclaw nodes screen record --node <idOrNameOrIp> --duration 10s --fps 10 --no-audio
```

注意事项：

- `screen.record` 要求节点应用处于前台运行状态。
- Android 将在开始录制前显示系统级屏幕录制提示。
- 屏幕录制时长上限为 `<= 60s`。
- `--no-audio` 可禁用麦克风音频采集（iOS/Android 支持；macOS 使用系统级音频采集）。
- 当存在多个显示器时，可使用 `--screen <index>` 指定目标显示器。

## 定位信息（节点）

当设置中启用“定位”功能后，节点将暴露 `location.get`。

CLI 辅助命令：

```bash
openclaw nodes location get --node <idOrNameOrIp>
openclaw nodes location get --node <idOrNameOrIp> --accuracy precise --max-age 15000 --location-timeout 10000
```

注意事项：

- 定位功能 **默认关闭**。
- “始终允许”需获得系统级权限；后台获取定位信息为尽力而为（best-effort）。
- 返回结果包含纬度/经度、精度（单位：米）及时间戳。

## 短信（Android 节点）

当用户授予 **短信（SMS）** 权限且设备支持电话功能时，Android 节点可暴露 `sms.send`。

底层调用方式：

```bash
openclaw nodes invoke --node <idOrNameOrIp> --command sms.send --params '{"to":"+15555550123","message":"Hello from OpenClaw"}'
```

注意事项：

- 必须先在 Android 设备上接受权限提示，该能力才会对外宣告。
- 不具备电话功能的纯 Wi-Fi 设备不会宣告 `sms.send`。

## Android 设备与个人数据命令

当对应的功能权限启用后，Android 节点可宣告更多命令族（command families）。

可用命令族包括：

- `device.status`、`device.info`、`device.permissions`、`device.health`
- `notifications.list`、`notifications.actions`
- `photos.latest`
- `contacts.search`、`contacts.add`
- `calendar.events`、`calendar.add`
- `motion.activity`、`motion.pedometer`
- `app.update`

调用示例：

```bash
openclaw nodes invoke --node <idOrNameOrIp> --command device.status --params '{}'
openclaw nodes invoke --node <idOrNameOrIp> --command notifications.list --params '{}'
openclaw nodes invoke --node <idOrNameOrIp> --command photos.latest --params '{"limit":1}'
```

注意事项：

- 运动类命令受设备所配备传感器能力的限制。
- `app.update` 同时受节点运行时的权限与策略管控。

## 系统命令（节点主机 / macOS 节点）

macOS 节点暴露 `system.run`、`system.notify` 和 `system.execApprovals.get/set`。  
无头节点主机暴露 `system.run`、`system.which` 和 `system.execApprovals.get/set`。

示例：

```bash
openclaw nodes run --node <idOrNameOrIp> -- echo "Hello from mac node"
openclaw nodes notify --node <idOrNameOrIp> --title "Ping" --body "Gateway ready"
```

注意事项：

- `system.run` 在有效载荷中返回 stdout/stderr/退出码。  
- `system.notify` 尊重 macOS 应用的系统通知权限状态。  
- 对于未识别的节点 `platform` / `deviceFamily` 元数据，采用保守的默认白名单策略，该策略排除了 `system.run` 和 `system.which`。若您确需在未知平台上使用这些命令，请通过 `gateway.nodes.allowCommands` 显式添加。  
- `system.run` 支持 `--cwd`、`--env KEY=VAL`、`--command-timeout` 和 `--needs-screen-recording`。  
- 对于 Shell 封装器（`bash|sh|zsh ... -c/-lc`），请求作用域内的 `--env` 值将被缩减为显式白名单（`TERM`、`LANG`、`LC_*`、`COLORTERM`、`NO_COLOR`、`FORCE_COLOR`）。  
- 在白名单模式下，对于“始终允许”类决策，已知的分发封装器（`env`、`nice`、`nohup`、`stdbuf`、`timeout`）会持久化其内部可执行文件路径，而非封装器路径。若解包操作不安全，则不会自动持久化任何白名单条目。  
- 在 Windows 节点主机的白名单模式下，通过 `cmd.exe /c` 运行的 Shell 封装器需单独获得批准（仅存在白名单条目本身并不自动允许该封装器形式）。  
- `system.notify` 支持 `--priority <passive|active|timeSensitive>` 和 `--delivery <system|overlay|auto>`。  
- 节点主机会忽略 `PATH` 的覆盖设置，并剥离危险的启动/Shell 键（`DYLD_*`、`LD_*`、`NODE_OPTIONS`、`PYTHON*`、`PERL*`、`RUBYOPT`、`SHELLOPTS`、`PS4`）。如需额外的 PATH 条目，请配置节点主机服务环境（或在标准位置安装工具），而非通过 `--env` 传递 `PATH`。  
- 在 macOS 节点模式下，`system.run` 受限于 macOS 应用中的执行审批（设置 → 执行审批）。  
  “询问/白名单/完全允许”行为与无头节点主机一致；被拒绝的提示将返回 `SYSTEM_RUN_DENIED`。  
- 在无头节点主机上，`system.run` 受执行审批（`~/.openclaw/exec-approvals.json`）管控。

## 执行节点绑定

当存在多个节点时，您可以将 exec 绑定到特定节点。  
此操作将为 `exec host=node` 设置默认节点（并可在每个代理级别进行覆盖）。

全局默认值：

```bash
openclaw config set tools.exec.node "node-id-or-name"
```

按代理覆盖：

```bash
openclaw config get agents.list
openclaw config set agents.list[0].tools.exec.node "node-id-or-name"
```

取消设置以允许任意节点：

```bash
openclaw config unset tools.exec.node
openclaw config unset agents.list[0].tools.exec.node
```

## 权限映射表

节点可在 `node.list` / `node.describe` 中包含一个 `permissions` 映射表，其键为权限名称（例如 `screenRecording`、`accessibility`），值为布尔类型（`true` = 已授予）。

## 无头节点主机（跨平台）

OpenClaw 可运行一个**无头节点主机**（无用户界面），该主机连接至 Gateway WebSocket 并暴露 `system.run` / `system.which`。此功能适用于 Linux/Windows 环境，或用于在服务器旁运行轻量级节点。

启动方式：

```bash
openclaw node run --host <gateway-host> --port 18789
```

注意事项：

- 仍需配对（Gateway 将显示设备配对提示）。  
- 节点主机将其节点 ID、令牌、显示名称及网关连接信息存储于 `~/.openclaw/node.json`。  
- 执行审批通过本地 `~/.openclaw/exec-approvals.json` 强制执行（参见 [执行审批](/tools/exec-approvals)）。  
- 在 macOS 上，无头节点主机默认在本地执行 `system.run`。设置 `OPENCLAW_NODE_EXEC_HOST=app` 可将 `system.run` 通过配套应用的执行主机路由；添加 `OPENCLAW_NODE_EXEC_FALLBACK=0` 则强制要求应用主机可用，若不可用则直接失败。  
- 当 Gateway WebSocket 使用 TLS 时，请添加 `--tls` / `--tls-fingerprint`。

## macOS 节点模式

- macOS 菜单栏应用作为节点连接至 Gateway WebSocket 服务器（因此 `openclaw nodes …` 可针对本 Mac 执行）。  
- 在远程模式下，该应用为 Gateway 端口打开一个 SSH 隧道，并连接至 `localhost`。