---
summary: "iMessage via BlueBubbles macOS server (REST send/receive, typing, reactions, pairing, advanced actions)."
read_when:
  - Setting up BlueBubbles channel
  - Troubleshooting webhook pairing
  - Configuring iMessage on macOS
title: "BlueBubbles"
---
# BlueBubbles (macOS REST)

状态: 内置插件，通过HTTP与BlueBubbles macOS服务器通信。**推荐用于iMessage集成**，因为它具有更丰富的API和比旧版imsg通道更容易的设置。

## 概述

- 通过BlueBubbles辅助应用程序([bluebubbles.app](https://bluebubbles.app))在macOS上运行。
- 推荐/测试版本: macOS Sequoia (15)。macOS Tahoe (26)可以工作；Tahoe上的编辑功能目前无法使用，群组图标更新可能报告成功但不同步。
- OpenClaw通过其REST API与其通信 (`GET /api/v1/ping`, `POST /message/text`, `POST /chat/:id/*`)。
- 收到的消息通过webhook到达；发送的回复、输入指示器、已读回执和tapbacks是REST调用。
- 附件和贴纸作为传入媒体处理（并在可能的情况下提供给代理）。
- 配对/白名单与其他通道(`/start/pairing`等)相同，使用`channels.bluebubbles.allowFrom` + 配对码。
- 反应作为系统事件显示，就像Slack/Telegram一样，因此代理可以在回复之前“提及”它们。
- 高级功能: 编辑、撤回、回复线程、消息效果、群组管理。

## 快速开始

1. 在Mac上安装BlueBubbles服务器（按照[bluebubbles.app/install](https://bluebubbles.app/install)上的说明操作）。
2. 在BlueBubbles配置中启用Web API并设置密码。
3. 运行`openclaw onboard`并选择BlueBubbles，或者手动配置：
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
4. 将BlueBubbles webhook指向您的网关（示例: `https://your-gateway-host:3000/bluebubbles-webhook?password=<password>`）。
5. 启动网关；它将注册webhook处理程序并开始配对。

## 保持Messages.app活跃（虚拟机/无头设置）

某些macOS虚拟机/始终在线设置可能导致Messages.app进入“空闲”状态（传入事件停止直到应用程序打开/置于前台）。一个简单的解决方法是**每5分钟poke一下Messages**，使用AppleScript + LaunchAgent。

### 1) 保存AppleScript

将其保存为：

- `~/Scripts/poke-messages.scpt`

示例脚本（非交互式；不会窃取焦点）：

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

### 2) 安装LaunchAgent

将其保存为：

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

Notes:

- This runs **every 300 seconds** and **on login**.
- The first run may trigger macOS **Automation** prompts (`osascript` → Messages). Approve them in the same user session that runs the LaunchAgent.

Load it:

```bash
launchctl unload ~/Library/LaunchAgents/com.user.poke-messages.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.user.poke-messages.plist
```

## Onboarding

BlueBubbles is available in the interactive setup wizard:

```
openclaw onboard
```

The wizard prompts for:

- **Server URL** (required): BlueBubbles server address (e.g., `http://192.168.1.100:1234`)
- **Password** (required): API password from BlueBubbles Server settings
- **Webhook path** (optional): Defaults to `/bluebubbles-webhook`
- **DM policy**: pairing, allowlist, open, or disabled
- **Allow list**: Phone numbers, emails, or chat targets

You can also add BlueBubbles via CLI:

```
openclaw channels add bluebubbles --http-url http://192.168.1.100:1234 --password <password>
```

## Access control (DMs + groups)

DMs:

- Default: `channels.bluebubbles.dmPolicy = "pairing"`.
- Unknown senders receive a pairing code; messages are ignored until approved (codes expire after 1 hour).
- Approve via:
  - `openclaw pairing list bluebubbles`
  - `openclaw pairing approve bluebubbles <CODE>`
- Pairing is the default token exchange. Details: [Pairing](/start/pairing)

Groups:

- `channels.bluebubbles.groupPolicy = open | allowlist | disabled` (default: `allowlist`).
- `channels.bluebubbles.groupAllowFrom` controls who can trigger in groups when `allowlist` is set.

### Mention gating (groups)

BlueBubbles supports mention gating for group chats, matching iMessage/WhatsApp behavior:

- Uses `agents.list[].groupChat.mentionPatterns` (or `messages.groupChat.mentionPatterns`) to detect mentions.
- When `requireMention` is enabled for a group, the agent only responds when mentioned.
- Control commands from authorized senders bypass mention gating.

Per-group configuration:

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

- 控制命令（例如，`/config`，`/model`）需要授权。
- 使用 `allowFrom` 和 `groupAllowFrom` 来确定命令授权。
- 授权的发送者即使在群组中未提及也可以运行控制命令。

## 输入 + 已读回执

- **输入指示器**：在响应生成之前和期间自动发送。
- **已读回执**：由 `channels.bluebubbles.sendReadReceipts` 控制（默认：`true`）。
- **输入指示器**：OpenClaw 发送输入开始事件；BlueBubbles 在发送或超时时自动清除输入（通过 DELETE 手动停止不可靠）。

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

- **react**：添加/移除轻触反应 (`messageId`，`emoji`，`remove`)
- **edit**：编辑已发送的消息 (`messageId`，`text`)
- **unsend**：撤回消息 (`messageId`)
- **reply**：回复特定消息 (`messageId`，`text`，`to`)
- **sendWithEffect**：使用 iMessage 效果发送 (`text`，`to`，`effectId`)
- **renameGroup**：重命名群组聊天 (`chatGuid`，`displayName`)
- **setGroupIcon**：设置群组聊天的图标/照片 (`chatGuid`，`media`) — 在 macOS 26 Tahoe 上可能不稳定（API 可能返回成功但图标不会同步）。
- **addParticipant**：将某人添加到群组 (`chatGuid`，`address`)
- **removeParticipant**：从群组中移除某人 (`chatGuid`，`address`)
- **leaveGroup**：离开群组聊天 (`chatGuid`)
- **sendAttachment**：发送媒体/文件 (`to`，`buffer`，`filename`，`asVoice`)
  - 语音备忘录：设置 `asVoice: true` 为 **MP3** 或 **CAF** 音频以作为 iMessage 语音消息发送。BlueBubbles 在发送语音备忘录时将 MP3 转换为 CAF。

### 消息 ID（短 vs 长）

OpenClaw 可能会显示 _短_ 消息 ID（例如，`1`，`2`）以节省令牌。

- `MessageSid` / `ReplyToId` 可以是短 ID。
- `MessageSidFull` / `ReplyToIdFull` 包含提供商的完整 ID。
- 短 ID 存在于内存中；它们可能会在重启或缓存清除时过期。
- 操作接受短或完整的 `messageId`，但如果短 ID 不再可用，则会出错。

使用完整 ID 进行持久化自动化和存储：

- 模板: `{{MessageSidFull}}`, `{{ReplyToIdFull}}`
- 上下文: `MessageSidFull` / `ReplyToIdFull` 在入站负载中

有关模板变量，请参阅[配置](/gateway/configuration)。

## 块流式传输

控制响应是以单个消息发送还是以块的形式流式传输：

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

- 入站附件会被下载并存储在媒体缓存中。
- 媒体容量通过 `channels.bluebubbles.mediaMaxMb` 限制（默认：8 MB）。
- 出站文本会被分块为 `channels.bluebubbles.textChunkLimit`（默认：4000 字符）。

## 配置参考

完整配置：[配置](/gateway/configuration)

提供商选项：

- `channels.bluebubbles.enabled`: 启用/禁用通道。
- `channels.bluebubbles.serverUrl`: BlueBubbles REST API 基础 URL。
- `channels.bluebubbles.password`: API 密码。
- `channels.bluebubbles.webhookPath`: Webhook 端点路径（默认：`/bluebubbles-webhook`）。
- `channels.bluebubbles.dmPolicy`: `pairing | allowlist | open | disabled`（默认：`pairing`）。
- `channels.bluebubbles.allowFrom`: DM 允许列表（句柄、电子邮件、E.164 号码、`chat_id:*`、`chat_guid:*`）。
- `channels.bluebubbles.groupPolicy`: `open | allowlist | disabled`（默认：`allowlist`）。
- `channels.bluebubbles.groupAllowFrom`: 群组发件人允许列表。
- `channels.bluebubbles.groups`: 按群组配置（`requireMention` 等）。
- `channels.bluebubbles.sendReadReceipts`: 发送已读回执（默认：`true`）。
- `channels.bluebubbles.blockStreaming`: 启用块流式传输（默认：`false`；流式回复所需）。
- `channels.bluebubbles.textChunkLimit`: 出站分块大小（字符数，默认：4000）。
- `channels.bluebubbles.chunkMode`: `length`（默认）仅在超过 `textChunkLimit` 时拆分；`newline` 在长度分块之前按空白行（段落边界）拆分。
- `channels.bluebubbles.mediaMaxMb`: 入站媒体容量（MB，默认：8）。
- `channels.bluebubbles.historyLimit`: 上下文中的最大群组消息数（0 表示禁用）。
- `channels.bluebubbles.dmHistoryLimit`: DM 历史记录限制。
- `channels.bluebubbles.actions`: 启用/禁用特定操作。
- `channels.bluebubbles.accounts`: 多账户配置。

相关全局选项：

- `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）。
- `messages.responsePrefix`。

## 地址化 / 交付目标

优先使用 `chat_guid` 进行稳定路由：

- `chat_guid:iMessage;-;+15555550123`（群组优先）
- `chat_id:123`
- `chat_identifier:...`
- 直接句柄：`+15555550123`，`user@example.com`
  - 如果直接句柄没有现有的 DM 聊天，OpenClaw 将通过 `POST /api/v1/chat/new` 创建一个。这需要启用 BlueBubbles 私有 API。

## 安全性

- Webhook 请求通过比较 `guid`/`password` 查询参数或头与 `channels.bluebubbles.password` 进行身份验证。来自 `localhost` 的请求也会被接受。
- 保持 API 密码和 webhook 端点的秘密（像对待凭据一样处理它们）。
- 本地主机信任意味着同一主机的反向代理可能会无意中绕过密码验证。如果您代理网关，请在代理处要求身份验证并配置 `gateway.trustedProxies`。参见 [网关安全](/gateway/security#reverse-proxy-configuration)。
- 如果在局域网外暴露 BlueBubbles 服务器，请在 BlueBubbles 服务器上启用 HTTPS + 防火墙规则。

## 故障排除

- 如果输入/读取事件停止工作，请检查 BlueBubbles webhook 日志并验证网关路径是否匹配 `channels.bluebubbles.webhookPath`。
- 配对码在一小时后过期；使用 `openclaw pairing list bluebubbles` 和 `openclaw pairing approve bluebubbles <code>`。
- 反应需要 BlueBubbles 私有 API (`POST /api/v1/message/react`)；确保服务器版本暴露了它。
- 编辑/撤回需要 macOS 13+ 和兼容的 BlueBubbles 服务器版本。在 macOS 26 (Tahoe) 上，由于私有 API 的更改，编辑当前已损坏。
- 在 macOS 26 (Tahoe) 上，群组图标更新可能不稳定：API 可能返回成功但新图标不会同步。
- OpenClaw 根据 BlueBubbles 服务器的 macOS 版本自动隐藏已知有问题的操作。如果在 macOS 26 (Tahoe) 上编辑仍然出现，请手动禁用它 `channels.bluebubbles.actions.edit=false`。
- 获取状态/健康信息：`openclaw status --all` 或 `openclaw status --deep`。

有关通用频道工作流程的参考，请参见 [Channels](/channels) 和 [Plugins](/plugins) 指南。