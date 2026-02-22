---
title: IRC
description: Connect OpenClaw to IRC channels and direct messages.
---
在需要在经典频道 (`#room`) 和直接消息中使用OpenClaw时，请使用IRC。
IRC作为扩展插件提供，但在主配置文件下的`channels.irc`进行配置。

## 快速开始

1. 在`~/.openclaw/openclaw.json`中启用IRC配置。
2. 至少设置：

```json
{
  "channels": {
    "irc": {
      "enabled": true,
      "host": "irc.libera.chat",
      "port": 6697,
      "tls": true,
      "nick": "openclaw-bot",
      "channels": ["#openclaw"]
    }
  }
}
```

3. 启动/重启网关：

```bash
openclaw gateway run
```

## 安全默认设置

- `channels.irc.dmPolicy` 默认为 `"pairing"`。
- `channels.irc.groupPolicy` 默认为 `"allowlist"`。
- 使用 `groupPolicy="allowlist"` 时，设置 `channels.irc.groups` 以定义允许的频道。
- 除非有意接受明文传输，否则使用TLS (`channels.irc.tls=true`)。

## 访问控制

IRC频道有两个独立的“门”：

1. **频道访问** (`groupPolicy` + `groups`)：机器人是否接受来自该频道的消息。
2. **发送者访问** (`groupAllowFrom` / 每频道 `groups["#channel"].allowFrom`)：谁有权在该频道触发机器人。

配置键：

- 直接消息白名单（DM发送者访问）：`channels.irc.allowFrom`
- 群组发送者白名单（频道发送者访问）：`channels.irc.groupAllowFrom`
- 每频道控制（频道 + 发送者 + 提及规则）：`channels.irc.groups["#channel"]`
- `channels.irc.groupPolicy="open"` 允许未配置的频道 (**默认仍然提及受控**）

白名单条目可以使用昵称或 `nick!user@host` 形式。

### 常见问题：`allowFrom` 是用于直接消息，而不是频道

如果你看到日志如下：

- `irc: drop group sender alice!ident@host (policy=allowlist)`

…这意味着发送者没有被允许用于 **群组/频道** 消息。通过以下方式修复：

- 设置 `channels.irc.groupAllowFrom`（对所有频道全局），或
- 设置每频道发送者白名单：`channels.irc.groups["#channel"].allowFrom`

示例（允许 `#tuirc-dev` 中的任何人与机器人对话）：

```json5
{
  channels: {
    irc: {
      groupPolicy: "allowlist",
      groups: {
        "#tuirc-dev": { allowFrom: ["*"] },
      },
    },
  },
}
```

## 回复触发（提及）

即使一个频道被允许（通过 `groupPolicy` + `groups`）且发送者被允许，OpenClaw默认在群组上下文中使用 **提及受控**。

这意味着你可能会看到日志如 `drop channel … (missing-mention)`，除非消息包含匹配机器人的提及模式。

要使机器人在IRC频道中回复 **无需提及**，禁用该频道的提及受控：

```json5
{
  channels: {
    irc: {
      groupPolicy: "allowlist",
      groups: {
        "#tuirc-dev": {
          requireMention: false,
          allowFrom: ["*"],
        },
      },
    },
  },
}
```

或者允许 **所有** IRC频道（无每频道白名单）并仍然无需提及回复：

```json5
{
  channels: {
    irc: {
      groupPolicy: "open",
      groups: {
        "*": { requireMention: false, allowFrom: ["*"] },
      },
    },
  },
}
```

## 安全注意事项（推荐用于公共频道）

如果你允许 `allowFrom: ["*"]` 在公共频道中，任何人都可以提示机器人。
为了降低风险，请限制该频道的工具。

### 频道中每个人相同的工具

```json5
{
  channels: {
    irc: {
      groups: {
        "#tuirc-dev": {
          allowFrom: ["*"],
          tools: {
            deny: ["group:runtime", "group:fs", "gateway", "nodes", "cron", "browser"],
          },
        },
      },
    },
  },
}
```

### 每发送者不同的工具（所有者获得更多权限）

使用 `toolsBySender` 对 `"*"` 应用更严格的策略，并对你自己的昵称应用宽松的策略：

```json5
{
  channels: {
    irc: {
      groups: {
        "#tuirc-dev": {
          allowFrom: ["*"],
          toolsBySender: {
            "*": {
              deny: ["group:runtime", "group:fs", "gateway", "nodes", "cron", "browser"],
            },
            eigen: {
              deny: ["gateway", "nodes", "cron"],
            },
          },
        },
      },
    },
  },
}
```

注意：

- `toolsBySender` 键可以是昵称（例如 `"eigen"`）或完整的主机掩码 (`"eigen!~eigen@174.127.248.171"`) 以实现更强的身份匹配。
- 第一个匹配的发送者策略生效；`"*"` 是通配符回退。

有关组访问与提及受控（以及它们如何交互）的更多信息，请参阅：[/channels/groups](/channels/groups)。

## NickServ

连接后使用NickServ认证：

```json
{
  "channels": {
    "irc": {
      "nickserv": {
        "enabled": true,
        "service": "NickServ",
        "password": "your-nickserv-password"
      }
    }
  }
}
```

可选的一次性注册连接：

```json
{
  "channels": {
    "irc": {
      "nickserv": {
        "register": true,
        "registerEmail": "bot@example.com"
      }
    }
  }
}
```

在昵称注册后禁用 `register` 以避免重复的REGISTER尝试。

## 环境变量

默认账户支持：

- `IRC_HOST`
- `IRC_PORT`
- `IRC_TLS`
- `IRC_NICK`
- `IRC_USERNAME`
- `IRC_REALNAME`
- `IRC_PASSWORD`
- `IRC_CHANNELS`（逗号分隔）
- `IRC_NICKSERV_PASSWORD`
- `IRC_NICKSERV_REGISTER_EMAIL`

## 故障排除

- 如果机器人连接但从未在频道中回复，请验证 `channels.irc.groups` **以及** 提及受控是否丢弃了消息 (`missing-mention`)。如果你想让它无需ping就回复，请为该频道设置 `requireMention:false`。
- 如果登录失败，请验证昵称可用性和服务器密码。
- 如果自定义网络上的TLS失败，请验证主机/端口和证书设置。