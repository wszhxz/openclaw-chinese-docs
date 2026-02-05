---
summary: "Android app (node): connection runbook + Canvas/Chat/Camera"
read_when:
  - Pairing or reconnecting the Android node
  - Debugging Android gateway discovery or auth
  - Verifying chat history parity across clients
title: "Android App"
---
# Android App (Node)

## 支持快照

- 角色：伴侣节点应用（Android 不托管网关）。
- 需要网关：是（通过 WSL2 在 macOS、Linux 或 Windows 上运行）。
- 安装：[入门指南](/start/getting-started) + [配对](/gateway/pairing)。
- 网关：[运行手册](/gateway) + [配置](/gateway/configuration)。
  - 协议：[网关协议](/gateway/protocol)（节点 + 控制平面）。

## 系统控制

系统控制（launchd/systemd）位于网关主机上。参见 [网关](/gateway)。

## 连接运行手册

Android 节点应用 ⇄ (mDNS/NSD + WebSocket) ⇄ **网关**

Android 直接连接到网关 WebSocket（默认 `ws://<host>:18789`）并使用网关拥有的配对。

### 先决条件

- 您可以在“主”机器上运行网关。
- Android 设备/模拟器可以访问网关 WebSocket：
  - 同一局域网使用 mDNS/NSD，**或**
  - 使用 Wide-Area Bonjour / 单播 DNS-SD 的同一 Tailscale 尾网（见下文），**或**
  - 手动指定网关主机/端口（备用）
- 您可以在网关机器上运行 CLI (`openclaw`)（或通过 SSH）。

### 1) 启动网关

```bash
openclaw gateway --port 18789 --verbose
```

确认日志中看到类似以下内容：

- `listening on ws://0.0.0.0:18789`

对于仅尾网设置（推荐用于维也纳 ⇄ 伦敦），将网关绑定到尾网 IP：

- 在网关主机上设置 `gateway.bind: "tailnet"` 在 `~/.openclaw/openclaw.json` 中。
- 重启网关 / macOS 菜单栏应用。

### 2) 验证发现（可选）

从网关机器：

```bash
dns-sd -B _openclaw-gw._tcp local.
```

更多调试说明：[Bonjour](/gateway/bonjour)。

#### 通过单播 DNS-SD 的尾网（维也纳 ⇄ 伦敦）发现

Android NSD/mDNS 发现不会跨网络。如果您的 Android 节点和网关在不同的网络但通过 Tailscale 连接，请改用 Wide-Area Bonjour / 单播 DNS-SD：

1. 在网关主机上设置一个 DNS-SD 区域（示例 `openclaw.internal.`）并发布 `_openclaw-gw._tcp` 记录。
2. 为选定的域名配置 Tailscale 分割 DNS 指向该 DNS 服务器。

详细信息和示例 CoreDNS 配置：[Bonjour](/gateway/bonjour)。

### 3) 从 Android 连接

在 Android 应用中：

- 该应用通过 **前台服务**（持续通知）保持与网关的连接。
- 打开 **设置**。
- 在 **发现的网关** 下，选择您的网关并点击 **连接**。
- 如果 mDNS 被阻止，使用 **高级 → 手动网关**（主机 + 端口）并点击 **手动连接**。

首次成功配对后，Android 在启动时自动重新连接：

- 手动端点（如果启用），否则
- 最后发现的网关（尽力而为）。

### 4) 批准配对（CLI）

在网关机器上：

```bash
openclaw nodes pending
openclaw nodes approve <requestId>
```

配对详情：[网关配对](/gateway/pairing)。

### 5) 验证节点已连接

- 通过节点状态：
  ```bash
  openclaw nodes status
  ```
- 通过网关：
  ```bash
  openclaw gateway call node.list --params "{}"
  ```

### 6) 聊天 + 历史记录

Android 节点的聊天表单使用网关的 **主会话密钥** (`main`)，因此历史记录和回复与 WebChat 和其他客户端共享：

- 历史记录：`chat.history`
- 发送：`chat.send`
- 推送更新（尽力而为）：`chat.subscribe` → `event:"chat"`

### 7) 画布 + 摄像头

#### 网关画布主机（推荐用于网页内容）

如果您希望节点显示代理可以在磁盘上编辑的真实 HTML/CSS/JS，请将节点指向网关画布主机。

注意：节点使用独立的画布主机在 `canvasHost.port`（默认 `18793`）。

1. 在网关主机上创建 `~/.openclaw/workspace/canvas/index.html`。

2. 导航节点到它（局域网）：

```bash
openclaw nodes invoke --node "<Android Node>" --command canvas.navigate --params '{"url":"http://<gateway-hostname>.local:18793/__openclaw__/canvas/"}'
```

尾网（可选）：如果两个设备都在 Tailscale 上，使用 MagicDNS 名称或尾网 IP 而不是 `.local`，例如 `http://<gateway-magicdns>:18793/__openclaw__/canvas/`。

此服务器将实时重载客户端注入到 HTML 并在文件更改时重新加载。
A2UI 主机位于 `http://<gateway-host>:18793/__openclaw__/a2ui/`。

画布命令（仅前台）：

- `canvas.eval`, `canvas.snapshot`, `canvas.navigate`（使用 `{"url":""}` 或 `{"url":"/"}` 返回默认脚手架）。`canvas.snapshot` 返回 `{ format, base64 }`（默认 `format="jpeg"`）。
- A2UI: `canvas.a2ui.push`, `canvas.a2ui.reset` (`canvas.a2ui.pushJSONL` 旧别名)

摄像头命令（仅前台；权限受限）：

- `camera.snap` (jpg)
- `camera.clip` (mp4)

参见 [摄像头节点](/nodes/camera) 了解参数和 CLI 辅助工具。