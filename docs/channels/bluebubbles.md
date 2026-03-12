---
summary: "iMessage via BlueBubbles macOS server (REST send/receive, typing, reactions, pairing, advanced actions)."
read_when:
  - Setting up BlueBubbles channel
  - Troubleshooting webhook pairing
  - Configuring iMessage on macOS
title: "BlueBubbles"
---
# BlueBubbles（macOS REST）

状态：作为捆绑插件运行，通过 HTTP 与 BlueBubbles macOS 服务器通信。**推荐用于 iMessage 集成**，因其 API 更丰富、设置比传统的 imsg 通道更简便。

## 概述

- 通过 BlueBubbles 辅助应用（[bluebubbles.app](https://bluebubbles.app)）在 macOS 上运行。
- 已推荐/测试版本：macOS Sequoia（15）。macOS Tahoe（26）可运行；但当前在 Tahoe 上编辑功能异常，且群组图标更新可能报告成功却未实际同步。
- OpenClaw 通过其 REST API（`GET /api/v1/ping`、`POST /message/text`、`POST /chat/:id/*`）与其通信。
- 入站消息通过 Webhook 到达；出站回复、输入提示、已读回执及 Tapback 均通过 REST 调用实现。
- 附件和贴纸作为入站媒体被接收（并在可能时向智能体暴露）。
- 配对/白名单机制与其他通道（`/channels/pairing` 等）一致，使用 `channels.bluebubbles.allowFrom` + 配对码。
- 表情反应以系统事件形式暴露，与 Slack/Telegram 类似，因此智能体可在回复前“提及”它们。
- 高级功能：编辑、撤回、回复线程、消息特效、群组管理。

## 快速开始

1. 在您的 Mac 上安装 BlueBubbles 服务器（请遵循 [bluebubbles.app/install](https://bluebubbles.app/install) 上的说明）。
2. 在 BlueBubbles 配置中启用 Web API 并设置密码。
3. 运行 `openclaw onboard` 并选择 BlueBubbles，或手动配置：

   ```json5
   {
     channels: {
       bluebubbles: {
         enabled: true,
         serverUrl: "http://192.168.1.100:1234",
         password: "example-password",
         webhookPath: "/bluebubbles-webhook",
       },
     },
   }
   ```

4. 将 BlueBubbles Webhook 指向您的网关（示例：`https://your-gateway-host:3000/bluebubbles-webhook?password=<password>`）。
5. 启动网关；它将注册 Webhook 处理器并开始配对。

安全提示：

- 务必始终设置 Webhook 密码。
- Webhook 身份验证始终为强制要求。OpenClaw 将拒绝所有 BlueBubbles Webhook 请求，除非其携带的密码/GUID 与 `channels.bluebubbles.password` 匹配（例如 `?password=<password>` 或 `x-password`），无论是否处于环回/代理拓扑结构中。
- 密码身份验证在读取/解析完整 Webhook 请求体之前即完成校验。

## 保持 Messages.app 活跃（虚拟机 / 无头环境）

某些 macOS 虚拟机 / 常驻运行环境中，Messages.app 可能进入“空闲”状态（入站事件停止，直至该应用被打开或置于前台）。一种简单解决方案是使用 AppleScript + LaunchAgent **每 5 分钟“轻触”一次 Messages**。

### 1）保存 AppleScript

将以下脚本保存为：

- `~/Scripts/poke-messages.scpt`

示例脚本（非交互式；不抢占焦点）：

```applescript
try
  tell application "Messages"
    if not running then
      launch
    end if

    -- Touch the scripting interface to keep the process responsive.
    set _chatCount to (count of chats)
  end tell
on error
  -- Ignore transient failures (first-run prompts, locked session, etc).
end try
```

### 2）安装 LaunchAgent

将以下内容保存为：

- `~/Library/LaunchAgents/com.user.poke-messages.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.user.poke-messages</string>

    <key>ProgramArguments</key>
    <array>
      <string>/bin/bash</string>
      <string>-lc</string>
      <string>/usr/bin/osascript &quot;$HOME/Scripts/poke-messages.scpt&quot;</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>StartInterval</key>
    <integer>300</integer>

    <key>StandardOutPath</key>
    <string>/tmp/poke-messages.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/poke-messages.err</string>
  </dict>
</plist>
```

说明：

- 此任务 **每 300 秒执行一次**，且 **在用户登录时触发**。
- 首次运行可能触发 macOS 的 **自动化权限提示**（`osascript` → Messages）。请在运行 LaunchAgent 的同一用户会话中批准这些提示。

加载该任务：

```bash
launchctl unload ~/Library/LaunchAgents/com.user.poke-messages.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.user.poke-messages.plist
```

## 入门引导

BlueBubbles 可在交互式设置向导中启用：

```
openclaw onboard
```

向导将提示您输入以下信息：

- **服务器 URL**（必填）：BlueBubbles 服务器地址（例如 `http://192.168.1.100:1234`）
- **密码**（必填）：BlueBubbles 服务器设置中的 API 密码
- **Webhook 路径**（可选）：默认为 `/bluebubbles-webhook`
- **私信策略**：配对、白名单、开放或禁用
- **白名单**：电话号码、邮箱地址或聊天目标

您也可通过 CLI 添加 BlueBubbles：

```
openclaw channels add bluebubbles --http-url http://192.168.1.100:1234 --password <password>
```

## 访问控制（私信 + 群组）

私信：

- 默认策略：`channels.bluebubbles.dmPolicy = "pairing"`。
- 未知发件人将收到配对码；其消息将在获准前被忽略（配对码 1 小时后过期）。
- 可通过以下方式批准：
  - `openclaw pairing list bluebubbles`
  - `openclaw pairing approve bluebubbles <CODE>`
- 配对是默认的令牌交换机制。详情参见：[配对](/channels/pairing)

群组：

- `channels.bluebubbles.groupPolicy = open | allowlist | disabled`（默认：`allowlist`）。
- 当 `allowlist` 启用时，`channels.bluebubbles.groupAllowFrom` 控制谁可在群组中触发响应。

### 提及门控（群组）

BlueBubbles 支持群聊中的提及门控，行为与 iMessage/WhatsApp 一致：

- 使用 `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）检测提及。
- 当某群组启用了 `requireMention` 时，智能体仅在被提及后才响应。
- 经授权发送者的控制命令不受提及门控限制。

按群组配置：

```json5
{
  channels: {
    bluebubbles: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15555550123"],
      groups: {
        "*": { requireMention: true }, // default for all groups
        "iMessage;-;chat123": { requireMention: false }, // override for specific group
      },
    },
  },
}
```

### 命令门控

- 控制命令（例如 `/config`、`/model`）需经授权。
- 使用 `allowFrom` 和 `groupAllowFrom` 判定命令授权。
- 经授权的发送者即使未在群组中提及，也可运行控制命令。

## 输入提示 + 已读回执

- **输入提示**：在响应生成前及生成过程中自动发送。
- **已读回执**：由 `channels.bluebubbles.sendReadReceipts` 控制（默认：`true`）。
- **输入提示**：OpenClaw 发送“开始输入”事件；BlueBubbles 在发送消息或超时后自动清除输入状态（通过 DELETE 手动停止不可靠）。

```json5
{
  channels: {
    bluebubbles: {
      sendReadReceipts: false, // disable read receipts
    },
  },
}
```

## 高级操作

当在配置中启用时，BlueBubbles 支持以下高级消息操作：

```json5
{
  channels: {
    bluebubbles: {
      actions: {
        reactions: true, // tapbacks (default: true)
        edit: true, // edit sent messages (macOS 13+, broken on macOS 26 Tahoe)
        unsend: true, // unsend messages (macOS 13+)
        reply: true, // reply threading by message GUID
        sendWithEffect: true, // message effects (slam, loud, etc.)
        renameGroup: true, // rename group chats
        setGroupIcon: true, // set group chat icon/photo (flaky on macOS 26 Tahoe)
        addParticipant: true, // add participants to groups
        removeParticipant: true, // remove participants from groups
        leaveGroup: true, // leave group chats
        sendAttachment: true, // send attachments/media
      },
    },
  },
}
```

可用操作：

- **react**：添加/移除 Tapback 表情反应（`messageId`、`emoji`、`remove`）
- **edit**：编辑已发送的消息（`messageId`、`text`）
- **unsend**：撤回一条消息（`messageId`）
- **reply**：回复特定消息（`messageId`、`text`、`to`）
- **sendWithEffect**：以 iMessage 特效发送消息（`text`、`to`、`effectId`）
- **renameGroup**：重命名群组聊天（`chatGuid`、`displayName`）
- **setGroupIcon**：设置群组聊天的图标/头像（`chatGuid`、`media`）——在 macOS 26 Tahoe 上不稳定（API 可能返回成功，但图标实际未同步）。
- **addParticipant**：向群组添加成员（`chatGuid`、`address`）
- **removeParticipant**：从群组中移除成员（`chatGuid`、`address`）
- **leaveGroup**：退出群组聊天（`chatGuid`）
- **sendAttachment**：发送媒体/文件（`to`、`buffer`、`filename`、`asVoice`）
  - 语音备忘录：将 `asVoice: true` 设置为 **MP3** 或 **CAF** 格式音频，即可作为 iMessage 语音消息发送。BlueBubbles 在发送语音备忘录时会将 MP3 自动转为 CAF。

### 消息 ID（短 ID 与完整 ID）

为节省 token，OpenClaw 可能向智能体暴露 _短格式_ 消息 ID（例如 `1`、`2`）。

- `MessageSid` / `ReplyToId` 可为短 ID。
- `MessageSidFull` / `ReplyToIdFull` 包含服务商提供的完整 ID。
- 短 ID 仅存在于内存中；重启或缓存清理后可能失效。
- 操作支持短 ID 或完整 `messageId`，但若短 ID 已不可用，则将报错。

对于持久化自动化和存储，请使用完整 ID：

- 模板中：`{{MessageSidFull}}`、`{{ReplyToIdFull}}`
- 上下文内：入站载荷中的 `MessageSidFull` / `ReplyToIdFull`

参见 [配置](/gateway/configuration) 了解模板变量。

## 阻断流式传输

控制响应是以单条消息发送，还是分块流式发送：

```json5
{
  channels: {
    bluebubbles: {
      blockStreaming: true, // enable block streaming (off by default)
    },
  },
}
```

## 媒体 + 限制

- 入站附件将被下载并存储于媒体缓存中。
- 入站与出站媒体均受 `channels.bluebubbles.mediaMaxMb` 限制（默认：8 MB）。
- 出站文本将被切分为长度不超过 `channels.bluebubbles.textChunkLimit` 的片段（默认：4000 字符）。

## 配置参考

完整配置说明：[配置](/gateway/configuration)

提供程序选项：

- `channels.bluebubbles.enabled`: 启用/禁用该通道。  
- `channels.bluebubbles.serverUrl`: BlueBubbles REST API 基础 URL。  
- `channels.bluebubbles.password`: API 密码。  
- `channels.bluebubbles.webhookPath`: Webhook 端点路径（默认：`/bluebubbles-webhook`）。  
- `channels.bluebubbles.dmPolicy`: `pairing | allowlist | open | disabled`（默认：`pairing`）。  
- `channels.bluebubbles.allowFrom`: 私信（DM）允许列表（支持句柄、邮箱、E.164 号码、`chat_id:*`、`chat_guid:*`）。  
- `channels.bluebubbles.groupPolicy`: `open | allowlist | disabled`（默认：`allowlist`）。  
- `channels.bluebubbles.groupAllowFrom`: 群组发件人允许列表。  
- `channels.bluebubbles.groups`: 每群组配置（如 `requireMention` 等）。  
- `channels.bluebubbles.sendReadReceipts`: 发送已读回执（默认：`true`）。  
- `channels.bluebubbles.blockStreaming`: 启用分块流式传输（默认：`false`；流式回复必需）。  
- `channels.bluebubbles.textChunkLimit`: 出站消息分块大小（字符数，默认：4000）。  
- `channels.bluebubbles.chunkMode`: `length`（默认）仅在超出 `textChunkLimit` 时进行分块；`newline` 则优先在空行（段落边界）处分块，再按长度分块。  
- `channels.bluebubbles.mediaMaxMb`: 入站/出站媒体文件大小上限（MB，默认：8）。  
- `channels.bluebubbles.mediaLocalRoots`: 明确指定允许用于出站本地媒体路径的绝对本地目录白名单。默认情况下，本地路径发送被拒绝，除非配置了此项。每账户覆盖配置项：`channels.bluebubbles.accounts.<accountId>.mediaLocalRoots`。  
- `channels.bluebubbles.historyLimit`: 用于上下文的最多群组消息数（0 表示禁用）。  
- `channels.bluebubbles.dmHistoryLimit`: 私信历史记录限制。  
- `channels.bluebubbles.actions`: 启用/禁用特定操作。  
- `channels.bluebubbles.accounts`: 多账户配置。

相关全局选项：

- `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）。  
- `messages.responsePrefix`。

## 地址解析 / 投递目标

建议使用 `chat_guid` 实现稳定路由：

- `chat_guid:iMessage;-;+15555550123`（群组首选）  
- `chat_id:123`  
- `chat_identifier:...`  
- 直接句柄：`+15555550123`、`user@example.com`  
  - 若某直接句柄尚无现有私信聊天，OpenClaw 将通过 `POST /api/v1/chat/new` 自动创建一个。此功能要求启用 BlueBubbles 私有 API。

## 安全性

- Webhook 请求通过比对 `guid`/`password` 查询参数或请求头与 `channels.bluebubbles.password` 进行身份验证。来自 `localhost` 的请求亦被接受。  
- 请妥善保管 API 密码和 webhook 端点地址（视同敏感凭证）。  
- “信任 localhost” 意味着同主机上的反向代理可能无意中绕过密码验证。若对网关进行了代理，请在代理层启用认证，并配置 `gateway.trustedProxies`。参见 [网关安全性](/gateway/security#reverse-proxy-configuration)。  
- 若将 BlueBubbles 服务器暴露于局域网外，请为其启用 HTTPS 并配置防火墙规则。

## 故障排查

- 若输入状态/已读状态事件停止工作，请检查 BlueBubbles webhook 日志，并确认网关路径与 `channels.bluebubbles.webhookPath` 一致。  
- 配对码一小时后过期；请使用 `openclaw pairing list bluebubbles` 和 `openclaw pairing approve bluebubbles <code>`。  
- 表情反应（Reactions）依赖 BlueBubbles 私有 API（`POST /api/v1/message/react`）；请确保服务器版本公开了该接口。  
- 编辑/撤回消息功能需 macOS 13+ 及兼容版本的 BlueBubbles 服务端。在 macOS 26（Tahoe）上，因私有 API 变更，当前编辑功能不可用。  
- 群组图标更新在 macOS 26（Tahoe）上可能不稳定：API 可能返回成功，但新图标无法同步。  
- OpenClaw 会根据 BlueBubbles 服务端所报告的 macOS 版本，自动隐藏已知失效的操作。若在 macOS 26（Tahoe）上仍显示“编辑”选项，请手动通过 `channels.bluebubbles.actions.edit=false` 禁用。  
- 查看状态/健康信息：`openclaw status --all` 或 `openclaw status --deep`。

有关通用通道工作流程参考，请参阅 [通道](/channels) 和 [插件](/tools/plugin) 指南。