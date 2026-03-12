---
summary: "Session management rules, keys, and persistence for chats"
read_when:
  - Modifying session handling or storage
title: "Session Management"
---
# 会话管理

OpenClaw 将**每个智能体的单一直接聊天会话**视为主会话。直接聊天会折叠为 `agent:<agentId>:<mainKey>`（默认为 `main`），而群组/频道聊天则拥有各自独立的键。`session.mainKey` 设置将被尊重。

使用 `session.dmScope` 控制**直接消息（DM）** 的分组方式：

- `main`（默认）：所有 DM 共享主会话，以保证上下文连续性。
- `per-peer`：按发送者 ID 跨频道隔离。
- `per-channel-peer`：按频道 + 发送者隔离（推荐用于多用户收件箱）。
- `per-account-channel-peer`：按账号 + 频道 + 发送者隔离（推荐用于多账号收件箱）。  
  使用 `session.identityLinks` 将带提供方前缀的对端 ID 映射为标准身份，以便在启用 `per-peer`、`per-channel-peer` 或 `per-account-channel-peer` 时，同一人在不同频道中的 DM 会话可共享。

## 安全 DM 模式（推荐用于多用户场景）

> **安全警告：** 如果您的智能体可接收**多位用户**发来的 DM，请务必考虑启用安全 DM 模式。否则，所有用户将共享同一对话上下文，可能导致用户间私密信息泄露。

**默认设置下问题的示例：**

- 爱丽丝（`<SENDER_A>`）向您的智能体发送一条关于私密话题（例如：医疗预约）的消息  
- 鲍勃（`<SENDER_B>`）向您的智能体提问：“我们刚才在聊什么？”  
- 由于两个 DM 共享同一会话，模型可能利用爱丽丝先前的上下文回答鲍勃。

**解决方案：** 设置 `dmScope`，实现按用户隔离会话：

```json5
// ~/.openclaw/openclaw.json
{
  session: {
    // Secure DM mode: isolate DM context per channel + sender.
    dmScope: "per-channel-peer",
  },
}
```

**应启用该模式的情形：**

- 您已为多个发送者配置了配对审批  
- 您使用了含多个条目的 DM 白名单  
- 您设置了 `dmPolicy: "open"`  
- 多个电话号码或账号均可向您的智能体发送消息  

注意事项：

- 默认为 `dmScope: "main"`（所有 DM 共享主会话），以保障上下文连续性；单用户场景下此设置完全适用。  
- 本地 CLI 初始化流程在未显式设置时默认写入 `session.dmScope: "per-channel-peer"`（已有显式值将被保留）。  
- 同一频道下的多账号收件箱，建议优先使用 `per-account-channel-peer`。  
- 若同一人通过多个频道联系您，请使用 `session.identityLinks` 将其 DM 会话合并至一个标准身份。  
- 您可通过 `openclaw security audit` 验证 DM 设置（参见 [安全](/cli/security)）。

## 网关是唯一可信源

所有会话状态均由**网关**（即“主” OpenClaw）持有。UI 客户端（macOS 应用、WebChat 等）必须向网关查询会话列表与 token 数量，不得读取本地文件。

- 在**远程模式**下，您所关注的会话存储位于远程网关主机上，而非您的 Mac。  
- UI 中显示的 token 数量来源于网关存储字段（`inputTokens`、`outputTokens`、`totalTokens`、`contextTokens`）。客户端不会解析 JSONL 转录文件来“修正”统计总数。

## 状态存储位置

- 在**网关主机**上：  
  - 存储文件：`~/.openclaw/agents/<agentId>/sessions/sessions.json`（每个智能体一份）。  
- 转录文件：`~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`（Telegram 主题会话使用 `.../<SessionId>-topic-<threadId>.jsonl`）。  
- 存储结构为映射表 `sessionKey -> { sessionId, updatedAt, ... }`。删除其中条目是安全的；条目将在需要时自动重建。  
- 群组条目可能包含 `displayName`、`channel`、`subject`、`room` 和 `space` 字段，用于在 UI 中标注会话。  
- 会话条目包含 `origin` 元数据（标签 + 路由提示），使 UI 可说明该会话来源。  
- OpenClaw **不读取**旧版 Pi/Tau 会话文件夹。

## 维护

OpenClaw 对会话存储执行维护操作，以确保 `sessions.json` 和转录文件随时间推移保持规模可控。

### 默认值

- `session.maintenance.mode`：`warn`  
- `session.maintenance.pruneAfter`：`30d`  
- `session.maintenance.maxEntries`：`500`  
- `session.maintenance.rotateBytes`：`10mb`  
- `session.maintenance.resetArchiveRetention`：默认为 `pruneAfter`（`30d`）  
- `session.maintenance.maxDiskBytes`：未设置（禁用）  
- `session.maintenance.highWaterBytes`：启用预算控制时，默认为 `80%` 占 `maxDiskBytes` 的比例  

### 工作机制

维护操作在会话存储写入期间自动运行；您也可通过 `openclaw sessions cleanup` 手动触发。

- `mode: "warn"`：仅报告将被清理的条目，不修改任何条目或转录文件。  
- `mode: "enforce"`：按以下顺序执行清理：  
  1. 清理早于 `pruneAfter` 的陈旧条目  
  2. 将条目数量上限设为 `maxEntries`（优先移除最旧条目）  
  3. 对已移除且不再被引用的条目，归档其转录文件  
  4. 根据保留策略，清除过期的 `*.deleted.<timestamp>` 和 `*.reset.<timestamp>` 归档  
  5. 当 `sessions.json` 超过 `rotateBytes` 时轮转  
  6. 若设置了 `maxDiskBytes`，则强制执行磁盘预算至 `highWaterBytes`（优先清理最旧的制品，其次是最旧的会话）  

### 大型存储的性能注意事项

大型会话存储在高吞吐量场景中十分常见。维护工作属于写入路径任务，因此存储规模过大可能增加写入延迟。

显著增加开销的因素包括：

- 过高的 `session.maintenance.maxEntries` 值  
- 过长的 `pruneAfter` 时间窗口，导致陈旧条目长期滞留  
- `~/.openclaw/agents/<agentId>/sessions/` 中存在大量转录/归档制品  
- 启用磁盘预算（`maxDiskBytes`）但未设置合理的清理/数量上限  

建议措施：

- 生产环境中使用 `mode: "enforce"`，使存储增长自动受限  
- 同时设置时间与数量限制（`pruneAfter` + `maxEntries`），而非仅设其一  
- 大型部署中，设置 `maxDiskBytes` + `highWaterBytes` 作为硬性上限  
- 将 `highWaterBytes` 设为明显低于 `maxDiskBytes`（默认为 80%）  
- 配置变更后，运行 `openclaw sessions cleanup --dry-run --json` 验证预期影响，再正式启用  
- 对频繁活跃的会话，手动执行清理时传入 `--active-key`  

### 自定义示例

采用保守的强制策略：

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

为会话目录启用硬性磁盘预算：

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

针对更大规模安装进行调优（示例）：

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

从 CLI 预览或强制执行维护：

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
```

## 会话裁剪

OpenClaw 默认在调用大语言模型（LLM）前，从内存上下文中裁剪掉**陈旧的工具执行结果**。  
该操作**不会**重写 JSONL 历史记录。详见 [/concepts/session-pruning](/concepts/session-pruning)。

## 预压缩内存刷新

当会话临近自动压缩时，OpenClaw 可执行一次**静默内存刷新**，提醒模型将持久化笔记写入磁盘。该操作仅在工作区可写时运行。详见 [内存](/concepts/memory) 和 [压缩](/concepts/compaction)。

## 传输通道 → 会话键映射

- 直接聊天遵循 `session.dmScope`（默认为 `main`）：  
  - `main`：`agent:<agentId>:<mainKey>`（保障跨设备/频道的上下文连续性）  
    - 多个电话号码和频道可映射至同一智能体主键；它们仅作为通向单一对话的传输通道。  
  - `per-peer`：`agent:<agentId>:dm:<peerId>`  
  - `per-channel-peer`：`agent:<agentId>:<channel>:dm:<peerId>`  
  - `per-account-channel-peer`：`agent:<agentId>:<channel>:<accountId>:dm:<peerId>`（accountId 默认为 `default`）  
  - 若 `session.identityLinks` 匹配某个带提供方前缀的对端 ID（例如 `telegram:123`），则标准键将替换 `<peerId>`，从而实现同一人在不同频道间共享会话。  
- 群组聊天隔离状态：`agent:<agentId>:<channel>:group:<id>`（房间/频道使用 `agent:<agentId>:<channel>:channel:<id>`）  
  - Telegram 论坛主题会在群组 ID 后附加 `:topic:<threadId>` 以实现隔离。  
  - 旧版 `group:<id>` 键仍被识别，用于迁移兼容。  
- 入站上下文可能仍使用 `group:<id>`；频道由 `Provider` 推断，并规范化为标准 `agent:<agentId>:<channel>:group:<id>` 形式。  
- 其他来源：  
  - 定时任务（Cron jobs）：`cron:<job.id>`  
  - Webhook：`hook:<uuid>`（除非 hook 显式指定）  
  - Node 运行：`node-<nodeId>`  

## 生命周期

- 重置策略：会话在过期前会被重复使用，而过期时间在下一条入站消息到达时进行判定。  
- 每日重置：默认为**网关主机本地时间凌晨 4:00**。若会话最后一次更新时间早于最近一次每日重置时间，则该会话即被视为陈旧。  
- 空闲重置（可选）：`idleMinutes` 添加一个滑动空闲窗口。当同时配置了每日重置和空闲重置时，**先到期者**将强制开启新会话。  
- 遗留仅空闲模式：若仅设置 `session.idleMinutes` 而未配置任何 `session.reset`/`resetByType`，OpenClaw 将为向后兼容而保持仅空闲模式。  
- 按类型覆盖（可选）：`resetByType` 允许您为 `direct`、`group` 和 `thread` 类型的会话覆盖策略（thread = Slack/Discord 的会话线程、Telegram 主题、Matrix 会话线程（由连接器提供时））。  
- 按频道覆盖（可选）：`resetByChannel` 为指定频道覆盖重置策略（适用于该频道所有会话类型，并优先于 `reset`/`resetByType`）。  
- 重置触发器：精确匹配 `/new` 或 `/reset`（以及 `resetTriggers` 中定义的任意额外指令）将启动一个全新的会话 ID，并将消息其余部分透传。`/new <model>` 接受模型别名、`provider/model` 或提供商名称（支持模糊匹配），用于设定新会话所用模型。若单独发送 `/new` 或 `/reset`，OpenClaw 将执行一次简短的“hello”问候轮次以确认重置完成。  
- 手动重置：从存储中删除特定键，或移除 JSONL 转录文件；下一条消息将重新创建它们。  
- 隔离的定时任务始终在每次运行时生成一个全新的 `sessionId`（不复用空闲会话）。

## 发送策略（可选）

针对特定会话类型阻止消息投递，无需逐个列出 ID。

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

- `/send on` → 对当前会话启用发送  
- `/send off` → 对当前会话禁用发送  
- `/send inherit` → 清除覆盖设置，恢复使用配置规则  
  请将这些指令作为独立消息发送，以确保其被正确注册。

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

- `openclaw status` — 显示存储路径及最近的会话。  
- `openclaw sessions --json` — 导出全部条目（可用 `--active <minutes>` 进行过滤）。  
- `openclaw gateway call sessions.list --params '{}'` — 从正在运行的网关中获取会话（如需访问远程网关，请使用 `--url`/`--token`）。  
- 在聊天中单独发送 `/status`，可检查代理是否可达、当前会话上下文已使用比例、当前思考/详细输出开关状态，以及 WhatsApp Web 凭据最近刷新时间（有助于识别是否需要重新链接）。  
- 发送 `/context list` 或 `/context detail` 可查看系统提示词及注入的工作区文件内容（以及占用上下文最多的主要贡献项）。  
- 发送 `/stop`（或独立的中止短语，例如 `stop`、`stop action`、`stop run`、`stop openclaw`），将中止当前运行、清空该会话排队的后续操作，并停止由此会话派生的所有子代理运行（回复中包含已停止的数量统计）。  
- 单独发送 `/compact`（可选说明）以总结较早的上下文并释放窗口空间。参见 [/concepts/compaction](/concepts/compaction)。  
- JSONL 转录文件可直接打开，以完整回顾各轮对话。

## 提示

- 将主键专用于一对一通信；让群组各自维护其独立的键。  
- 自动化清理时，请删除个别键而非整个存储，以保留其他位置的上下文。

## 会话来源元数据

每个会话条目均记录其来源（尽力而为），字段位于 `origin` 中：

- `label`：人工标签（由对话标签 + 群组主题/频道解析得出）  
- `provider`：标准化频道 ID（含扩展名）  
- `from`/`to`：来自入站信封的原始路由 ID  
- `accountId`：提供商账户 ID（多账户场景下）  
- `threadId`：当频道支持时的线程/主题 ID  
  来源字段对私聊、频道和群组均予以填充。若某连接器仅更新投递路由（例如，为保持私聊主会话新鲜），仍应提供入站上下文，以便会话保有其解释性元数据。扩展程序可通过在入站上下文中发送 `ConversationLabel`、`GroupSubject`、`GroupChannel`、`GroupSpace` 和 `SenderName`，并调用 `recordSessionMetaFromInbound`（或向 `updateLastRoute` 传递相同上下文）来实现此目的。