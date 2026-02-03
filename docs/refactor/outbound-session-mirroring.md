---
title: Outbound Session Mirroring Refactor (Issue #1520)
description: Track outbound session mirroring refactor notes, decisions, tests, and open items.
---
# 出站会话镜像重构（问题 #1520）

## 状态

- 进行中。
- 已更新核心 + 插件通道路由以支持出站镜像。
- 网关发送现在在未提供 sessionKey 时会推导目标会话。

## 背景

出站发送被镜像到当前代理会话（工具会话密钥）而非目标通道会话。入站路由使用通道/对等会话密钥，因此出站响应落在错误的会话中，且首次接触目标通常缺少会话条目。

## 目标

- 将出站消息镜像到目标通道会话密钥。
- 在缺少会话条目时创建会话条目。
- 保持线程/主题作用域与入站会话密钥一致。
- 覆盖核心通道及捆绑扩展。

## 实现概要

- 新的出站会话路由辅助工具：
  - `src/infra/outbound/outbound-session.ts`
  - `resolveOutboundSessionRoute` 使用 `buildAgentSessionKey`（dmScope + identityLinks）构建目标 sessionKey。
  - `ensureOut,SessionEntry` 通过 `recordSessionMetaFromInbound` 写入最小的 `MsgContext`。
- `runMessageAction`（发送）推导目标 sessionKey 并传递给 `executeSendAction` 进行镜像。
- `message-tool` 不再直接镜像；它仅从当前会话密钥解析 agentId。
- 插件发送路径通过 `appendAssistantMessageToSessionTranscript` 使用推导的 sessionKey 进行镜像。
- 网关发送在未提供 sessionKey 时推导目标会话密钥（默认代理），并确保会话条目。

## 线程/主题处理

- Slack：replyTo/threadId -> `resolveThreadSessionKeys`（后缀）。
- Discord：threadId/replyTo -> 使用 `useSuffix=false` 的 `resolveThreadSessionKeys` 以匹配入站（线程频道 ID 已经作用域会话）。
- Telegram：主题 ID 映射到 `chatId:topic:<id>` 通过 `buildTelegramGroupPeerId`。

## 覆盖的扩展

- Matrix, MS Teams, Mattermost, BlueBubbles, Nextcloud Talk, Zalo, Zalo Personal, Nostr, Tlon。
- 备注：
  - Mattermost 目标现在去除 `@` 以进行 DM 会话密钥路由。
  - Zalo Personal 使用 DM 对等类型进行 1:1 目标（仅当 `group:` 存在时为群组）。
  - BlueBubbles 群组目标去除 `chat_*` 前缀以匹配入站会话密钥。
  - Slack 自动线程镜像以不区分大小写匹配频道 ID。
  - 网关发送在镜像前将提供的会话密钥转为小写。

## 决策

- **网关发送会话推导**：如果提供 `sessionKey`，使用它。若未提供，从目标 + 默认代理推导 sessionKey 并镜像到该位置。
- **会话条目创建**：始终使用 `recordSessionMetaFromInbound`，并确保 `Provider/From/To/ChatType/AccountId/Originating*` 与入站格式一致。
- **目标规范化**：出站路由在可用时使用解析后的目标（post `resolveChannelTarget`）。
- **会话密钥大小写**：在写入和迁移期间将会话密钥标准化为小写。

## 新增/更新的测试

- `src/infra/outbound/outbound-session.test.ts`
  - Slack 线程会话密钥。
  - Telegram 主题会话密钥。
  - dmScope identityLinks 与 Discord。
- `src/agents/tools/message-tool.test.ts`
  - 从会话密钥推导 agentId（未传递 sessionKey）。
- `src/gateway/server-methods/send.test.ts`
  - 未提供 sessionKey 时推导会话密钥并创建会话条目。

## 待办事项 / 后续工作

- 语音通话插件使用自定义 `voice:<phone>` 会话密钥。出站映射在此未标准化；如果 message-tool 应支持语音通话发送，需添加显式映射。
- 确认是否有外部插件使用超出捆绑集的非标准 `From/To` 格式。

## 修改的文件

- `src/infra/outbound/outbound-session.ts`
- `src/infra/outbound/outbound-send-service.ts`
- `src/infra/outbound/message-action-runner.ts`
- `src/agents/tools/message-tool.ts`
- `src/gateway/server-methods/send.ts`
- 测试文件：
  - `src/infra/outbound/outbound-session.test.ts`
  - `src/agents/tools/message-tool.test.ts`
  - `src/gateway/server-methods/send.test.ts`