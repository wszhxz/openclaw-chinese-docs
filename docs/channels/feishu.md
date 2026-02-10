---
summary: "Feishu bot overview, features, and configuration"
read_when:
  - You want to connect a Feishu/Lark bot
  - You are configuring the Feishu channel
title: Feishu
---
# Feishu bot

Feishu (Lark) 是一个由公司用于消息传递和协作的团队聊天平台。此插件通过平台的 WebSocket 事件订阅将 OpenClaw 连接到 Feishu/Lark 机器人，以便在不公开 webhook URL 的情况下接收消息。

---

## 所需插件

安装 Feishu 插件：

```bash
openclaw plugins install @openclaw/feishu
```

本地检出（当从 git 仓库运行时）：

```bash
openclaw plugins install ./extensions/feishu
```

---

## 快速入门

有两种方法可以添加 Feishu 频道：

### 方法 1：入站向导（推荐）

如果您刚刚安装了 OpenClaw，请运行向导：

```bash
openclaw onboard
```

向导将引导您完成以下步骤：

1. 创建 Feishu 应用并收集凭据
2. 在 OpenClaw 中配置应用凭据
3. 启动网关

✅ **配置后**，检查网关状态：

- `openclaw gateway status`
- `openclaw logs --follow`

### 方法 2：CLI 设置

如果您已经完成了初始安装，请通过 CLI 添加频道：

```bash
openclaw channels add
```

选择 **Feishu**，然后输入 App ID 和 App Secret。

✅ **配置后**，管理网关：

- `openclaw gateway status`
- `openclaw gateway restart`
- `openclaw logs --follow`

---

## 步骤 1：创建 Feishu 应用

### 1. 打开 Feishu 开放平台

访问 [Feishu 开放平台](https://open.feishu.cn/app) 并登录。

Lark（全球）租户应使用 [https://open.larksuite.com/app](https://open.larksuite.com/app) 并在 Feishu 配置中设置 `domain: "lark"`。

### 2. 创建应用

1. 点击 **创建企业应用**
2. 填写应用名称 + 描述
3. 选择应用图标

![创建企业应用](../images/feishu-step2-create-app.png)

### 3. 复制凭据

从 **凭据与基本信息** 中复制：

- **App ID**（格式：`cli_xxx`）
- **App Secret**

❗ **重要：** 请保持 App Secret 私密。

![获取凭据](../images/feishu-step3-credentials.png)

### 4. 配置权限

在 **权限** 中，点击 **批量导入** 并粘贴：

```json
{
  "scopes": {
    "tenant": [
      "aily:file:read",
      "aily:file:write",
      "application:application.app_message_stats.overview:readonly",
      "application:application:self_manage",
      "application:bot.menu:write",
      "contact:user.employee_id:readonly",
      "corehr:file:download",
      "event:ip_list",
      "im:chat.access_event.bot_p2p_chat:read",
      "im:chat.members:bot_access",
      "im:message",
      "im:message.group_at_msg:readonly",
      "im:message.p2p_msg:readonly",
      "im:message:readonly",
      "im:message:send_as_bot",
      "im:resource"
    ],
    "user": ["aily:file:read", "aily:file:write", "im:chat.access_event.bot_p2p_chat:read"]
  }
}
```

![配置权限](../images/feishu-step4-permissions.png)

### 5. 启用机器人功能

在 **应用能力** > **机器人**：

1. 启用机器人功能
2. 设置机器人名称

![启用机器人功能](../images/feishu-step5-bot-capability.png)

### 6. 配置事件订阅

⚠️ **重要:** 在设置事件订阅之前，请确保：

1. 您已经为飞书运行了 `openclaw channels add`
2. 网关正在运行 (`openclaw gateway status`)

在 **事件订阅** 中：

1. 选择 **使用长连接接收事件** (WebSocket)
2. 添加事件: `im.message.receive_v1`

⚠️ 如果网关未运行，长连接设置可能无法保存。

![配置事件订阅](../images/feishu-step6-event-subscription.png)

### 7. 发布应用

1. 在 **版本管理与发布** 中创建一个版本
2. 提交审核并发布
3. 等待管理员批准（企业应用通常会自动批准）

---

## 步骤 2: 配置 OpenClaw

### 使用向导配置（推荐）

```bash
openclaw channels add
```

选择 **飞书** 并粘贴您的 App ID + App Secret。

### 通过配置文件配置

编辑 `~/.openclaw/openclaw.json`:

```json5
{
  channels: {
    feishu: {
      enabled: true,
      dmPolicy: "pairing",
      accounts: {
        main: {
          appId: "cli_xxx",
          appSecret: "xxx",
          botName: "My AI assistant",
        },
      },
    },
  },
}
```

### 通过环境变量配置

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
```

### Lark (全球) 域名

如果您的租户在 Lark（国际版），将域名设置为 `lark`（或完整的域名字符串）。您可以在 `channels.feishu.domain` 或每个账户中设置 (`channels.feishu.accounts.<id>.domain`)。

```json5
{
  channels: {
    feishu: {
      domain: "lark",
      accounts: {
        main: {
          appId: "cli_xxx",
          appSecret: "xxx",
        },
      },
    },
  },
}
```

---

## 步骤 3: 启动 + 测试

### 1. 启动网关

```bash
openclaw gateway
```

### 2. 发送测试消息

在飞书中找到您的机器人并发送一条消息。

### 3. 批准配对

默认情况下，机器人会回复一个配对码。批准它：

```bash
openclaw pairing approve feishu <CODE>
```

批准后，您可以正常聊天。

---

## 概述

- **飞书机器人通道**: 由网关管理的飞书机器人
- **确定性路由**: 回复总是返回到飞书
- **会话隔离**: 私聊共享一个主会话；群组是隔离的
- **WebSocket 连接**: 通过飞书 SDK 的长连接，无需公共 URL

---

## 访问控制

### 直接消息

- **默认**: `dmPolicy: "pairing"`（未知用户会收到配对码）
- **批准配对**:

  ```bash
  openclaw pairing list feishu
  openclaw pairing approve feishu <CODE>
  ```

- **白名单模式**: 设置 `channels.feishu.allowFrom` 为允许的 Open ID

### 群聊

**1. 群组策略** (`channels.feishu.groupPolicy`):

- `"open"` = 允许群组中的所有人（默认）
- `"allowlist"` = 仅允许 `groupAllowFrom`
- `"disabled"` = 禁用群组消息

**2. @提及要求** (`channels.feishu.groups.<chat_id>.requireMention`):

- `true` = require @mention (default)
- `false` = respond without mentions

---

## Group configuration examples

### Allow all groups, require @mention (default)

```json5
{
  channels: {
    feishu: {
      groupPolicy: "open",
      // Default requireMention: true
    },
  },
}
```

### Allow all groups, no @mention required

```json5
{
  channels: {
    feishu: {
      groups: {
        oc_xxx: { requireMention: false },
      },
    },
  },
}
```

### Allow specific users in groups only

```json5
{
  channels: {
    feishu: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["ou_xxx", "ou_yyy"],
    },
  },
}
```

---

## Get group/user IDs

### Group IDs (chat_id)

Group IDs look like `oc_xxx`.

**Method 1 (recommended)**

1. 启动网关并在群组中@mention机器人
2. 运行 `openclaw logs --follow` 并查找 `chat_id`

**Method 2**

使用飞书API调试器列出群聊。

### User IDs (open_id)

User IDs look like `ou_xxx`.

**Method 1 (recommended)**

1. 启动网关并直接消息机器人
2. 运行 `openclaw logs --follow` 并查找 `open_id`

**Method 2**

检查配对请求以获取用户Open ID：

```bash
openclaw pairing list feishu
```

---

## Common commands

| Command   | Description       |
| --------- | ----------------- |
| `/status` | Show bot status   |
| `/reset`  | Reset the session |
| `/model`  | Show/switch model |

> 注意：飞书目前不支持原生命令菜单，因此必须以文本形式发送命令。

## Gateway management commands

| Command                    | Description                   |
| -------------------------- | ----------------------------- |
| `openclaw gateway status`  | Show gateway status           |
| `openclaw gateway install` | Install/start gateway service |
| `openclaw gateway stop`    | Stop gateway service          |
| `openclaw gateway restart` | Restart gateway service       |
| `openclaw logs --follow`   | Tail gateway logs             |

---

## Troubleshooting

### Bot does not respond in group chats

1. 确保机器人已添加到群组
2. 确保您@mention了机器人（默认行为）
3. 检查 `groupPolicy` 是否未设置为 `"disabled"`
4. 检查日志：`openclaw logs --follow`

### Bot does not receive messages

1. 确保应用已发布并通过审批
2. 确保事件订阅包括 `im.message.receive_v1`
3. 确保已启用**长连接**
4. 确保应用权限完整
5. 确保网关正在运行：`openclaw gateway status`
6. 检查日志：`openclaw logs --follow`

### App Secret leak

1. 在飞书开放平台重置App Secret
2. 在您的配置中更新App Secret
3. 重启网关

### Message send failures

1. 确保应用具有 `im:message:send_as_bot` 权限
2. 确保应用已发布
3. 检查日志以获取详细错误信息

---

## Advanced configuration

### Multiple accounts

```json5
{
  channels: {
    feishu: {
      accounts: {
        main: {
          appId: "cli_xxx",
          appSecret: "xxx",
          botName: "Primary bot",
        },
        backup: {
          appId: "cli_yyy",
          appSecret: "yyy",
          botName: "Backup bot",
          enabled: false,
        },
      },
    },
  },
}
```

### 消息限制

- `textChunkLimit`: 出站文本块大小（默认：2000 字符）
- `mediaMaxMb`: 媒体上传/下载限制（默认：30MB）

### 流式传输

飞书支持通过交互卡片进行流式回复。启用后，机器人会在生成文本时更新卡片。

```json5
{
  channels: {
    feishu: {
      streaming: true, // enable streaming card output (default true)
      blockStreaming: true, // enable block-level streaming (default true)
    },
  },
}
```

设置 `streaming: false` 以等待完整回复后再发送。

### 多代理路由

使用 `bindings` 将飞书私信或群组路由到不同的代理。

```json5
{
  agents: {
    list: [
      { id: "main" },
      {
        id: "clawd-fan",
        workspace: "/home/user/clawd-fan",
        agentDir: "/home/user/.openclaw/agents/clawd-fan/agent",
      },
      {
        id: "clawd-xi",
        workspace: "/home/user/clawd-xi",
        agentDir: "/home/user/.openclaw/agents/clawd-xi/agent",
      },
    ],
  },
  bindings: [
    {
      agentId: "main",
      match: {
        channel: "feishu",
        peer: { kind: "direct", id: "ou_xxx" },
      },
    },
    {
      agentId: "clawd-fan",
      match: {
        channel: "feishu",
        peer: { kind: "direct", id: "ou_yyy" },
      },
    },
    {
      agentId: "clawd-xi",
      match: {
        channel: "feishu",
        peer: { kind: "group", id: "oc_zzz" },
      },
    },
  ],
}
```

路由字段：

- `match.channel`: `"feishu"`
- `match.peer.kind`: `"direct"` 或 `"group"`
- `match.peer.id`: 用户Open ID (`ou_xxx`) 或群组ID (`oc_xxx`)

查看[获取群组/用户ID](#get-groupuser-ids)获取查找提示。

---

## 配置参考

完整配置：[网关配置](/gateway/configuration)

关键选项：

| 设置                                           | 描述                     | 默认   |
| ------------------------------------------------- | ------------------------------- | --------- |
| `channels.feishu.enabled`                         | 启用/禁用频道          | `true`    |
| `channels.feishu.domain`                          | API 域 (`feishu` 或 `lark`) | `feishu`  |
| `channels.feishu.accounts.<id>.appId`             | 应用ID                          | -         |
| `channels.feishu.accounts.<id>.appSecret`         | 应用密钥                      | -         |
| `channels.feishu.accounts.<id>.domain`            | 按账户重写API域 | `feishu`  |
| `channels.feishu.dmPolicy`                        | DM策略                       | `pairing` |
| `channels.feishu.allowFrom`                       | DM白名单 (open_id列表)     | -         |
| `channels.feishu.groupPolicy`                     | 群组策略                    | `open`    |
| `channels.feishu.groupAllowFrom`                  | 群组白名单                 | -         |
| `channels.feishu.groups.<chat_id>.requireMention` | 需要@提及                | `true`    |
| `channels.feishu.groups.<chat_id>.enabled`        | 启用群组                    | `true`    |
| `channels.feishu.textChunkLimit`                  | 消息块大小              | `2000`    |
| `channels.feishu.mediaMaxMb`                      | 媒体大小限制                | `30`      |
| `channels.feishu.streaming`                       | 启用流卡片输出    | `true`    |
| `channels.feishu.blockStreaming`                  | 启用流阻塞          | `true`    |

---

## dmPolicy 参考

| 值         | 行为                                                        |
| ------------- | --------------------------------------------------------------- |
| `"pairing"`   | **默认。** 未知用户获得配对码；必须被批准 |
| `"allowlist"` | 仅`allowFrom`中的用户可以聊天                              |
| `"open"`      | 允许所有用户（需要`"*"`在allowFrom中）                   |
| `"disabled"`  | 禁用DMs                                                     |

---

## 支持的消息类型

### 接收

- ✅ 文本
- ✅ 富文本（帖子）
- ✅ 图片
- ✅ 文件
- ✅ 音频
- ✅ 视频
- ✅ 贴纸

### 发送

- ✅ 文本
- ✅ 图片
- ✅ 文件
- ✅ 音频
- ⚠️ 富文本（部分支持）