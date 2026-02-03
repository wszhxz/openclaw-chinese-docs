---
summary: "Loopback WebChat static host and Gateway WS usage for chat UI"
read_when:
  - Debugging or configuring WebChat access
title: "WebChat"
---
# WebChat（网关WebSocket用户界面）

状态：macOS/iOS SwiftUI聊天用户界面直接与网关WebSocket通信。

## 什么是WebChat

- 用于网关的原生聊天用户界面（无嵌入式浏览器和本地静态服务器）。
- 使用与其他通道相同的会话和路由规则。
- 确定性路由：回复始终返回到WebChat。

## 快速入门

1. 启动网关。
2. 打开WebChat用户界面（macOS/iOS应用）或控制台用户界面的聊天标签页。
3. 确保网关认证已配置（默认情况下必需，即使使用回环接口）。

## 工作原理（行为）

- 用户界面连接到网关WebSocket，并使用`chat.history`、`chat.send`和`chat.inject`。
- `chat.inject`将助手备注直接附加到对话记录并广播到用户界面（无需代理运行）。
- 历史记录始终从网关获取（无需本地文件监控）。
- 如果网关不可达，WebChat将只读。

## 远程使用

- 远程模式通过SSH/Tailscale隧道传输网关WebSocket。
- 无需运行独立的WebChat服务器。

## 配置参考（WebChat）

完整配置：[配置](/gateway/configuration)

通道选项：

- 无专用`webchat.*`块。WebChat使用网关端点和以下认证设置。

相关全局选项：

- `gateway.port`、`gateway.bind`：WebSocket主机/端口。
- `gateway.auth.mode`、`gateway.auth.token`、`gateway.auth.password`：WebSocket认证。
- `gateway.remote.url`、`gateway.remote.token`、`gateway.remote.password`：远程网关目标。
- `session.*`：会话存储和主密钥默认值。