---
summary: "Run the ACP bridge for IDE integrations"
read_when:
  - Setting up ACP-based IDE integrations
  - Debugging ACP session routing to the Gateway
title: "acp"
---
# acp

运行与 OpenClaw Gateway 通信的 ACP (Agent Client Protocol) 桥接。

该命令通过 stdio 使用 ACP 与 IDE 进行通信，并通过 WebSocket 将提示转发到网关。
它将 ACP 会话映射到网关会话密钥。

## 使用方法

```bash
openclaw acp

# Remote Gateway
openclaw acp --url wss://gateway-host:18789 --token <token>

# Attach to an existing session key
openclaw acp --session agent:main:main

# Attach by label (must already exist)
openclaw acp --session-label "support inbox"

# Reset the session key before the first prompt
openclaw acp --session agent:main:main --reset-session
```

## ACP 客户端（调试）

使用内置的 ACP 客户端在没有 IDE 的情况下检查桥接的正常性。
它会启动 ACP 桥接并允许您交互式地输入提示。

```bash
openclaw acp client

# Point the spawned bridge at a remote Gateway
openclaw acp client --server-args --url wss://gateway-host:18789 --token <token>

# Override the server command (default: openclaw)
openclaw acp client --server "node" --server-args openclaw.mjs acp --url ws://127.0.0.1:19001
```

## 如何使用

当 IDE（或其他客户端）使用 Agent Client Protocol 时，使用 ACP 来驱动 OpenClaw Gateway 会话。

1. 确保网关正在运行（本地或远程）。
2. 配置网关目标（配置文件或标志）。
3. 将您的 IDE 指向通过 stdio 运行 `openclaw acp`。

示例配置（持久化）：

```bash
openclaw config set gateway.remote.url wss://gateway-host:18789
openclaw config set gateway.remote.token <token>
```

示例直接运行（不写入配置）：

```bash
openclaw acp --url wss://gateway-host:18789 --token <token>
```

## 选择代理

ACP 不直接选择代理。它通过网关会话密钥进行路由。

使用代理范围的会话密钥来定位特定代理：

```bash
openclaw acp --session agent:main:main
openclaw acp --session agent:design:main
openclaw acp --session agent:qa:bug-123
```

每个 ACP 会话映射到一个网关会话密钥。一个代理可以有多个会话；ACP 默认使用隔离的 `acp:<uuid>` 会话，除非您覆盖密钥或标签。

## Zed 编辑器设置

在 `~/.config/zed/settings.json` 中添加自定义 ACP 代理（或使用 Zed 的设置界面）：

```json
{
  "agent_servers": {
    "OpenClaw ACP": {
      "type": "custom",
      "command": "openclaw",
      "args": ["acp"],
      "env": {}
    }
  }
}
```

要定位特定的网关或代理：

```json
{
  "agent_servers": {
    "OpenClaw ACP": {
      "type": "custom",
      "command": "openclaw",
      "args": [
        "acp",
        "--url",
        "wss://gateway-host:18789",
        "--token",
        "<token>",
        "--session",
        "agent:design:main"
      ],
      "env": {}
    }
  }
}
```

在 Zed 中，打开代理面板并选择“OpenClaw ACP”以启动线程。

## 会话映射

默认情况下，ACP 会话获得带有 `acp:` 前缀的隔离网关会话密钥。
要重用已知会话，请传递会话密钥或标签：

- `--session <key>`：使用特定的网关会话密钥。
- `--session-label <label>`：通过标签解析现有会话。
- `--reset-session`：为该密钥生成新的会话 ID（相同的密钥，新的对话记录）。

如果您的 ACP 客户端支持元数据，您可以按会话覆盖：

```json
{
  "_meta": {
    "sessionKey": "agent:main:main",
    "sessionLabel": "support inbox",
    "resetSession": true
  }
}
```

有关会话密钥的更多信息，请参阅 [/concepts/session](/concepts/session)。

## 选项

- `--url <url>`：网关 WebSocket URL（当配置时，默认为 gateway.remote.url）。
- `--token <token>`：网关认证令牌。
- `--password <password>`：网关认证密码。
- `--session <key>`：默认会话密钥。
- `--session-label <label>`：要解析的默认会话标签。
- `--require-existing`：如果会话密钥/标签不存在则失败。
- `--reset-session`：首次使用前重置会话密钥。
- `--no-prefix-cwd`：不在提示前加上工作目录。
- `--verbose, -v`：详细日志记录到 stderr。

### `acp client` 选项

- `--cwd <dir>`：ACP 会话的工作目录。
- `--server <command>`：ACP 服务器命令（默认：`openclaw`）。
- `openclaw`：传递给 ACP 服务器的额外参数。
- `--server-args <args...>`：在 ACP 服务器上启用详细日志记录。
- `--server-verbose`：详细客户端日志记录。