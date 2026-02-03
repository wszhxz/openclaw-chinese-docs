---
summary: "Gateway web surfaces: Control UI, bind modes, and security"
read_when:
  - You want to access the Gateway over Tailscale
  - You want the browser Control UI and config editing
title: "Web"
---
# Web（网关）

网关从与网关 WebSocket 相同的端口提供一个小型的 **浏览器控制用户界面**（Vite + Lit）：

- 默认：`http://<host>:18789/`
- 可选前缀：设置 `gateway.controlUi.basePath`（例如 `/openclaw`）

能力位于 [Control UI](/web/control-ui)。
本页重点介绍绑定模式、安全性和面向 Web 的接口。

## Webhook

当 `hooks.enabled=true` 时，网关还会在同一 HTTP 服务器上暴露一个小型的 Webhook 端点。
参见 [网关配置](/gateway/configuration) → `hooks` 以获取认证 + 数据负载。

## 配置（默认启用）

当存在资源（`dist/control-ui`）时，控制UI **默认启用**。
您可以通过配置控制它：

```json5
{
  gateway: {
    controlUi: { enabled: true, basePath: "/openclaw" }, // basePath 可选
  },
}
```

## Tailscale 访问

### 集成 Serve（推荐）

将网关保留在环回模式，并让 Tailscale Serve 代理它：

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

- `https://<magicdns>/`（或您配置的 `gateway.controlUi.basePath`）

### Tailnet 绑定 + 令牌

```json5
{
  gateway: {
    bind: "tailnet",
    controlUi: { enabled: true },
    auth: { mode: "token", token: "your-token" },
  },
}
```

然后启动网关（非环回绑定需要令牌）：

```bash
openclaw gateway
```

打开：

- `http://<tailscale-ip>:18789/`（或您配置的 `gateway.controlUi.basePath`）

### 公共互联网（Funnel）

```json5
{
  gateway: {
    bind: "loopback",
    tailscale: { mode: "funnel" },
    auth: { mode: "password" }, // 或 OPENCLAW_GATEWAY_PASSWORD
  },
}
```

## 安全说明

- 默认情况下，网关认证是必需的（令牌/密码或 Tailscale 身份头信息）。
- 非环回绑定仍 **需要** 一个共享令牌/密码（`gateway.auth` 或环境变量）。
- 向导默认生成一个网关令牌（即使在环回模式下）。
- UI 会发送 `connect.params.auth.token` 或 `connect.params.auth.password`。
- 使用 Serve 时，如果 `gateway.auth.allowTailscale` 设置为 `true`，Tailscale 身份头信息可以满足认证（无需令牌/密码）。设置 `gateway.auth.allowTailscale: false` 以要求显式凭证。参见 [Tailscale](/gateway/tailscale) 和 [安全](/gateway/security)。
- `gateway.tailscale.mode: "funnel"` 需要 `gateway.auth.mode: "password"`（共享密码）。

## 构建 UI

网关从 `dist/control-ui` 提供静态文件。使用以下命令构建它们：

```bash
pnpm ui:build # 第一次运行时会自动安装 UI 依赖
```