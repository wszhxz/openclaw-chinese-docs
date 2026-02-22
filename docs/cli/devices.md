---
summary: "CLI reference for `openclaw devices` (device pairing + token rotation/revocation)"
read_when:
  - You are approving device pairing requests
  - You need to rotate or revoke device tokens
title: "devices"
---
# `openclaw devices`

管理设备配对请求和设备范围的令牌。

## 命令

### `openclaw devices list`

列出待处理的配对请求和已配对的设备。

```
openclaw devices list
openclaw devices list --json
```

### `openclaw devices approve [requestId] [--latest]`

批准待处理的设备配对请求。如果省略`requestId`，OpenClaw会自动批准最新的待处理请求。

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

为特定角色轮换设备令牌（可选更新范围）。

```
openclaw devices rotate --device <deviceId> --role operator --scope operator.read --scope operator.write
```

### `openclaw devices revoke --device <id> --role <role>`

撤销特定角色的设备令牌。

```
openclaw devices revoke --device <deviceId> --role node
```

## 常用选项

- `--url <url>`: 网关WebSocket URL（当配置时默认为`gateway.remote.url`）。
- `--token <token>`: 网关令牌（如果需要）。
- `--password <password>`: 网关密码（密码认证）。
- `--timeout <ms>`: RPC超时。
- `--json`: JSON输出（推荐用于脚本编写）。

注意：当你设置`--url`时，CLI不会回退到配置或环境凭据。
显式传递`--token`或`--password`。缺少显式凭据是错误。

## 注意事项

- 令牌轮换会返回一个新令牌（敏感信息）。像对待机密一样处理它。
- 这些命令需要`operator.pairing`（或`operator.admin`）范围。