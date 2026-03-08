---
title: IRC
description: Connect OpenClaw to IRC channels and direct messages.
summary: "IRC plugin setup, access controls, and troubleshooting"
read_when:
  - You want to connect OpenClaw to IRC channels or DMs
  - You are configuring IRC allowlists, group policy, or mention gating
---
当您希望 OpenClaw 在经典频道 (`#room`) 和直接消息中使用 IRC 时。
IRC 作为扩展插件提供，但在主配置下的 `channels.irc` 中进行配置。

## 快速开始

1. 在 `~/.openclaw/openclaw.json` 中启用 IRC 配置。
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

## 安全默认值

- `channels.irc.dmPolicy` 默认为 `"pairing"`。
- `channels.irc.groupPolicy` 默认为 `"allowlist"`。
- 使用 `groupPolicy="allowlist"` 时，设置 `channels.irc.groups` 以定义允许的频道。
- 除非您有意接受明文传输，否则请使用 TLS (`channels.irc.tls=true`)。

## 访问控制

IRC 频道有两个独立的“门禁”：

1. **频道访问** (`groupPolicy` + `groups`)：机器人是否完全接受来自该频道的消息。
2. **发送者访问** (`groupAllowFrom` / 每频道 `groups["#channel"].allowFrom`)：谁被允许在该频道内触发机器人。

配置键：

- DM 白名单（DM 发送者访问）：`channels.irc.allowFrom`
- 群组发送者白名单（频道发送者访问）：`channels.irc.groupAllowFrom`
- 每频道控制（频道 + 发送者 + 提及规则）：`channels.irc.groups["#channel"]`
- `channels.irc.groupPolicy="open"` 允许未配置的频道（**默认仍受提及门禁限制**）

白名单条目应使用稳定的发送者身份 (`nick!user@host`)。
纯昵称匹配是可变的，仅在 `channels.irc.dangerouslyAllowNameMatching: true` 时启用。

### 常见陷阱：`allowFrom` 用于 DM，而非频道

如果您看到如下日志：

- `irc: drop group sender alice!ident@host (policy=allowlist)`

…这意味着发送者未被允许用于**群组/频道**消息。修复方法如下：

- 设置 `channels.irc.groupAllowFrom`（适用于所有频道的全局设置），或者
- 设置每频道发送者白名单：`channels.irc.groups["#channel"].allowFrom`

示例（允许 `#tuirc-dev` 中的任何人向机器人发言）：

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

即使频道已允许（通过 `groupPolicy` + `groups`）且发送者已允许，OpenClaw 在群组上下文中默认采用**提及门禁**。

这意味着除非消息包含与机器人匹配的提及模式，否则您可能会看到类似 `drop channel … (missing-mention)` 的日志。

若要使机器人在 IRC 频道中回复而**无需提及**，请禁用该频道的提及门禁：

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

或者要允许**所有**IRC 频道（无需每频道白名单）但仍无需提及即可回复：

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

## 安全说明（推荐用于公共频道）

如果您在公共频道中允许 `allowFrom: ["*"]`，任何人都可以向机器人发出提示。
为了降低风险，请限制该频道的工具。

### 频道内所有人使用相同工具

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

### 不同发送者使用不同工具（所有者获得更多权限）

使用 `toolsBySender` 对 `"*"` 应用更严格的策略，对您自己的昵称应用较宽松的策略：

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
            "id:eigen": {
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

- `toolsBySender` 键应为 IRC 发送者身份值使用 `id:`：
  `id:eigen` 或 `id:eigen!~eigen@174.127.248.171` 以实现更强的匹配。
- 旧的无前缀键仍被接受，并仅匹配为 `id:`。
- 第一个匹配的发送者策略生效；`"*"` 是通配符回退。

有关群组访问与提及门禁（以及它们如何交互）的更多信息，请参阅：[/channels/groups](/channels/groups)。

## NickServ

连接后向 NickServ 进行身份验证：

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

可选的连接时一次性注册：

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

昵称注册后禁用 `register` 以避免重复的 REGISTER 尝试。

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

- 如果机器人连接但从未在频道中回复，请验证 `channels.irc.groups` **和** 提及门禁是否丢弃了消息 (`missing-mention`)。如果您希望它无需 ping 即可回复，请为频道设置 `requireMention:false`。
- 如果登录失败，请验证昵称可用性和服务器密码。
- 如果在自定义网络上 TLS 失败，请验证主机/端口和证书设置。