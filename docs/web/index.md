---
summary: "Gateway web surfaces: Control UI, bind modes, and security"
read_when:
  - You want to access the Gateway over Tailscale
  - You want the browser Control UI and config editing
title: "Web"
---
# Web（网关）

网关从与网关WebSocket相同的端口提供一个小的**浏览器控制UI**（Vite + Lit）：

- 默认：`http://<host>:18789/`
- 可选前缀：设置`gateway.controlUi.basePath`（例如`/openclaw`）

功能位于[控制UI](/web/control-ui)。
本页面重点介绍绑定模式、安全性和面向Web的界面。

## Webhooks

当`hooks.enabled=true`时，网关还在同一HTTP服务器上公开一个小型webhook端点。
参见[网关配置](/gateway/configuration) → `hooks`了解认证和有效载荷。

## 配置（默认开启）

当资源存在时（`dist/control-ui`），控制UI**默认启用**。
您可以通过配置控制它：

```json5
{
  gateway: {
    controlUi: { enabled: true, basePath: "/openclaw" }, // basePath optional
  },
}
```

## Tailscale访问

### 集成Serve（推荐）

将网关保留在回环接口上，让Tailscale Serve代理它：

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

- `https://<magicdns>/`（或您配置的`gateway.controlUi.basePath`）

### Tailnet绑定+令牌

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

- `http://<tailscale-ip>:18789/`（或您配置的`gateway.controlUi.basePath`）

### 公共互联网（Funnel）

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

- 默认情况下需要网关认证（令牌/密码或Tailscale身份头）。
- 非回环绑定仍然**需要**共享令牌/密码（`gateway.auth`或环境变量）。
- 向导默认生成网关令牌（即使在回环上）。
- UI发送`connect.params.auth.token`或`connect.params.auth.password`。
- 控制UI发送防点击劫持头，并且仅接受同源浏览器websocket连接，除非设置了`gateway.controlUi.allowedOrigins`。
- 使用Serve时，当`gateway.auth.allowTailscale`为`true`时，Tailscale身份头可以满足认证要求（不需要令牌/密码）。设置`gateway.auth.allowTailscale: false`以要求明确的凭据。参见[Tailscale](/gateway/tailscale)和[安全](/gateway/security)。
- `gateway.tailscale.mode: "funnel"`需要`gateway.auth.mode: "password"`（共享密码）。

## 构建UI

网关从`dist/control-ui`提供静态文件。使用以下命令构建它们：

```bash
pnpm ui:build # auto-installs UI deps on first run
```