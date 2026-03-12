---
title: IRC
description: Connect OpenClaw to IRC channels and direct messages.
summary: "IRC plugin setup, access controls, and troubleshooting"
read_when:
  - You want to connect OpenClaw to IRC channels or DMs
  - You are configuring IRC allowlists, group policy, or mention gating
---
当您希望 OpenClaw 在经典 IRC 频道（`#room`）及私信中运行时，请使用 IRC 协议。  
IRC 以扩展插件形式提供，但在主配置文件中通过 `channels.irc` 进行配置。

## 快速开始

1. 在 `~/.openclaw/openclaw.json` 中启用 IRC 配置。  
2. 至少设置以下项：

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

3. 启动或重启网关：

```bash
openclaw gateway run
```

## 安全默认值

- `channels.irc.dmPolicy` 默认为 `"pairing"`。  
- `channels.irc.groupPolicy` 默认为 `"allowlist"`。  
- 若启用 `groupPolicy="allowlist"`，请设置 `channels.irc.groups` 以定义允许加入的频道。  
- 除非您明确接受明文传输，否则请务必启用 TLS（`channels.irc.tls=true`）。

## 访问控制

IRC 频道存在两个独立的“访问门控”机制：

1. **频道访问控制**（`groupPolicy` + `groups`）：决定机器人是否接收来自某频道的任何消息。  
2. **发送者访问控制**（`groupAllowFrom` / 每频道 `groups["#channel"].allowFrom`）：决定谁可以在该频道内触发机器人响应。

配置项说明：

- 私信发送者白名单（DM 发送者访问控制）：`channels.irc.allowFrom`  
- 群组发送者白名单（频道发送者访问控制）：`channels.irc.groupAllowFrom`  
- 每频道细粒度控制（频道 + 发送者 + @提及规则）：`channels.irc.groups["#channel"]`  
- `channels.irc.groupPolicy="open"` 允许未显式配置的频道（**但仍默认受 @提及门控限制**）

白名单条目应使用稳定的发送者身份标识（`nick!user@host`）。  
仅凭昵称（nick）匹配是可变的，仅在启用 `channels.irc.dangerouslyAllowNameMatching: true` 时生效。

### 常见误区：`allowFrom` 适用于私信（DM），而非频道

若您看到如下日志：

- `irc: drop group sender alice!ident@host (policy=allowlist)`

…这表示该发送者**未被允许向群组/频道发送消息**。请通过以下任一方式修复：

- 设置 `channels.irc.groupAllowFrom`（对所有频道全局生效），或  
- 设置每频道发送者白名单：`channels.irc.groups["#channel"].allowFrom`

示例（允许 `#tuirc-dev` 中的任何人与机器人交互）：

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

## 回复触发机制（@提及）

即使频道已被允许（通过 `groupPolicy` + `groups`），且发送者也被允许，OpenClaw 在群组上下文中仍默认启用 **@提及门控（mention-gating）**。

这意味着，除非消息中包含匹配机器人的 @提及模式，否则您可能会看到类似 `drop channel … (missing-mention)` 的日志。

若希望机器人在 IRC 频道中**无需 @提及即可自动回复**，请为该频道禁用 @提及门控：

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

或者，若希望**所有 IRC 频道均无需 @提及即可回复**（即不启用每频道白名单）：

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

## 安全提示（推荐用于公开频道）

若您允许 `allowFrom: ["*"]` 在公开频道中运行，则任何人都可向机器人发起指令。  
为降低风险，请对该频道限制可用工具集。

### 频道内所有用户使用相同工具集

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

### 不同发送者使用不同工具集（例如所有者拥有更高权限）

使用 `toolsBySender` 对 `"*"` 应用更严格的策略，同时对您的昵称应用更宽松的策略：

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

注意事项：

- `toolsBySender` 配置项中的键值应使用 `id:` 表示 IRC 发送者身份：  
  `id:eigen` 或 `id:eigen!~eigen@174.127.248.171` 可实现更强的身份匹配。  
- 已废弃的无前缀键仍被支持，但仅按 `id:` 方式匹配。  
- 匹配顺序遵循“首个匹配优先”原则；`"*"` 是通配符兜底策略。

有关群组访问控制与 @提及门控机制（及其相互作用）的更多说明，请参阅：[/channels/groups](/channels/groups)。

## NickServ

连接后通过 NickServ 进行身份认证：

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

连接时可选一次性注册：

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

昵称注册成功后，请禁用 `register`，以避免重复执行 REGISTER 操作。

## 环境变量

默认账户支持以下环境变量：

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

## 故障排查

- 若机器人成功连接但始终不在频道中回复，请确认 `channels.irc.groups` 是否已正确配置，**并检查** @提及门控是否导致消息被丢弃（`missing-mention`）。如需免 @提及回复，请为对应频道设置 `requireMention:false`。  
- 若登录失败，请验证昵称是否可用以及服务器密码是否正确。  
- 若在自定义网络中 TLS 连接失败，请检查主机名/端口及证书配置是否正确。