---
summary: "Session management rules, keys, and persistence for chats"
read_when:
  - Modifying session handling or storage
title: "Session Management"
---
# 会话管理

OpenClaw 将**每个代理的一个直接聊天会话**视为主会话。直接聊天会折叠到 `agent:<agentId>:<mainKey>`（默认为 `main`），而群组/频道聊天则获得自己的键值。遵循 `session.mainKey`。

使用 `session.dmScope` 来控制**直接消息**的分组方式：

- `main`（默认）：所有直接消息共享主会话以保持连续性。
- `per-peer`：按渠道中的发送者ID隔离。
- `per-channel-peer`：按渠道+发送者隔离（推荐用于多用户收件箱）。
- `per-account-channel-peer`：按账户+渠道+发送者隔离（推荐用于多账户收件箱）。
  使用 `session.identityLinks` 将提供程序前缀的对等ID映射到规范身份，以便在使用 `per-peer`、`per-channel-peer` 或 `per-account-channel-peer` 时，同一个人可以在不同渠道间共享一个直接消息会话。

### 安全直接消息模式（推荐）

如果您的代理可以接收来自**多人**的直接消息（多个发送者的配对批准、包含多个条目的直接消息白名单，或 `dmPolicy: "open"`），请启用**安全直接消息模式**以避免跨用户上下文泄漏：

```json5
// ~/.openclaw/openclaw.json
{
  session: {
    // Secure DM mode: isolate DM context per channel + sender.
    dmScope: "per-channel-peer",
  },
}
```

注意事项：

- 默认为 `dmScope: "main"` 以保持连续性（所有直接消息共享主会话）。
- 对于同一渠道上的多账户收件箱，请优先选择 `per-account-channel-peer`。
- 如果同一个人通过多个渠道联系您，请使用 `session.identityLinks` 将他们的直接消息会话合并为一个规范身份。

## 网关是真理来源

所有会话状态都由**网关**（"主" OpenClaw）拥有。UI客户端（macOS应用、WebChat等）必须向网关查询会话列表和令牌计数，而不是读取本地文件。

- 在**远程模式**下，您关心的会话存储位于远程网关主机上，而不是您的Mac上。
- UI中显示的令牌计数来自网关的存储字段（`inputTokens`、`outputTokens`、`totalTokens`、`contextTokens`）。客户端不会解析JSONL转录来"修复"总计。

## 状态存储位置

- 在**网关主机**上：
  - 存储文件：`~/.openclaw/agents/<agentId>/sessions/sessions.json`（每个代理一个）。
- 转录：`~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`（Telegram主题会话使用 `.../<SessionId>-topic-<threadId>.jsonl`）。
- 存储是一个映射 `sessionKey -> { sessionId, updatedAt, ... }`。删除条目是安全的；它们会在需要时重新创建。
- 群组条目可能包括 `displayName`、`channel`、`subject`、`room` 和 `space` 来标记UI中的会话。
- 会话条目包括 `origin` 元数据（标签+路由提示），这样UI可以解释会话的来源。
- OpenClaw 不会读取旧的Pi/Tau会话文件夹。

## 会话修剪

OpenClaw 默认在LLM调用之前从内存上下文中修剪**旧工具结果**。
这不会重写JSONL历史记录。参见 [/concepts/session-pruning](/concepts/session-pruning)。

## 预压缩内存刷新

当会话接近自动压缩时，OpenClaw可以运行**静默内存刷新**
这个功能提醒模型将持久化笔记写入磁盘。这只在工作区可写时运行。参见 [Memory](/concepts/memory) 和
[Compaction](/concepts/compaction)。

## 映射传输→会话键

- 直接聊天遵循 `session.dmScope`（默认为 `main`）。
  - `main`：`agent:<agentId>:<mainKey>`（跨设备/渠道的连续性）。
    - 多个电话号码和渠道可以映射到同一个代理主键；它们作为进入一个对话的传输方式。
  - `per-peer`：`agent:<agentId>:dm:<peerId>`。
  - `per-channel-peer`：`agent:<agentId>:<channel>:dm:<peerId>`。
  - `per-account-channel-peer`：`agent:<agentId>:<channel>:<accountId>:dm:<peerId>`（accountId默认为 `default`）。
  - 如果 `session.identityLinks` 匹配提供程序前缀的对等ID（例如 `telegram:123`），规范键会替换 `<peerId>`，使同一个人可以在不同渠道间共享会话。
- 群组聊天隔离状态：`agent:<agentId>:<channel>:group:<id>`（房间/频道使用 `agent:<agentId>:<channel>:channel:<id>`）。
  - Telegram论坛主题在群组ID后附加 `:topic:<threadId>` 以实现隔离。
  - 旧的 `group:<id>` 键仍被识别以进行迁移。
- 传入上下文可能仍在使用 `group:<id>`；渠道从 `Provider` 推断并规范化为标准的 `agent:<agentId>:<channel>:group:<id>` 形式。
- 其他来源：
  - Cron作业：`cron:<job.id>`
  - Webhooks：`hook:<uuid>`（除非由hook显式设置）
  - Node运行：`node-<nodeId>`

## 生命周期

- 重置策略：会话会被重用直到过期，过期时间在下次传入消息时评估。
- 每日重置：默认为**网关主机上的本地时间凌晨4:00**。一旦会话的最后更新早于最近的每日重置时间，该会话就变为陈旧状态。
- 空闲重置（可选）：`idleMinutes` 添加滑动空闲窗口。当同时配置了每日和空闲重置时，**先到期的那个**会强制开始新会话。
- 旧版仅空闲：如果您设置了 `session.idleMinutes` 而没有任何 `session.reset`/`resetByType` 配置，OpenClaw会保持仅空闲模式以向后兼容。
- 按类型覆盖（可选）：`resetByType` 允许您覆盖 `dm`、`group` 和 `thread` 会话的策略（线程=Slack/Discord线程、Telegram主题、Matrix线程，当由连接器提供时）。
- 按渠道覆盖（可选）：`resetByChannel` 覆盖渠道的重置策略（适用于该渠道的所有会话类型，并优先于 `reset`/`resetByType`）。
- 重置触发器：确切的 `/new` 或 `/reset`（加上 `resetTriggers` 中的任何额外内容）启动新的会话ID并将消息的其余部分传递。`/new <model>` 接受模型别名、`provider/model` 或提供程序名称（模糊匹配）来设置新会话模型。如果单独发送 `/new` 或 `/reset`，OpenClaw会运行简短的"hello"问候来确认重置。
- 手动重置：从存储中删除特定键或删除JSONL转录；下一条消息会重新创建它们。
- 隔离的cron作业每次运行都会生成一个新的 `sessionId`（无空闲重用）。

## 发送策略（可选）

阻止特定会话类型的交付，无需列出单个ID。

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
      dm: { mode: "idle", idleMinutes: 240 },
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
- `openclaw sessions --json` — 转储每个条目（使用 `--active <minutes>` 过滤）。
- `openclaw gateway call sessions.list --params '{}'` — 从运行的网关获取会话（使用 `--url`/`--token` 访问远程网关）。
- 在聊天中发送 `/status` 作为独立消息，查看代理是否可达、会话上下文使用了多少、当前的思考/详细切换状态，以及您的WhatsApp网页凭据上次刷新时间（有助于发现重新链接需求）。
- 发送 `/context list` 或 `/context detail` 查看系统提示和注入的工作区文件内容（以及最大的上下文贡献者）。
- 发送 `/stop` 作为独立消息以中止当前运行、清除该会话的排队后续消息，并停止从中派生的任何子代理运行（回复包含停止的计数）。
- 发送 `/compact`（可选说明）作为独立消息以总结较旧的上下文并释放窗口空间。参见 [/concepts/compaction](/concepts/compaction)。
- JSONL转录可以直接打开以查看完整回合。

## 提示

- 将主键专门用于1:1流量；让群组保持自己的键。
- 自动清理时，删除单个键而不是整个存储以保留其他地方的上下文。

## 会话来源元数据

每个会话条目在其来源处记录（尽力而为）在 `origin` 中：

- `label`：人工标签（从对话标签+群组主题/频道解析）
- `provider`：标准化渠道ID（包括扩展）
- `from`/`to`：来自传入信封的原始路由ID
- `accountId`：提供程序账户ID（多账户时）
- `threadId`：渠道支持时的线程/主题ID
  直接消息、频道和群组的来源字段都会填充。如果连接器只更新交付路由（例如，保持DM主会话新鲜），它仍应提供传入上下文，以便会话保持其解释元数据。扩展可以通过在传入上下文中发送 `ConversationLabel`、
  `GroupSubject`、`GroupChannel`、`GroupSpace` 和 `SenderName` 并调用 `recordSessionMetaFromInbound`（或向 `updateLastRoute` 传递相同上下文）来实现这一点。