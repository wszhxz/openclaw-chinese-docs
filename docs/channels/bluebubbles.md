---
summary: "iMessage via BlueBubbles macOS server (REST send/receive, typing, reactions, pairing, advanced actions)."
read_when:
  - Setting up BlueBubbles channel
  - Troubleshooting webhook pairing
  - Configuring iMessage on macOS
title: "BlueBubbles"
---
# BlueBubbles (macOS REST)

状态：捆绑插件，通过 HTTP 与 BlueBubbles macOS 服务器通信。**推荐用于 iMessage 集成**，因为其 API 更丰富且相比传统的 imsg 通道更容易设置。

## Overview

- 在 macOS 上运行，通过 BlueBubbles 辅助应用 ([bluebubbles.app](https://bluebubbles.app))。
- 推荐/已测试：macOS Sequoia (15)。macOS Tahoe (26) 可用；Tahoe 上的编辑功能目前损坏，群组图标更新可能报告成功但不同步。
- OpenClaw 通过其 REST API 与其通信 (`GET /api/v1/ping`, `POST /message/text`, `POST /chat/:id/*`)。
- 传入消息通过 webhooks 到达；传出回复、输入指示器、已读回执和 tapbacks 是 REST 调用。
- 附件和贴纸作为传入媒体被摄取（并在可能时呈现给代理）。
- 配对/白名单工作方式与其他通道相同 (`/channels/pairing` 等)，配合 `channels.bluebubbles.allowFrom` + 配对代码。
- 反应像 Slack/Telegram 一样作为系统事件呈现，以便代理可以在回复前“提及”它们。
- 高级功能：编辑、取消发送、回复线程、消息效果、群组管理。

## Quick start

1. 在你的 Mac 上安装 BlueBubbles 服务器（遵循 [bluebubbles.app/install](https://bluebubbles.app/install) 的说明）。
2. 在 BlueBubbles 配置中，启用 Web API 并设置密码。
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

4. 将 BlueBubbles webhooks 指向你的网关（示例：`https://your-gateway-host:3000/bluebubbles-webhook?password=<password>`）。
5. 启动网关；它将注册 webhook 处理程序并开始配对。

Security note:

- 始终设置 webhook 密码。
- 始终需要 webhook 身份验证。除非请求包含与 `channels.bluebubbles.password` 匹配的密码/guid（例如 `?password=<password>` 或 `x-password`），否则 OpenClaw 会拒绝 BlueBubbles webhook 请求，无论回环/代理拓扑如何。
- 密码身份验证在读取/解析完整 webhook 主体之前进行检查。

## Keeping Messages.app alive (VM / headless setups)

一些 macOS VM / 常开设置可能导致 Messages.app 进入“空闲”状态（传入事件停止直到应用被打开/前置）。一个简单的解决方法是使用 AppleScript + LaunchAgent **每 5 分钟“戳”一下 Messages**。

### 1) Save the AppleScript

保存为：

- `~/Scripts/poke-messages.scpt`

示例脚本（非交互；不抢占焦点）：

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

### 2) Install a LaunchAgent

保存为：

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

注意：

- 这每 300 秒运行一次并在登录时运行。
- 首次运行可能会触发 macOS **自动化**提示 (`osascript` → Messages)。在与运行 LaunchAgent 相同的用户会话中批准它们。

加载它：

```bash
launchctl unload ~/Library/LaunchAgents/com.user.poke-messages.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.user.poke-messages.plist
```

## Onboarding

BlueBubbles 可在交互式设置向导中使用：

```
openclaw onboard
```

向导提示输入：

- **服务器 URL**（必需）：BlueBubbles 服务器地址（例如 `http://192.168.1.100:1234`）
- **密码**（必需）：来自 BlueBubbles 服务器设置的 API 密码
- **Webhook 路径**（可选）：默认为 `/bluebubbles-webhook`
- **DM 策略**：配对、白名单、开放或禁用
- **允许列表**：电话号码、电子邮件或聊天目标

你也可以通过 CLI 添加 BlueBubbles：

```
openclaw channels add bluebubbles --http-url http://192.168.1.100:1234 --password <password>
```

## Access control (DMs + groups)

DMs:

- 默认：`channels.bluebubbles.dmPolicy = "pairing"`。
- 未知发件人收到配对代码；消息会被忽略直到批准（代码 1 小时后过期）。
- 通过以下方式批准：
  - `openclaw pairing list bluebubbles`
  - `openclaw pairing approve bluebubbles <CODE>`
- 配对是默认的令牌交换。详情：[Pairing](/channels/pairing)

Groups:

- `channels.bluebubbles.groupPolicy = open | allowlist | disabled`（默认：`allowlist`）。
- 当设置 `allowlist` 时，`channels.bluebubbles.groupAllowFrom` 控制谁可以在群组中触发。

### Mention gating (groups)

BlueBubbles 支持群聊的提及门控，匹配 iMessage/WhatsApp 行为：

- 使用 `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）检测提及。
- 当为群组启用 `requireMention` 时，代理仅在被提及时响应。
- 来自授权发件人的控制命令绕过提及门控。

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

### Command gating

- 控制命令（例如 `/config`, `/model`）需要授权。
- 使用 `allowFrom` 和 `groupAllowFrom` 确定命令授权。
- 授权发件人可以在不提及的情况下运行控制命令。

## Typing + read receipts

- **输入指示器**：在生成响应之前和期间自动发送。
- **已读回执**：由 `channels.bluebubbles.sendReadReceipts` 控制（默认：`true`）。
- **输入指示器**：OpenClaw 发送输入开始事件；BlueBubbles 在发送或超时后自动清除输入（通过 DELETE 手动停止不可靠）。

```json5
{
  channels: {
    bluebubbles: {
      sendReadReceipts: false, // disable read receipts
    },
  },
}
```

## Advanced actions

当在配置中启用时，BlueBubbles 支持高级消息操作：

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

- **react**：添加/移除 tapback 反应 (`messageId`, `emoji`, `remove`)
- **edit**：编辑已发送的消息 (`messageId`, `text`)
- **unsend**：取消发送消息 (`messageId`)
- **reply**：回复特定消息 (`messageId`, `text`, `to`)
- **sendWithEffect**：带 iMessage 效果发送 (`text`, `to`, `effectId`)
- **renameGroup**：重命名群聊 (`chatGuid`, `displayName`)
- **setGroupIcon**：设置群聊图标/照片 (`chatGuid`, `media`) — macOS 26 Tahoe 上不稳定（API 可能返回成功但图标不同步）。
- **addParticipant**：向群组添加某人 (`chatGuid`, `address`)
- **removeParticipant**：从群组移除某人 (`chatGuid`, `address`)
- **leaveGroup**：离开群聊 (`chatGuid`)
- **sendAttachment**：发送媒体/文件 (`to`, `buffer`, `filename`, `asVoice`)
  - 语音备忘录：设置 `asVoice: true` 为 **MP3** 或 **CAF** 音频以作为 iMessage 语音消息发送。BlueBubbles 在发送语音备忘录时将 MP3 转换为 CAF。

### Message IDs (short vs full)

OpenClaw 可能会显示短消息 ID（例如 `1`, `2`）以节省令牌。

- `MessageSid` / `ReplyToId` 可以是短 ID。
- `MessageSidFull` / `ReplyToIdFull` 包含提供商的全 ID。
- 短 ID 在内存中；重启或缓存驱逐时可能过期。
- 操作接受短或全 `messageId`，但如果不再可用则短 ID 会报错。

对于持久化自动化和存储使用全 ID：

- 模板：`{{MessageSidFull}}`, `{{ReplyToIdFull}}`
- 上下文：入站负载中的 `MessageSidFull` / `ReplyToIdFull`

参见 [Configuration](/gateway/configuration) 了解模板变量。

## Block streaming

控制响应是作为单条消息发送还是分块流式传输：

```json5
{
  channels: {
    bluebubbles: {
      blockStreaming: true, // enable block streaming (off by default)
    },
  },
}
```

## Media + limits

- 传入附件被下载并存储在媒体缓存中。
- 通过 `channels.bluebubbles.mediaMaxMb` 限制传入和传出媒体的容量（默认：8 MB）。
- 传出文本分块至 `channels.bluebubbles.textChunkLimit`（默认：4000 字符）。

## Configuration reference

完整配置：[Configuration](/gateway/configuration)

提供者选项：

- `channels.bluebubbles.enabled`: 启用/禁用通道。
- `channels.bluebubbles.serverUrl`: BlueBubbles REST API 基础 URL。
- `channels.bluebubbles.password`: API 密码。
- `channels.bluebubbles.webhookPath`: Webhook 端点路径（默认：`/bluebubbles-webhook`）。
- `channels.bluebubbles.dmPolicy`: `pairing | allowlist | open | disabled`（默认：`pairing`）。
- `channels.bluebubbles.allowFrom`: DM 允许列表（句柄、电子邮件、E.164 号码、`chat_id:*`、`chat_guid:*`）。
- `channels.bluebubbles.groupPolicy`: `open | allowlist | disabled`（默认：`allowlist`）。
- `channels.bluebubbles.groupAllowFrom`: 群组发送者允许列表。
- `channels.bluebubbles.groups`: 按组配置（`requireMention` 等）。
- `channels.bluebubbles.sendReadReceipts`: 发送已读回执（默认：`true`）。
- `channels.bluebubbles.blockStreaming`: 启用分块流式传输（默认：`false`；流式回复必需）。
- `channels.bluebubbles.textChunkLimit`: 出站分块大小（字符数，默认：4000）。
- `channels.bluebubbles.chunkMode`: `length`（默认）仅在超过 `textChunkLimit` 时拆分；`newline` 在长度分块前按空行（段落边界）拆分。
- `channels.bluebubbles.mediaMaxMb`: 入站/出站媒体限制（MB，默认：8）。
- `channels.bluebubbles.mediaLocalRoots`: 出站本地媒体路径允许的绝对本地目录显式允许列表。除非配置此项，否则默认拒绝本地路径发送。账户级覆盖：`channels.bluebubbles.accounts.<accountId>.mediaLocalRoots`。
- `channels.bluebubbles.historyLimit`: 上下文最大群组消息数（0 为禁用）。
- `channels.bluebubbles.dmHistoryLimit`: DM 历史记录限制。
- `channels.bluebubbles.actions`: 启用/禁用特定操作。
- `channels.bluebubbles.accounts`: 多账户配置。

相关全局选项：

- `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）。
- `messages.responsePrefix`。

## 寻址 / 交付目标

首选 `chat_guid` 以实现稳定路由：

- `chat_guid:iMessage;-;+15555550123`（群组首选）
- `chat_id:123`
- `chat_identifier:...`
- 直接句柄：`+15555550123`、`user@example.com`
  - 如果直接句柄没有现有的 DM 聊天，OpenClaw 将通过 `POST /api/v1/chat/new` 创建一个。这需要启用 BlueBubbles Private API。

## 安全

- Webhook 请求通过比较 `guid`/`password` 查询参数或标头与 `channels.bluebubbles.password` 进行身份验证。来自 `localhost` 的请求也被接受。
- 保持 API 密码和 Webhook 端点机密（将其视为凭据）。
- 本地主机信任意味着同一主机的反向代理可能会无意绕过密码。如果您代理网关，请在代理处要求身份验证并配置 `gateway.trustedProxies`。请参阅 [网关安全](/gateway/security#reverse-proxy-configuration)。
- 如果在 LAN 之外暴露 BlueBubbles 服务器，请启用 HTTPS + 防火墙规则。

## 故障排除

- 如果输入/已读事件停止工作，请检查 BlueBubbles webhook 日志并验证网关路径是否匹配 `channels.bluebubbles.webhookPath`。
- 配对码一小时后过期；请使用 `openclaw pairing list bluebubbles` 和 `openclaw pairing approve bluebubbles <code>`。
- 反应需要 BlueBubbles 私有 API（`POST /api/v1/message/react`）；请确保服务器版本公开了它。
- 编辑/撤回需要 macOS 13+ 及兼容的 BlueBubbles 服务器版本。在 macOS 26 (Tahoe) 上，由于私有 API 更改，编辑功能目前损坏。
- 群组图标更新在 macOS 26 (Tahoe) 上可能不稳定：API 可能返回成功，但新图标不同步。
- OpenClaw 根据 BlueBubbles 服务器的 macOS 版本自动隐藏已知损坏的操作。如果编辑功能仍在 macOS 26 (Tahoe) 上显示，请使用 `channels.bluebubbles.actions.edit=false` 手动禁用它。
- 对于状态/健康信息：`openclaw status --all` 或 `openclaw status --deep`。

有关常规通道工作流程参考，请参阅 [渠道](/channels) 和 [插件](/tools/plugin) 指南。