---
summary: "Run the ACP bridge for IDE integrations"
read_when:
  - Setting up ACP-based IDE integrations
  - Debugging ACP session routing to the Gateway
title: "acp"
---
# acp

运行 [代理客户端协议 (ACP)](https://agentclientprotocol.com/) 桥接器，该桥接器与 OpenClaw Gateway 通信。

此命令通过 stdio 为 IDE 提供 ACP 支持，并通过 WebSocket 将提示转发到 Gateway。它保持 ACP 会话映射到 Gateway 会话密钥。

``openclaw acp`` 是一个基于 Gateway 的 ACP 桥接器，而非完整的 ACP 原生编辑器运行时。它专注于会话路由、提示传递和基本流式更新。

如果您希望外部 MCP 客户端直接与 OpenClaw 频道对话通信，而不是托管 ACP harness 会话，请使用 [``openclaw mcp serve``](/cli/mcp)。

## 这不是什么

本页面常与 ACP harness 会话混淆。

``openclaw acp`` 意味着：

- OpenClaw 充当 ACP 服务器
- IDE 或 ACP 客户端连接到 OpenClaw
- OpenClaw 将该工作转发到 Gateway 会话

这与 [ACP Agents](/tools/acp-agents) 不同，后者 OpenClaw 通过 ``acpx`` 运行外部 harness（如 Codex 或 Claude Code）。

快速规则：

- 编辑器/客户端想要与 OpenClaw 进行 ACP 通信：使用 ``openclaw acp``
- OpenClaw 应启动 Codex/Claude/Gemini 作为 ACP harness：使用 ``/acp spawn`` 和 [ACP Agents](/tools/acp-agents)

## 兼容性矩阵

| ACP 区域                                                              | 状态      | 备注                                                                                                                                                                                                                                            |
| --------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ``initialize``, ``newSession``, ``prompt``, ``cancel``                        | 已实现 | 核心桥接流程，通过 stdio 到 Gateway 聊天/发送 + 中止。                                                                                                                                                                                        |
| ``listSessions``, 斜杠命令                                        | 已实现 | 会话列表针对 Gateway 会话状态工作；命令通过 ``available_commands_update`` 发布。                                                                                                                                       |
| ``loadSession``                                                         | 部分实现 | 将 ACP 会话重新绑定到 Gateway 会话密钥并重放存储的用户/助手文本历史。工具和系统历史尚未重建。                                                                                                   |
| 提示内容 (``text``, 嵌入的 ``resource``, 图像)                  | 部分实现 | 文本/资源被扁平化为聊天输入；图像变为 Gateway 附件。                                                                                                                                                                 |
| 会话模式                                                         | 部分实现 | 支持 ``session/set_mode``，且桥接器暴露初始的基于 Gateway 的会话控制，包括思维级别、工具详细程度、推理、使用详情和高级操作。更广泛的 ACP 原生模式/配置界面仍不在范围内。 |
| 会话信息和使用更新                                        | 部分实现 | 桥接器从缓存的 Gateway 会话快照中发出 ``session_info_update`` 和尽力而为的 ``usage_update`` 通知。使用情况是近似的，仅当 Gateway 令牌总数标记为新鲜时发送。                                        |
| 工具流式传输                                                        | 部分实现 | ``tool_call`` / ``tool_call_update`` 事件包含原始 I/O、文本内容，以及在 Gateway 工具参数/结果暴露它们时的最佳努力文件位置。嵌入式终端和更丰富的差异原生输出仍未暴露。                        |
| 每会话 MCP 服务器 (``mcpServers``)                                | 不支持 | 桥接模式拒绝每会话 MCP 服务器请求。请在 OpenClaw 网关或代理上配置 MCP。                                                                                                                                     |
| 客户端文件系统方法 (``fs/read_text_file``, ``fs/write_text_file``) | 不支持 | 桥接器不调用 ACP 客户端文件系统方法。                                                                                                                                                                                          |
| 客户端终端方法 (``terminal/*``)                                | 不支持 | 桥接器不创建 ACP 客户端终端或通过工具调用流式传输终端 ID。                                                                                                                                                       |
| 会话计划/思维流式传输                                     | 不支持 | 桥接器当前仅输出文本和工具状态，不输出 ACP 计划或思维更新。                                                                                                                                                         |

## 已知限制

- ``loadSession`` 重放存储的用户和助手文本历史，但它不重建历史工具调用、系统通知或更丰富的 ACP 原生事件类型。
- 如果多个 ACP 客户端共享相同的 Gateway 会话密钥，事件和取消路由是尽力而为的，而不是每个客户端严格隔离。当您需要进行干净的编辑器本地回合时，请优先使用默认隔离的 ``acp:<uuid>`` 会话。
- Gateway 停止状态被转换为 ACP 停止原因，但该映射不如完全 ACP 原生运行时表达力强。
- 初始会话控制目前显示 Gateway 设置的子集：思维级别、工具详细程度、推理、使用详情和高级操作。模型选择和执行主机控制尚未作为 ACP 配置选项暴露。
- ``session_info_update`` 和 ``usage_update`` 源自 Gateway 会话快照，而非实时 ACP 原生运行时会计。使用情况是近似的，不包含成本数据，仅在 Gateway 标记总令牌数据为新鲜时发出。
- 工具跟随数据是尽力而为的。桥接器可以显示出现在已知工具参数/结果中的文件路径，但它尚不发出 ACP 终端或结构化文件差异。

## 用法

````bash
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
````

## ACP 客户端 (调试)

使用内置 ACP 客户端在没有 IDE 的情况下验证桥接器。它会启动 ACP 桥接器并允许您交互式地输入提示。

````bash
openclaw acp client

# Point the spawned bridge at a remote Gateway
openclaw acp client --server-args --url wss://gateway-host:18789 --token-file ~/.openclaw/gateway.token

# Override the server command (default: openclaw)
openclaw acp client --server "node" --server-args openclaw.mjs acp --url ws://127.0.0.1:19001
````

权限模型（客户端调试模式）：

- 自动批准基于白名单，仅适用于受信任的核心工具 ID。
- ``read`` 自动批准的范围限定于当前工作目录 (``--cwd`` 当设置时)。
- ACP 仅自动批准狭窄的只读类别：活动 cwd 下的范围限定 ``read`` 调用加上只读搜索工具 (``search``, ``web_search``, ``memory_search``)。未知/非核心工具、超出范围的读取、可执行工具、控制平面工具、修改工具以及交互式流始终需要明确的提示批准。
- 服务器提供的 ``toolCall.kind`` 被视为不受信任的元数据（不是授权源）。
- 此 ACP 桥接策略与 ACPX harness 权限分开。如果您通过 ``acpx`` 后端运行 OpenClaw，则 ``plugins.entries.acpx.config.permissionMode=approve-all`` 是该 harness 会话的紧急 "yolo" 开关。

## 如何使用此功能

当 IDE（或其他客户端）使用代理客户端协议且您希望它驱动 OpenClaw Gateway 会话时使用 ACP。

1. 确保 Gateway 正在运行（本地或远程）。
2. 配置 Gateway 目标（配置或标志）。
3. 将您的 IDE 指向通过 stdio 运行 ``openclaw acp``。

示例配置（持久化）：

````bash
openclaw config set gateway.remote.url wss://gateway-host:18789
openclaw config set gateway.remote.token <token>
````

示例直接运行（不写入配置）：

````bash
openclaw acp --url wss://gateway-host:18789 --token <token>
# preferred for local process safety
openclaw acp --url wss://gateway-host:18789 --token-file ~/.openclaw/gateway.token
````

## 选择代理

ACP 不直接选择代理。它通过 Gateway 会话密钥进行路由。

使用代理范围会话密钥来定位特定代理：

````bash
openclaw acp --session agent:main:main
openclaw acp --session agent:design:main
openclaw acp --session agent:qa:bug-123
````

每个 ACP 会话映射到一个唯一的 Gateway 会话密钥。一个代理可以有多个会话；除非您覆盖密钥或标签，否则 ACP 默认为隔离的 ``acp:<uuid>`` 会话。

桥接模式下不支持每会话 ``mcpServers``。如果 ACP 客户端在 ``newSession`` 或 ``loadSession`` 期间发送它们，桥接器将返回清晰的错误，而不是静默忽略它们。

如果您希望基于 ACPX 的会话能够看到 OpenClaw 插件工具，请启用网关侧的 ACPX 插件桥接，而不是尝试传递每个会话的 `mcpServers`。参见 [ACP Agents](/tools/acp-agents#plugin-tools-mcp-bridge)。

## 从 `acpx` 使用（Codex、Claude 及其他 ACP 客户端）

如果您希望像 Codex 或 Claude Code 这样的编码代理通过 ACP 与您的 OpenClaw 机器人通信，请使用 `acpx` 及其内置的 `openclaw` 目标。

典型流程：

1. 运行 Gateway 并确保 ACP 桥接可以连接到它。
2. 将 `acpx openclaw` 指向 `openclaw acp`。
3. 指定编码代理要使用的 OpenClaw 会话密钥。

示例：

```bash
# One-shot request into your default OpenClaw ACP session
acpx openclaw exec "Summarize the active OpenClaw session state."

# Persistent named session for follow-up turns
acpx openclaw sessions ensure --name codex-bridge
acpx openclaw -s codex-bridge --cwd /path/to/repo \
  "Ask my OpenClaw work agent for recent context relevant to this repo."
```

如果您希望 `acpx openclaw` 每次都指向特定的 Gateway 和会话密钥，请在 `~/.acpx/config.json` 中覆盖 `openclaw` 代理命令：

```json
{
  "agents": {
    "openclaw": {
      "command": "env OPENCLAW_HIDE_BANNER=1 OPENCLAW_SUPPRESS_NOTES=1 openclaw acp --url ws://127.0.0.1:18789 --token-file ~/.openclaw/gateway.token --session agent:main:main"
    }
  }
}
```

对于本地仓库的 OpenClaw 检出，请使用直接的 CLI 入口点而不是开发运行器，以便 ACP 流保持干净。例如：

```bash
env OPENCLAW_HIDE_BANNER=1 OPENCLAW_SUPPRESS_NOTES=1 node openclaw.mjs acp ...
```

这是让 Codex、Claude Code 或其他 ACP 感知客户端无需抓取终端即可从 OpenClaw 代理拉取上下文信息的最简单方法。

## Zed 编辑器设置

在 `~/.config/zed/settings.json` 中添加自定义 ACP 代理（或使用 Zed 的设置 UI）：

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

若要指向特定的 Gateway 或代理：

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

在 Zed 中，打开 Agent 面板并选择“OpenClaw ACP”以启动线程。

## 会话映射

默认情况下，ACP 会话会获得一个带有 `acp:` 前缀的独立 Gateway 会话密钥。若要重用已知会话，请传递会话密钥或标签：

- `--session <key>`：使用特定的 Gateway 会话密钥。
- `--session-label <label>`：按标签解析现有会话。
- `--reset-session`：为该密钥生成新的会话 ID（相同密钥，新会话记录）。

如果您的 ACP 客户端支持元数据，您可以按会话进行覆盖：

```json
{
  "_meta": {
    "sessionKey": "agent:main:main",
    "sessionLabel": "support inbox",
    "resetSession": true
  }
}
```

有关会话密钥的更多信息，请访问 [/concepts/session](/concepts/session)。

## 选项

- `--url <url>`：Gateway WebSocket URL（配置时默认为 gateway.remote.url）。
- `--token <token>`：Gateway 身份验证令牌。
- `--token-file <path>`：从文件读取 Gateway 身份验证令牌。
- `--password <password>`：Gateway 身份验证密码。
- `--password-file <path>`：从文件读取 Gateway 身份验证密码。
- `--session <key>`：默认会话密钥。
- `--session-label <label>`：用于解析的默认会话标签。
- `--require-existing`：如果会话密钥/标签不存在则失败。
- `--reset-session`：首次使用前重置会话密钥。
- `--no-prefix-cwd`：提示符前不添加工作目录前缀。
- `--provenance <off|meta|meta+receipt>`：包含 ACP 来源元数据或收据。
- `--verbose, -v`：向 stderr 输出详细日志。

安全说明：

- `--token` 和 `--password` 在某些系统的本地进程列表中可能可见。
- 优先使用 `--token-file`/`--password-file` 或环境变量（`OPENCLAW_GATEWAY_TOKEN`, `OPENCLAW_GATEWAY_PASSWORD`）。
- Gateway 身份验证解析遵循其他 Gateway 客户端使用的共享约定：
  - 本地模式：环境 (`OPENCLAW_GATEWAY_*`) -> `gateway.auth.*` -> `gateway.remote.*` 回退仅在 `gateway.auth.*` 未设置时发生（已配置但未解析的本地 SecretRefs 失败关闭）
  - 远程模式：`gateway.remote.*`，根据远程优先级规则使用环境/配置回退
  - `--url` 是覆盖安全的，不会重用隐式配置/环境凭据；请传递显式的 `--token`/`--password`（或文件变体）
- ACP 运行时后端子进程接收 `OPENCLAW_SHELL=acp`，可用于特定上下文的 Shell/配置文件规则。
- `openclaw acp client` 在生成的桥接进程中设置 `OPENCLAW_SHELL=acp-client`。

### `acp client` 选项

- `--cwd <dir>`：ACP 会话的工作目录。
- `--server <command>`：ACP 服务器命令（默认值：`openclaw`）。
- `--server-args <args...>`：传递给 ACP 服务器的额外参数。
- `--server-verbose`：启用 ACP 服务器的详细日志记录。
- `--verbose, -v`：详细的客户端日志记录。