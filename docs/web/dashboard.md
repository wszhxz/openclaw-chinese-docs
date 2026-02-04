---

summary: "Gateway dashboard (Control UI) access and auth"
read_when:
  - Changing dashboard authentication or exposure modes
title: "Dashboard"

---
# 仪表盘（控制界面）

网关仪表盘是通过 `/` 默认提供的浏览器控制界面（可通过 `gateway.controlUi.basePath` 覆盖）。

快速打开（本地网关）：

- http://127.0.0.1:18789/ （或 http://localhost:18789/）

关键参考：

- [控制界面](/web/control-ui) 用于使用方法和界面功能。
- [Tailscale](/gateway/tailscale) 用于服务/流量转发自动化。
- [Web 界面](/web) 用于绑定模式和安全说明。

通过 `connect.params.auth`（令牌或密码）在 WebSocket 握手时强制认证。详见 [网关配置](/gateway/configuration) 中的 `gateway.auth`。

安全说明：控制界面是 **管理界面**（聊天、配置、执行审批）。请勿公开暴露。界面在首次加载后将令牌存储在 `localStorage`。建议使用本地主机、Tailscale 服务或 SSH 隧道。

## 快速路径（推荐）

- 完成注册后，CLI 现在会自动使用您的令牌打开仪表盘并打印相同的令牌化链接。
- 任何时候重新打开：`openclaw dashboard`（复制链接，若可能则打开浏览器，无头模式显示 SSH 提示）。
- 令牌保持本地（仅查询参数）；界面在首次加载后会剥离令牌并保存在 localStorage 中。

## 令牌基础（本地 vs 远程）

- **本地主机**：打开 `http://127.0.0.1:18789/`。若看到“未授权”，运行 `openclaw dashboard` 并使用令牌化链接（`?token=...`）。
- **令牌来源**：`gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）；界面在首次加载后存储该令牌。
- **非本地主机**：使用 Tailscale 服务（若 `gateway.auth.allowTailscale: true` 为无令牌模式），通过令牌进行 tailnet 绑定，或使用 SSH 隧道。详见 [Web 界面](/web)。

## 若看到“未授权” / 1008 错误

- 运行 `openclaw dashboard` 获取新的令牌化链接。
- 确保网关可达（本地：`openclaw status`；远程：SSH 隧道 `ssh -N -L 18789:127.0.0.1:18789 user@host` 后打开 `http://127.0.0.1:18789/?token=...`）。
- 在仪表盘设置中，粘贴您在 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）中配置的相同令牌。