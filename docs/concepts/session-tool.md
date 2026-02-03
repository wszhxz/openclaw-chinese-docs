---
summary: "Agent session tools for listing sessions, fetching history, and sending cross-session messages"
read_when:
  - Adding or modifying session tools
title: "Session Tools"
---
# 会话工具

目标：提供一组小型、难以误用的工具，使代理能够列出会话、获取历史记录，并将信息发送到另一个会话。

## 工具名称

- `sessions_list`
- `sessions_history`
- `sessions_send`
- `sessions_spawn`

## 关键模型

- 主要直接聊天桶始终是字面键 `"main"`（解析为当前代理的主要键）。
- 群聊使用 `agent:<agentId>:<channel>:group:<id>` 或 `agent:<agentId>:<channel>:channel:<id>`（传递完整键）。
- 定时任务使用 `cron:<job.id>`。
- 钩子使用 `hook:<uuid>`，除非显式设置。
- 节点会话使用 `node-<nodeId>`，除非显式设置。

`global` 和 `unknown` 是保留值，永远不会列出。如果 `session.scope = "global"`，我们将其别名为 `main`，以便所有工具调用者永远不会看到 `global`。

## sessions_list

以行数组形式列出会话。

参数：

- `kinds?: string[]` 过滤：任意 `"main" | "group" | "cron" | "hook" | "node" | "other"`
- `limit?: number` 最大行数（默认：服务器默认值，例如 200）
- `activeMinutes?: number` 仅列出最近 N 分钟内更新的会话
- `messageLimit?: number` 0 = 不包含消息（默认 0）；>0 = 包含最后 N 条消息

行为：

- `messageLimit > 0` 会为每个会话获取 `chat.history` 并包含最后 N 条消息。
- 工具结果在列表输出中被过滤；使用 `sessions_history` 获取工具消息。
- 在 **沙箱化** 的代理会话中运行时，会话工具默认仅显示 **生成的会话**（见下文）。

行形状（JSON）：

- `key`: 会话键（字符串）
- `kind`: `main | group | cron | hook | node | other`
- `channel`: `whatsapp | telegram | discord | signal | imessage | webchat | internal | unknown`
- `displayName`（如果有群显示标签）
- `updatedAt`（毫秒）
- `sessionId`
- `model`, `contextTokens`, `totalTokens`
- `thinkingLevel`, `verboseLevel`, `systemSent`, `abortedLastRun`
- `sendPolicy`（若设置则为会话覆盖）
- `lastChannel`, `lastTo`
- `deliveryContext`（可用时标准化的 `{ channel, to, accountId }`）
- `transcriptPath`（从存储目录 + sessionId 推导出的最佳尝试路径）
- `messages?`（仅当 `messageLimit > 0` 时）

## sessions_history

获取一个会话的对话记录。

参数：

- `sessionKey`（必填；接受会话键或 `sessions_list` 中的 `sessionId`）
- `limit?: number` 最大消息数（服务器限制）
- `includeTools?: boolean`（默认 false）

行为：

- `includeTools=false` 会过滤 `role: "toolResult"` 的消息。
- 返回原始对话记录格式的消息数组。
- 当提供 `sessionId` 时，OpenClaw 会将其解析为对应的会话键（缺少 ID 会报错）。

## sessions_send

将消息发送到另一个会话。

参数：

- `sessionKey`（必填；接受会话键或 `sessions_list` 中的 `sessionId`）
- `message`（必填）
- `timeoutSeconds?: number`（默认 >0；0 = fire-and-forget）

行为：

- `timeoutSeconds = 0`：入队并返回 `{ runId, status: "accepted" }`。
- `timeoutSeconds > 0`：等待最多 N 秒完成，然后返回 `{ runId, status: "ok", reply }`。
- 如果等待超时：`{ runId, status: "timeout", error }`。运行继续；稍后调用 `sessions_history`。
- 如果运行失败：`{ runId, status: "error", error }`。
- 在主运行完成后进行交付公告（尽力而为）；`status: "ok"` 不保证公告已送达。
- 通过网关 `agent.wait`（服务器端）等待，以防止重连丢失等待。
- 代理间的消息上下文会注入主运行。
- 主运行完成后，OpenClaw 会运行 **回复循环**：
  - 第 2 轮及以后交替请求者和目标代理。
  - 回复正好 `REPLY_SKIP` 停止 ping-pong。
  - 最大轮数是 `session.agentToAgent.maxPingPongTurns`（0–5，默认 5）。
- 循环结束后，OpenClaw 运行 **代理间公告步骤**（仅目标代理）：
  - 回复正好 `ANNOUNCE_SKIP` 保持静默。
  - 任何其他回复会发送到目标频道。
  - 公告步骤包含原始请求 + 第 1 轮回复 + 最新 ping-pong 回复。

## 渠道字段

- 对于群聊，`channel` 是会话条目中记录的渠道。
- 对于直接聊天，`channel` 映射自 `lastChannel`。
- 对于 cron/hook/node，`channel` 是 `internal`。
- 如果缺失，`channel` 是 `unknown`。

## 安全 / 发送策略

基于渠道/聊天类型的策略性阻止（非会话 ID 级别）。

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

运行