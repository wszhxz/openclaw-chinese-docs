---
title: Outbound Session Mirroring Refactor (Issue #1520)
description: Track outbound session mirroring refactor notes, decisions, tests, and open items.
---
# 出站会话镜像重构 (Issue #1520)

## 状态

- 进行中。
- 核心 + 插件通道路由已更新以支持出站镜像。
- 网关发送现在在省略sessionKey时派生目标会话。

## 上下文

出站发送被镜像到当前代理会话（工具会话密钥），而不是目标通道会话。入站路由使用通道/对等体会话密钥，因此出站响应落在错误的会话中，首次接触的目标通常缺少会话条目。

## 目标

- 将出站消息镜像到目标通道会话密钥。
- 在出站时创建缺失的会话条目。
- 保持线程/主题范围与入站会话密钥一致。
- 覆盖核心通道以及捆绑的扩展。

## 实现摘要

- 新的出站会话路由辅助工具：
  - `src/infra/outbound/outbound-session.ts`
  - `resolveOutboundSessionRoute` 使用 `buildAgentSessionKey` (dmScope + identityLinks) 构建目标sessionKey。
  - `ensureOutboundSessionEntry` 通过 `recordSessionMetaFromInbound` 写入最小的 `MsgContext`。
- `runMessageAction` (send) 派生目标sessionKey并将其传递给 `executeSendAction` 进行镜像。
- `message-tool` 不再直接镜像；它仅从当前会话密钥解析agentId。
- 插件发送路径通过 `appendAssistantMessageToSessionTranscript` 使用派生的sessionKey进行镜像。
- 网关发送在未提供目标会话密钥时派生一个目标会话密钥（默认代理），并确保会话条目存在。

## 线程/主题处理

- Slack: replyTo/threadId -> `resolveThreadSessionKeys` (后缀)。
- Discord: threadId/replyTo -> `resolveThreadSessionKeys` 带有 `useSuffix=false` 以匹配入站（线程通道ID已经对会话进行了范围限定）。
- Telegram: 主题ID通过 `buildTelegramGroupPeerId` 映射到 `chatId:topic:<id>`。

## 覆盖的扩展

- Matrix, MS Teams, Mattermost, BlueBubbles, Nextcloud Talk, Zalo, Zalo Personal, Nostr, Tlon。
- 注意事项：
  - Mattermost目标现在剥离 `@` 用于DM会话密钥路由。
  - Zalo Personal 对于一对一目标使用DM对等体类型（只有在存在 `group:` 时才为群组）。
  - BlueBubbles群组目标剥离 `chat_*` 前缀以匹配入站会话密钥。
  - Slack自动线程镜像不区分大小写地匹配频道ID。
  - 网关发送在镜像之前将提供的会话密钥转换为小写。

## 决策

- **网关发送会话派生**：如果提供了 `sessionKey`，则使用它。如果省略，则从目标 + 默认代理派生sessionKey并在此处镜像。
- **会话条目创建**：始终使用 `recordSessionMetaFromInbound` 并将 `Provider/From/To/ChatType/AccountId/Originating*` 与入站格式对齐。
- **目标规范化**：出站路由在可用时使用解析后的目标（`resolveChannelTarget` 后）。
- **会话密钥大小写**：在写入和迁移期间将会话密钥规范为小写。

## 添加/更新的测试

- `src/infra/outbound/outbound-session.test.ts`
  - Slack线程会话密钥。
  - Telegram主题会话密钥。
  - 带有Discord的dmScope identityLinks。
- `src/agents/tools/message-tool.test.ts`
  - 从会话密钥派生agentId（不传递sessionKey）。
- `src/gateway/server-methods/send.test.ts`
  - 省略时派生会话密钥并创建会话条目。

## 开放事项 / 后续工作

- 语音通话插件使用自定义 `voice:<phone>` 会话密钥。此处未标准化出站映射；如果消息工具应支持语音通话发送，请添加显式映射。
- 确认是否有任何外部插件使用超出捆绑集的非标准 `From/To` 格式。

## 修改的文件

- `src/infra/outbound/outbound-session.ts`
- `src/infra/outbound/outbound-send-service.ts`
- `src/infra/outbound/message-action-runner.ts`
- `src/agents/tools/message-tool.ts`
- `src/gateway/server-methods/send.ts`
- 测试位于：
  - `src/infra/outbound/outbound-session.test.ts`
  - `src/agents/tools/message-tool.test.ts`
  - `src/gateway/server-methods/send.test.ts`