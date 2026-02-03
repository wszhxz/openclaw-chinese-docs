---
summary: "Integrated Tailscale Serve/Funnel for the Gateway dashboard"
read_when:
  - Exposing the Gateway Control UI outside localhost
  - Automating tailnet or public dashboard access
title: "Tailscale"
---
# Tailscale（网关仪表板）

OpenClaw 可以自动配置 Tailscale **Serve**（tailnet）或 **Funnel**（公共）用于网关仪表板和 WebSocket 端口。这会将网关绑定到环回接口，同时 Tailscale 提供 HTTPS、路由以及（对于 Serve）身份头信息。

## 模式

- `serve`：通过 `tailscale serve` 仅使用 Tailnet 的 Serve。网关保持在 `127.0.0.1`。
- `funnel`：通过 `tailscale funnel` 提供公共 HTTPS。OpenClaw 需要一个共享密码。
- `off`：默认（无 Tailscale 自动配置）。

## 认证

设置 `gateway.auth.mode` 来控制握手：

- `token`（当 `OPENCLAW_GATEWAY_TOKEN` 设置时默认）
- `password`（通过 `OPENCLAW_GATEWAY_PASSWORD` 或配置提供共享密钥）

当 `tailscale.mode = "serve"` 且 `gateway.auth.allowTailscale` 为 `true` 时，有效的 Serve 代理请求可以通过 Tailscale 身份头信息（`tailscale-user-login`）进行认证，而无需提供令牌/密码。OpenClaw 通过本地 Tailscale 守护进程（`tailscale whois`）解析 `x-forwarded-for` 地址，并将其与头信息匹配后接受请求。OpenClaw 仅在请求从环回接口通过 Tailscale 的 `x-forwarded-for`、`x-forwarded-proto` 和 `x-forwarded-host` 头信息到达时才视为 Serve。若需要显式凭据，请将 `gateway.auth.allowTailscale: false` 或强制 `gateway.auth.mode: "password"`。

## 配置示例

### 仅 Tailnet（Serve）

```json5
{
  gateway: {
    bind: "loopback",
    tailscale: { mode: "serve" },
  },
}
```

打开：`https://<magicdns>/`（或您配置的 `gateway.controlUi.basePath`）

### 仅 Tailnet（绑定到 Tailnet IP）

当您希望网关直接监听 Tailnet IP（无 Serve/Funnel）时使用：

```json5
{
  gateway: {
    bind: "tailnet",
    auth: { mode: "token", token: "your-token" },
  },
}
```

从另一台 Tailnet 设备连接：

- 控制界面：`http://<tailscale-ip>:18789/`
- WebSocket：`ws://<tailscale-ip>:18789`

注意：环回接口（`http://127.0.0.1:18789`）在此模式下将 **不** 起作用。

### 公共互联网（Funnel + 共享密码）

```json5
{
  gateway: {
    bind: "loopback",
    tailscale: { mode: "funnel" },
    auth: { mode: "password", password: "replace-me" },
  },
}
```

优先使用 `OPENCLAW_GATEWAY_PASSWORD` 而不是将密码写入磁盘。

## CLI 示例

```bash
openclaw gateway --tailscale serve
openclaw gateway --tailscale funnel --auth password
```

## 注意事项

- Tailscale Serve/Funnel 需要安装并登录 Tailscale CLI。
- `tailscale.mode: "funnel"` 除非认证模式为 `password`，否则拒绝启动以避免公共暴露。
- 如果您希望 OpenClaw 在关闭时撤销 `tailscale serve` 或 `tailscale funnel` 配置，请设置 `gateway.tailscale.resetOnExit`。
- `gateway.bind: "tailnet"` 是直接绑定 Tailnet（无 HTTPS，无 Serve/Funnel）。
- `gateway.bind: "auto"` 优先使用环回接口；若您希望仅使用 Tailnet，请使用 `tailnet`。
- Serve/Funnel 仅暴露 **网关控制界面 + WebSocket**。节点通过相同的网关 WebSocket 端点连接，因此 Serve 可用于节点访问。

## 浏览器控制（远程网关 + 本地浏览器）

如果您在一台机器上运行网关，但希望在另一台机器上驱动浏览器，请在浏览器机器上运行 **节点主机**，并确保两者在同一 tailnet 中。网关将代理浏览器操作到节点；无需单独的控制服务器或 Serve URL。

避免使用 Funnel 进行浏览器控制；将节点配对视为操作员访问。

## Tailscale 先决条件 + 限制

- Serve 需要为您的 tailnet 启用 HTTPS；CLI 会在缺失时提示。
- Serve 注入 Tailscale 身份头信息；Funnel 不注入。
- Funnel 需要 Tailscale v1.38.3+、MagicDNS、HTTPS 启用以及 funnel 节点属性。
- Funnel 仅支持通过 TLS 的端口 `443`、`8443` 和 `10000`。
- macOS 上的 Funnel 需要开源 Tailscale 应用程序变体。

## 进一步学习

- Tailscale Serve 概述：https://tailscale.com/kb/1312/serve
- `tailscale serve` 命令：https://tailscale.com/kb/1242/tailscale-serve
- Tailscale Funnel 概述：https://tailscale.com/kb/1223/tailscale-funnel
- `tailscale funnel` 命令：https://tailscale.com/kb/1311/tailscale-funnel