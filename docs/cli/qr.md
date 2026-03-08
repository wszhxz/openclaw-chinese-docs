---
summary: "CLI reference for `openclaw qr` (generate iOS pairing QR + setup code)"
read_when:
  - You want to pair the iOS app with a gateway quickly
  - You need setup-code output for remote/manual sharing
title: "qr"
---
# `openclaw qr`

从您当前的 Gateway 配置生成 iOS 配对 QR 和 setup code。

## 用法

```bash
openclaw qr
openclaw qr --setup-code-only
openclaw qr --json
openclaw qr --remote
openclaw qr --url wss://gateway.example/ws --token '<token>'
```

## 选项

- `--remote`：使用 `gateway.remote.url` 加上 config 中的 remote token/password
- `--url <url>`：覆盖 payload 中使用的 gateway URL
- `--public-url <url>`：覆盖 payload 中使用的 public URL
- `--token <token>`：覆盖 payload 的 gateway token
- `--password <password>`：覆盖 payload 的 gateway password
- `--setup-code-only`：仅打印 setup code
- `--no-ascii`：跳过 ASCII QR rendering
- `--json`：输出 JSON（`setupCode`、`gatewayUrl`、`auth`、`urlSource`）

## 注意事项

- `--token` 和 `--password` 互斥。
- 使用 `--remote` 时，如果有效激活的 remote credentials 配置为 SecretRefs 且您未传递 `--token` 或 `--password`，命令将从 active gateway snapshot 解析它们。如果 gateway 不可用，命令将快速失败。
- 不使用 `--remote` 时，当未传递 CLI auth override 时，local gateway auth SecretRefs 会被解析：
  - 当 token auth 优先时解析 `gateway.auth.token`（显式 `gateway.auth.mode="token"` 或推断模式下没有 password source 优先）。
  - 当 password auth 优先时解析 `gateway.auth.password`（显式 `gateway.auth.mode="password"` 或推断模式下 auth/env 中没有优先的 token）。
- 如果 `gateway.auth.token` 和 `gateway.auth.password` 都配置了（包括 SecretRefs）且 `gateway.auth.mode` 未设置，setup-code resolution 将失败，直到显式设置 mode。
- Gateway version skew 注意：此 command path 需要支持 `secrets.resolve` 的 gateway；较旧的 gateway 会返回 unknown-method error。
- 扫描后，使用以下命令批准 device pairing：
  - `openclaw devices list`
  - `openclaw devices approve <requestId>`