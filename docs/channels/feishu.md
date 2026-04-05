---
summary: "Feishu bot overview, features, and configuration"
read_when:
  - You want to connect a Feishu/Lark bot
  - You are configuring the Feishu channel
title: Feishu
---
# 飞书机器人

飞书（Lark）是一个用于消息传递和协作的团队聊天平台。此插件通过平台的 WebSocket 事件订阅将 OpenClaw 连接到飞书/Lark 机器人，以便在不暴露公共 webhook URL 的情况下接收消息。

---

## 捆绑插件

飞书随当前 OpenClaw 版本捆绑发布，因此不需要单独安装插件。

如果您使用的是不包含捆绑飞书的旧版本构建或自定义安装，请手动安装：

```bash
openclaw plugins install @openclaw/feishu
```

---

## 快速开始

有两种方式可以添加飞书频道：

### 方法 1：初始化向导（推荐）

如果您刚安装 OpenClaw，请运行初始化向导：

```bash
openclaw onboard
```

向导将引导您完成以下步骤：

1. 创建飞书应用并收集凭据
2. 在 OpenClaw 中配置应用凭据
3. 启动网关

✅ **配置完成后**，检查网关状态：

- `openclaw gateway status`
- `openclaw logs --follow`

### 方法 2：CLI 设置

如果您已完成初始安装，请通过 CLI 添加频道：

```bash
openclaw channels add
```

选择 **Feishu**，然后输入 App ID 和 App Secret。

✅ **配置完成后**，管理网关：

- `openclaw gateway status`
- `openclaw gateway restart`
- `openclaw logs --follow`

---

## 步骤 1：创建飞书应用

### 1. 打开飞书开放平台

访问 [飞书开放平台](https://open.feishu.cn/app) 并登录。

Lark（全球）租户应使用 [https://open.larksuite.com/app](https://open.larksuite.com/app) 并在飞书配置中设置 `domain: "lark"`。

### 2. 创建应用

1. 点击 **创建企业应用**
2. 填写应用名称 + 描述
3. 选择应用图标

![创建企业应用](/images/feishu-step2-create-app.png)

### 3. 复制凭据

从 **凭证与基本信息** 中复制：

- **App ID** (格式：`cli_xxx`)
- **App Secret**

❗ **重要：** 请保密 App Secret。

![获取凭据](/images/feishu-step3-credentials.png)

### 4. 配置权限

在 **权限** 上，点击 **批量导入** 并粘贴：

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

![配置权限](/images/feishu-step4-permissions.png)

### 5. 启用机器人能力

在 **应用能力** > **机器人** 中：

1. 启用机器人能力
2. 设置机器人名称

![启用机器人能力](/images/feishu-step5-bot-capability.png)

### 6. 配置事件订阅

⚠️ **重要：** 在设置事件订阅之前，请确保：

1. 您已经为飞书运行了 `openclaw channels add`
2. 网关正在运行 (`openclaw gateway status`)

在 **事件订阅** 中：

1. 选择 **使用长连接接收事件** (WebSocket)
2. 添加事件：`im.message.receive_v1`
3. （可选）对于云盘评论工作流，还需添加：`drive.notice.comment_add_v1`

⚠️ 如果网关未运行，长连接设置可能无法保存。

![配置事件订阅](/images/feishu-step6-event-subscription.png)

### 7. 发布应用

1. 在 **版本管理与发布** 中创建版本
2. 提交审核并发布
3. 等待管理员批准（企业应用通常自动批准）

---

## 步骤 2：配置 OpenClaw

### 使用向导配置（推荐）

```bash
openclaw channels add
```

选择 **Feishu** 并粘贴您的 App ID 和 App Secret。

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
          name: "My AI assistant",
        },
      },
    },
  },
}
```

如果您使用 `connectionMode: "webhook"`，请同时设置 `verificationToken` 和 `encryptKey`。飞书 webhook 服务器默认绑定到 `127.0.0.1`；仅当您确实需要不同的绑定地址时才设置 `webhookHost`。

#### 验证令牌和加密密钥（webhook 模式）

使用 webhook 模式时，请在配置中同时设置 `channels.feishu.verificationToken` 和 `channels.feishu.encryptKey`。获取这些值的方法：

1. 在飞书开放平台中，打开您的应用
2. 前往 **开发** → **事件与回调** (开发配置 → 事件与回调)
3. 打开 **加密** 选项卡 (加密策略)
4. 复制 **Verification Token** 和 **Encrypt Key**

下图显示了在哪里找到 **Verification Token**。 **Encrypt Key** 列在同一 **加密** 部分中。

![验证令牌位置](/images/feishu-verification-token.png)

### 通过环境变量配置

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
```

### Lark（全球）域名

如果您的租户在 Lark（国际版）上，请将域名设置为 `lark`（或完整域名字符串）。您可以在 `channels.feishu.domain` 处设置，或按账户设置 (`channels.feishu.accounts.<id>.domain`)。

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

### 配额优化标志

您可以使用两个可选标志来减少飞书 API 的使用：

- `typingIndicator` (默认 `true`)：当 `false` 时，跳过打字反应调用。
- `resolveSenderNames` (默认 `true`)：当 `false` 时，跳过发送者资料查找调用。

在顶层或按账户设置它们：

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

## 步骤 3：启动 + 测试

### 1. 启动网关

```bash
openclaw gateway
```

### 2. 发送测试消息

在飞书中，找到您的机器人并发送消息。

### 3. 批准配对

默认情况下，机器人会回复一个配对码。批准它：

```bash
openclaw pairing approve feishu <CODE>
```

批准后，您可以正常聊天。

---

## 概述

- **飞书机器人频道**：由网关管理的飞书机器人
- **确定性路由**：回复始终返回飞书
- **会话隔离**：私聊共享主会话；群组是隔离的
- **WebSocket 连接**：通过飞书 SDK 建立长连接，无需公开 URL

---

## 访问控制

### 私聊消息

- **默认**：`dmPolicy: "pairing"`（未知用户获得配对码）
- **批准配对**：

  ```bash
  openclaw pairing list feishu
  openclaw pairing approve feishu <CODE>
  ```

- **白名单模式**：设置 `channels.feishu.allowFrom` 包含允许的 Open IDs

### 群聊

**1. 群组策略** (`channels.feishu.groupPolicy`)：

- `"open"` = 允许群组中的所有人
- `"allowlist"` = 仅允许 `groupAllowFrom`
- `"disabled"` = 禁用群消息

默认：`allowlist`

**2. @提及要求** (`channels.feishu.requireMention`，可通过 `channels.feishu.groups.<chat_id>.requireMention` 覆盖)：

- 显式 `true` = 需要 @提及
- 显式 `false` = 无提及即回复
- 当未设置且 `groupPolicy: "open"` = 默认为 `false`
- 当未设置且 `groupPolicy` 不是 `"open"` = 默认为 `true`

---

## 群组配置示例

### 允许所有群组，无需 @提及（公开群组默认）

```json5
{
  channels: {
    feishu: {
      groupPolicy: "open",
    },
  },
}
```

### 允许所有群组，但仍需 @提及

```json5
{
  channels: {
    feishu: {
      groupPolicy: "open",
      requireMention: true,
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

### 限制哪些发送者可以在群组中发消息（发送者白名单）

除了允许该群组本身外，该群组中的 **所有消息** 都由发送者 open_id 进行门控：只有列在 `groups.<chat_id>.allowFrom` 中的用户的消息会被处理；来自其他成员的消息将被忽略（这是完整的发送者级别门控，不仅限于控制命令如 /reset 或 /new）。

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

<a id="get-groupuser-ids"></a>

## 获取群组/用户 ID

### 群组 ID (chat_id)

群组 ID 看起来像 `oc_xxx`。

**方法 1（推荐）**

1. 启动网关并在群组中 @提及机器人
2. 运行 `openclaw logs --follow` 并查找 `chat_id`

**方法 2**

使用飞书 API 调试器列出群聊。

### 用户 ID (open_id)

用户 ID 看起来像 `ou_xxx`。

**方法 1（推荐）**

1. 启动网关并私聊机器人
2. 运行 `openclaw logs --follow` 并查找 `open_id`

**方法 2**

检查配对请求以获取用户 Open IDs：

```bash
openclaw pairing list feishu
```

---

## 常用命令

| 命令 | 描述 |
| --------- | ----------------- |
| `/status` | 显示机器人状态 |
| `/reset` | 重置会话 |
| `/model` | 显示/切换模型 |

> 注意：飞书尚不支持原生命令菜单，因此命令必须作为文本发送。

## 网关管理命令

| 命令                    | 描述                   |
| -------------------------- | ----------------------------- |
| `openclaw gateway status`  | 显示网关状态           |
| `openclaw gateway install` | 安装/启动网关服务 |
| `openclaw gateway stop`    | 停止网关服务          |
| `openclaw gateway restart` | 重启网关服务       |
| `openclaw logs --follow`   | 查看网关日志尾部             |

---

## 故障排除

### 机器人在群聊中无响应

1. 确保机器人已加入群组
2. 确保您 @提及了机器人（默认行为）
3. 检查 `groupPolicy` 未设置为 `"disabled"`
4. 查看日志：`openclaw logs --follow`

### 机器人未收到消息

1. 确保应用已发布并获批
2. 确保事件订阅包含 `im.message.receive_v1`
3. 确保 **长连接** 已启用
4. 确保应用权限完整
5. 确保网关正在运行：`openclaw gateway status`
6. 查看日志：`openclaw logs --follow`

### 应用密钥泄露

1. 在飞书开放平台重置应用密钥
2. 在您的配置中更新应用密钥
3. 重启网关

### 消息发送失败

1. 确保应用拥有 `im:message:send_as_bot` 权限
2. 确保应用已发布
3. 查看日志以获取详细错误信息

---

## 高级配置

### 多账号

```json5
{
  channels: {
    feishu: {
      defaultAccount: "main",
      accounts: {
        main: {
          appId: "cli_xxx",
          appSecret: "xxx",
          name: "Primary bot",
        },
        backup: {
          appId: "cli_yyy",
          appSecret: "yyy",
          name: "Backup bot",
          enabled: false,
        },
      },
    },
  },
}
```

`defaultAccount` 控制当出站 API 未明确指定 `accountId` 时使用哪个飞书账号。

### 消息限制

- `textChunkLimit`：出站文本块大小（默认：2000 字符）
- `mediaMaxMb`：媒体上传/下载限制（默认：30MB）

### 流式传输

飞书支持通过互动卡片进行流式回复。启用后，机器人会在生成文本时更新卡片。

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

设置 `streaming: false` 以在发送前等待完整回复。

### ACP 会话

飞书支持以下场景的 ACP：

- 私聊
- 群话题对话

飞书 ACP 由文本命令驱动。没有原生的斜杠命令菜单，因此请在对话中直接使用 `/acp ...` 消息。

#### 持久化 ACP 绑定

使用顶层类型化 ACP 绑定将飞书私聊或话题对话固定到持久化 ACP 会话。

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "feishu",
        accountId: "default",
        peer: { kind: "direct", id: "ou_1234567890" },
      },
    },
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "feishu",
        accountId: "default",
        peer: { kind: "group", id: "oc_group_chat:topic:om_topic_root" },
      },
      acp: { label: "codex-feishu-topic" },
    },
  ],
}
```

#### 从聊天中生成线程绑定的 ACP

在飞书私聊或话题对话中，您可以就地生成并绑定 ACP 会话：

```text
/acp spawn codex --thread here
```

注意：

- `--thread here` 适用于私聊和飞书话题。
- 绑定私聊/话题中的后续消息直接路由到该 ACP 会话。
- v1 不针对通用的非话题群聊。

### 多代理路由

使用 `bindings` 将飞书私聊或群组路由到不同的代理。

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

- `match.channel`：`"feishu"`
- `match.peer.kind`：`"direct"` 或 `"group"`
- `match.peer.id`：用户 Open ID (`ou_xxx`) 或群组 ID (`oc_xxx`)

有关查找提示，请参阅 [获取群组/用户 ID](#get-groupuser-ids)。

---

## 配置参考

完整配置：[网关配置](/gateway/configuration)

关键选项：

| 设置                                           | 描述                             | 默认值          |
| ------------------------------------------------- | --------------------------------------- | ---------------- |
| `channels.feishu.enabled`                         | 启用/禁用频道                  | `true`           |
| `channels.feishu.domain`                          | API 域名 (`feishu` 或 `lark`)         | `feishu`         |
| `channels.feishu.connectionMode`                  | 事件传输模式                    | `websocket`      |
| `channels.feishu.defaultAccount`                  | 出站路由的默认账号 ID | `default`        |
| `channels.feishu.verificationToken`               | Webhook 模式必需               | -                |
| `channels.feishu.encryptKey`                      | Webhook 模式必需               | -                |
| `channels.feishu.webhookPath`                     | Webhook 路由路径                      | `/feishu/events` |
| `channels.feishu.webhookHost`                     | Webhook 绑定主机                       | `127.0.0.1`      |
| `channels.feishu.webhookPort`                     | Webhook 绑定端口                       | `3000`           |
| `channels.feishu.accounts.<id>.appId`             | 应用 ID                                  | -                |
| `channels.feishu.accounts.<id>.appSecret`         | 应用密钥                              | -                |
| `channels.feishu.accounts.<id>.domain`            | 每账号 API 域名覆盖         | `feishu`         |
| `channels.feishu.dmPolicy`                        | 私聊策略                               | `pairing`        |
| `channels.feishu.allowFrom`                       | 私聊白名单 (open_id 列表)             | -                |
| `channels.feishu.groupPolicy`                     | 群组策略                            | `allowlist`      |
| `channels.feishu.groupAllowFrom`                  | 群组白名单                         | -                |
| `channels.feishu.requireMention`                  | 默认需要 @提及                | 条件性      |
| `channels.feishu.groups.<chat_id>.requireMention` | 每群组需要 @提及 覆盖     | 继承        |
| `channels.feishu.groups.<chat_id>.enabled`        | 启用群组                            | `true`           |
| `channels.feishu.textChunkLimit`                  | 消息块大小                      | `2000`           |
| `channels.feishu.mediaMaxMb`                      | 媒体大小限制                        | `30`             |
| `channels.feishu.streaming`                       | 启用流式卡片输出            | `true`           |
| `channels.feishu.blockStreaming`                  | 启用块流式传输                  | `true`           |

---

## dmPolicy 参考

| 值         | 行为                                                        |
| ------------- | --------------------------------------------------------------- |
| `"pairing"`   | **默认。** 未知用户会获得配对码；必须批准 |
| `"allowlist"` | 仅 `allowFrom` 中的用户可以聊天                              |
| `"open"`      | 允许所有用户（需要在 allowFrom 中包含 `"*"`）                   |
| `"disabled"`  | 禁用私聊                                                     |

---

## 支持的消息类型

### 接收

- ✅ 文本
- ✅ 富文本 (帖子)
- ✅ 图片
- ✅ 文件
- ✅ 音频
- ✅ 视频/媒体
- ✅ 贴纸

### 发送

- ✅ 文本
- ✅ 图片
- ✅ 文件
- ✅ 音频
- ✅ 视频/媒体
- ✅ 互动卡片
- ⚠️ 富文本（帖子样式格式和卡片，不支持任意飞书创作功能）

### 线程和回复

- ✅ 内联回复
- ✅ 飞书暴露 `reply_in_thread` 的话题线程回复
- ✅ 回复线程/话题消息时，媒体回复保持线程感知

## 云文档评论

当有人在飞书云文档（文档、表格等）上添加评论时，飞书可以触发代理。代理接收评论文本、文档上下文和评论线程，以便在线程内回复或进行文档编辑。

要求：

- 在飞书应用事件订阅设置中订阅 `drive.notice.comment_add_v1`（与现有的 `im.message.receive_v1` 一起）
- Drive 工具默认启用；使用 `channels.feishu.tools.drive: false` 禁用

`feishu_drive` 工具提供以下评论操作：

| 操作                 | 描述                         |
| ---------------------- | ----------------------------------- |
| `list_comments`        | 列出文档上的评论         |
| `list_comment_replies` | 列出评论线程中的回复    |
| `add_comment`          | 添加新的顶级评论         |
| `reply_comment`        | 回复现有评论线程 |

当代理处理 Drive 评论事件时，它将接收：

- 评论文本和发送者
- 文档元数据（标题、类型、URL）
- 用于线程内回复的评论线程上下文

进行文档编辑后，代理将被引导使用 `feishu_drive.reply_comment` 通知评论者，然后输出确切的静默令牌 `NO_REPLY` / `no_reply` 以避免重复发送。

## 运行时操作面

飞书目前提供以下运行时操作：

- `send`
- `read`
- `edit`
- `thread-reply`
- `pin`
- `list-pins`
- `unpin`
- `member-info`
- `channel-info`
- `channel-list`
- 当配置中启用反应功能时的 `react` 和 `reactions`
- `feishu_drive` 评论操作：`list_comments`、`list_comment_replies`、`add_comment`、`reply_comment`

## 相关

- [通道概览](/channels) — 所有支持的通道
- [配对](/channels/pairing) — DM 认证和配对流程
- [群组](/channels/groups) — 群聊行为和提及限制
- [通道路由](/channels/channel-routing) — 消息会话路由
- [安全](/gateway/security) — 访问模型和加固