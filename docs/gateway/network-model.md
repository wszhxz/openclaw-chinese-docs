---
summary: "How the Gateway, nodes, and canvas host connect."
read_when:
  - You want a concise view of the Gateway networking model
title: "Network model"
---
大多数操作都通过网关（`openclaw gateway`）进行，这是一个长期运行的单一进程，负责管理通道连接和 WebSocket 控制平面。

## 核心规则

- 建议每台主机仅运行一个网关。它是唯一被允许拥有 WhatsApp Web 会话的进程。对于救援型机器人或需要严格隔离的场景，可运行多个网关，并为每个网关配置相互隔离的用户资料和端口。参见[多个网关](/gateway/multiple-gateways)。
- 优先使用回环地址（loopback first）：网关 WebSocket 默认绑定至 `ws://127.0.0.1:18789`。向导默认会为回环地址生成一个网关令牌。若需通过 Tailnet 访问，则需运行 `openclaw gateway --bind tailnet --token ...`，因为非回环地址绑定必须使用令牌。
- 节点可根据需要通过局域网（LAN）、Tailnet 或 SSH 连接到网关 WebSocket。传统的 TCP 桥接方式已被弃用。
- Canvas 主机由网关 HTTP 服务器提供服务，且与网关使用**同一端口**（默认为 `18789`）：
  - `/__openclaw__/canvas/`
  - `/__openclaw__/a2ui/`
    当配置了 `gateway.auth` 且网关绑定地址超出回环范围时，上述路由将受到网关身份验证保护。节点客户端使用与其当前活跃 WebSocket 会话绑定的、具备节点作用域的能力 URL（capability URLs）。参见[网关配置](/gateway/configuration)（`canvasHost`、`gateway`）。
- 远程使用通常采用 SSH 隧道或 Tailnet VPN 方式。参见[远程访问](/gateway/remote)和[服务发现](/gateway/discovery)。