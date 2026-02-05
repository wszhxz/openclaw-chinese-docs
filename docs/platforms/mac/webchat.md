---
summary: "How the mac app embeds the gateway WebChat and how to debug it"
read_when:
  - Debugging mac WebChat view or loopback port
title: "WebChat"
---
# WebChat (macOS 应用程序)

macOS 菜单栏应用程序将 WebChat UI 嵌入为原生的 SwiftUI 视图。它
连接到网关，默认使用所选代理人的 **主会话**（并提供其他会话的会话切换器）。

- **本地模式**：直接连接到本地网关 WebSocket。
- **远程模式**：通过 SSH 转发网关控制端口，并使用该隧道作为数据平面。

## 启动与调试

- 手动：Lobster 菜单 → “打开聊天”。
- 测试时自动打开：
  ```bash
  dist/OpenClaw.app/Contents/MacOS/OpenClaw --webchat
  ```
- 日志：`./scripts/clawlog.sh` (子系统 `bot.molt`，类别 `WebChatSwiftUI`)。

## 连接方式

- 数据平面：网关 WS 方法 `chat.history`，`chat.send`，`chat.abort`，
  `chat.inject` 和事件 `chat`，`agent`，`presence`，`tick`，`health`。
- 会话：默认使用主会话 (`main`，或 `global` 当范围为全局)。UI 可以在会话之间切换。
- 入门使用专用会话以保持首次运行设置独立。

## 安全面

- 远程模式仅通过 SSH 转发网关 WebSocket 控制端口。

## 已知限制

- UI 优化用于聊天会话（不是完整的浏览器沙盒）。