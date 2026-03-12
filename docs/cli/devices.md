---
summary: "CLI reference for `openclaw devices` (device pairing + token rotation/revocation)"
read_when:
  - You are approving device pairing requests
  - You need to rotate or revoke device tokens
title: "devices"
---
# `openclaw devices`

管理设备配对请求和设备级令牌。

## 命令

### `openclaw devices list`

列出待处理的配对请求及已配对的设备。

```
openclaw devices list
openclaw devices list --json
```

### `openclaw devices remove <deviceId>`

移除一个已配对的设备条目。

```
openclaw devices remove <deviceId>
openclaw devices remove <deviceId> --json
```

### `openclaw devices clear --yes [--pending]`

批量清除已配对的设备。

```
openclaw devices clear --yes
openclaw devices clear --yes --pending
openclaw devices clear --yes --pending --json
```

### `openclaw devices approve [requestId] [--latest]`

批准一个待处理的设备配对请求。如果省略了 `requestId`，OpenClaw 将自动批准最新的一条待处理请求。

```
openclaw devices approve
openclaw devices approve <requestId>
openclaw devices approve --latest
```

### `openclaw devices reject <requestId>`

拒绝一个待处理的设备配对请求。

```
openclaw devices reject <requestId>
```

### `openclaw devices rotate --device <id> --role <role> [--scope <scope...>]`

为特定角色轮换设备令牌（可选地更新作用域）。

```
openclaw devices rotate --device <deviceId> --role operator --scope operator.read --scope operator.write
```

### `openclaw devices revoke --device <id> --role <role>`

撤销特定角色的设备令牌。

```
openclaw devices revoke --device <deviceId> --role node
```

## 常用选项

- `--url <url>`: 网关 WebSocket URL（配置后默认为 `gateway.remote.url`）。
- `--token <token>`: 网关令牌（如需）。
- `--password <password>`: 网关密码（密码认证方式）。
- `--timeout <ms>`: RPC 超时时间。
- `--json`: JSON 格式输出（建议用于脚本调用）。

注意：当设置了 `--url` 后，CLI 不会回退至配置文件或环境变量中的凭据。请显式传入 `--token` 或 `--password`。缺少显式凭据将导致错误。

## 注意事项

- 令牌轮换将返回一个新令牌（敏感信息），应将其视为密钥进行保护。
- 这些命令需要具备 `operator.pairing`（或 `operator.admin`）作用域权限。
- `devices clear` 故意受到 `--yes` 的限制。
- 如果本地环回地址上不可用配对作用域（且未显式传入 `--url`），则 `list`/`approve` 命令可使用本地配对回退机制。