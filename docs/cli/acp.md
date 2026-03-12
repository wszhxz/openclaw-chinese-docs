---
summary: "Run the ACP bridge for IDE integrations"
read_when:
  - Setting up ACP-based IDE integrations
  - Debugging ACP session routing to the Gateway
title: "acp"
---
# acp

运行 [Agent Client Protocol（ACP）](https://agentclientprotocol.com/) 桥接程序，该程序与 OpenClaw 网关通信。

该命令通过标准输入/输出（stdio）与 IDE 等客户端进行 ACP 通信，并通过 WebSocket 将提示转发至网关。它将 ACP 会话持续映射到网关会话密钥。

## 用法

```bash
openclaw acp

# Remote Gateway
openclaw acp --url wss://gateway-host:18789 --token <token>

# Remote Gateway (token from file)
openclaw acp --url wss://gateway-host:18789 --token-file ~/.openclaw/gateway.token

# Attach to an existing session key
openclaw acp --session agent:main:main

# Attach by label (must already exist)
openclaw acp --session-label "support inbox"

# Reset the session key before the first prompt
openclaw acp --session agent:main:main --reset-session
```

## ACP 客户端（调试模式）

使用内置的 ACP 客户端，在不依赖 IDE 的情况下对桥接程序进行基本功能验证。  
它会启动 ACP 桥接程序，并允许你以交互方式输入提示。

```bash
openclaw acp client

# Point the spawned bridge at a remote Gateway
openclaw acp client --server-args --url wss://gateway-host:18789 --token-file ~/.openclaw/gateway.token

# Override the server command (default: openclaw)
openclaw acp client --server "node" --server-args openclaw.mjs acp --url ws://127.0.0.1:19001
```

权限模型（客户端调试模式）：

- 自动批准基于白名单机制，且仅适用于受信任的核心工具 ID。
- `read` 的自动批准作用域限定为当前工作目录（当设置为 `--cwd` 时）。
- 对于未知或非核心工具名称、超出作用域的读取操作，以及危险性工具，始终需要显式提示批准。
- 服务端提供的 `toolCall.kind` 被视为不可信元数据（不作为授权依据）。

## 如何使用本功能

当你的 IDE（或其他客户端）支持 Agent Client Protocol（ACP），且你希望它驱动一个 OpenClaw 网关会话时，请使用 ACP。

1. 确保网关正在运行（本地或远程均可）。
2. 配置网关目标（通过配置文件或命令行参数）。
3. 在 IDE 中配置其通过标准输入/输出（stdio）运行 `openclaw acp`。

示例配置（持久化保存）：

```bash
openclaw config set gateway.remote.url wss://gateway-host:18789
openclaw config set gateway.remote.token <token>
```

示例直接运行（不写入配置）：

```bash
openclaw acp --url wss://gateway-host:18789 --token <token>
# preferred for local process safety
openclaw acp --url wss://gateway-host:18789 --token-file ~/.openclaw/gateway.token
```

## 选择代理（Agent）

ACP 不直接选择代理。它通过网关会话密钥进行路由。

使用面向特定代理的会话密钥，可定向调用某个代理：

```bash
openclaw acp --session agent:main:main
openclaw acp --session agent:design:main
openclaw acp --session agent:qa:bug-123
```

每个 ACP 会话对应一个唯一的网关会话密钥。一个代理可拥有多个会话；除非你显式覆盖密钥或标签，否则 ACP 默认使用隔离的 `acp:<uuid>` 会话。

## Zed 编辑器配置

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

如需指定特定网关或代理：

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

在 Zed 中，打开“Agent”面板并选择“OpenClaw ACP”，即可启动一个对话线程。

## 会话映射

默认情况下，ACP 会话将获得一个带 `acp:` 前缀的隔离网关会话密钥。  
若要复用已知会话，请传入会话密钥或标签：

- `--session <key>`：使用指定的网关会话密钥。
- `--session-label <label>`：按标签解析已有会话。
- `--reset-session`：为该密钥生成一个全新的会话 ID（密钥相同，但对话记录全新）。

如果你的 ACP 客户端支持元数据，你还可以按会话覆盖配置：

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

- `--url <url>`：网关 WebSocket URL（若已配置，则默认为 `gateway.remote.url`）。
- `--token <token>`：网关认证令牌。
- `--token-file <path>`：从文件读取网关认证令牌。
- `--password <password>`：网关认证密码。
- `--password-file <path>`：从文件读取网关认证密码。
- `--session <key>`：默认会话密钥。
- `--session-label <label>`：用于解析的默认会话标签。
- `--require-existing`：若会话密钥/标签不存在则报错退出。
- `--reset-session`：首次使用前重置会话密钥。
- `--no-prefix-cwd`：不在提示前添加工作目录路径前缀。
- `--verbose, -v`：向标准错误输出（stderr）输出详细日志。

安全说明：

- `--token` 和 `--password` 在某些系统上可能在本地进程列表中可见。
- 推荐使用 `--token-file`/`--password-file` 或环境变量（`OPENCLAW_GATEWAY_TOKEN`、`OPENCLAW_GATEWAY_PASSWORD`）。
- 网关认证解析遵循其他网关客户端所共用的约定：
  - 本地模式：环境变量（`OPENCLAW_GATEWAY_*`）→ `gateway.auth.*` → `gateway.remote.*`（当 `gateway.auth.*` 未设置时的回退方案）
  - 远程模式：`gateway.remote.*`，并依据远程优先级规则进行环境变量/配置回退
  - `--url` 是可安全覆盖的选项，不会复用隐式的配置/环境凭证；请显式传入 `--token`/`--password`（或其文件变体）
- ACP 运行时后端子进程接收 `OPENCLAW_SHELL=acp`，可用于上下文相关的 shell/profile 规则。
- `openclaw acp client` 会在启动的桥接进程中设置 `OPENCLAW_SHELL=acp-client`。

### `acp client` 选项

- `--cwd <dir>`：ACP 会话的工作目录。
- `--server <command>`：ACP 服务端命令（默认为 `openclaw`）。
- `--server-args <args...>`：传递给 ACP 服务端的额外参数。
- `--server-verbose`：在 ACP 服务端启用详细日志。
- `--verbose, -v`：启用客户端详细日志。