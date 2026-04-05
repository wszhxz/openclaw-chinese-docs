---
summary: "Behavior and config for WhatsApp group message handling (mentionPatterns are shared across surfaces)"
read_when:
  - Changing group message rules or mentions
title: "Group Messages"
---
# 群消息（WhatsApp Web 频道）

目标：让 Clawd 加入 WhatsApp 群组，仅在收到提及时唤醒，并将该线程与个人私聊会话保持分离。

注意：`agents.list[].groupChat.mentionPatterns` 现在也被 Telegram/Discord/Slack/iMessage 使用；本文档专注于 WhatsApp 特有的行为。对于多智能体设置，请为每个智能体设置 `agents.list[].groupChat.mentionPatterns`（或使用 `messages.groupChat.mentionPatterns` 作为全局回退）。

## 当前实现 (2025-12-03)

- 激活模式：`mention`（默认）或 `always`。`mention` 需要提及（通过 `mentionedJids` 的真实 WhatsApp @提及、安全正则表达式模式，或文本中任意位置的机器人 E.164 号码）。`always` 会在每条消息上唤醒智能体，但它应仅在能增加有意义价值时回复；否则它返回确切的静默令牌 `NO_REPLY` / `no_reply`。默认值可在配置中设置（`channels.whatsapp.groups`），并通过 `/activation` 按组覆盖。当设置 `channels.whatsapp.groups` 时，它也充当群组白名单（包含 `"*"` 以允许所有）。
- 群组策略：`channels.whatsapp.groupPolicy` 控制是否接受群消息（`open|disabled|allowlist`）。`allowlist` 使用 `channels.whatsapp.groupAllowFrom`（回退：显式 `channels.whatsapp.allowFrom`）。默认为 `allowlist`（在添加发送者之前被阻止）。
- 每群组会话：会话密钥看起来像 `agent:<agentId>:whatsapp:group:<jid>`，因此诸如 `/verbose on` 或 `/think high` 的命令（作为独立消息发送）限定于该群组；个人私聊状态不受影响。群组线程会跳过心跳检测。
- 上下文注入：**仅待处理**的群消息（默认 50 条）若 _未_ 触发运行，则前缀置于 `[Chat messages since your last reply - for context]` 下，触发行置于 `[Current message - respond to this]` 下。已在会话中的消息不会重新注入。
- 发送者显示：每个群组批次现在以 `[from: Sender Name (+E164)]` 结尾，以便 Pi 知道谁在说话。
- 临时/阅后即焚：我们在提取文本/提及之前解开这些消息，因此其中的提及仍然会触发。
- 群组系统提示词：在群组会话的第一轮（以及每当 `/activation` 更改模式时），我们会向系统提示词注入一段简短说明，如 `You are replying inside the WhatsApp group "<subject>". Group members: Alice (+44...), Bob (+43...), … Activation: trigger-only … Address the specific sender noted in the message context.`。如果元数据不可用，我们仍会告知智能体这是一个群聊。

## 配置示例（WhatsApp）

向 `~/.openclaw/openclaw.json` 添加一个 `groupChat` 块，以便即使 WhatsApp 剥离了文本正文中的视觉 `@`，显示名称提及也能工作：

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

- 正则表达式不区分大小写，并使用与其他配置正则表达式表面相同的安全正则表达式护栏；无效模式和嵌套重复会被忽略。
- 当某人点击联系人时，WhatsApp 仍通过 `mentionedJids` 发送标准提及，因此数字回退很少需要，但是一个有用的安全网。

### 激活命令（仅限所有者）

使用群聊命令：

- `/activation mention`
- `/activation always`

只有所有者号码（来自 `channels.whatsapp.allowFrom`，或未设置时的机器人自身 E.164）可以更改此设置。在群组中作为独立消息发送 `/status` 以查看当前的激活模式。

## 如何使用

1. 将您的 WhatsApp 账户（运行 OpenClaw 的那个）添加到群组。
2. 说 `@openclaw …`（或包含号码）。除非您设置了 `groupPolicy: "open"`，否则只有白名单发送者才能触发它。
3. 智能体提示词将包括最近的群组上下文以及尾随的 `[from: …]` 标记，以便它可以针对正确的人。
4. 会话级指令（`/verbose on`、`/think high`、`/new` 或 `/reset`、`/compact`）仅适用于该群组的会话；将它们作为独立消息发送以便注册。您的个人私聊会话保持独立。

## 测试/验证

- 手动冒烟测试：
  - 在群组中发送一个 `@openclaw` 提及，并确认回复引用了发送者名称。
  - 发送第二个提及，并验证历史记录块被包含然后在下一轮清除。
- 检查网关日志（使用 `--verbose` 运行）以查看显示 `from: <groupJid>` 和 `[from: …]` 后缀的 `inbound web message` 条目。

## 已知注意事项

- 为避免嘈杂的广播，群组有意跳过心跳检测。
- 回声抑制使用组合批次字符串；如果您两次发送相同的文本且没有提及，只有第一次会得到响应。
- 会话存储条目将以 `agent:<agentId>:whatsapp:group:<jid>` 的形式出现在会话存储中（默认为 `~/.openclaw/agents/<agentId>/sessions/sessions.json`）；缺少条目仅意味着群组尚未触发运行。
- 群组中的输入指示符遵循 `agents.defaults.typingMode`（默认：未提及时为 `message`）。