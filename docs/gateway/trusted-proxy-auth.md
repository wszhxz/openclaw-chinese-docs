---
summary: "Delegate gateway authentication to a trusted reverse proxy (Pomerium, Caddy, nginx + OAuth)"
read_when:
  - Running OpenClaw behind an identity-aware proxy
  - Setting up Pomerium, Caddy, or nginx with OAuth in front of OpenClaw
  - Fixing WebSocket 1008 unauthorized errors with reverse proxy setups
---
# 受信任代理认证

> ⚠️ **安全敏感功能。** 此模式将身份验证完全委托给您的反向代理。错误的配置可能会使您的网关暴露于未经授权的访问。在启用之前仔细阅读此页面。

## 使用场景

在以下情况下使用 `trusted-proxy` 认证模式：

- 您在 **身份感知代理**（Pomerium, Caddy + OAuth, nginx + oauth2-proxy, Traefik + forward auth）后面运行 OpenClaw
- 您的代理处理所有身份验证并通过头部传递用户身份
- 您在一个 Kubernetes 或容器环境中，代理是访问网关的唯一路径
- 您遇到 WebSocket `1008 unauthorized` 错误，因为浏览器无法在 WS 负载中传递令牌

## 不适用场景

- 如果您的代理不进行用户身份验证（仅作为 TLS 终止器或负载均衡器）
- 如果有绕过代理访问网关的任何路径（防火墙漏洞、内部网络访问）
- 如果您不确定代理是否正确地剥离/覆盖转发的头部
- 如果您只需要个人单用户访问（考虑使用 Tailscale Serve + 回环以简化设置）

## 工作原理

1. 您的反向代理对用户进行身份验证（OAuth, OIDC, SAML 等）
2. 代理添加一个包含已认证用户身份的头部（例如，`x-forwarded-user: nick@example.com`）
3. OpenClaw 检查请求是否来自 **受信任的代理 IP**（在 `gateway.trustedProxies` 中配置）
4. OpenClaw 从配置的头部提取用户身份
5. 如果一切正常，请求将被授权

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

如果 `gateway.bind` 是 `loopback`，请在 `gateway.trustedProxies` 中包含回环代理地址
(`127.0.0.1`, `::1`，或等效的回环 CIDR）。

### 配置参考

| 字段                                       | 必需 | 描述                                                                 |
| ------------------------------------------- | -------- | --------------------------------------------------------------------------- |
| `gateway.trustedProxies`                    | 是      | 要信任的代理 IP 地址数组。来自其他 IP 的请求将被拒绝。 |
| `gateway.auth.mode`                         | 是      | 必须是 `"trusted-proxy"`                                                   |
| `gateway.auth.trustedProxy.userHeader`      | 是      | 包含已认证用户身份的头部名称                      |
| `gateway.auth.trustedProxy.requiredHeaders` | 否       | 请求被信任所需的附加头部       |
| `gateway.auth.trustedProxy.allowUsers`      | 否       | 用户身份白名单。空表示允许所有已认证用户。    |

## 代理设置示例

### Pomerium

Pomerium 通过 `x-pomerium-claim-email`（或其他声明头部）传递身份，并在 `x-pomerium-jwt-assertion` 中传递 JWT。

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

### Caddy with OAuth

带有 `caddy-security` 插件的 Caddy 可以对用户进行身份验证并传递身份头部。

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

oauth2-proxy 对用户进行身份验证并将身份传递在 `x-auth-request-email` 中。

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

### Traefik with Forward Auth

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

在启用受信任代理认证之前，请验证：

- [ ] **代理是唯一路径**：网关端口被防火墙保护，除了您的代理之外不允许其他访问
- [ ] **trustedProxies 最小化**：仅包含实际的代理 IP，而不是整个子网
- [ ] **代理剥离头部**：您的代理覆盖（而不是追加）客户端的 `x-forwarded-*` 头部
- [ ] **TLS 终止**：您的代理处理 TLS；用户通过 HTTPS 连接
- [ ] **allowUsers 已设置**（推荐）：限制为已知用户而不是允许任何已认证用户

## 安全审计

`openclaw security audit` 将以 **严重性关键** 的问题标记受信任代理认证。这是有意为之——提醒您将安全性委托给了代理设置。

审计检查：

- 缺少 `trustedProxies` 配置
- 缺少 `userHeader` 配置
- 空的 `allowUsers`（允许任何已认证用户）

## 故障排除

### "trusted_proxy_untrusted_source"

请求未来自 `gateway.trustedProxies` 中的 IP。检查：

- 代理 IP 是否正确？（Docker 容器 IP 可能会更改）
- 您的代理前面是否有负载均衡器？
- 使用 `docker inspect` 或 `kubectl get pods -o wide` 查找实际 IP

### "trusted_proxy_user_missing"

用户头部为空或缺失。检查：

- 您的代理是否配置为传递身份头部？
- 头部名称是否正确？（不区分大小写，但拼写很重要）
- 用户是否在代理处实际进行了身份验证？

### "trusted*proxy_missing_header*\*"

缺少必需的头部。检查：

- 您的代理配置中的这些特定头部
- 头部是否在链路的某个地方被剥离

### "trusted_proxy_user_not_allowed"

用户已认证但不在 `allowUsers` 中。要么将其添加到白名单，要么移除白名单。

### WebSocket 仍然失败

确保您的代理：

- 支持 WebSocket 升级 (`Upgrade: websocket`, `Connection: upgrade`)
- 在 WebSocket 升级请求中传递身份头部（而不仅仅是 HTTP）
- 没有为 WebSocket 连接设置单独的身份验证路径

## 从令牌认证迁移

如果您从令牌认证迁移到受信任代理：

1. 配置您的代理对用户进行身份验证并传递头部
2. 独立测试代理设置（使用带有头部的 curl）
3. 使用受信任代理认证更新 OpenClaw 配置
4. 重启网关
5. 从控制界面测试 WebSocket 连接
6. 运行 `openclaw security audit` 并审查结果

## 相关

- [Security](/gateway/security) — 完整的安全指南
- [Configuration](/gateway/configuration) — 配置参考
- [Remote Access](/gateway/remote) — 其他远程访问模式
- [Tailscale](/gateway/tailscale) — 仅限尾网访问的更简单替代方案