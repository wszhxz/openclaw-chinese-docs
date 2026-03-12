---
summary: "Android app (node): connection runbook + Connect/Chat/Voice/Canvas command surface"
read_when:
  - Pairing or reconnecting the Android node
  - Debugging Android gateway discovery or auth
  - Verifying chat history parity across clients
title: "Android App"
---
# Android App (Node)

## 支持快照

- 角色：伴侣节点应用（Android不托管网关）。
- 是否需要网关：是（在macOS、Linux或通过WSL2的Windows上运行）。
- 安装：[入门](/start/getting-started) + [配对](/channels/pairing)。
- 网关：[运行手册](/gateway) + [配置](/gateway/configuration)。
  - 协议：[网关协议](/gateway/protocol)（节点+控制平面）。

## 系统控制

系统控制（launchd/systemd）位于网关主机上。请参见[网关](/gateway)。

## 连接运行手册

Android节点应用 ⇄ (mDNS/NSD + WebSocket) ⇄ **网关**

Android直接连接到网关WebSocket（默认`ws://<host>:18789`），并使用设备配对(`role: node`)。

### 前提条件

- 您可以在“主”机器上运行网关。
- Android设备/模拟器可以访问网关WebSocket：
  - 同一局域网内使用mDNS/NSD，**或者**
  - 使用Wide-Area Bonjour / 单播DNS-SD的同一Tailscale尾网（见下文），**或者**
  - 手动网关主机/端口（备用）
- 您可以在网关机器上运行CLI(`openclaw`)（或通过SSH）。

### 1) 启动网关

```bash
openclaw gateway --port 18789 --verbose
```

确认日志中看到类似以下内容：

- `listening on ws://0.0.0.0:18789`

对于仅尾网设置（建议用于Vienna ⇄ London），将网关绑定到尾网IP：

- 在网关主机上的`~/.openclaw/openclaw.json`中设置`gateway.bind: "tailnet"`。
- 重启网关/macOS菜单栏应用。

### 2) 验证发现（可选）

从网关机器：

```bash
dns-sd -B _openclaw-gw._tcp local.
```

更多调试说明：[Bonjour](/gateway/bonjour)。

#### 通过单播DNS-SD进行尾网（Vienna ⇄ London）发现

Android NSD/mDNS发现不会跨越网络。如果您的Android节点和网关位于不同的网络但通过Tailscale连接，请改用Wide-Area Bonjour / 单播DNS-SD：

1. 在网关主机上设置一个DNS-SD区域（示例`openclaw.internal.`）并发布`_openclaw-gw._tcp`记录。
2. 为所选域名配置指向该DNS服务器的Tailscale拆分DNS。

详细信息和CoreDNS配置示例：[Bonjour](/gateway/bonjour)。

### 3) 从Android连接

在Android应用中：

- 应用通过**前台服务**（持久通知）保持其网关连接活跃。
- 打开**连接**标签页。
- 使用**设置代码**或**手动**模式。
- 如果发现被阻止，在**高级控制**中使用手动主机/端口（以及需要时的TLS/令牌/密码）。

首次成功配对后，Android会在启动时自动重新连接：

- 手动端点（如果启用），否则
- 最近发现的网关（尽力而为）。

### 4) 批准配对（CLI）

在网关机器上：

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw devices reject <requestId>
```

配对详情：[配对](/channels/pairing)。

### 5) 验证节点已连接

- 通过节点状态：

  ```bash
  openclaw nodes status
  ```

- 通过网关：

  ```bash
  openclaw gateway call node.list --params "{}"
  ```

### 6) 聊天+历史

Android聊天标签页支持会话选择（默认`main`，以及其他现有会话）：

- 历史：`chat.history`
- 发送：`chat.send`
- 推送更新（尽力而为）：`chat.subscribe` → `event:"chat"`

### 7) 画布+屏幕+摄像头

#### 网关画布主机（推荐用于网页内容）

如果您希望节点显示代理可以在磁盘上编辑的真实HTML/CSS/JS，请将节点指向网关画布主机。

注意：节点从网关HTTP服务器加载画布（与`gateway.port`相同端口，默认`18789`）。

1. 在网关主机上创建`~/.openclaw/workspace/canvas/index.html`。

2. 导航节点至它（局域网）：

```bash
openclaw nodes invoke --node "<Android Node>" --command canvas.navigate --params '{"url":"http://<gateway-hostname>.local:18789/__openclaw__/canvas/"}'
```

尾网（可选）：如果两台设备都在Tailscale上，使用MagicDNS名称或尾网IP代替`.local`，例如`http://<gateway-magicdns>:18789/__openclaw__/canvas/`。

此服务器将实时重载客户端注入到HTML中，并在文件更改时重载。
A2UI主机位于`http://<gateway-host>:18789/__openclaw__/a2ui/`。

画布命令（仅前景）：

- `canvas.eval`, `canvas.snapshot`, `canvas.navigate`（使用`{"url":""}`或`{"url":"/"}`返回默认框架）。`canvas.snapshot` 返回 `{ format, base64 }`（默认`format="jpeg"`）。
- A2UI: `canvas.a2ui.push`, `canvas.a2ui.reset` (`canvas.a2ui.pushJSONL` 旧别名)

摄像头命令（仅前景；权限受限）：

- `camera.snap` (jpg)
- `camera.clip` (mp4)

有关参数和CLI助手的信息，请参阅[摄像头节点](/nodes/camera)。

屏幕命令：

- `screen.record` (mp4; 仅前景)

### 8) 语音+扩展的Android命令界面

- 语音：Android在语音标签页中使用单一麦克风开关流程，带有转录捕获和TTS播放（配置ElevenLabs时使用，系统TTS作为后备）。
- 语音唤醒/对话模式切换目前从Android用户体验/运行时中移除。
- 其他Android命令系列（可用性取决于设备+权限）：
  - `device.status`, `device.info`, `device.permissions`, `device.health`
  - `notifications.list`, `notifications.actions`
  - `photos.latest`
  - `contacts.search`, `contacts.add`
  - `calendar.events`, `calendar.add`
  - `motion.activity`, `motion.pedometer`
  - `app.update`