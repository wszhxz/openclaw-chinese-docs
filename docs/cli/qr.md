---
summary: "CLI reference for `openclaw qr` (generate mobile pairing QR + setup code)"
read_when:
  - You want to pair a mobile node app with a gateway quickly
  - You need setup-code output for remote/manual sharing
title: "qr"
---
# `openclaw qr`

从您当前的 Gateway 配置生成 Mobile Pairing QR 和 Setup Code。

## 用法

```bash
openclaw qr
openclaw qr --setup-code-only
openclaw qr --json
openclaw qr --remote
openclaw qr --url wss://gateway.example/ws
```

## 选项

- `--remote`: 偏好 `gateway.remote.url`；如果未设置，`gateway.tailscale.mode=serve|funnel` 仍可提供 Remote Public URL
- `--url <url>`: 覆盖 Payload 中使用的 Gateway URL
- `--public-url <url>`: 覆盖 Payload 中使用的 Public URL
- `--token <token>`: 覆盖 Bootstrap Flow 验证的 Gateway Token
- `--password <password>`: 覆盖 Bootstrap Flow 验证的 Gateway Password
- `--setup-code-only`: 仅打印 Setup Code
- `--no-ascii`: 跳过 ASCII QR Rendering
- `--json`: 输出 JSON (`setupCode`, `gatewayUrl`, `auth`, `urlSource`)

## 注意

- `--token` 和 `--password` 互斥。
- Setup Code 本身现在携带不透明的短期 `bootstrapToken`，而不是共享的 Gateway Token/Password。
- 在内置的 Node/Operator Bootstrap Flow 中，Primary Node Token 仍然与 `scopes: []` 一起落地。
- 如果 Bootstrap Handoff 也颁发 Operator Token，它保持在 Bootstrap Allowlist 范围内：`operator.approvals`, `operator.read`, `operator.talk.secrets`, `operator.write`。
- Bootstrap Scope Checks 是 Role-Prefixed 的。该 Operator Allowlist 仅满足 Operator Requests；Non-Operator Roles 仍需在其各自的 Role Prefix 下拥有 Scopes。
- Mobile Pairing 对 Tailscale/Public `ws://` Gateway URLs 失败关闭。Private LAN `ws://` 仍受支持，但 Tailscale/Public Mobile Routes 应使用 Tailscale Serve/Funnel 或 `wss://` Gateway URL。
- 使用 `--remote` 时，OpenClaw 需要 `gateway.remote.url` 或 `gateway.tailscale.mode=serve|funnel`。
- 使用 `--remote` 时，如果有效活动的 Remote Credentials 配置为 SecretRefs 且您未传递 `--token` 或 `--password`，命令将从 Active Gateway Snapshot 解析它们。如果 Gateway 不可用，命令将快速失败。
- 没有 `--remote` 时，Local Gateway Auth SecretRefs 将在未传递 CLI Auth Override 时解析：
  - `gateway.auth.token` 在 Token Auth 可以获胜时解析（明确的 `gateway.auth.mode="token"` 或推断 Mode，其中无 Password Source 获胜）。
  - `gateway.auth.password` 在 Password Auth 可以获胜时解析（明确的 `gateway.auth.mode="password"` 或推断 Mode，其中无来自 Auth/Env 的获胜 Token）。
- 如果同时配置了 `gateway.auth.token` 和 `gateway.auth.password`（包括 SecretRefs）且 `gateway.auth.mode` 未设置，则直到明确设置 Mode 之前，Setup-code Resolution 将失败。
- Gateway Version Skew Note：此命令路径需要一个支持 `secrets.resolve` 的 Gateway；旧版 Gateways 返回 Unknown-method Error。
- 扫描后，使用以下命令批准 Device Pairing：
  - `openclaw devices list`
  - `openclaw devices approve <requestId>`