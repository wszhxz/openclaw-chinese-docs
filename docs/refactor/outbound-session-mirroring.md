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

- 正在进行中。
- 核心模块及插件的通道路由已更新以支持出站镜像。
- 网关发送（Gateway send）现在在未提供 `sessionKey` 时，自动推导目标会话。

## 背景

此前，出站发送被镜像至 _当前_ 代理会话（即工具会话密钥），而非目标通道会话。而入站路由使用的是通道/对等方会话密钥，因此出站响应落入了错误的会话中，且首次联系的目标往往缺少对应的会话条目。

## 目标

- 将出站消息镜像至目标通道会话密钥（target channel session key）。
- 在缺失会话条目时，于出站阶段自动创建会话条目。
- 保持线程（thread）/主题（topic）的作用域与入站会话密钥对齐。
- 覆盖核心通道及所有内置扩展。

## 实现概要

- 新增出站会话路由辅助函数：
  - `src/infra/outbound/outbound-session.ts`
  - `resolveOutboundSessionRoute` 使用 `buildAgentSessionKey`（`dmScope` + `identityLinks`）构建目标 `sessionKey`。
  - `ensureOutboundSessionEntry` 通过 `recordSessionMetaFromInbound` 写入最小化的 `MsgContext`。
- `runMessageAction`（`send`）推导目标 `sessionKey` 并将其传递给 `executeSendAction` 执行镜像。
- `message-tool` 不再直接执行镜像；仅从当前会话密钥中解析 `agentId`。
- 插件发送路径通过 `appendAssistantMessageToSessionTranscript` 利用推导出的 `sessionKey` 进行镜像。
- 网关发送在未提供 `sessionKey` 时（默认代理场景）推导目标会话密钥，并确保存在对应会话条目。

## 线程/主题处理

- Slack：`replyTo`/`threadId` → `resolveThreadSessionKeys`（后缀形式）。
- Discord：`threadId`/`replyTo` → `resolveThreadSessionKeys`，并结合 `useSuffix=false` 以匹配入站行为（线程频道 ID 已天然限定会话范围）。
- Telegram：主题 ID 映射为 `chatId:topic:<id>`，通过 `buildTelegramGroupPeerId` 实现。

## 已覆盖的扩展

- Matrix、MS Teams、Mattermost、BlueBubbles、Nextcloud Talk、Zalo、Zalo Personal、Nostr、Tlon。
- 说明：
  - Mattermost 目标现在为私信（DM）会话密钥路由剥离 `@`。
  - Zalo Personal 对 1:1 目标使用 DM 对等方类型（peer kind）；仅当存在 `group:` 时才视为群组。
  - BlueBubbles 群组目标剥离 `chat_*` 前缀，以匹配入站会话密钥格式。
  - Slack 自动线程镜像对频道 ID 进行不区分大小写的匹配。
  - 网关发送在镜像前将提供的 `sessionKey` 统一转为小写。

## 决策要点

- **网关发送的会话密钥推导**：若提供了 `sessionKey`，则直接使用；若未提供，则基于目标 + 默认代理推导 `sessionKey` 并在该会话中执行镜像。
- **会话条目创建**：始终使用 `recordSessionMetaFromInbound`，且 `Provider/From/To/ChatType/AccountId/Originating*` 需与入站格式保持一致。
- **目标标准化**：出站路由在可用时优先采用已解析的目标（即经 `resolveChannelTarget` 处理后的结果）。
- **会话密钥大小写规范**：写入及迁移过程中，统一将 `sessionKey` 规范化为小写。

## 新增/更新的测试

- `src/infra/outbound/outbound.test.ts`
  - Slack 线程会话密钥。
  - Telegram 主题会话密钥。
  - 结合 Discord 的 `dmScope` 与 `identityLinks` 的私信会话密钥。
- `src/agents/tools/message-tool.test.ts`
  - 从会话密钥中解析 `agentId`（不传递 `sessionKey`）。
- `src/gateway/server-methods/send.test.ts`
  - 在未提供 `sessionKey` 时推导其值，并创建会话条目。

## 待办事项 / 后续工作

- 语音通话插件（voice-call plugin）使用自定义的 `voice:<phone>` 会话密钥。此处尚未标准化出站映射逻辑；若消息工具需支持语音通话发送，请添加显式映射。
- 请确认是否存在外部插件使用了超出内置集合范围的非标准 `From/To` 格式。

## 修改的文件

- `src/infra/outbound/outbound-session.ts`
- `src/infra/outbound/outbound-send-service.ts`
- `src/infra/outbound/message-action-runner.ts`
- `src/agents/tools/message-tool.ts`
- `src/gateway/server-methods/send.ts`
- 测试文件位于：
  - `src/infra/outbound/outbound.test.ts`
  - `src/agents/tools/message-tool.test.ts`
  - `src/gateway/server-methods/send.test.ts`