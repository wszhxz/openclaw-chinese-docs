---
summary: "Sub-agents: spawning isolated agent runs that announce results back to the requester chat"
read_when:
  - You want background/parallel work via the agent
  - You are changing sessions_spawn or sub-agent tool policy
  - You are implementing or troubleshooting thread-bound subagent sessions
title: "Sub-Agents"
---
# 子代理

子代理是从现有代理运行中生成的后台代理运行。它们在自己的会话中运行 (`agent:<agentId>:subagent:<uuid>`)，并在完成后**通知**其结果给请求者的聊天频道。

## 斜杠命令

使用 `/subagents` 检查或控制当前会话的子代理运行：

- `/subagents list`
- `/subagents kill <id|#|all>`
- `/subagents log <id|#> [limit] [tools]`
- `/subagents info <id|#>`
- `/subagents send <id|#> <message>`
- `/subagents steer <id|#> <message>`
- `/subagents spawn <agentId> <task> [--model <model>] [--thinking <level>]`

Discord 线程绑定控制：

- `/focus <subagent-label|session-key|session-id|session-label>`
- `/unfocus`
- `/agents`
- `/session ttl <duration|off>`

`/subagents info` 显示运行元数据（状态、时间戳、会话ID、转录路径、清理）。

### 生成行为

`/subagents spawn` 作为用户命令启动后台子代理，而不是内部中继，并在运行结束后向请求者的聊天发送一个最终的完成更新。

- 生成命令是非阻塞的；它会立即返回一个运行ID。
- 完成后，子代理会向请求者的聊天频道发送一个摘要/结果消息。
- 对于手动生成，传递是具有弹性的：
  - OpenClaw 首先尝试使用稳定的幂等键进行直接 `agent` 传递。
  - 如果直接传递失败，则回退到队列路由。
  - 如果队列路由仍然不可用，则在最终放弃之前使用短指数退避重试通知。
- 完成消息是一个系统消息，包括：
  - `Result` (`assistant` 回复文本，或如果助手回复为空则为最新的 `toolResult`)
  - `Status` (`completed successfully` / `failed` / `timed out`)
  - 紧凑的运行时/令牌统计信息
- `--model` 和 `--thinking` 覆盖该特定运行的默认设置。
- 使用 `info`/`log` 在完成后检查详细信息和输出。
- `/subagents spawn` 是一次性模式 (`mode: "run"`)。对于持久线程绑定会话，请使用 `sessions_spawn` 并结合 `thread: true` 和 `mode: "session"`。

主要目标：

- 并行化“研究/长时间任务/慢工具”工作而不阻塞主运行。
- 默认隔离子代理（会话分离 + 可选沙箱）。
- 保持工具表面难以误用：子代理默认情况下**不**获取会话工具。
- 支持可配置的嵌套深度以支持编排模式。

费用说明：每个子代理都有其**独立**的上下文和令牌使用情况。对于繁重或重复的任务，请为子代理设置更便宜的模型，并将主代理保留在更高质量的模型上。您可以通过 `agents.defaults.subagents.model` 或每个代理的覆盖设置来配置此选项。

## 工具

使用 `sessions_spawn`：

- 启动子代理运行 (`deliver: false`，全局通道: `subagent`)
- 然后运行一个公告步骤，并将公告回复发布到请求者的聊天频道
- 默认模型：继承调用者，除非你设置了 `agents.defaults.subagents.model`（或每个代理的 `agents.list[].subagents.model`）；显式的 `sessions_spawn.model` 仍然优先。
- 默认思考：继承调用者，除非你设置了 `agents.defaults.subagents.thinking`（或每个代理的 `agents.list[].subagents.thinking`）；显式的 `sessions_spawn.thinking` 仍然优先。

工具参数：

- `task` (必需)
- `label?` (可选)
- `agentId?` (可选；如果允许，可以在另一个代理ID下生成)
- `model?` (可选；覆盖子代理模型；无效值将被跳过，并且子代理将在默认模型上运行，并在工具结果中发出警告)
- `thinking?` (可选；覆盖子代理运行的思考级别)
- `runTimeoutSeconds?` (默认 `0`；设置后，子代理运行将在N秒后中止)
- `thread?` (默认 `false`；当 `true` 时，请求此子代理会话的频道线程绑定)
- `mode?` (`run|session`)
  - 默认是 `run`
  - 如果省略 `thread: true` 和 `mode`，默认变为 `session`
  - `mode: "session"` 需要 `thread: true`
- `cleanup?` (`delete|keep`，默认 `keep`)

## Discord 线程绑定会话

当启用线程绑定时，子代理可以绑定到一个Discord线程，因此该线程中的后续用户消息将继续路由到相同的子代理会话。

快速流程：

1. 使用 `thread: true`（和可选的 `mode: "session"`）通过 `sessions_spawn` 生成。
2. OpenClaw 为该会话目标创建或绑定一个Discord线程。
3. 该线程中的回复和后续消息将路由到绑定的会话。
4. 使用 `/session ttl` 检查/更新自动失焦TTL。
5. 使用 `/unfocus` 手动分离。

手动控制：

- `/focus <target>` 将当前线程（或创建一个）绑定到子代理/会话目标。
- `/unfocus` 移除当前Discord线程的绑定。
- `/agents` 列出活动运行和绑定状态 (`thread:<id>` 或 `unbound`)。
- `/session ttl` 仅适用于聚焦的Discord线程。

配置开关：

- 全局默认：`session.threadBindings.enabled`，`session.threadBindings.ttlHours`
- Discord 覆盖：`channels.discord.threadBindings.enabled`，`channels.discord.threadBindings.ttlHours`
- 生成自动绑定选择加入：`channels.discord.threadBindings.spawnSubagentSessions`

参见 [Discord](/channels/discord)，[配置参考](/gateway/configuration-reference)，和 [斜杠命令](/tools/slash-commands)。

白名单：

- `agents.list[].subagents.allowAgents`：可以通过 `agentId` 目标化的代理ID列表 (`["*"]` 允许任何)。默认：只有请求者代理。

发现：

- 使用 `agents_list` 查看当前允许的 `sessions_spawn` 的代理ID。

自动归档：

- 子代理会话在 `agents.defaults.subagents.archiveAfterMinutes` 后自动归档（默认：60）。
- 归档使用 `sessions.delete` 并将记录重命名为 `*.deleted.<timestamp>`（同一文件夹）。
- `cleanup: "delete"` 在宣布后立即归档（通过重命名仍然保留记录）。
- 自动归档是尽力而为；如果网关重启，待处理的计时器将丢失。
- `runTimeoutSeconds` 不会自动归档；它只会停止运行。会话将保持到自动归档。
- 自动归档对深度-1和深度-2会话同样适用。

## 嵌套子代理

默认情况下，子代理不能生成自己的子代理 (`maxSpawnDepth: 1`)。您可以通过设置 `maxSpawnDepth: 2` 启用一级嵌套，这允许 **编排器模式**：主代理 → 编排器子代理 → 工作者子子代理。

### 如何启用

```json5
{
  agents: {
    defaults: {
      subagents: {
        maxSpawnDepth: 2, // allow sub-agents to spawn children (default: 1)
        maxChildrenPerAgent: 5, // max active children per agent session (default: 5)
        maxConcurrent: 8, // global concurrency lane cap (default: 8)
      },
    },
  },
}
```

### 深度级别

| 深度 | 会话键形状                            | 角色                                          | 可生成？                   |
| ----- | -------------------------------------------- | --------------------------------------------- | ---------------------------- |
| 0     | `agent:<id>:main`                            | 主代理                                    | 总是                       |
| 1     | `agent:<id>:subagent:<uuid>`                 | 子代理（当允许深度2时为编排器） | 仅当 `maxSpawnDepth >= 2` |
| 2     | `agent:<id>:subagent:<uuid>:subagent:<uuid>` | 子子代理（叶工作者）                   | 从不                        |

### 宣布链

结果沿链向上流动：

1. 深度-2工作者完成 → 向其父代理（深度-1编排器）宣布
2. 深度-1编排器接收宣布，综合结果，完成 → 向主代理宣布
3. 主代理接收宣布并交付给用户

每个级别仅看到其直接子代理的宣布。

### 按深度的工具策略

- **深度 1（编排器，当 `maxSpawnDepth >= 2`)**：获取 `sessions_spawn`，`subagents`，`sessions_list`，`sessions_history` 以便管理其子代理。其他会话/系统工具被拒绝。
- **深度 1（叶节点，当 `maxSpawnDepth == 1`)**：无会话工具（当前默认行为）。
- **深度 2（叶工作者）**：无会话工具 — `sessions_spawn` 在深度2时总是被拒绝。无法生成进一步的子代理。

### 每代理生成限制

每个代理会话（任何深度）最多可以有 `maxChildrenPerAgent` （默认：5）个活动子代理。这防止单个编排器产生失控的扇出。

### 级联停止

停止深度-1编排器会自动停止其所有深度-2子代理：

- `/stop` 在主聊天中停止所有深度-1代理，并级联到它们的深度-2子代理。
- `/subagents kill <id>` 停止特定的子代理，并级联到其子代理。
- `/subagents kill all` 停止请求者的所有子代理，并级联。

## 认证

子代理认证通过 **代理ID** 解决，而不是会话类型：

- 子代理会话密钥是 `agent:<agentId>:subagent:<uuid>`。
- 认证存储从该代理的 `agentDir` 加载。
- 主代理的认证配置文件作为 **后备** 合并；代理配置文件在冲突时覆盖主配置文件。

注意：合并是累加的，因此主配置文件始终可用作后备。每个代理的完全隔离认证尚不支持。

## 公告

子代理通过公告步骤报告回：

- 公告步骤在子代理会话中运行（不是请求者会话）。
- 如果子代理回复正好是 `ANNOUNCE_SKIP`，则不会发布任何内容。
- 否则，公告回复通过后续的 `agent` 调用（`deliver=true`）发布到请求者的聊天频道。
- 公告回复在可用时保留线程/主题路由（Slack 线程、Telegram 主题、Matrix 线程）。
- 公告消息标准化为一个稳定的模板：
  - `Status:` 根据运行结果派生（`success`，`error`，`timeout` 或 `unknown`）。
  - `Result:` 公告步骤中的摘要内容（如果缺失则为 `(not available)`）。
  - `Notes:` 错误详细信息和其他有用上下文。
- `Status` 不是从模型输出推断的；它来自运行时结果信号。

公告负载在末尾包含一行统计信息（即使被包装）：

- 运行时间（例如，`runtime 5m12s`）
- 令牌使用情况（输入/输出/总计）
- 配置了模型定价时的估算成本 (`models.providers.*.models[].cost`)
- `sessionKey`，`sessionId` 和 transcripts 路径（以便主代理可以通过 `sessions_history` 获取历史记录或检查磁盘上的文件）

## 工具策略（子代理工具）

默认情况下，子代理获得 **除会话工具外的所有工具** 和系统工具：

- `sessions_list`
- `sessions_history`
- `sessions_send`
- `sessions_spawn`

当 `maxSpawnDepth >= 2` 时，深度-1 编排子代理还会接收 `sessions_spawn`，`subagents`，`sessions_list` 和 `sessions_history`，以便管理其子代理。

通过配置重写：

```json5
{
  agents: {
    defaults: {
      subagents: {
        maxConcurrent: 1,
      },
    },
  },
  tools: {
    subagents: {
      tools: {
        // deny wins
        deny: ["gateway", "cron"],
        // if allow is set, it becomes allow-only (deny still wins)
        // allow: ["read", "exec", "process"]
      },
    },
  },
}
```

## 并发

子代理使用专用的进程内队列通道：

- 通道名称：`subagent`
- 并发：`agents.defaults.subagents.maxConcurrent`（默认 `8`）

## 停止

- 在请求者聊天中发送 `/stop` 终止请求者会话，并停止从其生成的所有活动子代理运行，级联到嵌套的子代理。
- `/subagents kill <id>` 停止特定的子代理，并级联到其子代理。

## 限制

- 子代理公告是**尽力而为**的。如果网关重启，待处理的“回告”工作将丢失。
- 子代理仍然共享相同的网关进程资源；将 `maxConcurrent` 视为安全阀。
- `sessions_spawn` 始终是非阻塞的：它立即返回 `{ status: "accepted", runId, childSessionKey }`。
- 子代理上下文仅注入 `AGENTS.md` + `TOOLS.md`（不包括 `SOUL.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md` 或 `BOOTSTRAP.md`）。
- 最大嵌套深度为5 (`maxSpawnDepth` 范围：1–5)。对于大多数用例，建议使用深度2。
- `maxChildrenPerAgent` 限制每个会话的活动子代理数量（默认：5，范围：1–20）。