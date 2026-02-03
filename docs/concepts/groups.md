---
summary: "Group chat behavior across surfaces (WhatsApp/Telegram/Discord/Slack/Signal/iMessage/Microsoft Teams)"
read_when:
  - Changing group chat behavior or mention gating
title: "Groups"
---
# 群组

OpenClaw 在不同平台（WhatsApp、Telegram、Discord、Slack、Signal、iMessage、Microsoft Teams）上对群聊的处理方式保持一致。

## 初学者简介（2分钟）

OpenClaw 会驻留在你的个人消息账户中。没有单独的 WhatsApp 机器人用户。
如果你在某个群组中，OpenClaw 可以看到该群组并在其中进行回复。

默认行为：

- 群组被限制（`groupPolicy: "allowlist"`）。
- 回复需要提及，除非你明确禁用提及门控。

翻译：白名单发送者可以通过提及来触发 OpenClaw。

> TL;DR
>
> - **私聊访问**由 `*.allowFrom` 控制。
> - **群组访问**由 `*.groupPolicy` + 白名单（`*.groups`, `*.groupAllowFrom`）控制。
> - **回复触发**由提及门控（`requireMention`, `/activation`）控制。

快速流程（群组消息的处理方式）：

```
groupPolicy? disabled -> 丢弃
groupPolicy? allowlist -> 群组允许? 否 -> 丢弃
requireMention? 是 -> 是否被提及? 否 -> 仅存储上下文
否则 -> 回复
```

![群组消息流程](/images/groups-flow.svg)

如果你想...
| 目标 | 设置内容 |
|------|-------------|
| 允许所有群组但仅在 @提及时回复 | `groups: { "*": { requireMention: true } }` |
| 禁用所有群组回复 | `groupPolicy: "disabled"` |
| 仅特定群组 | `groups: { "<group-id>": { ... } }`（不包含 `"*"` 键） |
| 仅你可以在群组中触发 | `groupPolicy: "allowlist"`, `groupAllowFrom: ["+1555..."]` |

## 会话密钥

- 群组会话使用 `agent:<agentId>:<channel>:group:<id>` 会话密钥（房间/频道使用 `agent:<agentId>:<channel>:channel:<id>`）。
- Telegram 论坛主题在群组 ID 后添加 `:topic:<threadId>`，使每个主题拥有独立的会话。
- 私聊使用主会话（或按发送者配置的每个发送者会话）。
- 群组会话会跳过心跳。

## 模式：个人私聊 + 公共群组（单代理）

是的——如果你的“个人”流量是 **私聊**，而你的“公共”流量是 **群组**，这会很好地工作。

原因：在单代理模式下，私聊通常进入 **主** 会话密钥（`agent:main:main`），而群组始终使用 **非主** 会话密钥（`agent:main:<channel>:group:<id>`）。如果你启用 `mode: "non-main"` 的沙箱，这些群组会话将在 Docker 中运行，而你的主私聊会话保留在主机上。

这为你提供了一个代理“大脑”（共享工作区 + 记忆），但有两种会话类型：

- 主会话（私聊）
- 非主会话（群组）

## 激活（仅限群主）

群主可以切换每个群组的激活状态：

- `/activation mention`
- `/activation always`

群主由 `channels.whatsapp.allowFrom`（或未设置时机器人的自我 E.164）确定。发送命令时需作为独立消息。其他平台目前忽略 `/activation`。

## 上下文字段

群组入站数据设置：

- `ChatType=group`
- `GroupSubject`（如果已知）
- `GroupMembers`（如果已知）
- `WasMentioned`（提及门控结果）
- Telegram 论坛主题还包括 `MessageThreadId` 和 `IsForum`。

代理系统提示在新群组会话的首次轮询中包含群组简介。它提醒模型像人类一样回应，避免使用 Markdown 表格，避免输入字面 `\n` 序列。

## iMessage 特定信息

- 路由或白名单时优先使用 `chat_id:<id>`。
- 列出聊天：`imsg chats --limit 20`。
- 群组回复始终返回到相同的 `chat_id`。

## WhatsApp 特定信息

查看 [群组消息](/concepts/group-messages) 了解仅限 WhatsApp 的行为（历史注入、提及处理细节）。