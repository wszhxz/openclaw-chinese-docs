---
summary: "Gateway dashboard (Control UI) access and auth"
read_when:
  - Changing dashboard authentication or exposure modes
title: "Dashboard"
---
# 仪表盘 (控制UI)

网关仪表盘是默认在 `/` 提供的浏览器控制UI
（通过 `gateway.controlUi.basePath` 覆盖）。

快速打开（本地网关）：

- [http://127.0.0.1:18789/](http://127.0.0.1:18789/) （或 [http://localhost:18789/](http://localhost:18789/)）

关键参考：

- [控制UI](/web/control-ui) 用于使用方法和UI功能。
- [Tailscale](/gateway/tailscale) 用于Serve/Funnel自动化。
- [Web表面](/web) 用于绑定模式和安全说明。

身份验证通过 `connect.params.auth` 在WebSocket握手时强制执行
（令牌或密码）。参见 [网关配置](/gateway/configuration) 中的 `gateway.auth`。

安全说明：控制UI是一个 **管理界面**（聊天、配置、执行审批）。
不要公开暴露它。UI在首次加载后将令牌存储在 `localStorage` 中。
优先使用localhost、Tailscale Serve或SSH隧道。

## 快速路径（推荐）

- 完成入站设置后，CLI会自动打开仪表盘并打印一个干净的（非令牌化）链接。
- 随时重新打开：`openclaw dashboard` （复制链接，如果可能则打开浏览器，无头模式下显示SSH提示）。
- 如果UI提示需要身份验证，请将来自 `gateway.auth.token` （或 `OPENCLAW_GATEWAY_TOKEN`）的令牌粘贴到控制UI设置中。

## 令牌基础知识（本地与远程）

- **本地主机**：打开 `http://127.0.0.1:18789/`。
- **令牌来源**：`gateway.auth.token` （或 `OPENCLAW_GATEWAY_TOKEN`）；连接后UI会在localStorage中存储一份副本。
- **非本地主机**：使用Tailscale Serve（如果 `gateway.auth.allowTailscale: true`，控制UI/WebSocket无需令牌，假设网关主机可信；HTTP API仍然需要令牌/密码），tailnet绑定使用令牌，或SSH隧道。参见 [Web表面](/web)。

## 如果看到“未授权” / 1008

- 确保网关可达（本地：`openclaw status`；远程：通过SSH隧道 `ssh -N -L 18789:127.0.0.1:18789 user@host` 然后打开 `http://127.0.0.1:18789/`）。
- 从网关主机检索令牌：`openclaw config get gateway.auth.token` （或生成一个：`openclaw doctor --generate-gateway-token`）。
- 在仪表盘设置中，将令牌粘贴到身份验证字段中，然后连接。