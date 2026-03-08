---
summary: "Delegate gateway authentication to a trusted reverse proxy (Pomerium, Caddy, nginx + OAuth)"
read_when:
  - Running OpenClaw behind an identity-aware proxy
  - Setting up Pomerium, Caddy, or nginx with OAuth in front of OpenClaw
  - Fixing WebSocket 1008 unauthorized errors with reverse proxy setups
  - Deciding where to set HSTS and other HTTP hardening headers
---
# 可信代理认证

> ⚠️ **安全敏感功能。** 此模式将认证完全委托给您的反向代理。配置错误可能导致您的网关暴露于未授权访问。启用前请仔细阅读本页。

## 何时使用

当以下情况时，使用 `trusted-proxy` 认证模式：

- 您在 **身份感知代理**（Pomerium, Caddy + OAuth, nginx + oauth2-proxy, Traefik + forward auth）后运行 OpenClaw
- 您的代理处理所有认证并通过 Headers 传递用户身份
- 您处于 Kubernetes 或容器环境中，且代理是通往网关的唯一路径
- 您遇到 WebSocket `1008 unauthorized` 错误，因为浏览器无法在 WS payload 中传递 tokens

## 何时不应使用

- 如果您的代理不认证用户（仅是 TLS 终止器或负载均衡器）
- 如果存在任何绕过代理到达网关的路径（防火墙漏洞，内部网络访问）
- 如果您不确定代理是否正确剥离/覆盖 forwarded headers
- 如果您只需要个人单用户访问（考虑使用 Tailscale Serve + loopback 以获得更简单的设置）

## 工作原理

1. 您的反向代理认证用户 (OAuth, OIDC, SAML 等)
2. 代理添加一个包含认证用户身份的 Header（例如 `x-forwarded-user: nick@example.com`）
3. OpenClaw 检查请求是否来自 **可信代理 IP**（在 `gateway.trustedProxies` 中配置）
4. OpenClaw 从配置的 Header 中提取用户身份
5. 如果一切检查通过，请求将被授权

## 控制 UI 配对行为

当 `gateway.auth.mode = "trusted-proxy"` 激活且请求通过可信代理检查时，Control UI WebSocket 会话可以在没有设备配对身份的情况下连接。

影响：

- 在此模式下，配对不再是 Control UI 访问的主要关口。
- 您的反向代理认证策略和 `allowUsers` 成为有效的访问控制。
- 保持网关入口仅锁定到可信代理 IP（`gateway.trustedProxies` + 防火墙）。

## 配置

```json5
{
  gateway: {
    // Use loopback for same-host proxy setups; use lan/custom for remote proxy hosts
    bind: "loopback",

    // CRITICAL: Only add your proxy's IP(s) here
    trustedProxies: ["10.0.0.1", "172.17.0.1"],

    auth: {
      mode: "trusted-proxy",
      trustedProxy: {
        // Header containing authenticated user identity (required)
        userHeader: "x-forwarded-user",

        // Optional: headers that MUST be present (proxy verification)
        requiredHeaders: ["x-forwarded-proto", "x-forwarded-host"],

        // Optional: restrict to specific users (empty = allow all)
        allowUsers: ["nick@example.com", "admin@company.org"],
      },
    },
  },
}
```

如果 `gateway.bind` 为 `loopback`，请在 `gateway.trustedProxies` 中包含一个 loopback 代理地址（`127.0.0.1`，`::1`，或等效的 loopback CIDR）。

### 配置参考

| 字段                                        | 必填 | 描述                                                                        |
| ------------------------------------------- | ---- | --------------------------------------------------------------------------- |
| `gateway.trustedProxies`                    | 是   | 要信任的代理 IP 地址数组。来自其他 IP 的请求将被拒绝。 |
| `gateway.auth.mode`                         | 是   | 必须为 `"trusted-proxy"`                                                   |
| `gateway.auth.trustedProxy.userHeader`      | 是   | 包含认证用户身份的 Header 名称                      |
| `gateway.auth.trustedProxy.requiredHeaders` | 否   | 请求被信任所必须存在的额外 Headers       |
| `gateway.auth.trustedProxy.allowUsers`      | 否   | 用户身份允许列表。为空意味着允许所有认证用户。    |

## TLS 终止与 HSTS

使用一个 TLS 终止点并在那里应用 HSTS。

### 推荐模式：代理 TLS 终止

当您的反向代理为 `https://control.example.com` 处理 HTTPS 时，在该域名的代理处设置 `Strict-Transport-Security`。

- 适合面向互联网的部署。
- 将证书 + HTTP 硬化策略集中在一处。
- OpenClaw 可以保持在代理后的 loopback HTTP 上。

示例 Header 值：

```text
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### 网关 TLS 终止

如果 OpenClaw 本身直接提供 HTTPS 服务（无 TLS 终止代理），设置：

```json5
{
  gateway: {
    tls: { enabled: true },
    http: {
      securityHeaders: {
        strictTransportSecurity: "max-age=31536000; includeSubDomains",
      },
    },
  },
}
```

`strictTransportSecurity` 接受字符串 Header 值，或 `false` 以明确禁用。

### 部署指导

- 首先使用较短的 max age（例如 `max-age=300`）同时验证流量。
- 仅在信心充足后增加到长期值（例如 `max-age=31536000`）。
- 仅当每个子域都准备好 HTTPS 时才添加 `includeSubDomains`。
- 仅当您有意为完整域名集满足 preload 要求时才使用 preload。
- 仅 loopback 的本地开发不会从 HSTS 受益。

## 代理设置示例

### Pomerium

Pomerium 在 `x-pomerium-claim-email`（或其他 claim headers）中传递身份，在 `x-pomerium-jwt-assertion` 中传递 JWT。

```json5
{
  gateway: {
    bind: "lan",
    trustedProxies: ["10.0.0.1"], // Pomerium's IP
    auth: {
      mode: "trusted-proxy",
      trustedProxy: {
        userHeader: "x-pomerium-claim-email",
        requiredHeaders: ["x-pomerium-jwt-assertion"],
      },
    },
  },
}
```

Pomerium 配置片段：

```yaml
routes:
  - from: https://openclaw.example.com
    to: http://openclaw-gateway:18789
    policy:
      - allow:
          or:
            - email:
                is: nick@example.com
    pass_identity_headers: true
```

### 带 OAuth 的 Caddy

带有 `caddy-security` 插件的 Caddy 可以认证用户并传递身份 Headers。

```json5
{
  gateway: {
    bind: "lan",
    trustedProxies: ["127.0.0.1"], // Caddy's IP (if on same host)
    auth: {
      mode: "trusted-proxy",
      trustedProxy: {
        userHeader: "x-forwarded-user",
      },
    },
  },
}
```

Caddyfile 片段：

```
openclaw.example.com {
    authenticate with oauth2_provider
    authorize with policy1

    reverse_proxy openclaw:18789 {
        header_up X-Forwarded-User {http.auth.user.email}
    }
}
```

### nginx + oauth2-proxy

oauth2-proxy 认证用户并在 `x-auth-request-email` 中传递身份。

```json5
{
  gateway: {
    bind: "lan",
    trustedProxies: ["10.0.0.1"], // nginx/oauth2-proxy IP
    auth: {
      mode: "trusted-proxy",
      trustedProxy: {
        userHeader: "x-auth-request-email",
      },
    },
  },
}
```

nginx 配置片段：

```nginx
location / {
    auth_request /oauth2/auth;
    auth_request_set $user $upstream_http_x_auth_request_email;

    proxy_pass http://openclaw:18789;
    proxy_set_header X-Auth-Request-Email $user;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### 带 Forward Auth 的 Traefik

```json5
{
  gateway: {
    bind: "lan",
    trustedProxies: ["172.17.0.1"], // Traefik container IP
    auth: {
      mode: "trusted-proxy",
      trustedProxy: {
        userHeader: "x-forwarded-user",
      },
    },
  },
}
```

## 安全检查清单

启用可信代理认证前，请验证：

- [ ] **代理是唯一路径**：网关端口除您的代理外对所有内容防火墙隔离
- [ ] **trustedProxies 是最小的**：仅您的实际代理 IP，而非整个子网
- [ ] **代理剥离 Headers**：您的代理覆盖（而非追加）来自客户端的 `x-forwarded-*` Headers
- [ ] **TLS 终止**：您的代理处理 TLS；用户通过 HTTPS 连接
- [ ] **allowUsers 已设置**（推荐）：限制为已知用户，而非允许任何认证用户

## 安全审计

`openclaw security audit` 将标记可信代理认证为 **critical** 严重性发现项。这是故意的——它提醒您正在将安全性委托给您的代理设置。

审计检查以下内容：

- 缺少 `trustedProxies` 配置
- 缺少 `userHeader` 配置
- 空的 `allowUsers`（允许任何认证用户）

## 故障排除

### "trusted_proxy_untrusted_source"

请求并非来自 `gateway.trustedProxies` 中的 IP。检查：

- 代理 IP 是否正确？（Docker 容器 IP 可能会变）
- 您的代理前面是否有负载均衡器？
- 使用 `docker inspect` 或 `kubectl get pods -o wide` 查找实际 IP

### "trusted_proxy_user_missing"

用户 Header 为空或缺失。检查：

- 您的代理是否配置为传递身份 Headers？
- Header 名称是否正确？（不区分大小写，但拼写很重要）
- 用户是否确实在代理处进行了认证？

### "trusted*proxy_missing_header*\*"

所需的 Header 不存在。检查：

- 您的代理针对这些特定 Headers 的配置
- Headers 是否在链中的某处被剥离

### "trusted_proxy_user_not_allowed"

用户已认证但不在 `allowUsers` 中。要么添加他们，要么移除允许列表。

### WebSocket 仍然失败

确保您的代理：

- 支持 WebSocket 升级 (`Upgrade: websocket`, `Connection: upgrade`)
- 在 WebSocket 升级请求上传递身份 Headers（不仅是 HTTP）
- 没有针对 WebSocket 连接的单独认证路径

## 从 Token 认证迁移

如果您正在从 token 认证迁移到可信代理：

1. 配置您的代理以认证用户并传递 Headers
2. 独立测试代理设置（使用 Headers 的 curl）
3. 使用可信代理认证更新 OpenClaw 配置
4. 重启网关
5. 从 Control UI 测试 WebSocket 连接
6. 运行 `openclaw security audit` 并审查发现项

## 相关内容

- [安全](/gateway/security) — 完整安全指南
- [配置](/gateway/configuration) — 配置参考
- [远程访问](/gateway/remote) — 其他远程访问模式
- [Tailscale](/gateway/tailscale) — 仅 tailnet 访问的更简单替代方案