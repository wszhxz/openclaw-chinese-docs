---
summary: "Feishu bot overview, features, and configuration"
read_when:
  - You want to connect a Feishu/Lark bot
  - You are configuring the Feishu channel
title: Feishu
---
# 飞书机器人

飞书（Lark）是一个由公司用于消息传递和协作的团队聊天平台。此插件通过平台的WebSocket事件订阅将OpenClaw连接到飞书/Lark机器人，以便在不公开Webhook URL的情况下接收消息。

---

## 所需插件

安装飞书插件：

```bash
openclaw plugins install @openclaw/feishu
```

本地检出（当从git仓库运行时）：

```bash
openclaw plugins install ./extensions/feishu
```

---

## 快速入门

有两种方法可以添加飞书频道：

### 方法1：入站向导（推荐）

如果您刚刚安装了OpenClaw，请运行向导：

```bash
openclaw onboard
```

向导会引导您完成以下步骤：

1. 创建飞书应用并收集凭据
2. 在OpenClaw中配置应用凭据
3. 启动网关

✅ **配置完成后**，检查网关状态：

- `openclaw gateway status`
- `openclaw logs --follow`

### 方法2：CLI设置

如果您已经完成了初始安装，请通过CLI添加频道：

```bash
openclaw channels add
```

选择**飞书**，然后输入App ID和App Secret。

✅ **配置完成后**，管理网关：

- `openclaw gateway status`
- `openclaw gateway restart`
- `openclaw logs --follow`

---

## 步骤1：创建飞书应用

### 1. 打开飞书开放平台

访问[飞书开放平台](https://open.feishu.cn/app)并登录。

Lark（全球）租户应使用[https://open.larksuite.com/app](https://open.larksuite.com/app)并在飞书配置中设置`domain: "lark"`。

### 2. 创建应用

1. 点击**创建企业应用**
2. 填写应用名称+描述
3. 选择应用图标

![创建企业应用](../images/feishu-step2-create-app.png)

### 3. 复制凭据

在**凭据与基本信息**中复制：

- **App ID**（格式：`cli_xxx`）
- **App Secret**

❗ **重要：** 请保持App Secret私密。

![获取凭据](../images/feishu-step3-credentials.png)

### 4. 配置权限

在**权限**中，点击**批量导入**并粘贴：

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

在**应用能力** > **机器人**中：

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

如果您使用 `connectionMode: "webhook"`，请设置 `verificationToken`。飞书 Webhook 服务器默认绑定到 `127.0.0.1`；只有在您有意需要不同的绑定地址时才设置 `webhookHost`。

### 通过环境变量配置

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
```

### Lark（全球）域名

如果您的租户在 Lark（国际），请将域名设置为 `lark`（或完整的域名字符串）。您可以在 `channels.feishu.domain` 或每个账户中设置 (`channels.feishu.accounts.<id>.domain`)。

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
- **WebSocket 连接**: 通过飞书 SDK 的长连接，不需要公共 URL

---

## 访问控制

### 直接消息

- **默认**: `dmPolicy: "pairing"`（未知用户收到配对码）
- **批准配对**:

  ```bash
  openclaw pairing list feishu
  openclaw pairing approve feishu <CODE>
  ```

- **白名单模式**: 设置 `channels.feishu.allowFrom` 并包含允许的 Open ID

### 群聊

**1. 群组策略** (`channels.feishu.groupPolicy`):

- `"open"` = 允许所有组中的所有人（默认）
- `"allowlist"` = 仅允许 `groupAllowFrom`
- `"disabled"` = 禁用组消息

**2. 提及要求** (`channels.feishu.groups.<chat_id>.requireMention`):

- `true` = 需要 @提及（默认）
- `false` = 不带提及回复

---

## 组配置示例

### 允许所有组，需要 @提及（默认）

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

### 允许所有组，不需要 @提及

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

### 仅允许组中的特定用户

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

## 获取组/用户ID

### 组ID (chat_id)

组ID看起来像 `oc_xxx`。

**方法1（推荐）**

1. 启动网关并在组中@提及机器人
2. 运行 `openclaw logs --follow` 并查找 `chat_id`

**方法2**

使用飞书API调试器列出群聊。

### 用户ID (open_id)

用户ID看起来像 `ou_xxx`。

**方法1（推荐）**

1. 启动网关并直接消息机器人
2. 运行 `openclaw logs --follow` 并查找 `open_id`

**方法2**

检查配对请求以获取用户Open ID：

```bash
openclaw pairing list feishu
```

---

## 常用命令

| 命令   | 描述       |
| --------- | ----------------- |
| `/status` | 显示机器人状态   |
| `/reset`  | 重置会话 |
| `/model`  | 显示/切换模型 |

> 注意：飞书目前不支持原生命令菜单，因此命令必须作为文本发送。

## 网关管理命令

| 命令                    | 描述                   |
| -------------------------- | ----------------------------- |
| `openclaw gateway status`  | 显示网关状态           |
| `openclaw gateway install` | 安装/启动网关服务 |
| `openclaw gateway stop`    | 停止网关服务          |
| `openclaw gateway restart` | 重启网关服务       |
| `openclaw logs --follow`   | 查看网关日志             |

---

## 故障排除

### 机器人在群聊中不响应

1. 确保机器人已添加到群组
2. 确保您@提及了机器人（默认行为）
3. 检查 `groupPolicy` 是否未设置为 `"disabled"`
4. 检查日志: `openclaw logs --follow`

### 机器人未收到消息

1. 确保应用已发布并通过审批
2. 确保事件订阅包括 `im.message.receive_v1`
3. 确保启用了**长连接**
4. 确保应用权限完整
5. 确保网关正在运行: `openclaw gateway status`
6. 检查日志: `openclaw logs --follow`

### 应用密钥泄露

1. 在飞书开放平台重置App Secret
2. 在您的配置中更新App Secret
3. 重启网关

### 消息发送失败

1. 确保应用具有 `im:message:send_as_bot` 权限
2. 确保应用已发布
3. 检查日志以获取详细错误信息

---

## 高级配置

### 多个账户

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

- `textChunkLimit`: 发送文本块大小（默认：2000 字符）
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

查看[获取群组/用户ID](#get-groupuser-ids)以获取查找提示。

---

## 配置参考

完整配置：[网关配置](/gateway/configuration)

关键选项：

| 设置                                           | 描述                     | 默认          |
| ------------------------------------------------- | ------------------------------- | ---------------- |
| `channels.feishu.enabled`                         | 启用/禁用频道          | `true`           |
| `channels.feishu.domain`                          | API 域 (`feishu` 或 `lark`) | `feishu`         |
| `channels.feishu.connectionMode`                  | 事件传输模式            | `websocket`      |
| `channels.feishu.verificationToken`               | Webhook 模式必需       | -                |
| `channels.feishu.webhookPath`                     | Webhook 路径              | `/feishu/events` |
| `channels.feishu.webhookHost`                     | Webhook 绑定主机               | `127.0.0.1`      |
| `channels.feishu.webhookPort`                     | Webhook 绑定端口               | `3000`           |
| `channels.feishu.accounts.<id>.appId`             | 应用ID                          | -                |
| `channels.feishu.accounts.<id>.appSecret`         | 应用密钥                      | -                |
| `channels.feishu.accounts.<id>.domain`            | 按账户覆盖API域 | `feishu`         |
| `channels.feishu.dmPolicy`                        | 私信策略                       | `pairing`        |
| `channels.feishu.allowFrom`                       | 私信白名单 (open_id 列表)     | -                |
| `channels.feishu.groupPolicy`                     | 群组策略                    | `open`           |
| `channels.feishu.groupAllowFrom`                  | 群组白名单                 | -                |
| `channels.feishu.groups.<chat_id>.requireMention` | 需要@提及                | `true`           |
| `channels.feishu.groups.<chat_id>.enabled`        | 启用群组                    | `true`           |
| `channels.feishu.textChunkLimit`                  | 消息块大小              | `2000`           |
| `channels.feishu.mediaMaxMb`                      | 媒体大小限制                | `30`             |
| `channels.feishu.streaming`                       | 启用流式卡片输出    | `true`           |
| `channels.feishu.blockStreaming`                  | 启用块流式          | `true`           |

---

## dmPolicy 参考

| 值         | 行为                                                        |
| ------------- | --------------------------------------------------------------- |
| `"pairing"`   | **默认.** 未知用户获取配对码；必须被批准 |
| `"allowlist"` | 仅允许 `allowFrom` 中的用户聊天                              |
| `"open"`      | 允许所有用户 (需要 `"*"` 在 allowFrom 中)                   |
| `"disabled"`  | 禁用私信                                                     |

---

## 支持的消息类型

### 接收

- ✅ 文本
- ✅ 富文本 (帖子)
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
- ⚠️ 富文本 (部分支持)