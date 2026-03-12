---
summary: "Microsoft Teams bot support status, capabilities, and configuration"
read_when:
  - Working on MS Teams channel features
title: "Microsoft Teams"
---
# Microsoft Teams（插件）

> “入此门者，须弃一切希望。”

更新时间：2026-01-21

状态：支持纯文本及私信附件；群组/频道文件发送需启用 `sharePointSiteId` + Graph 权限（参见[在群组聊天中发送文件](#sending-files-in-group-chats)）。投票通过自适应卡片（Adaptive Cards）发送。

## 需要安装插件

Microsoft Teams 以插件形式提供，**不包含在核心安装包中**。

**重大变更（2026.1.15）：** MS Teams 已从核心模块中移出。若您正在使用该功能，则必须手动安装插件。

说明：此举可保持核心安装更轻量，并使 MS Teams 的依赖项能够独立更新。

通过 CLI（npm 仓库）安装：

```bash
openclaw plugins install @openclaw/msteams
```

本地检出（当从 Git 仓库运行时）：

```bash
openclaw plugins install ./extensions/msteams
```

若在配置/初始引导过程中选择 Teams，且检测到 Git 检出，
OpenClaw 将自动提供本地安装路径。

详情参见：[插件](/tools/plugin)

## 快速设置（新手向）

1. 安装 Microsoft Teams 插件。
2. 创建一个 **Azure Bot**（应用 ID + 客户端密钥 + 租户 ID）。
3. 使用上述凭据配置 OpenClaw。
4. 通过公网 URL 或隧道暴露 `/api/messages`（默认端口为 3978）。
5. 安装 Teams 应用包并启动网关。

最小化配置示例：

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

注意：群组聊天默认被阻止（`channels.msteams.groupPolicy: "allowlist"`）。如需允许群组回复，请设置 `channels.msteams.groupAllowFrom`（或使用 `groupPolicy: "open"` 允许任意成员，但仍需提及触发）。

## 目标

- 通过 Teams 私信、群组聊天或频道与 OpenClaw 对话。
- 保证路由确定性：回复始终返回至消息来源的同一频道。
- 默认采用安全的频道行为（除非另行配置，否则必须提及才响应）。

## 配置写入权限

默认情况下，Microsoft Teams 被允许通过 `/config set|unset` 触发配置更新（需具备 `commands.config: true` 权限）。

禁用方式：

```json5
{
  channels: { msteams: { configWrites: false } },
}
```

## 访问控制（私信 + 群组）

**私信访问控制**

- 默认策略：`channels.msteams.dmPolicy = "pairing"`。未知发送者将被忽略，直至获得批准。
- `channels.msteams.allowFrom` 应使用稳定的 AAD 对象 ID。
- UPN/显示名称是可变的；默认禁用直接匹配，仅在启用 `channels.msteams.dangerouslyAllowNameMatching: true` 后才启用。
- 配置向导可在凭证允许时，通过 Microsoft Graph 将名称解析为 ID。

**群组访问控制**

- 默认策略：`channels.msteams.groupPolicy = "allowlist"`（除非添加 `groupAllowFrom`，否则被阻止）。可使用 `channels.defaults.groupPolicy` 在未设置时覆盖默认值。
- `channels.msteams.groupAllowFrom` 控制哪些发送者可在群组聊天/频道中触发响应（回退至 `channels.msteams.allowFrom`）。
- 设置 `groupPolicy: "open"` 可允许任意成员（仍默认需提及触发）。
- 若要禁止**所有频道**，请设置 `channels.msteams.groupPolicy: "disabled"`。

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

**Teams + 频道白名单**

- 通过在 `channels.msteams.teams` 下列出团队和频道，限定群组/频道回复范围。
- 键名可以是团队 ID 或名称；频道键名可以是会话 ID 或名称。
- 当启用 `groupPolicy="allowlist"` 且存在 Teams 白名单时，仅接受白名单中列出的团队/频道（仍需提及触发）。
- 配置向导支持输入 `Team/Channel` 条目，并为您自动保存。
- 启动时，OpenClaw 在 Graph 权限允许的前提下，将团队/频道及用户白名单中的名称解析为 ID，并记录映射关系；无法解析的条目将保留原始输入形式。

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
2. 创建一个 **Azure Bot**（应用 ID + 密钥 + 租户 ID）。
3. 构建一个 **Teams 应用包**，其中引用该 Bot 并包含下方所列 RSC 权限。
4. 将 Teams 应用上传/安装至某个团队（或个人作用域以支持私信）。
5. 在 `~/.openclaw/openclaw.json`（或环境变量）中配置 `msteams`，然后启动网关。
6. 网关默认监听 Bot Framework Webhook 流量，地址为 `/api/messages`。

## Azure Bot 设置（前置条件）

在配置 OpenClaw 前，您需先创建 Azure Bot 资源。

### 步骤 1：创建 Azure Bot

1. 访问 [创建 Azure Bot](https://portal.azure.com/#create/Microsoft.AzureBot)
2. 填写 **基本信息** 页：

   | 字段               | 值                                                         |
   | ------------------ | ---------------------------------------------------------- |
   | **Bot handle**     | 您的 Bot 名称，例如 `openclaw-msteams`（必须唯一）         |
   | **Subscription**   | 选择您的 Azure 订阅                                        |
   | **Resource group** | 新建或使用已有资源组                                       |
   | **Pricing tier**   | **免费**（适用于开发/测试）                                |
   | **Type of App**    | **单租户**（推荐 —— 见下方说明）                           |
   | **Creation type**  | **新建 Microsoft 应用 ID**                                 |

> **弃用通知：** 自 2025-07-31 起，新多租户 Bot 的创建已被弃用。新 Bot 请使用 **单租户** 模式。

3. 点击 **查看 + 创建** → **创建**（等待约 1–2 分钟）

### 步骤 2：获取凭据

1. 进入您的 Azure Bot 资源 → **配置**
2. 复制 **Microsoft 应用 ID** → 即您的 `appId`
3. 点击 **管理密码** → 进入应用注册页面
4. 在 **证书与机密** 下 → **新建客户端密钥** → 复制 **值** → 即您的 `appPassword`
5. 进入 **概览** → 复制 **目录（租户）ID** → 即您的 `tenantId`

### 步骤 3：配置消息端点

1. 在 Azure Bot → **配置**
2. 将 **消息端点** 设为您的 Webhook URL：
   - 生产环境：`https://your-domain.com/api/messages`
   - 本地开发：使用隧道（参见下方[本地开发（隧道）](#local-development-tunneling)）

### 步骤 4：启用 Teams 渠道

1. 在 Azure Bot → **渠道**
2. 点击 **Microsoft Teams** → 配置 → 保存
3. 接受服务条款

## 本地开发（隧道）

Teams 无法访问 `localhost`。本地开发请使用隧道：

**选项 A：ngrok**

```bash
ngrok http 3978
# Copy the https URL, e.g., https://abc123.ngrok.io
# Set messaging endpoint to: https://abc123.ngrok.io/api/messages
```

**选项 B：Tailscale Funnel**

```bash
tailscale funnel 3978
# Use your Tailscale funnel URL as the messaging endpoint
```

## Teams 开发者门户（替代方案）

您无需手动创建 manifest ZIP 包，可改用 [Teams 开发者门户](https://dev.teams.microsoft.com/apps)：

1. 点击 **+ 新建应用**
2. 填写基本信息（名称、描述、开发者信息）
3. 进入 **应用功能** → **Bot**
4. 选择 **手动输入 Bot ID**，并粘贴您的 Azure Bot 应用 ID
5. 勾选作用域：**个人**、**团队**、**群组聊天**
6. 点击 **分发** → **下载应用包**
7. 在 Teams 中：**应用** → **管理你的应用** → **上传自定义应用** → 选择 ZIP 文件

此方法通常比手动编辑 JSON manifest 更便捷。

## 测试 Bot

**选项 A：Azure Web Chat（先验证 Webhook）**

1. 在 Azure 门户 → 您的 Azure Bot 资源 → **Web Chat 中测试**
2. 发送一条消息 —— 您应收到响应
3. 此步骤用于确认 Webhook 端点正常工作，再进行 Teams 配置

**选项 B：Teams（应用安装后）**

1. 安装 Teams 应用（侧载或组织应用目录）
2. 在 Teams 中找到该 Bot 并发送一条私信
3. 查看网关日志，确认是否有入站活动

## 设置（最小化纯文本模式）

1. **安装 Microsoft Teams 插件**
   - 从 npm 安装：`openclaw plugins install @openclaw/msteams`
   - 从本地检出安装：`openclaw plugins install ./extensions/msteams`

2. **Bot 注册**
   - 创建 Azure Bot（参见上文），并记录以下信息：
     - 应用 ID
     - 客户端密钥（应用密码）
     - 租户 ID（单租户）

3. **Teams 应用 manifest**
   - 包含一项 `bot` 条目，其值为 `botId = <App ID>`。
   - 作用域：`personal`、`team`、`groupChat`。
   - `supportsFiles: true`（个人作用域文件处理必需）。
   - 添加 RSC 权限（见下文）。
   - 创建图标：`outline.png`（32×32）和 `color.png`（192×192）。
   - 将三个文件打包为 ZIP：`manifest.json`、`outline.png`、`color.png`。

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

   您也可使用环境变量代替配置项：
   - `MSTEAMS_APP_ID`
   - `MSTEAMS_APP_PASSWORD`
   - `MSTEAMS_TENANT_ID`

5. **Bot 端点**
   - 将 Azure Bot 的消息端点设为：
     - `https://<host>:3978/api/messages`（或您指定的路径/端口）。

6. **运行网关**
   - 当插件已安装且 `msteams` 配置中存在有效凭据时，Teams 渠道将自动启动。

## 历史上下文

- `channels.msteams.historyLimit` 控制最近多少条频道/群组消息会被纳入提示词（prompt）中。
- 默认回退至 `messages.groupChat.historyLimit`。设置 `0` 可禁用该功能（默认值为 50）。
- 私信历史可通过 `channels.msteams.dmHistoryLimit`（用户轮次）限制。支持按用户覆盖：`channels.msteams.dms["<user_id>"].historyLimit`。

## 当前 Teams RSC 权限（Manifest）

以下为 Teams 应用 manifest 中当前使用的 **资源特定（resourceSpecific）权限**。这些权限仅在已安装该应用的团队/聊天中生效。

**针对频道（团队作用域）：**

- `ChannelMessage.Read.Group`（应用）—— 接收所有频道消息，无需 @提及  
- `ChannelMessage.Send.Group`（应用）  
- `Member.Read.Group`（应用）  
- `Owner.Read.Group`（应用）  
- `ChannelSettings.Read.Group`（应用）  
- `TeamMember.Read.Group`（应用）  
- `TeamSettings.Read.Group`（应用）  

**对于群聊：**  

- `ChatMessage.Read.Chat`（应用）—— 接收所有群聊消息，无需 @提及  

## 示例 Teams 清单文件（已脱敏）  

包含必需字段的最简有效示例。请替换其中的 ID 和 URL。  

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

### 清单文件注意事项（必需字段）  

- `bots[].botId` **必须** 与 Azure Bot 应用 ID 一致。  
- `webApplicationInfo.id` **必须** 与 Azure Bot 应用 ID 一致。  
- `bots[].scopes` 必须包含您计划使用的界面类型（`personal`、`team`、`groupChat`）。  
- `bots[].supportsFiles: true` 在个人作用域中处理文件时为必需项。  
- `authorization.permissions.resourceSpecific` 若需接收/发送频道消息，则必须包含频道读取/发送权限。  

### 更新已安装的应用  

要更新已安装的 Teams 应用（例如：添加 RSC 权限）：  

1. 使用新配置更新您的 `manifest.json`  
2. **递增 `version` 字段**（例如：`1.0.0` → `1.1.0`）  
3. **重新打包** 清单文件（含图标：`manifest.json`、`outline.png`、`color.png`）  
4. 上传新的 ZIP 包：  
   - **选项 A（Teams 管理中心）：** Teams 管理中心 → Teams 应用 → 管理应用 → 查找您的应用 → 上传新版本  
   - **选项 B（侧载）：** 在 Teams 中 → 应用 → 管理您的应用 → 上传自定义应用  
5. **对于团队频道：** 需在每个团队中重新安装该应用，新权限方可生效  
6. **完全退出并重新启动 Teams**（不只是关闭窗口），以清除缓存的应用元数据  

## 功能对比：仅 RSC vs Graph  

### 仅启用 **Teams RSC**（已安装应用，无 Graph API 权限）  

支持：  

- 读取频道消息的**文本内容**。  
- 发送频道消息的**文本内容**。  
- 接收**个人（私聊）** 中的文件附件。  

不支持：  

- 频道/群聊中的**图片或文件内容**（有效载荷仅包含 HTML 占位符）。  
- 下载存储在 SharePoint/OneDrive 中的附件。  
- 读取消息历史记录（超出实时 Webhook 事件范围）。  

### 启用 **Teams RSC + Microsoft Graph 应用权限**  

新增支持：  

- 下载托管内容（如粘贴到消息中的图片）。  
- 下载存储在 SharePoint/OneDrive 中的文件附件。  
- 通过 Graph API 读取频道/聊天消息历史记录。  

### RSC vs Graph API  

| 功能                  | RSC 权限             | Graph API                           |  
| --------------------- | -------------------- | ----------------------------------- |  
| **实时消息**          | 是（通过 Webhook）    | 否（仅支持轮询）                     |  
| **历史消息**          | 否                   | 是（可查询历史记录）                 |  
| **部署复杂度**        | 仅需清单文件          | 需管理员同意 + Token 流程            |  
| **离线可用性**        | 否（必须保持运行）     | 是（可随时查询）                     |  

**核心结论：** RSC 适用于实时监听；Graph API 适用于历史访问。若需在离线期间补获错过的消息，您需要启用 Graph API 并配置 `ChannelMessage.Read.All`（需管理员同意）。  

## 启用 Graph 的媒体与历史功能（频道场景必需）  

若您需要在**频道**中获取图片/文件，或希望获取**消息历史记录**，则必须启用 Microsoft Graph 权限并获得管理员同意。  

1. 在 Entra ID（Azure AD）的**应用注册**中，添加 Microsoft Graph **应用权限**：  
   - `ChannelMessage.Read.All`（频道附件 + 历史记录）  
   - `Chat.Read.All` 或 `ChatMessage.Read.All`（群聊）  
2. 为租户**授予管理员同意**。  
3. 提升 Teams 应用的**清单文件版本号**，重新上传，并在 Teams 中**重新安装该应用**。  
4. **完全退出并重新启动 Teams**，以清除缓存的应用元数据。  

**用户 @提及的额外权限：** 用户 @提及对当前会话中的用户默认即生效。但若您希望动态搜索并提及**当前会话中不存在的用户**，请添加 `User.Read.All`（应用）权限并授予管理员同意。  

## 已知限制  

### Webhook 超时  

Teams 通过 HTTP Webhook 传递消息。若处理耗时过长（例如：大语言模型响应缓慢），可能出现以下情况：  

- 网关超时  
- Teams 重试发送消息（导致重复）  
- 回复被丢弃  

OpenClaw 通过快速返回响应并主动发送回复来应对该问题，但极慢的响应仍可能导致异常。  

### 格式化支持  

Teams 的 Markdown 支持比 Slack 或 Discord 更有限：  

- 基础格式化可用：**粗体**、_斜体_、`code`、链接  
- 复杂 Markdown（表格、嵌套列表）可能无法正确渲染  
- 自适应卡片（Adaptive Cards）支持投票及任意卡片发送（详见下文）  

## 配置  

关键设置（共享频道模式参见 `/gateway/configuration`）：  

- `channels.msteams.enabled`：启用/禁用该频道。  
- `channels.msteams.appId`、`channels.msteams.appPassword`、`channels.msteams.tenantId`：机器人凭据。  
- `channels.msteams.webhook.port`（默认值：`3978`）  
- `channels.msteams.webhook.path`（默认值：`/api/messages`）  
- `channels.msteams.dmPolicy`：`pairing | allowlist | open | disabled`（默认：配对）  
- `channels.msteams.allowFrom`：私聊白名单（推荐使用 AAD 对象 ID）。向导在具备 Graph 访问权限时，可在配置过程中将用户名解析为对应 ID。  
- `channels.msteams.dangerouslyAllowNameMatching`：紧急开关，用于重新启用可变 UPN/显示名称匹配。  
- `channels.msteams.textChunkLimit`：出站文本分块大小。  
- `channels.msteams.chunkMode`：`length`（默认）或 `newline`（在按长度分块前，先按空行拆分，即按段落边界拆分）。  
- `channels.msteams.mediaAllowHosts`：入站附件主机白名单（默认为 Microsoft/Teams 域名）。  
- `channels.msteams.mediaAuthAllowHosts`：媒体重试时附加 Authorization 请求头的主机白名单（默认为 Graph + Bot Framework 主机）。  
- `channels.msteams.requireMention`：是否要求在频道/群聊中使用 @提及（默认为 true）。  
- `channels.msteams.replyStyle`：`thread | top-level`（参见 [回复样式：线程 vs 帖子](#reply-style-threads-vs-posts)）。  
- `channels.msteams.teams.<teamId>.replyStyle`：按团队覆盖。  
- `channels.msteams.teams.<teamId>.requireMention`：按团队覆盖。  
- `channels.msteams.teams.<teamId>.tools`：团队级默认工具策略覆盖（当频道级覆盖缺失时，使用 `allow`/`deny`/`alsoAllow`）。  
- `channels.msteams.teams.<teamId>.toolsBySender`：团队级、按发送者默认工具策略覆盖（支持 `"*"` 通配符）。  
- `channels.msteams.teams.<teamId>.channels.<conversationId>.replyStyle`：按频道覆盖。  
- `channels.msteams.teams.<teamId>.channels.<conversationId>.requireMention`：按频道覆盖。  
- `channels.msteams.teams.<teamId>.channels.<conversationId>.tools`：频道级工具策略覆盖（`allow`/`deny`/`alsoAllow`）。  
- `channels.msteams.teams.<teamId>.channels.<conversationId>.toolsBySender`：频道级、按发送者工具策略覆盖（支持 `"*"` 通配符）。  
- `toolsBySender` 键应使用显式前缀：  
  `id:`、`e164:`、`username:`、`name:`（旧版无前缀键仍仅映射至 `id:`）。  
- `channels.msteams.sharePointSiteId`：群聊/频道中文件上传所用的 SharePoint 站点 ID（参见 [在群聊中发送文件](#sending-files-in-group-chats)）。  

## 路由与会话  

- 会话键遵循标准代理格式（参见 [/concepts/session](/concepts/session)）：  
  - 私聊共享主会话（`agent:<agentId>:<mainKey>`）。  
  - 频道/群聊消息使用会话 ID：  
    - `agent:<agentId>:msteams:channel:<conversationId>`  
    - `agent:<agentId>:msteams:group:<conversationId>`  

## 回复样式：线程 vs 帖子  

Teams 近期在相同底层数据模型上引入了两种频道 UI 样式：  

| 样式                    | 描述                                               | 推荐的 `replyStyle` |  
| ----------------------- | -------------------------------------------------- | ------------------------ |  
| **帖子（经典）**         | 消息以卡片形式呈现，下方嵌套线程式回复              | `thread`（默认）       |  
| **线程（类 Slack）**     | 消息呈线性流动，更接近 Slack 风格                  | `top-level`              |  

**问题所在：** Teams API 并未暴露频道实际使用的 UI 样式。若您使用了错误的 `replyStyle`：

- `thread` 在 Threads 风格的频道中 → 回复会以嵌套形式 awkwardly（别扭地）显示  
- `top-level` 在 Posts 风格的频道中 → 回复会作为独立的顶级帖子显示，而非在对话线程内  

**解决方案：** 根据频道的具体配置方式，为每个频道单独配置 `replyStyle`：  

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

## 附件与图片  

**当前限制：**  

- **私聊（DMs）：** 图片和文件附件可通过 Teams Bot 的文件 API 实现。  
- **频道/群组：** 附件存储在 M365 存储（SharePoint / OneDrive）中。Webhook 负载仅包含 HTML 占位符，**不包含实际文件字节**。**需要 Graph API 权限** 才能下载频道中的附件。  

若未配置 Graph 权限，含图片的频道消息将仅以纯文本形式被接收（图片内容对 Bot 不可见）。  
默认情况下，OpenClaw 仅从 Microsoft/Teams 域名下载媒体资源。可通过 `channels.msteams.mediaAllowHosts` 覆盖该行为（使用 `["*"]` 可允许任意域名）。  
授权请求头（Authorization headers）仅附加至 `channels.msteams.mediaAuthAllowHosts` 中列出的域名（默认为 Graph + Bot Framework 域名）。请严格维护此列表（避免使用多租户后缀）。  

## 在群聊中发送文件  

Bot 可通过内置的 `FileConsentCard` 流程在私聊中发送文件（开箱即用）。但 **在群聊/频道中发送文件** 需要额外配置：  

| 上下文                  | 文件发送方式                           | 所需配置                                    |  
| ------------------------ | -------------------------------------- | ------------------------------------------- |  
| **私聊（DMs）**          | `FileConsentCard` → 用户确认 → Bot 上传 | 开箱即用                                    |  
| **群聊/频道**            | 上传至 SharePoint → 分享链接            | 需要配置 `sharePointSiteId` + Graph 权限     |  
| **图片（任意上下文）**    | Base64 编码内联                         | 开箱即用                                    |  

### 为何群聊需依赖 SharePoint  

Bot 没有个人 OneDrive 空间（``/me/drive`` Graph API 端点对应用身份不可用）。为在群聊/频道中发送文件，Bot 需将文件上传至 **SharePoint 站点** 并生成共享链接。  

### 配置步骤  

1. **在 Entra ID（Azure AD）→ 应用注册中添加 Graph API 权限：**  
   - `Sites.ReadWrite.All`（应用权限）—— 用于向 SharePoint 上传文件  
   - `Chat.Read.All`（应用权限）—— 可选，启用按用户生成的共享链接  

2. **为租户授予管理员同意（Admin Consent）。**  

3. **获取您的 SharePoint 站点 ID：**  

   ```bash
   # Via Graph Explorer or curl with a valid token:
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/{hostname}:/{site-path}"

   # Example: for a site at "contoso.sharepoint.com/sites/BotFiles"
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com:/sites/BotFiles"

   # Response includes: "id": "contoso.sharepoint.com,guid1,guid2"
   ```  

4. **配置 OpenClaw：**  

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
| --------------------------------- | ------------------------------------------------- |  
| 仅 `Sites.ReadWrite.All`           | 组织范围共享链接（组织内任何人均可访问）           |  
| `Sites.ReadWrite.All` + `Chat.Read.All` | 按用户共享链接（仅聊天参与者可访问）                |  

按用户共享更安全，因为只有聊天成员才能访问该文件。若缺少 `Chat.Read.All` 权限，Bot 将自动回退至组织范围共享。  

### 回退行为  

| 场景                                          | 结果                                             |  
| --------------------------------------------- | ------------------------------------------------ |  
| 群聊 + 文件 + 已配置 `sharePointSiteId`       | 上传至 SharePoint，发送共享链接                   |  
| 群聊 + 文件 + 未配置 `sharePointSiteId`       | 尝试 OneDrive 上传（可能失败），仅发送纯文本       |  
| 私聊 + 文件                                   | `FileConsentCard` 流程（无需 SharePoint 即可工作） |  
| 任意上下文 + 图片                             | Base64 编码内联（无需 SharePoint 即可工作）        |  

### 文件存储位置  

上传的文件将保存在已配置 SharePoint 站点的默认文档库中的 `/OpenClawShared/` 文件夹内。  

## 投票（自适应卡片，Adaptive Cards）  

OpenClaw 将 Teams 投票以自适应卡片（Adaptive Cards）形式发送（Teams 无原生投票 API）。  

- CLI：`openclaw message poll --channel msteams --target conversation:<id> ...`  
- 投票记录由网关写入 `~/.openclaw/msteams-polls.json`。  
- 网关必须保持在线状态，才能记录投票。  
- 投票目前尚不支持自动发布结果摘要（如需查看，可检查存储文件）。  

## 自适应卡片（任意类型）  

可使用 `message` 工具或 CLI，向 Teams 用户或会话发送任意自适应卡片 JSON。  

``card`` 参数接受一个自适应卡片 JSON 对象。当提供 ``card`` 时，消息正文文本为可选。  

**Agent 工具：**  

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

有关卡片 Schema 和示例，请参阅 [自适应卡片文档](https://adaptivecards.io/)。目标格式详情见下方 [目标格式](#target-formats)。  

## 目标格式  

Teams 目标使用前缀区分用户与会话：  

| 目标类型         | 格式                           | 示例                                             |  
| ---------------- | ------------------------------ | ------------------------------------------------ |  
| 用户（按 ID）     | `user:<aad-object-id>`         | `user:40a1a0ed-4ff2-4164-a219-55518990c197`         |  
| 用户（按姓名）    | `user:<display-name>`          | `user:John Smith`（需 Graph API）                 |  
| 群组/频道         | `conversation:<conversation-id>` | `conversation:19:abc123...@thread.tacv2`            |  
| 群组/频道（原始） | `<conversation-id>`              | `19:abc123...@thread.tacv2`（若包含 `@thread`）     |  

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

**Agent 工具示例：**  

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

注意：若未使用 `user:` 前缀，名称默认按群组/团队解析。**当按显示名称定位人员时，务必使用 `user:`。**  

## 主动消息（Proactive messaging）  

- 主动消息仅在用户**完成首次交互后**才可行，因为我们此时已存储了会话引用（conversation reference）。  
- 详见 `/gateway/configuration` 中关于 `dmPolicy` 及白名单管控机制的说明。  

## 团队与频道 ID（常见误区）  

Teams URL 中的 ``groupId`` 查询参数 **并非** 配置所用的团队 ID。请从 URL 路径中提取 ID：  

**团队 URL：**  

```
https://teams.microsoft.com/l/team/19%3ABk4j...%40thread.tacv2/conversations?groupId=...
                                    └────────────────────────────┘
                                    Team ID (URL-decode this)
```  

**频道 URL：**  

```
https://teams.microsoft.com/l/channel/19%3A15bc...%40thread.tacv2/ChannelName?groupId=...
                                      └─────────────────────────┘
                                      Channel ID (URL-decode this)
```  

**用于配置：**  
- 团队 ID = ``/team/`` 后的路径段（URL 解码后，例如 `19:Bk4j...@thread.tacv2`）  
- 频道 ID = ``/channel/`` 后的路径段（URL 解码后）  
- **忽略** ``groupId`` 查询参数  

## 私密频道（Private Channels）  

Bot 在私密频道中支持有限：  

| 功能                      | 标准频道 | 私密频道         |  
| ------------------------- | -------- | ---------------- |  
| Bot 安装                  | 是       | 有限             |  
| 实时消息（Webhook）       | 是       | 可能无法工作     |  
| RSC 权限                  | 是       | 行为可能不同     |  
| @提及                     | 是       | 若 Bot 可访问则支持 |  
| Graph API 历史记录        | 是       | 是（需相应权限） |  

**若私密频道不可用，可采用以下变通方案：**  
1. 在标准频道中进行 Bot 交互  
2. 使用私聊（DMs）—— 用户始终可直接向 Bot 发送消息  
3. 使用 Graph API 访问历史记录（需 `ChannelMessage.Read.All`）  

## 故障排查  

### 常见问题

- **频道中图片未显示：** Graph 权限或管理员同意缺失。请重新安装 Teams 应用，并完全退出后重新打开 Teams。
- **频道中无响应：** 默认情况下需要提及（mentions）；请设置 `channels.msteams.requireMention=false`，或按团队/频道单独配置。
- **版本不匹配（Teams 仍显示旧清单文件）：** 移除并重新添加应用，并完全退出 Teams 以刷新缓存。
- **Webhook 返回 401 Unauthorized：** 手动测试时若未使用 Azure JWT，则会出现此情况——表示端点可达但身份验证失败。请使用 Azure Web Chat 进行正确测试。

### 清单文件上传错误

- **“图标文件不能为空”：** 清单文件引用了大小为 0 字节的图标文件。请创建有效的 PNG 图标（`outline.png` 使用 32×32 像素，`color.png` 使用 192×192 像素）。
- **“webApplicationInfo.Id 已被占用”：** 该应用仍安装在其他团队/聊天中。请先查找并卸载，或等待 5–10 分钟等待传播完成。
- **上传时显示“发生某些错误”：** 请改用 [https://admin.teams.microsoft.com](https://admin.teams.microsoft.com) 上传，在浏览器中打开开发者工具（F12）→ “网络”（Network）选项卡，检查响应体以获取实际错误信息。
- **侧载（sideload）失败：** 尝试选择“将应用上传至组织的应用目录”而非“上传自定义应用”——这通常可绕过侧载限制。

### RSC 权限未生效

1. 确认 `webApplicationInfo.id` 与机器人的应用 ID 完全一致  
2. 重新上传应用并在团队/聊天中重新安装  
3. 检查组织管理员是否已禁用 RSC 权限  
4. 确认您使用的是正确的范围：团队场景使用 `ChannelMessage.Read.Group`，群组聊天场景使用 `ChatMessage.Read.Chat`

## 参考资料

- [创建 Azure Bot](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-quickstart-registration) — Azure Bot 配置指南  
- [Teams 开发者门户](https://dev.teams.microsoft.com/apps) — 创建和管理 Teams 应用  
- [Teams 应用清单架构](https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema)  
- [使用 RSC 接收频道消息](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/channel-messages-with-rsc)  
- [RSC 权限参考](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/rsc/resource-specific-consent)  
- [Teams 机器人文件处理](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/bots-filesv4)（频道/群组需使用 Graph）  
- [主动式消息发送（Proactive messaging）](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/send-proactive-messages)