---
summary: "Loopback WebChat static host and Gateway WS usage for chat UI"
read_when:
  - Debugging or configuring WebChat access
title: "WebChat"
---
# WebChat (网关 WebSocket UI)

状态：macOS/iOS SwiftUI 聊天界面直接与网关 WebSocket 通信。

## 什么是 WebChat

- 一个针对网关的原生聊天界面（没有嵌入浏览器，也没有本地静态服务器）。
- 使用与其他通道相同的会话和路由规则。
- 确定性路由：回复总是返回到 WebChat。

## 快速开始

1. 启动网关。
2. 打开 WebChat UI（macOS/iOS 应用程序）或控制 UI 的聊天标签页。
3. 确保配置了网关认证（默认情况下即使在回环接口上也需要）。

## 工作原理（行为）

- UI 连接到 Gateway WebSocket 并使用 `chat.history`、`chat.send` 和 `chat.inject`。
- `chat.history` 为了稳定性进行了限制：网关可能会截断长文本字段，省略大量元数据，并用 `[chat.history omitted: message too large]` 替换过大的条目。
- `chat.inject` 直接将助手备注附加到记录并广播到 UI（无需代理运行）。
- 中断的运行可以在 UI 中保留部分助手输出可见。
- 当存在缓冲输出时，网关会将中断的部分助手文本持久化到记录历史中，并用中断元数据标记这些条目。
- 历史记录始终从网关获取（不监视本地文件）。
- 如果网关不可达，WebChat 将变为只读模式。

## 控制 UI 代理工具面板

- 控制 UI `/agents` 工具面板通过 `tools.catalog` 获取运行时目录，并将每个
  工具标记为 `core` 或 `plugin:<id>`（加上 `optional` 用于可选插件工具）。
- 如果 `tools.catalog` 不可用，面板将回退到内置的静态列表。
- 面板可以编辑配置文件和覆盖配置，但有效的运行时访问仍然遵循策略
  优先级 (`allow`/`deny`，每个代理和提供者/通道的覆盖)。

## 远程使用

- 远程模式通过 SSH/Tailscale 隧道传输网关 WebSocket。
- 您不需要运行单独的 WebChat 服务器。

## 配置参考（WebChat）

完整配置：[配置](/gateway/configuration)

通道选项：

- 没有专用的 `webchat.*` 块。WebChat 使用下面的网关端点 + 认证设置。

相关全局选项：

- `gateway.port`, `gateway.bind`: WebSocket 主机/端口。
- `gateway.auth.mode`, `gateway.auth.token`, `gateway.auth.password`: WebSocket 认证（令牌/密码）。
- `gateway.auth.mode: "trusted-proxy"`: 浏览器客户端的反向代理认证（参见 [可信代理认证](/gateway/trusted-proxy-auth)）。
- `gateway.remote.url`, `gateway.remote.token`, `gateway.remote.password`: 远程网关目标。
- `session.*`: 会话存储和主密钥默认值。