---
summary: "iMessage via BlueBubbles macOS server (REST send/receive, typing, reactions, pairing, advanced actions)."
read_when:
  - Setting up BlueBubbles channel
  - Troubleshooting webhook pairing
  - Configuring iMessage on macOS
title: "BlueBubbles"
---
# BlueBubbles (macOS REST)

状态：捆绑插件，通过 HTTP 与 BlueBubbles macOS 服务器通信。**推荐用于 iMessage 集成**，因为其 API 更丰富，且相比旧的 imsg 通道设置更简单。

## 捆绑插件

当前 OpenClaw 版本已捆绑 BlueBubbles，因此常规打包构建不需要单独的 `openclaw plugins install` 步骤。

## 概述

- 通过 BlueBubbles 辅助应用程序在 macOS 上运行（[bluebubbles.app](https://bluebubbles.app)）。
- 推荐/测试版本：macOS Sequoia (15)。macOS Tahoe (26) 可用；但在 Tahoe 上编辑功能目前存在故障，群组图标更新可能报告成功但不同步。
- OpenClaw 通过其 REST API 与其通信（`GET /api/v1/ping`，`POST /message/text`，`POST /chat/:id/*`）。
- 传入消息通过 webhooks 到达；传出回复、输入指示器、已读回执和 tapbacks 均为 REST 调用。
- 附件和贴纸作为传入媒体被摄取（并在可能时展示给代理）。
- 配对/白名单的工作方式与其他通道相同（`/channels/pairing` 等），使用 `channels.bluebubbles.allowFrom` + 配对码。
- 反应像 Slack/Telegram 一样作为系统事件展示，以便代理可以在回复前“提及”它们。
- 高级功能：编辑、撤回、回复线程、消息效果、群组管理。

## 快速开始

1. 在您的 Mac 上安装 BlueBubbles 服务器（按照 [bluebubbles.app/install](https://bluebubbles.app/install) 上的说明操作）。
2. 在 BlueBubbles 配置中，启用 web API 并设置密码。
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

4. 将 BlueBubbles webhooks 指向您的网关（示例：`https://your-gateway-host:3000/bluebubbles-webhook?password=<password>`）。
5. 启动网关；它将注册 webhook 处理器并开始配对。

安全提示：

- 始终设置 webhook 密码。
- 始终需要 webhook 身份验证。除非包含与 `channels.bluebubbles.password` 匹配的密码/guid（例如 `?password=<password>` 或 `x-password`），否则 OpenClaw 会拒绝 BlueBubbles webhook 请求，无论 loopback/代理拓扑如何。
- 在读取/解析完整 webhook 主体之前会检查密码身份验证。

## 保持 Messages.app 存活（VM / 无头设置）

某些 macOS VM / 常开设置可能会导致 Messages.app 进入“空闲”状态（传入事件停止，直到应用程序被打开/置于前台）。一个简单的解决方法是使用 AppleScript + LaunchAgent **每 5 分钟唤醒一次 Messages**。

### 1) 保存 AppleScript

另存为：

- `~/Scripts/poke-messages.scpt`

示例脚本（非交互式；不窃取焦点）：

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

### 2) 安装 LaunchAgent

另存为：

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

- 此任务 **每 300 秒** 运行一次，并在 **登录时** 运行。
- 首次运行可能会触发 macOS **自动化** 提示（`osascript` → Messages）。请在运行 LaunchAgent 的同一用户会话中批准它们。

加载它：

```bash
launchctl unload ~/Library/LaunchAgents/com.user.poke-messages.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.user.poke-messages.plist
```

## 入门引导

BlueBubbles 可在交互式入门引导中使用：

```
openclaw onboard
```

向导提示输入：

- **服务器 URL**（必需）：BlueBubbles 服务器地址（例如 `http://192.168.1.100:1234`）
- **密码**（必需）：来自 BlueBubbles 服务器设置的 API 密码
- **Webhook 路径**（可选）：默认为 `/bluebubbles-webhook`
- **DM 策略**：配对、白名单、开放或禁用
- **允许列表**：电话号码、电子邮件或聊天目标

您也可以通过 CLI 添加 BlueBubbles：

```
openclaw channels add bluebubbles --http-url http://192.168.1.100:1234 --password <password>
```

## 访问控制（DM + 群组）

DM：

- 默认：`channels.bluebubbles.dmPolicy = "pairing"`。
- 未知发送者会收到一个配对码；消息在被批准前会被忽略（代码 1 小时后过期）。
- 通过以下方式批准：
  - `openclaw pairing list bluebubbles`
  - `openclaw pairing approve bluebubbles <CODE>`
- 配对是默认的令牌交换。详情：[配对](/channels/pairing)

群组：

- `channels.bluebubbles.groupPolicy = open | allowlist | disabled`（默认：`allowlist`）。
- 当设置 `allowlist` 时，`channels.bluebubbles.groupAllowFrom` 控制谁可以在群组中触发。

### 联系人名称增强（macOS，可选）

BlueBubbles 群组 webhooks 通常仅包含原始参与者地址。如果您希望 `GroupMembers` 上下文显示本地联系人名称，您可以选择在 macOS 上进行本地联系人增强：

- `channels.bluebubbles.enrichGroupParticipantsFromContacts = true` 启用查找。默认：`false`。
- 查找仅在群组访问、命令授权和提及门控允许消息通过后运行。
- 仅未命名的电话参与者会被增强。
- 当找不到本地匹配项时，原始电话号码保留为后备。

```json5
{
  channels: {
    bluebubbles: {
      enrichGroupParticipantsFromContacts: true,
    },
  },
}
```

### 提及门控（群组）

BlueBubbles 支持群聊的提及门控，匹配 iMessage/WhatsApp 行为：

- 使用 `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）检测提及。
- 当为群组启用 `requireMention` 时，代理仅在被提及时响应。
- 来自授权发送者的控制命令绕过提及门控。

每群组配置：

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

- 控制命令（例如 `/config`，`/model`）需要授权。
- 使用 `allowFrom` 和 `groupAllowFrom` 确定命令授权。
- 授权发送者即使不在群组中提及也可以运行控制命令。

## ACP 对话绑定

BlueBubbles 聊天可以转换为持久的 ACP 工作区，而无需更改传输层。

快速操作员流程：

- 在 DM 或允许的群聊中运行 `/acp spawn codex --bind here`。
- 该 BlueBubbles 对话中的未来消息将路由到生成的 ACP 会话。
- `/new` 和 `/reset` 就地重置相同的绑定 ACP 会话。
- `/acp close` 关闭 ACP 会话并移除绑定。

配置的持久绑定也通过顶层 `bindings[]` 条目以及 `type: "acp"` 和 `match.channel: "bluebubbles"` 支持。

`match.peer.id` 可以使用任何支持的 BlueBubbles 目标形式：

- 标准化的 DM 句柄，如 `+15555550123` 或 `user@example.com`
- `chat_id:<id>`
- `chat_guid:<guid>`
- `chat_identifier:<identifier>`

对于稳定的群组绑定，建议使用 `chat_id:*` 或 `chat_identifier:*`。

示例：

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: { agent: "codex", backend: "acpx", mode: "persistent" },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "bluebubbles",
        accountId: "default",
        peer: { kind: "dm", id: "+15555550123" },
      },
      acp: { label: "codex-imessage" },
    },
  ],
}
```

有关共享 ACP 绑定行为，请参阅 [ACP Agents](/tools/acp-agents)。

## 输入指示 + 已读回执

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

- **react**: 添加/移除 Tapback 反应 (`messageId`, `emoji`, `remove`)
- **edit**: 编辑已发送的消息 (`messageId`, `text`)
- **unsend**: 撤回消息 (`messageId`)
- **reply**: 回复特定消息 (`messageId`, `text`, `to`)
- **sendWithEffect**: 使用 iMessage 效果发送 (`text`, `to`, `effectId`)
- **renameGroup**: 重命名群聊 (`chatGuid`, `displayName`)
- **setGroupIcon**: 设置群聊图标/照片 (`chatGuid`, `media`) — 在 macOS 26 Tahoe 上不稳定（API 可能返回成功但图标未同步）。
- **addParticipant**: 将某人添加到群组 (`chatGuid`, `address`)
- **removeParticipant**: 从群组中移除某人 (`chatGuid`, `address`)
- **leaveGroup**: 退出群聊 (`chatGuid`)
- **upload-file**: 发送媒体/文件 (`to`, `buffer`, `filename`, `asVoice`)
  - 语音备忘录：设置 `asVoice: true` 为 **MP3** 或 **CAF** 音频以作为 iMessage 语音消息发送。BlueBubbles 在发送语音备忘录时将 MP3 转换为 CAF。
- 旧版别名：`sendAttachment` 仍然有效，但 `upload-file` 是规范的操作名称。

### 消息 ID（短 ID 与完整 ID）

OpenClaw 可能会提供 _短_ 消息 ID（例如 `1`, `2`）以节省 token。

- `MessageSid` / `ReplyToId` 可以是短 ID。
- `MessageSidFull` / `ReplyToIdFull` 包含提供商的完整 ID。
- 短 ID 存储在内存中；它们可能在重启或缓存清除时失效。
- 操作接受短或完整的 `messageId`，但如果短 ID 不再可用则会报错。

对于持久化自动化和存储，请使用完整 ID：

- 模板：`{{MessageSidFull}}`, `{{ReplyToIdFull}}`
- 上下文：入站负载中的 `MessageSidFull` / `ReplyToIdFull`

有关模板变量，请参阅 [配置](/gateway/configuration)。

## 块流式传输

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

## 媒体 + 限制

- 入站附件会被下载并存储在媒体缓存中。
- 通过 `channels.bluebubbles.mediaMaxMb` 限制入站和出站媒体的大小（默认：8 MB）。
- 出站文本被分块至 `channels.bluebubbles.textChunkLimit`（默认：4000 字符）。

## 配置参考

完整配置：[配置](/gateway/configuration)

提供商选项：

- `channels.bluebubbles.enabled`：启用/禁用通道。
- `channels.bluebubbles.serverUrl`：BlueBubbles REST API 基础 URL。
- `channels.bluebubbles.password`：API 密码。
- `channels.bluebubbles.webhookPath`：Webhook 端点路径（默认：`/bluebubbles-webhook`）。
- `channels.bluebubbles.dmPolicy`：`pairing | allowlist | open | disabled`（默认：`pairing`）。
- `channels.bluebubbles.allowFrom`：DM 允许列表（句柄、电子邮件、E.164 号码、`chat_id:*`、`chat_guid:*`）。
- `channels.bluebubbles.groupPolicy`：`open | allowlist | disabled`（默认：`allowlist`）。
- `channels.bluebubbles.groupAllowFrom`：群组发送者允许列表。
- `channels.bluebubbles.enrichGroupParticipantsFromContacts`：在 macOS 上，通过门禁检查后，可选择从本地通讯录丰富无名群组参与者信息。默认：`false`。
- `channels.bluebubbles.groups`：按群组配置（`requireMention` 等）。
- `channels.bluebubbles.sendReadReceipts`：发送已读回执（默认：`true`）。
- `channels.bluebubbles.blockStreaming`：启用块流式传输（默认：`false`；流式回复必需）。
- `channels.bluebubbles.textChunkLimit`：出站分块大小（字符）（默认：4000）。
- `channels.bluebubbles.chunkMode`：`length`（默认）仅在超过 `textChunkLimit` 时分块；`newline` 在长度分块前按空行（段落边界）分块。
- `channels.bluebubbles.mediaMaxMb`：入站/出站媒体上限（MB）（默认：8）。
- `channels.bluebubbles.mediaLocalRoots`：允许用于出站本地媒体路径的绝对本地目录的显式允许列表。除非配置此项，否则默认拒绝本地路径发送。按账户覆盖：`channels.bluebubbles.accounts.<accountId>.mediaLocalRoots`。
- `channels.bluebubbles.historyLimit`：上下文中最大群组消息数（0 表示禁用）。
- `channels.bluebubbles.dmHistoryLimit`：DM 历史记录限制。
- `channels.bluebubbles.actions`：启用/禁用特定操作。
- `channels.bluebubbles.accounts`：多账户配置。

相关全局选项：

- `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）。
- `messages.responsePrefix`。

## 寻址 / 交付目标

优先使用 `chat_guid` 进行稳定路由：

- `chat_guid:iMessage;-;+15555550123`（群组首选）
- `chat_id:123`
- `chat_identifier:...`
- 直接句柄：`+15555550123`, `user@example.com`
  - 如果直接句柄没有现有的 DM 聊天，OpenClaw 将通过 `POST /api/v1/chat/new` 创建一个。这需要启用 BlueBubbles Private API。

## 安全

- Webhook 请求通过将 `guid`/`password` 查询参数或标头与 `channels.bluebubbles.password` 进行比较进行身份验证。
- 请保密 API 密码和 Webhook 端点（将其视为凭据）。
- BlueBubbles Webhook 认证没有 localhost 绕过方式。如果您代理 Webhook 流量，请在请求端到端保持 BlueBubbles 密码。此处 `gateway.trustedProxies` 不替代 `channels.bluebubbles.password`。请参阅 [网关安全](/gateway/security#reverse-proxy-configuration)。
- 如果将 BlueBubbles 服务器暴露到局域网之外，请启用 HTTPS + 防火墙规则。

## 故障排除

- 如果输入/读取事件停止工作，请检查 BlueBubbles Webhook 日志并验证网关路径是否匹配 `channels.bluebubbles.webhookPath`。
- 配对代码在一小时后过期；请使用 `openclaw pairing list bluebubbles` 和 `openclaw pairing approve bluebubbles <code>`。
- 反应需要 BlueBubbles Private API (`POST /api/v1/message/react`)；确保服务器版本公开了它。
- 编辑/撤回需要 macOS 13+ 和兼容的 BlueBubbles 服务器版本。在 macOS 26 (Tahoe) 上，由于 Private API 变更，编辑功能目前损坏。
- 群组图标更新在 macOS 26 (Tahoe) 上可能不稳定：API 可能返回成功但新图标未同步。
- OpenClaw 根据 BlueBubbles 服务器的 macOS 版本自动隐藏已知损坏的操作。如果在 macOS 26 (Tahoe) 上仍显示编辑功能，请使用 `channels.bluebubbles.actions.edit=false` 手动禁用它。
- 有关状态/健康信息：`openclaw status --all` 或 `openclaw status --deep`。

有关一般通道工作流程参考，请参阅 [通道](/channels) 和 [插件](/tools/plugin) 指南。

## 相关

- [通道概览](/channels) — 所有支持的通道
- [配对](/channels/pairing) — DM 认证和配对流程
- [群组](/channels/groups) — 群聊行为和提及门禁
- [通道路由](/channels/channel-routing) — 消息的会话路由
- [安全](/gateway/security) — 访问模型和加固