---
summary: "Behavior and config for WhatsApp group message handling (mentionPatterns are shared across surfaces)"
read_when:
  - Changing group message rules or mentions
title: "Group Messages"
---
# 群消息（WhatsApp网页通道）

目标：让Clawd加入WhatsApp群组，仅在被提及时唤醒，并将该对话线程与个人私聊会话分开。

注意：`agents.list[].groupChat.mentionPatterns` 现在也被Telegram/Discord/Slack/iMessage使用；本文档专注于WhatsApp特定行为。对于多代理设置，按代理设置 `agents.list[].groupChat.mentionPatterns`（或使用 `messages.groupChat.mentionPatterns` 作为全局回退）。

## 已实现功能（2025-12-03）

- 激活模式：`mention`（默认）或 `always`。`mention` 需要被提及（通过 `mentionedJids`、正则表达式模式或机器人E.164号码在文本中的任何位置进行真实WhatsApp @提及）。`always` 模式会在每条消息时唤醒代理，但应仅在能提供有意义价值时回复；否则返回静默标记 `NO_REPLY`。默认值可在配置中设置（`channels.whatsapp.groups`），并通过 `/activation` 命令按群组覆盖。当 `channels.whatsapp.groups` 设置时，它也充当群组白名单（包含 `"*"` 以允许所有）。
- 群组策略：`channels.whatsapp.groupPolicy` 控制是否接受群组消息（`open|disabled|allowlist`）。`allowlist` 使用 `channels.whatsapp.groupAllowFrom`（回退：显式 `channels.whatsapp.allowFrom`）。默认是 `allowlist`（直到你添加发送者才允许）。
- 每个群组会话：会话密钥看起来像 `agent:<agentId>:whatsapp:group:<jid>`，因此诸如 `/verbose on` 或 `/think high`（作为独立消息发送）等命令将仅作用于该群组；个人私聊状态不受影响。群组线程会跳过心跳。
- 上下文注入：仅限待处理的群消息（默认50条）且未触发运行的，会在 `[Chat messages since your last reply - for context]` 下前缀，触发行在 `[Current message - respond to this]` 下。已包含在会话中的消息不会重新注入。
- 发送者显示：每个群组批次现在以 `[from: 发送者名称 (+E164)]` 结尾，以便Pi知道谁在说话。
- 临时/一次查看：我们在提取文本/提及前解包这些消息，因此其中的提及仍会触发。
- 群组系统提示：在群组会话的首次轮询（以及每当 `/activation` 改变模式时），我们会将类似 `You are replying inside the WhatsApp group "<subject>". Group members: Alice (+44...), Bob (+43...), … Activation: trigger-only … Address the specific sender noted in the message context.` 的简短说明注入系统提示。如果元数据不可用，我们仍会告诉代理这是一个群聊。

## 配置示例（WhatsApp）

将 `groupChat` 块添加到 `~/.openclaw/openclaw.json`，以便即使WhatsApp在文本正文中移除了可视的@符号，也能正常工作：

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "*": { requireMention: true },
      },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: {
          historyLimit: 50,
          mentionPatterns: ["@?openclaw", "\\+?15555550123"],
        },
      },
    ],
  },
}
```

注意：

- 正则表达式是不区分大小写的；它们覆盖了类似 `@openclaw` 的显示名称提及和原始号码（带或不带 `+`/空格）。
- WhatsApp在有人点击联系人时仍通过 `mentionedJids` 发送规范提及，因此数字回退很少需要，但作为有用的保险措施。

### 激活命令（仅限所有者）

使用群聊命令：

- `/activation mention`
- `/activation always`

只有所有者号码（来自 `channels.whatsapp.allowFrom`，或当未设置时为机器人的E.164）才能更改此设置。在群组中发送 `/status` 作为独立消息以查看当前激活模式。

## 如何使用

1. 将你的WhatsApp账户（运行OpenClaw的账户）添加到群组。
2. 输入 `@openclaw …`（或包含号码）。除非你将 `groupPolicy` 设置为 `"open"`，否则只有白名单发送者才能触发它。
3. 代理提示将包含最近的群组上下文以及末尾的 `[from: …]` 标记，以便它可以针对正确的发送者进行回复。
4. 会话级指令（`/verbose on`、`/think high`、`/new` 或 `/reset`、`/compact`）仅适用于该群组的会话；发送它们作为独立消息以便注册。你的个人私聊会话保持独立。

## 测试/验证

- 手动测试：
  - 在群组中发送 `@openclaw` 提及并确认回复中引用了发送者名称。
  - 发送第二个提及并验证历史记录块被包含然后在下一轮清除。
- 检查网关日志（使用 `--verbose` 运行）以查看 `inbound web message` 条目显示 `from: <groupJid>` 和 `[from: …]` 后缀。

## 已知注意事项

- 有意跳过群组的心跳以避免嘈杂的广播。
- 回声抑制使用组合的批次字符串；如果你在没有提及的情况下发送相同文本两次，只有第一次会收到回复。
- 会话存储条目将显示为 `agent:<agentId>:whatsapp:group:<jid>` 在会话存储中（默认为 `~/.openclaw/agents/<agentId>/sessions/sessions.json`）；缺少条目仅表示群组尚未触发运行。
- 群组中的输入指示器遵循 `agents.defaults.typingMode`（未提及时默认为 `message`）。