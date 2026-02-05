---
summary: "iMessage support via imsg (JSON-RPC over stdio), setup, and chat_id routing"
read_when:
  - Setting up iMessage support
  - Debugging iMessage send/receive
title: iMessage
---
# iMessage (imsg)

状态: 外部CLI集成。网关生成 `imsg rpc` (通过stdio的JSON-RPC)。

## 快速设置 (初学者)

1. 确保此Mac上的消息已登录。
2. 安装 `imsg`:
   - `brew install steipete/tap/imsg`
3. 使用 `channels.imessage.cliPath` 和 `channels.imessage.dbPath` 配置OpenClaw。
4. 启动网关并批准任何macOS提示（自动化 + 完整磁盘访问）。

最小配置:

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "/usr/local/bin/imsg",
      dbPath: "/Users/<you>/Library/Messages/chat.db",
    },
  },
}
```

## 什么是它

- 基于macOS上的 `imsg` 的iMessage通道。
- 确定性路由：回复总是回到iMessage。
- 直接消息共享代理的主要会话；群组是隔离的 (`agent:<agentId>:imessage:group:<chat_id>`)。
- 如果带有 `is_group=false` 到达一个多参与者线程，您可以通过 `chat_id` 使用 `channels.imessage.groups` 将其隔离（见下方“类似群组的线程”）。

## 配置写入

默认情况下，允许iMessage写入由 `/config set|unset` 触发的配置更新（需要 `commands.config: true`）。

禁用方法:

```json5
{
  channels: { imessage: { configWrites: false } },
}
```

## 要求

- 已登录消息的macOS。
- OpenClaw + `imsg` 的完整磁盘访问权限（消息数据库访问）。
- 发送时的自动化权限。
- `channels.imessage.cliPath` 可以指向任何代理stdin/stdout的命令（例如，一个通过SSH连接到另一台Mac并运行 `imsg rpc` 的包装脚本）。

## 设置 (快速路径)

1. 确保此Mac上的消息已登录。
2. 配置iMessage并启动网关。

### 专用机器人macOS用户（用于隔离身份）

如果您希望机器人从一个 **单独的iMessage身份** 发送消息（并保持您的个人消息整洁），请使用专用的Apple ID + 专用的macOS用户。

1. 创建一个专用的Apple ID（示例：`my-cool-bot@icloud.com`）。
   - Apple可能需要电话号码进行验证/双重认证。
2. 创建一个macOS用户（示例：`openclawhome`）并登录。
3. 在该macOS用户中打开消息，并使用机器人Apple ID登录iMessage。
4. 启用远程登录（系统设置 → 常规 → 共享 → 远程登录）。
5. 安装 `imsg`:
   - `brew install steipete/tap/imsg`
6. 设置SSH以便 `ssh <bot-macos-user>@localhost true` 可以在无需密码的情况下工作。
7. 将 `channels.imessage.accounts.bot.cliPath` 指向一个运行 `imsg` 的SSH包装器作为机器人用户。

首次运行注意事项：发送/接收可能需要在 _机器人macOS用户_ 中批准GUI提示（自动化 + 完整磁盘访问）。如果 `imsg rpc` 似乎卡住或退出，请登录该用户（屏幕共享有帮助），运行一次 `imsg chats --limit 1` / `imsg send ...`，批准提示，然后重试。

示例包装器 (`chmod +x`)。将 `<bot-macos-user>` 替换为您的实际macOS用户名：

```bash
#!/usr/bin/env bash
set -euo pipefail

# Run an interactive SSH once first to accept host keys:
#   ssh <bot-macos-user>@localhost true
exec /usr/bin/ssh -o BatchMode=yes -o ConnectTimeout=5 -T <bot-macos-user>@localhost \
  "/usr/local/bin/imsg" "$@"
```

示例配置:

```json5
{
  channels: {
    imessage: {
      enabled: true,
      accounts: {
        bot: {
          name: "Bot",
          enabled: true,
          cliPath: "/path/to/imsg-bot",
          dbPath: "/Users/<bot-macos-user>/Library/Messages/chat.db",
        },
      },
    },
  },
}
```

对于单账户设置，使用平面选项 (`channels.imessage.cliPath`, `channels.imessage.dbPath`) 而不是 `accounts` 映射。

### 远程/SSH变体（可选）

如果您想在另一台Mac上使用iMessage，请将 `channels.imessage.cliPath` 设置为一个包装器，该包装器通过SSH在远程macOS主机上运行 `imsg`。OpenClaw只需要stdio。

示例包装器:

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

**远程附件:** 当 `cliPath` 通过SSH指向远程主机时，消息数据库中的附件路径引用远程机器上的文件。通过设置 `channels.imessage.remoteHost`，OpenClaw可以自动通过SCP获取这些文件：

```json5
{
  channels: {
    imessage: {
      cliPath: "~/imsg-ssh", // SSH wrapper to remote Mac
      remoteHost: "user@gateway-host", // for SCP file transfer
      includeAttachments: true,
    },
  },
}
```

如果未设置 `remoteHost`，OpenClaw会尝试通过解析包装器脚本中的SSH命令来自动检测它。建议显式配置以确保可靠性。

#### 通过Tailscale的远程Mac（示例）

如果网关在Linux主机/VM上运行但iMessage必须在Mac上运行，Tailscale是最简单的桥接方式：网关通过tailnet与Mac通信，通过SSH运行 `imsg`，并通过SCP传输附件。

架构:

```
┌──────────────────────────────┐          SSH (imsg rpc)          ┌──────────────────────────┐
│ Gateway host (Linux/VM)      │──────────────────────────────────▶│ Mac with Messages + imsg │
│ - openclaw gateway           │          SCP (attachments)        │ - Messages signed in     │
│ - channels.imessage.cliPath  │◀──────────────────────────────────│ - Remote Login enabled   │
└──────────────────────────────┘                                   └──────────────────────────┘
              ▲
              │ Tailscale tailnet (hostname or 100.x.y.z)
              ▼
        user@gateway-host
```

具体配置示例（Tailscale主机名）:

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "~/.openclaw/scripts/imsg-ssh",
      remoteHost: "bot@mac-mini.tailnet-1234.ts.net",
      includeAttachments: true,
      dbPath: "/Users/bot/Library/Messages/chat.db",
    },
  },
}
```

示例包装器 (`~/.openclaw/scripts/imsg-ssh`)：

```bash
#!/usr/bin/env bash
exec ssh -T bot@mac-mini.tailnet-1234.ts.net imsg "$@"
```

注意:

- 确保Mac已登录消息，并且启用了远程登录。
- 使用SSH密钥以便 `ssh bot@mac-mini.tailnet-1234.ts.net` 可以在无需提示的情况下工作。
- `remoteHost` 应与SSH目标匹配，以便SCP可以获取附件。

多账户支持：使用 `channels.imessage.accounts` 和每个账户的配置以及可选的 `name`。参见[`gateway/configuration`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 获取共享模式。不要提交 `~/.openclaw/openclaw.json`（它通常包含令牌）。

## 访问控制（直接消息 + 群组）

直接消息:

- 默认: `channels.imessage.dmPolicy = "pairing"`。
- 未知发送者会收到配对码；消息会被忽略直到批准（码在1小时后过期）。
- 通过以下方式批准:
  - `openclaw pairing list imessage`
  - `openclaw pairing approve imessage <CODE>`
- 配对是iMessage直接消息的默认令牌交换方式。详情: [配对](/start/pairing)

群组:

- `channels.imessage.groupPolicy = open | allowlist | disabled`。
- 当设置了 `allowlist` 时，`channels.imessage.groupAllowFrom` 控制谁可以在群组中触发。
- 提及门控使用 `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`），因为iMessage没有原生提及元数据。
- 多代理覆盖：在 `agents.list[].groupChat.mentionPatterns` 上设置每个代理模式。

## 工作原理（行为）

- `imsg` 流式传输消息事件；网关将它们规范化为共享通道信封。
- 回复总是路由回相同的聊天ID或句柄。

## 类似群组的线程 (`is_group=false`)

一些iMessage线程可以有多个参与者，但仍会根据Messages存储聊天标识符的方式带有 `is_group=false`。

如果您在 `channels.imessage.groups` 下明确配置了 `chat_id`，OpenClaw会将该线程视为“群组”以实现：

- 会话隔离（单独的 `agent:<agentId>:imessage:group:<chat_id>` 会话密钥）
- 群组白名单/提及门控行为

示例:

```json5
{
  channels: {
    imessage: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15555550123"],
      groups: {
        "42": { requireMention: false },
      },
    },
  },
}
```

当您希望特定线程有一个隔离的身份/模型时这很有用（参见[多代理路由](/concepts/multi-agent)）。有关文件系统隔离，请参见[沙盒化](/gateway/sandboxing)。

## 媒体 + 限制

- 可选的附件摄取通过 `channels.imessage.includeAttachments`。
- 媒体限制通过 `channels.imessage.mediaMaxMb`。

## 限制

- 出站文本被分块为 `channels.imessage.textChunkLimit`（默认4000）。
- 可选的新行分块：设置 `channels.imessage.chunkMode="newline"` 以在长度分块之前按空白行（段落边界）拆分。
- 媒体上传限制为 `channels.imessage.mediaMaxMb`（默认16）。

## 地址 / 交付目标

优先使用 `chat_id` 进行稳定路由：

- `chat_id:123`（首选）
- `chat_guid:...`
- `chat_identifier:...`
- 直接句柄: `imessage:+1555` / `sms:+1555` / `user@example.com`

列出聊天:

```
imsg chats --limit 20
```

## 配置参考 (iMessage)

完整配置: [配置](/gateway/configuration)

提供商选项:

- `channels.imessage.enabled`: 启用/禁用通道启动。
- `channels.imessage.cliPath`: `imsg` 的路径。
- `channels.imessage.dbPath`: 消息数据库路径。
- `channels.imessage.remoteHost`: 当 `cliPath` 指向远程Mac时用于SCP附件传输的SSH主机（例如，`user@gateway-host`）。如果未设置，则从SSH包装器自动检测。
- `channels.imessage.service`: `imessage | sms | auto`。
- `channels.imessage.region`: SMS区域。
- `channels.imessage.dmPolicy`: `pairing | allowlist | open | disabled`（默认：配对）。
- `channels.imessage.allowFrom`: 直接消息白名单（句柄、电子邮件、E.164号码或 `chat_id:*`）。`open` 需要 `"*"`。iMessage没有用户名；使用句柄或聊天目标。
- `channels.imessage.groupPolicy`: `open | allowlist | disabled`（默认：白名单）。
- `channels.imessage.groupAllowFrom`: 群组发送者白名单。
- `channels.imessage.historyLimit` / `channels.imessage.accounts.*.historyLimit`: 作为上下文包含的最大群组消息数（0禁用）。
- `channels.imessage.dmHistoryLimit`: 用户轮次的直接消息历史记录限制。每个用户的覆盖：`channels.imessage.dms["<handle>"].historyLimit`。
- `channels.imessage.groups`: 每个群组的默认值 + 白名单（使用 `"*"` 进行全局默认设置）。
- `channels.imessage.includeAttachments`: 将附件摄取到上下文中。
- `channels.imessage.mediaMaxMb`: 入站/出站媒体限制（MB）。
- `channels.imessage.textChunkLimit`: 出站分块大小（字符）。
- `channels.imessage.chunkMode`: `length`（默认）或 `newline` 以在长度分块之前按空白行（段落边界）拆分。

相关全局选项:

- `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）。
- `messages.responsePrefix`。