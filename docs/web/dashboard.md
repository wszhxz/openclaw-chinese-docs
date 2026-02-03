---
summary: "Gateway dashboard (Control UI) access and auth"
read_when:
  - Changing dashboard authentication or exposure modes
title: "Dashboard"
---
# 仪表盘（控制界面）

网关仪表盘是通过默认路径 `/` 提供的浏览器控制界面（可通过 `gateway.controlUi.basePath` 覆盖）。

快速打开（本地网关）：

- http://127.0.0.1:18789/（或 http://localhost:18789/）

关键参考：

- [控制界面](/web/control-ui) 用于使用方法和界面功能。
- [Tailscale](/gateway/tailscale) 用于服务/分流自动化。
- [网页界面](/web) 用于绑定模式和安全说明。

通过 `connect.params.auth`（令牌或密码）在 WebSocket 握手过程中强制执行认证。有关 [网关配置](/gateway/configuration) 中的 `gateway.auth` 详细信息，请参阅。

安全说明：控制界面是一个 **管理界面**（聊天、配置、执行审批）。请勿公开暴露。界面在首次加载后会将令牌存储在 `localStorage` 中。建议使用本地主机、Tailscale 服务或 SSH 隧道。

## 快速路径（推荐）

- 在完成注册后，CLI 会自动使用您的令牌打开仪表盘，并打印相同的令牌化链接。
- 任何时候均可重新打开：`openclaw dashboard`（复制链接，如果可能则打开浏览器，若为无头模式则显示 SSH 提示）。
- 令牌仅保留在本地（仅查询参数）；界面在首次加载后会剥离令牌并将其存储在 `localStorage` 中。

## 令牌基础（本地 vs 远程）

- **本地主机**：打开 `http://127.0.0.1:18789/`。如果看到“未授权”，请运行 `openclaw dashboard` 并使用令牌化链接（`?token=...`）。
- **令牌来源**：`gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）；界面在首次加载后会存储该令牌。
- **非本地主机**：使用 Tailscale 服务（如果 `gateway.auth.allowTailscale: true`，则无需令牌），通过令牌绑定 tailnet，或使用 SSH 隧道。请参阅 [网页界面](/web)。

## 如果看到“未授权” / 1008

- 运行 `openclaw dashboard` 获取新的令牌化链接。
- 确保网关可访问（本地：`openclaw status`；远程：SSH 隧道 `ssh -N -L 18789:127.0.0.1:18789 user@host` 然后打开 `http://127.0.0.1:18789/?token=...`）。
- 在仪表盘设置中，粘贴您在 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）中配置的相同令牌。