---
title: Outbound Session Mirroring Refactor (Issue #1520)
description: Track outbound session mirroring refactor notes, decisions, tests, and open items.
summary: "Refactor notes for mirroring outbound sends into target channel sessions"
read_when:
  - Working on outbound transcript/session mirroring behavior
  - Debugging sessionKey derivation for send/message tool paths
---
# 出站会话镜像重构（问题 #1520）

## 状态

- 进行中。
- Core + plugin 通道路由已针对出站镜像进行更新。
- Gateway send 现在在省略 sessionKey 时推导目标会话。

## 背景

出站消息被镜像到了当前代理会话（工具会话密钥），而非目标通道会话。入站路由使用通道/对等会话密钥，因此出站响应落入错误的会话，且首次联系的目标通常缺少会话条目。

## 目标

- 将出站消息镜像到目标通道会话密钥中。
- 在出站时创建缺失的会话条目。
- 保持线程/主题范围与入站会话密钥一致。
- 覆盖 core 通道及捆绑扩展。

## 实施摘要

- 新的出站会话路由辅助函数：
  - `src/infra/outbound/outbound-session.ts`
  - `resolveOutboundSessionRoute` 使用 `buildAgentSessionKey` 构建目标 sessionKey（dmScope + identityLinks）。
  - `ensureOutboundSessionEntry` 通过 `recordSessionMetaFromInbound` 写入最小化的 `MsgContext`。
- `runMessageAction` (send) 推导目标 sessionKey 并将其传递给 `executeSendAction` 用于镜像。
- `message-tool` 不再直接镜像；它仅从当前会话密钥解析 agentId。
- 插件发送路径通过 `appendAssistantMessageToSessionTranscript` 使用推导出的 sessionKey 进行镜像。
- Gateway send 在未提供目标会话密钥时（默认代理）会推导一个目标会话密钥，并确保存在会话条目。

## 线程/主题处理

- Slack: replyTo/threadId -> `resolveThreadSessionKeys`（后缀）。
- Discord: threadId/replyTo -> `resolveThreadSessionKeys` 带有 `useSuffix=false` 以匹配入站（线程通道 ID 已经限定会话范围）。
- Telegram: topic IDs 映射到 `chatId:topic:<id>` 通过 `buildTelegramGroupPeerId`。

## 覆盖的扩展

- Matrix, MS Teams, Mattermost, BlueBubbles, Nextcloud Talk, Zalo, Zalo Personal, Nostr, Tlon。
- 注意：
  - Mattermost 目标现在剥离 `@` 以用于 DM 会话密钥路由。
  - Zalo Personal 为 1:1 目标使用 DM 对等类型（仅当 `group:` 存在时使用群组）。
  - BlueBubbles 群组目标剥离 `chat_*` 前缀以匹配入站会话密钥。
  - Slack 自动线程镜像不区分大小写地匹配通道 ID。
  - Gateway send 在镜像前将提供的会话密钥小写化。

## 决策

- **Gateway send 会话推导**：如果提供了 `sessionKey`，则使用它。如果省略，则从目标 + 默认代理推导 sessionKey 并在那里镜像。
- **会话条目创建**：始终使用 `recordSessionMetaFromInbound`，其中 `Provider/From/To/ChatType/AccountId/Originating*` 与入站格式对齐。
- **目标标准化**：出站路由使用解析后的目标（`resolveChannelTarget` 之后），如果可用。
- **会话密钥大小写**：写入和迁移期间将会话密钥规范化为小写。

## 新增/更新的测试

- `src/infra/outbound/outbound.test.ts`
  - Slack 线程会话密钥。
  - Telegram 主题会话密钥。
  - dmScope identityLinks 与 Discord。
- `src/agents/tools/message-tool.test.ts`
  - 从会话密钥推导 agentId（不传递 sessionKey）。
- `src/gateway/server-methods/send.test.ts`
  - 省略时推导会话密钥并创建会话条目。

## 待办事项/后续跟进

- Voice-call 插件使用自定义 `voice:<phone>` 会话密钥。此处出站映射未标准化；如果 message-tool 应支持语音呼叫发送，请添加显式映射。
- 确认是否有任何外部插件在捆绑集之外使用了非标准的 `From/To` 格式。

## 受影响的文件

- `src/infra/outbound/outbound-session.ts`
- `src/infra/outbound/outbound-send-service.ts`
- `src/infra/outbound/message-action-runner.ts`
- `src/agents/tools/message-tool.ts`
- `src/gateway/server-methods/send.ts`
- 测试位于：
  - `src/infra/outbound/outbound.test.ts`
  - `src/agents/tools/message-tool.test.ts`
  - `src/gateway/server-methods/send.test.ts`