---
summary: "Feishu bot overview, features, and configuration"
read_when:
  - You want to connect a Feishu/Lark bot
  - You are configuring the Feishu channel
title: Feishu
---
# 飞书机器人（Feishu bot）

飞书（Lark）是企业用于消息沟通与协作的团队聊天平台。本插件通过飞书平台的 WebSocket 事件订阅机制，将 OpenClaw 连接到飞书/ Lark 机器人，从而无需暴露公网 Webhook 地址即可接收消息。

---

## 插件安装要求

安装飞书插件：

```bash
openclaw plugins install @openclaw/feishu
```

本地检出（当从 Git 仓库运行时）：

```bash
openclaw plugins install ./extensions/feishu
```

---

## 快速开始

添加飞书通道有两种方式：

### 方法 1：引导向导（推荐）

若您刚刚安装 OpenClaw，请运行向导：

```bash
openclaw onboard
```

向导将引导您完成以下步骤：

1. 创建飞书应用并获取凭证
2. 在 OpenClaw 中配置应用凭证
3. 启动网关

✅ **配置完成后**，检查网关状态：

- `openclaw gateway status`
- `openclaw logs --follow`

### 方法 2：命令行（CLI）配置

若您已完成初始安装，可通过 CLI 添加通道：

```bash
openclaw channels add
```

选择 **飞书（Feishu）**，然后输入 App ID 和 App Secret。

✅ **配置完成后**，管理网关：

- `openclaw gateway status`
- `openclaw gateway restart`
- `openclaw logs --follow`

---

## 步骤 1：创建飞书应用

### 1. 打开飞书开放平台

访问 [飞书开放平台](https://open.feishu.cn/app) 并登录。

使用 Lark（国际版）租户的用户应访问 [https://open.larksuite.com/app](https://open.larksuite.com/app)，并在飞书配置中设置 `domain: "lark"`。

### 2. 创建应用

1. 点击 **创建企业自建应用**
2. 填写应用名称和描述
3. 选择应用图标

![创建企业自建应用](../images/feishu-step2-create-app.png)

### 3. 复制凭证信息

在 **凭证与基本信息** 页面中，复制以下内容：

- **App ID**（格式为：`cli_xxx`）
- **App Secret**

❗ **重要提示：** 请严格保密 App Secret。

![获取凭证](../images/feishu-step3-credentials.png)

### 4. 配置权限

在 **权限管理** 页面中，点击 **批量导入**，粘贴以下内容：

```json
{
  "scopes": {
    "tenant": [
      "aily:file:read",
      "aily:file:write",
      "application:application.app_message_stats.overview:readonly",
      "application:application:self_manage",
      "application:bot.menu:write",
      "cardkit:card:read",
      "cardkit:card:write",
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

### 5. 启用机器人能力

在 **应用能力** → **机器人** 中：

1. 启用机器人能力
2. 设置机器人名称

![启用机器人能力](../images/feishu-step5-bot-capability.png)

### 6. 配置事件订阅

⚠️ **重要提示：** 在配置事件订阅前，请确保：

1. 已对飞书执行过 `openclaw channels add`
2. 网关正在运行（`openclaw gateway status`）

在 **事件订阅** 页面中：

1. 选择 **使用长连接接收事件（WebSocket）**
2. 添加事件：`im.message.receive_v1`

⚠️ 若网关未运行，长连接配置可能无法保存。

![配置事件订阅](../images/feishu-step6-event-subscription.png)

### 7. 发布应用

1. 在 **版本管理与发布** 中创建一个版本
2. 提交审核并发布
3. 等待管理员审批（企业应用通常自动通过）

---

## 步骤 2：配置 OpenClaw

### 使用向导配置（推荐）

```bash
openclaw channels add
```

选择 **飞书（Feishu）**，并粘贴您的 App ID 和 App Secret。

### 通过配置文件配置

编辑 `~/.openclaw/openclaw.json`：

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

若您使用 `connectionMode: "webhook"`，请设置 `verificationToken`。飞书 Webhook 服务默认绑定到 `127.0.0.1`；仅当您明确需要不同的绑定地址时，才需设置 `webhookHost`。

#### 验证令牌（Webhook 模式）

在 Webhook 模式下，需在配置中设置 `channels.feishu.verificationToken`。获取该值的方法如下：

1. 在飞书开放平台中打开您的应用
2. 进入 **开发** → **事件与回调**（开发配置 → 事件与回调）
3. 打开 **加密策略** 标签页
4. 复制 **验证令牌（Verification Token）**

![验证令牌位置](../images/feishu-verification-token.png)

### 通过环境变量配置

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
```

### Lark（国际版）域名

若您的租户属于 Lark（国际版），请将域名设为 `lark`（或完整域名字符串）。您可在 `channels.feishu.domain` 或按账号（`channels.feishu.accounts.<id>.domain`）进行设置。

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

### 配额优化标志位

您可通过两个可选标志位减少飞书 API 调用量：

- `typingIndicator`（默认值为 `true`）：当设为 `false` 时，跳过“正在输入”反应调用。
- `resolveSenderNames`（默认值为 `true`）：当设为 `false` 时，跳过发送者资料查询调用。

可在顶层或按账号设置：

```json5
{
  channels: {
    feishu: {
      typingIndicator: false,
      resolveSenderNames: false,
      accounts: {
        main: {
          appId: "cli_xxx",
          appSecret: "xxx",
          typingIndicator: true,
          resolveSenderNames: false,
        },
      },
    },
  },
}
```

---

## 步骤 3：启动并测试

### 1. 启动网关

```bash
openclaw gateway
```

### 2. 发送测试消息

在飞书中找到您的机器人，并发送一条消息。

### 3. 确认配对

默认情况下，机器人会回复一个配对码。请确认配对：

```bash
openclaw pairing approve feishu <CODE>
```

确认后，即可正常聊天。

---

## 概览

- **飞书机器人通道**：由网关统一管理的飞书机器人
- **确定性路由**：所有回复均返回至飞书
- **会话隔离**：私聊共享主会话；群聊相互隔离
- **WebSocket 连接**：通过飞书 SDK 建立长连接，无需公网 URL

---

## 访问控制

### 私聊（Direct messages）

- **默认行为**：`dmPolicy: "pairing"`（未知用户将收到配对码）
- **确认配对**：

  ```bash
  openclaw pairing list feishu
  openclaw pairing approve feishu <CODE>
  ```

- **白名单模式**：设置 `channels.feishu.allowFrom`，填入允许的 Open ID 列表

### 群聊（Group chats）

**1. 群组策略**（`channels.feishu.groupPolicy`）：

- `"open"` = 允许所有群组成员（默认）
- `"allowlist"` = 仅允许 `groupAllowFrom`
- `"disabled"` = 禁用群聊消息

**2. @提及要求**（`channels.feishu.groups.<chat_id>.requireMention`）：

- `true` = 必须 @提及机器人（默认）
- `false` = 无需 @提及即可响应

---

## 群组配置示例

### 允许全部群组，且必须 @提及（默认）

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

### 允许全部群组，且无需 @提及

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

### 仅允许特定群组

```json5
{
  channels: {
    feishu: {
      groupPolicy: "allowlist",
      // Feishu group IDs (chat_id) look like: oc_xxx
      groupAllowFrom: ["oc_xxx", "oc_yyy"],
    },
  },
}
```

### 限制群组内可发消息的发送者（发送者白名单）

除允许该群组本身外，**该群组内的所有消息**均受发送者 open_id 控制：仅 `groups.<chat_id>.allowFrom` 中列出的用户所发消息会被处理；其余成员的消息将被忽略（这是完整的发送者级别管控，不仅限于 `/reset` 或 `/new` 等控制指令）。

```json5
{
  channels: {
    feishu: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["oc_xxx"],
      groups: {
        oc_xxx: {
          // Feishu user IDs (open_id) look like: ou_xxx
          allowFrom: ["ou_user1", "ou_user2"],
        },
      },
    },
  },
}
```

---

## 获取群组/用户 ID

### 群组 ID（chat_id）

群组 ID 形如 `oc_xxx`。

**方法 1（推荐）**

1. 启动网关，并在目标群组中 @提及机器人
2. 运行 `openclaw logs --follow`，查找 `chat_id`

**方法 2**

使用飞书 API 调试器列出群聊。

### 用户 ID（open_id）

用户 ID 形如 `ou_xxx`。

**方法 1（推荐）**

1. 启动网关，并向机器人发起私聊
2. 运行 `openclaw logs --follow`，查找 `open_id`

**方法 2**

在配对请求中查看用户 Open ID：

```bash
openclaw pairing list feishu
```

---

## 常用命令

| 命令         | 描述             |
| ------------ | ---------------- |
| `/status` | 显示机器人状态     |
| `/reset`  | 重置会话           |
| `/model`  | 显示/切换模型       |

> 注意：飞书目前尚不支持原生命令菜单，因此命令需以纯文本形式发送。

## 网关管理命令

| 命令                         | 描述               |
| ---------------------------- | ------------------ |
| `openclaw gateway status`  | 显示网关状态         |
| `openclaw gateway install` | 安装/启动网关服务     |
| `openclaw gateway stop`    | 停止网关服务         |
| `openclaw gateway restart` | 重启网关服务         |
| `openclaw logs --follow`   | 实时查看网关日志      |

---

## 故障排查

### 机器人在群聊中无响应

1. 确保机器人已加入群组  
2. 确保您 @提及该机器人（默认行为）  
3. 检查 `groupPolicy` 未被设置为 `"disabled"`  
4. 查看日志：`openclaw logs --follow`  

### 机器人未收到消息  

1. 确保应用已发布并获批准  
2. 确保事件订阅中包含 `im.message.receive_v1`  
3. 确保已启用**长连接**  
4. 确保应用权限完整  
5. 确保网关正在运行：`openclaw gateway status`  
6. 查看日志：`openclaw logs --follow`  

### 应用密钥（App Secret）泄露  

1. 在飞书开放平台重置 App Secret  
2. 在您的配置中更新 App Secret  
3. 重启网关  

### 消息发送失败  

1. 确保应用拥有 `im:message:send_as_bot` 权限  
2. 确保应用已发布  
3. 查看日志以获取详细错误信息  

---  

## 高级配置  

### 多账号支持  

```json5
{
  channels: {
    feishu: {
      defaultAccount: "main",
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

`defaultAccount` 控制在出站 API 未显式指定 `accountId` 时所使用的飞书账号。  

### 消息长度限制  

- `textChunkLimit`：出站文本分块大小（默认：2000 字符）  
- `mediaMaxMb`：媒体上传/下载限制（默认：30MB）  

### 流式响应（Streaming）  

飞书支持通过交互式卡片实现流式回复。启用后，机器人将在生成文本过程中持续更新卡片内容。  

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

将 `streaming: false` 设置为 `true`，可等待完整回复生成完毕后再统一发送。  

### 多智能体路由（Multi-agent routing）  

使用 `bindings` 将飞书私聊（DM）或群组消息路由至不同智能体。  

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

路由字段说明：  

- `match.channel`：`"feishu"`  
- `match.peer.kind`：`"direct"` 或 `"group"`  
- `match.peer.id`：用户 Open ID（`ou_xxx`）或群组 ID（`oc_xxx`）  

查找 ID 方法请参阅 [获取群组/用户 ID](#get-groupuser-ids)。  

---  

## 配置项参考  

完整配置说明：[网关配置](/gateway/configuration)  

关键配置项：  

| 设置                                           | 描述                                     | 默认值          |  
| ---------------------------------------------- | ---------------------------------------- | ---------------- |  
| `channels.feishu.enabled`                         | 启用/禁用通道                            | `true`           |  
| `channels.feishu.domain`                          | API 域名（`feishu` 或 `lark`）         | `feishu`         |  
| `channels.feishu.connectionMode`                  | 事件传输模式                             | `websocket`      |  
| `channels.feishu.defaultAccount`                  | 出站路由默认账号 ID                      | `default`        |  
| `channels.feishu.verificationToken`               | Webhook 模式必需                         | -                |  
| `channels.feishu.webhookPath`                     | Webhook 路由路径                         | `/feishu/events` |  
| `channels.feishu.webhookHost`                     | Webhook 绑定主机                         | `127.0.0.1`      |  
| `channels.feishu.webhookPort`                     | Webhook 绑定端口                         | `3000`           |  
| `channels.feishu.accounts.<id>.appId`             | 应用 ID                                  | -                |  
| `channels.feishu.accounts.<id>.appSecret`         | 应用密钥（App Secret）                  | -                |  
| `channels.feishu.accounts.<id>.domain`            | 按账号覆盖 API 域名                      | `feishu`         |  
| `channels.feishu.dmPolicy`                        | 私聊（DM）策略                           | `pairing`        |  
| `channels.feishu.allowFrom`                       | 私聊白名单（Open ID 列表）              | -                |  
| `channels.feishu.groupPolicy`                     | 群组策略                                 | `open`           |  
| `channels.feishu.groupAllowFrom`                  | 群组白名单                               | -                |  
| `channels.feishu.groups.<chat_id>.requireMention` | 是否强制要求 @提及                       | `true`           |  
| `channels.feishu.groups.<chat_id>.enabled`        | 是否启用群组功能                         | `true`           |  
| `channels.feishu.textChunkLimit`                  | 消息分块大小                             | `2000`           |  
| `channels.feishu.mediaMaxMb`                      | 媒体文件大小限制                         | `30`             |  
| `channels.feishu.streaming`                       | 是否启用流式卡片输出                     | `true`           |  
| `channels.feishu.blockStreaming`                  | 是否启用区块流式（block streaming）       | `true`           |  

---  

## dmPolicy 参考  

| 值             | 行为                                                                 |  
| -------------- | -------------------------------------------------------------------- |  
| `"pairing"`   | **默认值。** 未知用户将获得配对码；需经管理员审批后方可通信         |  
| `"allowlist"` | 仅允许 `allowFrom` 中的用户发起聊天                           |  
| `"open"`      | 允许所有用户（需在 `allowFrom` 中配置 `"*"`）           |  
| `"disabled"`  | 禁用私聊（DM）                                                       |  

---  

## 支持的消息类型  

### 接收  

- ✅ 文本  
- ✅ 富文本（post）  
- ✅ 图片  
- ✅ 文件  
- ✅ 音频  
- ✅ 视频  
- ✅ 表情贴纸  

### 发送  

- ✅ 文本  
- ✅ 图片  
- ✅ 文件  
- ✅ 音频  
- ⚠️ 富文本（部分支持）