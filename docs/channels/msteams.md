---
summary: "Microsoft Teams bot support status, capabilities, and configuration"
read_when:
  - Working on MS Teams channel features
title: "Microsoft Teams"
---
# Microsoft Teams (plugin)

> "Abandon all hope, ye who enter here."

更新时间: 2026-01-21

状态: 支持文本和DM附件；发送频道/组文件需要 `sharePointSiteId` + Graph权限（参见[在群聊中发送文件](#sending-files-in-group-chats)）。投票通过自适应卡片发送。

## 需要插件

Microsoft Teams 作为插件提供，不包含在核心安装中。

**重大变更（2026.1.15）：** MS Teams 已移出核心。如果您使用它，必须安装插件。

可解释：保持核心安装更轻量，并允许 MS Teams 依赖项独立更新。

通过 CLI 安装（npm 仓库）：

```bash
openclaw plugins install @openclaw/msteams
```

本地检出（从 git 仓库运行时）：

```bash
openclaw plugins install ./extensions/msteams
```

如果您在配置/入职期间选择 Teams 并检测到 git 检出，
OpenClaw 将自动提供本地安装路径。

详情：[插件](/tools/plugin)

## 快速设置（初学者）

1. 安装 Microsoft Teams 插件。
2. 创建一个 **Azure Bot**（应用ID + 客户端密钥 + 租户ID）。
3. 使用这些凭据配置 OpenClaw。
4. 通过公共URL或隧道公开 `/api/messages`（默认端口3978）。
5. 安装 Teams 应用包并启动网关。

最小配置：

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      appPassword: "<APP_PASSWORD>",
      tenantId: "<TENANT_ID>",
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

注意：群聊默认被阻止 (`channels.msteams.groupPolicy: "allowlist"`)。要允许群聊回复，请设置 `channels.msteams.groupAllowFrom`（或使用 `groupPolicy: "open"` 允许任何成员，提及触发）。

## 目标

- 通过 Teams DM、群聊或频道与 OpenClaw 进行交流。
- 保持路由的确定性：回复总是回到收到消息的频道。
- 默认采用安全的频道行为（除非配置否则需要提及）。

## 配置写入

默认情况下，Microsoft Teams 允许由 `/config set|unset` 触发的配置更新写入（需要 `commands.config: true`）。

禁用方法：

```json5
{
  channels: { msteams: { configWrites: false } },
}
```

## 访问控制（DM + 群组）

**DM 访问**

- 默认：`channels.msteams.dmPolicy = "pairing"`。未知发送者在批准之前会被忽略。
- `channels.msteams.allowFrom` 接受 AAD 对象ID、UPN 或显示名称。向导在凭据允许的情况下通过 Microsoft Graph 解析名称为ID。

**群组访问**

- 默认: `channels.msteams.groupPolicy = "allowlist"` (除非你添加 `groupAllowFrom` 否则会被阻止). 使用 `channels.defaults.groupPolicy` 覆盖默认设置（当未设置时）。
- `channels.msteams.groupAllowFrom` 控制哪些发送者可以在群聊/频道中触发（回退到 `channels.msteams.allowFrom`）。
- 设置 `groupPolicy: "open"` 允许任何成员（默认情况下仍然需要提及）。
- 要允许 **无频道**，设置 `channels.msteams.groupPolicy: "disabled"`。

示例:

```json5
{
  channels: {
    msteams: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["user@org.com"],
    },
  },
}
```

**团队 + 频道白名单**

- 通过在 `channels.msteams.teams` 下列出团队和频道来限制组/频道回复。
- 键可以是团队ID或名称；频道键可以是对话ID或名称。
- 当 `groupPolicy="allowlist"` 和团队白名单存在时，仅接受列出的团队/频道（需要提及）。
- 配置向导接受 `Team/Channel` 条目并为您存储它们。
- 启动时，OpenClaw 将团队/频道和用户白名单名称解析为ID（当Graph权限允许时）
  并记录映射；无法解析的条目将保持原样。

示例:

```json5
{
  channels: {
    msteams: {
      groupPolicy: "allowlist",
      teams: {
        "My Team": {
          channels: {
            General: { requireMention: true },
          },
        },
      },
    },
  },
}
```

## 工作原理

1. 安装 Microsoft Teams 插件。
2. 创建一个 **Azure Bot**（应用ID + 密钥 + 租户ID）。
3. 构建一个 **Teams 应用包**，该包引用该机器人并包括以下RSC权限。
4. 将 Teams 应用上传/安装到一个团队（或个人范围用于直接消息）。
5. 在 `msteams` 中配置 `~/.openclaw/openclaw.json`（或环境变量）并启动网关。
6. 网关默认监听 `/api/messages` 上的 Bot Framework Webhook 流量。

## Azure Bot 设置（先决条件）

在配置 OpenClaw 之前，您需要创建一个 Azure Bot 资源。

### 步骤 1: 创建 Azure Bot

1. 前往 [创建 Azure Bot](https://portal.azure.com/#create/Microsoft.AzureBot)
2. 填写 **基本信息** 选项卡：

   | 字段              | 值                                                    |
   | ------------------ | -------------------------------------------------------- |
   | **机器人句柄**     | 您的机器人名称，例如 `openclaw-msteams`（必须唯一） |
   | **订阅**   | 选择您的 Azure 订阅                           |
   | **资源组** | 创建新组或使用现有组                               |
   | **定价层**   | **免费** 用于开发/测试                                 |
   | **应用类型**    | **单租户**（推荐 - 请参见下方说明）         |
   | **创建类型**  | **创建新的 Microsoft 应用ID**                          |

> **弃用通知:** 在 2025-07-31 之后，不再支持创建新的多租户机器人。对于新机器人，请使用 **单租户**。

3. 点击 **Review + create** → **Create** (等待约1-2分钟)

### 第2步：获取凭据

1. 转到你的Azure Bot资源 → **Configuration**
2. 复制 **Microsoft App ID** → 这是你的 `appId`
3. 点击 **Manage Password** → 跳转到应用注册
4. 在 **Certificates & secrets** 下 → **New client secret** → 复制 **Value** → 这是你的 `appPassword`
5. 转到 **Overview** → 复制 **Directory (tenant) ID** → 这是你的 `tenantId`

### 第3步：配置消息终结点

1. 在Azure Bot → **Configuration**
2. 将 **Messaging endpoint** 设置为你的webhook URL：
   - 生产环境: `https://your-domain.com/api/messages`
   - 本地开发: 使用隧道（见下方[本地开发](#local-development-tunneling)）

### 第4步：启用Teams通道

1. 在Azure Bot → **Channels**
2. 点击 **Microsoft Teams** → 配置 → 保存
3. 接受服务条款

## 本地开发（隧道）

Teams无法访问 `localhost`。使用隧道进行本地开发：

**选项A: ngrok**

```bash
ngrok http 3978
# Copy the https URL, e.g., https://abc123.ngrok.io
# Set messaging endpoint to: https://abc123.ngrok.io/api/messages
```

**选项B: Tailscale Funnel**

```bash
tailscale funnel 3978
# Use your Tailscale funnel URL as the messaging endpoint
```

## Teams开发者门户（替代方案）

与其手动创建manifest ZIP文件，你可以使用[Teams开发者门户](https://dev.teams.microsoft.com/apps)：

1. 点击 **+ 新建应用**
2. 填写基本信息（名称、描述、开发者信息）
3. 转到 **App features** → **Bot**
4. 选择 **手动输入bot ID** 并粘贴你的Azure Bot App ID
5. 勾选范围：**Personal**, **Team**, **Group Chat**
6. 点击 **Distribute** → **下载应用包**
7. 在Teams中: **Apps** → **管理你的应用** → **上传自定义应用** → 选择ZIP文件

这通常比手动编辑JSON manifest更简单。

## 测试机器人

**选项A: Azure Web Chat（先验证webhook）**

1. 在Azure门户 → 你的Azure Bot资源 → **Test in Web Chat**
2. 发送一条消息 - 你应该会看到回复
3. 这确认了在Teams设置之前你的webhook终结点正常工作

**选项B: Teams（应用安装后）**

1. 安装Teams应用（侧载或组织目录）
2. 在Teams中找到机器人并发送私信
3. 检查网关日志以查看传入活动

## 设置（最小文本仅）

1. **安装Microsoft Teams插件**
   - 从npm: `openclaw plugins install @openclaw/msteams`
   - 从本地检出: `openclaw plugins install ./extensions/msteams`

2. **机器人注册**
   - 创建一个Azure Bot（见上文）并记下：
     - App ID
     - 客户端密钥（应用密码）
     - 租户ID（单租户）

3. **Teams app manifest**
   - 包含一个 `bot` 条目，其中包含 `botId = <App ID>`。
   - 范围: `personal`, `team`, `groupChat`。
   - `supportsFiles: true`（个人范围文件处理所需）。
   - 添加 RSC 权限（如下所示）。
   - 创建图标: `outline.png` (32x32) 和 `color.png` (192x192)。
   - 将三个文件一起压缩: `manifest.json`, `outline.png`, `color.png`。

4. **Configure OpenClaw**

   ```json
   {
     "msteams": {
       "enabled": true,
       "appId": "<APP_ID>",
       "appPassword": "<APP_PASSWORD>",
       "tenantId": "<TENANT_ID>",
       "webhook": { "port": 3978, "path": "/api/messages" }
     }
   }
   ```

   你也可以使用环境变量而不是配置键：
   - `MSTEAMS_APP_ID`
   - `MSTEAMS_APP_PASSWORD`
   - `MSTEAMS_TENANT_ID`

5. **Bot endpoint**
   - 将 Azure Bot Messaging Endpoint 设置为：
     - `https://<host>:3978/api/messages`（或你选择的路径/端口）。

6. **运行网关**
   - 当插件安装并且存在带有凭据的 `msteams` 配置时，Teams 通道会自动启动。

## 历史上下文

- `channels.msteams.historyLimit` 控制最近多少条频道/组消息会被包含在提示中。
- 回退到 `messages.groupChat.historyLimit`。设置 `0` 以禁用（默认 50）。
- 可以使用 `channels.msteams.dmHistoryLimit` 限制 DM 历史记录（用户轮次）。每个用户的重写：`channels.msteams.dms["<user_id>"].historyLimit`。

## 当前 Teams RSC 权限（清单）

这些是我们 Teams 应用程序清单中的 **现有资源特定权限**。它们仅适用于安装应用程序的团队/聊天内部。

**对于频道（团队范围）：**

- `ChannelMessage.Read.Group` (Application) - 接收所有频道消息而无需 @ 提及
- `ChannelMessage.Send.Group` (Application)
- `Member.Read.Group` (Application)
- `Owner.Read.Group` (Application)
- `ChannelSettings.Read.Group` (Application)
- `TeamMember.Read.Group` (Application)
- `TeamSettings.Read.Group` (Application)

**对于群聊：**

- `ChatMessage.Read.Chat` (Application) - 接收所有群聊消息而无需 @ 提及

## 示例 Teams 清单（已删减）

包含必需字段的最小有效示例。替换 ID 和 URL。

```json
{
  "$schema": "https://developer.microsoft.com/en-us/json-schemas/teams/v1.23/MicrosoftTeams.schema.json",
  "manifestVersion": "1.23",
  "version": "1.0.0",
  "id": "00000000-0000-0000-0000-000000000000",
  "name": { "short": "OpenClaw" },
  "developer": {
    "name": "Your Org",
    "websiteUrl": "https://example.com",
    "privacyUrl": "https://example.com/privacy",
    "termsOfUseUrl": "https://example.com/terms"
  },
  "description": { "short": "OpenClaw in Teams", "full": "OpenClaw in Teams" },
  "icons": { "outline": "outline.png", "color": "color.png" },
  "accentColor": "#5B6DEF",
  "bots": [
    {
      "botId": "11111111-1111-1111-1111-111111111111",
      "scopes": ["personal", "team", "groupChat"],
      "isNotificationOnly": false,
      "supportsCalling": false,
      "supportsVideo": false,
      "supportsFiles": true
    }
  ],
  "webApplicationInfo": {
    "id": "11111111-1111-1111-1111-111111111111"
  },
  "authorization": {
    "permissions": {
      "resourceSpecific": [
        { "name": "ChannelMessage.Read.Group", "type": "Application" },
        { "name": "ChannelMessage.Send.Group", "type": "Application" },
        { "name": "Member.Read.Group", "type": "Application" },
        { "name": "Owner.Read.Group", "type": "Application" },
        { "name": "ChannelSettings.Read.Group", "type": "Application" },
        { "name": "TeamMember.Read.Group", "type": "Application" },
        { "name": "TeamSettings.Read.Group", "type": "Application" },
        { "name": "ChatMessage.Read.Chat", "type": "Application" }
      ]
    }
  }
}
```

### 清单注意事项（必需字段）

- `bots[].botId` **必须** 与 Azure Bot 应用程序 ID 匹配。
- `webApplicationInfo.id` **必须** 与 Azure Bot 应用程序 ID 匹配。
- `bots[].scopes` 必须包含您计划使用的表面 (`personal`, `team`, `groupChat`)。
- `bots[].supportsFiles: true` 在个人作用域中处理文件时是必需的。
- `authorization.permissions.resourceSpecific` 如果您希望处理频道流量，则必须包含频道读取/发送。

### 更新现有应用

要更新已安装的 Teams 应用程序（例如，添加 RSC 权限）：

1. 使用新设置更新您的 `manifest.json`
2. **递增 `version` 字段**（例如，`1.0.0` → `1.1.0`）
3. **重新压缩** 清单及其图标 (`manifest.json`, `outline.png`, `color.png`)
4. 上传新的 zip 文件：
   - **选项 A（Teams 管理中心）：** Teams 管理中心 → Teams 应用程序 → 管理应用程序 → 找到您的应用程序 → 上传新版本
   - **选项 B（侧载）：** 在 Teams 中 → 应用程序 → 管理您的应用程序 → 上传自定义应用程序
5. **对于团队频道：** 在每个团队中重新安装应用程序以使新权限生效
6. **完全退出并重新启动 Teams**（不仅仅是关闭窗口）以清除缓存的应用程序元数据

## 功能：仅 RSC 与 Graph

### 仅使用 **Teams RSC**（已安装应用，无 Graph API 权限）

工作：

- 读取频道消息的 **文本** 内容。
- 发送频道消息的 **文本** 内容。
- 接收 **个人（DM）** 文件附件。

不起作用的情况：

- 频道/组中的 **图像或文件内容**（负载仅包括HTML存根）。
- 下载存储在SharePoint/OneDrive中的附件。
- 读取消息历史记录（超出实时Webhook事件）。

### 使用 **Teams RSC + Microsoft Graph应用程序权限**

添加功能：

- 下载托管内容（粘贴到消息中的图像）。
- 下载存储在SharePoint/OneDrive中的文件附件。
- 通过Graph读取频道/聊天消息历史记录。

### RSC 与 Graph API

| 功能                | RSC权限          | Graph API                           |
| --------------------- | ------------------ | ----------------------------------- |
| **实时消息**        | 是（通过webhook）  | 否（仅轮询）                        |
| **历史消息**        | 否               | 是（可以查询历史记录）              |
| **设置复杂性**      | 仅应用清单       | 需要管理员同意 + 令牌流             |
| **离线工作**        | 否（必须运行）     | 是（随时查询）                      |

**总结：** RSC用于实时监听；Graph API用于历史访问。为了在离线时追上错过的消息，你需要Graph API和 `ChannelMessage.Read.All` （需要管理员同意）。

## 支持Graph的媒体和历史记录（频道所需）

如果你需要**频道**中的图像/文件或想要获取**消息历史记录**，必须启用Microsoft Graph权限并授予管理员同意。

1. 在Entra ID（Azure AD）**应用注册**中，添加Microsoft Graph **应用程序权限**：
   - `ChannelMessage.Read.All`（频道附件+历史记录）
   - `Chat.Read.All` 或 `ChatMessage.Read.All`（组聊天）
2. **授予租户管理员同意**。
3. 提升Teams应用**清单版本**，重新上传，并**在Teams中重新安装应用**。
4. **完全退出并重新启动Teams**以清除缓存的应用元数据。

**用户提及的附加权限：** 用户@提及对对话中的用户默认可用。但是，如果你想动态搜索并提及**不在当前对话**中的用户，添加 `User.Read.All` （应用程序）权限并授予管理员同意。

## 已知限制

### Webhook超时

Teams通过HTTP webhook传递消息。如果处理时间过长（例如，慢速LLM响应），你可能会看到：

- 网关超时
- Teams重试消息（导致重复）
- 丢失的回复

OpenClaw通过快速返回并主动发送回复来处理这种情况，但非常缓慢的响应仍可能导致问题。

### 格式化

Teams的markdown比Slack或Discord更有限：

- 基本格式可用：**粗体**，_斜体_，`code`，链接
- 复杂的markdown（表格、嵌套列表）可能无法正确渲染
- 支持自适应卡片用于投票和任意卡片发送（见下文）

## 配置

关键设置（有关共享频道模式，请参阅 `/gateway/configuration`）：

- `channels.msteams.enabled`: 启用/禁用通道。
- `channels.msteams.appId`, `channels.msteams.appPassword`, `channels.msteams.tenantId`: 机器人凭据。
- `channels.msteams.webhook.port` (默认 `3978`)
- `channels.msteams.webhook.path` (默认 `/api/messages`)
- `channels.msteams.dmPolicy`: `pairing | allowlist | open | disabled` (默认: pairing)
- `channels.msteams.allowFrom`: 直接消息的允许列表 (AAD 对象 ID、UPN 或显示名称)。向导在设置期间会解析名称为 ID，前提是可用 Graph 访问权限。
- `channels.msteams.textChunkLimit`: 出站文本块大小。
- `channels.msteams.chunkMode`: `length` (默认) 或 `newline` 在长度分块之前按空白行（段落边界）拆分。
- `channels.msteams.mediaAllowHosts`: 入站附件主机的允许列表（默认为 Microsoft/Teams 域）。
- `channels.msteams.mediaAuthAllowHosts`: 在媒体重试时附加 Authorization 头的允许列表（默认为 Graph + Bot Framework 主机）。
- `channels.msteams.requireMention`: 在频道/组中需要 @提及（默认 true）。
- `channels.msteams.replyStyle`: `thread | top-level` (参见 [回复样式](#reply-style-threads-vs-posts))。
- `channels.msteams.teams.<teamId>.replyStyle`: 每个团队的覆盖。
- `channels.msteams.teams.<teamId>.requireMention`: 每个团队的覆盖。
- `channels.msteams.teams.<teamId>.tools`: 默认每个团队的工具策略覆盖 (`allow`/`deny`/`alsoAllow`)，当通道覆盖缺失时使用。
- `channels.msteams.teams.<teamId>.toolsBySender`: 默认每个团队每个发送者的工具策略覆盖 (`"*"` 支持通配符)。
- `"*"`: 每个通道的覆盖。
- `channels.msteams.teams.<teamId>.channels.<conversationId>.replyStyle`: 每个通道的覆盖。
- `channels.msteams.teams.<teamId>.channels.<conversationId>.requireMention`: 每个通道的工具策略覆盖 (`channels.msteams.teams.<teamId>.channels.<conversationId>.tools`/`allow`/`deny`)。
- `channels.msteams.teams.<teamId>.channels.<conversationId>.tools`: 每个通道每个发送者的工具策略覆盖 (`alsoAllow` 支持通配符)。
- `channels.msteams.teams.<teamId>.channels.<conversationId>.toolsBySender`: 群聊/频道中的文件上传的 SharePoint 站点 ID (参见 [在群聊中发送文件](#sending-files-in-group-chats))。

## 路由与会话

- 会话密钥遵循标准代理格式 (参见 [/concepts/session](/concepts/session))：
  - 直接消息共享主会话 (`agent:<agentId>:<mainKey>`)。
  - 频道/组消息使用对话 ID：
    - `agent:<agentId>:msteams:channel:<conversationId>`
    - `agent:<agentId>:msteams:group:<conversationId>`

## 回复样式：线程与帖子

Teams 最近引入了两种基于相同底层数据模型的频道用户界面样式：

| 样式                    | 描述                                               | 推荐 `replyStyle` |
| ------------------------ | --------------------------------------------------------- | ------------------------ |
| **帖子** (经典)      | 消息以卡片形式出现，下方有线程回复 | `thread` (默认)       |
| **线程** (类似Slack) | 消息线性流动，更像Slack                   | `top-level`              |

**问题:** Teams API 不会暴露频道使用的UI样式。如果您使用错误的 `replyStyle`:

- `thread` 在线程样式的频道中 → 回复会以奇怪的方式嵌套
- `top-level` 在帖子样式的频道中 → 回复会作为单独的顶级帖子出现而不是在线程中

**解决方案:** 根据频道设置为每个频道配置 `replyStyle`:

```json
{
  "msteams": {
    "replyStyle": "thread",
    "teams": {
      "19:abc...@thread.tacv2": {
        "channels": {
          "19:xyz...@thread.tacv2": {
            "replyStyle": "top-level"
          }
        }
      }
    }
  }
}
```

## 附件和图片

**当前限制:**

- **直接消息:** 图片和文件附件通过Teams机器人文件API工作。
- **频道/组:** 附件存储在M365存储（SharePoint/OneDrive）中。Webhook负载仅包括HTML存根，而不是实际文件字节。**需要Graph API权限**才能下载频道附件。

没有Graph权限，带有图片的频道消息将仅以文本形式接收（机器人无法访问图片内容）。
默认情况下，OpenClaw仅从Microsoft/Teams主机名下载媒体。使用 `channels.msteams.mediaAllowHosts` 覆盖（使用 `["*"]` 允许任何主机）。
仅为主机 `channels.msteams.mediaAuthAllowHosts` 附加授权头（默认为Graph + 机器人框架主机）。保持此列表严格（避免多租户后缀）。

## 在群聊中发送文件

机器人可以使用FileConsentCard流程（内置）在直接消息中发送文件。然而，**在群聊/频道中发送文件**需要额外设置：

| 上下文                  | 文件如何发送                           | 需要的设置                                    |
| ------------------------ | -------------------------------------------- | ----------------------------------------------- |
| **直接消息**                  | FileConsentCard → 用户接受 → 机器人上传 | 开箱即用                            |
| **群聊/频道** | 上传到SharePoint → 分享链接            | 需要 `sharePointSiteId` + Graph权限 |
| **图片（任何上下文）** | 内联Base64编码                        | 开箱即用                            |

### 为什么群聊需要SharePoint

机器人没有个人的OneDrive驱动器（`/me/drive` Graph API端点对应用程序标识符不起作用）。要在群聊/频道中发送文件，机器人会上传到一个**SharePoint站点**并创建一个共享链接。

### 设置

1. **在Entra ID (Azure AD) → 应用注册中添加Graph API权限：**
   - `Sites.ReadWrite.All` (应用程序) - 上传文件到SharePoint
   - `Chat.Read.All` (应用程序) - 可选，启用按用户共享链接

2. **授予租户管理员同意。**

3. **获取您的SharePoint站点ID：**

   ```bash
   # Via Graph Explorer or curl with a valid token:
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/{hostname}:/{site-path}"

   # Example: for a site at "contoso.sharepoint.com/sites/BotFiles"
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com:/sites/BotFiles"

   # Response includes: "id": "contoso.sharepoint.com,guid1,guid2"
   ```

4. **配置OpenClaw：**

   ```json5
   {
     channels: {
       msteams: {
         // ... other config ...
         sharePointSiteId: "contoso.sharepoint.com,guid1,guid2",
       },
     },
   }
   ```

### 共享行为

| 权限                              | 共享行为                                          |
| --------------------------------------- | --------------------------------------------------------- |
| 仅`Sites.ReadWrite.All`              | 组织范围内的共享链接（组织中的任何人都可以访问） |
| `Sites.ReadWrite.All` + `Chat.Read.All` | 按用户共享链接（只有聊天成员可以访问）      |

按用户共享更安全，因为只有聊天参与者才能访问文件。如果缺少`Chat.Read.All`权限，机器人将回退到组织范围内的共享。

### 回退行为

| 场景                                          | 结果                                             |
| ------------------------------------------------- | -------------------------------------------------- |
| 群聊 + 文件 + 配置了`sharePointSiteId` | 上传到SharePoint，发送共享链接            |
| 群聊 + 文件 + 未配置`sharePointSiteId`         | 尝试OneDrive上传（可能失败），仅发送文本 |
| 个人聊天 + 文件                              | FileConsentCard流程（无需SharePoint）    |
| 任何上下文 + 图像                               | Base64编码的内联（无需SharePoint）   |

### 存储文件的位置

上传的文件存储在配置的SharePoint站点默认文档库中的`/OpenClawShared/`文件夹中。

## 投票 (自适应卡片)

OpenClaw通过自适应卡片发送Teams投票（没有原生Teams投票API）。

- CLI: `openclaw message poll --channel msteams --target conversation:<id> ...`
- 投票由网关在`~/.openclaw/msteams-polls.json`记录。
- 网关必须在线以记录投票。
- 目前投票不会自动发布结果摘要（如有需要，请检查存储文件）。

## 自适应卡片 (任意)

使用`message`工具或CLI向Teams用户或对话发送任何自适应卡片JSON。

`card` 参数接受一个 Adaptive Card JSON 对象。当提供 `card` 时，消息文本是可选的。

**代理工具：**

```json
{
  "action": "send",
  "channel": "msteams",
  "target": "user:<id>",
  "card": {
    "type": "AdaptiveCard",
    "version": "1.5",
    "body": [{ "type": "TextBlock", "text": "Hello!" }]
  }
}
```

**CLI：**

```bash
openclaw message send --channel msteams \
  --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello!"}]}'
```

有关卡片架构和示例，请参阅 [Adaptive Cards 文档](https://adaptivecards.io/)。有关目标格式的详细信息，请参阅下面的 [目标格式](#target-formats)。

## 目标格式

MSTeams 目标使用前缀来区分用户和对话：

| 目标类型         | 格式                           | 示例                                             |
| ------------------- | -------------------------------- | --------------------------------------------------- |
| 用户（按ID）        | `user:<aad-object-id>`           | `user:40a1a0ed-4ff2-4164-a219-55518990c197`         |
| 用户（按名称）      | `user:<display-name>`            | `user:John Smith` (需要 Graph API)              |
| 组/频道       | `conversation:<conversation-id>` | `conversation:19:abc123...@thread.tacv2`            |
| 组/频道（原始） | `<conversation-id>`              | `19:abc123...@thread.tacv2` (如果包含 `@thread`) |

**CLI 示例：**

```bash
# Send to a user by ID
openclaw message send --channel msteams --target "user:40a1a0ed-..." --message "Hello"

# Send to a user by display name (triggers Graph API lookup)
openclaw message send --channel msteams --target "user:John Smith" --message "Hello"

# Send to a group chat or channel
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" --message "Hello"

# Send an Adaptive Card to a conversation
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello"}]}'
```

**代理工具示例：**

```json
{
  "action": "send",
  "channel": "msteams",
  "target": "user:John Smith",
  "message": "Hello!"
}
```

```json
{
  "action": "send",
  "channel": "msteams",
  "target": "conversation:19:abc...@thread.tacv2",
  "card": {
    "type": "AdaptiveCard",
    "version": "1.5",
    "body": [{ "type": "TextBlock", "text": "Hello" }]
  }
}
```

注意：没有 `user:` 前缀，名称默认为组/团队解析。始终在通过显示名称定位人员时使用 `user:`。

## 主动消息

- 主动消息仅在用户交互 **之后** 才可能，因为我们在该点存储对话引用。
- 有关 `/gateway/configuration` 的 `dmPolicy` 和允许列表门控，请参阅 `/gateway/configuration`。

## 团队和频道 ID（常见问题）

`groupId` 查询参数在 Teams URL 中**不是**用于配置的团队ID。请从URL路径中提取ID：

**团队URL:**

```
https://teams.microsoft.com/l/team/19%3ABk4j...%40thread.tacv2/conversations?groupId=...
                                    └────────────────────────────┘
                                    Team ID (URL-decode this)
```

**频道URL:**

```
https://teams.microsoft.com/l/channel/19%3A15bc...%40thread.tacv2/ChannelName?groupId=...
                                      └─────────────────────────┘
                                      Channel ID (URL-decode this)
```

**用于配置:**

- 团队ID = `/team/` 之后的路径段（URL解码，例如 `19:Bk4j...@thread.tacv2`）
- 频道ID = `/channel/` 之后的路径段（URL解码）
- **忽略** `groupId` 查询参数

## 私有频道

机器人在私有频道中的支持有限：

| 功能                      | 标准频道 | 私有频道       |
| ---------------------------- | ----------------- | ---------------------- |
| 机器人安装             | 是               | 有限                |
| 实时消息（Webhook） | 是               | 可能无法工作           |
| RSC权限              | 是               | 可能表现不同 |
| @提及                    | 是               | 如果机器人可访问   |
| Graph API历史            | 是               | 是（需权限） |

**如果私有频道不起作用的解决方法:**

1. 使用标准频道进行机器人交互
2. 使用DM - 用户可以随时直接向机器人发送消息
3. 使用Graph API进行历史访问（需要 `ChannelMessage.Read.All`）

## 故障排除

### 常见问题

- **频道中图像不显示:** 缺少Graph权限或管理员同意。重新安装Teams应用程序并完全退出/重新打开Teams。
- **频道中无响应:** 默认情况下需要提及；设置 `channels.msteams.requireMention=false` 或按团队/频道配置。
- **版本不匹配（Teams仍显示旧清单）:** 删除并重新添加应用程序，然后完全退出Teams以刷新。
- **来自Webhook的401未授权:** 手动测试时没有Azure JWT时预期会出现 - 意味着端点可达但身份验证失败。使用Azure Web Chat进行正确测试。

### 清单上传错误

- **"图标文件不能为空":** 清单引用了大小为0字节的图标文件。创建有效的PNG图标（`outline.png` 的32x32，`color.png` 的192x192）。
- **"webApplicationInfo.Id已被使用":** 该应用程序仍在另一个团队/聊天中安装。首先找到并卸载它，或者等待5-10分钟以进行传播。
- **上传时出现“出错”:** 通过 [https://admin.teams.microsoft.com](https://admin.teams.microsoft.com) 上传，打开浏览器DevTools（F12）→ 网络选项卡，并检查响应体以获取实际错误。
- **侧加载失败:** 尝试“上传应用程序到组织的应用程序目录”而不是“上传自定义应用程序” - 这通常会绕过侧加载限制。

### RSC 权限不起作用

1. 验证 `webApplicationInfo.id` 是否与机器人的 App ID 完全匹配
2. 重新上传应用程序并在团队/聊天中重新安装
3. 检查您的组织管理员是否已阻止 RSC 权限
4. 确认您使用了正确的范围：`ChannelMessage.Read.Group` 用于团队，`ChatMessage.Read.Chat` 用于群聊

## 参考资料

- [创建 Azure Bot](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-quickstart-registration) - Azure Bot 设置指南
- [Teams 开发者门户](https://dev.teams.microsoft.com/apps) - 创建/管理 Teams 应用程序
- [Teams 应用程序清单架构](https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema)
- [使用 RSC 接收频道消息](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/channel-messages-with-rsc)
- [RSC 权限参考](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/rsc/resource-specific-consent)
- [Teams 机器人文件处理](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/bots-filesv4)（频道/群聊需要 Graph）
- [主动消息](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/send-proactive-messages)