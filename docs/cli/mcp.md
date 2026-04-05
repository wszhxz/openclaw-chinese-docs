---
summary: "Expose OpenClaw channel conversations over MCP and manage saved MCP server definitions"
read_when:
  - Connecting Codex, Claude Code, or another MCP client to OpenClaw-backed channels
  - Running `openclaw mcp serve`
  - Managing OpenClaw-saved MCP server definitions
title: "mcp"
---
# mcp

`openclaw mcp` 有两个任务：

- 使用 `openclaw mcp serve` 运行 OpenClaw 作为 MCP 服务器
- 使用 `list`, `show`,
  `set`, 和 `unset` 管理 OpenClaw 拥有的出站 MCP 服务器定义

换句话说：

- `serve` 是 OpenClaw 充当 MCP 服务器
- `list` / `show` / `set` / `unset` 是 OpenClaw 充当 MCP 客户端注册表，用于其运行时稍后可能消费的其他 MCP 服务器

使用 [`openclaw acp`](/cli/acp) 当 OpenClaw 应托管编码工具会话本身并通过 ACP 路由该运行时。

## OpenClaw 作为 MCP 服务器

这是 `openclaw mcp serve` 路径。

## 何时使用 `serve`

当以下条件满足时使用 `openclaw mcp serve`：

- Codex、Claude Code 或其他 MCP 客户端应直接与 OpenClaw 支持的频道对话通信
- 您已拥有带有路由会话的本地或远程 OpenClaw Gateway
- 您希望有一个 MCP 服务器可在 OpenClaw 的频道后端之间工作，而不是为每个频道运行单独的桥接器

如果 OpenClaw 应托管编码运行时本身并将代理会话保留在 OpenClaw 内部，请使用 [`openclaw acp`](/cli/acp)。

## 工作原理

`openclaw mcp serve` 启动一个 stdio MCP 服务器。MCP 客户端拥有该进程。只要客户端保持 stdio 会话打开，桥接器就会通过 WebSocket 连接到本地或远程 OpenClaw Gateway，并通过 MCP 暴露路由的频道对话。

生命周期：

1. MCP 客户端启动 `openclaw mcp serve`
2. 桥接器连接到 Gateway
3. 路由会话变为 MCP 对话以及转录/历史记录工具
4. 实时事件在桥接器连接期间排队到内存中
5. 如果启用了 Claude 频道模式，同一会话还可以接收特定的 Claude 推送通知

重要行为：

- 实时队列状态在桥接器连接时开始
- 较旧的转录历史记录使用 `messages_read` 读取
- Claude 推送通知仅在 MCP 会话存活时存在
- 当客户端断开连接时，桥接器退出，实时队列消失

## 选择客户端模式

以两种不同的方式使用同一个桥接器：

- 通用 MCP 客户端：仅标准 MCP 工具。使用 `conversations_list`,
  `messages_read`, `events_poll`, `events_wait`, `messages_send`, 以及批准工具。
- Claude Code：标准 MCP 工具加上特定于 Claude 的频道适配器。启用 `--claude-channel-mode on` 或保留默认值 `auto`。

目前，`auto` 的行为与 `on` 相同。尚未进行客户端功能检测。

## `serve` 暴露什么

桥接器使用现有的 Gateway 会话路由元数据来暴露基于频道的对话。当 OpenClaw 已经拥有具有已知路由的会话状态时，会出现对话，例如：

- `channel`
- 收件人或目标元数据
- 可选的 `accountId`
- 可选的 `threadId`

这为 MCP 客户端提供了一个位置来：

- 列出最近的路由对话
- 读取最近的转录历史
- 等待新的入站事件
- 通过相同的路由发送回复
- 查看桥接器连接期间到达的批准请求

## 用法

```bash
# Local Gateway
openclaw mcp serve

# Remote Gateway
openclaw mcp serve --url wss://gateway-host:18789 --token-file ~/.openclaw/gateway.token

# Remote Gateway with password auth
openclaw mcp serve --url wss://gateway-host:18789 --password-file ~/.openclaw/gateway.password

# Enable verbose bridge logs
openclaw mcp serve --verbose

# Disable Claude-specific push notifications
openclaw mcp serve --claude-channel-mode off
```

## 桥接器工具

当前桥接器暴露以下 MCP 工具：

- `conversations_list`
- `conversation_get`
- `messages_read`
- `attachments_fetch`
- `events_poll`
- `events_wait`
- `messages_send`
- `permissions_list_open`
- `permissions_respond`

### `conversations_list`

列出 Gateway 会话状态中已有路由元数据的最近基于会话的对话。

有用的过滤器：

- `limit`
- `search`
- `channel`
- `includeDerivedTitles`
- `includeLastMessage`

### `conversation_get`

通过 `session_key` 返回一个对话。

### `messages_read`

读取一个基于会话的对话的最近转录消息。

### `attachments_fetch`

从一个转录消息中提取非文本消息内容块。这是对转录内容的元数据视图，而不是独立的持久附件 blob 存储。

### `events_poll`

读取自数字游标以来的排队实时事件。

### `events_wait`

长轮询直到下一个匹配的排队事件到达或超时到期。

当通用 MCP 客户端需要近实时传递而不使用特定于 Claude 的推送协议时，请使用此方法。

### `messages_send`

通过会话中已记录的相同路由发送文本。

当前行为：

- 需要现有的对话路由
- 使用会话的频道、收件人、账户 id 和线程 id
- 仅发送文本

### `permissions_list_open`

列出桥接器自连接到 Gateway 以来观察到的待处理执行/插件批准请求。

### `permissions_respond`

解决一个待处理的执行/插件批准请求，使用：

- `allow-once`
- `allow-always`
- `deny`

## 事件模型

桥接器在连接期间维护内存中的事件队列。

当前事件类型：

- `message`
- `exec_approval_requested`
- `exec_approval_resolved`
- `plugin_approval_requested`
- `plugin_approval_resolved`
- `claude_permission_request`

重要限制：

- 队列仅限实时；它在 MCP 桥接器启动时开始
- `events_poll` 和 `events_wait` 不会自行重放较旧的 Gateway 历史
- 持久积压应使用 `messages_read` 读取

## Claude 频道通知

桥接器还可以暴露特定于 Claude 的频道通知。这是 OpenClaw 对 Claude Code 频道适配器的等效实现：标准 MCP 工具仍然可用，但实时入站消息也可以作为特定于 Claude 的 MCP 通知到达。

标志：

- `--claude-channel-mode off`：仅标准 MCP 工具
- `--claude-channel-mode on`：启用 Claude 频道通知
- `--claude-channel-mode auto`：当前默认值；与 `on` 相同的桥接器行为

当启用 Claude 频道模式时，服务器会通告 Claude 实验性功能并发出：

- `notifications/claude/channel`
- `notifications/claude/channel/permission`

当前桥接器行为：

- 入站 `user` 转录消息被转发为 `notifications/claude/channel`
- 通过 MCP 接收的 Claude 权限请求在内存中跟踪
- 如果链接的对话随后发送 `yes abcde` 或 `no abcde`，桥接器将其转换为 `notifications/claude/channel/permission`
- 这些通知仅限实时会话；如果 MCP 客户端断开连接，则没有推送目标

这是有意针对特定客户端的。通用 MCP 客户端应依赖标准轮询工具。

## MCP 客户端配置

示例 stdio 客户端配置：

```json
{
  "mcpServers": {
    "openclaw": {
      "command": "openclaw",
      "args": [
        "mcp",
        "serve",
        "--url",
        "wss://gateway-host:18789",
        "--token-file",
        "/path/to/gateway.token"
      ]
    }
  }
}
```

对于大多数通用 MCP 客户端，从标准工具表面开始并忽略 Claude 模式。仅对真正理解特定于 Claude 的通知方法的客户端开启 Claude 模式。

## 选项

`openclaw mcp serve` 支持：

- `--url <url>`：Gateway WebSocket URL
- `--token <token>`：Gateway token
- `--token-file <path>`：从文件读取 token
- `--password <password>`：Gateway password
- `--password-file <path>`：从文件读取 password
- `--claude-channel-mode <auto|on|off>`：Claude 通知模式
- `-v`, `--verbose`：在 stderr 上输出详细日志

尽可能优先使用 `--token-file` 或 `--password-file` 代替内联密钥。

## 安全性和信任边界

桥接器不发明路由。它仅暴露 Gateway 已经知道如何路由的对话。

这意味着：

- 发件人白名单、配对和频道级信任仍属于底层 OpenClaw 频道配置
- `messages_send` 只能通过现有存储的路由回复
- 批准状态仅对当前桥接器会话为实时/内存中
- 桥接器身份验证应使用与您信任任何其他远程 Gateway 客户端相同的 Gateway token 或密码控制

如果 `conversations_list` 中缺少对话，通常原因不是 MCP 配置。而是底层 Gateway 会话中缺少或不完整的路由元数据。

## 测试

OpenClaw 为此桥接器提供了确定性 Docker 冒烟测试：

```bash
pnpm test:docker:mcp-channels
```

该冒烟测试：

- 启动种子 Gateway 容器
- 启动第二个容器以生成 `openclaw mcp serve`
- 验证对话发现、转录读取、附件元数据读取、实时事件队列行为和出站发送路由
- 验证真实 stdio MCP 桥接器上的类 Claude 频道和权限通知

这是在测试运行中无需连接真实的 Telegram、Discord 或 iMessage 账户来证明桥接器工作的最快方法。

有关更广泛的测试上下文，请参阅 [Testing](/help/testing)。

## 故障排除

### 未返回对话

通常意味着 Gateway 会话尚不可路由。确认底层会话已存储频道/提供者、收件人和可选的账户/线程路由元数据。

### `events_poll` 或 `events_wait` 遗漏了旧消息

预期如此。实时队列在桥接器连接时开始。使用 `messages_read` 读取较旧的转录历史。

### Claude 通知未显示

检查所有以下内容：

- 客户端保持了 stdio MCP 会话打开
- `--claude-channel-mode` 是 `on` 或 `auto`
- 客户端确实理解特定于 Claude 的通知方法
- 入站消息发生在桥接器连接之后

### 批准缺失

`permissions_list_open` 仅显示桥接器连接期间观察到的批准请求。它不是一个持久的批准历史 API。

## OpenClaw 作为 MCP 客户端注册表

这是 `openclaw mcp list`、`show`、`set` 和 `unset` 路径。

这些命令不会通过 MCP 暴露 OpenClaw。它们管理 OpenClaw 配置的 `mcp.servers` 下的 OpenClaw 拥有的 MCP 服务器定义。

这些保存的定义用于 OpenClaw 稍后启动或配置的运行环境，例如嵌入式 Pi 和其他运行时适配器。OpenClaw 集中存储这些定义，以便这些运行环境无需维护各自重复的 MCP 服务器列表。

重要行为：

- 这些命令仅读取或写入 OpenClaw 配置
- 它们不连接到目标 MCP 服务器
- 它们不验证命令、URL 或远程传输当前是否可达
- 运行时适配器在执行时决定它们实际支持的传输类型

## 已保存的 MCP 服务器定义

OpenClaw 还在配置中存储了一个轻量级 MCP 服务器注册表，供需要 OpenClaw 管理的 MCP 定义的界面使用。

命令：

- `openclaw mcp list`
- `openclaw mcp show [name]`
- `openclaw mcp set <name> <json>`
- `openclaw mcp unset <name>`

注意：

- `list` 对服务器名称进行排序。
- `show` 不带名称时打印完整的配置 MCP 服务器对象。
- `set` 期望命令行上有一个 JSON 对象值。
- 如果命名的服务器不存在，`unset` 将失败。

示例：

```bash
openclaw mcp list
openclaw mcp show context7 --json
openclaw mcp set context7 '{"command":"uvx","args":["context7-mcp"]}'
openclaw mcp set docs '{"url":"https://mcp.example.com"}'
openclaw mcp unset context7
```

示例配置结构：

```json
{
  "mcp": {
    "servers": {
      "context7": {
        "command": "uvx",
        "args": ["context7-mcp"]
      },
      "docs": {
        "url": "https://mcp.example.com"
      }
    }
  }
}
```

### Stdio 传输

启动本地子进程并通过 stdin/stdout 进行通信。

| Field                      | Description                       |
| -------------------------- | --------------------------------- |
| `command`                  | 要启动的可执行程序（必需）    |
| `args`                     | 命令行参数数组   |
| `env`                      | 额外的环境变量       |
| `cwd` / `workingDirectory` | 进程的工作目录 |

### SSE / HTTP 传输

通过 HTTP Server-Sent Events 连接到远程 MCP 服务器。

| Field                 | Description                                                      |
| --------------------- | ---------------------------------------------------------------- |
| `url`                 | 远程服务器的 HTTP 或 HTTPS URL（必需）                |
| `headers`             | 可选的 HTTP 头键值映射（例如认证令牌） |
| `connectionTimeoutMs` | 每个服务器的连接超时时间（毫秒）（可选）                   |

示例：

```json
{
  "mcp": {
    "servers": {
      "remote-tools": {
        "url": "https://mcp.example.com",
        "headers": {
          "Authorization": "Bearer <token>"
        }
      }
    }
  }
}
```

`url`（userinfo）和 `headers` 中的敏感值在日志和状态输出中会被脱敏。

### Streamable HTTP 传输

`streamable-http` 是 `sse` 和 `stdio` 之外的额外传输选项。它使用 HTTP 流式传输与远程 MCP 服务器进行双向通信。

| Field                 | Description                                                                            |
| --------------------- | -------------------------------------------------------------------------------------- |
| `url`                 | 远程服务器的 HTTP 或 HTTPS URL（必需）                                      |
| `transport`           | 设置为 `"streamable-http"` 以选择此传输；省略时，OpenClaw 使用 `sse` |
| `headers`             | 可选的 HTTP 头键值映射（例如认证令牌）                       |
| `connectionTimeoutMs` | 每个服务器的连接超时时间（毫秒）（可选）                                         |

示例：

```json
{
  "mcp": {
    "servers": {
      "streaming-tools": {
        "url": "https://mcp.example.com/stream",
        "transport": "streamable-http",
        "connectionTimeoutMs": 10000,
        "headers": {
          "Authorization": "Bearer <token>"
        }
      }
    }
  }
}
```

这些命令仅管理保存的配置。它们不启动通道桥接器，不开启实时 MCP 客户端会话，也不证明目标服务器可达。

## 当前限制

本文档记录了今日发布的桥接器功能。

当前限制：

- 对话发现依赖于现有的 Gateway 会话路由元数据
- 除了 Claude 特定适配器外，没有通用的推送协议
- 目前尚无消息编辑或反应工具
- HTTP/SSE/streamable-http 传输连接到单个远程服务器；尚未支持上游多路复用
- `permissions_list_open` 仅包含桥接器连接期间观察到的批准