---
summary: "iOS node app: connect to the Gateway, pairing, canvas, and troubleshooting"
read_when:
  - Pairing or reconnecting the iOS node
  - Running the iOS app from source
  - Debugging gateway discovery or canvas commands
title: "iOS App"
---
# iOS App (Node)

可用性：内部预览。iOS应用尚未公开分发。

## 功能

- 通过WebSocket（局域网或tailnet）连接到网关。
- 暴露节点功能：画布、屏幕快照、相机捕获、位置、对话模式、语音唤醒。
- 接收`node.invoke`命令并报告节点状态事件。

## 要求

- 在另一台设备上运行的网关（macOS、Linux或通过WSL2的Windows）。
- 网络路径：
  - 同一局域网通过Bonjour，**或**
  - 通过单播DNS-SD的tailnet（示例域名：`openclaw.internal.`），**或**
  - 手动主机/端口（备用）。

## 快速开始（配对 + 连接）

1. 启动网关：

```bash
openclaw gateway --port 18789
```

2. 在iOS应用中，打开设置并选择一个发现的网关（或启用手动主机并输入主机/端口）。

3. 在网关主机上批准配对请求：

```bash
openclaw nodes pending
openclaw nodes approve <requestId>
```

4. 验证连接：

```bash
openclaw nodes status
openclaw gateway call node.list --params "{}"
```

## 发现路径

### Bonjour（局域网）

网关在`local.`上广播`_openclaw-gw._tcp`。iOS应用会自动列出这些。

### Tailnet（跨网络）

如果mDNS被阻止，请使用单播DNS-SD区域（选择一个域名；示例：`openclaw.internal.`）和Tailscale拆分DNS。
有关CoreDNS示例，请参见[Bonjour](/gateway/bonjour)。

### 手动主机/端口

在设置中启用**手动主机**并输入网关主机+端口（默认`18789`）。

## Canvas + A2UI

iOS节点渲染一个WKWebView画布。使用`node.invoke`来驱动它：

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.navigate --params '{"url":"http://<gateway-host>:18793/__openclaw__/canvas/"}'
```

注意事项：

- 网关画布主机提供`/__openclaw__/canvas/`和`/__openclaw__/a2ui/`。
- 当连接时广告了画布主机URL，iOS节点会自动导航到A2UI。
- 使用`canvas.navigate`和`{"url":""}`返回内置脚手架。

### Canvas eval / 快照

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.eval --params '{"javaScript":"(() => { const {ctx} = window.__openclaw; ctx.clearRect(0,0,innerWidth,innerHeight); ctx.lineWidth=6; ctx.strokeStyle=\"#ff2d55\"; ctx.beginPath(); ctx.moveTo(40,40); ctx.lineTo(innerWidth-40, innerHeight-40); ctx.stroke(); return \"ok\"; })()"}'
```

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.snapshot --params '{"maxWidth":900,"format":"jpeg"}'
```

## 语音唤醒 + 对话模式

- 语音唤醒和对话模式在设置中可用。
- 当应用不活动时，iOS可能会挂起后台音频；将语音功能视为尽力而为。

## 常见错误

- `NODE_BACKGROUND_UNAVAILABLE`：将iOS应用带到前台（画布/相机/屏幕命令需要它）。
- `A2UI_HOST_NOT_CONFIGURED`：网关没有广告画布主机URL；检查[网关配置](/gateway/configuration)中的`canvasHost`。
- 配对提示从未出现：运行`openclaw nodes pending`并手动批准。
- 重新安装后重新连接失败：密钥链配对令牌已被清除；重新配对节点。

## 相关文档

- [配对](/gateway/pairing)
- [发现](/gateway/discovery)
- [Bonjour](/gateway/bonjour)