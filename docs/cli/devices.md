---
summary: "CLI reference for `openclaw devices` (device pairing + token rotation/revocation)"
read_when:
  - You are approving device pairing requests
  - You need to rotate or revoke device tokens
title: "devices"
---
# `openclaw 设备`

管理设备配对请求和设备作用域的令牌。

## 命令

### `openclaw devices list`

列出待处理的配对请求和已配对的设备。

```
openclaw devices list
openclaw devices list --json
```

### `openclaw devices approve <requestId>`

批准待处理的设备配对请求。

```
openclaw devices approve <requestId>
```

### `openclaw devices reject <requestId>`

拒绝待处理的设备配对请求。

```
openclaw devices reject <requestId>
```

### `openclaw devices rotate --device <id> --role <role> [--scope <scope. ..>]`

为特定角色旋转设备令牌（可选地更新作用域）。

```
openclaw devices rotate --device <deviceId> --role operator --scope operator.read --scope operator.write
```

### `openclaw devices revoke --device <id> --role <role>`

撤销特定角色的设备令牌。

```
openclaw devices revoke --device <deviceId> --role node
```

## 公共选项

- `--url <url>`：网关 WebSocket URL（在配置时默认为 `gateway.remote.url`）。
- `--token <token>`：网关令牌（如需）。
- `--password <password>`：网关密码（密码认证）。
- `--timeout <ms>`：RPC 超时时间。
- `--json`：JSON 输出（推荐用于脚本）。

## 注意事项

- 令牌轮换返回新令牌（敏感）。将其视为机密。
- 这些命令需要 `operator.pairing`（或 `operator.admin`）作用域。