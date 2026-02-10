---
summary: "Session management rules, keys, and persistence for chats"
read_when:
  - Modifying session handling or storage
title: "Session Management"
---
# 会话管理

OpenClaw 将 **每个代理一个直接聊天会话** 视为主会话。直接聊天会话合并到 `agent:<agentId>:<mainKey>`（默认 `main`），而群组/频道聊天则各自拥有自己的密钥。`session.mainKey` 会被遵守。

使用 `session.dmScope` 来控制 **直接消息** 如何分组：

- `main`（默认）：所有 DM 共享主会话以保持连续性。
- `per-peer`：按发送者 ID 跨频道隔离。
- `per-channel-peer`：按频道 + 发送者隔离（推荐用于多用户收件箱）。
- `per-account-channel-peer`：按账户 + 频道 + 发送者隔离（推荐用于多账户收件箱）。
  使用 `session.identityLinks` 将带有提供者前缀的对等 ID 映射到规范身份，以便在使用 `per-peer`、`per-channel-peer` 或 `per-account-channel-peer` 时，同一个人在不同频道中共享同一个 DM 会话。

## 安全 DM 模式（推荐用于多用户设置）

> **安全警告：** 如果您的代理可以接收来自 **多个人** 的 DM，您应该强烈考虑启用安全 DM 模式。否则，所有用户将共享相同的对话上下文，这可能导致用户之间的隐私信息泄露。

**默认设置下的问题示例：**

- Alice (`<SENDER_A>`) 向您的代理发送关于私密主题的消息（例如，医疗预约）
- Bob (`<SENDER_B>`) 向您的代理询问“我们在聊什么？”
- 因为两个 DM 共享同一个会话，模型可能会使用 Alice 的先前上下文来回答 Bob。

**解决方法：** 设置 `dmScope` 以按用户隔离会话：

```json5
// ~/.openclaw/openclaw.json
{
  session: {
    // Secure DM mode: isolate DM context per channel + sender.
    dmScope: "per-channel-peer",
  },
}
```

**何时启用此功能：**

- 您有多个发送者的配对批准
- 您使用包含多个条目的 DM 允许列表
- 您设置了 `dmPolicy: "open"`
- 多个电话号码或账户可以向您的代理发送消息

注意事项：

- 默认是 `dmScope: "main"` 以保持连续性（所有 DM 共享主会话）。这对于单用户设置来说是可以的。
- 对于同一频道上的多账户收件箱，优先使用 `per-account-channel-peer`。
- 如果同一个人通过多个频道联系您，请使用 `session.identityLinks` 将他们的 DM 会话合并为一个规范身份。
- 您可以使用 `openclaw security audit` 验证您的 DM 设置（参见 [安全](/cli/security)）。

## 网关是真相的来源

所有会话状态都由 **网关**（“主” OpenClaw）**拥有**。UI 客户端（macOS 应用、WebChat 等）必须查询网关获取会话列表和令牌计数，而不是读取本地文件。

- 在 **远程模式** 下，您关心的会话存储位于远程网关主机上，而不是您的 Mac 上。
- UI 中显示的令牌计数来自网关存储字段 (`inputTokens`，`outputTokens`，`totalTokens`，`contextTokens`)。客户端不会解析 JSONL 转录文件来“修复”总数。

## 状态存储位置

- 在 **网关主机** 上:
  - 存储文件: `~/.openclaw/agents/<agentId>/sessions/sessions.json` (每个代理一个).
- 对话记录: `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl` (Telegram 主题对话使用 `.../<SessionId>-topic-<threadId>.jsonl`).
- 存储是一个映射 `sessionKey -> { sessionId, updatedAt, ... }`. 删除条目是安全的；它们按需重新创建.
- 组条目可能包含 `displayName`, `channel`, `subject`, `room`, 和 `space` 以在用户界面中标记会话.
- 会话条目包含 `origin` 元数据（标签 + 路由提示），以便用户界面可以解释会话的来源.
- OpenClaw 不会读取旧的 Pi/Tau 会话文件夹.

## 会话修剪

默认情况下，OpenClaw 在调用 LLM 之前会从内存上下文中修剪 **旧工具结果**.
这不会重写 JSONL 历史记录. 详见 [/concepts/session-pruning](/concepts/session-pruning).

## 预压缩内存刷新

当会话接近自动压缩时，OpenClaw 可以运行一个 **静默内存刷新**
提醒模型将持久化笔记写入磁盘. 这仅在工作区可写时运行. 详见 [Memory](/concepts/memory) 和
[Compaction](/concepts/compaction).

## 映射传输 → 会话密钥

- 直接聊天遵循 `session.dmScope` (默认 `main`).
  - `main`: `agent:<agentId>:<mainKey>` (设备/频道之间的连续性).
    - 多个电话号码和频道可以映射到同一个代理主密钥；它们作为进入同一对话的传输通道.
  - `per-peer`: `agent:<agentId>:dm:<peerId>`.
  - `per-channel-peer`: `agent:<agentId>:<channel>:dm:<peerId>`.
  - `per-account-channel-peer`: `agent:<agentId>:<channel>:<accountId>:dm:<peerId>` (accountId 默认为 `default`).
  - 如果 `session.identityLinks` 匹配提供者前缀的对等 id（例如 `telegram:123`），规范密钥将替换 `<peerId>` 以便同一个人在不同频道共享会话.
- 群组聊天隔离状态: `agent:<agentId>:<channel>:group:<id>` (房间/频道使用 `agent:<agentId>:<channel>:channel:<id>`).
  - Telegram 论坛主题会在群组 id 后附加 `:topic:<threadId>` 以实现隔离.
  - 旧的 `group:<id>` 密钥仍然被识别用于迁移.
- 入站上下文可能仍然使用 `group:<id>`; 通道从 `Provider` 推断并标准化为规范的 `agent:<agentId>:<channel>:group:<id>` 形式.
- 其他来源:
  - 定时任务: `cron:<job.id>`
  - Webhook: `hook:<uuid>` (除非钩子显式设置)
  - 节点运行: `node-<nodeId>`

## 生命周期

- 重置策略：会话会一直复用直到过期，过期会在下一个入站消息时评估。
- 每日重置：默认为**网关主机本地时间的凌晨4:00**。一旦会话的最后更新时间早于最近的每日重置时间，该会话即为过时。
- 空闲重置（可选）：`idleMinutes` 添加一个滑动空闲窗口。当同时配置了每日和空闲重置时，**先过期的那个**会强制开启新会话。
- 旧版仅空闲：如果你设置了 `session.idleMinutes` 而没有设置任何 `session.reset`/`resetByType` 配置，OpenClaw 为了向后兼容会保持仅空闲模式。
- 按类型覆盖（可选）：`resetByType` 允许你覆盖 `direct`、`group` 和 `thread` 会话的策略（线程 = Slack/Discord 线程，Telegram 主题，Matrix 线程（由连接器提供时））。
- 按频道覆盖（可选）：`resetByChannel` 覆盖某个频道的重置策略（适用于该频道的所有会话类型，并优先于 `reset`/`resetByType`）。
- 重置触发器：确切的 `/new` 或 `/reset`（加上 `resetTriggers` 中的任何额外内容）会启动一个新的会话 ID 并传递消息的其余部分。`/new <model>` 接受模型别名 `provider/model` 或提供商名称（模糊匹配）来设置新的会话模型。如果单独发送 `/new` 或 `/reset`，OpenClaw 会运行一个简短的“你好”问候轮次以确认重置。
- 手动重置：从存储中删除特定键或移除 JSONL 对话记录；下一条消息会重新创建它们。
- 隔离的 cron 作业每次运行都会生成一个新的 `sessionId`（不复用空闲会话）。

## 发送策略（可选）

阻止特定类型的会话而不列出单个 ID。

```json5
{
  session: {
    sendPolicy: {
      rules: [
        { action: "deny", match: { channel: "discord", chatType: "group" } },
        { action: "deny", match: { keyPrefix: "cron:" } },
      ],
      default: "allow",
    },
  },
}
```

运行时覆盖（仅限所有者）：

- `/send on` → 允许此会话
- `/send off` → 拒绝此会话
- `/send inherit` → 清除覆盖并使用配置规则
  将这些作为独立消息发送以便注册。

## 配置（可选重命名示例）

```json5
// ~/.openclaw/openclaw.json
{
  session: {
    scope: "per-sender", // keep group keys separate
    dmScope: "main", // DM continuity (set per-channel-peer/per-account-channel-peer for shared inboxes)
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
    reset: {
      // Defaults: mode=daily, atHour=4 (gateway host local time).
      // If you also set idleMinutes, whichever expires first wins.
      mode: "daily",
      atHour: 4,
      idleMinutes: 120,
    },
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
    },
    resetByChannel: {
      discord: { mode: "idle", idleMinutes: 10080 },
    },
    resetTriggers: ["/new", "/reset"],
    store: "~/.openclaw/agents/{agentId}/sessions/sessions.json",
    mainKey: "main",
  },
}
```

## 检查

- `openclaw status` — 显示存储路径和最近会话。
- `openclaw sessions --json` — 转储每个条目（使用 `--active <minutes>` 进行过滤）。
- `openclaw gateway call sessions.list --params '{}'` — 从正在运行的网关获取会话（使用 `--url`/`--token` 进行远程网关访问）。
- 在聊天中单独发送 `/status` 以查看代理是否可达、会话上下文的使用情况、当前的思考/详细模式开关以及您的WhatsApp Web凭证上次刷新的时间（有助于发现重新链接的需求）。
- 发送 `/context list` 或 `/context detail` 查看系统提示和注入的工作区文件（以及最大的上下文贡献者）。
- 单独发送 `/stop` 以中止当前运行、清除该会话的排队后续操作，并停止由此生成的任何子代理运行（回复中包括停止的数量）。
- 单独发送 `/compact`（可选指令）以总结旧的上下文并释放窗口空间。参见 [/concepts/compaction](/concepts/compaction)。
- 可直接打开JSONL转录文件以审查完整的对话轮次。

## 提示

- 将主密钥专用于一对一流量；让群组保持自己的密钥。
- 自动清理时，删除单个密钥而不是整个存储，以保留其他地方的上下文。

## 会话来源元数据

每个会话条目在 `origin` 中记录其来源（尽力而为）：

- `label`: human label (resolved from conversation label + group subject/channel)
- `provider`: normalized channel id (including extensions)
- `from`/`to`: raw routing ids from the inbound envelope
- `accountId`: provider account id (when multi-account)
- `threadId`: thread/topic id when the channel supports it
  origin字段用于直接消息、频道和群组。如果一个连接器仅更新传递路由（例如，以保持DM主会话的新鲜度），它仍然应提供传入上下文，以便会话保留其说明元数据。扩展可以通过在传入上下文中发送`ConversationLabel`，`GroupSubject`，`GroupChannel`，`GroupSpace`和`SenderName`并调用`recordSessionMetaFromInbound`（或将相同的上下文传递给`updateLastRoute`）来实现这一点。