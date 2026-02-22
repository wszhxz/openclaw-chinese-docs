---
summary: "Slack setup and runtime behavior (Socket Mode + HTTP Events API)"
read_when:
  - Setting up Slack or debugging Slack socket/HTTP mode
title: "Slack"
---
# Slack

状态：通过Slack应用集成，适用于DM和频道的生产就绪。默认模式为Socket Mode；也支持HTTP Events API模式。

<CardGroup cols={3}>
  <Card title="配对" icon="link" href="/channels/pairing">
    Slack DM默认为配对模式。
  </Card>
  <Card title="斜杠命令" icon="terminal" href="/tools/slash-commands">
    原生命令行为和命令目录。
  </Card>
  <Card title="频道故障排除" icon="wrench" href="/channels/troubleshooting">
    跨频道诊断和修复手册。
  </Card>
</CardGroup>

## 快速设置

<Tabs>
  <Tab title="Socket Mode (default)">
    <Steps>
      <Step title="Create Slack app and tokens">
        In Slack app settings:

        - enable **Socket Mode**
        - create **App Token** (__CODE_BLOCK_0__) with __CODE_BLOCK_1__
        - install app and copy **Bot Token** (__CODE_BLOCK_2__)
      </Step>

      <Step title="Configure OpenClaw">

__CODE_BLOCK_3__

        Env fallback (default account only):

__CODE_BLOCK_4__

      </Step>

      <Step title="Subscribe app events">
        Subscribe bot events for:

        - __CODE_BLOCK_5__
        - __CODE_BLOCK_6__, __CODE_BLOCK_7__, __CODE_BLOCK_8__, __CODE_BLOCK_9__
        - __CODE_BLOCK_10__, __CODE_BLOCK_11__
        - __CODE_BLOCK_12__, __CODE_BLOCK_13__
        - __CODE_BLOCK_14__
        - __CODE_BLOCK_15__, __CODE_BLOCK_16__

        Also enable App Home **Messages Tab** for DMs.
      </Step>

      <Step title="Start gateway">

__CODE_BLOCK_17__

      </Step>
    </Steps>

  </Tab>

  <Tab title="HTTP Events API mode">
    <Steps>
      <Step title="Configure Slack app for HTTP">

        - set mode to HTTP (__CODE_BLOCK_18__)
        - copy Slack **Signing Secret**
        - set Event Subscriptions + Interactivity + Slash command Request URL to the same webhook path (default __CODE_BLOCK_19__)

      </Step>

      <Step title="Configure OpenClaw HTTP mode">

__CODE_BLOCK_20__

      </Step>

      <Step title="Use unique webhook paths for multi-account HTTP">
        Per-account HTTP mode is supported.

        Give each account a distinct __CODE_BLOCK_21__ so registrations do not collide.
      </Step>
    </Steps>

  </Tab>
</Tabs>

## 令牌模型

- `botToken` + `appToken` 是 Socket Mode 所必需的。
- HTTP 模式需要 `botToken` + `signingSecret`。
- 配置令牌会覆盖环境变量回退。
- `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` 环境变量回退仅适用于默认账户。
- `userToken` (`xoxp-...`) 是仅配置选项（无环境变量回退），默认为只读行为 (`userTokenReadOnly: true`)。
- 可选：如果希望外出消息使用活动代理身份（自定义 `username` 和图标），请添加 `chat:write.customize`。`icon_emoji` 使用 `:emoji_name:` 语法。

<Tip>
For actions/directory reads, user token can be preferred when configured. For writes, bot token remains preferred; user-token writes are only allowed when __CODE_BLOCK_13__ and bot token is unavailable.
</Tip>

## 访问控制和路由

<Tabs>
  <Tab title="DM policy">
    __CODE_BLOCK_14__ controls DM access (legacy: __CODE_BLOCK_15__):

    - __CODE_BLOCK_16__ (default)
    - __CODE_BLOCK_17__
    - __CODE_BLOCK_18__ (requires __CODE_BLOCK_19__ to include __CODE_BLOCK_20__; legacy: __CODE_BLOCK_21__)
    - __CODE_BLOCK_22__

    DM flags:

    - __CODE_BLOCK_23__ (default true)
    - __CODE_BLOCK_24__ (preferred)
    - __CODE_BLOCK_25__ (legacy)
    - __CODE_BLOCK_26__ (group DMs default false)
    - __CODE_BLOCK_27__ (optional MPIM allowlist)

    Pairing in DMs uses __CODE_BLOCK_28__.

  </Tab>

  <Tab title="Channel policy">
    __CODE_BLOCK_29__ controls channel handling:

    - __CODE_BLOCK_30__
    - __CODE_BLOCK_31__
    - __CODE_BLOCK_32__

    Channel allowlist lives under __CODE_BLOCK_33__.

    Runtime note: if __CODE_BLOCK_34__ is completely missing (env-only setup) and __CODE_BLOCK_35__ is unset, runtime falls back to __CODE_BLOCK_36__ and logs a warning.

    Name/ID resolution:

    - channel allowlist entries and DM allowlist entries are resolved at startup when token access allows
    - unresolved entries are kept as configured

  </Tab>

  <Tab title="Mentions and channel users">
    Channel messages are mention-gated by default.

    Mention sources:

    - explicit app mention (__CODE_BLOCK_37__)
    - mention regex patterns (__CODE_BLOCK_38__, fallback __CODE_BLOCK_39__)
    - implicit reply-to-bot thread behavior

    Per-channel controls (__CODE_BLOCK_40__):

    - __CODE_BLOCK_41__
    - __CODE_BLOCK_42__ (allowlist)
    - __CODE_BLOCK_43__
    - __CODE_BLOCK_44__
    - __CODE_BLOCK_45__
    - __CODE_BLOCK_46__, __CODE_BLOCK_47__

  </Tab>
</Tabs>

## 命令和斜杠行为

- Native command auto-mode 是 **off** 对于 Slack (`commands.native: "auto"` 不启用 Slack 原生命令)。
- 使用 `channels.slack.commands.native: true` 启用原生 Slack 命令处理器（或全局 `commands.native: true`）。
- 当启用原生命令时，在 Slack 中注册匹配的斜杠命令 (`/<command>` 名称)。
- 如果未启用原生命令，可以通过 `channels.slack.slashCommand` 运行单个配置的斜杠命令。
- 原生参数菜单现在适应其渲染策略：
  - 最多 5 个选项：按钮块
  - 6-100 个选项：静态选择菜单
  - 超过 100 个选项：外部选择，并在可用时使用异步选项过滤
  - 如果编码选项值超出 Slack 限制，流程将回退到按钮
- 对于长选项负载，斜杠命令参数菜单在分派选定值之前使用确认对话框。

默认斜杠命令设置：

- `enabled: false`
- `name: "openclaw"`
- `sessionPrefix: "slack:slash"`
- `ephemeral: true`

斜杠会话使用隔离密钥：

- `agent:<agentId>:slack:slash:<userId>`

并仍然针对目标对话会话路由命令执行 (`CommandTargetSessionKey`)。

## 线程、会话和回复标签

- 直接消息路由为 `direct`；频道为 `channel`；多人即时消息为 `group`。
- 使用默认 `session.dmScope=main`，Slack 直接消息合并到代理主会话。
- 频道会话：`agent:<agentId>:slack:channel:<channelId>`。
- 线程回复可以在适用时创建线程会话后缀 (`:thread:<threadTs>`)。
- `channels.slack.thread.historyScope` 默认为 `thread`；`thread.inheritParent` 默认为 `false`。
- `channels.slack.thread.initialHistoryLimit` 控制在启动新线程会话时获取多少现有线程消息（默认 `20`；设置 `0` 以禁用）。

回复线程控制：

- `channels.slack.replyToMode`: `off|first|all`（默认 `off`）
- `channels.slack.replyToModeByChatType`: 按 `direct|group|channel`
- 直接聊天的旧版回退：`channels.slack.dm.replyToMode`

支持手动回复标签：

- `[[reply_to_current]]`
- `[[reply_to:<id>]]`

注意：`replyToMode="off"` 禁用隐式回复线程。显式 `[[reply_to_*]]` 标签仍然有效。

## 媒体、分块和交付

<AccordionGroup>
  <Accordion title="传入附件">
    Slack 文件附件从 Slack 托管的私有 URL 下载（令牌认证请求流），并在获取成功且大小限制允许的情况下写入媒体存储。

    运行时传入大小上限默认为 `20MB`，除非被 `channels.slack.mediaMaxMb` 覆盖。

  </Accordion>

<Accordion title="外发文本和文件">
    - 文本块使用 `channels.slack.textChunkLimit`（默认 4000）
    - `channels.slack.chunkMode="newline"` 启用段落优先拆分
    - 文件发送使用 Slack 上传 API 并可以包含线程回复 (`thread_ts`)
    - 外发媒体限制遵循 `channels.slack.mediaMaxMb` 配置；否则通道发送使用媒体管道的 MIME 类型默认值
  </Accordion>

  <Accordion title="交付目标">
    偏好的显式目标：

    - `user:<id>` 用于直接消息
    - `channel:<id>` 用于频道

    发送到用户目标时，通过 Slack 对话 API 打开 Slack 直接消息。

  </Accordion>
</AccordionGroup>

## 操作和网关

Slack 操作由 `channels.slack.actions.*` 控制。

当前 Slack 工具中的可用操作组：

| 组      | 默认 |
| ---------- | ------- |
| messages   | enabled |
| reactions  | enabled |
| pins       | enabled |
| memberInfo | enabled |
| emojiList  | enabled |

## 事件和操作行为

- 消息编辑/删除/线程广播映射为系统事件。
- 反应添加/移除事件映射为系统事件。
- 成员加入/离开、频道创建/重命名和固定添加/移除事件映射为系统事件。
- 助手线程状态更新（用于线程中的“正在输入...”指示器）使用 `assistant.threads.setStatus` 并需要机器人范围 `assistant:write`。
- `channel_id_changed` 可以在启用 `configWrites` 时迁移频道配置键。
- 频道主题/目的元数据被视为不可信上下文，并可以注入到路由上下文中。
- 块操作和模态交互发出结构化的 `Slack interaction: ...` 系统事件，具有丰富的负载字段：
  - 块操作：选定值、标签、选择器值和 `workflow_*` 元数据
  - 模态 `view_submission` 和 `view_closed` 事件，带有路由频道元数据和表单输入

## 认可反应

`ackReaction` 在 OpenClaw 处理传入消息时发送认可表情符号。

解析顺序：

- `channels.slack.accounts.<accountId>.ackReaction`
- `channels.slack.ackReaction`
- `messages.ackReaction`
- 代理身份表情符号回退 (`agents.list[].identity.emoji`，否则 "👀")

注意：

- Slack 期望简码（例如 `"eyes"`）。
- 使用 `""` 禁用某个频道或账户的反应。

## 清单和范围检查清单

<AccordionGroup>
  <Accordion title="Slack 应用清单示例">

```json
{
  "display_information": {
    "name": "OpenClaw",
    "description": "Slack connector for OpenClaw"
  },
  "features": {
    "bot_user": {
      "display_name": "OpenClaw",
      "always_online": false
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/openclaw",
        "description": "Send a message to OpenClaw",
        "should_escape": false
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "chat:write",
        "channels:history",
        "channels:read",
        "groups:history",
        "im:history",
        "mpim:history",
        "users:read",
        "app_mentions:read",
        "assistant:write",
        "reactions:read",
        "reactions:write",
        "pins:read",
        "pins:write",
        "emoji:read",
        "commands",
        "files:read",
        "files:write"
      ]
    }
  },
  "settings": {
    "socket_mode_enabled": true,
    "event_subscriptions": {
      "bot_events": [
        "app_mention",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "reaction_added",
        "reaction_removed",
        "member_joined_channel",
        "member_left_channel",
        "channel_rename",
        "pin_added",
        "pin_removed"
      ]
    }
  }
}
```

  </Accordion>

  <Accordion title="可选的 user-token 范围（读操作）">
    如果你配置了 `channels.slack.userToken`，典型的读范围包括：

    - `channels:history`, `groups:history`, `im:history`, `mpim:history`
    - `channels:read`, `groups:read`, `im:read`, `mpim:read`
    - `users:read`
    - `reactions:read`
    - `pins:read`
    - `emoji:read`
    - `search:read`（如果你依赖于 Slack 搜索读取）

  </Accordion>
</AccordionGroup>

## 故障排除

<AccordionGroup>
  <Accordion title="频道中没有回复">
    按顺序检查：

    - `groupPolicy`
    - 频道白名单 (`channels.slack.channels`)
    - `requireMention`
    - 每个频道的 `users` 白名单

    有用的命令：

```bash
openclaw channels status --probe
openclaw logs --follow
openclaw doctor
```

  </Accordion>

  <Accordion title="忽略直接消息">
    检查：

    - `channels.slack.dm.enabled`
    - `channels.slack.dmPolicy`（或旧版 `channels.slack.dm.policy`）
    - 配对审批/白名单条目

```bash
openclaw pairing list slack
```

  </Accordion>

  <Accordion title="Socket 模式无法连接">
    验证 Slack 应用设置中的机器人 + 应用令牌以及 Socket 模式的启用。
  </Accordion>

  <Accordion title="HTTP 模式未接收事件">
    验证：

    - 签名密钥
    - Webhook 路径
    - Slack 请求 URL（事件 + 交互性 + 斜杠命令）
    - 每个 HTTP 帐户的唯一 `webhookPath`

  </Accordion>

  <Accordion title="原生/斜杠命令未触发">
    验证你是否打算：

- 本地命令模式 (`channels.slack.commands.native: true`) 并在Slack中注册匹配的斜杠命令
    - 或单斜杠命令模式 (`channels.slack.slashCommand.enabled: true`)

    同时检查 `commands.useAccessGroups` 和频道/用户白名单。

  </Accordion>
</AccordionGroup>

## 文本流式传输

OpenClaw 通过 Agents 和 AI Apps API 支持 Slack 的本地文本流式传输。

`channels.slack.streaming` 控制实时预览行为：

- `off`：禁用实时预览流式传输。
- `partial`（默认）：用最新的部分输出替换预览文本。
- `block`：附加分块预览更新。
- `progress`：在生成时显示进度状态文本，然后发送最终文本。

`channels.slack.nativeStreaming` 控制 Slack 的本地流式传输 API (`chat.startStream` / `chat.appendStream` / `chat.stopStream`) 当 `streaming` 是 `partial`（默认：`true`）。

禁用原生 Slack 流式传输（保持草稿预览行为）：

```yaml
channels:
  slack:
    streaming: partial
    nativeStreaming: false
```

旧密钥：

- `channels.slack.streamMode` (`replace | status_final | append`) 自动迁移到 `channels.slack.streaming`。
- 布尔值 `channels.slack.streaming` 自动迁移到 `channels.slack.nativeStreaming`。

### 要求

1. 在您的 Slack 应用设置中启用 **Agents and AI Apps**。
2. 确保应用具有 `assistant:write` 范围。
3. 该消息必须有回复线程可用。线程选择仍然遵循 `replyToMode`。

### 行为

- 第一个文本块启动流 (`chat.startStream`)。
- 后续的文本块附加到同一个流 (`chat.appendStream`)。
- 回复结束完成流 (`chat.stopStream`)。
- 媒体和其他非文本负载回退到正常交付。
- 如果回复中途流式传输失败，OpenClaw 将剩余负载回退到正常交付。

## 配置参考指针

主要参考：

- [配置参考 - Slack](/gateway/configuration-reference#slack)

  高信号 Slack 字段：
  - mode/auth: `mode`, `botToken`, `appToken`, `signingSecret`, `webhookPath`, `accounts.*`
  - DM 访问: `dm.enabled`, `dmPolicy`, `allowFrom`（旧版：`dm.policy`, `dm.allowFrom`），`dm.groupEnabled`, `dm.groupChannels`
  - 频道访问: `groupPolicy`, `channels.*`, `channels.*.users`, `channels.*.requireMention`
  - 线程/历史记录: `replyToMode`, `replyToModeByChatType`, `thread.*`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
  - 交付: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `streaming`, `nativeStreaming`
  - 操作/功能: `configWrites`, `commands.native`, `slashCommand.*`, `actions.*`, `userToken`, `userTokenReadOnly`

## 相关

- [配对](/channels/pairing)
- [频道路由](/channels/channel-routing)
- [故障排除](/channels/troubleshooting)
- [配置](/gateway/configuration)
- [斜杠命令](/tools/slash-commands)