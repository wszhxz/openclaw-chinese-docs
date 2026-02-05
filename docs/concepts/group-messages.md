---
summary: "Behavior and config for WhatsApp group message handling (mentionPatterns are shared across surfaces)"
read_when:
  - Changing group message rules or mentions
title: "Group Messages"
---
# 群组消息（WhatsApp Web 频道）

目标：让 Clawd 坐在 WhatsApp 群组中，仅在被提及时唤醒，并将该线程与个人直接消息会话分开。

注意：`agents.list[].groupChat.mentionPatterns` 现在也被 Telegram/Discord/Slack/iMessage 使用；本文档专注于 WhatsApp 特定的行为。对于多代理设置，请为每个代理设置 `agents.list[].groupChat.mentionPatterns`（或使用 `messages.groupChat.mentionPatterns` 作为全局回退）。

## 已实现的功能（2025-12-03）

- 激活模式：`mention`（默认）或 `always`。`mention` 需要提及（通过 `mentionedJids` 的真实 WhatsApp @-提及、正则表达式模式或文本中的机器人 E.164）。`always` 在每条消息时唤醒代理，但只有在可以提供有意义的价值时才回复；否则返回静默令牌 `NO_REPLY`。默认值可以在配置中设置 (`channels.whatsapp.groups`) 并通过 `/activation` 覆盖每个群组。当设置了 `channels.whatsapp.groups` 时，它还充当群组白名单（包含 `"*"` 允许所有）。
- 群组策略：`channels.whatsapp.groupPolicy` 控制是否接受群组消息 (`open|disabled|allowlist`)。`allowlist` 使用 `channels.whatsapp.groupAllowFrom`（回退：显式 `channels.whatsapp.allowFrom`)。默认是 `allowlist`（阻止直到你添加发送者）。
- 每群组会话：会话密钥类似于 `agent:<agentId>:whatsapp:group:<jid>`，因此命令如 `/verbose on` 或 `/think high`（作为独立消息发送）仅限于该群组；个人 DM 状态不受影响。心跳跳过群组线程。
- 上下文注入：**仅待处理**的群组消息（默认 50）如果没有触发运行，则在 `[Chat messages since your last reply - for context]` 下前缀，触发行为的行在 `[Current message - respond to this]` 下。会话中已有的消息不会重新注入。
- 发送者显示：每个群组批次现在以 `[from: Sender Name (+E164)]` 结尾，因此 Pi 知道是谁在说话。
- 即时消息/查看一次：我们在提取文本/提及之前解包这些消息，因此其中的提及仍然会触发。
- 群组系统提示：在群组会话的第一轮（以及每当 `/activation` 更改模式时），我们向系统提示注入简短说明，例如 `You are replying inside the WhatsApp group "<subject>". Group members: Alice (+44...), Bob (+43...), … Activation: trigger-only … Address the specific sender noted in the message context.`。如果元数据不可用，我们仍然告诉代理这是一个群聊。

## 配置示例（WhatsApp）

在 `~/.openclaw/openclaw.json` 中添加一个 `groupChat` 块，以便即使 WhatsApp 剥离了文本主体中的视觉 `@`，显示名称提及也能正常工作：

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

注意事项：

- 正则表达式不区分大小写；它们涵盖了类似 `@openclaw` 的显示名称提及以及带或不带 `+`/空格的原始号码。
- 当有人点击联系人时，WhatsApp 仍然通过 `mentionedJids` 发送规范提及，因此很少需要号码回退，但它是一个有用的保险网。

### 激活命令（仅限所有者）

使用群组聊天命令：

- `/activation mention`
- `/activation always`

只有所有者号码（来自 `channels.whatsapp.allowFrom`，或未设置时机器人的 E.164）才能更改此设置。在群组中发送 `/status` 作为独立消息以查看当前激活模式。

## 如何使用

1. 将你的 WhatsApp 账户（运行 OpenClaw 的账户）添加到群组中。
2. 说 `@openclaw …`（或包括号码）。只有白名单发送者可以触发它，除非你设置了 `groupPolicy: "open"`。
3. 代理提示将包括最近的群组上下文加上尾随的 `[from: …]` 标记，以便它可以正确回应。
4. 会话级别指令 (`/verbose on`, `/think high`, `/new` 或 `/reset`, `/compact`) 仅适用于该群组的会话；将其作为独立消息发送以注册。你的个人 DM 会话保持独立。

## 测试 / 验证

- 手动测试：
  - 在群组中发送一个 `@openclaw` 提及并确认回复引用了发送者名称。
  - 发送第二个提及并验证历史块已包含然后在下一轮清除。
- 检查网关日志（使用 `--verbose` 运行）以查看 `inbound web message` 条目显示 `from: <groupJid>` 和 `[from: …]` 后缀。

## 已知注意事项

- 为了避免嘈杂的广播，故意跳过了群组的心跳。
- 回声抑制使用组合批次字符串；如果你两次发送相同的文本而没有提及，只有第一次会得到响应。
- 会话存储条目将以 `agent:<agentId>:whatsapp:group:<jid>` 出现在会话存储中 (`~/.openclaw/agents/<agentId>/sessions/sessions.json` 默认)；缺少条目仅意味着该群组尚未触发运行。
- 群组中的输入指示符遵循 `agents.defaults.typingMode`（默认：`message` 当未提及时）。