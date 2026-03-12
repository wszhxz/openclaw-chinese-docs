---
summary: "Delegate gateway authentication to a trusted reverse proxy (Pomerium, Caddy, nginx + OAuth)"
read_when:
  - Running OpenClaw behind an identity-aware proxy
  - Setting up Pomerium, Caddy, or nginx with OAuth in front of OpenClaw
  - Fixing WebSocket 1008 unauthorized errors with reverse proxy setups
  - Deciding where to set HSTS and other HTTP hardening headers
---
# 受信任代理认证

> ⚠️ **安全敏感功能。** 此模式将全部认证工作完全委托给您的反向代理。配置错误可能导致网关暴露于未授权访问之下。启用前请仔细阅读本页内容。

## 适用场景

当满足以下条件时，请使用 `trusted-proxy` 认证模式：

- 您将 OpenClaw 部署在 **具备身份感知能力的代理**（Pomerium、Caddy + OAuth、nginx + oauth2-proxy、Traefik + forward auth）之后；
- 您的代理负责全部认证流程，并通过请求头传递用户身份；
- 您处于 Kubernetes 或容器环境中，且代理是访问网关的唯一路径；
- 您正遭遇 WebSocket `1008 unauthorized` 错误，因为浏览器无法在 WebSocket 载荷中传递令牌。

## 不适用场景

- 您的代理不执行用户认证（仅作为 TLS 终止器或负载均衡器）；
- 存在任何绕过代理直接访问网关的路径（例如防火墙漏洞、内网直连）；
- 您不确定代理是否能正确清除/覆写已转发的请求头；
- 您仅需个人单用户访问（可考虑使用 Tailscale Serve + 回环地址以获得更简单的部署方式）。

## 工作原理

1. 您的反向代理对用户进行认证（OAuth、OIDC、SAML 等）；
2. 代理添加一个包含已认证用户身份的请求头（例如：`x-forwarded-user: nick@example.com`）；
3. OpenClaw 校验该请求是否来自 **受信任的代理 IP**（在 `gateway.trustedProxies` 中配置）；
4. OpenClaw 从已配置的请求头中提取用户身份；
5. 若全部校验通过，则该请求被授权。

## 控制界面配对行为控制

当 `gateway.auth.mode = "trusted-proxy"` 启用且请求通过受信任代理校验时，控制界面的 WebSocket 会话可在无需设备配对身份的情况下建立连接。

影响说明：

- 在此模式下，配对不再作为控制界面访问的主要准入机制；
- 您的反向代理认证策略与 `allowUsers` 共同构成实际的访问控制；
- 请确保网关入口仅对受信任代理 IP 开放（`gateway.trustedProxies` + 防火墙策略）。

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

若 `gateway.bind` 为 `loopback`，请在 `gateway.trustedProxies` 中包含回环代理地址（如 `127.0.0.1`、`::1` 或等效的回环 CIDR 地址）。

### 配置参考

| 字段                                       | 是否必需 | 描述                                                                 |
| ------------------------------------------- | -------- | ------------------------------------------------------------------- |
| `gateway.trustedProxies`                    | 是       | 受信任代理 IP 地址数组。来自其他 IP 的请求将被拒绝。                 |
| `gateway.auth.mode`                         | 是       | 必须为 `"trusted-proxy"`                                           |
| `gateway.auth.trustedProxy.userHeader`      | 是       | 包含已认证用户身份的请求头名称                                      |
| `gateway.auth.trustedProxy.requiredHeaders` | 否       | 请求必须携带的额外请求头（否则视为不可信）                          |
| `gateway.auth.trustedProxy.allowUsers`      | 否       | 用户身份白名单。空值表示允许所有已认证用户。                        |

## TLS 终止与 HSTS

请仅使用一个 TLS 终止点，并在该点启用 HSTS。

### 推荐模式：代理端 TLS 终止

当您的反向代理为 `https://control.example.com` 处理 HTTPS 时，请在该域名的代理上设置 `Strict-Transport-Security`。

- 适用于面向互联网的部署；
- 将证书与 HTTP 安全加固策略集中管理；
- OpenClaw 可继续在代理后方以回环 HTTP 方式运行。

示例请求头值：

```text
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### 网关端 TLS 终止

若 OpenClaw 自身直接提供 HTTPS 服务（无 TLS 终止代理），请设置：

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

`strictTransportSecurity` 接受字符串类型的请求头值，或使用 `false` 显式禁用。

### 上线指导建议

- 初期先采用较短的最大有效期（例如 `max-age=300`），以便验证流量；
- 仅在充分确认稳定性后，再提升至长期有效值（例如 `max-age=31536000`）；
- 仅当所有子域名均已支持 HTTPS 时，才添加 `includeSubDomains`；
- 仅当您明确满足整个域名集的预加载要求时，才启用 preload；
- 仅限回环地址的本地开发环境无法从 HSTS 中获益。

## 代理配置示例

### Pomerium

Pomerium 通过 `x-pomerium-claim-email`（或其他声明请求头）传递身份信息，并在 `x-pomerium-jwt-assertion` 中传递 JWT。

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

### Caddy 配合 OAuth

Caddy 使用 `caddy-security` 插件可实现用户认证并传递身份请求头。

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

oauth2-proxy 对用户进行认证，并在 `x-auth-request-email` 中传递身份信息。

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

### Traefik 配合 Forward Auth

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

启用受信任代理认证前，请确认以下各项：

- [ ] **代理是唯一入口路径**：网关端口已通过防火墙限制，仅允许来自代理的访问；
- [ ] **trustedProxies 配置最小化**：仅列出实际代理 IP，而非整个子网；
- [ ] **代理清除请求头**：代理会覆写（而非追加）来自客户端的 `x-forwarded-*` 请求头；
- [ ] **TLS 终止配置正确**：代理负责 TLS 终止；用户通过 HTTPS 连接；
- [ ] **已设置 allowUsers（推荐）**：限制为已知用户，而非允许任意已认证用户。

## 安全审计

`openclaw security audit` 将以 **严重（critical）** 级别告警提示受信任代理认证。这是有意为之——提醒您已将安全性完全交由代理配置承担。

审计项包括：

- 缺少 `trustedProxies` 配置；
- 缺少 `userHeader` 配置；
- `allowUsers` 为空（允许任意已认证用户）。

## 故障排查

### “trusted_proxy_untrusted_source”

请求来源 IP 不在 `gateway.trustedProxies` 列表中。请检查：

- 代理 IP 是否正确？（Docker 容器 IP 可能动态变化）；
- 代理前方是否存在负载均衡器？
- 使用 `docker inspect` 或 `kubectl get pods -o wide` 查看真实客户端 IP。

### “trusted_proxy_user_missing”

用户身份请求头为空或缺失。请检查：

- 代理是否已配置为传递身份请求头？
- 请求头名称是否正确？（不区分大小写，但拼写必须准确）；
- 用户是否确已在代理端完成认证？

### “trusted*proxy_missing_header*\*”

某个必需请求头缺失。请检查：

- 代理配置中是否包含这些特定请求头；
- 请求头是否在传输链路中某处被清除。

### “trusted_proxy_user_not_allowed”

用户已通过认证，但不在 `allowUsers` 白名单中。请将其加入白名单，或移除白名单限制。

### WebSocket 仍失败

请确保您的代理：

- 支持 WebSocket 升级（`Upgrade: websocket`、`Connection: upgrade`）；
- 在 WebSocket 升级请求中（而不仅限于普通 HTTP 请求）传递身份请求头；
- WebSocket 连接未配置独立的认证路径。

## 从 Token 认证迁移

若您正从 Token 认证迁移到受信任代理认证，请按以下步骤操作：

1. 配置代理以完成用户认证并传递请求头；
2. 独立测试代理配置（例如使用 curl 携带请求头测试）；
3. 更新 OpenClaw 配置，启用受信任代理认证；
4. 重启网关；
5. 从控制界面测试 WebSocket 连接；
6. 运行 `openclaw security audit` 并审阅检测结果。

## 相关

- [安全性](/gateway/security) — 完整的安全指南  
- [配置](/gateway/configuration) — 配置参考  
- [远程访问](/gateway/remote) — 其他远程访问模式  
- [Tailscale](/gateway/tailscale) — 仅限 tailnet 访问的更简单替代方案