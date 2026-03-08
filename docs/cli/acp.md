---
summary: "Run the ACP bridge for IDE integrations"
read_when:
  - Setting up ACP-based IDE integrations
  - Debugging ACP session routing to the Gateway
title: "acp"
---
# acp

运行与 OpenClaw Gateway 通信的 [Agent Client Protocol (ACP)](https://agentclientprotocol.com/) 桥接器。

此命令通过 stdio 为 IDE 提供 ACP 通信，并通过 WebSocket 将提示转发到 Gateway。它保持 ACP 会话与 Gateway 会话密钥的映射。

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

## ACP 客户端（调试）

使用内置的 ACP 客户端在不借助 IDE 的情况下对桥接器进行健全性检查。
它会生成 ACP 桥接器并允许您交互式地输入提示。

```bash
openclaw acp client

# Point the spawned bridge at a remote Gateway
openclaw acp client --server-args --url wss://gateway-host:18789 --token-file ~/.openclaw/gateway.token

# Override the server command (default: openclaw)
openclaw acp client --server "node" --server-args openclaw.mjs acp --url ws://127.0.0.1:19001
```

权限模型（客户端调试模式）：

- 自动批准基于允许列表，仅适用于受信任的核心工具 ID。
- ``read`` 自动批准限定于当前工作目录（设置 ``--cwd`` 时）。
- 未知/非核心工具名称、范围外读取和危险工具始终需要明确的提示批准。
- 服务器提供的 ``toolCall.kind`` 被视为不可信的元数据（不是授权来源）。

## 如何使用

当 IDE（或其他客户端）使用 Agent Client Protocol 通信且您希望它驱动 OpenClaw Gateway 会话时，请使用 ACP。

1. 确保 Gateway 正在运行（本地或远程）。
2. 配置 Gateway 目标（配置或标志）。
3. 指向您的 IDE 通过 stdio 运行 ``openclaw acp``。

示例配置（持久化）：

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

## 选择代理

ACP 不直接选择代理。它通过 Gateway 会话密钥进行路由。

使用代理范围的会话密钥来定位特定代理：

```bash
openclaw acp --session agent:main:main
openclaw acp --session agent:design:main
openclaw acp --session agent:qa:bug-123
```

每个 ACP 会话映射到单个 Gateway 会话密钥。一个代理可以拥有多个会话；除非您覆盖密钥或标签，否则 ACP 默认为隔离的 ``acp:<uuid>`` 会话。

## Zed 编辑器设置

在 ``~/.config/zed/settings.json`` 中添加自定义 ACP 代理（或使用 Zed 的设置 UI）：

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

要定位特定 Gateway 或代理：

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

在 Zed 中，打开 Agent 面板并选择"OpenClaw ACP"以启动线程。

## 会话映射

默认情况下，ACP 会话获得带有 ``acp:`` 前缀的隔离 Gateway 会话密钥。
要重用已知会话，传递会话密钥或标签：

- ``--session <key>``：使用特定 Gateway 会话密钥。
- ``--session-label <label>``：按标签解析现有会话。
- ``--reset-session``：为该密钥生成新的会话 id（相同密钥，新记录）。

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

在 [/concepts/session](/concepts/session) 了解更多关于会话密钥的信息。

## 选项

- ``--url <url>``：Gateway WebSocket URL（配置时默认为 gateway.remote.url）。
- ``--token <token>``：Gateway 认证令牌。
- ``--token-file <path>``：从文件读取 Gateway 认证令牌。
- ``--password <password>``：Gateway 认证密码。
- ``--password-file <path>``：从文件读取 Gateway 认证密码。
- ``--session <key>``：默认会话密钥。
- ``--session-label <label>``：要解析的默认会话标签。
- ``--require-existing``：如果会话密钥/标签不存在则失败。
- ``--reset-session``：首次使用前重置会话密钥。
- ``--no-prefix-cwd``：不要在工作目录前缀提示。
- ``--verbose, -v``：向 stderr 输出详细日志。

安全说明：

- ``--token`` 和 ``--password`` 在某些系统上可能在本地进程列表中可见。
- 首选 ``--token-file``/``--password-file`` 或环境变量（``OPENCLAW_GATEWAY_TOKEN``，``OPENCLAW_GATEWAY_PASSWORD``）。
- Gateway 认证解析遵循其他 Gateway 客户端使用的共享契约：
  - 本地模式：env (``OPENCLAW_GATEWAY_*``) -> ``gateway.auth.*`` -> ``gateway.remote.*`` 当 ``gateway.auth.*`` 未设置时的回退
  - 远程模式：``gateway.remote.*`` 带有根据远程优先级规则的 env/配置 回退
  - ``--url`` 是覆盖安全的，不重用隐式配置/环境变量凭据；传递显式的 ``--token``/``--password``（或文件变体）
- ACP 运行时后端子进程接收 ``OPENCLAW_SHELL=acp``，可用于特定上下文的 shell/profile 规则。
- ``openclaw acp client`` 在生成的桥接进程上设置 ``OPENCLAW_SHELL=acp-client``。

### ``acp client`` 选项

- ``--cwd <dir>``：ACP 会话的工作目录。
- ``--server <command>``：ACP 服务器命令（默认：``openclaw``）。
- ``--server-args <args...>``：传递给 ACP 服务器的额外参数。
- ``--server-verbose``：在 ACP 服务器上启用详细日志记录。
- ``--verbose, -v``：详细客户端日志记录。