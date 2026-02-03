---
summary: "Nodes: pairing, capabilities, permissions, and CLI helpers for canvas/camera/screen/system"
read_when:
  - Pairing iOS/Android nodes to a gateway
  - Using node canvas/camera for agent context
  - Adding new node commands or CLI helpers
title: "Nodes"
---
# 节点

一个 **节点** 是一个配套设备（macOS/iOS/Android/无头模式），通过 `role: "node"` 连接到网关 **WebSocket**（与操作员相同的端口），并通过 `node.invoke` 暴露命令接口（例如 `canvas.*`、`camera.*`、`system.*`）。协议详情：[网关协议](/gateway/protocol)。

旧传输方式：[桥接协议](/gateway/bridge-protocol)（TCP JSONL；当前节点已弃用/移除）。

macOS 也可以以 **节点模式** 运行：菜单栏应用连接到网关的 WS 服务器，并将本地画布/摄像头命令作为节点暴露（因此 `openclaw nodes …` 可以针对此 Mac 运行）。

说明：

- 节点是 **外设**，不是网关。它们不运行网关服务。
- Telegram/WhatsApp 等消息会发送到 **网关**，而不是节点。

## 配对 + 状态

**WS 节点使用设备配对。** 节点在 `connect` 时提供设备身份；网关会为 `role: node` 创建设备配对请求。通过设备 CLI（或 UI）批准。

快速 CLI：

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw devices reject <requestId>
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
```

说明：

- `nodes status` 会在节点的设备配对角色包含 `node` 时将其标记为 **已配对**。
- `node.pair.*`（CLI：`openclaw nodes pending/approve/reject`）是网关拥有的独立节点配对存储；它 **不** 控制 WS `connect` 握手。

## 远程节点主机（system.run）

当网关运行在一台机器上，而你希望命令在另一台机器上执行时，使用 **节点主机**。模型仍然与 **网关** 通信；当选择 `host=node` 时，网关会将 `exec` 调用转发到 **节点主机**。

### 哪里运行什么

- **网关主机**：接收消息，运行模型，路由工具调用。
- **节点主机**：在节点机器上执行 `system.run`/`system.which`。
- **审批**：通过 `~/.openclaw/exec-approvals.json` 在节点主机上强制执行。

### 启动节点主机（前台）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789
```

### 启动节点主机（后台）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --daemon
```

### 启动节点主机（指定路径）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --working-directory /path/to/dir
```

### 启动节点主机（指定环境变量）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --env KEY=VALUE
```

### 启动节点主机（指定超时时间）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --command-timeout 30
```

### 启动节点主机（指定需要屏幕录制）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --needs-screen-recording
```

### 启动节点主机（指定优先级）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --priority passive
```

### 启动节点、主机（指定交付方式）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --delivery system
```

### 启动节点主机（指定 TLS）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --tls
```

### 启动节点主机（指定 TLS 指纹）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --tls-fingerprint <fingerprint>
```

### 启动节点主机（指定节点 ID）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --node-id <node-id>
```

### 启动节点主机（指定节点名称）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --node-name <node-name>
```

### 启动节点主机（指定节点令牌）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --node-token <node-token>
```

### 启动节点主机（指定节点显示名称）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --node-display-name <node-display-name>
```

### 启动节点主机（指定节点连接信息）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --node-connection-info <node-connection-info>
```

### 启动节点主机（指定节点配置文件）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --node-config <node-config>
```

### 启动节点主机（指定节点日志级别）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --log-level debug
```

### 启动节点主机（指定节点日志文件）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --log-file /path/to/logfile.log
```

### 启动节点主机（指定节点日志格式）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --log-format json
```

### 启动节点主机（指定节点日志轮转）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --log-rotate daily
```

### 启动节点主机（指定节点日志保留天数）

在节点机器上：

```bash
openclaw node run --host <gateway-host> --port 18789 --log-keep 30
```

### 启