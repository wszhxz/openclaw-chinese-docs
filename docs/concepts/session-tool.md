---
summary: "Agent session tools for listing sessions, fetching history, and sending cross-session messages"
read_when:
  - Adding or modifying session tools
title: "Session Tools"
---
# 会话工具

目标：提供一组小型且难以误用的工具集，使代理能够列出会话、获取历史记录并发送到另一个会话。

## 工具名称

- `sessions_list`
- `sessions_history`
- `sessions_send`
- `sessions_spawn`

## 关键模型

- 主直接聊天桶始终是字面键 `"main"`（解析为当前代理的主要键）。
- 群组聊天使用 `agent:<agentId>:<channel>:group:<id>` 或 `agent:<agentId>:<channel>:channel:<id>`（传递完整键）。
- 定时任务使用 `cron:<job.id>`。
- 钩子使用 `hook:<uuid>` 除非显式设置。
- 节点会话使用 `node-<nodeId>` 除非显式设置。

`global` 和 `unknown` 是保留值，从不列出。如果 `session.scope = "global"`，我们将其别名为 `main` 以便所有工具使用，因此调用者从看不到 `global`。

## sessions_list

以行数组的形式列出会话。

参数：

- `kinds?: string[]` 过滤器：任何 `"main" | "group" | "cron" | "hook" | "node" | "other"`
- `limit?: number` 最大行数（默认：服务器默认，限制例如 200）
- `activeMinutes?: number` 仅列出在 N 分钟内更新的会话
- `messageLimit?: number` 0 = 不包含消息（默认 0）；>0 = 包含最后 N 条消息

行为：

- `messageLimit > 0` 每个会话获取 `chat.history` 并包含最后 N 条消息。
- 工具结果在列表输出中被过滤掉；使用 `sessions_history` 获取工具消息。
- 当在 **沙盒化** 代理会话中运行时，默认为 **仅显示生成的会话**（见下文）。

行形状（JSON）：

- `key`：会话键（字符串）
- `kind`：`main | group | cron | hook | node | other`
- `channel`：`whatsapp | telegram | discord | signal | imessage | webchat | internal | unknown`
- `displayName`（如果有群组显示标签）
- `updatedAt`（毫秒）
- `sessionId`
- `model`，`contextTokens`，`totalTokens`
- `thinkingLevel`，`verboseLevel`，`systemSent`，`abortedLastRun`
- `sendPolicy`（如果有会话覆盖设置）
- `lastChannel`，`lastTo`
- `deliveryContext`（如果有可用的标准化 `{ channel, to, accountId }`）
- `transcriptPath`（从存储目录 + sessionId 推导的最佳路径）
- `messages?`（仅当 `messageLimit > 0`）

## sessions_history

获取单个会话的对话记录。

参数：

- `sessionKey`（必需；接受会话键或 `sessionId` 从 `sessions_list`）
- `limit?: number` 最大消息数（服务器限制）
- `includeTools?: boolean`（默认 false）

行为：

- `includeTools=false` 过滤 `role: "toolResult"` 消息。
- 返回原始对话记录格式的消息数组。
- 当给定 `sessionId` 时，OpenClaw 解析为相应的会话键（缺失 id 错误）。

## sessions_send

向另一个会话发送消息。

参数：

- `sessionKey`（必需；接受会话键或 `sessionId` 从 `sessions_list`）
- `message`（必需）
- `timeoutSeconds?: number`（默认 >0；0 = 发送即忘记）

行为：

- `timeoutSeconds = 0`：排队并返回 `{ runId, status: "accepted" }`。
- `timeoutSeconds > 0`：等待最多 N 秒完成，然后返回 `{ runId, status: "ok", reply }`。
- 如果等待超时：`{ runId, status: "timeout", error }`。继续运行；稍后调用 `sessions_history`。
- 如果运行失败：`{ runId, status: "error", error }`。
- 宣布交付在主运行完成后进行，为尽力而为；`status: "ok"` 不保证宣布已送达。
- 通过网关 `agent.wait`（服务器端）等待，以便重新连接不会丢失等待。
- 为主运行注入代理到代理消息上下文。
- 主运行完成后，OpenClaw 运行一个 **回复循环**：
  - 第 2 轮及以后在请求者和目标代理之间交替。
  - 精确回复 `REPLY_SKIP` 停止乒乓。
  - 最大轮次为 `session.agentToAgent.maxPingPongTurns`（0–5，默认 5）。
- 循环结束后，OpenClaw 运行 **代理到代理宣布步骤**（仅目标代理）：
  - 精确回复 `ANNOUNCE_SKIP` 保持沉默。
  - 任何其他回复都会发送到目标频道。
  - 宣布步骤包括原始请求 + 第一轮回复 + 最新乒乓回复。

## 通道字段

- 对于群组，`channel` 是会话条目上记录的通道。
- 对于直接聊天，`channel` 映射自 `lastChannel`。
- 对于 cron/钩子/节点，`channel` 是 `internal`。
- 如果缺失，`channel` 是 `unknown`。

## 安全性 / 发送策略

基于通道/聊天类型的策略阻止（不是按会话 ID）。

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
- 可通过 `sessions.patch` 或仅所有者 `/send on|off|inherit`（独立消息）设置。

执行点：

- `chat.send` / `agent`（网关）
- 自动回复交付逻辑

## sessions_spawn

在一个隔离的会话中生成一个子代理运行，并将结果宣布回请求者的聊天频道。

参数：

- `task`（必需）
- `label?`（可选；用于日志/UI）
- `agentId?`（可选；如果允许则在另一个代理 ID 下生成）
- `model?`（可选；覆盖子代理模型；无效值错误）
- `runTimeoutSeconds?`（默认 0；设置后，在 N 秒后中止子代理运行）
- `cleanup?` (`delete|keep`，默认 `keep`)

白名单：

- `agents.list[].subagents.allowAgents`：通过 `agentId` 允许的代理 ID 列表 (`["*"]` 允许任何）。默认：只有请求者代理。

发现：

- 使用 `agents_list` 发现哪些代理 ID 允许 `sessions_spawn`。

行为：

- 使用 `deliver: false` 启动一个新的 `agent:<agentId>:subagent:<uuid>` 会话。
- 子代理默认具有完整的工具集 **减去会话工具**（可通过 `tools.subagents.tools` 配置）。
- 子代理不允许调用 `sessions_spawn`（不允许子代理生成子代理）。
- 始终非阻塞：立即返回 `{ status: "accepted", runId, childSessionKey }`。
- 完成后，OpenClaw 运行子代理 **宣布步骤** 并将结果发布到请求者的聊天频道。
- 在宣布步骤期间精确回复 `ANNOUNCE_SKIP` 保持沉默。
- 宣布回复标准化为 `Status`/`Result`/`Notes`；`Status` 来自运行时结果（不是模型文本）。
- 子代理会话在 `agents.defaults.subagents.archiveAfterMinutes` 后自动归档（默认：60）。
- 宣布回复包括一行统计信息（运行时间、令牌、sessionKey/sessionId、对话记录路径和可选成本）。

## 沙盒会话可见性

沙盒会话可以使用会话工具，但默认情况下它们只能看到通过 `sessions_spawn` 生成的会话。

配置：

```json5
{
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