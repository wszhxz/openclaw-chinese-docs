---
summary: "Run the ACP bridge for IDE integrations"
read_when:
  - Setting up ACP-based IDE integrations
  - Debugging ACP session routing to the Gateway
title: "acp"
---
# acp

运行与 OpenClaw 网关通信的 ACP（Agent 客户端协议）桥接器。

此命令通过 stdio 以 ACP 协议与 IDE 通信，并通过 WebSocket 将提示转发到网关。它会将 ACP 会话映射到网关会话密钥。

## 使用方法

```bash
openclaw acp

# 远程网关
openclaw acp --url wss://gateway-host:18789 --token <token>

# 附加到现有会话密钥
openclaw acp --session agent:main:main

# 通过标签附加（必须已存在）
openclaw acp --session-label "support inbox"

# 在首次提示前重置会话密钥
openclaw acp --session agent:main:main --reset-session
```

## ACP 客户端（调试）

使用内置的 ACP 客户端在没有 IDE 的情况下对桥接器进行健康检查。它会启动 ACP 桥接器并允许您交互式输入提示。

```bash
openclaw acp client

# 指定生成的桥接器连接到远程网关
openclaw acp client --server-args --url wss://gateway-host:18789 --token <token>

# 覆盖服务器命令（默认：openclaw）
openclaw acp client --server "node" --server-args openclaw.mjs acp --url ws://127.0.0.1:19001
```

## 如何使用

当 IDE（或其他客户端）支持 Agent 客户端协议且您希望其驱动 OpenClaw 网关会话时，请使用 ACP。

1. 确保网关正在运行（本地或远程）。
2. 配置网关目标（配置或标志）。
3. 将您的 IDE 指向通过 stdio 运行 `openclaw acp`。

示例配置（持久化）：

```bash
openclaw config set gateway.remote.url wss://gateway-host:18789
openclaw config set gateway.remote.token <token>
```

示例直接运行（无需写入配置）：

```bash
openclaw acp --url wss://gateway-host:18789 --token <token>
```

## 选择代理

ACP 不直接选择代理。它通过网关会话密钥进行路由。

使用代理作用域的会话密钥来指定特定代理：

```bash
openclaw acp --session agent:main:main
openclaw acp --session agent:design:main
openclaw acp --session agent:qa:bug-123
```

每个 ACP 会话映射到一个网关会话密钥。一个代理可以有多个会话；ACP 默认使用隔离的 `acp:<uuid>` 会话，除非您覆盖密钥或标签。

## Zed 编辑器设置

在 `~/.config/zed/settings.json` 中添加一个自定义 ACP 代理（或使用 Zed 的设置界面）：

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

要指定特定的网关或代理：

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

默认情况下，ACP 会话会获得一个带有 `acp:` 前缀的隔离网关会话密钥。要重用已知会话，请传递会话密钥或标签：

- `--session <key>`：使用特定的网关会话密钥。
- `--session-label <label>`：通过标签解析现有会话。
- `--reset-session`：为该密钥生成新的会话 ID（相同密钥，新会话记录）。

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

了解更多关于会话密钥的信息，请参阅 [/concepts/session](/concepts/session)。

## 选项

- `--url <url>`：网关 WebSocket URL（默认为配置的 gateway.remote.url）。
- `--token <token>`：网关认证令牌。
- `--password <password>`：网关认证密码。
- `--session <key>`：默认会话密钥。
- `--session-label <label>`：默认会话标签。
- `--require-existing`：如果会话密钥/标签不存在则失败。
- `--reset-session`：在首次使用前重置会话密钥。
- `--no-prefix-cwd`：不要在提示前添加工作目录。
- `--verbose, -v`：向 stderr 输出详细日志。

### `acp client` 选项

- `--cwd <dir>`：ACP 会话的工作目录。
- `--server <command>`：ACP 服务器命令（默认：`openclaw`）。
- `--server-args <args...>`：传递给 ACP 服务器的额外参数。
- `--server-verbose`：启用 ACP 服务器的详细日志。
- `--verbose, -v`：客户端详细日志。