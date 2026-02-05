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

- http://127.0.0.1:18789/ (或 http://localhost:18789/)

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

- 完成入站设置后，CLI现在会自动使用您的令牌打开仪表盘并打印相同的带令牌链接。
- 随时重新打开：`openclaw dashboard`（复制链接，如果可能则打开浏览器，无头模式下显示SSH提示）。
- 令牌仅保留在本地（仅作为查询参数）；UI在首次加载后会将其剥离并保存在localStorage中。

## 令牌基础（本地与远程）

- **本地主机**：打开 `http://127.0.0.1:18789/`。如果看到“未授权”，运行 `openclaw dashboard` 并使用带令牌的链接 (`?token=...`)。
- **令牌来源**：`gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）；UI在首次加载后存储它。
- **非本地主机**：使用Tailscale Serve（如果 `gateway.auth.allowTailscale: true` 则无需令牌），tailnet绑定加上一个令牌，或SSH隧道。参见 [Web表面](/web)。

## 如果您看到“未授权” / 1008

- 运行 `openclaw dashboard` 以获取新的带令牌链接。
- 确保网关可达（本地：`openclaw status`；远程：通过SSH隧道 `ssh -N -L 18789:127.0.0.1:18789 user@host` 然后打开 `http://127.0.0.1:18789/?token=...`）。
- 在仪表盘设置中，粘贴您在 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）中配置的相同令牌。