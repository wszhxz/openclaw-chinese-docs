---
title: Outbound Session Mirroring Refactor (Issue #1520)
description: Track outbound session mirroring refactor notes, decisions, tests, and open items.
---
# 出站会话镜像重构（问题 #1520）

## 状态

- 进行中。
- 核心 + 插件通道路由已更新用于出站镜像。
- 网关发送现在在省略 sessionKey 时推导目标会话。

## 上下文

出站发送被镜像到 _当前_ 代理会话（工具会话密钥）而不是目标通道会话。入站路由使用通道/对等会话密钥，因此出站响应落在了错误的会话中，首次联系目标通常缺少会话条目。

## 目标

- 将出站消息镜像到目标通道会话密钥。
- 在出站时创建缺失的会话条目。
- 保持线程/主题范围与入站会话密钥对齐。
- 覆盖核心通道及捆绑扩展。

## 实现摘要

- 新的出站会话路由助手：
  - `session.ts`
  - `deriveTargetSessionKey` 使用 `resolveSessionTargets`（dmScope + identityLinks）构建目标 sessionKey。
  - `ensureSessionEntry` 通过 `upsertSession` 写入最小的 `sessionEntry`。
- `gateway.send`（发送）推导目标 sessionKey 并将其传递给 `mirrorAgentMessage` 进行镜像。
- `plugin.send` 不再直接镜像；它仅从当前会话密钥解析 agentId。
- 插件发送路径通过 `mirrorAgentMessage` 使用推导的 sessionKey 进行镜像。
- 网关发送在未提供时推导目标会话密钥（默认代理），并确保会话条目存在。

## 线程/主题处理

- Slack: replyTo/threadId -> `thread_suffix`（后缀）。
- Discord: threadId/replyTo -> `threadId` 与 `channelId` 匹配入站（线程通道 id 已经作用域化会话）。
- Telegram: 主题 ID 映射到 `topicId` 通过 `session.ts`。

## 涵盖的扩展

- Matrix, MS Teams, Mattermost, BlueBubbles, Nextcloud Talk, Zalo, Zalo Personal, Nostr, Tlon。
- 注意事项：
  - Mattermost 目标现在剥离 `bot_id` 以进行 DM 会话密钥路由。
  - Zalo Personal 对 1:1 目标使用 DM 对等类型（仅当 `group_id` 存在时为群组）。
  - BlueBubbles 群组目标剥离 `group_` 前缀以匹配入站会话密钥。
  - Slack 自动线程镜像不区分大小写地匹配通道 id。
  - 网关发送在镜像前将提供的会话密钥转换为小写。

## 决策

- **网关发送会话推导**：如果提供了 `sessionKey`，则使用它。如果省略，则从目标 + 默认代理推导 sessionKey 并在那里镜像。
- **会话条目创建**：始终使用 `upsertSession` 具有与入站格式对齐的 `sessionEntry`。
- **目标标准化**：出站路由在可用时使用解析的目标（后 `resolveTarget`）。
- **会话密钥大小写**：在写入和迁移期间将会话密钥规范化为小写。

## 添加/更新的测试

- `test/core/session.test.ts`
  - Slack 线程会话密钥。
  - Telegram 主题会话密钥。
  - 使用 Discord 的 dmScope identityLinks。
- `test/core/plugins.test.ts`
  - 从会话密钥推导 agentId（没有传递 sessionKey）。
- `test/core/gateway.test.ts`
  - 在省略时推导会话密钥并创建会话条目。

## 待办项目 / 后续工作

- 语音通话插件使用自定义 `voice-call` 会话密钥。此处未标准化出站映射；如果消息工具应支持语音通话发送，请添加显式映射。
- 确认是否有任何外部插件使用超出捆绑集的标准外 `sessionKey` 格式。

## 修改的文件

- `src/session.ts`
- `src/plugins.ts`
- `src/gateway.ts`
- `src/mirror.ts`
- `src/types.ts`
- 测试位于：
  - `test/core/session.test.ts`
  - `test/core/plugins.test.ts`
  - `test/core/gateway.test.ts`