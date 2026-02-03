---
summary: "Sub-agents: spawning isolated agent runs that announce results back to the requester chat"
read_when:
  - You want background/parallel work via the agent
  - You are changing sessions_spawn or sub-agent tool policy
title: "Sub-Agents"
---
# 子代理

子代理是现有代理运行生成的后台代理运行。它们在自己的会话中运行（`agent:<agentId>:subagent:<uuid>`），完成后会将结果**公告**回请求者的聊天频道。

## 斜杠命令

使用 `/subagents` 来检查或控制**当前会话**的子代理运行：

- `/subagents list`
- `/subagents stop <id|#|all>`
- `/subagents log <id|#> [limit] [tools]`
- `/subagents info <id|#>`
- `/subagents send <id|#> <message>`

`/subagents info` 显示运行元数据（状态、时间戳、会话 ID、对话记录路径、清理）。

主要目标：

- 并行执行“研究/长时间任务/慢工具”工作，而不会阻塞主运行。
- 默认保持子代理隔离（会话分离 + 可选沙箱）。
- 保持工具表面难以滥用：子代理默认**不**获得会话工具。
- 避免嵌套扇出：子代理不能生成子代理。

成本说明：每个子代理都有其**独立**的上下文和令牌使用。对于繁重或重复任务，为子代理设置更便宜的模型，并保持主代理使用高质量模型。您可以通过 `agents.defaults.subagents.model` 或每个代理的覆盖配置来设置此选项。

## 工具

使用 `sessions_spawn`：

- 启动子代理运行（`deliver: false`，全局车道：`subagent`）
- 然后运行公告步骤，并将公告回复发布到请求者的聊天频道
- 默认模型：继承调用者，除非您设置 `agents.defaults.subagents.model`（或每个代理的 `agents.list[].subagents.model`）；显式的 `sessions_spawn.model` 仍会覆盖。

工具参数：

- `task`（必填）
- `label?`（可选）
- `agentId?`（可选；如果允许，可在另一个代理 ID 下生成）
- `model?`（可选；覆盖子代理模型；无效值会被跳过，并在工具结果中发出警告，子代理使用默认模型运行）
- `thinking?`（可选；覆盖子代理运行的思考级别）
- `runTimeoutSeconds?`（默认 `0`；设置后，子代理运行会在 N 秒后中止）
- `cleanup?`（`delete|keep`，默认 `keep`）

允许列表：

- `agents.list[].subagents.allowAgents`：可以使用 `agentId` 目标代理的 ID 列表（`["*"]` 允许任何）。默认：仅请求者代理。

发现：

- 使用 `agents_list` 查看哪些代理 ID 当前允许用于 `sessions_spawn`。

自动归档：

- 子代理会话在 `agents.defaults.subagents.archiveAfterMinutes`（默认：60）分钟后自动归档。
- 归档使用 `sessions.delete` 并将对话记录重命名为 `*.deleted.<timestamp>`（同一文件夹）。
- `cleanup: "delete"` 在公告后立即归档（仍通过重命名保留对话记录）。
- 自动归档是尽力而为；如果网关重启，待处理的定时器会丢失。
- `runTimeoutSeconds` **不会**自动归档；它仅停止运行。会话会持续到自动归档为止。

## 认证

子代理认证通过**代理 ID**解决，而不是会话类型：

- 子代理会话密钥是 `agent:<agentId>:subagent:<uuid>`。
- 认证存储从该代理的 `agentDir` 加载。
- 主代理的认证配置文件作为**回退**合并；代理配置文件在冲突时覆盖主配置文件。

注意：合并是累加的，因此主配置文件始终可用作为回退。目前还不支持每个代理的完全隔离认证。

## 公告

子代理通过公告步骤报告结果：

- 公告步骤在子代理会话中运行（不是请求者会话）。
- 如果子代理回复正好是 `ANNOUNCE_SKIP`，则不会发布任何内容。
- 否则，公告回复通过后续的 `agent` 调用发布到请求者聊天频道（`deliver=true`）。
- 公告回复在可用时保留线程/主题路由（Slack 线程、Telegram 主题、Matrix 线程）。
- 公告消息会规范化为稳定的模板：
  - `状态:` 从运行结果推导（`success`、`error`、`timeout` 或 `unknown`）。
  - `结果:` 从公告步骤获取的摘要内容（如果缺失则为 `(not available)`）。
  - `备注:` 错误详情和其他有用上下文。
- `状态` 不是从模型输出推断而来；它来自运行时结果信号。

公告负载在最后包含一行统计信息（即使被包裹）：

- 运行时间（例如 `runtime 5m12s`）
- 令牌使用（输入/输出/总计）
- 当模型定价配置时的预估成本（`models.providers.*.models[].cost`）
- `sessionKey`、`sessionId` 和对话记录路径（以便主代理通过 `sessions_history` 获取历史记录或检查磁盘上的文件）

## 工具策略（子代理工具）

默认情况下，子代理获得**所有工具，除了会话工具**：

- `sessions_list`
- `sessions_history`
- `sessions_send`
- `sessions_spawn`

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
        // 拒绝优先
        deny: ["gateway", "cron"],
        // 如果设置了 allow，则变为只允许（拒绝仍优先）
        // allow: ["read", "exec", "process"]
      },
    },
  },
}
```

## 并发

子代理使用专用的进程内队列车道：

- 车道名称：`subagent`
- 并发数：`agents.defaults.subagents.maxConcurrent`（默认 `8`）

## 停止

- 在请求者聊天中发送 `/stop` 会中止请求者会话并停止从其生成的任何活动子代理运行。

## 限制

- 子代理公告是**尽力而为**。如果网关重启，待处理的“公告返回”工作会丢失。
- 子代理仍共享相同的网关进程资源；将 `maxConcurrent` 视为安全阀。
- `sessions_spawn` 始终是非阻塞的：它立即返回 `{ status: "accepted", runId, childSessionKey }`。
- 子代理上下文仅注入 `AGENTS.md` + `TOOLS.md`（不包括 `SOUL.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md` 或 `BOOTSTRAP.md`）。