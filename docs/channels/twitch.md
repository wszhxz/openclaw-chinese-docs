---
summary: "Twitch chat bot configuration and setup"
read_when:
  - Setting up Twitch chat integration for OpenClaw
title: "Twitch"
---
# Twitch（插件）

通过IRC连接支持Twitch聊天。OpenClaw以Twitch用户（机器人账户）身份连接，以接收和发送频道中的消息。

## 所需插件

Twitch作为插件提供，不包含在核心安装中。

通过CLI（npm注册表）安装：

```bash
openclaw plugins install @openclaw/twitch
```

本地检出（当从git仓库运行时）：

```bash
openclaw plugins install ./extensions/twitch
```

详情：[插件](/plugin)

## 快速设置（初学者）

1. 为机器人创建一个专用的Twitch账户（或使用现有账户）。
2. 生成凭据：[Twitch Token生成器](https://twitchtokengenerator.com/)
   - 选择**Bot Token**
   - 确认选中了`chat:read`和`chat:write`作用域
   - 复制**Client ID**和**Access Token**
3. 查找您的Twitch用户ID：https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/
4. 配置令牌：
   - 环境变量：`OPENCLAW_TWITCH_ACCESS_TOKEN=...`（仅默认账户）
   - 或配置：`channels.twitch.accessToken`
   - 如果两者都设置，配置优先（环境变量回退为仅默认账户）。
5. 启动网关。

**⚠️ 重要：** 添加访问控制（`allowFrom`或`allowedRoles`）以防止未经授权的用户触发机器人。`requireMention`默认为`true`。

最小配置：

```json5
{
  channels: {
    twitch: {
      enabled: true,
      username: "openclaw", // 机器人的Twitch账户
      accessToken: "oauth:abc123...", // OAuth访问令牌（或使用OPENCLAW_TWITCH_ACCESS_TOKEN环境变量）
      clientId: "xyz789...", // 从Token生成器获取的Client ID
      channel: "vevisk", // 要加入的Twitch频道（必需）
      allowFrom: ["123456789"], // （推荐）仅您的Twitch用户ID - 从https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/获取
    },
  },
}
```

## 它是什么

- 由网关拥有的Twitch频道。
- 确定性路由：回复始终返回到Twitch。
- 每个账户映射到一个隔离的会话密钥`agent:<agentId>:twitch:<accountName>`。
- `username`是机器人的账户（用于认证），`channel`是加入的聊天室。

## 设置（详细）

### 生成凭据

使用[Twitch Token生成器](https://twitchtokengenerator.com/)：

- 选择**Bot Token**
- 确认选中了`chat:read`和`chat:write`作用域
- 复制**Client ID**和**Access Token**

无需手动应用注册。令牌在数小时后过期。

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
      allowFrom: ["123456789"], // （推荐）仅您的Twitch用户ID
    },
  },
}
```

优先使用`allowFrom`进行硬白名单。如果需要基于角色的访问，使用`allowedRoles`代替。

**可用角色：** `"moderator"`、`"owner"`、`"vip"`、`"subscriber"`、`"all"`。

**为什么使用用户ID？** 用户名可以更改，允许伪装。用户ID是永久的。

查找您的Twitch用户ID：https://www.streamweasels.com/tools/convert-twitch-username-%20to-user-id/（将您的Twitch用户名转换为ID）

## 令牌刷新（可选）

从[Twitch Token生成器](https://twitchtokengenerator.com/)获取的令牌无法自动刷新 - 令牌过期后需重新生成。

如需自动刷新令牌，请在[Twitch开发者控制台](https://dev.twitch.tv/console)创建自己的Twitch应用，并添加到配置中：

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

机器人会在令牌过期前自动刷新令牌，并记录刷新事件。

## 多账户支持

使用`channels.twitch.accounts`与每个账户的令牌。查看[`gateway/configuration`](/gateway/configuration)了解共享模式。

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
          channel: "your_channel",
        },
        channel2: {
          username: "openclaw",
          accessToken: "oauth:def456...",
          clientId: "uvw789...",
          channel: "another_channel",
        },
      },
    },
  },
}
```

## 工具操作

代理可以使用`twitch`动作：

- `send` - 向频道发送消息

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

- **将令牌视为密码** - 永远不要将令牌提交到git
- **为长时间运行的机器人使用自动令牌刷新**
- **使用用户ID白名单而不是用户名进行访问控制**
- **监控日志**以获取令牌刷新事件和连接状态
- **最小化令牌作用域** - 仅请求`chat:read`和`chat:write`
- **如果卡住**：在确认没有其他进程占用会话后重启网关

## 限制

- **每条消息500个字符**（在单词边界自动分块）
- 分块前会移除Markdown
- 无速率限制（使用Twitch内置的速率限制）