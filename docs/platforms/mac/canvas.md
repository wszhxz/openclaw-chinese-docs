---
summary: "Agent-controlled Canvas panel embedded via WKWebView + custom URL scheme"
read_when:
  - Implementing the macOS Canvas panel
  - Adding agent controls for visual workspace
  - Debugging WKWebView canvas loads
title: "Canvas"
---
# 画布（macOS 应用）

该 macOS 应用通过 `WKWebView` 嵌入了一个由代理控制的 **画布面板**。它是一个轻量级的可视化工作区，支持 HTML/CSS/JS、A2UI 以及小型交互式 UI 表面。

## 画布的位置

画布状态存储在应用程序支持目录下：

- `~/Library/Application Support/OpenClaw/canvas/<session>/...`

画布面板通过 **自定义 URL 方案** 提供这些文件：

- `openclaw-canvas://<session>/<path>`

示例：

- `open

openclaw-canvas://main/` → `<canvasRoot>/main/index.html`
- `openclaw-canvas://main/assets/app.css` → `<canvasRoot>/main/assets/app.css`
- `openclaw-canvas://main/widgets/todo/` → `<canvasRoot>/main/widgets/todo/index.html`

如果根目录下没有 `index.html`，应用将显示一个 **内置的骨架页面**。

## 面板行为

- 无边框、可调整大小的面板，靠近菜单栏（或鼠标光标）固定。
- 按会话记住大小和位置。
- 当本地画布文件更改时自动重新加载。
- 每次只显示一个画布面板（会话切换时自动切换）。

可以在设置中禁用画布：设置 → **允许画布**。禁用后，画布节点命令将返回 `CANVAS_DISABLED`。

## 代理 API 接口

画布通过 **网关 WebSocket** 暴露，因此代理可以：

- 显示/隐藏面板
- 跳转到路径或 URL
- 评估 JavaScript
- 捕获快照图像

CLI 示例：

```bash
openclaw nodes canvas present --node <id>
openclaw nodes canvas navigate --node <id> --url "/"
openclaw nodes canvas eval --node <id> --js "document.title"
openclaw nodes canvas snapshot --node <id>
```

说明：

- `canvas.navigate` 接受 **本地画布路径**、`http(s)` URL 和 `file://` URL。
- 如果传递 `"/"`，画布将显示本地骨架页面或 `index.html`。

## 画布中的 A2UI

A2UI 由网关画布主机托管，并在画布面板内渲染。当网关宣布一个画布主机时，macOS 应用在首次打开时会自动导航到 A2UI 主机页面。

默认 A2UI 主机 URL：

```
http://<gateway-host>:18793/__openclaw__/a2ui/
```

### A2UI 命令（v0.8）

当前画布接受 **A2UI v0.8** 服务器→客户端消息：

- `beginRendering`
- `surfaceUpdate`
- `dataModelUpdate`
- `deleteSurface`

`createSurface`（v0.9）不被支持。

CLI 示例：

```bash
cat > /tmp/a2ui-v0.8.jsonl <<'EOFA2'
{"surfaceUpdate":{"surfaceId":"main","components":[{"id":"root","component":{"Column":{"children":{"explicitList":["title","content"]}}}},{"id":"title","component":{"Text":{"text":{"literalString":"Canvas (A2UI v0.8)","usageHint":"h1"}}},{"id":"content","component":{"Text":{"text":{"literalString":"If you can read this, A2UI push works."},"usageHint":"body"}}}]}}
{"beginRendering":{"surfaceId":"main","root":"root"}}
EOFA2

openclaw nodes canvas a2ui push --jsonl /tmp/a2ui-v0.8.jsonl --node <id>
```

快速测试：

```bash
openclaw nodes canvas a2ui push --node <id> --text "Hello from A2UI"
```

## 从画布触发代理运行

画布可通过深度链接触发新的代理运行：

- `openclaw://agent?...`

示例（在 JS 中）：

```js
window.location.href = "openclaw://agent?message=Review%20this%20design";
```

除非提供有效的密钥，否则应用会提示确认。

## 安全说明

- 画布方案阻止目录遍历；文件必须位于会话根目录下。
- 本地画布内容使用自定义方案（无需回环服务器）。
- 外部 `http(s)` URL 仅在显式导航时允许。