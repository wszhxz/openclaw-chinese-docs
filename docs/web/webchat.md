---
summary: "Loopback WebChat static host and Gateway WS usage for chat UI"
read_when:
  - Debugging or configuring WebChat access
title: "WebChat"
---
# WebChat（网关WebSocket UI）

状态：macOS/iOS SwiftUI聊天UI直接与网关WebSocket通信。

## 功能介绍

- 网关的原生聊天UI（无嵌入浏览器，无本地静态服务器）。
- 使用与其他通道相同的会话和路由规则。
- 确定性路由：回复始终返回到WebChat。

## 快速开始

1. 启动网关。
2. 打开WebChat UI（macOS/iOS应用）或控制UI聊天标签页。
3. 确保网关认证已配置（默认情况下需要，即使在回环连接上也是如此）。

## 工作原理（行为）

- UI连接到网关WebSocket并使用`chat`, `transcript`, 和 `files`。
- `@gateway`应用直接向对话记录追加助手注释并向UI广播（无代理运行）。
- 历史记录始终从网关获取（无本地文件监控）。
- 如果网关无法访问，WebChat为只读模式。

## 远程使用

- 远程模式通过SSH/Tailscale隧道传输网关WebSocket。
- 您无需运行单独的WebChat服务器。

## 配置参考（WebChat）

完整配置：[配置](/gateway/configuration)

通道选项：

- 无专用的`webchat`块。WebChat使用网关端点+下面的认证设置。

相关全局选项：

- `websocket_host`, `websocket_port`：WebSocket主机/端口。
- `websocket_auth`, `websocket_auth_key`, `websocket_auth_secret`：WebSocket认证。
- `remote_gateway_host`, `remote_gateway_port`, `remote_gateway_token`：远程网关目标。
- `session_store`：会话存储和主键默认值。