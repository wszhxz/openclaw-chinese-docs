---
summary: "Sub-agents: spawning isolated agent runs that announce results back to the requester chat"
read_when:
  - You want background/parallel work via the agent
  - You are changing sessions_spawn or sub-agent tool policy
  - You are implementing or troubleshooting thread-bound subagent sessions
title: "Sub-Agents"
---
# 子代理

子代理是从现有代理运行中派生的后台代理运行。它们在自己的会话（`agent:<agentId>:subagent:<uuid>`）中运行，并且在完成后，**通知**其结果回到请求者的聊天频道。

## 斜杠命令

使用`/subagents`来检查或控制**当前会话**的子代理运行：

- `/subagents list`
- `/subagents kill <id|#|all>`
- `/subagents log <id|#> [limit] [tools]`
- `/subagents info <id|#>`
- `/subagents send <id|#> <message>`
- `/subagents steer <id|#> <message>`
- `/subagents spawn <agentId> <task> [--model <model>] [--thinking <level>]`

线程绑定控制：

这些命令适用于支持持久线程绑定的频道。请参阅下面的**支持线程的频道**。

- `/focus <subagent-label|session-key|session-id|session-label>`
- `/unfocus`
- `/agents`
- `/session idle <duration|off>`
- `/session max-age <duration|off>`

`/subagents info`显示运行元数据（状态、时间戳、会话ID、转录路径、清理）。

### 生成行为

`/subagents spawn`作为用户命令而非内部中继启动一个后台子代理，并在运行结束时向请求者聊天发送最终完成更新。

- 生成命令是非阻塞的；它立即返回一个运行ID。
- 完成后，子代理将摘要/结果消息通知回请求者聊天频道。
- 对于手动生成，交付是弹性的：
  - OpenClaw首先尝试直接`agent`交付，使用稳定的幂等键。
  - 如果直接交付失败，则回退到队列路由。
  - 如果队列路由仍然不可用，则以短指数退避重试公告，直到最终放弃。
- 完成交付给请求者会话的是运行时生成的内部上下文（不是用户编写的文本），包括：
  - `Result` (`assistant`回复文本，如果助手回复为空则为最新的`toolResult`)
  - `Status` (`completed successfully` / `failed` / `timed out` / `unknown`)
  - 紧凑的运行时/令牌统计
  - 一条交付指令告诉请求者代理以正常的助手语气重写（而不是转发原始内部元数据）
- `--model`和`--thinking`覆盖该特定运行的默认设置。
- 使用`info`/`log`来检查完成后的详细信息和输出。
- `/subagents spawn`是一次性模式(`mode: "run"`)。对于持久线程绑定会话，请使用带有`thread: true`和`mode: "session"`的`sessions_spawn`。
- 对于ACP套件会话（Codex, Claude Code, Gemini CLI），请使用带有`runtime: "acp"`的`sessions_spawn`并参见[ACP代理](/tools/acp-agents)。

主要目标：

- 并行化“研究/长任务/慢工具”工作而不阻塞主运行。
- 默认情况下保持子代理隔离（会话分离+可选沙箱）。
- 保持工具表面难以误用：子代理默认**不**获得会话工具。
- 支持可配置的嵌套深度以用于编排模式。

成本说明：每个子代理都有其**自己**的上下文和令牌使用。对于繁重或重复的任务，为子代理设置更便宜的模型，并保持您的主代理在更高品质的模型上。您可以通过`agents.defaults.subagents.model`或每代理覆盖来配置这一点。

## 工具

使用`sessions_spawn`：

- 启动子代理运行(`deliver: false`, 全局车道: `subagent`)
- 然后运行公告步骤并将公告回复发布到请求者聊天频道
- 默认模型：继承调用者，除非您设置了`agents.defaults.subagents.model`（或每代理`agents.list[].subagents.model`）；明确的`sessions_spawn.model`仍然优先。
- 默认思考：继承调用者，除非您设置了`agents.defaults.subagents.thinking`（或每代理`agents.list[].subagents.thinking`）；明确的`sessions_spawn.thinking`仍然优先。
- 默认运行超时：如果省略了`sessions_spawn.runTimeoutSeconds`，OpenClaw将在设置时使用`agents.defaults.subagents.runTimeoutSeconds`；否则它将回退到`0`（无超时）。

工具参数：

- `task` (必需)
- `label?` (可选)
- `agentId?` (可选；如果允许的话，在另一个代理ID下生成)
- `model?` (可选；覆盖子代理模型；无效值将被跳过，子代理将以默认模型运行并在工具结果中发出警告)
- `thinking?` (可选；覆盖子代理运行的思考级别)
- `runTimeoutSeconds?` (当设置时，默认为`agents.defaults.subagents.runTimeoutSeconds`，否则为`0`；当设置时，子代理运行将在N秒后中止)
- `thread?` (默认`false`；当`true`时，请求此子代理会话的频道线程绑定)
- `mode?` (`run|session`)
  - 默认为`run`
  - 如果`thread: true`和`mode`被省略，默认变为`session`
  - `mode: "session"`需要`thread: true`
- `cleanup?` (`delete|keep`, 默认`keep`)
- `sandbox?` (`inherit|require`, 默认`inherit`; `require`拒绝生成除非目标子运行时被沙箱化)
- `sessions_spawn` **不**接受频道交付参数(`target`, `channel`, `to`, `threadId`, `replyTo`, `transport`)。对于交付，请从生成的运行中使用`message`/`sessions_send`。

## 绑定线程的会话

当为频道启用线程绑定时，子代理可以绑定到一个线程，以便该线程中的后续用户消息继续路由到相同的子代理会话。

### 支持线程的频道

- Discord（目前唯一支持的频道）：支持持久线程绑定的子代理会话(`sessions_spawn`与`thread: true`)，手动线程控制(`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age`)，以及适配器密钥`channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`, 和 `channels.discord.threadBindings.spawnSubagentSessions`。

快速流程：

1. 使用`thread: true`（以及可选的`mode: "session"`）通过`sessions_spawn`生成。
2. OpenClaw在活动频道中创建或绑定一个线程到该会话目标。
3. 在该线程中的回复和后续消息路由到绑定的会话。
4. 使用`/session idle`检查/更新非活动自动失焦，并使用`/session max-age`控制硬上限。
5. 使用`/unfocus`手动解除绑定。

手动控制：

- `/focus <target>`将当前线程（或创建一个）绑定到子代理/会话目标。
- `/unfocus`移除当前绑定线程的绑定。
- `/agents`列出活跃运行和绑定状态(`thread:<id>`或`unbound`)。
- `/session idle`和`/session max-age`仅对聚焦的绑定线程有效。

配置开关：

- 全局默认：`session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`
- 频道覆盖和自动生成绑定密钥是特定于适配器的。请参阅上面的**支持线程的频道**。

请参阅[配置参考](/gateway/configuration-reference)和[斜杠命令](/tools/slash-commands)获取当前适配器详情。

允许列表：

- `agents.list[].subagents.allowAgents`：可通过`agentId`定位的代理ID列表(`["*"]`允许任何)。默认：只有请求者代理。
- 沙箱继承保护：如果请求者会话被沙箱化，`sessions_spawn`拒绝那些将运行未沙箱化的目标。

发现：

- 使用`agents_list`查看当前允许哪些代理ID用于`sessions_spawn`。

自动归档：

- 子代理会话在`agents.defaults.subagents.archiveAfterMinutes`后自动归档（默认：60）。
- 归档使用`sessions.delete`并将转录重命名为`*.deleted.<timestamp>`（同一文件夹）。
- `cleanup: "delete"`在公告后立即归档（仍通过重命名保留转录）。
- 自动归档尽最大努力；如果网关重启，待处理的计时器将丢失。
- `runTimeoutSeconds` **不**自动归档；它只停止运行。会话一直持续到自动归档。
- 自动归档同样适用于深度1和深度2的会话。

## 嵌套子代理

默认情况下，子代理不能生成自己的子代理(`maxSpawnDepth: 1`)。您可以通过设置`maxSpawnDepth: 2`来启用一层嵌套，这允许**编排模式**：主→编排子代理→工作者子子代理。

### 如何启用

```json5
{
  agents: {
    defaults: {
      subagents: {
        maxSpawnDepth: 2, // allow sub-agents to spawn children (default: 1)
        maxChildrenPerAgent: 5, // max active children per agent session (default: 5)
        maxConcurrent: 8, // global concurrency lane cap (default: 8)
        runTimeoutSeconds: 900, // default timeout for sessions_spawn when omitted (0 = no timeout)
      },
    },
  },
}
```

### 深度级别

| 深度 | 会话密钥形状                            | 角色                                          | 可以生成？                   |
| ----- | -------------------------------------------- | --------------------------------------------- | ---------------------------- |
| 0     | `agent:<id>:main`                            | 主代理                                    | 总是                       |
| 1     | `agent:<id>:subagent:<uuid>`                 | 子代理（当允许深度2时为编排器） | 仅当`maxSpawnDepth >= 2` |
| 2     | `agent:<id>:subagent:<uuid>:subagent:<uuid>` | 子子代理（叶工作者）                   | 从不                        |

### 公告链

结果沿链向上流动：

1. 深度2的工作者完成 → 向其父级（深度1的编排器）公告
2. 深度1的编排器接收公告，综合结果，完成 → 向主公告
3. 主代理接收公告并向用户传递

每一层只能看到来自其直接子级的公告。

### 按深度划分的工具策略

- **深度1（协调器，当`maxSpawnDepth >= 2`时）**：获取`sessions_spawn`、`subagents`、`sessions_list`、`sessions_history`以便管理其子节点。其他会话/系统工具保持被拒绝状态。
- **深度1（叶子节点，当`maxSpawnDepth == 1`时）**：没有会话工具（当前默认行为）。
- **深度2（叶子工作节点）**：没有会话工具 — `sessions_spawn` 在深度2时总是被拒绝。不能进一步生成子节点。

### 每个代理的生成限制

每个代理会话（任何深度）一次最多可以有`maxChildrenPerAgent`（默认值：5）个活跃子节点。这防止了从单个协调器开始的失控扩展。

### 级联停止

停止深度为1的协调器会自动停止其所有深度为2的子节点：

- 主聊天中的`/stop`会停止所有深度为1的代理，并级联到它们的深度为2的子节点。
- `/subagents kill <id>`停止特定的子代理并级联到其子节点。
- `/subagents kill all`停止请求者的全部子代理并级联。

## 身份验证

子代理的身份验证通过**代理ID**解决，而不是通过会话类型：

- 子代理会话密钥是`agent:<agentId>:subagent:<uuid>`。
- 从该代理的`agentDir`加载身份验证存储。
- 主代理的身份验证配置文件作为**后备**合并进来；在冲突时，代理配置文件优先于主配置文件。

注意：合并是累加的，因此主配置文件始终可用作后备。目前还不支持每个代理完全隔离的身份验证。

## 宣告

子代理通过宣告步骤报告回来：

- 宣告步骤在子代理会话内运行（不在请求者会话中）。
- 如果子代理回复恰好是`ANNOUNCE_SKIP`，则不会发布任何内容。
- 否则，交付取决于请求者的深度：
  - 顶层请求者会话使用带有外部交付（`deliver=true`）的后续`agent`调用
  - 嵌套请求者子代理会话接收内部后续注入（`deliver=false`），以便协调器可以在会话中合成子结果
  - 如果嵌套请求者子代理会话已不存在，OpenClaw会在可用时回退到该会话的请求者
- 子节点完成聚合范围限定在当前请求者运行中，以防止旧的先前运行子输出泄露到当前宣告中。
- 宣告回复在通道适配器上可用时保留线程/主题路由。
- 宣告上下文被规范化为一个稳定的内部事件块：
  - 来源（`subagent`或`cron`）
  - 子会话密钥/ID
  - 宣告类型 + 任务标签
  - 从运行时结果派生的状态行（`success`、`error`、`timeout`或`unknown`）
  - 宣告步骤的结果内容（如果缺失则为`(no output)`）
  - 一条后续指令，描述何时回复与保持沉默
- `Status`不是从模型输出推断出来的；它来自运行时结果信号。

宣告负载包括最后的一行统计信息（即使被包装）：

- 运行时间（例如，`runtime 5m12s`）
- 令牌使用情况（输入/输出/总计）
- 配置了模型定价时的估计成本（`models.providers.*.models[].cost`）
- `sessionKey`、`sessionId`和转录路径（这样主代理可以通过`sessions_history`获取历史记录或在磁盘上检查文件）
- 内部元数据仅用于编排；面向用户的回复应以正常的助手语气重写。

## 工具策略（子代理工具）

默认情况下，子代理获得**除会话工具外的所有工具**和系统工具：

- `sessions_list`
- `sessions_history`
- `sessions_send`
- `sessions_spawn`

当`maxSpawnDepth >= 2`时，深度为1的协调器子代理还会收到`sessions_spawn`、`subagents`、`sessions_list`和`sessions_history`，以便它们可以管理其子节点。

通过配置覆盖：

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
- 并发数：`agents.defaults.subagents.maxConcurrent`（默认值`8`）

## 停止

- 在请求者聊天中发送`/stop`将中止请求者会话，并停止从中生成的所有活动子代理运行，级联到嵌套子节点。
- `/subagents kill <id>`停止特定的子代理并级联到其子节点。

## 限制

- 子代理宣告是**尽力而为**的。如果网关重启，待处理的“宣告返回”工作将丢失。
- 子代理仍然共享相同的网关进程资源；将`maxConcurrent`视为安全阀。
- `sessions_spawn`始终是非阻塞的：它立即返回`{ status: "accepted", runId, childSessionKey }`。
- 子代理上下文仅注入`AGENTS.md` + `TOOLS.md`（无`SOUL.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`或`BOOTSTRAP.md`）。
- 最大嵌套深度为5（`maxSpawnDepth`范围：1–5）。对于大多数用例，建议使用深度2。
- `maxChildrenPerAgent`限制每个会话的活跃子节点数量（默认值：5，范围：1–20）。