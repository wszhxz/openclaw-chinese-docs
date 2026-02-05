---
summary: "Gateway dashboard (Control UI) access and auth"
read_when:
  - Changing dashboard authentication or exposure modes
title: "Dashboard"
---
# 仪表板（控制界面）

网关仪表板是在默认情况下通过 `/` 提供的浏览器控制界面
（可通过 `gateway.controlUi.basePath` 覆盖）。

快速打开（本地网关）：

- http://127.0.0.1:18789/ （或 http://localhost:18789/）

关键参考：

- [控制界面](/web/control-ui) 了解使用方法和界面功能。
- [Tailscale](/gateway/tailscale) 了解 Serve/Funnel 自动化。
- [Web surfaces](/web) 了解绑定模式和安全说明。

认证通过 `connect.params.auth`
（令牌或密码）在 WebSocket 握手时强制执行。参见 [网关配置](/gateway/configuration) 中的 `gateway.auth`。

安全说明：控制界面是一个 **管理面**（聊天、配置、执行审批）。
不要公开暴露它。界面在首次加载后将令牌存储在 `localStorage` 中。
建议使用 localhost、Tailscale Serve 或 SSH 隧道。

## 快速路径（推荐）

- 入门后，CLI 现在会自动使用您的令牌打开仪表板并打印相同的带令牌链接。
- 随时重新打开：`openclaw dashboard` （复制链接，如果可能则打开浏览器，如果是无头环境则显示 SSH 提示）。
- 令牌保持在本地（仅查询参数）；界面在首次加载后会去除它并保存在 localStorage 中。

## 令牌基础（本地 vs 远程）

- **本地主机**：打开 `http://127.0.0.1:18789/`。如果您看到"未授权"，运行 `openclaw dashboard` 并使用带令牌的链接（`?token=...`）。
- **令牌来源**：`gateway.auth.token` （或 `OPENCLAW_GATEWAY_TOKEN`）；界面在首次加载后存储它。
- **非本地主机**：使用 Tailscale Serve（如果 `gateway.auth.allowTailscale: true` 则无需令牌）、使用令牌进行尾网绑定或 SSH 隧道。参见 [Web surfaces](/web)。

## 如果您看到"未授权" / 1008

- 运行 `openclaw dashboard` 获取新的带令牌链接。
- 确保网关可访问（本地：`openclaw status`；远程：SSH 隧道 `ssh -N -L 18789:127.0.0.1:18789 user@host` 然后打开 `http://127.0.0.1:18789/?token=...`）。
- 在仪表板设置中，粘贴您在 `gateway.auth.token` （或 `OPENCLAW_GATEWAY_TOKEN`）中配置的相同令牌。