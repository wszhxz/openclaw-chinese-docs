---
summary: "Agent session tools for listing sessions, fetching history, and sending cross-session messages"
read_when:
  - Adding or modifying session tools
title: "Session Tools"
---
# 会话工具

目标：提供一套小巧、不易误用的工具集，使智能体能够列出会话、获取历史记录，并向另一会话发送消息。

## 工具名称

- `sessions_list`
- `sessions_history`
- `sessions_send`
- `sessions_spawn`

## 关键模型

- 主直连聊天桶（main direct chat bucket）始终为字面量键 `"main"`（解析为当前智能体的主键）。
- 群组聊天使用 `agent:<agentId>:<channel>:group:<id>` 或 `agent:<agentId>:<channel>:channel:<id>`（需传入完整键）。
- 定时任务（cron jobs）使用 `cron:<job.id>`。
- 钩子（hooks）默认使用 `hook:<uuid>`，除非显式设置。
- 节点会话（node sessions）默认使用 `node-<nodeId>`，除非显式设置。

`global` 和 `unknown` 是保留值，永远不会出现在列表中。若出现 `session.scope = "global"`，我们将其统一别名为 `main`，以确保所有工具调用方均不会看到 `global`。

## sessions_list

以行数组形式列出会话。

参数：

- `kinds?: string[]` 过滤器：可取值为 `"main" | "group" | "cron" | "hook" | "node" | "other"` 中任意一项
- `limit?: number` 最大行数（默认：服务端默认值，例如限制为 200）
- `activeMinutes?: number` 仅列出最近 N 分钟内更新过的会话
- `messageLimit?: number` 0 = 不包含消息（默认为 0）；>0 = 包含最近 N 条消息

行为：

- `messageLimit > 0` 为每个会话获取 `chat.history`，并包含最近 N 条消息。
- 工具调用结果在列表输出中被过滤掉；如需查看工具消息，请使用 `sessions_history`。
- 当在 **沙箱化（sandboxed）** 的智能体会话中运行时，会话工具默认仅对 **已派生（spawned-only）** 的会话可见（详见下文）。

行结构（JSON）：

- `key`：会话键（字符串）
- `kind`：`main | group | cron | hook | node | other`
- `channel`：`whatsapp | telegram | discord | signal | imessage | webchat | internal | unknown`
- `displayName`（如有，为群组显示标签）
- `updatedAt`（毫秒）
- `sessionId`
- `model`、`contextTokens`、`totalTokens`
- `thinkingLevel`、`verboseLevel`、`systemSent`、`abortedLastRun`
- `sendPolicy`（若已设置，则为会话覆盖值）
- `lastChannel`、`lastTo`
- `deliveryContext`（在可用时为标准化的 `{ channel, to, accountId }`）
- `transcriptPath`（尽最大努力从存储目录 + sessionId 推导出的路径）
- `messages?`（仅当 `messageLimit > 0` 时存在）

## sessions_history

获取单个会话的对话记录（transcript）。

参数：

- `sessionKey`（必填；接受会话键或来自 `sessions_list` 的 `sessionId`）
- `limit?: number` 最大消息数（服务端会做限制）
- `includeTools?: boolean`（默认 false）

行为：

- `includeTools=false` 过滤掉 `role: "toolResult"` 类型的消息。
- 返回原始对话记录格式的消息数组。
- 若传入 `sessionId`，OpenClaw 将其解析为对应会话键（缺失 ID 时将报错）。

## sessions_send

向另一会话发送一条消息。

参数：

- `sessionKey`（必填；接受会话键或来自 `sessions_list` 的 `sessionId`）
- `message`（必填）
- `timeoutSeconds?: number`（默认 >0；0 = 发送即忘）

行为：

- `timeoutSeconds = 0`：入队后立即返回 `{ runId, status: "accepted" }`。
- `timeoutSeconds > 0`：最多等待 N 秒直至完成，然后返回 `{ runId, status: "ok", reply }`。
- 若等待超时：`{ runId, status: "timeout", error }`。主流程继续执行；稍后可调用 `sessions_history`。
- 若运行失败：`{ runId, status: "error", error }`。
- 投递通知（announce delivery）在主流程完成后异步执行，属尽力而为（best-effort）；`status: "ok"` 并不保证该通知一定送达。
- 等待过程通过网关 `agent.wait`（服务端实现）进行，因此重连不会中断等待。
- 智能体到智能体的消息上下文会在主流程中注入。
- 跨会话消息以 `message.provenance.kind = "inter_session"` 方式持久化，以便对话记录阅读器可区分路由的智能体指令与外部用户输入。
- 主流程完成后，OpenClaw 启动一个 **回复循环（reply-back loop）**：
  - 第二轮及后续轮次在请求方与目标智能体之间交替进行。
  - 精确回复 `REPLY_SKIP` 可终止该乒乓式交互。
  - 最大轮次为 `session.agentToAgent.maxPingPongTurns`（取值范围 0–5，默认为 5）。
- 循环结束后，OpenClaw 执行 **智能体到智能体的通知步骤（agent‑to‑agent announce step）**（仅限目标智能体）：
  - 精确回复 `ANNOUNCE_SKIP` 可保持静默。
  - 其他任何回复均会被发送至目标频道。
  - 此通知步骤包含原始请求 + 第一轮回复 + 最新一次乒乓回复。

## 频道字段（Channel Field）

- 对于群组：`channel` 是会话条目中记录的频道。
- 对于直连聊天：`channel` 由 `lastChannel` 映射而来。
- 对于定时任务/钩子/节点：`channel` 为 `internal`。
- 若缺失：`channel` 为 `unknown`。

## 安全性 / 发送策略（Security / Send Policy）

基于频道/聊天类型（而非按会话 ID）的策略驱动式拦截。

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
- 可通过 `sessions.patch` 或仅所有者可设的 `/send on|off|inherit`（独立消息）进行设置。

执行检查点：

- `chat.send` / `agent`（网关层）
- 自动回复投递逻辑

## sessions_spawn

在隔离会话中启动子智能体运行，并将结果通知回请求方的聊天频道。

参数：

- `task`（必填）
- `label?`（可选；用于日志/UI 显示）
- `agentId?`（可选；若允许，可在另一智能体 ID 下启动）
- `model?`（可选；覆盖子智能体所用模型；无效值将报错）
- `thinking?`（可选；覆盖子智能体运行时的思考层级）
- `runTimeoutSeconds?`（设为 `agents.defaults.subagents.runTimeoutSeconds` 时默认启用，否则为 `0`；启用后，N 秒后自动中止子智能体运行）
- `thread?`（默认 false；当频道/插件支持时，请求线程绑定路由）
- `mode?`（`run|session`；默认为 `run`，但当 `thread=true` 时默认为 `session`；`mode="session"` 要求启用 `thread=true`）
- `cleanup?`（`delete|keep`，默认为 `keep`）
- `sandbox?`（`inherit|require`，默认为 `inherit`；`require` 在目标子运行时非沙箱化时拒绝启动）
- `attachments?`（可选的内联文件数组；仅子智能体运行时有效，AC P 拒绝）；每项为 `{ name, content, encoding?: "utf8" | "base64", mimeType? }`；文件将在 `.openclaw/attachments/<uuid>/` 处挂载至子工作区；返回含各文件 sha256 的收据。
- `attachAs?`（可选；`{ mountPath? }` 提示为未来挂载实现预留）

白名单（Allowlist）：

- `agents.list[].subagents.allowAgents`：允许通过 `agentId` 启动的智能体 ID 列表（`["*"]` 表示允许任意）；默认：仅请求方智能体。
- 沙箱继承防护：若请求方会话为沙箱化，则 `sessions_spawn` 将拒绝可能以非沙箱方式运行的目标。

发现机制（Discovery）：

- 使用 `agents_list` 发现哪些智能体 ID 允许用于 `sessions_spawn`。

行为：

- 启动一个新 `agent:<agentId>:subagent:<uuid>` 会话，使用 `deliver: false`。
- 子智能体默认拥有完整工具集（**不含会话工具**），可通过 `tools.subagents.tools` 配置。
- 子智能体不允许调用 `sessions_spawn`（禁止子智能体 → 子智能体嵌套启动）。
- 始终为非阻塞式：立即返回 `{ status: "accepted", runId, childSessionKey }`。
- 启用 `thread=true` 后，频道插件可将投递/路由绑定至线程目标（Discord 支持由 `session.threadBindings.*` 和 `channels.discord.threadBindings.*` 控制）。
- 完成后，OpenClaw 执行子智能体 **通知步骤（announce step）**，并将结果发布至请求方聊天频道。
  - 若助手最终回复为空，则从子智能体历史中选取最新的 `toolResult`，作为 `Result` 一并包含。
- 在通知步骤中精确回复 `ANNOUNCE_SKIP` 可保持静默。
- 通知回复被规范化为 `Status`/`Result`/`Notes`；其中 `Status` 来自运行时结果（而非模型生成文本）。
- 子智能体会话在 `agents.defaults.subagents.archiveAfterMinutes` 秒后自动归档（默认：60）。
- 通知回复中包含统计信息行（运行时、token 数、sessionKey/sessionId、对话记录路径，以及可选成本）。

## 沙箱会话可见性（Sandbox Session Visibility）

会话工具可限定作用域，以减少跨会话访问。

默认行为：

- `tools.sessions.visibility` 默认为 `tree`（当前会话 + 当前会话派生的子智能体会话）。
- 对于沙箱化会话，`agents.defaults.sandbox.sessionToolsVisibility` 可严格限制可见范围。

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

说明：

- `self`：仅当前会话键。
- `tree`：当前会话 + 当前会话所派生的所有会话。
- `agent`：属于当前智能体 ID 的任意会话。
- `all`：任意会话（跨智能体访问仍需满足 `tools.agentToAgent`）。
- 当会话为沙箱化且启用了 `sessionToolsVisibility="spawned"` 时，OpenClaw 将强制限制可见范围为 `tree`，即使您设置了 `tools.sessions.visibility="all"`。