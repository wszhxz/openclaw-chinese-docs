---
summary: "Mattermost bot setup and OpenClaw config"
read_when:
  - Setting up Mattermost
  - Debugging Mattermost routing
title: "Mattermost"
---
# Mattermost (插件)

状态：通过插件支持（机器人令牌 + WebSocket 事件）。支持频道、群组和 DM。
Mattermost 是一个可自托管的团队消息平台；有关产品详情和下载，请访问官方网站
[mattermost.com](https://mattermost.com)。

## 需要插件

Mattermost 以插件形式发布，不包含在核心安装中。

通过 CLI 安装（npm 注册表）：

```bash
openclaw plugins install @openclaw/mattermost
```

本地检出（当从 git 仓库运行时）：

```bash
openclaw plugins install ./extensions/mattermost
```

如果在配置/入门期间选择 Mattermost 并检测到 git 检出，
OpenClaw 将自动提供本地安装路径。

详情：[插件](/tools/plugin)

## 快速设置

1. 安装 Mattermost 插件。
2. 创建 Mattermost 机器人账户并复制 **bot token**。
3. 复制 Mattermost **base URL**（例如，`https://chat.example.com`）。
4. 配置 OpenClaw 并启动网关。

最小配置：

```json5
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token",
      baseUrl: "https://chat.example.com",
      dmPolicy: "pairing",
    },
  },
}
```

## 原生斜杠命令

原生斜杠命令为可选启用。启用后，OpenClaw 通过 Mattermost API 注册 `oc_*` 斜杠命令，并在网关 HTTP 服务器上接收回调 POST。

```json5
{
  channels: {
    mattermost: {
      commands: {
        native: true,
        nativeSkills: true,
        callbackPath: "/api/channels/mattermost/command",
        // Use when Mattermost cannot reach the gateway directly (reverse proxy/public URL).
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
    },
  },
}
```

注意：

- `native: "auto"` 对于 Mattermost 默认禁用。设置 `native: true` 以启用。
- 如果省略 `callbackUrl`，OpenClaw 将从网关主机/端口 + `callbackPath` 派生一个。
- 对于多账户设置，`commands` 可以在顶层设置或在 `channels.mattermost.accounts.<id>.commands` 下设置（账户值覆盖顶层字段）。
- 命令回调使用每个命令的令牌进行验证，当令牌检查失败时关闭。
- 可达性要求：回调端点必须能从 Mattermost 服务器访问。
  - 除非 Mattermost 与 OpenClaw 运行在同一主机/网络命名空间中，否则不要将 `callbackUrl` 设置为 `localhost`。
  - 除非该 URL 反向代理 `/api/channels/mattermost/command` 到 OpenClaw，否则不要将 `callbackUrl` 设置为您 Mattermost 的 base URL。
  - 快速检查是 `curl https://<gateway-host>/api/channels/mattermost/command`；GET 请求应从 OpenClaw 返回 `405 Method Not Allowed`，而不是 `404`。
- Mattermost 出站白名单要求：
  - 如果您的回调目标是私有/tailnet/内部地址，请设置 Mattermost `ServiceSettings.AllowedUntrustedInternalConnections` 以包含回调主机/域名。
  - 使用主机/域名条目，而非完整 URL。
    - 正确：`gateway.tailnet-name.ts.net`
    - 错误：`https://gateway.tailnet-name.ts.net`

## 环境变量（默认账户）

如果您更喜欢环境变量，请在网关主机上设置这些：

- `MATTERMOST_BOT_TOKEN=...`
- `MATTERMOST_URL=https://chat.example.com`

环境变量仅适用于 **默认** 账户（`default`）。其他账户必须使用配置值。

## 聊天模式

Mattermost 会自动响应 DM。频道行为由 `chatmode` 控制：

- `oncall`（默认）：仅在频道中被@提及时响应。
- `onmessage`：响应每个频道消息。
- `onchar`：当消息以触发前缀开头时响应。

配置示例：

```json5
{
  channels: {
    mattermost: {
      chatmode: "onchar",
      oncharPrefixes: [">", "!"],
    },
  },
}
```

注意：

- `onchar` 仍会响应显式@提及。
- `channels.mattermost.requireMention` 用于旧版配置但保留，推荐使用 `chatmode`。

## 访问控制（DMs）

- 默认：`channels.mattermost.dmPolicy = "pairing"`（未知发送者获得配对码）。
- 批准方式：
  - `openclaw pairing list mattermost`
  - `openclaw pairing approve mattermost <CODE>`
- 公开 DM：`channels.mattermost.dmPolicy="open"` 加上 `channels.mattermost.allowFrom=["*"]`。

## 频道（群组）

- 默认：`channels.mattermost.groupPolicy = "allowlist"`（提及门禁）。
- 使用 `channels.mattermost.groupAllowFrom` 允许列表发送者（推荐用户 ID）。
- `@username` 匹配是可变的，仅在 `channels.mattermost.dangerouslyAllowNameMatching: true` 时启用。
- 开放频道：`channels.mattermost.groupPolicy="open"`（提及门禁）。
- 运行时注意：如果完全缺少 `channels.mattermost`，运行时将回退到 `groupPolicy="allowlist"` 进行群组检查（即使设置了 `channels.defaults.groupPolicy`）。

## 出站交付目标

配合 `openclaw message send` 或 cron/webhooks 使用这些目标格式：

- `channel:<id>` 用于频道
- `user:<id>` 用于 DM
- `@username` 用于 DM（通过 Mattermost API 解析）

裸 ID 被视为频道。

## 反应（消息工具）

- 使用 `message action=react` 配合 `channel=mattermost`。
- `messageId` 是 Mattermost 帖子 ID。
- `emoji` 接受如 `thumbsup` 或 `:+1:` 的名称（冒号可选）。
- 设置 `remove=true`（布尔值）以移除反应。
- 反应添加/移除事件作为系统事件转发到路由的代理会话。

示例：

```
message action=react channel=mattermost target=channel:<channelId> messageId=<postId> emoji=thumbsup
message action=react channel=mattermost target=channel:<channelId> messageId=<postId> emoji=thumbsup remove=true
```

配置：

- `channels.mattermost.actions.reactions`：启用/禁用反应操作（默认 true）。
- 每账户覆盖：`channels.mattermost.accounts.<id>.actions.reactions`。

## 交互式按钮（消息工具）

发送带有可点击按钮的消息。当用户点击按钮时，代理接收选择并可响应。

通过将 `inlineButtons` 添加到频道功能来启用按钮：

```json5
{
  channels: {
    mattermost: {
      capabilities: ["inlineButtons"],
    },
  },
}
```

使用 `message action=send` 配合 `buttons` 参数。按钮是一个二维数组（按钮行）：

```
message action=send channel=mattermost target=channel:<channelId> buttons=[[{"text":"Yes","callback_data":"yes"},{"text":"No","callback_data":"no"}]]
```

按钮字段：

- `text`（必需）：显示标签。
- `callback_data`（必需）：点击时发送回的值（用作操作 ID）。
- `style`（可选）：`"default"`、`"primary"` 或 `"danger"`。

当用户点击按钮时：

1. 所有按钮被替换为一行确认信息（例如，“✓ **是** 由 @user 选择”）。
2. 代理将选择作为入站消息接收并响应。

注意：

- 按钮回调使用 HMAC-SHA256 验证（自动，无需配置）。
- Mattermost 从其 API 响应中剥离回调数据（安全特性），因此点击时所有按钮都会被移除——无法部分移除。
- 包含连字符或下划线的操作 ID 会自动清理（Mattermost 路由限制）。

配置：

- `channels.mattermost.capabilities`：能力字符串数组。添加 `"inlineButtons"` 以在代理系统提示中启用按钮工具描述。
- `channels.mattermost.interactions.callbackBaseUrl`：按钮回调的可选外部 base URL（例如 `https://gateway.example.com`）。当 Mattermost 无法直接在绑定主机上到达网关时使用此选项。
- 在多账户设置中，您也可以在下方的 `channels.mattermost.accounts.<id>.interactions.callbackBaseUrl` 下设置相同字段。
- 如果省略 `interactions.callbackBaseUrl`，OpenClaw 从 `gateway.customBindHost` + `gateway.port` 派生回调 URL，然后回退到 `http://localhost:<port>`。
- 可达性规则：按钮回调 URL 必须能从 Mattermost 服务器访问。
  `localhost` 仅在 Mattermost 和 OpenClaw 运行在同一主机/网络命名空间时有效。
- 如果您的回调目标是私有/tailnet/内部，请将其主机/域名添加到 Mattermost `ServiceSettings.AllowedUntrustedInternalConnections`。

### 直接 API 集成（外部脚本）

外部脚本和网络钩子可以直接通过 Mattermost REST API 发布按钮，而不经过代理的 `message` 工具。尽可能使用扩展中的 `buildButtonAttachments()`；如果发布原始 JSON，请遵循以下规则：

**负载结构：**

```json5
{
  channel_id: "<channelId>",
  message: "Choose an option:",
  props: {
    attachments: [
      {
        actions: [
          {
            id: "mybutton01", // alphanumeric only — see below
            type: "button", // required, or clicks are silently ignored
            name: "Approve", // display label
            style: "primary", // optional: "default", "primary", "danger"
            integration: {
              url: "https://gateway.example.com/mattermost/interactions/default",
              context: {
                action_id: "mybutton01", // must match button id (for name lookup)
                action: "approve",
                // ... any custom fields ...
                _token: "<hmac>", // see HMAC section below
              },
            },
          },
        ],
      },
    ],
  },
}
```

**关键规则：**

1. 附件放在 `props.attachments` 中，而不是顶层 `attachments`（会被静默忽略）。
2. 每个操作都需要 `type: "button"` —— 没有它，点击会被静默吞掉。
3. 每个操作都需要一个 `id` 字段 —— Mattermost 会忽略没有 ID 的操作。
4. 操作 `id` 必须仅为 **字母数字**（`[a-zA-Z0-9]`）。连字符和下划线会破坏 Mattermost 的服务器端操作路由（返回 404）。使用前请去除它们。
5. `context.action_id` 必须与按钮的 `id` 匹配，以便确认消息显示按钮名称（例如“批准”）而不是原始 ID。
6. `context.action_id` 是必需的 —— 交互处理器在没有它时会返回 400。

**HMAC 令牌生成：**

网关使用 HMAC-SHA256 验证按钮点击。外部脚本必须生成与网关验证逻辑匹配的令牌：

1. 从机器人令牌派生密钥：
   `HMAC-SHA256(key="openclaw-mattermost-interactions", data=botToken)`
2. 构建上下文对象，包含所有字段，**除了** `_token`。
3. 使用**排序后的键**和**无空格**进行序列化（网关使用 `JSON.stringify` 配合排序后的键，从而产生紧凑的输出）。
4. 签名：`HMAC-SHA256(key=secret, data=serializedContext)`
5. 将生成的十六进制摘要作为 `_token` 添加到上下文中。

Python 示例：

```python
import hmac, hashlib, json

secret = hmac.new(
    b"openclaw-mattermost-interactions",
    bot_token.encode(), hashlib.sha256
).hexdigest()

ctx = {"action_id": "mybutton01", "action": "approve"}
payload = json.dumps(ctx, sort_keys=True, separators=(",", ":"))
token = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

context = {**ctx, "_token": token}
```

常见的 HMAC 陷阱：

- Python 的 `json.dumps` 默认会添加空格 (`{"key": "val"}`)。请使用 `separators=(",", ":")` 以匹配 JavaScript 的紧凑输出 (`{"key":"val"}`)。
- 始终对**所有**上下文字段进行签名（减去 `_token`）。网关会剥离 `_token` 然后对剩余的所有内容进行签名。仅对子集签名会导致静默验证失败。
- 使用 `sort_keys=True` —— 网关在签名前会对键进行排序，且 Mattermost 在存储负载时可能会重新排序上下文字段。
- 从机器人令牌派生密钥（确定性），而不是随机字节。密钥必须在创建按钮的过程和验证它的网关之间保持一致。

## 目录适配器

Mattermost 插件包含一个目录适配器，通过 Mattermost API 解析频道和用户名。这使得在 `openclaw message send` 以及 cron/webhook 交付中能够使用 `#channel-name` 和 `@username` 目标。

无需配置——适配器使用账户配置中的机器人令牌。

## 多账户

Mattermost 支持在 `channels.mattermost.accounts` 下管理多个账户：

```json5
{
  channels: {
    mattermost: {
      accounts: {
        default: { name: "Primary", botToken: "mm-token", baseUrl: "https://chat.example.com" },
        alerts: { name: "Alerts", botToken: "mm-token-2", baseUrl: "https://alerts.example.com" },
      },
    },
  },
}
```

## 故障排除

- 频道中没有回复：确保机器人已在频道中并提及它（oncall），使用触发前缀（onchar），或设置 `chatmode: "onmessage"`。
- 认证错误：检查机器人令牌、基础 URL 以及账户是否已启用。
- 多账户问题：环境变量仅适用于 `default` 账户。
- 按钮显示为白色方框：代理可能正在发送格式错误的按钮数据。请检查每个按钮是否同时具有 `text` 和 `callback_data` 字段。
- 按钮渲染但点击无效：验证 Mattermost 服务器配置中的 `AllowedUntrustedInternalConnections` 是否包含 `127.0.0.1 localhost`，并且 `EnablePostActionIntegration` 在 ServiceSettings 中为 `true`。
- 按钮点击返回 404：按钮 `id` 可能包含连字符或下划线。Mattermost 的动作路由在处理非字母数字 ID 时会出错。仅使用 `[a-zA-Z0-9]`。
- 网关日志 `invalid _token`：HMAC 不匹配。请检查您是否对所有上下文字段进行了签名（而非子集），使用了排序后的键，并使用了紧凑 JSON（无空格）。请参阅上方的 HMAC 部分。
- 网关日志 `missing _token in context`：`_token` 字段不在按钮的上下文中。请确保在构建集成负载时包含该字段。
- 确认对话框显示原始 ID 而非按钮名称：`context.action_id` 与按钮的 `id` 不匹配。将两者设置为相同的清理值。
- 代理不知道按钮：将 `capabilities: ["inlineButtons"]` 添加到 Mattermost 频道配置中。