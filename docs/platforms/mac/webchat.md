---
summary: "How the mac app embeds the gateway WebChat and how to debug it"
read_when:
  - Debugging mac WebChat view or loopback port
title: "WebChat"
---
# WebChat (macOS app)

macOS菜单栏应用程序将WebChat UI嵌入为一个原生的SwiftUI视图。它连接到网关，并默认选择代理的**主会话**（带有会话切换器以供其他会话使用）。

- **本地模式**：直接连接到本地网关WebSocket。
- **远程模式**：通过SSH转发网关控制端口，并使用该隧道作为数据平面。

## 启动与调试

- 手动：Lobster菜单 → “打开聊天”。
- 测试时自动打开：

  ```bash
  dist/OpenClaw.app/Contents/MacOS/OpenClaw --webchat
  ```

- 日志：`./scripts/clawlog.sh`（子系统 `ai.openclaw`，类别 `WebChatSwiftUI`）。

## 连接方式

- 数据平面：网关WS方法 `chat.history`, `chat.send`, `chat.abort`,
  `chat.inject` 和事件 `chat`, `agent`, `presence`, `tick`, `health`。
- 会话：默认为主会话 (`main`, 或者当范围是全局时为 `global`)。用户界面可以在会话之间切换。
- 引导使用专用会话，以保持首次运行设置的独立性。

## 安全面

- 远程模式仅通过SSH转发网关WebSocket控制端口。

## 已知限制

- 用户界面针对聊天会话进行了优化（不是一个完整的浏览器沙箱）。