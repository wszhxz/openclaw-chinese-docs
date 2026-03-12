---
summary: "Twitch chat bot configuration and setup"
read_when:
  - Setting up Twitch chat integration for OpenClaw
title: "Twitch"
---
# Twitch（插件）

通过 IRC 连接支持 Twitch 聊天。OpenClaw 以 Twitch 用户（机器人账号）身份连接，从而在频道中接收和发送消息。

## 插件要求

Twitch 作为插件提供，未与核心安装包捆绑。

通过 CLI（npm 仓库）安装：

```bash
openclaw plugins install @openclaw/twitch
```

本地检出（当从 git 仓库运行时）：

```bash
openclaw plugins install ./extensions/twitch
```

详情参见：[插件](/tools/plugin)

## 快速设置（新手向）

1. 为机器人创建一个专用的 Twitch 账号（或使用已有账号）。
2. 生成凭据：[Twitch Token Generator](https://twitchtokengenerator.com/)
   - 选择 **Bot Token**
   - 确认已勾选权限范围 `chat:read` 和 `chat:write`
   - 复制 **Client ID** 和 **Access Token**
3. 查询您的 Twitch 用户 ID：[https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/](https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/)
4. 配置令牌：
   - 环境变量：`OPENCLAW_TWITCH_ACCESS_TOKEN=...`（仅默认账号生效）
   - 或配置文件：`channels.twitch.accessToken`
   - 若两者均设置，以配置文件为准（环境变量仅作为默认账号的回退方案）。
5. 启动网关。

**⚠️ 重要提示：** 添加访问控制（`allowFrom` 或 `allowedRoles`），防止未授权用户触发机器人。`requireMention` 默认值为 `true`。

最小化配置示例：

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

- 由网关拥有的 Twitch 频道。
- 确定性路由：回复始终返回至 Twitch。
- 每个账号映射到一个独立的会话密钥 `agent:<agentId>:twitch:<accountName>`。
- `username` 是机器人的账号（用于身份验证），`channel` 是要加入的聊天室。

## 详细设置

### 生成凭据

使用 [Twitch Token Generator](https://twitchtokengenerator.com/)：

- 选择 **Bot Token**
- 确认已勾选权限范围 `chat:read` 和 `chat:write`
- 复制 **Client ID** 和 **Access Token**

无需手动注册应用。令牌数小时后过期。

### 配置机器人

**环境变量（仅默认账号）：**

```bash
OPENCLAW_TWITCH_ACCESS_TOKEN=oauth:abc123...
```

**或配置文件：**

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

若同时设置了环境变量与配置文件，以配置文件为准。

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

建议使用 `allowFrom` 实现严格的白名单机制。如需基于角色的访问控制，请改用 `allowedRoles`。

**可用角色：** `"moderator"`、`"owner"`、`"vip"`、`"subscriber"`、`"all"`。

**为何使用用户 ID？** 用户名可变更，存在冒充风险；而用户 ID 是永久不变的。

查询您的 Twitch 用户 ID：[https://www.streamweasels.com/tools/convert-twitch-username-%20to-user-id/](https://www.streamweasels.com/tools/convert-twitch-username-%20to-user-id/)（将您的 Twitch 用户名转换为 ID）

## 令牌刷新（可选）

来自 [Twitch Token Generator](https://twitchtokengenerator.com/) 的令牌无法自动刷新——过期后需手动重新生成。

如需自动刷新令牌，请在 [Twitch Developer Console](https://dev.twitch.tv/console) 创建您自己的 Twitch 应用，并在配置中添加以下内容：

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

机器人将在令牌过期前自动刷新，并记录刷新事件。

## 多账号支持

使用 `channels.twitch.accounts` 并为每个账号提供独立令牌。共享配置模式详见 [`gateway/configuration`](/gateway/configuration)。

示例（一个机器人账号加入两个频道）：

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

**注意：** 每个账号需拥有其专属令牌（每频道一个令牌）。

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

### 基于用户 ID 的白名单（最安全）

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

`allowFrom` 是硬性白名单。一旦设置，仅允许列表中的用户 ID 访问。  
若您希望启用基于角色的访问，请勿设置 `allowFrom`，而是配置 `allowedRoles`：

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

### 禁用 @提及要求

默认情况下，`requireMention` 为 `true`。如需禁用该限制并响应所有消息，请设置：

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

## 故障排查

首先运行诊断命令：

```bash
openclaw doctor
openclaw channels status --probe
```

### 机器人不响应消息

**检查访问控制：** 确保您的用户 ID 已加入 `allowFrom`；或临时移除 `allowFrom` 并将 `allowedRoles: ["all"]` 设为测试值。

**检查机器人是否已在频道中：** 机器人必须加入 `channel` 中指定的频道。

### 令牌问题

**“连接失败”或身份验证错误：**

- 确认 `accessToken` 是 OAuth 访问令牌值（通常以 `oauth:` 开头）
- 检查令牌是否包含 `chat:read` 和 `chat:write` 权限范围
- 若启用了令牌刷新，请确认已正确设置 `clientSecret` 和 `refreshToken`

### 令牌刷新未生效

**检查日志中是否有刷新事件：**

```
Using env token source for mybot
Access token refreshed for user 123456 (expires in 14400s)
```

若看到 “token refresh disabled (no refresh token)” 提示：

- 确保提供了 `clientSecret`
- 确保提供了 `refreshToken`

## 配置项

**账号配置：**

- `username` — 机器人用户名  
- `accessToken` — 具有 `chat:read` 和 `chat:write` 权限的 OAuth 访问令牌  
- `clientId` — Twitch Client ID（来自 Token Generator 或您自己的应用）  
- `channel` — 要加入的频道（必需）  
- `enabled` — 启用此账号（默认：`true`）  
- `clientSecret` — 可选：用于自动令牌刷新  
- `refreshToken` — 可选：用于自动令牌刷新  
- `expiresIn` — 令牌有效期（单位：秒）  
- `obtainmentTimestamp` — 获取令牌的时间戳  
- `allowFrom` — 用户 ID 白名单  
- `allowedRoles` — 基于角色的访问控制（`"moderator" | "owner" | "vip" | "subscriber" | "all"`）  
- `requireMention` — 是否要求 @提及（默认：`true`）

**提供者选项：**

- `channels.twitch.enabled` — 启用/禁用频道启动  
- `channels.twitch.username` — 机器人用户名（简化单账号配置）  
- `channels.twitch.accessToken` — OAuth 访问令牌（简化单账号配置）  
- `channels.twitch.clientId` — Twitch Client ID（简化单账号配置）  
- `channels.twitch.channel` — 要加入的频道（简化单账号配置）  
- `channels.twitch.accounts.<accountName>` — 多账号配置（含上述全部账号字段）

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

代理可调用 `twitch` 并执行以下动作：

- `send` — 向频道发送消息

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

- **将令牌视同密码对待** — 切勿将令牌提交至 Git  
- **对长期运行的机器人启用自动令牌刷新**  
- **使用用户 ID 白名单而非用户名进行访问控制**  
- **监控日志**，关注令牌刷新事件及连接状态  
- **最小化令牌权限范围** — 仅申请 `chat:read` 和 `chat:write` 权限  
- **如遇卡顿**：确认无其他进程占用会话后，重启网关  

## 限制

- 每条消息最多 **500 字符**（按词边界自动分块）  
- 分块前将剥离 Markdown 格式  
- 无额外限频机制（依赖 Twitch 内置限频）