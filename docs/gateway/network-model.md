---
summary: "How the Gateway, nodes, and canvas host connect."
read_when:
  - You want a concise view of the Gateway networking model
title: "Network model"
---
大多数操作通过网关 (`openclaw gateway`) 流动，这是一个单一的长期运行进程，拥有通道连接和WebSocket控制平面。

## 核心规则

- 每个主机建议只运行一个网关。它是唯一允许拥有WhatsApp Web会话的进程。对于救援机器人或严格的隔离，请使用独立的配置文件和端口运行多个网关。参见[多个网关](/gateway/multiple-gateways)。
- 先环回：网关WS默认使用 `ws://127.0.0.1:18789`。向导会默认生成一个网关令牌，即使在环回情况下也是如此。对于Tailnet访问，请运行 `openclaw gateway --bind tailnet --token ...` 因为非环回绑定需要令牌。
- 节点根据需要通过LAN、Tailnet或SSH连接到网关WS。传统的TCP桥接已被弃用。
- Canvas主机由网关HTTP服务器在与网关相同的端口上提供服务（默认 `18789`）：
  - `/__openclaw__/canvas/`
  - `/__openclaw__/a2ui/`
    当 `gateway.auth` 配置好并且网关绑定到环回之外时，这些路由将受到网关身份验证的保护。节点客户端使用与其活动WS会话关联的节点范围功能URL。参见[网关配置](/gateway/configuration) (`canvasHost`, `gateway`)。
- 远程使用通常是SSH隧道或Tailnet VPN。参见[远程访问](/gateway/remote) 和[发现](/gateway/discovery)。