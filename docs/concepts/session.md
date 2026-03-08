---
summary: "Session management rules, keys, and persistence for chats"
read_when:
  - Modifying session handling or storage
title: "Session Management"
---
# 会话管理

OpenClaw 将 **每个代理一个直接聊天会话** 视为主要会话。直接聊天折叠为 `agent:<agentId>:<mainKey>`（默认 `main`），而群组/频道聊天拥有各自的密钥。`session.mainKey` 将被遵守。

使用 `session.dmScope` 来控制 **直接消息** 的分组方式：

- `main`（默认）：所有 DM 共享主会话以保持连续性。
- `per-peer`：跨频道按发送者 ID 隔离。
- `per-channel-peer`：按频道 + 发送者隔离（推荐用于多用户收件箱）。
- `per-account-channel-peer`：按账户 + 频道 + 发送者隔离（推荐用于多账户收件箱）。
  使用 `session.identityLinks` 将提供商前缀的对等 ID 映射到规范身份，以便在使用 `per-peer`、`per-channel-peer` 或 `per-account-channel-peer` 时，同一个人跨频道共享一个 DM 会话。

## 安全 DM 模式（推荐用于多用户设置）

> **安全警告：** 如果您的代理可以接收来自 **多人** 的 DM，您应该强烈考虑启用安全 DM 模式。否则，所有用户将共享相同的对话上下文，这可能会导致用户之间的私人信息泄露。

**默认设置下的问题示例：**

- Alice (`<SENDER_A>`) 就私人话题（例如医疗预约）向您的代理发送消息
- Bob (`<SENDER_B>`) 向您的代理发送消息询问“我们刚才在聊什么？”
- 由于两个 DM 共享同一个会话，模型可能会使用 Alice 之前的上下文来回答 Bob。

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
- 您使用包含多个条目的 DM 白名单
- 您设置了 `dmPolicy: "open"`
- 多个电话号码或账户可以向您的代理发送消息

注意：

- 默认是 `dmScope: "main"` 以保持连续性（所有 DM 共享主会话）。这对于单用户设置没问题。
- 本地 CLI 引导在未设置时默认写入 `session.dmScope: "per-channel-peer"`（现有的显式值会被保留）。
- 对于同一频道上的多账户收件箱，首选 `per-account-channel-peer`。
- 如果同一个人在多个频道上联系您，使用 `session.identityLinks` 将他们的 DM 会话折叠为一个规范身份。
- 您可以使用 `openclaw security audit` 验证您的 DM 设置（参见 [安全](/cli/security)）。

## 网关是事实来源

所有会话状态都 **由网关拥有**（“主”OpenClaw）。UI 客户端（macOS 应用、WebChat 等）必须向网关查询会话列表和令牌计数，而不是读取本地文件。

- 在 **远程模式** 下，您关心的会话存储位于远程网关主机上，而不是您的 Mac 上。
- UI 中显示的令牌计数来自网关的存储字段 (`inputTokens`, `outputTokens`, `totalTokens`, `contextTokens`)。客户端不会解析 JSONL 记录来“修正”总数。

## 状态存放位置

- 在 **网关主机** 上：
  - 存储文件：`~/.openclaw/agents/<agentId>/sessions/sessions.json`（每个代理）。
- 记录：`~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`（Telegram 主题会话使用 `.../<SessionId>-topic-<threadId>.jsonl`）。
- 存储是一个映射 `sessionKey -> { sessionId, updatedAt, ... }`。删除条目是安全的；它们会在需要时重新创建。
- 群组条目可能包括 `displayName`、`channel`、`subject`、`room` 和 `space` 以在 UI 中标记会话。
- 会话条目包括 `origin` 元数据（标签 + 路由提示），以便 UI 可以解释会话来源。
- OpenClaw **不** 读取遗留的 Pi/Tau 会话文件夹。

## 维护

OpenClaw 应用会话存储维护以保持 `sessions.json` 和记录产物随时间保持在受限范围内。

### 默认值

- `session.maintenance.mode`: `warn`
- `session.maintenance.pruneAfter`: `30d`
- `session.maintenance.maxEntries`: `500`
- `session.maintenance.rotateBytes`: `10mb`
- `session.maintenance.resetArchiveRetention`：默认为 `pruneAfter` (`30d`)
- `session.maintenance.maxDiskBytes`：未设置（禁用）
- `session.maintenance.highWaterBytes`：启用预算控制时默认为 `maxDiskBytes` 的 `80%`

### 工作原理

维护在会话存储写入期间运行，您可以使用 `openclaw sessions cleanup` 按需触发它。

- `mode: "warn"`：报告将被淘汰的内容，但不修改条目/记录。
- `mode: "enforce"`：按以下顺序应用清理：
  1. 修剪早于 `pruneAfter` 的过时条目
  2. 将条目数量上限设为 `maxEntries`（最旧优先）
  3. 归档不再引用的已移除条目的记录文件
  4. 根据保留策略清除旧的 `*.deleted.<timestamp>` 和 `*.reset.<timestamp>` 归档
  5. 当 `sessions.json` 超过 `rotateBytes` 时进行轮换
  6. 如果设置了 `maxDiskBytes`，则向 `highWaterBytes` 执行磁盘预算（最旧的产物优先，然后是最旧的会话）

### 大型存储的性能注意事项

大型会话存储在高容量设置中很常见。维护工作是写入路径工作，因此非常大的存储可能会增加写入延迟。

最增加成本的因素：

- 非常高的 `session.maintenance.maxEntries` 值
- 保留过时条目的长 `pruneAfter` 窗口
- `~/.openclaw/agents/<agentId>/sessions/` 中有许多记录/归档产物
- 启用磁盘预算 (`maxDiskBytes`) 而没有合理的修剪/上限限制

怎么做：

- 在生产环境中使用 `mode: "enforce"` 以便自动限制增长
- 设置时间和数量限制 (`pruneAfter` + `maxEntries`)，而不仅仅是其中一个
- 在大型部署中设置 `maxDiskBytes` + `highWaterBytes` 作为硬上限
- 保持 `highWaterBytes` 明显低于 `maxDiskBytes`（默认是 80%）
- 在配置更改后运行 `openclaw sessions cleanup --dry-run --json` 以在强制执行前验证预计影响
- 对于频繁的活动会话，运行手动清理时传递 `--active-key`

### 自定义示例

使用保守的强制执行策略：

```json5
{
  session: {
    maintenance: {
      mode: "enforce",
      pruneAfter: "45d",
      maxEntries: 800,
      rotateBytes: "20mb",
      resetArchiveRetention: "14d",
    },
  },
}
```

为会话目录启用硬磁盘预算：

```json5
{
  session: {
    maintenance: {
      mode: "enforce",
      maxDiskBytes: "1gb",
      highWaterBytes: "800mb",
    },
  },
}
```

为大型安装调整（示例）：

```json5
{
  session: {
    maintenance: {
      mode: "enforce",
      pruneAfter: "14d",
      maxEntries: 2000,
      rotateBytes: "25mb",
      maxDiskBytes: "2gb",
      highWaterBytes: "1.6gb",
    },
  },
}
```

从 CLI 预览或强制维护：

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
```

## 会话修剪

OpenClaw 默认在 LLM 调用之前从内存上下文中修剪 **旧工具结果**。
这 **不会** 重写 JSONL 历史。参见 [/concepts/session-pruning](/concepts/session-pruning)。

## 预压缩内存刷新

当会话接近自动压缩时，OpenClaw 可以运行一个 **静默内存刷新** 回合，提醒模型将持久笔记写入磁盘。这仅在工作区可写时运行。参见 [内存](/concepts/memory) 和 [压缩](/concepts/compaction)。

## 映射传输 → 会话密钥

- 直接聊天遵循 `session.dmScope`（默认 `main`）。
  - `main`: `agent:<agentId>:<mainKey>`（跨设备/频道的连续性）。
    - 多个电话号码和频道可以映射到同一个代理主密钥；它们作为进入同一对话的传输通道。
  - `per-peer`: `agent:<agentId>:dm:<peerId>`。
  - `per-channel-peer`: `agent:<agentId>:<channel>:dm:<peerId>`。
  - `per-account-channel-peer`: `agent:<agentId>:<channel>:<accountId>:dm:<peerId>`（accountId 默认为 `default`）。
  - 如果 `session.identityLinks` 匹配提供商前缀的对等 ID（例如 `telegram:123`），规范密钥将替换 `<peerId>`，以便同一个人跨频道共享会话。
- 群组聊天隔离状态：`agent:<agentId>:<channel>:group:<id>`（房间/频道使用 `agent:<agentId>:<channel>:channel:<id>`）。
  - Telegram 论坛主题将 `:topic:<threadId>` 附加到群组 ID 以进行隔离。
  - 遗留的 `group:<id>` 密钥仍被识别用于迁移。
- 入站上下文可能仍使用 `group:<id>`；频道从 `Provider` 推断并规范化为规范 `agent:<agentId>:<channel>:group:<id>` 形式。
- 其他来源：
  - 定时任务：`cron:<job.id>`
  - Webhooks: `hook:<uuid>`（除非由 hook 显式设置）
  - 节点运行：`node-<nodeId>`

## 生命周期

- 重置策略：会话在过期前会被复用，且过期判断在下一次入站消息时进行。
- 每日重置：默认为 **网关主机上的本地时间凌晨 4:00**。一旦会话的最后更新时间早于最近的每日重置时间，该会话即视为失效。
- 空闲重置（可选）：`idleMinutes` 添加一个滑动空闲窗口。当同时配置了每日重置和空闲重置时，**任一先过期**将强制创建新会话。
- 旧版仅空闲模式：如果您设置了 `session.idleMinutes` 但未设置任何 `session.reset`/`resetByType` 配置，OpenClaw 将保持仅空闲模式以兼容旧版本。
- 按类型覆盖（可选）：`resetByType` 允许您为 `direct`、`group` 和 `thread` 会话覆盖策略（线程 = Slack/Discord 线程，Telegram 主题，由连接器提供的 Matrix 线程）。
- 按通道覆盖（可选）：`resetByChannel` 覆盖特定通道的重置策略（适用于该通道的所有会话类型，并优先于 `reset`/`resetByType`）。
- 重置触发器：精确匹配 `/new` 或 `/reset`（加上 `resetTriggers` 中的任何额外内容）将启动新的会话 ID 并传递消息的其余部分。`/new <model>` 接受模型别名、`provider/model` 或提供商名称（模糊匹配）以设置新会话模型。如果单独发送 `/new` 或 `/reset`，OpenClaw 将运行简短的“你好”问候回合以确认重置。
- 手动重置：从存储中删除特定键或删除 JSONL 转录；下一条消息将重新创建它们。
- 隔离的 cron 任务：每次运行始终生成一个新的 `sessionId`（无空闲复用）。

## 发送策略（可选）

无需列出单个 ID 即可阻止特定会话类型的交付。

```json5
{
  session: {
    sendPolicy: {
      rules: [
        { action: "deny", match: { channel: "discord", chatType: "group" } },
        { action: "deny", match: { keyPrefix: "cron:" } },
        // Match the raw session key (including the `agent:<id>:` prefix).
        { action: "deny", match: { rawKeyPrefix: "agent:main:discord:" } },
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
- `openclaw sessions --json` — 转储每个条目（使用 `--active <minutes>` 过滤）。
- `openclaw gateway call sessions.list --params '{}'` — 从运行的网关获取会话（使用 `--url`/`--token` 进行远程网关访问）。
- 在聊天中发送 `/status` 作为独立消息，以查看代理是否可达、使用了多少会话上下文、当前的思考/详细切换状态，以及您的 WhatsApp Web 凭据上次刷新时间（有助于发现需要重新链接的情况）。
- 发送 `/context list` 或 `/context detail` 以查看系统提示词和注入的工作区文件内容（以及最大的上下文贡献者）。
- 发送 `/stop`（或独立的中止短语，如 `stop`、`stop action`、`stop run`、`stop openclaw`）以中止当前运行，清除该会话的排队后续操作，并停止由此生成的任何子代理运行（回复中包含已停止的数量）。
- 发送 `/compact`（可选指令）作为独立消息以总结较旧的上下文并释放窗口空间。参见 [/concepts/compaction](/concepts/compaction)。
- JSONL 转录可以直接打开以审查完整轮次。

## 提示

- 将主密钥专用于 1:1 流量；让群组保留自己的密钥。
- 自动化清理时，请删除单个密钥而不是整个存储，以在其他地方保留上下文。

## 会话来源元数据

每个会话条目记录其来源（尽力而为），存储在 `origin` 中：

- `label`：人工标签（从对话标签 + 群组主题/通道解析）
- `provider`：标准化通道 ID（包括扩展）
- `from`/`to`：来自入站信封的原始路由 ID
- `accountId`：提供商账户 ID（多账户时）
- `threadId`：当通道支持时的线程/主题 ID
  来源字段针对直接消息、通道和群组进行填充。如果连接器仅更新交付路由（例如，为了保持 DM 主会话新鲜），它仍应提供入站上下文，以便会话保留其解释元数据。扩展可以通过在入站上下文中发送 `ConversationLabel`、`GroupSubject`、`GroupChannel`、`GroupSpace` 和 `SenderName` 来执行此操作，并调用 `recordSessionMetaFromInbound`（或将相同的上下文传递给 `updateLastRoute`）。