---
summary: "iOS node app: connect to the Gateway, pairing, canvas, and troubleshooting"
read_when:
  - Pairing or reconnecting the iOS node
  - Running the iOS app from source
  - Debugging gateway discovery or canvas commands
title: "iOS App"
---
# iOS 应用（节点）

可用性：内部预览。iOS 应用尚未公开分发。

## 功能说明

- 通过 WebSocket 连接到网关（局域网或 tailnet）。
- 暴露节点功能：画布、屏幕快照、摄像头捕获、位置、对话模式、语音唤醒。
- 接收 `node.invoke` 命令并报告节点状态事件。

## 要求

- 网关需在另一设备上运行（macOS、Linux 或通过 WSL2 的 Windows）。
- 网络路径：
  - 通过 Bonjour 在同一局域网内，**或**
  - 通过 unicast DNS-SD 在 tailnet 中（示例域名：`openclaw.internal.`），**或**
  - 手动输入主机和端口（回退方式）。

## 快速入门（配对 + 连接）

1. 启动网关：

```bash
openclaw gateway --port 18789
```

2. 在 iOS 应用中打开设置，选择发现的网关（或启用手动主机并输入主机/端口）。

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

网关在 `local.` 上广播 `_openclaw-gw._tcp`。iOS 应用会自动列出这些网关。

### Tailnet（跨网络）

如果 mDNS 被阻止，使用 unicast DNS-SD 区域（选择一个域；示例：`openclaw.internal.`）和 Tailscale 分割 DNS。
查看 [Bonjour](/gateway/bonjour) 了解 CoreDNS 示例。

### 手动主机/端口

在设置中启用 **手动主机**，并输入网关主机 + 端口（默认 `18789`）。

## 画布 + A2UI

iOS 节点渲染一个 WKWebView 画布。使用 `node.invoke` 来驱动它：

```bash
openclaw nodes invoke --node "iOS 节点" --command canvas.navigate --params '{"url":"http://<gateway-host>:18793/__openclaw__/canvas/"}'
```

说明：

- 网关画布主机提供 `/__openclaw__/canvas/` 和 `/__openclaw__/a2ui/`。
- 当连接时，iOS 节点会自动导航到 A2UI（如果广告了画布主机 URL）。
- 使用 `canvas.navigate` 和 `{"url":""}` 返回内置框架。

### 画布评估 / 快照

```bash
openclaw nodes invoke --node "iOS 节点" --command canvas.eval --params '{"javaScript":"(() => { const {ctx} = window.__openclaw; ctx.clearRect(0,0,innerWidth,innerHeight); ctx.lineWidth=6; ctx.strokeStyle=\"#ff2d55\"; ctx.beginPath(); ctx.moveTo(40,40); ctx.lineTo(innerWidth-40, innerHeight-40); ctx.stroke(); return \"ok\"; })()"}'
```

```bash
openclaw nodes invoke --node "iOS 节点" --command canvas.snapshot --params '{"maxWidth":900,"format":"jpeg"}'
```

## 语音唤醒 + 对话模式

- 语音唤醒和对话模式可在设置中启用。
- iOS 可能会暂停后台音频；当应用未激活时，将语音功能视为尽力而为。

## 常见错误

- `NODE_BACKGROUND_UNAVAILABLE`：将 iOS 应用带到前台（画布/摄像头/屏幕命令需要它）。
- `A2UI_HOST_NOT_CONFIGURED`：网关未广告画布主机 URL；检查 [网关配置](/gateway/configuration) 中的 `canvasHost`。
- 配对提示从未出现：运行 `openclaw nodes pending` 并手动批准。
- 重新安装后重新连接失败：Keychain 配对令牌已被清除；重新配对节点。

## 相关文档

- [配对](/gateway/pairing)
- [发现](/gateway/discovery)
- [Bonjour](/gateway/bonjour)