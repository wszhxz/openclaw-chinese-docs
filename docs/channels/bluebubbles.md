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
- 推荐/测试版本：macOS Sequoia (15)。macOS Tahoe (26)可以工作；Tahoe上的编辑功能目前无法使用，群组图标更新可能报告成功但不同步。
- OpenClaw通过其REST API与其通信（`GET /api/v1/ping`，`POST /message/text`，`POST /chat/:id/*`）。
- 收到的消息通过webhooks到达；发送的回复、输入指示器、已读回执和tapbacks是REST调用。
- 附件和贴纸作为传入媒体处理（并在可能的情况下呈现给代理）。
- 配对/允许列表与其他通道（`/start/pairing`等）相同，使用`channels.bluebubbles.allowFrom` + 配对码。
- 反应作为系统事件呈现，就像Slack/Telegram一样，因此代理可以在回复之前“提及”它们。
- 高级功能：编辑、撤回、回复线程、消息效果、群组管理。

## 快速入门

1. 在Mac上安装BlueBubbles服务器（按照[bluebubbles.app/install](https://bluebubbles.app/install)中的说明操作）。
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
4. 将BlueBubbles webhooks指向您的网关（示例：`https://your-gateway-host:3000/bluebubbles-webhook?password=<password>`）。
5. 启动网关；它将注册webhook处理程序并开始配对。

## 入门

BlueBubbles在交互式设置向导中可用：

```
openclaw onboard
```

向导提示输入：

- **服务器URL**（必需）：BlueBubbles服务器地址（例如，`http://192.168.1.100:1234`）
- **密码**（必需）：来自BlueBubbles服务器设置的API密码
- **Webhook路径**（可选）：默认为`/bluebubbles-webhook`
- **DM策略**：配对、允许列表、开放或禁用
- **允许列表**：电话号码、电子邮件或聊天目标

您也可以通过CLI添加BlueBubbles：

```
openclaw channels add bluebubbles --http-url http://192.168.1.100:1234 --password <password>
```

## 访问控制（DM + 群组）

DM：

- 默认：`channels.bluebubbles.dmPolicy = "pairing"`。
- 未知发件人会收到配对码；消息会被忽略直到批准（代码在一小时后过期）。
- 通过以下方式批准：
  - `openclaw pairing list bluebubbles`
  - `openclaw pairing approve bluebubbles <CODE>`
- 配对是默认的令牌交换。详情：[Pairing](/start/pairing)

群组：

- `channels.bluebubbles.groupPolicy = open | allowlist | disabled`（默认：`allowlist`）。
- `channels.bluebubbles.groupAllowFrom`控制谁可以在群组中触发，当`allowlist`被设置时。

### 提及门控（群组）

BlueBubbles支持群聊中的提及门控，匹配iMessage/WhatsApp的行为：

- 使用`agents.list[].groupChat.mentionPatterns`（或`messages.groupChat.mentionPatterns`）检测提及。
- 当`requireMention`为群组启用时，代理仅在被提及时响应。
- 来自授权发件人的控制命令绕过提及门控。

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

- 控制命令（例如，`/config`，`/model`）需要授权。
- 使用`allowFrom`和`groupAllowFrom`确定命令授权。
- 授权发件人即使在群组中未提及也可以运行控制命令。

## 输入 + 已读回执

- **输入指示器**：在响应生成前自动发送，并在响应生成期间继续发送。
- **已读回执**：由`channels.bluebubbles.sendReadReceipts`控制（默认：`true`）。
- **输入指示器**：OpenClaw发送输入开始事件；BlueBubbles在发送或超时时自动清除输入（手动停止通过DELETE不可靠）。

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

当在配置中启用时，BlueBubbles支持高级消息操作：

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

- **react**：添加/移除tapback反应 (`messageId`，`emoji`，`remove`)
- **edit**：编辑已发送的消息 (`messageId`，`text`)
- **unsend**：撤回消息 (`messageId`)
- **reply**：回复特定消息 (`messageId`，`text`，`to`)
- **sendWithEffect**：使用iMessage效果发送 (`text`，`to`，`effectId`)
- **renameGroup**：重命名群聊 (`chatGuid`，`displayName`)
- **setGroupIcon**：设置群聊的图标/照片 (`chatGuid`，`media`) — 在macOS 26 Tahoe上不稳定（API可能返回成功但图标不同步）。
- **addParticipant**：将某人添加到群组 (`chatGuid`，`address`)
- **removeParticipant**：从群组中移除某人 (`chatGuid`，`address`)
- **leaveGroup**：离开群聊 (`chatGuid`)
- **sendAttachment**：发送媒体/文件 (`to`，`buffer`，`filename`，`asVoice`)
  - 语音备忘录：设置`asVoice: true`为**MP3**或**CAF**音频以作为iMessage语音消息发送。BlueBubbles在发送语音备忘录时将MP3转换为CAF。

### 消息ID（短 vs 完整）

OpenClaw可能会呈现_short_消息ID（例如，`1`，`2`）以节省标记。

- `MessageSid` / `ReplyToId` 可以是短ID。
- `MessageSidFull` / `ReplyToIdFull` 包含提供商的完整ID。
- 短ID存储在内存中；它们可能在重启或缓存清除时过期。
- 操作接受短或完整的`messageId`，但如果短ID不再可用，则会出错。

使用完整ID进行持久化自动化和存储：

- 模板：`{{MessageSidFull}}`，`{{ReplyToIdFull}}`
- 上下文：`MessageSidFull` / `ReplyToIdFull` 在传入负载中

参见[Configuration](/gateway/configuration)了解模板变量。

## 块流式传输

控制响应是以单条消息发送还是分块流式传输：

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

- 传入附件会被下载并存储在媒体缓存中。
- 通过`channels.bluebubbles.mediaMaxMb`设置媒体上限（默认：8 MB）。
- 发送的文本被分块为`channels.bluebubbles.textChunkLimit`（默认：4000个字符）。

## 配置参考

完整配置：[Configuration](/gateway/configuration)

提供商选项：

- `channels.bluebubbles.enabled`：启用/禁用通道。
- `channels.bluebubbles.serverUrl`：BlueBubbles REST API基础URL。
- `channels.bluebubbles.password`：API密码。
- `channels.bluebubbles.webhookPath`：Webhook端点路径（默认：`/bluebubbles-webhook`）。
- `channels.bluebubbles.dmPolicy`：`pairing | allowlist | open | disabled`（默认：`pairing`）。
- `channels.bluebubbles.allowFrom`：DM允许列表（句柄、电子邮件、E.164号码，`chat_id:*`，`chat_guid:*`）。
- `channels.bluebubbles.groupPolicy`：`open | allowlist | disabled`（默认：`allowlist`）。
- `channels.bluebubbles.groupAllowFrom`：群组发件人允许列表。
- `channels.bluebubbles.groups`：每个群组的配置 (`requireMention`等）。
- `channels.bluebubbles.sendReadReceipts`：发送已读回执（默认：`true`）。
- `channels.bluebubbles.blockStreaming`：启用块流式传输（默认：`false`；流式回复所需）。
- `channels.bluebubbles.textChunkLimit`：以字符为单位的传出分块大小（默认：4000）。
- `channels.bluebubbles.chunkMode`：`length`（默认）仅在超过`textChunkLimit`时拆分；`newline`在长度分块前按空白行（段落边界）拆分。
- `channels.bluebubbles.mediaMaxMb`：以MB为单位的传入媒体上限（默认：8）。
- `channels.bluebubbles.historyLimit`：上下文的最大群组消息数（0表示禁用）。
- `channels.bluebubbles.dmHistoryLimit`：DM历史记录限制。
- `channels.bluebubbles.actions`：启用/禁用特定操作。
- `channels.bluebubbles.accounts`：多账户配置。

相关全局选项：

- `agents.list[].groupChat.mentionPatterns`（或`messages.groupChat.mentionPatterns`）。
- `messages.responsePrefix`。

## 地址 / 交付目标

优先使用`chat_guid`以实现稳定路由：

- `chat_guid:iMessage;-;+15555550123`（群组首选）
- `chat_id:123`
- `chat_identifier:...`
- 直接句柄：`+15555550123`，`user@example.com`
  - 如果直接句柄没有现有的DM聊天，OpenClaw将通过`POST /api/v1/chat/new`创建一个。这需要启用BlueBubbles私有API。

## 安全性

- Webhook请求通过比较`guid`/`password`查询参数或头与`channels.bluebubbles.password`进行身份验证。来自`localhost`的请求也被接受。
- 保持API密码和webhook端点的秘密（像对待凭据一样）。
- 本地主机信任意味着同一主机的反向代理可能会无意中绕过密码。如果您代理网关，请在代理处要求身份验证并配置`gateway.trustedProxies`。参见[网关安全性](/gateway/security#reverse-proxy-configuration)。
- 如果在LAN之外公开BlueBubbles服务器，请启用HTTPS + 防火墙规则。

## 故障排除

- 如果输入/已读事件停止工作，请检查BlueBubbles webhook日志并验证网关路径是否匹配`channels.bluebubbles.webhookPath`。
- 配对码在一小时后过期；使用`openclaw pairing list bluebubbles`和`openclaw pairing approve bluebubbles <code>`。
- 反应需要BlueBubbles私有API (`POST /api/v1/message/react`)；确保服务器版本暴露了它。
- 编辑/撤回需要macOS 13+和兼容的BlueBubbles服务器版本。在macOS 26 (Tahoe)上，由于私有API更改，编辑当前无法使用。
- 在macOS 26 (Tahoe)上，群组图标更新可能不稳定：API可能返回成功但新图标不同步。
- OpenClaw根据BlueBubbles服务器的macOS版本自动隐藏已知有问题的操作。如果在macOS 26 (Tahoe)上编辑仍然出现，请使用`channels.bluebubbles.actions.edit=false`手动禁用它。
- 有关状态/健康信息：`openclaw status --all` 或 `openclaw status --deep`。

有关通用通道工作流程的参考，请参见[Channels](/channels)和[Plugins](/plugins)指南。