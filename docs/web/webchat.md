---
summary: "Loopback WebChat static host and Gateway WS usage for chat UI"
read_when:
  - Debugging or configuring WebChat access
title: "WebChat"
---
# WebChat (Gateway WebSocket UI)

状态：macOS/iOS SwiftUI聊天界面直接与Gateway WebSocket通信。

## 什么是它

- 一个原生的网关聊天界面（不嵌入浏览器且没有本地静态服务器）。
- 使用与其他通道相同的会话和路由规则。
- 确定性路由：回复总是返回到WebChat。

## 快速开始

1. 启动网关。
2. 打开WebChat UI（macOS/iOS应用）或Control UI聊天标签。
3. 确保网关认证已配置（默认情况下需要，即使在回环中也是如此）。

## 工作原理（行为）

- 用户界面连接到网关WebSocket并使用`chat.history`，`chat.send`，和`chat.inject`。
- `chat.inject`直接将助手备注附加到记录中，并将其广播到用户界面（无需运行代理）。
- 历史记录始终从网关获取（不监视本地文件）。
- 如果网关无法访问，WebChat为只读模式。

## 远程使用

- 远程模式通过SSH/Tailscale隧道传输网关WebSocket。
- 您不需要运行单独的WebChat服务器。

## 配置参考（WebChat）

完整配置：[Configuration](/gateway/configuration)

通道选项：

- 没有专用的`webchat.*`块。WebChat使用网关端点+以下认证设置。

相关全局选项：

- `gateway.port`，`gateway.bind`：WebSocket主机/端口。
- `gateway.auth.mode`，`gateway.auth.token`，`gateway.auth.password`：WebSocket认证。
- `gateway.remote.url`，`gateway.remote.token`，`gateway.remote.password`：远程网关目标。
- `session.*`：会话存储和主密钥默认值。