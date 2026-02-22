---
summary: "Channel agnostic session binding architecture and iteration 1 delivery scope"
owner: "onutc"
status: "in-progress"
last_updated: "2026-02-21"
title: "Session Binding Channel Agnostic Plan"
---
# 会话绑定通道不可知计划

## 概述

本文档定义了长期的通道不可知会话绑定模型以及下一个实现迭代的具体范围。

目标：

- 使子代理绑定会话路由成为核心能力
- 在适配器中保留特定于通道的行为
- 避免对正常Discord行为产生倒退

## 为什么存在

当前行为混合了：

- 完成内容策略
- 目的地路由策略
- 特定于Discord的细节

这导致了边缘情况，例如：

- 并发运行时主频道和线程交付的重复
- 重用绑定管理器时使用过期令牌
- 通过Webhook发送时缺少活动记录

## 迭代1范围

此迭代有意限制范围。

### 1. 添加通道不可知的核心接口

为绑定和路由添加核心类型和服务接口。

提议的核心类型：

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

### 2. 为子代理完成事件添加一个核心交付路由器

为完成事件添加单一的目标解析路径。

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

对于此迭代：

- 仅`task_completion`通过此新路径路由
- 其他事件类型的现有路径保持不变

### 3. 将Discord作为适配器

Discord仍然是第一个适配器实现。

适配器职责：

- 创建/重用线程对话
- 通过Webhook或频道发送发送绑定消息
- 验证线程状态（已归档/已删除）
- 映射适配器元数据（Webhook身份，线程ID）

### 4. 修复目前已知的正确性问题

此迭代必需：

- 重用现有线程绑定管理器时刷新令牌使用
- 记录基于Webhook的Discord发送的外发活动
- 当选择绑定线程目的地进行会话模式完成时停止隐式主频道回退

### 5. 保留当前运行时安全默认值

禁用线程绑定生成的用户行为不变。

默认值保持：

- `channels.discord.threadBindings.spawnSubagentSessions = false`

结果：

- 正常Discord用户保持当前行为
- 新核心路径仅影响启用时的绑定会话完成路由

## 不在迭代1中

明确推迟：

- ACP绑定目标 (`targetKind: "acp"`)
- Discord之外的新通道适配器
- 所有交付路径的全局替换 (`spawn_ack`, 未来的 `subagent_message`)
- 协议级别的更改
- 所有绑定持久化的存储迁移/版本重新设计

关于ACP的说明：

- 接口设计为ACP留有空间
- 此迭代不开始ACP实现

## 路由不变量

这些不变量是迭代1的强制要求。

- 目的地选择和内容生成是分开的步骤
- 如果会话模式完成解析为活动的绑定目的地，则交付必须针对该目的地
- 无从绑定目的地到主频道的隐藏重定向
- 回退行为必须是显式且可观察的

## 兼容性和推出

兼容性目标：

- 对禁用线程绑定生成的用户无回归
- 此迭代中非Discord通道无变化

推出：

1. 在当前功能门后部署接口和路由器。
2. 通过路由器路由Discord完成模式绑定交付。
3. 保持非绑定流的旧路径。
4. 使用针对性测试和金丝雀运行时日志验证。

## 迭代1所需的测试

需要的单元和集成覆盖：

- 管理器令牌轮换在重用管理器后使用最新令牌
- Webhook发送更新频道活动时间戳
- 同一请求者频道中的两个活动绑定会话不会复制到主频道
- 绑定会话模式运行的完成解析仅为线程目的地
- 禁用生成标志保持遗留行为不变

## 提议的实现文件

核心：

- `src/infra/outbound/session-binding-service.ts` (新)
- `src/infra/outbound/bound-delivery-router.ts` (新)
- `src/agents/subagent-announce.ts` (完成目标解析集成)

Discord适配器和运行时：

- `src/discord/monitor/thread-bindings.manager.ts`
- `src/discord/monitor/reply-delivery.ts`
- `src/discord/send.outbound.ts`

测试：

- `src/discord/monitor/provider*.test.ts`
- `src/discord/monitor/reply-delivery.test.ts`
- `src/agents/subagent-announce.format.e2e.test.ts`

## 迭代1完成标准

- 核心接口存在并连接用于完成路由
- 上述正确性修复与测试合并
- 会话模式绑定运行中无主频道和线程完成交付的重复
- 禁用绑定生成部署的行为不变
- ACP保持明确推迟