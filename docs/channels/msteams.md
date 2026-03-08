---
summary: "Microsoft Teams bot support status, capabilities, and configuration"
read_when:
  - Working on MS Teams channel features
title: "Microsoft Teams"
---
# Microsoft Teams (插件)

> “进入此地者，放弃一切希望。”

更新时间：2026-01-21

状态：支持文本 + 私信附件；频道/群组文件发送需要 `sharePointSiteId` + Graph 权限（参见 [在群组聊天中发送文件](#sending-files-in-group-chats)）。投票通过 Adaptive Cards 发送。

## 需要插件

Microsoft Teams 作为插件提供，不包含在核心安装中。

**重大变更 (2026.1.15)：** MS Teams 已移出核心。如果您使用它，必须安装插件。

说明：保持核心安装更轻量，并允许 MS Teams 依赖项独立更新。

通过 CLI 安装 (npm registry)：

```bash
openclaw plugins install @openclaw/msteams
```

本地 checkout (当从 git repo 运行时)：

```bash
openclaw plugins install ./extensions/msteams
```

如果在配置/入职期间选择 Teams 且检测到 git checkout，
OpenClaw 将自动提供本地安装路径。

详情：[插件](/tools/plugin)

## 快速设置（初学者）

1. 安装 Microsoft Teams 插件。
2. 创建一个 **Azure Bot** (App ID + client secret + tenant ID)。
3. 使用这些凭据配置 OpenClaw。
4. 通过公共 URL 或隧道暴露 `/api/messages` (默认为端口 3978)。
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

注意：群组聊天默认被阻止 (`channels.msteams.groupPolicy: "allowlist"`)。要允许群组回复，设置 `channels.msteams.groupAllowFrom` (或使用 `groupPolicy: "open"` 允许任何成员，需提及)。

## 目标

- 通过 Teams 私信、群组聊天或频道与 OpenClaw 交谈。
- 保持路由确定性：回复始终返回到它们到达的频道。
- 默认为安全频道行为（除非另有配置，否则需要提及）。

## 配置写入

默认情况下，允许 Microsoft Teams 写入由 `/config set|unset` 触发的配置更新（需要 `commands.config: true`）。

禁用方式：

```json5
{
  channels: { msteams: { configWrites: false } },
}
```

## 访问控制 (私信 + 群组)

**私信访问**

- 默认：`channels.msteams.dmPolicy = "pairing"`。未知发送者将被忽略直到获批。
- `channels.msteams.allowFrom` 应使用稳定的 AAD object IDs。
- UPNs/显示名称是可变的；默认禁用直接匹配，仅在使用 `channels.msteams.dangerouslyAllowNameMatching: true` 时启用。
- 当凭据允许时，向导可以通过 Microsoft Graph 将名称解析为 IDs。

**群组访问**

- 默认：`channels.msteams.groupPolicy = "allowlist"` (被阻止，除非您添加 `groupAllowFrom`)。当未设置时使用 `channels.defaults.groupPolicy` 覆盖默认值。
- `channels.msteams.groupAllowFrom` 控制哪些发送者可以在群组聊天/频道中触发 (回退到 `channels.msteams.allowFrom`)。
- 设置 `groupPolicy: "open"` 以允许任何成员 (默认仍需提及)。
- 要允许 **无频道**，设置 `channels.msteams.groupPolicy: "disabled"`。

示例：

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

**Teams + 频道允许列表**

- 通过在 `channels.msteams.teams` 下列出 teams 和 channels 来限定群组/频道回复范围。
- Keys 可以是 team IDs 或 names；channel keys 可以是 conversation IDs 或 names。
- 当 `groupPolicy="allowlist"` 且存在 teams allowlist 时，仅接受列出的 teams/channels (需提及)。
- 配置向导接受 `Team/Channel` 条目并为您存储。
- 启动时，OpenClaw 将 team/channel 和 user allowlist 名称解析为 IDs (当 Graph 权限允许时) 并记录映射；未解析的条目保持原样。

示例：

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
2. 创建一个 **Azure Bot** (App ID + secret + tenant ID)。
3. 构建一个 **Teams app package**，引用 bot 并包含下面的 RSC 权限。
4. 将 Teams app 上传/安装到 team (或用于私信的 personal scope)。
5. 在 `~/.openclaw/openclaw.json` (或 env vars) 中配置 `msteams` 并启动网关。
6. 网关默认在 `/api/messages` 上监听 Bot Framework webhook 流量。

## Azure Bot 设置 (先决条件)

在配置 OpenClaw 之前，您需要创建一个 Azure Bot 资源。

### 步骤 1：创建 Azure Bot

1. 前往 [Create Azure Bot](https://portal.azure.com/#create/Microsoft.AzureBot)
2. 填写 **Basics** 选项卡：

   | 字段              | 值                                                    |
   | ------------------ | -------------------------------------------------------- |
   | **Bot handle**     | 您的 bot 名称，例如 `openclaw-msteams` (必须唯一) |
   | **Subscription**   | 选择您的 Azure subscription                           |
   | **Resource group** | 创建新的或使用现有的                               |
   | **Pricing tier**   | **Free** 用于开发/测试                                 |
   | **Type of App**    | **Single Tenant** (推荐 - 见下方注意)         |
   | **Creation type**  | **Create new Microsoft App ID**                          |

> **弃用通知：** 创建新的 multi-tenant bots 已在 2025-07-31 后弃用。新 bots 请使用 **Single Tenant**。

3. 点击 **Review + create** → **Create** (等待 ~1-2 分钟)

### 步骤 2：获取凭据

1. 前往您的 Azure Bot 资源 → **Configuration**
2. 复制 **Microsoft App ID** → 这是您的 `appId`
3. 点击 **Manage Password** → 前往 App Registration
4. 在 **Certificates & secrets** 下 → **New client secret** → 复制 **Value** → 这是您的 `appPassword`
5. 前往 **Overview** → 复制 **Directory (tenant) ID** → 这是您的 `tenantId`

### 步骤 3：配置 Messaging Endpoint

1. 在 Azure Bot → **Configuration**
2. 设置 **Messaging endpoint** 为您的 webhook URL：
   - 生产环境：`https://your-domain.com/api/messages`
   - 本地开发：使用隧道 (见下方 [Local Development](#local-development-tunneling))

### 步骤 4：启用 Teams Channel

1. 在 Azure Bot → **Channels**
2. 点击 **Microsoft Teams** → Configure → Save
3. 接受服务条款

## 本地开发 (隧道)

Teams 无法 reach `localhost`。本地开发请使用隧道：

**选项 A: ngrok**

```bash
ngrok http 3978
# Copy the https URL, e.g., https://abc123.ngrok.io
# Set messaging endpoint to: https://abc123.ngrok.io/api/messages
```

**选项 B: Tailscale Funnel**

```bash
tailscale funnel 3978
# Use your Tailscale funnel URL as the messaging endpoint
```

## Teams Developer Portal (替代方案)

您可以使用 [Teams Developer Portal](https://dev.teams.microsoft.com/apps) 而不是手动创建 manifest ZIP：

1. 点击 **+ New app**
2. 填写基本信息 (name, description, developer info)
3. 前往 **App features** → **Bot**
4. 选择 **Enter a bot ID manually** 并粘贴您的 Azure Bot App ID
5. 勾选 scopes: **Personal**, **Team**, **Group Chat**
6. 点击 **Distribute** → **Download app package**
7. 在 Teams 中：**Apps** → **Manage your apps** → **Upload a custom app** → 选择 ZIP

这通常比手动编辑 JSON manifests 更容易。

## 测试 Bot

**选项 A: Azure Web Chat (首先验证 webhook)**

1. 在 Azure Portal → 您的 Azure Bot 资源 → **Test in Web Chat**
2. 发送消息 - 您应该看到响应
3. 这在 Teams 设置之前确认您的 webhook endpoint 有效

**选项 B: Teams (应用安装后)**

1. 安装 Teams app (sideload 或 org catalog)
2. 在 Teams 中找到 bot 并发送私信
3. 检查 gateway logs 以查看传入活动

## 设置 (最小化仅文本)

1. **安装 Microsoft Teams 插件**
   - 来自 npm: `openclaw plugins install @openclaw/msteams`
   - 来自本地 checkout: `openclaw plugins install ./extensions/msteams`

2. **Bot 注册**
   - 创建一个 Azure Bot (见上文) 并注意：
     - App ID
     - Client secret (App password)
     - Tenant ID (single-tenant)

3. **Teams app manifest**
   - 包含一个带有 `botId = <App ID>` 的 `bot` 条目。
   - Scopes: `personal`, `team`, `groupChat`。
   - `supportsFiles: true` (personal scope 文件处理所需)。
   - 添加 RSC 权限 (如下)。
   - 创建图标：`outline.png` (32x32) 和 `color.png` (192x192)。
   - 将所有三个文件打包：`manifest.json`, `outline.png`, `color.png`。

4. **配置 OpenClaw**

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

   您也可以使用环境变量代替 config keys：
   - `MSTEAMS_APP_ID`
   - `MSTEAMS_APP_PASSWORD`
   - `MSTEAMS_TENANT_ID`

5. **Bot endpoint**
   - 设置 Azure Bot Messaging Endpoint 为：
     - `https://<host>:3978/api/messages` (或您选择的路径/端口)。

6. **运行网关**
   - 当插件已安装且存在带有凭据的 `msteams` 配置时，Teams channel 自动启动。

## 历史记录上下文

- `channels.msteams.historyLimit` 控制多少最近的 channel/group 消息被包装到 prompt 中。
- 回退到 `messages.groupChat.historyLimit`。设置 `0` 以禁用 (默认 50)。
- DM 历史记录可以用 `channels.msteams.dmHistoryLimit` 限制 (user turns)。每用户覆盖：`channels.msteams.dms["<user_id>"].historyLimit`。

## 当前 Teams RSC 权限 (Manifest)

这些是我们 Teams app manifest 中的 **现有 resourceSpecific 权限**。它们仅适用于安装应用的 team/chat 内部。

**对于 channels (team scope):**

- `ChannelMessage.Read.Group` (Application) - 接收所有频道消息，无需 @ 提及
- `ChannelMessage.Send.Group` (Application)
- `Member.Read.Group` (Application)
- `Owner.Read.Group` (Application)
- `ChannelSettings.Read.Group` (Application)
- `TeamMember.Read.Group` (Application)
- `TeamSettings.Read.Group` (Application)

**对于群聊：**

- `ChatMessage.Read.Chat` (Application) - 接收所有群聊消息，无需 @ 提及

## Teams 清单示例（已脱敏）

包含所需字段的极简有效示例。请替换 ID 和 URL。

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

### 清单注意事项（必填字段）

- `bots[].botId` **必须** 与 Azure Bot App ID 匹配。
- `webApplicationInfo.id` **必须** 与 Azure Bot App ID 匹配。
- `bots[].scopes` 必须包含您计划使用的平台 (`personal`, `team`, `groupChat`)。
- `bots[].supportsFiles: true` 用于个人范围内的文件处理。
- `authorization.permissions.resourceSpecific` 若需频道流量，必须包含频道读取/发送权限。

### 更新现有应用

要更新已安装的 Teams 应用（例如添加 RSC 权限）：

1. 使用新设置更新您的 `manifest.json`
2. **增加 `version` 字段**（例如：`1.0.0` → `1.1.0`）
3. **重新压缩** 包含图标的清单 (`manifest.json`, `outline.png`, `color.png`)
4. 上传新的 zip 包：
   - **选项 A（Teams 管理中心）：** Teams 管理中心 → Teams 应用 → 管理应用 → 查找您的应用 → 上传新版本
   - **选项 B（侧载）：** 在 Teams 中 → 应用 → 管理您的应用 → 上传自定义应用
5. **对于团队频道：** 在每个团队中重新安装应用以使新权限生效
6. **完全退出并重新启动 Teams**（不仅仅是关闭窗口）以清除缓存的应用元数据

## 功能：仅 RSC 与 Graph

### 使用 **仅 Teams RSC**（已安装应用，无 Graph API 权限）

支持：

- 读取频道消息的 **文本** 内容。
- 发送频道消息的 **文本** 内容。
- 接收 **个人（DM）** 文件附件。

不支持：

- 频道/群组的 **图片或文件内容**（负载仅包含 HTML 存根）。
- 下载存储在 SharePoint/OneDrive 中的附件。
- 读取消息历史记录（超出实时 webhook 事件）。

### 使用 **Teams RSC + Microsoft Graph 应用程序权限**

新增：

- 下载托管内容（粘贴到消息中的图片）。
- 下载存储在 SharePoint/OneDrive 中的文件附件。
- 通过 Graph 读取频道/聊天消息历史记录。

### RSC 与 Graph API

| 功能                | RSC 权限             | Graph API                           |
| ------------------- | -------------------- | ----------------------------------- |
| **实时消息**        | 是（通过 webhook）   | 否（仅轮询）                        |
| **历史消息**        | 否                   | 是（可查询历史记录）                |
| **设置复杂度**      | 仅需应用清单         | 需要管理员同意 + 令牌流             |
| **离线工作**        | 否（必须正在运行）   | 是（随时查询）                      |

**结论：** RSC 用于实时监听；Graph API 用于历史访问。若要离线时补发错过的消息，您需要带有 `ChannelMessage.Read.All` 的 Graph API（需要管理员同意）。

## 启用 Graph 的媒体 + 历史记录（频道必需）

如果您需要在 **频道** 中使用图片/文件或想要获取 **消息历史记录**，则必须启用 Microsoft Graph 权限并授予管理员同意。

1. 在 Entra ID (Azure AD) **应用注册** 中，添加 Microsoft Graph **应用程序权限**：
   - `ChannelMessage.Read.All`（频道附件 + 历史记录）
   - `Chat.Read.All` 或 `ChatMessage.Read.All`（群聊）
2. 为租户 **授予管理员同意**。
3. 提升 Teams 应用 **清单版本**，重新上传，并在 Teams 中 **重新安装应用**。
4. **完全退出并重新启动 Teams** 以清除缓存的应用元数据。

**用户提及的额外权限：** 对话中的用户 @ 提及开箱即用。但是，如果您想动态搜索并提及 **不在当前对话中** 的用户，请添加 `User.Read.All` (Application) 权限并授予管理员同意。

## 已知限制

### Webhook 超时

Teams 通过 HTTP webhook 传递消息。如果处理时间过长（例如 LLM 响应慢），您可能会看到：

- 网关超时
- Teams 重试消息（导致重复）
- 回复丢失

OpenClaw 通过快速返回并主动发送回复来处理此问题，但非常慢的响应仍可能导致问题。

### 格式

Teams markdown 比 Slack 或 Discord 更有限：

- 基本格式有效：**粗体**，_斜体_，`code`，链接
- 复杂 markdown（表格、嵌套列表）可能无法正确渲染
- 支持自适应卡片用于投票和任意卡片发送（见下文）

## 配置

关键设置（共享频道模式请参阅 `/gateway/configuration`）：

- `channels.msteams.enabled`: 启用/禁用频道。
- `channels.msteams.appId`, `channels.msteams.appPassword`, `channels.msteams.tenantId`: 机器人凭据。
- `channels.msteams.webhook.port`（默认 `3978`）
- `channels.msteams.webhook.path`（默认 `/api/messages`）
- `channels.msteams.dmPolicy`: `pairing | allowlist | open | disabled`（默认：配对）
- `channels.msteams.allowFrom`: DM 白名单（推荐 AAD 对象 ID）。当可用 Graph 访问时，向导在设置期间将名称解析为 ID。
- `channels.msteams.dangerouslyAllowNameMatching`: 紧急修复开关，用于重新启用可变的 UPN/显示名称匹配。
- `channels.msteams.textChunkLimit`: 出站文本块大小。
- `channels.msteams.chunkMode`: `length`（默认）或 `newline` 以便在长度分块前按空行（段落边界）拆分。
- `channels.msteams.mediaAllowHosts`: 入站附件主机白名单（默认为 Microsoft/Teams 域名）。
- `channels.msteams.mediaAuthAllowHosts`: 媒体重试时附加 Authorization 头的白名单（默认为 Graph + Bot Framework 主机）。
- `channels.msteams.requireMention`: 频道/群组中要求 @ 提及（默认 true）。
- `channels.msteams.replyStyle`: `thread | top-level`（参见 [回复样式](#reply-style-threads-vs-posts)）。
- `channels.msteams.teams.<teamId>.replyStyle`: 每团队覆盖。
- `channels.msteams.teams.<teamId>.requireMention`: 每团队覆盖。
- `channels.msteams.teams.<teamId>.tools`: 默认每团队工具策略覆盖（`allow`/`deny`/`alsoAllow`），在缺少频道覆盖时使用。
- `channels.msteams.teams.<teamId>.toolsBySender`: 默认每团队每发送者工具策略覆盖（支持 `"*"` 通配符）。
- `channels.msteams.teams.<teamId>.channels.<conversationId>.replyStyle`: 每频道覆盖。
- `channels.msteams.teams.<teamId>.channels.<conversationId>.requireMention`: 每频道覆盖。
- `channels.msteams.teams.<teamId>.channels.<conversationId>.tools`: 每频道工具策略覆盖（`allow`/`deny`/`alsoAllow`）。
- `channels.msteams.teams.<teamId>.channels.<conversationId>.toolsBySender`: 每频道每发送者工具策略覆盖（支持 `"*"` 通配符）。
- `toolsBySender` 键应使用显式前缀：
  `id:`, `e164:`, `username:`, `name:`（遗留无前缀键仍仅映射到 `id:`）。
- `channels.msteams.sharePointSiteId`: 群聊/频道中文件上传的 SharePoint 站点 ID（参见 [在群聊中发送文件](#sending-files-in-group-chats)）。

## 路由与会话

- 会话密钥遵循标准代理格式（参见 [/concepts/session](/concepts/session)）：
  - 直接消息共享主会话 (`agent:<agentId>:<mainKey>`)。
  - 频道/群组消息使用对话 ID：
    - `agent:<agentId>:msteams:channel:<conversationId>`
    - `agent:<agentId>:msteams:group:<conversationId>`

## 回复样式：线程与帖子

Teams 最近在同一底层数据模型上引入了两种频道 UI 样式：

| 样式                     | 描述                                                  | 推荐 `replyStyle` |
| ------------------------ | ----------------------------------------------------- | ---------------------- |
| **帖子**（经典）         | 消息显示为带下方回复线程的卡片                        | `thread`（默认）       |
| **线程**（类 Slack）     | 消息线性流动，更像 Slack                              | `top-level`              |

**问题：** Teams API 不暴露频道使用的 UI 样式。如果您使用了错误的 `replyStyle`：

- ``thread`` 在 Threads 样式频道中 → 回复会显得嵌套不自然
- ``top-level`` 在 Posts 样式频道中 → 回复显示为独立的顶级帖子，而不是线程内的回复

**解决方案：** 根据频道的设置方式，按频道配置 ``replyStyle``：

````json
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
````

## 附件与图片

**当前限制：**

- **DM：** 图片和文件附件通过 Teams 机器人文件 API 工作。
- **频道/群组：** 附件存储在 M365 存储中（SharePoint/OneDrive）。Webhook 负载仅包含 HTML 存根，不包含实际文件字节。**需要 Graph API 权限**才能下载频道附件。

如果没有 Graph 权限，带有图片的频道消息将仅作为文本接收（机器人无法访问图像内容）。
默认情况下，OpenClaw 仅从 Microsoft/Teams 主机名下载媒体。使用 ``channels.msteams.mediaAllowHosts`` 覆盖（使用 ``["*"]`` 允许任何主机）。
授权标头仅附加给 ``channels.msteams.mediaAuthAllowHosts`` 中的主机（默认为 Graph + Bot Framework 主机）。保持此列表严格（避免多租户后缀）。

## 在群聊中发送文件

机器人可以使用 FileConsentCard 流程（内置）在 DM 中发送文件。但是，**在群聊/频道中发送文件**需要额外的设置：

| 上下文 | 文件发送方式 | 所需设置 |
| :--- | :--- | :--- |
| **DM** | FileConsentCard → 用户接受 → 机器人上传 | 开箱即用 |
| **群聊/频道** | 上传到 SharePoint → 分享链接 | 需要 ``sharePointSiteId`` + Graph 权限 |
| **图片（任何上下文）** | Base64 编码内联 | 开箱即用 |

### 为什么群聊需要 SharePoint

机器人没有个人 OneDrive 驱动器（``/me/drive`` Graph API 端点不适用于应用程序身份）。要在群聊/频道中发送文件，机器人需上传到 **SharePoint 站点**并创建共享链接。

### 设置

1. **添加 Graph API 权限** 在 Entra ID (Azure AD) → 应用注册：
   - ``Sites.ReadWrite.All`` (Application) - 上传文件到 SharePoint
   - ``Chat.Read.All`` (Application) - 可选，启用按用户共享链接

2. **授予租户的管理员同意**。

3. **获取您的 SharePoint 站点 ID：**

   ````bash
   # Via Graph Explorer or curl with a valid token:
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/{hostname}:/{site-path}"

   # Example: for a site at "contoso.sharepoint.com/sites/BotFiles"
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com:/sites/BotFiles"

   # Response includes: "id": "contoso.sharepoint.com,guid1,guid2"
   ````

4. **配置 OpenClaw：**

   ````json5
   {
     channels: {
       msteams: {
         // ... other config ...
         sharePointSiteId: "contoso.sharepoint.com,guid1,guid2",
       },
     },
   }
   ````

### 共享行为

| 权限 | 共享行为 |
| :--- | :--- |
| ``Sites.ReadWrite.All`` 仅限 | 组织范围共享链接（组织中任何人都可访问） |
| ``Sites.ReadWrite.All`` + ``Chat.Read.All`` | 按用户共享链接（仅聊天成员可访问） |

按用户共享更安全，因为只有聊天参与者可以访问文件。如果缺少 ``Chat.Read.All`` 权限，机器人将回退到组织范围共享。

### 回退行为

| 场景 | 结果 |
| :--- | :--- |
| 群聊 + 文件 + 已配置 ``sharePointSiteId`` | 上传到 SharePoint，发送共享链接 |
| 群聊 + 文件 + 无 ``sharePointSiteId`` | 尝试 OneDrive 上传（可能失败），仅发送文本 |
| 个人聊天 + 文件 | FileConsentCard 流程（无需 SharePoint 即可工作） |
| 任何上下文 + 图片 | Base64 编码内联（无需 SharePoint 即可工作） |

### 文件存储位置

上传的文件存储在配置的 SharePoint 站点的默认文档库中的 ``/OpenClawShared/`` 文件夹中。

## 投票（自适应卡片）

OpenClaw 将 Teams 投票作为自适应卡片发送（没有原生的 Teams 投票 API）。

- CLI: ``openclaw message poll --channel msteams --target conversation:<id> ...``
- 投票由网关在 ``~/.openclaw/msteams-polls.json`` 中记录。
- 网关必须保持在线以记录投票。
- 投票目前不会自动发布结果摘要（如有需要请检查存储文件）。

## 自适应卡片（任意）

使用 ``message`` 工具或 CLI 向 Teams 用户或对话发送任何自适应卡片 JSON。

``card`` 参数接受自适应卡片 JSON 对象。当提供 ``card`` 时，消息文本是可选的。

**代理工具：**

````json
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
````

**CLI：**

````bash
openclaw message send --channel msteams \
  --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello!"}]}'
````

有关卡片架构和示例，请参阅 [自适应卡片文档](https://adaptivecards.io/)。有关目标格式详细信息，请参阅下面的 [目标格式](#target-formats)。

## 目标格式

MSTeams 目标使用前缀来区分用户和对话：

| 目标类型 | 格式 | 示例 |
| :--- | :--- | :--- |
| 用户（按 ID） | ``user:<aad-object-id>`` | ``user:40a1a0ed-4ff2-4164-a219-55518990c197`` |
| 用户（按名称） | ``user:<display-name>`` | ``user:John Smith``（需要 Graph API） |
| 组/频道 | ``conversation:<conversation-id>`` | ``conversation:19:abc123...@thread.tacv2`` |
| 组/频道（原始） | ``<conversation-id>`` | ``19:abc123...@thread.tacv2``（如果包含 ``@thread``） |

**CLI 示例：**

````bash
# Send to a user by ID
openclaw message send --channel msteams --target "user:40a1a0ed-..." --message "Hello"

# Send to a user by display name (triggers Graph API lookup)
openclaw message send --channel msteams --target "user:John Smith" --message "Hello"

# Send to a group chat or channel
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" --message "Hello"

# Send an Adaptive Card to a conversation
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello"}]}'
````

**代理工具示例：**

````json
{
  "action": "send",
  "channel": "msteams",
  "target": "user:John Smith",
  "message": "Hello!"
}
````

````json
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
````

注意：如果没有 ``user:`` 前缀，名称默认为组/团队解析。通过显示名称定位人员时，始终使用 ``user:``。

## 主动消息

- 主动消息仅在用户交互**之后**才可能实现，因为我们在该点存储对话引用。
- 有关 ``dmPolicy`` 和允许列表门控，请参阅 ``/gateway/configuration``。

## 团队和频道 ID（常见陷阱）

Teams URL 中的 ``groupId`` 查询参数**不是**用于配置的团队 ID。改为从 URL 路径中提取 ID：

**团队 URL：**

````
https://teams.microsoft.com/l/team/19%3ABk4j...%40thread.tacv2/conversations?groupId=...
                                    └────────────────────────────┘
                                    Team ID (URL-decode this)
````

**频道 URL：**

````
https://teams.microsoft.com/l/channel/19%3A15bc...%40thread.tacv2/ChannelName?groupId=...
                                      └─────────────────────────┘
                                      Channel ID (URL-decode this)
````

**对于配置：**

- 团队 ID = ``/team/`` 之后的路径段（URL 解码，例如 ``19:Bk4j...@thread.tacv2``）
- 频道 ID = ``/channel/`` 之后的路径段（URL 解码）
- **忽略** ``groupId`` 查询参数

## 私有频道

机器人在私有频道中的支持有限：

| 功能 | 标准频道 | 私有频道 |
| :--- | :--- | :--- |
| 机器人安装 | 是 | 有限 |
| 实时消息（webhook） | 是 | 可能无法工作 |
| RSC 权限 | 是 | 行为可能不同 |
| @提及 | 是 | 如果机器人可访问 |
| Graph API 历史记录 | 是 | 是（带权限） |

**如果私有频道不起作用的变通方法：**

1. 使用标准频道进行机器人交互
2. 使用 DM - 用户始终可以直接向机器人发送消息
3. 使用 Graph API 进行历史访问（需要 ``ChannelMessage.Read.All``）

## 故障排除

### 常见问题

- **频道中图像无法显示：** Graph 权限或管理员同意缺失。重新安装 Teams 应用并完全退出/重新打开 Teams。
- **频道中没有响应：** 默认需要提及；设置 `channels.msteams.requireMention=false` 或按团队/频道配置。
- **版本不匹配（Teams 仍显示旧 manifest）：** 移除并重新添加应用，然后完全退出 Teams 以刷新。
- **来自 webhook 的 401 Unauthorized：** 手动测试且未使用 Azure JWT 时预期会出现 - 表示端点可达但认证失败。请使用 Azure Web Chat 进行正确测试。

### Manifest 上传错误

- **“图标文件不能为空”：** Manifest 引用了大小为 0 字节的图标文件。创建有效的 PNG 图标（32x32 用于 `outline.png`，192x192 用于 `color.png`）。
- **“webApplicationInfo.Id 已在使用中”：** 该应用仍安装在另一个团队/聊天中。请先查找并卸载它，或者等待 5-10 分钟让更改生效。
- **上传时出现“出错了”：** 请改用 [https://admin.teams.microsoft.com](https://admin.teams.microsoft.com) 上传，打开浏览器 DevTools (F12) → Network 选项卡，并检查响应体中的实际错误。
- **Sideload 失败：** 尝试“向组织的应用目录上传应用”而不是“上传自定义应用” - 这通常可绕过 Sideload 限制。

### RSC 权限无法正常工作

1. 验证 `webApplicationInfo.id` 是否与您的 Bot 的 App ID 完全匹配
2. 重新上传应用并在团队/聊天中重新安装
3. 检查您的组织管理员是否阻止了 RSC 权限
4. 确认您使用的是正确的 scope：teams 使用 `ChannelMessage.Read.Group`，group chats 使用 `ChatMessage.Read.Chat`

## 参考资料

- [创建 Azure Bot](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-quickstart-registration) - Azure Bot 设置指南
- [Teams 开发门户](https://dev.teams.microsoft.com/apps) - 创建/管理 Teams 应用
- [Teams 应用 manifest 架构](https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema)
- [使用 RSC 接收频道消息](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/channel-messages-with-rsc)
- [RSC 权限参考](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/rsc/resource-specific-consent)
- [Teams Bot 文件处理](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/bots-filesv4) (频道/群聊需要 Graph)
- [主动式消息传递](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/send-proactive-messages)