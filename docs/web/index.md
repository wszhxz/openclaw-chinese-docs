---
summary: "Gateway web surfaces: Control UI, bind modes, and security"
read_when:
  - You want to access the Gateway over Tailscale
  - You want the browser Control UI and config editing
title: "Web"
---
# Web (网关)

网关从与网关 WebSocket 相同的端口提供一个小型的 **浏览器控制界面** (Vite + Lit)：

- 默认: `http://<host>:18789/`
- 可选前缀: 设置 `gateway.controlUi.basePath` (例如 `/openclaw`)

功能位于 [控制界面](/web/control-ui)。
本页重点介绍绑定模式、安全性和面向 Web 的表面。

## Webhook

当 `hooks.enabled=true` 时，网关还会在同一 HTTP 服务器上暴露一个小的 webhook 端点。
有关身份验证和有效负载的信息，请参阅 [网关配置](/gateway/configuration) → `hooks`。

## 配置 (默认启用)

当存在资源时，控制界面默认 **启用** (`dist/control-ui`)。
您可以通过配置来控制它：

```json5
{
  gateway: {
    controlUi: { enabled: true, basePath: "/openclaw" }, // basePath optional
  },
}
```

## Tailscale 访问

### 集成 Serve（推荐）

将网关保留在回环中，并让 Tailscale Serve 代理它：

```json5
{
  gateway: {
    bind: "loopback",
    tailscale: { mode: "serve" },
  },
}
```

然后启动网关：

```bash
openclaw gateway
```

打开：

- `https://<magicdns>/` (或您配置的 `gateway.controlUi.basePath`)

### 尾网绑定 + 令牌

```json5
{
  gateway: {
    bind: "tailnet",
    controlUi: { enabled: true },
    auth: { mode: "token", token: "your-token" },
  },
}
```

然后启动网关（非回环绑定需要令牌）：

```bash
openclaw gateway
```

打开：

- `http://<tailscale-ip>:18789/` (或您配置的 `gateway.controlUi.basePath`)

### 公共互联网 (Funnel)

```json5
{
  gateway: {
    bind: "loopback",
    tailscale: { mode: "funnel" },
    auth: { mode: "password" }, // or OPENCLAW_GATEWAY_PASSWORD
  },
}
```

## 安全注意事项

- 默认情况下，网关认证是必需的（令牌/密码或 Tailscale 身份头）。
- 非回环绑定仍然 **需要** 共享令牌/密码 (`gateway.auth` 或环境变量）。
- 向导默认生成网关令牌（即使在回环中也是如此）。
- UI 发送 `connect.params.auth.token` 或 `connect.params.auth.password`。
- 控制界面发送防点击劫持头，并且除非设置了 `gateway.controlUi.allowedOrigins`，否则只接受同源浏览器的 websocket 连接。
- 使用 Serve 时，当 `gateway.auth.allowTailscale` 为 `true` 时，Tailscale 身份头可以满足认证（不需要令牌/密码）。设置 `gateway.auth.allowTailscale: false` 以要求显式凭据。请参阅 [Tailscale](/gateway/tailscale) 和 [安全性](/gateway/security)。
- `gateway.tailscale.mode: "funnel"` 需要 `gateway.auth.mode: "password"`（共享密码）。

## 构建 UI

网关从 `dist/control-ui` 提供静态文件。使用以下命令构建它们：

```bash
pnpm ui:build # auto-installs UI deps on first run
```