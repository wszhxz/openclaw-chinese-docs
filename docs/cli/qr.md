---
summary: "CLI reference for `openclaw qr` (generate iOS pairing QR + setup code)"
read_when:
  - You want to pair the iOS app with a gateway quickly
  - You need setup-code output for remote/manual sharing
title: "qr"
---
# `openclaw qr`

根据当前网关配置生成 iOS 配对二维码和设置代码。

## 使用方法

```bash
openclaw qr
openclaw qr --setup-code-only
openclaw qr --json
openclaw qr --remote
openclaw qr --url wss://gateway.example/ws --token '<token>'
```

## 选项

- `--remote`: 使用 `gateway.remote.url`，并从配置中加载远程令牌/密码
- `--url <url>`: 覆盖有效载荷中使用的网关 URL
- `--public-url <url>`: 覆盖有效载荷中使用的公共 URL
- `--token <token>`: 覆盖有效载荷中使用的网关令牌
- `--password <password>`: 覆盖有效载荷中使用的网关密码
- `--setup-code-only`: 仅输出设置代码
- `--no-ascii`: 跳过 ASCII 格式二维码渲染
- `--json`: 输出 JSON（`setupCode`、`gatewayUrl`、`auth`、`urlSource`）

## 注意事项

- `--token` 和 `--password` 互斥。
- 使用 `--remote` 时，若实际生效的远程凭据已配置为 SecretRefs，且未传入 `--token` 或 `--password`，则该命令将从当前活动的网关快照中解析这些凭据；若网关不可用，则命令快速失败。
- 若未指定 `--remote`，当未通过 CLI 指定认证覆盖参数时，本地网关认证 SecretRefs 将被解析：
  - `gateway.auth.token` 在令牌认证可生效时被解析（显式指定 `gateway.auth.mode="token"`，或推断出无密码源胜出的模式）。
  - `gateway.auth.password` 在密码认证可生效时被解析（显式指定 `gateway.auth.mode="password"`，或推断出无令牌认证在认证/环境变量中胜出的模式）。
- 若同时配置了 `gateway.auth.token` 和 `gateway.auth.password`（包括 SecretRefs），且未设置 `gateway.auth.mode`，则设置代码解析将失败，直至显式指定认证模式。
- 网关版本兼容性说明：此命令路径要求网关支持 `secrets.resolve`；旧版网关将返回“未知方法”错误。
- 扫描完成后，请通过以下方式批准设备配对：
  - `openclaw devices list`
  - `openclaw devices approve <requestId>`