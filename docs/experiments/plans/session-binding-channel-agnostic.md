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
# 会话绑定通道无关方案

## 概述

本文档定义了长期的、与通道无关的会话绑定模型，以及下一轮实现迭代的具体范围。

目标：

- 将子代理绑定会话路由打造为核心能力  
- 将通道特定行为保留在适配器中  
- 避免对常规 Discord 行为造成回归

## 此方案存在的原因

当前行为混合了以下内容：

- 完成内容策略  
- 目标路由策略  
- Discord 特定细节  

这导致了如下边缘情况：

- 在并发运行时，主频道与线程频道重复投递  
- 在复用绑定管理器时使用过期的 token  
- 基于 webhook 的发送缺失活动性统计

## 迭代 1 范围

本迭代范围有意限定。

### 1. 添加通道无关的核心接口

添加用于绑定与路由的核心类型及服务接口。

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

### 2. 为子代理完成事件添加一个核心投递路由器

为完成事件添加一条单一的目标解析路径。

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

在本迭代中：

- 仅 `task_completion` 经由此新路径路由  
- 其他事件类型的现有路径保持不变  

### 3. 保留 Discord 作为适配器

Discord 仍为首个适配器实现。

适配器职责包括：

- 创建/复用线程对话  
- 通过 webhook 或频道直发方式发送已绑定消息  
- 验证线程状态（归档/已删除）  
- 映射适配器元数据（webhook 身份、线程 ID）

### 4. 修复当前已知的正确性问题

本迭代必需完成：

- 在复用现有线程绑定管理器时刷新 token 使用  
- 为基于 webhook 的 Discord 发送记录外发活动性  
- 当会话模式完成已选定绑定线程目标时，禁止隐式回退至主频道

### 5. 保留当前运行时安全默认值

对禁用线程绑定启动功能的用户，不改变任何行为。

默认值保持：

- `channels.discord.threadBindings.spawnSubagentSessions = false`

结果：

- 常规 Discord 用户维持当前行为  
- 新核心路径仅影响启用绑定会话完成路由的场景  

## 迭代 1 不包含的内容

明确推迟实现：

- ACP 绑定目标（`targetKind: "acp"`）  
- Discord 之外的新通道适配器  
- 所有投递路径的全局替换（`spawn_ack`，未来 `subagent_message`）  
- 协议层级变更  
- 所有绑定持久化存储的迁移/版本重设计  

关于 ACP 的说明：

- 接口设计为 ACP 预留了扩展空间  
- 本迭代中不启动 ACP 实现  

## 路由不变量

以下不变量在迭代 1 中为强制要求：

- 目标选择与内容生成为两个独立步骤  
- 若会话模式完成解析至一个活跃的已绑定目标，则投递必须定向该目标  
- 禁止从已绑定目标隐式重路由至主频道  
- 回退行为必须显式且可观测  

## 兼容性与发布计划

兼容性目标：

- 对禁用线程绑定启动功能的用户无任何回归  
- 本迭代中不对非 Discord 通道作任何变更  

发布流程：

1. 将接口与路由器置于当前特性开关之后合入  
2. 将 Discord 完成模式下的绑定投递经由该路由器路由  
3. 对非绑定流程继续保留原有路径  
4. 通过定向测试与灰度运行日志验证  

## 迭代 1 所需测试

需覆盖的单元测试与集成测试包括：

- 管理器复用后，token 轮换使用最新 token  
- webhook 发送更新频道活动时间戳  
- 同一请求者频道内两个活跃绑定会话不会向主频道重复投递  
- 绑定会话模式运行的完成事件仅解析至线程目标  
- 禁用启动标志时，遗留行为保持不变  

## 建议的实现文件

核心模块：

- `src/infra/outbound/session-binding-service.ts`（新增）  
- `src/infra/outbound/bound-delivery-router.ts`（新增）  
- `src/agents/subagent-announce.ts`（完成目标解析集成）  

Discord 适配器与运行时：

- `src/discord/monitor/thread-bindings.manager.ts`  
- `src/discord/monitor/reply-delivery.ts`  
- `src/discord/send.outbound.ts`  

测试：

- `src/discord/monitor/provider*.test.ts`  
- `src/discord/monitor/reply-delivery.test.ts`  
- `src/agents/subagent-announce.format.test.ts`  

## 迭代 1 完成标准

- 核心接口已存在，并已接入完成路由流程  
- 上述正确性修复均已合入并附带对应测试  
- 会话模式绑定运行中不再出现主频道与线程频道重复完成投递  
- 对禁用绑定启动的部署无任何行为变更  
- ACP 仍明确推迟实现