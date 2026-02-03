---
summary: "How the mac app embeds the gateway WebChat and how to debug it"
read_when:
  - Debugging mac WebChat view or loopback port
title: "WebChat"
---
# WebChat（macOS应用）

macOS菜单栏应用将WebChat UI作为原生SwiftUI视图嵌入。它连接到网关，默认使用选定代理的**主会话**（可通过会话切换器切换其他会话）。

- **本地模式**：直接连接到本地网关WebSocket。
- **远程模式**：通过SSH转发网关控制端口，并使用该隧道作为数据平面。

## 启动与调试

- 手动：Lobster菜单 → “打开聊天”。
- 测试自动打开：
  ```bash
  dist/OpenClaw.app/Contents/MacOS/OpenClaw --webchat
  ```
- 日志：`./scripts/clawlog.sh`（子系统 `bot.molt`，类别 `WebChatSwiftUI`）。

## 连接方式

- 数据平面：网关WS方法 `chat.history`、`chat.send`、`chat.abort`、`chat.inject` 以及事件 `chat`、`agent`、`presence`、`tick`、`health`。
- 会话：默认使用主会话（`main`，或 `global` 当作用域为全局时）。UI可切换不同会话。
- 入门流程使用专用会话，以保持首次运行设置独立。

## 安全面

- 远程模式仅通过SSH转发网关WebSocket控制端口。

## 已知限制

- UI优化用于聊天会话（非完整的浏览器沙盒）。