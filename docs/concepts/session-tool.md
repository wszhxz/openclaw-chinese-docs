---
summary: "Agent session tools for listing sessions, fetching history, and sending cross-session messages"
read_when:
  - Adding or modifying session tools
title: "Session Tools"
---
# 会话工具

目标：提供一套小巧且不易误用的工具集，使智能体能够列出会话、获取历史记录并向另一个会话发送消息。

## 工具名称

- `sessions_list`
- `sessions_history`
- `sessions_send`
- `sessions_spawn`

## 键模型

- 主直接聊天桶始终为字面量键 `"main"`（解析为当前智能体的主键）。
- 群聊使用 `agent:<agentId>:<channel>:group:<id>` 或 `agent:<agentId>:<channel>:channel:<id>`（传递完整键）。
- 定时任务使用 `cron:<job.id>`。
- 钩子使用 `hook:<uuid>`，除非显式设置。
- 节点会话使用 `node-<nodeId>`，除非显式设置。

`global` 和 `unknown` 是保留值，永远不会被列出。如果 `session.scope = "global"`，我们将它别名为 `main` 供所有工具使用，这样调用者就永远不会看到 `global`。

## sessions_list

将会话列为行数组。

参数：

- `kinds?: string[]` 过滤器：`"main" | "group" | "cron" | "hook" | "node" | "other"` 中的任意一项
- `limit?: number` 最大行数（默认：服务器默认值，限制例如 200）
- `activeMinutes?: number` 仅更新于 N 分钟内的会话
- `messageLimit?: number` 0 = 无消息（默认 0）；>0 = 包含最后 N 条消息

行为：

- `messageLimit > 0` 获取每个会话的 `chat.history` 并包含最后 N 条消息。
- 工具结果在列表输出中被过滤掉；使用 `sessions_history` 处理工具消息。
- 当在沙箱化智能体会话中运行时，会话工具默认为仅限生成会话的可见性（见下文）。

行结构（JSON）：

- `key`：会话键（字符串）
- `kind`：`main | group | cron | hook | node | other`
- `channel`：`whatsapp | telegram | discord | signal | imessage | webchat | internal | unknown`
- `displayName`（如有则显示组标签）
- `updatedAt`（毫秒）
- `sessionId`
- `model`，`contextTokens`，`totalTokens`
- `thinkingLevel`，`verboseLevel`，`systemSent`，`abortedLastRun`
- `sendPolicy`（如设置则为会话覆盖）
- `lastChannel`，`lastTo`
- `deliveryContext`（如有则为标准化的 `{ channel, to, accountId }`）
- `transcriptPath`（尽力而为的路径，源自 store dir + sessionId）
- `messages?`（仅在 `messageLimit > 0` 时）

## sessions_history

获取单个会话的对话记录。

参数：

- `sessionKey`（必需；接受会话键或来自 `sessions_list` 的 `sessionId`）
- `limit?: number` 最大消息数（服务器会限制）
- `includeTools?: boolean`（默认 false）

行为：

- `includeTools=false` 过滤 `role: "toolResult"` 消息。
- 以原始对话记录格式返回消息数组。
- 给定 `sessionId` 时，OpenClaw 将其解析为相应的会话键（缺失 id 报错）。

## sessions_send

向另一个会话发送消息。

参数：

- `sessionKey`（必需；接受会话键或来自 `sessions_list` 的 `sessionId`）
- `message`（必需）
- `timeoutSeconds?: number`（默认 >0；0 = 发后即忘）

行为：

- `timeoutSeconds = 0`：入队并返回 `{ runId, status: "accepted" }`。
- `timeoutSeconds > 0`：最多等待 N 秒完成，然后返回 `{ runId, status: "ok", reply }`。
- 如果等待超时：`{ runId, status: "timeout", error }`。运行继续；稍后调用 `sessions_history`。
- 如果运行失败：`{ runId, status: "error", error }`。
- 在主运行完成后宣布传递运行，且为尽力而为；`status: "ok"` 不能保证宣布已送达。
- 通过网关 `agent.wait`（服务端）等待，因此重连不会中断等待。
- 智能体对智能体的消息上下文会被注入到主运行中。
- 会话间消息使用 `message.provenance.kind = "inter_session"` 持久化，以便对话记录阅读器可以区分路由的智能体指令与外部用户输入。
- 主运行完成后，OpenClaw 运行 **回复回环**：
  - 第 2 轮及之后在请求者和目标智能体之间交替。
  - 精确回复 `REPLY_SKIP` 以停止乒乓。
  - 最大回合数为 `session.agentToAgent.maxPingPongTurns`（0–5，默认 5）。
- 循环结束后，OpenClaw 运行 **智能体对智能体公告步骤**（仅目标智能体）：
  - 精确回复 `ANNOUNCE_SKIP` 以保持沉默。
  - 任何其他回复都会发送到目标频道。
  - 公告步骤包括原始请求 + 第 1 轮回复 + 最新乒乓回复。

## 频道字段

- 对于群聊，`channel` 是会话条目上记录的频道。
- 对于直接聊天，`channel` 从 `lastChannel` 映射。
- 对于 cron/钩子/节点，`channel` 为 `internal`。
- 如果缺失，`channel` 为 `unknown`。

## 安全 / 发送策略

基于频道/聊天类型（而非每个会话 id）的策略阻止。

```json
{
  "session": {
    "sendPolicy": {
      "rules": [
        {
          "match": { "channel": "discord", "chatType": "group" },
          "action": "deny"
        }
      ],
      "default": "allow"
    }
  }
}
```

运行时覆盖（按会话条目）：

- `sendPolicy: "allow" | "deny"`（未设置 = 继承配置）
- 可通过 `sessions.patch` 或仅所有者设置的 `/send on|off|inherit`（独立消息）设置。

执行点：

- `chat.send` / `agent`（网关）
- 自动回复交付逻辑

## sessions_spawn

在隔离会话中启动子智能体运行，并将结果公告回请求者聊天频道。

参数：

- `task`（必需）
- `label?`（可选；用于日志/UI）
- `agentId?`（可选；如果允许则在另一个智能体 id 下生成）
- `model?`（可选；覆盖子智能体模型；无效值报错）
- `thinking?`（可选；覆盖子智能体运行的思考级别）
- `runTimeoutSeconds?`（设置时默认为 `agents.defaults.subagents.runTimeoutSeconds`，否则为 `0`；设置后，N 秒后中止子智能体运行）
- `thread?`（默认 false；当频道/插件支持时，请求此生成的线程绑定路由）
- `mode?`（`run|session`；默认为 `run`，但当 `thread=true` 时默认为 `session`；`mode="session"` 需要 `thread=true`）
- `cleanup?`（`delete|keep`，默认 `keep`）
- `sandbox?`（`inherit|require`，默认 `inherit`；`require` 除非目标子运行时处于沙箱化状态则拒绝生成）
- `attachments?`（可选的行内文件数组；仅子智能体运行时，ACP 拒绝）。每个条目：`{ name, content, encoding?: "utf8" | "base64", mimeType? }`。文件将在 `.openclaw/attachments/<uuid>/` 处实例化到子工作区。返回带 sha256 的回执。
- `attachAs?`（可选；`{ mountPath? }` 提示符保留用于未来的挂载实现）

白名单：

- `agents.list[].subagents.allowAgents`：通过 `agentId` 允许的代理 ID 列表（`["*"]` 允许任意）。默认：仅请求者智能体。
- 沙箱继承保护：如果请求者会话处于沙箱化状态，`sessions_spawn` 拒绝那些将运行在非沙箱环境中的目标。

发现：

- 使用 `agents_list` 来发现哪些代理 ID 被允许用于 `sessions_spawn`。

行为：

- 启动一个新的 `agent:<agentId>:subagent:<uuid>` 会话，带有 `deliver: false`。
- 子智能体默认拥有完整工具集 **减去会话工具**（可通过 `tools.subagents.tools` 配置）。
- 子智能体不允许调用 `sessions_spawn`（禁止子智能体 → 子智能体生成）。
- 始终为非阻塞：立即返回 `{ status: "accepted", runId, childSessionKey }`。
- 通过 `thread=true`，频道插件可以将交付/路由绑定到线程目标（Discord 支持由 `session.threadBindings.*` 和 `channels.discord.threadBindings.*` 控制）。
- 完成后，OpenClaw 运行子智能体 **公告步骤** 并将结果发布到请求者聊天频道。
  - 如果助手最终回复为空，则包含来自子智能体历史的最新 `toolResult` 作为 `Result`。
- 在公告步骤期间回复确切的 `ANNOUNCE_SKIP` 以保持沉默。
- 公告回复标准化为 `Status`/`Result`/`Notes`；`Status` 来自运行时结果（而非模型文本）。
- 子智能体会话在 `agents.defaults.subagents.archiveAfterMinutes` 后自动归档（默认：60）。
- 公告回复包含一行统计信息（运行时、令牌、sessionKey/sessionId、对话记录路径以及可选成本）。

## 沙箱会话可见性

会话工具可以缩小范围以减少跨会话访问。

默认行为：

- `tools.sessions.visibility` 默认为 `tree`（当前会话 + 生成的子智能体会话）。
- 对于沙箱化会话，`agents.defaults.sandbox.sessionToolsVisibility` 可以硬性限制可见性。

配置：

```json5
{
  tools: {
    sessions: {
      // "self" | "tree" | "agent" | "all"
      // default: "tree"
      visibility: "tree",
    },
  },
  agents: {
    defaults: {
      sandbox: {
        // default: "spawned"
        sessionToolsVisibility: "spawned", // or "all"
      },
    },
  },
}
```

注意：

- `self`：仅当前会话键。
- `tree`：当前会话 + 由当前会话生成的会话。
- `agent`：属于当前智能体 ID 的任何会话。
- `all`：任何会话（跨智能体访问仍需 `tools.agentToAgent`）。
- 当会话处于沙箱化状态且 `sessionToolsVisibility="spawned"` 时，即使您设置了 `tools.sessions.visibility="all"`，OpenClaw 也会将可见性限制为 `tree`。