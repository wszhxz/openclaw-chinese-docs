---
summary: "Session management rules, keys, and persistence for chats"
read_when:
  - Modifying session handling or storage
title: "Session Management"
---
# 会话管理

OpenClaw 将 **每个代理的单个直接聊天会话** 作为主要会话。直接聊天会话会合并为 `agent:<agentId>:<mainKey>`（默认 `main`），而群组/频道聊天会话会获得各自的键。`session.mainKey` 会被优先使用。

使用 `session.dmScope` 来控制 **直接消息** 如何分组：

- `main`（默认）：所有 DM 共享主会话以保持连续性。
- `per-peer`：跨频道按发送者 ID 隔离。
- `per-channel-peer`：按频道 + 发送者隔离（推荐用于多用户收件箱）。
- `per-account-channel-peer`：按账户 + 频道 + 发送者隔离（推荐用于多账户收件箱）。
  使用 `session.identityLinks` 将提供方前缀的对等 ID 映射到规范身份，以便在使用 `per-peer`、`per-channel-peer` 或 `per-account-channel-peer` 时，同一人跨频道共享 DM 会话。

## 网关是真实来源

所有会话状态都 **由网关拥有**（“主” OpenClaw）。UI 客户端（macOS 应用、WebChat 等）必须从网关查询会话列表和令牌计数，而不是读取本地文件。

- 在 **远程模式** 下，您关心的会话存储位于远程网关主机上，而不是您的 Mac。
- UI 中显示的令牌计数来自网关的存储字段（`inputTokens`、`outputTokens`、`totalTokens`、`contextTokens`）。客户端不会解析 JSONL 转录本以“修复”总计数。

## 状态存储位置

- 在 **网关主机** 上：
  - 存储文件：`~/.openclaw/agents/<agentId>/sessions/sessions.json`（每个代理）。
- 转录本：`~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`（Telegram 主题会话使用 `.../<SessionId>-topic-<threadId>.jsonl`）。
- 存储是一个映射 `sessionKey -> { sessionId, updatedAt, ... }`。删除条目是安全的；它们会在需要时被重新创建。
- 群组条目可能包括 `displayName`、`channel`、`subject`、`room` 和 `space` 以在 UI 中标记会话。
- 会话条目包括 `origin` 元数据（标签 + 路由提示），以便 UI 解释会话的来源。
- OpenClaw **不会** 读取旧版 Pi/Tau 会话文件夹。

## 会话修剪

OpenClaw 默认在 LLM 调用前立即从内存上下文中修剪 **旧工具结果**。
这 **不会** 重写 JSONL 历史记录。请参阅 [/concepts/session-pruning](/concepts/session-pruning)。

## 预压缩内存刷新

当会话接近自动压缩时，OpenClaw 可以运行一个 **静默内存刷新** 操作
提醒模型将持久化笔记写入磁盘。此操作仅在
工作区可写时运行。请参阅 [Memory](/concepts/memory) 和
[Compaction](/concepts/compaction)。

## 映射传输 → 会话键

- 直接聊天遵循 `session.dmScope`（默认 `main`）。
  - `main`：`agent:<agentId>:<mainKey>`（跨设备/频道连续性）。
  - `per-peer`：`agent:<agentId>:<peerKey>`（按发送者隔离）。
  - `per-channel-peer`：`agent:<agentId>:<channelKey>`（按频道隔离）。
  - `per-account-channel-peer`：`agent:<agentId>:<accountKey>`（按账户隔离）。
- 群组/频道聊天会话使用 `agent:<agentId>:<groupKey>` 或 `agent:<agentId>:<channelKey>`。
- 转录本键格式为 `agent:<agentId>:<keyType>`，其中 `<keyType>` 是 `main`、`peer`、`channel`、`group` 等。

## 会话生命周期

- **重置策略**：定义会话何时被重置或更新。
- **每日重置**：按时间间隔自动重置会话。
- **空闲重置**：当会话空闲一段时间后自动重置。
- **覆盖**：允许通过 `resetByType` 或 `resetByChannel` 覆盖默认重置行为。

## 发送策略

- **