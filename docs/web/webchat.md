---
summary: "Loopback WebChat static host and Gateway WS usage for chat UI"
read_when:
  - Debugging or configuring WebChat access
title: "WebChat"
---
# WebChat (Gateway WebSocket UI)

状态：macOS/iOS SwiftUI 聊天界面直接与 Gateway WebSocket 进行通信。

## 什么是它

- 网关的原生聊天界面（不嵌入浏览器且没有本地静态服务器）。
- 使用与其他通道相同的会话和路由规则。
- 确定性路由：回复总是返回到 WebChat。

## 快速开始

1. 启动网关。
2. 打开 WebChat 界面（macOS/iOS 应用）或控制界面聊天标签。
3. 确保网关认证已配置（默认情况下需要，即使在回环中也是如此）。

## 工作原理（行为）

- 界面连接到 Gateway WebSocket 并使用 `chat.history`，`chat.send` 和 `chat.inject`。
- `chat.history` 受限以确保稳定性：网关可能会截断长文本字段，省略大量元数据，并用 `[chat.history omitted: message too large]` 替换超大条目。
- `chat.inject` 直接将助手备注附加到记录并广播到界面（无需代理运行）。
- 中断的运行可以在界面中保持部分助手输出可见。
- 当缓冲输出存在时，网关将中断的部分助手文本持久化到记录历史，并标记这些条目带有中断元数据。
- 历史记录始终从网关获取（不监视本地文件）。
- 如果网关无法访问，WebChat 为只读模式。

## 远程使用

- 远程模式通过 SSH/Tailscale 隧道网关 WebSocket。
- 您不需要运行单独的 WebChat 服务器。

## 配置参考（WebChat）

完整配置：[Configuration](/gateway/configuration)

通道选项：

- 没有专用的 `webchat.*` 块。WebChat 使用网关端点 + 下方的认证设置。

相关全局选项：

- `gateway.port`，`gateway.bind`：WebSocket 主机/端口。
- `gateway.auth.mode`，`gateway.auth.token`，`gateway.auth.password`：WebSocket 认证（令牌/密码）。
- `gateway.auth.mode: "trusted-proxy"`：浏览器客户端的反向代理认证（参见 [Trusted Proxy Auth](/gateway/trusted-proxy-auth)）。
- `gateway.remote.url`，`gateway.remote.token`，`gateway.remote.password`：远程网关目标。
- `session.*`：会话存储和主键默认值。