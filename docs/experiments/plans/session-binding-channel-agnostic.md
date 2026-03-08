---
summary: "Channel agnostic session binding architecture and iteration 1 delivery scope"
read_when:
  - Refactoring channel-agnostic session routing and bindings
  - Investigating duplicate, stale, or missing session delivery across channels
owner: "onutc"
status: "in-progress"
last_updated: "2026-02-21"
title: "Session Binding Channel Agnostic Plan"
---
# Session Binding Channel Agnostic 计划

## 概述

本文档定义了长期的 Channel Agnostic 会话绑定模型以及下一次实现迭代的具体范围。

目标：

- 将 Subagent 绑定会话路由作为核心功能
- 在 Adapters 中保留特定渠道行为
- 避免正常 Discord 行为的回归

## 为什么存在此方案

当前行为混合了：

- 完成内容策略
- 目的地路由策略
- Discord 特定细节

这导致了以下边缘情况：

- 并发运行时主频道和线程投递重复
- 复用的 Binding Managers 上使用过期的 Token
- Webhook 发送缺少活动记录

## 迭代 1 范围

本次迭代有意限制范围。

### 1. 添加 Channel Agnostic 核心接口

为 Bindings 和 Routing 添加核心类型和服务接口。

建议的核心类型：

```ts
export type BindingTargetKind = "subagent" | "session";
export type BindingStatus = "active" | "ending" | "ended";

export type ConversationRef = {
  channel: string;
  accountId: string;
  conversationId: string;
  parentConversationId?: string;
};

export type SessionBindingRecord = {
  bindingId: string;
  targetSessionKey: string;
  targetKind: BindingTargetKind;
  conversation: ConversationRef;
  status: BindingStatus;
  boundAt: number;
  expiresAt?: number;
  metadata?: Record<string, unknown>;
};
```

核心服务契约：

```ts
export interface SessionBindingService {
  bind(input: {
    targetSessionKey: string;
    targetKind: BindingTargetKind;
    conversation: ConversationRef;
    metadata?: Record<string, unknown>;
    ttlMs?: number;
  }): Promise<SessionBindingRecord>;

  listBySession(targetSessionKey: string): SessionBindingRecord[];
  resolveByConversation(ref: ConversationRef): SessionBindingRecord | null;
  touch(bindingId: string, at?: number): void;
  unbind(input: {
    bindingId?: string;
    targetSessionKey?: string;
    reason: string;
  }): Promise<SessionBindingRecord[]>;
}
```

### 2. 为 Subagent 完成添加一个核心投递路由器

为完成事件添加单一目的地解析路径。

路由器契约：

```ts
export interface BoundDeliveryRouter {
  resolveDestination(input: {
    eventKind: "task_completion";
    targetSessionKey: string;
    requester?: ConversationRef;
    failClosed: boolean;
  }): {
    binding: SessionBindingRecord | null;
    mode: "bound" | "fallback";
    reason: string;
  };
}
```

针对本次迭代：

- 仅 `task_completion` 通过此新路径路由
- 其他事件类型的现有路径保持不变

### 3. 保持 Discord 作为 Adapter

Discord 仍然是第一个 Adapter 实现。

Adapter 职责：

- 创建/复用线程对话
- 通过 Webhook 或频道发送绑定消息
- 验证线程状态（归档/删除）
- 映射 Adapter 元数据（Webhook 身份，线程 ID）

### 4. 修复当前已知的正确性问题

本次迭代必需：

- 复用现有线程 Binding Manager 时刷新 Token 使用
- 记录基于 Webhook 的 Discord 发送出站活动
- 当为 Session Mode 完成选择绑定线程目的地时，停止隐式主频道回退

### 5. 保留当前运行时安全默认值

对于禁用线程绑定生成的用户无行为变更。

默认值保持不变：

- `channels.discord.threadBindings.spawnSubagentSessions = false`

结果：

- 普通 Discord 用户保持当前行为
- 新核心路径仅在启用时影响绑定会话完成路由

## 不在迭代 1 中

明确延期：

- ACP 绑定目标 (`targetKind: "acp"`)
- 除 Discord 外的新渠道 Adapters
- 所有投递路径的全局替换 (`spawn_ack`, 未来 `subagent_message`)
- 协议级别变更
- 所有绑定持久化的 Store 迁移/版本重设计

关于 ACP 的说明：

- 接口设计为 ACP 保留了空间
- ACP 实现未在本次迭代开始

## 路由不变量

这些不变量对迭代 1 是强制性的。

- 目的地选择和内容生成是分开的步骤
- 如果 Session Mode 完成解析到活动的绑定目的地，投递必须针对该目的地
- 从绑定目的地到主频道的隐藏重路由
- 回退行为必须是显式的且可观测的

## 兼容性和发布

兼容性目标：

- 禁用线程绑定生成的用户无回归
- 本次迭代非 Discord 渠道无变更

发布：

1. 在当前 Feature Gates 后落地接口和路由器。
2. 通过路由器路由 Discord 完成模式绑定投递。
3. 为非绑定流程保留旧路径。
4. 通过针对性测试和 Canary 运行时日志进行验证。

## 迭代 1 所需测试

需要单元测试和集成覆盖：

- 管理器 Token 轮换在管理器复用后使用最新 Token
- Webhook 发送更新频道活动时间戳
- 同一请求者频道中的两个活动绑定会话不会重复到主频道
- 绑定 Session Mode 运行的完成仅解析到线程目的地
- 禁用的 Spawn 标志保持旧行为不变

## 建议的实现文件

核心：

- `src/infra/outbound/session-binding-service.ts` (新建)
- `src/infra/outbound/bound-delivery-router.ts` (新建)
- `src/agents/subagent-announce.ts` (完成目的地解析集成)

Discord Adapter 和运行时：

- `src/discord/monitor/thread-bindings.manager.ts`
- `src/discord/monitor/reply-delivery.ts`
- `src/discord/send.outbound.ts`

测试：

- `src/discord/monitor/provider*.test.ts`
- `src/discord/monitor/reply-delivery.test.ts`
- `src/agents/subagent-announce.format.test.ts`

## 迭代 1 完成标准

- 核心接口存在并连接至完成路由
- 上述正确性修复已合并测试
- Session Mode 绑定运行中无主频道和线程重复完成投递
- 禁用绑定生成的部署无行为变更
- ACP 保持明确延期