---
summary: "Gateway web surfaces: Control UI, bind modes, and security"
read_when:
  - You want to access the Gateway over Tailscale
  - You want the browser Control UI and config editing
title: "Web"
---
# Web (Gateway)

网关从与网关WebSocket相同的端口提供一个小的**浏览器控制界面**（Vite + Lit）：

- 默认：`http://<host>:18789/`
- 可选前缀：设置`gateway.controlUi.basePath`（例如`/openclaw`）

功能位于[控制界面](/web/control-ui)。
此页面重点介绍绑定模式、安全性和面向Web的表面。

## Webhooks

当`hooks.enabled=true`时，网关还在同一HTTP服务器上暴露了一个小的webhook端点。
请参阅[网关配置](/gateway/configuration) → `hooks` 以获取认证和负载信息。

## 配置（默认开启）

当存在资源文件时(`dist/control-ui`)，控制界面**默认启用**。
您可以通过配置来控制它：

```json5
{
  gateway: {
    controlUi: { enabled: true, basePath: "/openclaw" }, // basePath optional
  },
}
```

## Tailscale访问

### 集成服务（推荐）

保持网关在回环地址上，并让Tailscale Serve代理它：

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

### Tailnet绑定 + 令牌

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
- 非回环绑定仍然**需要**共享令牌/密码(`gateway.auth` 或环境变量)。
- 向导默认生成一个网关令牌（即使是在回环地址上）。
- 用户界面发送`connect.params.auth.token` 或 `connect.params.auth.password`。
- 对于非回环控制界面部署，请显式设置`gateway.controlUi.allowedOrigins`（完整来源）。没有它，默认情况下网关启动将被拒绝。
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true` 启用
  Host-header源回退模式，但这是一个危险的安全降级。
- 使用Serve时，当`gateway.auth.allowTailscale` 是 `true` 时，Tailscale身份头可以满足控制界面/WebSocket认证
  （不需要令牌/密码）。HTTP API端点仍需要令牌/密码。设置
  `gateway.auth.allowTailscale: false` 以要求明确的凭证。请参阅
  [Tailscale](/gateway/tailscale) 和 [Security](/gateway/security)。这种无令牌流程假设网关主机是可信的。
- `gateway.tailscale.mode: "funnel"` 需要 `gateway.auth.mode: "password"`（共享密码）。

## 构建用户界面

网关从`dist/control-ui` 提供静态文件。使用以下命令构建它们：

```bash
pnpm ui:build # auto-installs UI deps on first run
```