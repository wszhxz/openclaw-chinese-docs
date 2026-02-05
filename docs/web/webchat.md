---
summary: "Loopback WebChat static host and Gateway WS usage for chat UI"
read_when:
  - Debugging or configuring WebChat access
title: "WebChat"
---
# WebChat (Gateway WebSocket UI)

状态：macOS/iOS SwiftUI 聊天界面直接与 Gateway WebSocket 进行通信。

## 什么是它

- 网关的原生聊天界面（不嵌入浏览器且无需本地静态服务器）。
- 使用与其他通道相同的会话和路由规则。
- 确定性路由：回复总是返回到 WebChat。

## 快速开始

1. 启动网关。
2. 打开 WebChat 界面（macOS/iOS 应用）或控制界面聊天标签。
3. 确保网关认证已配置（默认情况下需要，即使在回环接口上也是如此）。

## 工作原理（行为）

- 界面连接到 Gateway WebSocket 并使用 `chat.history`，`chat.send` 和 `chat.inject`。
- `chat.inject` 直接将助手备注附加到对话记录并广播到界面（无需运行代理）。
- 历史记录始终从网关获取（不监视本地文件）。
- 如果网关无法访问，WebChat 为只读模式。

## 远程使用

- 远程模式通过 SSH/Tailscale 隧道网关 WebSocket。
- 您无需运行单独的 WebChat 服务器。

## 配置参考（WebChat）

完整配置：[Configuration](/gateway/configuration)

通道选项：

- 没有专用的 `webchat.*` 块。WebChat 使用网关端点 + 下方的认证设置。

相关全局选项：

- `gateway.port`，`gateway.bind`：WebSocket 主机/端口。
- `gateway.auth.mode`，`gateway.auth.token`，`gateway.auth.password`：WebSocket 认证。
- `gateway.remote.url`，`gateway.remote.token`，`gateway.remote.password`：远程网关目标。
- `session.*`：会话存储和主密钥默认值。