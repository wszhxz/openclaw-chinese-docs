---
summary: "CLI reference for `openclaw devices` (device pairing + token rotation/revocation)"
read_when:
  - You are approving device pairing requests
  - You need to rotate or revoke device tokens
title: "devices"
---
# `openclaw devices`

管理设备配对请求和设备范围令牌。

## 命令

### `openclaw devices list`

列出待处理的配对请求和已配对的设备。

```
openclaw devices list
openclaw devices list --json
```

### `openclaw devices remove <deviceId>`

移除一个已配对设备条目。

```
openclaw devices remove <deviceId>
openclaw devices remove <deviceId> --json
```

### `openclaw devices clear --yes [--pending]`

批量清除已配对设备。

```
openclaw devices clear --yes
openclaw devices clear --yes --pending
openclaw devices clear --yes --pending --json
```

### `openclaw devices approve [requestId] [--latest]`

批准待处理的设备配对请求。如果省略 `requestId`，OpenClaw 会自动批准最近的待处理请求。

```
openclaw devices approve
openclaw devices approve <requestId>
openclaw devices approve --latest
```

### `openclaw devices reject <requestId>`

拒绝待处理的设备配对请求。

```
openclaw devices reject <requestId>
```

### `openclaw devices rotate --device <id> --role <role> [--scope <scope...>]`

轮换特定角色的设备令牌（可选更新范围）。

```
openclaw devices rotate --device <deviceId> --role operator --scope operator.read --scope operator.write
```

### `openclaw devices revoke --device <id> --role <role>`

撤销特定角色的设备令牌。

```
openclaw devices revoke --device <deviceId> --role node
```

## 常用选项

- `--url <url>`：网关 WebSocket URL（配置后默认为 `gateway.remote.url`）。
- `--token <token>`：网关令牌（如果需要）。
- `--password <password>`：网关密码（密码认证）。
- `--timeout <ms>`：RPC 超时。
- `--json`：JSON 输出（推荐用于脚本）。

注意：设置 `--url` 时，CLI 不会回退到配置或环境凭据。
请显式传递 `--token` 或 `--password`。缺少显式凭据将导致错误。

## 注意事项

- 令牌轮换会返回一个新令牌（敏感）。请将其视为秘密处理。
- 这些命令需要 `operator.pairing`（或 `operator.admin`）范围。
- `devices clear` 特意受 `--yes` 管控。
- 如果本地回环上不可用配对范围（且未传递显式的 `--url`），list/approve 可以使用本地配对回退方案。