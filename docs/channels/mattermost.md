---
summary: "Mattermost bot setup and OpenClaw config"
read_when:
  - Setting up Mattermost
  - Debugging Mattermost routing
title: "Mattermost"
---
# Mattermost（插件）

状态：通过插件支持（使用机器人令牌 + WebSocket 事件）。支持频道、群组和私信（DM）。

Mattermost 是一款可自托管的团队消息协作平台；有关产品详情和下载，请访问其官方网站  
[mattermost.com](https://mattermost.com)。

## 需要安装插件

Mattermost 以插件形式提供，**不包含在核心安装包中**。

通过 CLI（npm 仓库）安装：

```bash
openclaw plugins install @openclaw/mattermost
```

本地检出（当从 Git 仓库运行时）：

```bash
openclaw plugins install ./extensions/mattermost
```

如果在配置/入门向导过程中选择了 Mattermost，且检测到 Git 检出路径，  
OpenClaw 将自动提供本地安装路径。

详情参见：[插件](/tools/plugin)

## 快速设置

1. 安装 Mattermost 插件。  
2. 创建一个 Mattermost 机器人账号，并复制其 **机器人令牌（bot token）**。  
3. 复制 Mattermost 的 **基础 URL（base URL）**（例如：`https://chat.example.com`）。  
4. 配置 OpenClaw 并启动网关。

最小化配置示例：

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

## 原生斜杠命令（Native slash commands）

原生斜杠命令为可选功能。启用后，OpenClaw 将通过 Mattermost API 注册 `oc_*` 个斜杠命令，  
并在网关 HTTP 服务器上接收回调 POST 请求。

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

注意事项：

- `native: "auto"` 默认对 Mattermost **禁用**。需将 `native: true` 设为 `true` 以启用。  
- 若未指定 `callbackUrl`，OpenClaw 将基于网关主机名/端口与 `callbackPath` 自动推导。  
- 对于多账号部署，`commands` 可在顶层配置，也可置于 `channels.mattermost.accounts.<id>.commands` 下（子账号值将覆盖顶层字段）。  
- 命令回调使用**按命令生成的令牌**进行校验；令牌校验失败时，请求将被拒绝（fail closed）。  
- **可达性要求**：回调端点必须能从 Mattermost 服务器访问。  
  - 切勿将 `callbackUrl` 设为 `localhost`，除非 Mattermost 与 OpenClaw 运行在同一主机或网络命名空间内。  
  - 切勿将 `callbackUrl` 设为您的 Mattermost 基础 URL，除非该 URL 已通过反向代理将 `/api/channels/mattermost/command` 路由至 OpenClaw。  
  - 快速验证方法：执行 `curl https://<gateway-host>/api/channels/mattermost/command`；HTTP GET 应返回来自 OpenClaw 的 `405 Method Not Allowed`，而非 `404`。  
- Mattermost 出站白名单要求：  
  - 若您的回调目标为私有网络/尾部网络（tailnet）/内网地址，请在 Mattermost 中将回调主机名/域名添加至  
    `ServiceSettings.AllowedUntrustedInternalConnections` 白名单中。  
  - 请仅填写主机名或域名，**不可填写完整 URL**。  
    - 正确示例：`gateway.tailnet-name.ts.net`  
    - 错误示例：`https://gateway.tailnet-name.ts.net`

## 环境变量（默认账号）

若偏好使用环境变量，请在网关主机上设置以下变量：

- `MATTERMOST_BOT_TOKEN=...`  
- `MATTERMOST_URL=https://chat.example.com`

环境变量**仅作用于默认账号**（`default`）。其他账号必须使用配置文件方式设置。

## 聊天模式

Mattermost 会自动响应私信（DM）。频道行为由 `chatmode` 控制：

- `oncall`（默认）：仅在频道中被 `@提及` 时响应。  
- `onmessage`：响应所有频道消息。  
- `onchar`：仅当消息以触发前缀开头时响应。

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

注意事项：

- `onchar` 模式下仍会响应显式的 `@提及`。  
- `channels.mattermost.requireMention` 在旧版配置中仍受支持，但推荐使用 `chatmode`。

## 访问控制（私信 DM）

- 默认策略：`channels.mattermost.dmPolicy = "pairing"`（未知发送者将收到配对码）。  
- 批准方式包括：  
  - `openclaw pairing list mattermost`  
  - `openclaw pairing approve mattermost <CODE>`  
- 公开私信（Public DMs）：启用 `channels.mattermost.dmPolicy="open"` 并配合 `channels.mattermost.allowFrom=["*"]`。

## 频道（群组）

- 默认策略：`channels.mattermost.groupPolicy = "allowlist"`（需 `@提及` 才响应）。  
- 使用 `channels.mattermost.groupAllowFrom` 白名单限定可发送者（推荐使用用户 ID）。  
- `@username` 匹配规则是可变的，**仅当启用 `channels.mattermost.dangerouslyAllowNameMatching: true` 时生效**。  
- 开放频道（Open channels）：`channels.mattermost.groupPolicy="open"`（仍为 `@提及` 触发）。  
- 运行时说明：若配置中完全缺失 `channels.mattermost`，运行时将回退至使用 `groupPolicy="allowlist"` 进行群组权限检查（即使已设置 `channels.defaults.groupPolicy`）。

## 出站消息投递目标

在使用 `openclaw message send` 或定时任务（cron）/Webhook 时，请采用以下目标格式：

- `channel:<id>` 表示频道  
- `user:<id>` 表示私信（DM）  
- `@username` 表示私信（DM），通过 Mattermost API 动态解析  

裸 ID（无前缀）将被视作频道 ID。

## 消息反应（Reactions）

- 使用 `message action=react` 配合 `channel=mattermost`。  
- `messageId` 是 Mattermost 的帖子 ID（post id）。  
- `emoji` 接受如下格式的反应名称：`thumbsup` 或 `:+1:`（冒号为可选）。  
- 设置布尔型 `remove=true` 可移除已有反应。  
- 反应添加/移除事件将以系统事件形式转发至对应路由的智能体（agent）会话。

示例：

```
message action=react channel=mattermost target=channel:<channelId> messageId=<postId> emoji=thumbsup
message action=react channel=mattermost target=channel:<channelId> messageId=<postId> emoji=thumbsup remove=true
```

配置项：

- `channels.mattermost.actions.reactions`：启用/禁用反应操作（默认为 `true`）。  
- 按账号覆盖配置：`channels.mattermost.accounts.<id>.actions.reactions`。

## 交互式按钮（Interactive buttons）

发送含可点击按钮的消息。当用户点击按钮时，智能体将接收到选择结果并可作出响应。

通过向频道能力（channel capabilities）中添加 `inlineButtons` 启用按钮功能：

```json5
{
  channels: {
    mattermost: {
      capabilities: ["inlineButtons"],
    },
  },
}
```

使用 `message action=send` 并传入 `buttons` 参数。按钮为二维数组（每行是一组按钮）：

```
message action=send channel=mattermost target=channel:<channelId> buttons=[[{"text":"Yes","callback_data":"yes"},{"text":"No","callback_data":"no"}]]
```

按钮字段说明：

- `text`（必需）：显示文本（label）。  
- `callback_data`（必需）：点击后回传的值（作为 action ID 使用）。  
- `style`（可选）：取值为 `"default"`、`"primary"` 或 `"danger"`。

当用户点击按钮时：

1. 所有按钮将被替换为确认行（例如：“✓ **Yes** selected by @user”）。  
2. 智能体将收到该选择作为一条入站消息，并可据此响应。

注意事项：

- 按钮回调使用 HMAC-SHA256 自动校验（无需额外配置）。  
- Mattermost 会在其 API 响应中剥离回调数据（安全机制），因此**点击后所有按钮均会被移除**；无法实现部分移除。  
- Action ID 中若含连字符（hyphen）或下划线（underscore），将被自动清洗（sanitized）——这是 Mattermost 路由机制的限制。

配置项：

- `channels.mattermost.capabilities`：能力字符串数组。添加 `"inlineButtons"` 可在智能体系统提示词中启用按钮工具描述。  
- `channels.mattermost.interactions.callbackBaseUrl`：按钮回调的可选外部基础 URL（例如：`https://gateway.example.com`）。当 Mattermost 无法直接访问网关绑定的主机地址时使用。  
- 在多账号部署中，您也可在 `channels.mattermost.accounts.<id>.interactions.callbackBaseUrl` 下设置相同字段。  
- 若未指定 `interactions.callbackBaseUrl`，OpenClaw 将先尝试从 `gateway.customBindHost` + `gateway.port` 推导回调 URL，再回退至 `http://localhost:<port>`。  
- **可达性规则**：按钮回调 URL 必须能从 Mattermost 服务器访问。  
  `localhost` 仅在 Mattermost 与 OpenClaw 运行于同一主机或网络命名空间时有效。  
- 若您的回调目标为私有网络/尾部网络（tailnet）/内网地址，请将其主机名/域名添加至 Mattermost 的  
  `ServiceSettings.AllowedUntrustedInternalConnections` 白名单中。

### 直接 API 集成（外部脚本）

外部脚本和 Webhook 可**直接调用 Mattermost REST API** 发送带按钮的消息，而无需经过智能体的 `message` 工具。  
建议尽可能使用扩展中提供的 `buildButtonAttachments()`；若需手动发送原始 JSON，请遵循以下规则：

**载荷结构（Payload structure）：**

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

1. 附件（attachments）必须置于 `props.attachments` 字段内，**不可置于顶层 `attachments` 字段中**（否则将被静默忽略）。  
2. 每个 action 必须包含 `type: "button"` —— 缺失则点击将被静默丢弃。  
3. 每个 action 必须包含 `id` 字段 —— Mattermost 会忽略无 ID 的 action。  
4. Action 的 `id` 必须**仅含字母数字字符**（`[a-zA-Z0-9]`）。连字符与下划线会导致 Mattermost 服务端 action 路由失败（返回 404），请在使用前清除。  
5. `context.action_id` 必须与按钮的 `id` 一致，以确保确认消息中显示按钮名称（如 “Approve”），而非原始 ID。  
6. `context.action_id` 为必需字段 —— 若缺失，交互处理器将返回 400 错误。

**HMAC 令牌生成：**

网关使用 HMAC-SHA256 验证按钮点击。外部脚本必须生成与网关验证逻辑相匹配的令牌：

1. 从机器人令牌派生密钥：
   `HMAC-SHA256(key="openclaw-mattermost-interactions", data=botToken)`
2. 构建上下文对象，包含**除** `_token` 之外的所有字段。
3. 使用**排序后的键**和**无空格**方式序列化（网关使用 `JSON.stringify` 并按键排序，从而生成紧凑输出）。
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

常见 HMAC 坑点：

- Python 的 `json.dumps` 默认添加空格（`{"key": "val"}`）。请使用 `separators=(",", ":")` 以匹配 JavaScript 的紧凑输出（`{"key":"val"}`）。
- 始终对**全部**上下文字段（减去 `_token`）进行签名。网关会先剔除 `_token`，再对剩余所有字段签名。仅对子集签名将导致静默验证失败。
- 使用 `sort_keys=True` —— 网关在签名前会对键进行排序，而 Mattermost 在存储有效载荷时可能重新排列上下文字段顺序。
- 密钥应从机器人令牌（确定性生成）派生，而非随机字节。生成按钮的进程与验证按钮的网关所使用的密钥必须一致。

## 目录适配器

Mattermost 插件包含一个目录适配器，可通过 Mattermost API 解析频道和用户名。这使得在 `#channel-name` 和 `@username` 中支持 `openclaw message send` 及 cron/webhook 投递目标。

无需额外配置 —— 该适配器直接使用账户配置中的机器人令牌。

## 多账户支持

Mattermost 在 `channels.mattermost.accounts` 下支持多个账户：

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

## 故障排查

- 频道中无回复：确保机器人已加入该频道，并提及它（oncall），或使用触发前缀（onchar），或设置 `chatmode: "onmessage"`。
- 认证错误：检查机器人令牌、基础 URL，以及账户是否已启用。
- 多账户问题：环境变量仅适用于 `default` 账户。
- 按钮显示为白色方块：代理可能发送了格式错误的按钮数据。请确认每个按钮均同时包含 `text` 和 `callback_data` 字段。
- 按钮正常渲染但点击无响应：验证 Mattermost 服务端配置中的 `AllowedUntrustedInternalConnections` 是否包含 `127.0.0.1 localhost`，且 ServiceSettings 中的 `EnablePostActionIntegration` 是否设为 `true`。
- 按钮点击返回 404：按钮的 `id` 很可能包含连字符或下划线。Mattermost 的操作路由机制不支持非字母数字 ID。请仅使用 `[a-zA-Z0-9]`。
- 网关日志出现 `invalid _token`：HMAC 不匹配。请检查是否对全部上下文字段（而非子集）进行了签名、是否使用了排序后的键，以及是否采用紧凑 JSON 格式（无空格）。详见上方 HMAC 章节。
- 网关日志出现 `missing _token in context`：按钮上下文中缺少 `_token` 字段。请确保在构建集成有效载荷时包含该字段。
- 确认弹窗中显示原始 ID 而非按钮名称：`context.action_id` 与按钮的 `id` 不匹配。请将二者设为相同的规范化值。
- 代理不了解按钮：在 Mattermost 频道配置中添加 `capabilities: ["inlineButtons"]`。