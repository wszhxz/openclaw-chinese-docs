---
summary: "Sub-agents: spawning isolated agent runs that announce results back to the requester chat"
read_when:
  - You want background/parallel work via the agent
  - You are changing sessions_spawn or sub-agent tool policy
title: "Sub-Agents"
---
# 子代理

子代理允许你在不阻塞主对话的情况下运行后台任务。当你启动一个子代理时，它会在自己的隔离会话中运行，完成工作后会将结果通知回聊天。

**使用场景：**

- 在主代理继续回答问题的同时研究某个主题
- 并行运行多个长时间任务（网页抓取、代码分析、文件处理）
- 在多代理设置中将任务委托给专用代理

## 快速入门

使用子代理的最简单方法是自然地向代理提出请求：

> "启动一个子代理来研究最新的 Node.js 发行说明"

代理会在后台调用 `sessions_spawn` 工具。当子代理完成时，它会将其发现的结果通知回你的聊天。

你也可以明确指定选项：

> "启动一个子代理来分析今天的服务器日志。使用 gpt-5.2 并设置 5 分钟超时。"

## 工作原理

<Steps>
  <Step title="Main agent spawns">
    The main agent calls __CODE_BLOCK_1__ with a task description. The call is **non-blocking** — the main agent gets back __CODE_BLOCK_2__ immediately.
  </Step>
  <Step title="Sub-agent runs in the background">
    A new isolated session is created (__CODE_BLOCK_3__) on the dedicated __CODE_BLOCK_4__ queue lane.
  </Step>
  <Step title="Result is announced">
    When the sub-agent finishes, it announces its findings back to the requester chat. The main agent posts a natural-language summary.
  </Step>
  <Step title="Session is archived">
    The sub-agent session is auto-archived after 60 minutes (configurable). Transcripts are preserved.
  </Step>
</Steps>

<Tip>
Each sub-agent has its **own** context and token usage. Set a cheaper model for sub-agents to save costs — see [Setting a Default Model](#setting-a-default-model) below.
</Tip>

## 配置

子代理无需配置即可开箱即用。默认设置如下：

- 模型：目标代理的正常模型选择（除非 `subagents.model` 被设置）
- 思考：无子代理覆盖（除非 `subagents.thinking` 被设置）
- 最大并发数：8
- 自动归档：60分钟后

### 设置默认模型

使用更便宜的模型来节省代币费用：

```json5
{
  agents: {
    defaults: {
      subagents: {
        model: "minimax/MiniMax-M2.1",
      },
    },
  },
}
```

### 设置默认思考级别

```json5
{
  agents: {
    defaults: {
      subagents: {
        thinking: "low",
      },
    },
  },
}
```

### 按代理覆盖

在多代理设置中，你可以为每个代理设置子代理的默认值：

```json5
{
  agents: {
    list: [
      {
        id: "researcher",
        subagents: {
          model: "anthropic/claude-sonnet-4",
        },
      },
      {
        id: "assistant",
        subagents: {
          model: "minimax/MiniMax-M2.1",
        },
      },
    ],
  },
}
```

### 并发控制

控制可以同时运行的子代理数量：

```json5
{
  agents: {
    defaults: {
      subagents: {
        maxConcurrent: 4, // default: 8
      },
    },
  },
}
```

子代理使用一个专用的队列车道 (`subagent`)，与主代理队列分开，因此子代理运行不会阻塞传入的回复。

### 自动归档

子代理会话在可配置的时间段后自动归档：

```json5
{
  agents: {
    defaults: {
      subagents: {
        archiveAfterMinutes: 120, // default: 60
      },
    },
  },
}
```

<Note>
Archive renames the transcript to __CODE_BLOCK_3__ (same folder) — transcripts are preserved, not deleted. Auto-archive timers are best-effort; pending timers are lost if the gateway restarts.
</Note>

## `sessions_spawn` 工具

这是代理调用以创建子代理的工具。

### 参数

| 参数           | 类型                   | 默认            | 描述                                                    |
| ------------------- | ---------------------- | ------------------ | -------------------------------------------------------------- |
| `task`              | string                 | _(required)_       | 子代理应该做什么                                   |
| `label`             | string                 | —                  | 短标签用于标识                                 |
| `agentId`           | string                 | _(caller's agent)_ | 在不同的代理ID下生成（必须被允许）             |
| `model`             | string                 | _(optional)_       | 覆盖此子代理的模型                          |
| `thinking`          | string                 | _(optional)_       | 覆盖思考级别 (`off`, `low`, `medium`, `high` 等) |
| `runTimeoutSeconds` | number                 | `0` (无限制)     | N秒后中止子代理                            |
| `cleanup`           | `"delete"` \| `"keep"` | `"keep"`           | `"delete"` 在宣布后立即归档                 |

### 模型解析顺序

子代理模型按以下顺序解析（第一个匹配项获胜）：

1. `sessions_spawn` 调用中的显式 `model` 参数
2. 每个代理的配置: `agents.list[].subagents.model`
3. 全局默认: `agents.defaults.subagents.model`
4. 目标代理对该新会话的正常模型解析

思考级别按以下顺序解析：

1. `sessions_spawn` 调用中的显式 `thinking` 参数
2. 每个代理的配置: `agents.list[].subagents.thinking`
3. 全局默认: `agents.defaults.subagents.thinking`
4. 否则不应用特定于子代理的思考覆盖

<Note>
Invalid model values are silently skipped — the sub-agent runs on the next valid default with a warning in the tool result.
</Note>

### 跨代理生成

默认情况下，子代理只能在其自己的代理ID下生成。要允许代理在其他代理ID下生成子代理：

```json5
{
  agents: {
    list: [
      {
        id: "orchestrator",
        subagents: {
          allowAgents: ["researcher", "coder"], // or ["*"] to allow any
        },
      },
    ],
  },
}
```

<Tip>
Use the __CODE_BLOCK_1__ tool to discover which agent ids are currently allowed for __CODE_BLOCK_2__.
</Tip>

## 管理子代理 (`/subagents`)

使用 `/subagents` 滑块命令来检查和控制当前会话中的子代理运行：

| 命令                                  | 描述                                    |
| ---------------------------------------- | ---------------------------------------------- |
| `/subagents list`                        | 列出所有子代理运行（活动和已完成） |
| `/subagents stop <id\|#\|all>`           | 停止正在运行的子代理                       |
| `/subagents log <id\|#> [limit] [tools]` | 查看子代理对话记录                      |
| `/subagents info <id\|#>`                | 显示详细的运行元数据                     |
| `/subagents send <id\|#> <message>`      | 向正在运行的子代理发送消息          |

您可以按列表索引 (`1`, `2`)、运行ID前缀、完整会话密钥或 `last` 引用子代理。

<AccordionGroup>
  <Accordion title="Example: list and stop a sub-agent">
    __CODE_BLOCK_13__

    __CODE_BLOCK_14__

    __CODE_BLOCK_15__

    __CODE_BLOCK_16__

  </Accordion>
  <Accordion title="Example: inspect a sub-agent">
    __CODE_BLOCK_17__

    __CODE_BLOCK_18__

  </Accordion>
  <Accordion title="Example: view sub-agent log">
    __CODE_BLOCK_19__

    Shows the last 10 messages from the sub-agent's transcript. Add __CODE_BLOCK_20__ to include tool call messages:

    __CODE_BLOCK_21__

  </Accordion>
  <Accordion title="Example: send a follow-up message">
    __CODE_BLOCK_22__

    Sends a message into the running sub-agent's session and waits up to 30 seconds for a reply.

  </Accordion>
</AccordionGroup>

## 公告（结果如何返回）

当子代理完成时，它会经过一个**公告**步骤：

1. 捕获子代理的最终回复
2. 将包含结果、状态和统计信息的摘要消息发送到主代理的会话
3. 主代理在聊天中发布自然语言摘要

宣布回复在可用时保留线程/主题路由（Slack 线程、Telegram 主题、Matrix 线程）。

### 宣布统计信息

每个宣布包括一行统计信息，包含：

- 运行时持续时间
- 令牌使用情况（输入/输出/总计）
- 估计成本（当模型定价通过 `models.providers.*.models[].cost` 配置时）
- 会话密钥、会话 ID 和 transcripts 路径

### 宣布状态

宣布消息包括从运行时结果派生的状态（不是从模型输出派生的）：

- **successful completion** (`ok`) — 任务正常完成
- **error** — 任务失败（错误详情在备注中）
- **timeout** — 任务超出 `runTimeoutSeconds`
- **unknown** — 状态无法确定

<Tip>
If no user-facing announcement is needed, the main-agent summarize step can return __CODE_BLOCK_3__ and nothing is posted.
This is different from __CODE_BLOCK_4__, which is used in agent-to-agent announce flow (__CODE_BLOCK_5__).
</Tip>

## 工具策略

默认情况下，子代理获取 **除** 一组不安全或对后台任务不必要的被拒绝工具之外的所有工具：

<AccordionGroup>
  <Accordion title="Default denied tools">
    | Denied tool | Reason |
    |-------------|--------|
    | __CODE_BLOCK_6__ | Session management — main agent orchestrates |
    | __CODE_BLOCK_7__ | Session management — main agent orchestrates |
    | __CODE_BLOCK_8__ | Session management — main agent orchestrates |
    | __CODE_BLOCK_9__ | No nested fan-out (sub-agents cannot spawn sub-agents) |
    | __CODE_BLOCK_10__ | System admin — dangerous from sub-agent |
    | __CODE_BLOCK_11__ | System admin |
    | __CODE_BLOCK_12__ | Interactive setup — not a task |
    | __CODE_BLOCK_13__ | Status/scheduling — main agent coordinates |
    | __CODE_BLOCK_14__ | Status/scheduling — main agent coordinates |
    | __CODE_BLOCK_15__ | Pass relevant info in spawn prompt instead |
    | __CODE_BLOCK_16__ | Pass relevant info in spawn prompt instead |
  </Accordion>
</AccordionGroup>

### 自定义子代理工具

您可以进一步限制子代理工具：

```json5
{
  tools: {
    subagents: {
      tools: {
        // deny always wins over allow
        deny: ["browser", "firecrawl"],
      },
    },
  },
}
```

要将子代理限制为 **仅** 特定工具：

```json5
{
  tools: {
    subagents: {
      tools: {
        allow: ["read", "exec", "process", "write", "edit", "apply_patch"],
        // deny still wins if set
      },
    },
  },
}
```

<Note>
Custom deny entries are **added to** the default deny list. If __CODE_BLOCK_19__ is set, only those tools are available (the default deny list still applies on top).
</Note>

## 认证

子代理认证通过 **代理 ID** 解析，而不是通过会话类型：

- 认证存储从目标代理的 `agentDir` 加载
- 主代理的认证配置文件作为 **后备** 合并（代理配置文件在冲突时优先）
- 合并是累加的 — 主配置文件始终可用作为后备

<Note>
Fully isolated auth per sub-agent is not currently supported.
</Note>

## 上下文和系统提示

子代理接收的系统提示比主代理要少：

- **包含:** 工具、工作区、运行时部分，以及 `AGENTS.md` 和 `TOOLS.md`
- **不包含:** `SOUL.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`

子代理还会收到一个任务导向的系统提示，指示它专注于分配的任务，完成它，并且不要充当主代理。

## 停止子代理

| 方法                 | 效果                                                                    |
| ---------------------- | ------------------------------------------------------------------------- |
| 聊天中的 `/stop`    | 中止主会话 **和** 从其生成的所有活动子代理运行 |
| `/subagents stop <id>` | 停止特定的子代理而不影响主会话             |
| `runTimeoutSeconds`    | 在指定时间后自动中止子代理运行           |

<Note>
__CODE_BLOCK_10__ does **not** auto-archive the session. The session remains until the normal archive timer fires.
</Note>

## 完整配置示例

<Accordion title="完整的子代理配置">
```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-sonnet-4" },
      subagents: {
        model: "minimax/MiniMax-M2.1",
        thinking: "low",
        maxConcurrent: 4,
        archiveAfterMinutes: 30,
      },
    },
    list: [
      {
        id: "main",
        default: true,
        name: "Personal Assistant",
      },
      {
        id: "ops",
        name: "Ops Agent",
        subagents: {
          model: "anthropic/claude-sonnet-4",
          allowAgents: ["main"], // ops can spawn sub-agents under "main"
        },
      },
    ],
  },
  tools: {
    subagents: {
      tools: {
        deny: ["browser"], // sub-agents can't use the browser
      },
    },
  },
}
```
</Accordion>

## 限制

<Warning>
- **Best-effort announce:** If the gateway restarts, pending announce work is lost.
- **No nested spawning:** Sub-agents cannot spawn their own sub-agents.
- **Shared resources:** Sub-agents share the gateway process; use __CODE_BLOCK_12__ as a safety valve.
- **Auto-archive is best-effort:** Pending archive timers are lost on gateway restart.
</Warning>

## 参见

- [会话工具](/concepts/session-tool) — 关于 `sessions_spawn` 和其他会话工具的详细信息
- [多代理沙盒和工具](/tools/multi-agent-sandbox-tools) — 每个代理的工具限制和沙箱化
- [配置](/gateway/configuration) — `agents.defaults.subagents` 参考
- [队列](/concepts/queue) — `subagent` 队列的工作原理