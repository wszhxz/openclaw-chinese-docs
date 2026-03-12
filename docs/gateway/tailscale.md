---
summary: "Integrated Tailscale Serve/Funnel for the Gateway dashboard"
read_when:
  - Exposing the Gateway Control UI outside localhost
  - Automating tailnet or public dashboard access
title: "Tailscale"
---
# Tailscale（网关仪表板）

OpenClaw 可自动为网关仪表板和 WebSocket 端口配置 Tailscale 的 **Serve**（仅限 Tailnet）或 **Funnel**（公开访问）功能。这使得网关始终绑定到回环地址（loopback），而由 Tailscale 提供 HTTPS、路由，以及（在 Serve 模式下）身份标识头（identity headers）。

## 模式

- `serve`：仅通过 `tailscale serve` 启用 Tailnet 内的 Serve。网关仍运行在 `127.0.0.1` 上。
- `funnel`：通过 `tailscale funnel` 提供公开 HTTPS 访问。OpenClaw 需要一个共享密码。
- `off`：默认模式（不启用 Tailscale 自动化）。

## 认证（Auth）

设置 `gateway.auth.mode` 以控制握手方式：

- `token`（当设置了 `OPENCLAW_GATEWAY_TOKEN` 时为默认值）
- `password`（通过 `OPENCLAW_GATEWAY_PASSWORD` 或配置文件提供共享密钥）

当 `tailscale.mode = "serve"` 和 `gateway.auth.allowTailscale` 均为 `true` 时，  
控制界面（Control UI）/WebSocket 认证可利用 Tailscale 身份标识头（`tailscale-user-login`）进行认证，无需提供 token 或密码。OpenClaw 会通过本地 Tailscale 守护进程（`tailscale whois`）解析请求来源的 `x-forwarded-for` 地址，并与请求头中的信息比对，验证通过后才接受该请求。  
OpenClaw 仅将来自回环地址（loopback）且携带 Tailscale 的 `x-forwarded-for`、`x-forwarded-proto` 和 `x-forwarded-host` 头的请求视为 Serve 请求。  
HTTP API 接口（例如 `/v1/*`、`/tools/invoke` 和 `/api/channels/*`）仍需 token 或密码认证。  
该免 token 流程的前提是网关主机可信。若同一主机上可能运行不可信的本地代码，请禁用 `gateway.auth.allowTailscale`，并强制使用 token/密码认证。  
如需显式凭证认证，请设置 `gateway.auth.allowTailscale: false`，或强制启用 `gateway.auth.mode: "password"`。

## 配置示例

### 仅限 Tailnet（Serve）

```json5
{
  gateway: {
    bind: "loopback",
    tailscale: { mode: "serve" },
  },
}
```

访问地址：`https://<magicdns>/`（或您自定义的 `gateway.controlUi.basePath`）

### 仅限 Tailnet（直接绑定到 Tailnet IP）

适用于希望网关直接监听 Tailnet IP（不使用 Serve/Funnel）的场景。

```json5
{
  gateway: {
    bind: "tailnet",
    auth: { mode: "token", token: "your-token" },
  },
}
```

从另一台 Tailnet 设备连接：

- 控制界面（Control UI）：`http://<tailscale-ip>:18789/`
- WebSocket：`ws://<tailscale-ip>:18789`

注意：此模式下回环地址（`http://127.0.0.1:18789`）将**无法工作**。

### 公网访问（Funnel + 共享密码）

```json5
{
  gateway: {
    bind: "loopback",
    tailscale: { mode: "funnel" },
    auth: { mode: "password", password: "replace-me" },
  },
}
```

建议优先使用 `OPENCLAW_GATEWAY_PASSWORD`，而非将密码明文写入磁盘。

## CLI 示例

```bash
openclaw gateway --tailscale serve
openclaw gateway --tailscale funnel --auth password
```

## 注意事项

- Tailscale Serve/Funnel 要求已安装并登录 `tailscale` CLI。
- `tailscale.mode: "funnel"` 在认证模式非 `password` 时拒绝启动，以避免意外暴露至公网。
- 若希望 OpenClaw 在退出时自动撤销 `tailscale serve` 或 `tailscale funnel` 的配置，请设置 `gateway.tailscale.resetOnExit`。
- `gateway.bind: "tailnet"` 是直接绑定 Tailnet IP 的方式（无 HTTPS，不启用 Serve/Funnel）。
- `gateway.bind: "auto"` 优先使用回环地址；如需仅限 Tailnet 访问，请改用 `tailnet`。
- Serve/Funnel 仅暴露 **网关控制界面 + WebSocket**。节点也通过同一网关 WebSocket 端点连接，因此 Serve 模式同样支持节点接入。

## 浏览器控制（远程网关 + 本地浏览器）

若您在一台机器上运行网关，但希望在另一台机器上的浏览器中进行操作，请在浏览器所在机器上运行一个 **node host**，并确保两台机器处于同一 tailnet 中。网关将代理浏览器操作至 node，无需单独的控制服务器或 Serve URL。

请勿对浏览器控制使用 Funnel；应将 node 配对视同运维人员访问权限管理。

## Tailscale 前置条件与限制

- Serve 要求您的 tailnet 已启用 HTTPS；CLI 将在缺失时提示启用。
- Serve 会注入 Tailscale 身份标识头（identity headers）；Funnel 不支持该功能。
- Funnel 要求 Tailscale 版本 ≥ v1.38.3、启用 MagicDNS 和 HTTPS，并具备 funnel node 属性。
- Funnel 仅支持通过 TLS 暴露端口 `443`、`8443` 和 `10000`。
- macOS 上的 Funnel 需使用开源版本的 Tailscale 应用程序。

## 进一步了解

- Tailscale Serve 概览：[https://tailscale.com/kb/1312/serve](https://tailscale.com/kb/1312/serve)
- `tailscale serve` 命令说明：[https://tailscale.com/kb/1242/tailscale-serve](https://tailscale.com/kb/1242/tailscale-serve)
- Tailscale Funnel 概览：[https://tailscale.com/kb/1223/tailscale-funnel](https://tailscale.com/kb/1223/tailscale-funnel)
- `tailscale funnel` 命令说明：[https://tailscale.com/kb/1311/tailscale-funnel](https://tailscale.com/kb/1311/tailscale-funnel)