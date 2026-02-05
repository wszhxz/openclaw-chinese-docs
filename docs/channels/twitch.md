---
summary: "Twitch chat bot configuration and setup"
read_when:
  - Setting up Twitch chat integration for OpenClaw
title: "Twitch"
---
# Twitch (插件)

通过IRC连接支持Twitch聊天。OpenClaw以Twitch用户（机器人账户）身份连接，接收和发送频道中的消息。

## 需要插件

Twitch作为插件提供，不包含在核心安装中。

通过CLI安装（npm仓库）：

```bash
openclaw plugins install @openclaw/twitch
```

本地检出（从git仓库运行时）：

```bash
openclaw plugins install ./extensions/twitch
```

详情：[Plugins](/plugin)

## 快速设置（初学者）

1. 为机器人创建一个专用的Twitch账户（或使用现有账户）。
2. 生成凭据：[Twitch Token Generator](https://twitchtokengenerator.com/)
   - 选择 **Bot Token**
   - 确认选择了范围 `chat:read` 和 `chat:write`
   - 复制 **Client ID** 和 **Access Token**
3. 查找您的Twitch用户ID：https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/
4. 配置令牌：
   - 环境变量: `OPENCLAW_TWITCH_ACCESS_TOKEN=...`（仅默认账户）
   - 或配置: `channels.twitch.accessToken`
   - 如果两者都设置，配置优先（环境变量回退仅限默认账户）。
5. 启动网关。

**⚠️ 注意：** 添加访问控制 (`allowFrom` 或 `allowedRoles`) 以防止未经授权的用户触发机器人。`requireMention` 默认为 `true`。

最小配置：

```json5
{
  channels: {
    twitch: {
      enabled: true,
      username: "openclaw", // Bot's Twitch account
      accessToken: "oauth:abc123...", // OAuth Access Token (or use OPENCLAW_TWITCH_ACCESS_TOKEN env var)
      clientId: "xyz789...", // Client ID from Token Generator
      channel: "vevisk", // Which Twitch channel's chat to join (required)
      allowFrom: ["123456789"], // (recommended) Your Twitch user ID only - get it from https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/
    },
  },
}
```

## 它是什么

- 由网关拥有的Twitch频道。
- 确定性路由：回复总是返回到Twitch。
- 每个账户映射到一个独立的会话密钥 `agent:<agentId>:twitch:<accountName>`。
- `username` 是机器人的账户（谁进行身份验证），`channel` 是要加入的聊天室。

## 设置（详细）

### 生成凭据

使用 [Twitch Token Generator](https://twitchtokengenerator.com/)：

- 选择 **Bot Token**
- 确认选择了范围 `chat:read` 和 `chat:write`
- 复制 **Client ID** 和 **Access Token**

不需要手动注册应用。令牌在几小时后过期。

### 配置机器人

**环境变量（仅默认账户）：**

```bash
OPENCLAW_TWITCH_ACCESS_TOKEN=oauth:abc123...
```

**或配置：**

```json5
{
  channels: {
    twitch: {
      enabled: true,
      username: "openclaw",
      accessToken: "oauth:abc123...",
      clientId: "xyz789...",
      channel: "vevisk",
    },
  },
}
```

如果同时设置了环境变量和配置，配置优先。

### 访问控制（推荐）

```json5
{
  channels: {
    twitch: {
      allowFrom: ["123456789"], // (recommended) Your Twitch user ID only
    },
  },
}
```

首选 `allowFrom` 用于硬白名单。如果您需要基于角色的访问，请使用 `allowedRoles`。

**可用角色：** `"moderator"`, `"owner"`, `"vip"`, `"subscriber"`, `"all"`。

**为什么使用用户ID？** 用户名可以更改，允许冒充。用户ID是永久的。

查找您的Twitch用户ID：https://www.streamweasels.com/tools/convert-twitch-username-%20to-user-id/ （将您的Twitch用户名转换为ID）

## 令牌刷新（可选）

来自 [Twitch Token Generator](https://twitchtokengenerator.com/) 的令牌无法自动刷新 - 过期时重新生成。

为了自动刷新令牌，在 [Twitch Developer Console](https://dev.twitch.tv/console) 创建自己的Twitch应用程序并添加到配置中：

```json5
{
  channels: {
    twitch: {
      clientSecret: "your_client_secret",
      refreshToken: "your_refresh_token",
    },
  },
}
```

机器人会在过期前自动刷新令牌并记录刷新事件。

## 多账户支持

使用 `channels.twitch.accounts` 和每个账户的令牌。参见 [`gateway/configuration`](/gateway/configuration) 中的共享模式。

示例（一个机器人账户在两个频道）：

```json5
{
  channels: {
    twitch: {
      accounts: {
        channel1: {
          username: "openclaw",
          accessToken: "oauth:abc123...",
          clientId: "xyz789...",
          channel: "vevisk",
        },
        channel2: {
          username: "openclaw",
          accessToken: "oauth:def456...",
          clientId: "uvw012...",
          channel: "secondchannel",
        },
      },
    },
  },
}
```

**注意：** 每个账户需要自己的令牌（每个频道一个令牌）。

## 访问控制

### 基于角色的限制

```json5
{
  channels: {
    twitch: {
      accounts: {
        default: {
          allowedRoles: ["moderator", "vip"],
        },
      },
    },
  },
}
```

### 基于用户ID的白名单（最安全）

```json5
{
  channels: {
    twitch: {
      accounts: {
        default: {
          allowFrom: ["123456789", "987654321"],
        },
      },
    },
  },
}
```

### 基于角色的访问（替代方案）

`allowFrom` 是硬白名单。当设置时，只有这些用户ID被允许。
如果您需要基于角色的访问，请留空 `allowFrom` 并配置 `allowedRoles`：

```json5
{
  channels: {
    twitch: {
      accounts: {
        default: {
          allowedRoles: ["moderator"],
        },
      },
    },
  },
}
```

### 禁用@提及要求

默认情况下，`requireMention` 是 `true`。要禁用并响应所有消息：

```json5
{
  channels: {
    twitch: {
      accounts: {
        default: {
          requireMention: false,
        },
      },
    },
  },
}
```

## 故障排除

首先，运行诊断命令：

```bash
openclaw doctor
openclaw channels status --probe
```

### 机器人不响应消息

**检查访问控制：** 确保您的用户ID在 `allowFrom` 中，或临时移除
`allowFrom` 并设置 `allowedRoles: ["all"]` 进行测试。

**检查机器人是否在频道中：** 机器人必须加入 `channel` 中指定的频道。

### 令牌问题

**“连接失败”或身份验证错误：**

- 验证 `accessToken` 是OAuth访问令牌值（通常以 `oauth:` 前缀开头）
- 检查令牌具有 `chat:read` 和 `chat:write` 范围
- 如果使用令牌刷新，验证 `clientSecret` 和 `refreshToken` 已设置

### 令牌刷新不起作用

**检查日志中的刷新事件：**

```
Using env token source for mybot
Access token refreshed for user 123456 (expires in 14400s)
```

如果看到“令牌刷新已禁用（没有刷新令牌）”：

- 确保提供了 `clientSecret`
- 确保提供了 `refreshToken`

## 配置

**账户配置：**

- `username` - 机器人用户名
- `accessToken` - 具有 `chat:read` 和 `chat:write` 的OAuth访问令牌
- `clientId` - Twitch Client ID（来自Token Generator或您的应用）
- `channel` - 要加入的频道（必需）
- `enabled` - 启用此账户（默认： `true`）
- `clientSecret` - 可选：用于自动令牌刷新
- `refreshToken` - 可选：用于自动令牌刷新
- `expiresIn` - 令牌过期时间（秒）
- `obtainmentTimestamp` - 获取令牌的时间戳
- `allowFrom` - 用户ID白名单
- `allowedRoles` - 基于角色的访问控制 (`"moderator" | "owner" | "vip" | "subscriber" | "all"`)
- `requireMention` - 要求@提及（默认： `true`）

**提供商选项：**

- `channels.twitch.enabled` - 启用/禁用频道启动
- `channels.twitch.username` - 机器人用户名（简化单账户配置）
- `channels.twitch.accessToken` - OAuth访问令牌（简化单账户配置）
- `channels.twitch.clientId` - Twitch Client ID（简化单账户配置）
- `channels.twitch.channel` - 要加入的频道（简化单账户配置）
- `channels.twitch.accounts.<accountName>` - 多账户配置（上述所有账户字段）

完整示例：

```json5
{
  channels: {
    twitch: {
      enabled: true,
      username: "openclaw",
      accessToken: "oauth:abc123...",
      clientId: "xyz789...",
      channel: "vevisk",
      clientSecret: "secret123...",
      refreshToken: "refresh456...",
      allowFrom: ["123456789"],
      allowedRoles: ["moderator", "vip"],
      accounts: {
        default: {
          username: "mybot",
          accessToken: "oauth:abc123...",
          clientId: "xyz789...",
          channel: "your_channel",
          enabled: true,
          clientSecret: "secret123...",
          refreshToken: "refresh456...",
          expiresIn: 14400,
          obtainmentTimestamp: 1706092800000,
          allowFrom: ["123456789", "987654321"],
          allowedRoles: ["moderator"],
        },
      },
    },
  },
}
```

## 工具操作

代理可以使用 `twitch` 调用操作：

- `send` - 发送消息到频道

示例：

```json5
{
  action: "twitch",
  params: {
    message: "Hello Twitch!",
    to: "#mychannel",
  },
}
```

## 安全与运维

- **像对待密码一样对待令牌** - 永远不要将令牌提交到git
- **使用自动令牌刷新** 对于长时间运行的机器人
- **使用用户ID白名单** 而不是用户名进行访问控制
- **监控日志** 以获取令牌刷新事件和连接状态
- **最小化令牌范围** - 仅请求 `chat:read` 和 `chat:write`
- **如果卡住**：确认没有其他进程拥有会话后重启网关

## 限制

- **每条消息500个字符**（在单词边界处自动分块）
- 在分块前剥离Markdown
- 无速率限制（使用Twitch内置的速率限制）