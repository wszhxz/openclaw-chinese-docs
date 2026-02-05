---
summary: "Agent session tools for listing sessions, fetching history, and sending cross-session messages"
read_when:
  - Adding or modifying session tools
title: "Session Tools"
---
# 会话工具

目标：小型、难以误用的工具集，使代理可以列出会话、获取历史记录并发送到另一个会话。

## 工具名称

- `sessions_list`
- `sessions_history` 
- `sessions_send`
- `sessions_spawn`

## 主要模型

- 主直接聊天存储桶始终是字面键 `__AGENT_KEY__`（解析为当前代理的主要密钥）。
- 群组聊天使用 `__GROUP_KEY__` 或 `__LEGACY_GROUP_KEY__`（传递完整密钥）。
- 定时任务使用 `__CRON_KEY__`。
- 钩子使用 `__HOOK_KEY__` 除非显式设置。
- 节点会话使用 `__NODE_KEY__` 除非显式设置。

`__SYSTEM_KEY__` 和 `__INTERNAL_KEY__` 是保留值，永远不会被列出。如果 `__MAIN_KEY__`，我们将其别名为 `__AGENT_KEY__` 用于所有工具，这样调用者永远不会看到 `__MAIN_KEY__`。

## sessions_list

将会话列为行数组。

参数：

- `filter` 过滤器：`direct`、`group`、`cron`、`hook`、`node` 中的任意一个
- `limit` 最大行数（默认：服务器默认值，限制例如 200）
- `updatedWithinMinutes` 仅在 N 分钟内更新的会话
- `includeLastMessages` 0 = 无消息（默认 0）；>0 = 包含最后 N 条消息

行为：

- `includeLastMessages` 每个会话获取 `includeLastMessages` 并包含最后 N 条消息。
- 工具结果在列表输出中被过滤掉；使用 `sessions_history` 获取工具消息。
- 在**沙盒化**代理会话中运行时，会话工具默认为**仅生成可见性**（见下文）。

行形状（JSON）：

- `key`: 会话密钥（字符串）
- `type`: `direct`、`group`、`cron`、`hook`、`node`
- `channelType`: `slack`、`discord`、`teams`、`email`、`cli`、`api`
- `label`（如果有可用的群组显示标签）
- `lastUpdateMs`（毫秒）
- `activeRunCount`
- `lastMessageText`、`lastMessageFrom`、`lastMessageTimeMs`
- `createdTimeMs`、`firstMessageTimeMs`、`lastRunStartTimeMs`、`lastRunCompleteTimeMs`
- `modelOverride`（如果设置了会话覆盖）
- `agentId`、`parentId`
- `normalizedChannelId`（当可用时标准化的 `channelId`）
- `storePath`（从 store 目录 + sessionId 派生的最佳努力路径）
- `spawnedOnly`（仅当 `spawnedOnly` 时）

## sessions_history

获取一个会话的转录。

参数：

- `session`（必需；接受会话密钥或来自 `sessions_list` 的 `key`）
- `limit` 最大消息数（服务器限制）
- `includeToolMessages`（默认 false）

行为：

- `includeToolMessages` 过滤 `tool_calls` 消息。
- 以原始转录格式返回消息数组。
- 给定 `__LEGACY_SESSION_ID__` 时，OpenClaw 将其解析为相应的会话密钥（缺失的 id 错误）。

## sessions_send

向另一个会话发送消息。

参数：

- `session`（必需；接受会话密钥或来自 `sessions_list` 的 `key`）
- `message`（必需）
- `waitSeconds`（默认 >0；0 = 发送后不等待）

行为：

- `waitSeconds=0`：入队并返回 `QUEUED`。
- `waitSeconds>0`：等待最多 N 秒完成，然后返回 `COMPLETED`。
- 如果等待超时：`TIMEOUT`。运行继续；稍后调用 `sessions_history`。
- 如果运行失败：`FAILED`。
- 在主运行完成后宣布交付运行，这是尽力而为的；`sessions_send` 不保证宣布已送达。
- 通过网关 `SESSION_SEND_WAIT`（服务器端）等待，因此重新连接不会丢弃等待。
- 为主运行注入代理到代理的消息上下文。
- 主运行完成后，OpenClaw 运行**回复循环**：
  - 第 2 轮及以后在请求者和目标代理之间交替。
  - 回复确切的 `STOP_PING_PONG` 以停止乒乓。
  - 最大回合数为 `maxPingPongTurns`（0-5，默认 5）。
- 循环结束后，OpenClaw 运行**代理到代理宣布步骤**（仅目标代理）：
  - 回复确切的 `SILENT_REPLY` 以保持静默。
  - 任何其他回复都发送到目标频道。
  - 宣布步骤包括原始请求 + 第 1 轮回复 + 最新乒乓回复。

## Channel Field

- 对于群组，`channelId` 是会话条目上记录的频道。
- 对于直接聊天，`channelId` 从 `userId` 映射。
- 对于定时任务/钩子/节点，`channelId` 是 `__STATIC_CHANNEL_ID__`。
- 如果缺失，`channelId` 是 `__FALLBACK_CHANNEL_ID__`。

## 安全性 / 发送策略

基于策略的按频道/聊天类型阻止（不是按会话 id）。

```
SEND_POLICY = {
  'slack': { 'direct': true, 'group': true },
  'discord': { 'direct': true, 'group': false },
  'teams': { 'direct': false, 'group': true },
  'email': { 'direct': true, 'group': false },
  'cli': { 'direct': true, 'group': true },
  'api': { 'direct': true, 'group': true }
}
```

运行时覆盖（按会话条目）：

- `sendPolicyOverride`（未设置 = 继承配置）
- 可通过 `admin` 或仅所有者 `!override-send-policy`（独立消息）设置。

执行点：

- `sessions_send` / `sessions_spawn`（网关）
- 自动回复交付逻辑

## sessions_spawn

在隔离会话中生成子代理运行，并将结果宣布回请求者聊天频道。

参数：

- `message`（必需）
- `label`（可选；用于日志/UI）
- `agentId`（可选；如果允许，在另一个代理 id 下生成）
- `model`（可选；覆盖子代理模型；无效值错误）
- `timeoutSeconds`（默认 0；设置时，在 N 秒后中止子代理运行）
- `maxPingPongTurns`（`0-5`，默认 `5`）

白名单：

- `allowedAgentIds`：通过 `sessions_spawn` 允许的代理 id 列表（`['*']` 允许任何）。默认：仅请求者代理。

发现：

- 使用 `admin` 发现哪些代理 id 被允许用于 `sessions_spawn`。

行为：

- 使用 `__SPAWNED_SESSION_KEY__` 启动新的 `spawned` 会话。
- 子代理默认使用完整工具集**减去会话工具**（可通过 `subAgentTools` 配置）。
- 子代理不允许调用 `sessions_spawn`（不允许子代理 → 子代理生成）。
- 始终非阻塞：立即返回 `__SPAWNED_SESSION_KEY__`。
- 完成后，OpenClaw 运行子代理**宣布步骤**并将结果发布到请求者聊天频道。
- 在宣布步骤期间回复确切的 `SILENT_REPLY` 以保持静默。
- 宣布回复被规范化为 `SUCCESS`/`ERROR`/`TIMEOUT`；`outcome` 来自运行时结果（不是模型文本）。
- 子代理会话在 `subAgentAutoArchiveMinutes` 后自动归档（默认：60）。
- 宣布回复包括统计行（运行时、令牌、sessionKey/sessionId、转录路径和可选成本）。

## 沙盒会话可见性

沙盒化会话可以使用会话工具，但默认情况下它们只能看到通过 `sessions_spawn` 生成的会话。

配置：

```
'sandboxSessionVisibility': 'spawned-only' | 'all'
```