---
summary: "Mattermost bot setup and OpenClaw config"
read_when:
  - Setting up Mattermost
  - Debugging Mattermost routing
title: "Mattermost"
---
# Mattermost

状态：捆绑插件（机器人令牌 + WebSocket 事件）。支持频道、群组和私信。
Mattermost 是一个可自托管的团队消息平台；有关产品详情和下载，请访问官方网站
[mattermost.com](https://mattermost.com)。

## 捆绑插件

Mattermost 在当前 OpenClaw 版本中作为捆绑插件发布，因此常规打包构建不需要单独安装。

如果您使用的是旧版构建或排除了 Mattermost 的自定义安装，请手动安装：

通过 CLI 安装（npm 注册表）：

```bash
openclaw plugins install @openclaw/mattermost
```

本地检出（当从 git 仓库运行时）：

```bash
openclaw plugins install ./path/to/local/mattermost-plugin
```

详情：[插件](/tools/plugin)

## 快速设置

1. 确保 Mattermost 插件可用。
   - 当前打包的 OpenClaw 版本已捆绑它。
   - 旧版/自定义安装可以使用上述命令手动添加它。
2. 创建一个 Mattermost 机器人账户并复制 **机器人令牌**。
3. 复制 Mattermost **基础 URL**（例如，`https://chat.example.com`）。
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

- `native: "auto"` 默认为 Mattermost 禁用。设置 `native: true` 以启用。
- 如果省略 `callbackUrl`，OpenClaw 将从网关主机/端口 + `callbackPath` 派生一个。
- 对于多账户设置，`commands` 可以在顶层设置或在
  `channels.mattermost.accounts.<id>.commands` 下设置（账户值覆盖顶层字段）。
- 命令回调使用 Mattermost 在 OpenClaw 注册 `oc_*` 命令时返回的每命令令牌进行验证。
- 如果注册失败、启动不完整或回调令牌不匹配任何注册命令，斜杠回调将关闭失败。
- 可达性要求：回调端点必须可从 Mattermost 服务器访问。
  - 除非 Mattermost 与 OpenClaw 运行在同一主机/网络命名空间中，否则不要将 `callbackUrl` 设置为 `localhost`。
  - 除非该 URL 反向代理 `/api/channels/mattermost/command` 到 OpenClaw，否则不要将 `callbackUrl` 设置为您的 Mattermost 基础 URL。
  - 快速检查是 `curl https://<gateway-host>/api/channels/mattermost/command`；GET 应返回来自 OpenClaw 的 `405 Method Not Allowed`，而不是 `404`。
- Mattermost 出站白名单要求：
  - 如果您的回调目标是私有/tailnet/内部地址，请设置 Mattermost
    `ServiceSettings.AllowedUntrustedInternalConnections` 以包含回调主机/域名。
  - 使用主机/域名条目，而非完整 URL。
    - 好：`gateway.tailnet-name.ts.net`
    - 差：`https://gateway.tailnet-name.ts.net`

## 环境变量（默认账户）

如果您更喜欢环境变量，请在网关主机上设置这些：

- `MATTERMOST_BOT_TOKEN=...`
- `MATTERMOST_URL=https://chat.example.com`

环境变量仅适用于 **默认** 账户 (`default`)。其他账户必须使用配置值。

## 聊天模式

Mattermost 自动响应私信。频道行为由 `chatmode` 控制：

- `oncall`（默认）：仅在频道中被提及时响应。
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

- `onchar` 仍响应显式提及。
- `channels.mattermost.requireMention` 对旧配置有效，但首选 `chatmode`。

## 线程与会话

使用 `channels.mattermost.replyToMode` 控制频道和群组回复是保留在主频道中还是在触发帖子下开启线程。

- `off`（默认）：仅当传入帖子已在线程中时才在线程中回复。
- `first`：对于顶级频道/群组帖子，在该帖子下开启线程并将对话路由到线程范围会话。
- `all`：今天与 `first` 行为相同。
- 私信忽略此设置并保持非线程化。

配置示例：

```json5
{
  channels: {
    mattermost: {
      replyToMode: "all",
    },
  },
}
```

注意：

- 线程范围会话使用触发帖子 ID 作为线程根。
- `first` 和 `all` 目前等效，因为一旦 Mattermost 有了线程根，
  后续块和媒体将继续在同一线程中。

## 访问控制（私信）

- 默认：`channels.mattermost.dmPolicy = "pairing"`（未知发送者获得配对码）。
- 批准方式：
  - `openclaw pairing list mattermost`
  - `openclaw pairing approve mattermost <CODE>`
- 公共私信：`channels.mattermost.dmPolicy="open"` 加上 `channels.mattermost.allowFrom=["*"]`。

## 频道（群组）

- 默认：`channels.mattermost.groupPolicy = "allowlist"`（提及门禁）。
- 使用 `channels.mattermost.groupAllowFrom` 允许发送者（推荐用户 ID）。
- 每频道提及覆盖位于 `channels.mattermost.groups.<channelId>.requireMention`
  或 `channels.mattermost.groups["*"].requireMention` 下作为默认值。
- `@username` 匹配是可变的，仅在 `channels.mattermost.dangerouslyAllowNameMatching: true` 时启用。
- 开放频道：`channels.mattermost.groupPolicy="open"`（提及门禁）。
- 运行时注意：如果 `channels.mattermost` 完全缺失，运行时回退到 `groupPolicy="allowlist"` 进行群组检查（即使设置了 `channels.defaults.groupPolicy`）。

示例：

```json5
{
  channels: {
    mattermost: {
      groupPolicy: "open",
      groups: {
        "*": { requireMention: true },
        "team-channel-id": { requireMention: false },
      },
    },
  },
}
```

## 出站交付目标

配合 `openclaw message send` 或 cron/webhooks 使用这些目标格式：

- `channel:<id>` 用于频道
- `user:<id>` 用于私信
- `@username` 用于私信（通过 Mattermost API 解析）

裸透明 ID（如 `64ifufp...`）在 Mattermost 中具有歧义性（用户 ID 与频道 ID）。

OpenClaw 优先按用户解析：

- 如果 ID 存在为用户 (`GET /api/v4/users/<id>` 成功)，OpenClaw 通过解析直接频道发送 **私信** 经由 `/api/v4/channels/direct`。
- 否则 ID 被视为 **频道 ID**。

如果需要确定性行为，请始终使用显式前缀 (`user:<id>` / `channel:<id>`)。

## 私信频道重试

当 OpenClaw 向 Mattermost 私信目标发送且需要先解析直接频道时，默认会重试直接频道创建失败。

使用 `channels.mattermost.dmChannelRetry` 全局调整 Mattermost 插件的行为，或使用 `channels.mattermost.accounts.<id>.dmChannelRetry` 针对单个账户。

```json5
{
  channels: {
    mattermost: {
      dmChannelRetry: {
        maxRetries: 3,
        initialDelayMs: 1000,
        maxDelayMs: 10000,
        timeoutMs: 30000,
      },
    },
  },
}
```

注意：

- 这仅适用于私信频道创建 (`/api/v4/channels/direct`)，不适用于每个 Mattermost API 调用。
- 重试适用于瞬态故障，例如速率限制、5xx 响应以及网络或超时错误。
- 除 `429` 外的 4xx 客户端错误被视为永久错误且不重试。

## 反应（消息工具）

- 使用 `message action=react` 配合 `channel=mattermost`。
- `messageId` 是 Mattermost 帖子 ID。
- `emoji` 接受诸如 `thumbsup` 或 `:+1:` 的名称（冒号可选）。
- 设置 `remove=true`（布尔值）以移除反应。
- 反应添加/移除事件作为系统事件转发到路由代理会话。

示例：

```
message action=react channel=mattermost target=channel:<channelId> messageId=<postId> emoji=thumbsup
message action=react channel=mattermost target=channel:<channelId> messageId=<postId> emoji=thumbsup remove=true
```

配置：

- `channels.mattermost.actions.reactions`：启用/禁用反应操作（默认为 true）。
- 单账户覆盖：`channels.mattermost.accounts.<id>.actions.reactions`。

## 交互式按钮（消息工具）

发送带有可点击按钮的消息。当用户点击按钮时，代理接收选择并可以响应。

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
- `callback_data`（必需）：点击时返回的值（用作操作 ID）。
- `style`（可选）：`"default"`、`"primary"` 或 `"danger"`。

当用户点击按钮时：

1. 所有按钮替换为一行确认信息（例如，“✓ **是** 被 @user 选中”）。
2. 代理将选择作为传入消息接收并响应。

注意：

- 按钮回调使用 HMAC-SHA256 验证（自动，无需配置）。
- Mattermost 从其 API 响应中剥离回调数据（安全特性），因此点击后所有按钮都会被移除——无法部分移除。
- 包含连字符或下划线的操作 ID 会自动清理（Mattermost 路由限制）。

配置：

- ``channels.mattermost.capabilities``: 能力字符串数组。添加 ``"inlineButtons"`` 以在代理系统提示中启用按钮工具描述。
- ``channels.mattermost.interactions.callbackBaseUrl``: 按钮回调的可选外部基础 URL（例如 ``https://gateway.example.com``）。当 Mattermost 无法直接通过其绑定主机访问网关时使用此选项。
- 在多账户设置中，您也可以在 ``channels.mattermost.accounts.<id>.interactions.callbackBaseUrl`` 下设置相同字段。
- 如果省略 ``interactions.callbackBaseUrl``，OpenClaw 将从 ``gateway.customBindHost`` + ``gateway.port`` 推导回调 URL，然后回退到 ``http://localhost:<port>``。
- 可达性规则：按钮回调 URL 必须可从 Mattermost 服务器访问。
  ``localhost`` 仅在 Mattermost 和 OpenClaw 在同一主机或网络命名空间上运行时有效。
- 如果您的回调目标是私有/tailnet/internal，请将其主机/域名添加到 Mattermost ``ServiceSettings.AllowedUntrustedInternalConnections``。

### 直接 API 集成（外部脚本）

外部脚本和 Webhooks 可以直接通过 Mattermost REST API 发布按钮，而无需经过代理的 ``message`` 工具。尽可能使用扩展中的 ``buildButtonAttachments()``；如果发布原始 JSON，请遵循以下规则：

**负载结构：**

````json5
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
````

**关键规则：**

1. 附件应放在 ``props.attachments`` 中，而不是顶层的 ``attachments``（会被静默忽略）。
2. 每个操作都需要 ``type: "button"`` —— 没有它，点击将被静默吞没。
3. 每个操作都需要一个 ``id`` 字段 —— Mattermost 会忽略没有 ID 的操作。
4. 操作 ``id`` 必须**仅限字母数字字符** (``[a-zA-Z0-9]``)。连字符和下划线会破坏 Mattermost 的服务器端操作路由（返回 404）。使用前请移除它们。
5. ``context.action_id`` 必须与按钮的 ``id`` 匹配，以便确认消息显示按钮名称（例如“批准”）而不是原始 ID。
6. ``context.action_id`` 是必需的 —— 如果没有它，交互处理器将返回 400。

**HMAC 令牌生成：**

网关使用 HMAC-SHA256 验证按钮点击。外部脚本必须生成与网关验证逻辑匹配的令牌：

1. 从机器人令牌派生密钥：
   ``HMAC-SHA256(key="openclaw-mattermost-interactions", data=botToken)``
2. 构建上下文对象，包含**除了** ``_token`` **之外**的所有字段。
3. 使用**排序后的键**且**无空格**进行序列化（网关使用 ``JSON.stringify`` 配合排序后的键，从而产生紧凑输出）。
4. 签名：``HMAC-SHA256(key=secret, data=serializedContext)``
5. 将生成的十六进制摘要作为 ``_token`` 添加到上下文中。

Python 示例：

````python
import hmac, hashlib, json

secret = hmac.new(
    b"openclaw-mattermost-interactions",
    bot_token.encode(), hashlib.sha256
).hexdigest()

ctx = {"action_id": "mybutton01", "action": "approve"}
payload = json.dumps(ctx, sort_keys=True, separators=(",", ":"))
token = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

context = {**ctx, "_token": token}
````

常见 HMAC 陷阱：

- Python 的 ``json.dumps`` 默认添加空格 (``{"key": "val"}``)。使用 ``separators=(",", ":")`` 以匹配 JavaScript 的紧凑输出 (``{"key":"val"}``)。
- 始终对**所有**上下文字段进行签名（**减去** ``_token``）。网关会剥离 ``_token``，然后对剩余所有内容签名。对子集签名会导致静默验证失败。
- 使用 ``sort_keys=True`` —— 网关在签名前会对键进行排序，Mattermost 在存储负载时可能会重新排列上下文字段。
- 从机器人令牌（**确定性**）派生密钥，而不是随机字节。密钥必须在创建按钮的过程和验证令牌的网关之间保持一致。

## 目录适配器

Mattermost 插件包含一个目录适配器，通过 Mattermost API 解析频道和用户名。这使得在 ``openclaw message send`` 以及 cron/Webhook 交付中能够使用 ``#channel-name`` 和 ``@username`` 目标。

无需配置 —— 适配器使用账户配置中的机器人令牌。

## 多账户

Mattermost 支持在 ``channels.mattermost.accounts`` 下管理多个账户：

````json5
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
````

## 故障排除

- 频道中没有回复：确保机器人在频道中并提及它（oncall），使用触发前缀（onchar），或设置 ``chatmode: "onmessage"``。
- 认证错误：检查机器人令牌、基础 URL 以及账户是否已启用。
- 多账户问题：环境变量仅适用于 ``default`` 账户。
- 原生斜杠命令返回 ``Unauthorized: invalid command token.``：OpenClaw 未接受回调令牌。典型原因：
  - 斜杠命令注册失败或在启动时仅部分完成
  - 回调正指向错误的网关/账户
  - Mattermost 仍保留指向先前回调目标的老命令
  - 网关重启但未重新激活斜杠命令
- 如果原生斜杠命令停止工作，请检查日志中的 ``mattermost: failed to register slash commands`` 或 ``mattermost: native slash commands enabled but no commands could be registered``。
- 如果省略 ``callbackUrl`` 且日志警告回调解析为 ``http://127.0.0.1:18789/...``，则该 URL 可能仅在 Mattermost 与 OpenClaw 运行在同一主机/网络命名空间时可访问。改为设置明确的、外部可访问的 ``commands.callbackUrl``。
- 按钮显示为白色方框：代理可能正在发送格式错误的按钮数据。检查每个按钮是否同时具有 ``text`` 和 ``callback_data`` 字段。
- 按钮渲染但点击无效：验证 Mattermost 服务器配置中的 ``AllowedUntrustedInternalConnections`` 包含 ``127.0.0.1 localhost``，并且 ``EnablePostActionIntegration`` 在 ServiceSettings 中为 ``true``。
- 点击按钮返回 404：按钮 ``id`` 可能包含连字符或下划线。Mattermost 的操作路由器在非字母数字 ID 上会失效。仅使用 ``[a-zA-Z0-9]``。
- 网关日志 ``invalid _token``：HMAC 不匹配。检查您是否对所有上下文字段（而非子集）进行了签名，使用了排序后的键，并使用了紧凑 JSON（无空格）。请参阅上方的 HMAC 部分。
- 网关日志 ``missing _token in context``：``_token`` 字段不在按钮的上下文中。确保在构建集成负载时包含它。
- 确认消息显示原始 ID 而非按钮名称：``context.action_id`` 与按钮的 ``id`` 不匹配。将两者设置为相同的清理值。
- 代理不知道按钮：将 ``capabilities: ["inlineButtons"]`` 添加到 Mattermost 频道配置中。

## 相关

- [频道概览](/channels) — 所有支持的频道
- [配对](/channels/pairing) — DM 认证和配对流程
- [群组](/channels/groups) — 群聊行为和提及门控
- [频道路由](/channels/channel-routing) — 消息会话路由
- [安全](/gateway/security) — 访问模型和加固