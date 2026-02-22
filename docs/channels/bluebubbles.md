---
summary: "iMessage via BlueBubbles macOS server (REST send/receive, typing, reactions, pairing, advanced actions)."
read_when:
  - Setting up BlueBubbles channel
  - Troubleshooting webhook pairing
  - Configuring iMessage on macOS
title: "BlueBubbles"
---
# BlueBubbles (macOS REST)

状态：捆绑插件，通过HTTP与BlueBubbles macOS服务器通信。**推荐用于iMessage集成**，因为它具有更丰富的API和比旧版imsg通道更容易的设置。

## 概述

- 通过BlueBubbles辅助应用程序（[bluebubbles.app](https://bluebubbles.app)）在macOS上运行。
- 推荐/测试：macOS Sequoia (15)。macOS Tahoe (26)可以工作；Tahoe上的编辑当前已损坏，群组图标更新可能会报告成功但不同步。
- OpenClaw通过其REST API与其通信 (`GET /api/v1/ping`, `POST /message/text`, `POST /chat/:id/*`)。
- 收到的消息通过webhooks到达；发送的回复、输入指示器、已读回执和tapbacks是REST调用。
- 附件和贴纸作为传入媒体处理（并在可能的情况下提供给代理）。
- 配对/允许列表与其他通道的工作方式相同 (`/channels/pairing` 等)，使用 `channels.bluebubbles.allowFrom` + 配对码。
- 反应作为系统事件显示，就像Slack/Telegram一样，因此代理可以在回复之前“提及”它们。
- 高级功能：编辑、撤回、回复线程、消息效果、群组管理。

## 快速入门

1. 在Mac上安装BlueBubbles服务器（按照[bluebubbles.app/install](https://bluebubbles.app/install)上的说明操作）。
2. 在BlueBubbles配置中启用Web API并设置密码。
3. 运行 `openclaw onboard` 并选择BlueBubbles，或者手动配置：

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

4. 将BlueBubbles webhooks指向您的网关（示例：`https://your-gateway-host:3000/bluebubbles-webhook?password=<password>`）。
5. 启动网关；它将注册webhook处理程序并开始配对。

安全注意事项：

- 始终设置webhook密码。
- Webhook身份验证始终是必需的。OpenClaw拒绝不包含与 `channels.bluebubbles.password` 匹配的密码/guid的BlueBubbles webhook请求（例如 `?password=<password>` 或 `x-password`），无论loopback/proxy拓扑如何。

## 保持Messages.app活跃（虚拟机/无头设置）

某些macOS虚拟机/始终在线设置可能导致Messages.app进入“空闲”状态（传入事件停止，直到应用程序被打开/置于前台）。一个简单的解决方法是**每5分钟使用AppleScript + LaunchAgent“唤醒”Messages**。

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

注意事项：

- 此操作每**300秒**执行一次，并在**登录时**执行。
- 第一次运行可能会触发macOS **自动化**提示 (`osascript` → 消息)。请在同一用户会话中批准这些提示。

加载方式：

```bash
launchctl unload ~/Library/LaunchAgents/com.user.poke-messages.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.user.poke-messages.plist
```

## 入门

BlueBubbles可在交互式设置向导中使用：

```
openclaw onboard
```

向导会提示您输入以下信息：

- **服务器URL** (必填)：BlueBubbles服务器地址（例如，`http://192.168.1.100:1234`）
- **密码** (必填)：来自BlueBubbles服务器设置的API密码
- **Webhook路径** (可选)：默认为`/bluebubbles-webhook`
- **DM策略**：配对、允许列表、开放或禁用
- **允许列表**：电话号码、电子邮件或聊天目标

您也可以通过CLI添加BlueBubbles：

```
openclaw channels add bluebubbles --http-url http://192.168.1.100:1234 --password <password>
```

## 访问控制（DM + 群组）

DM：

- 默认：`channels.bluebubbles.dmPolicy = "pairing"`。
- 未知发送者会收到一个配对码；消息会被忽略直到批准（配对码在1小时后过期）。
- 批准方式：
  - `openclaw pairing list bluebubbles`
  - `openclaw pairing approve bluebubbles <CODE>`
- 配对是默认的令牌交换方式。详情：[配对](/channels/pairing)

群组：

- `channels.bluebubbles.groupPolicy = open | allowlist | disabled` (默认：`allowlist`)。
- `channels.bluebubbles.groupAllowFrom` 控制当`allowlist`设置时谁可以在群组中触发。

### 提及限制（群组）

BlueBubbles支持群聊中的提及限制，与iMessage/WhatsApp行为匹配：

- 使用`agents.list[].groupChat.mentionPatterns` (或`messages.groupChat.mentionPatterns`)检测提及。
- 当`requireMention`为群组启用时，代理仅在被提及时响应。
- 授权发送者的控制命令会绕过提及限制。

每个群组的配置：

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

- 控制命令（例如，`/config`, `/model`）需要授权。
- 使用 `allowFrom` 和 `groupAllowFrom` 来确定命令授权。
- 授权的发送者即使不在群组中提及也可以运行控制命令。

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

- **react**：添加/移除轻触反应 (`messageId`, `emoji`, `remove`)
- **edit**：编辑已发送的消息 (`messageId`, `text`)
- **unsend**：撤回消息 (`messageId`)
- **reply**：回复特定消息 (`messageId`, `text`, `to`)
- **sendWithEffect**：使用 iMessage 效果发送 (`text`, `to`, `effectId`)
- **renameGroup**：重命名群组聊天 (`chatGuid`, `displayName`)
- **setGroupIcon**：设置群组聊天的图标/照片 (`chatGuid`, `media`) — 在 macOS 26 Tahoe 上不稳定（API 可能返回成功但图标不会同步）。
- **addParticipant**：将某人添加到群组 (`chatGuid`, `address`)
- **removeParticipant**：从群组中移除某人 (`chatGuid`, `address`)
- **leaveGroup**：离开群组聊天 (`chatGuid`)
- **sendAttachment**：发送媒体/文件 (`to`, `buffer`, `filename`, `asVoice`)
  - 语音备忘录：设置 `asVoice: true` 为 **MP3** 或 **CAF** 音频以作为 iMessage 语音消息发送。BlueBubbles 在发送语音备忘录时将 MP3 转换为 CAF。

### 消息 ID（短 vs 全）

OpenClaw 可能会显示 _短_ 消息 ID（例如，`1`, `2`）以节省令牌。

- `MessageSid` / `ReplyToId` 可以是短ID。
- `MessageSidFull` / `ReplyToIdFull` 包含提供商的完整ID。
- 短ID存储在内存中；它们可能在重启或缓存失效时过期。
- 动作接受短或完整的 `messageId`，但如果短ID不再可用，则会出错。

使用完整ID用于持久化自动化和存储：

- 模板：`{{MessageSidFull}}`, `{{ReplyToIdFull}}`
- 上下文：入站负载中的 `MessageSidFull` / `ReplyToIdFull`

参见 [Configuration](/gateway/configuration) 了解模板变量。

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
- 媒体大小限制通过 `channels.bluebubbles.mediaMaxMb` 设置（默认：8 MB）。
- 出站文本会被分块为 `channels.bluebubbles.textChunkLimit`（默认：4000 字符）。

## 配置参考

完整配置：[Configuration](/gateway/configuration)

提供商选项：

- `channels.bluebubbles.enabled`: 启用/禁用通道。
- `channels.bluebubbles.serverUrl`: BlueBubbles REST API 基础URL。
- `channels.bluebubbles.password`: API 密码。
- `channels.bluebubbles.webhookPath`: Webhook 端点路径（默认：`/bluebubbles-webhook`）。
- `channels.bluebubbles.dmPolicy`: `pairing | allowlist | open | disabled`（默认：`pairing`）。
- `channels.bluebubbles.allowFrom`: DM 允许列表（句柄、电子邮件、E.164 号码、`chat_id:*`、`chat_guid:*`）。
- `channels.bluebubbles.groupPolicy`: `open | allowlist | disabled`（默认：`allowlist`）。
- `channels.bluebubbles.groupAllowFrom`: 群组发送者允许列表。
- `channels.bluebubbles.groups`: 按群组配置 (`requireMention` 等）。
- `channels.bluebubbles.sendReadReceipts`: 发送已读回执（默认：`true`）。
- `channels.bluebubbles.blockStreaming`: 启用块流式传输（默认：`false`；流式回复所需）。
- `channels.bluebubbles.textChunkLimit`: 出站分块大小（字符数，默认：4000）。
- `channels.bluebubbles.chunkMode`: `length`（默认）仅在超过 `textChunkLimit` 时拆分；`newline` 在长度分块之前按空白行（段落边界）拆分。
- `channels.bluebubbles.mediaMaxMb`: 入站媒体大小限制（MB，默认：8）。
- `channels.bluebubbles.mediaLocalRoots`: 明确允许的绝对本地目录列表，允许用于出站本地媒体路径。默认情况下，除非配置，否则本地路径发送会被拒绝。按账户覆盖：`channels.bluebubbles.accounts.<accountId>.mediaLocalRoots`。
- `channels.bluebubbles.historyLimit`: 上下文中的最大群组消息数（0 表示禁用）。
- `channels.bluebubbles.dmHistoryLimit`: DM 历史记录限制。
- `channels.bluebubbles.actions`: 启用/禁用特定操作。
- `channels.bluebubbles.accounts`: 多账户配置。

相关全局选项：

## 地址/交付目标

优先使用 `chat_guid` 进行稳定路由：

- `chat_guid:iMessage;-;+15555550123`（适用于群组）
- `chat_id:123`
- `chat_identifier:...`
- 直接句柄：`+15555550123`, `user@example.com`
  - 如果直接句柄没有现有的DM聊天，OpenClaw 将通过 `POST /api/v1/chat/new` 创建一个。这需要启用 BlueBubbles 私有 API。

## 安全

- Webhook 请求通过比较 `guid`/`password` 查询参数或头信息与 `channels.bluebubbles.password` 进行身份验证。也接受来自 `localhost` 的请求。
- 保持 API 密码和 webhook 端点的秘密（像对待凭据一样处理它们）。
- 本地主机信任意味着同一主机的反向代理可能会无意中绕过密码。如果代理网关，请在代理处要求身份验证并配置 `gateway.trustedProxies`。参见 [网关安全](/gateway/security#reverse-proxy-configuration)。
- 如果在局域网外暴露 BlueBubbles 服务器，请在服务器上启用 HTTPS + 防火墙规则。

## 故障排除

- 如果输入/读取事件停止工作，请检查 BlueBubbles webhook 日志并验证网关路径是否匹配 `channels.bluebubbles.webhookPath`。
- 配对码在一小时后过期；使用 `openclaw pairing list bluebubbles` 和 `openclaw pairing approve bluebubbles <code>`。
- 反应需要 BlueBubbles 私有 API (`POST /api/v1/message/react`)；确保服务器版本提供它。
- 编辑/撤回需要 macOS 13+ 和兼容的 BlueBubbles 服务器版本。在 macOS 26 (Tahoe) 上，由于私有 API 更改，编辑当前已损坏。
- 在 macOS 26 (Tahoe) 上，群组图标更新可能不稳定：API 可能返回成功但新图标不会同步。
- OpenClaw 根据 BlueBubbles 服务器的 macOS 版本自动隐藏已知有问题的操作。如果在 macOS 26 (Tahoe) 上仍然显示编辑，请使用 `channels.bluebubbles.actions.edit=false` 手动禁用它。
- 有关状态/健康信息：`openclaw status --all` 或 `openclaw status --deep`。

有关常规频道工作流程的参考，请参见 [频道](/channels) 和 [插件](/tools/plugin) 指南。