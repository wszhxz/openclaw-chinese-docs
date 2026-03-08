---
summary: "Integrate ACP coding agents via a first-class ACP control plane in core and plugin-backed runtimes (acpx first)"
owner: "onutc"
status: "draft"
last_updated: "2026-02-25"
title: "ACP Thread Bound Agents"
---
# ACP 线程绑定代理

## 概述

本计划定义了 OpenClaw 应如何在支持线程的通道中（首选 Discord）为 ACP 编码代理提供生产级生命周期和恢复支持。

相关文档：

- [统一运行时流重构计划](/experiments/plans/acp-unified-streaming-refactor)

目标用户体验：

- 用户将 ACP 会话启动或聚焦到线程中
- 该线程中的用户消息路由到绑定的 ACP 会话
- 代理输出流回同一线程角色
- 会话可以是持久的或一次性的，并带有明确的清理控制

## 决策摘要

长期建议采用混合架构：

- OpenClaw 核心负责 ACP 控制平面事务
  - 会话身份和元数据
  - 线程绑定和路由决策
  - 交付不变量和重复抑制
  - 生命周期清理和恢复语义
- ACP 运行时后端是可插拔的
  - 首个后端是 acpx 支持的插件服务
  - 运行时处理 ACP 传输、排队、取消、重连

OpenClaw 不应在核心中重新实现 ACP 传输内部细节。
OpenClaw 不应依赖纯插件拦截路径进行路由。

## 北极星架构（圣杯）

将 ACP 视为 OpenClaw 中的一等控制平面，配备可插拔的运行时适配器。

不可协商的不变量：

- 每个 ACP 线程绑定引用有效的 ACP 会话记录
- 每个 ACP 会话都有明确的生命周期状态 (`creating`, `idle`, `running`, `cancelling`, `closed`, `error`)
- 每个 ACP 运行都有明确的运行状态 (`queued`, `running`, `completed`, `failed`, `cancelled`)
- 启动、绑定和初始入队是原子的
- 命令重试是可幂等的（无重复运行或重复的 Discord 输出）
- 绑定线程通道输出是 ACP 运行事件的投影，绝非临时副作用

长期所有权模型：

- `AcpSessionManager` 是唯一的 ACP 写入者和编排器
- 管理器首先存在于网关进程中；之后可以移动到专用的 Sidecar 后面，通过相同的接口
- 针对每个 ACP 会话键，管理器拥有一个内存中的 Actor（串行化命令执行）
- 适配器 (`acpx`，未来后端) 仅是传输/运行时实现

长期持久化模型：

- 将 ACP 控制平面状态移至 OpenClaw 状态目录下的专用 SQLite 存储（WAL 模式）
- 迁移期间保留 `SessionEntry.acp` 作为兼容性投影，而非事实来源
- 以追加方式存储 ACP 事件以支持重放、崩溃恢复和确定性交付

### 交付策略（通往圣杯的桥梁）

- 短期桥梁
  - 保持当前的线程绑定机制和现有的 ACP 配置表面
  - 修复元数据间隙错误，并通过单一核心 ACP 分支路由 ACP 回合
  - 立即添加幂等键和故障关闭路由检查
- 长期切换
  - 将 ACP 事实来源移至控制平面数据库 + Actors
  - 使绑定线程交付完全基于事件投影
  - 移除依赖于机会性会话入口元数据的遗留回退行为

## 为何不纯靠插件

没有核心更改，当前的插件钩子不足以支持端到端 ACP 会话路由。

- 来自线程绑定的入站路由首先解析为核心分发中的会话键
- 消息钩子是即发即弃的，无法短路主回复路径
- 插件命令适合控制操作，但不适合替换核心的每回合分发流程

结果：

- ACP 运行时可以被插件化
- ACP 路由分支必须存在于核心中

## 可复用的现有基础

已实现且应保持为标准：

- 线程绑定目标支持 `subagent` 和 `acp`
- 入站线程路由覆盖通过绑定在正常分发之前解析
- 通过回复交付中的 Webhook 进行出站线程标识
- `/focus` 和 `/unfocus` 流与 ACP 目标兼容
- 持久化绑定存储，启动时恢复
- 归档、删除、取消聚焦、重置和删除时的解绑生命周期

本计划扩展了该基础，而不是替换它。

## 架构

### 边界模型

核心（必须在 OpenClaw 核心中）：

- 回复管道中的 ACP 会话模式分发分支
- 交付仲裁以避免父级加线程重复
- ACP 控制平面持久化（迁移期间带有 `SessionEntry.acp` 兼容性投影）
- 与会话重置/删除关联的生命周期解绑和运行时分离语义

插件后端（acpx 实现）：

- ACP 运行时工作进程监督
- acpx 进程调用和事件解析
- ACP 命令处理器 (`/acp ...`) 和操作员 UX
- 特定后端的配置默认值和诊断

### 运行时所有权模型

- 一个网关进程拥有 ACP 编排状态
- ACP 执行通过 acpx 后端在受监督的子进程中运行
- 进程策略是针对每个活动的 ACP 会话键长期存在，而非针对每条消息

这避免了每次提示的启动成本，并保持取消和重连语义可靠。

### 核心运行时契约

添加核心 ACP 运行时契约，以便路由代码不依赖于 CLI 细节，并且可以在不更改分发逻辑的情况下切换后端：

```ts
export type AcpRuntimePromptMode = "prompt" | "steer";

export type AcpRuntimeHandle = {
  sessionKey: string;
  backend: string;
  runtimeSessionName: string;
};

export type AcpRuntimeEvent =
  | { type: "text_delta"; stream: "output" | "thought"; text: string }
  | { type: "tool_call"; name: string; argumentsText: string }
  | { type: "done"; usage?: Record<string, number> }
  | { type: "error"; code: string; message: string; retryable?: boolean };

export interface AcpRuntime {
  ensureSession(input: {
    sessionKey: string;
    agent: string;
    mode: "persistent" | "oneshot";
    cwd?: string;
    env?: Record<string, string>;
    idempotencyKey: string;
  }): Promise<AcpRuntimeHandle>;

  submit(input: {
    handle: AcpRuntimeHandle;
    text: string;
    mode: AcpRuntimePromptMode;
    idempotencyKey: string;
  }): Promise<{ runtimeRunId: string }>;

  stream(input: {
    handle: AcpRuntimeHandle;
    runtimeRunId: string;
    onEvent: (event: AcpRuntimeEvent) => Promise<void> | void;
    signal?: AbortSignal;
  }): Promise<void>;

  cancel(input: {
    handle: AcpRuntimeHandle;
    runtimeRunId?: string;
    reason?: string;
    idempotencyKey: string;
  }): Promise<void>;

  close(input: { handle: AcpRuntimeHandle; reason: string; idempotencyKey: string }): Promise<void>;

  health?(): Promise<{ ok: boolean; details?: string }>;
}
```

实现细节：

- 首个后端：`AcpxRuntime` 作为插件服务发布
- 核心通过注册表解析运行时，当没有可用的 ACP 运行时后端时，以显式操作员错误失败

### 控制平面数据模型和持久化

长期事实来源是专用的 ACP SQLite 数据库（WAL 模式），用于事务更新和崩溃安全恢复：

- `acp_sessions`
  - `session_key` (pk), `backend`, `agent`, `mode`, `cwd`, `state`, `created_at`, `updated_at`, `last_error`
- `acp_runs`
  - `run_id` (pk), `session_key` (fk), `state`, `requester_message_id`, `idempotency_key`, `started_at`, `ended_at`, `error_code`, `error_message`
- `acp_bindings`
  - `binding_key` (pk), `thread_id`, `channel_id`, `account_id`, `session_key` (fk), `expires_at`, `bound_at`
- `acp_events`
  - `event_id` (pk), `run_id` (fk), `seq`, `kind`, `payload_json`, `created_at`
- `acp_delivery_checkpoint`
  - `run_id` (pk/fk), `last_event_seq`, `last_discord_message_id`, `updated_at`
- `acp_idempotency`
  - `scope`, `idempotency_key`, `result_json`, `created_at`, unique `(scope, idempotency_key)`

```ts
export type AcpSessionMeta = {
  backend: string;
  agent: string;
  runtimeSessionName: string;
  mode: "persistent" | "oneshot";
  cwd?: string;
  state: "idle" | "running" | "error";
  lastActivityAt: number;
  lastError?: string;
};
```

存储规则：

- 迁移期间保留 `SessionEntry.acp` 作为兼容性投影
- 进程 ID 和套接字仅保留在内存中
- 持久化生命周期和运行状态位于 ACP 数据库中，而非通用会话 JSON
- 如果运行时所有者死亡，网关从 ACP 数据库恢复并从检查点继续

### 路由和交付

入站：

- 保持当前线程绑定查找作为第一步路由
- 如果绑定目标是 ACP 会话，则路由到 ACP 运行时分支而不是 `getReplyFromConfig`
- 显式 `/acp steer` 命令使用 `mode: "steer"`

出站：

- ACP 事件流标准化为 OpenClaw 回复块
- 交付目标通过现有的绑定目标路径解析
- 当绑定线程对该会话回合处于活动状态时，父通道完成被抑制

流策略：

- 使用合并窗口流式传输部分输出
- 可配置的最小间隔和最大块字节以保持低于 Discord 速率限制
- 最终消息总是在完成或失败时发出

### 状态机和事务边界

会话状态机：

- `creating -> idle -> running -> idle`
- `running -> cancelling -> idle | error`
- `idle -> closed`
- `error -> idle | closed`

运行状态机：

- `queued -> running -> completed`
- `running -> failed | cancelled`
- `queued -> cancelled`

必需的事务边界：

- 启动事务
  - 创建 ACP 会话行
  - 创建/更新 ACP 线程绑定行
  - 入队初始运行行
- 关闭事务
  - 标记会话关闭
  - 删除/过期绑定行
  - 写入最终关闭事件
- 取消事务
  - 使用幂等键标记目标运行正在取消/已取消

这些边界之间不允许部分成功。

### 每会话 Actor 模型

`AcpSessionManager` 为每个 ACP 会话键运行一个 Actor：

- Actor 邮箱序列化 `submit`, `cancel`, `close` 和 `stream` 副作用
- Actor 拥有该会话的运行时句柄填充和运行时适配器进程生命周期
- Actor 在任何 Discord 交付之前按顺序写入运行事件 (`seq`)
- Actor 在成功出站发送后更新交付检查点

这消除了跨回合竞争，并防止重复或乱序的线程输出。

### 幂等性与投递投影

所有外部 ACP 操作必须携带幂等键：

- spawn 幂等键
- prompt/steer 幂等键
- cancel 幂等键
- close 幂等键

投递规则：

- Discord 消息源自 `acp_events` 加上 `acp_delivery_checkpoint`
- 重试从检查点恢复，不重新发送已交付的块
- 最终回复发射在每次运行中根据投影逻辑精确一次

### 恢复与自愈

在网关启动时：

- 加载非终端 ACP 会话 (`creating`, `idle`, `running`, `cancelling`, `error`)
- 在第一个入站事件上惰性重建 Actor，或在配置限制下急切重建
- 协调任何缺少心跳的 `running` 运行，并标记 `failed` 或通过适配器恢复

在接收 Discord 线程消息时：

- 如果绑定存在但 ACP 会话缺失，则显式失败并附带过时的绑定消息
- 可选地在操作员安全验证后自动解除过时绑定
- 切勿静默将过时的 ACP 绑定路由到正常的 LLM 路径

### 生命周期与安全

支持的操作：

- 取消当前运行：`/acp cancel`
- 解除线程绑定：`/unfocus`
- 关闭 ACP 会话：`/acp close`
- 通过有效 TTL 自动关闭空闲会话

TTL 策略：

- 有效 TTL 为以下的最小值
  - 全局/会话 TTL
  - Discord 线程绑定 TTL
  - ACP 运行时所有者 TTL

安全控制：

- 按名称允许 ACP Agents
- 限制 ACP 会话的工作区根目录
- 环境变量允许列表透传
- 每账户及全局最大并发 ACP 会话数
- 运行时崩溃的有界重启退避

## 配置表面

核心键：

- `acp.enabled`
- `acp.dispatch.enabled` (独立 ACP 路由熔断开关)
- `acp.backend` (默认 `acpx`)
- `acp.defaultAgent`
- `acp.allowedAgents[]`
- `acp.maxConcurrentSessions`
- `acp.stream.coalesceIdleMs`
- `acp.stream.maxChunkChars`
- `acp.runtime.ttlMinutes`
- `acp.controlPlane.store` (`sqlite` 默认)
- `acp.controlPlane.storePath`
- `acp.controlPlane.recovery.eagerActors`
- `acp.controlPlane.recovery.reconcileRunningAfterMs`
- `acp.controlPlane.checkpoint.flushEveryEvents`
- `acp.controlPlane.checkpoint.flushEveryMs`
- `acp.idempotency.ttlHours`
- `channels.discord.threadBindings.spawnAcpSessions`

插件/后端键 (acpx 插件部分)：

- 后端命令/路径覆盖
- 后端环境允许列表
- 后端每个 Agent 预设
- 后端启动/停止超时
- 后端每个会话最大进行中运行数

## 实现规范

### 控制平面模块 (新增)

在核心中添加专用的 ACP 控制平面模块：

- `src/acp/control-plane/manager.ts`
  - 拥有 ACP Actors、生命周期转换、命令序列化
- `src/acp/control-plane/store.ts`
  - SQLite 架构管理、事务、查询辅助
- `src/acp/control-plane/events.ts`
  - 类型化 ACP 事件定义和序列化
- `src/acp/control-plane/checkpoint.ts`
  - 持久化投递检查点和重放游标
- `src/acp/control-plane/idempotency.ts`
  - 幂等键预留和响应重放
- `src/acp/control-plane/recovery.ts`
  - 启动时协调和 Actor 重建计划

兼容性桥接模块：

- `src/acp/runtime/session-meta.ts`
  - 暂时保留用于向 `SessionEntry.acp` 投影
  - 迁移切换后必须停止作为事实来源

### 必需不变量 (必须在代码中强制执行)

- ACP 会话创建和线程绑定是原子的（单个事务）
- 同一时间每个 ACP 会话 Actor 最多有一个活动运行
- 事件 `seq` 在每个运行中严格递增
- 投递检查点绝不推进超过最后提交的事件
- 幂等重放对于重复的命令键返回之前的成功负载
- 过时/缺失的 ACP 元数据不能路由到正常的非 ACP 回复路径

### 核心接触点

需要更改的核心文件：

- `src/auto-reply/reply/dispatch-from-config.ts`
  - ACP 分支调用 `AcpSessionManager.submit` 和事件投影投递
  - 移除绕过控制平面不变量的直接 ACP 回退
- `src/auto-reply/reply/inbound-context.ts` (或最近的标准化上下文边界)
  - 暴露标准化的路由键和 ACP 控制平面幂等种子
- `src/config/sessions/types.ts`
  - 保持 `SessionEntry.acp` 作为仅投影兼容字段
- `src/gateway/server-methods/sessions.ts`
  - 重置/删除/归档必须调用 ACP 管理器关闭/解除绑定事务路径
- `src/infra/outbound/bound-delivery-router.ts`
  - 对 ACP 绑定会话回合强制执行故障关闭目标行为
- `src/discord/monitor/thread-bindings.ts`
  - 添加 ACP 过时绑定验证助手，连接到控制平面查找
- `src/auto-reply/reply/commands-acp.ts`
  - 通过 ACP 管理器 API 路由 spawn/cancel/close/steer
- `src/agents/acp-spawn.ts`
  - 停止临时元数据写入；调用 ACP 管理器 spawn 事务
- `src/plugin-sdk/**` 和插件运行时桥接
  - 干净地暴露 ACP 后端注册和健康语义

明确不替换的核心文件：

- `src/discord/monitor/message-handler.preflight.ts`
  - 保持线程绑定覆盖行为作为标准会话键解析器

### ACP 运行时注册表 API

添加一个核心注册表模块：

- `src/acp/runtime/registry.ts`

所需 API：

```ts
export type AcpRuntimeBackend = {
  id: string;
  runtime: AcpRuntime;
  healthy?: () => boolean;
};

export function registerAcpRuntimeBackend(backend: AcpRuntimeBackend): void;
export function unregisterAcpRuntimeBackend(id: string): void;
export function getAcpRuntimeBackend(id?: string): AcpRuntimeBackend | null;
export function requireAcpRuntimeBackend(id?: string): AcpRuntimeBackend;
```

行为：

- 当不可用时，`requireAcpRuntimeBackend` 抛出类型化的 ACP 后端缺失错误
- 插件服务在 `start` 上注册后端，在 `stop` 上注销
- 运行时查找是只读且进程本地的

### acpx 运行时插件契约 (实现细节)

对于首个生产后端 (`extensions/acpx`)，OpenClaw 和 acpx 通过严格的命令契约连接：

- 后端 ID: `acpx`
- 插件服务 ID: `acpx-runtime`
- 运行时句柄编码：`runtimeSessionName = acpx:v1:<base64url(json)>`
- 编码负载字段：
  - `name` (acpx 命名会话；使用 OpenClaw `sessionKey`)
  - `agent` (acpx Agent 命令)
  - `cwd` (会话工作区根目录)
  - `mode` (`persistent | oneshot`)

命令映射：

- 确保会话：
  - `acpx --format json --json-strict --cwd <cwd> <agent> sessions ensure --name <name>`
- 提示回合：
  - `acpx --format json --json-strict --cwd <cwd> <agent> prompt --session <name> --file -`
- 取消：
  - `acpx --format json --json-strict --cwd <cwd> <agent> cancel --session <name>`
- 关闭：
  - `acpx --format json --json-strict --cwd <cwd> <agent> sessions close <name>`

流式传输：

- OpenClaw 从 `acpx --format json --json-strict` 消费 ndjson 事件
- `text` => `text_delta/output`
- `thought` => `text_delta/thought`
- `tool_call` => `tool_call`
- `done` => `done`
- `error` => `error`

### 会话架构补丁

在 `src/config/sessions/types.ts` 中修补 `SessionEntry`：

```ts
type SessionAcpMeta = {
  backend: string;
  agent: string;
  runtimeSessionName: string;
  mode: "persistent" | "oneshot";
  cwd?: string;
  state: "idle" | "running" | "error";
  lastActivityAt: number;
  lastError?: string;
};
```

持久化字段：

- `SessionEntry.acp?: SessionAcpMeta`

迁移规则：

- 阶段 A：双写 (`acp` 投影 + ACP SQLite 事实来源)
- 阶段 B：主读来自 ACP SQLite，回退读来自旧版 `SessionEntry.acp`
- 阶段 C：迁移命令从有效的旧版条目回填缺失的 ACP 行
- 阶段 D：移除回退读，仅保留投影供 UX 使用
- 旧版字段 (`cliSessionIds`, `claudeCliSessionId`) 保持不变

### 错误契约

添加稳定的 ACP 错误码和用户可见消息：

- `ACP_BACKEND_MISSING`
  - 消息：`ACP runtime backend is not configured. Install and enable the acpx runtime plugin.`
- `ACP_BACKEND_UNAVAILABLE`
  - 消息：`ACP runtime backend is currently unavailable. Try again in a moment.`
- `ACP_SESSION_INIT_FAILED`
  - 消息：`Could not initialize ACP session runtime.`
- `ACP_TURN_FAILED`
  - 消息：`ACP turn failed before completion.`

规则：

- 在线程内返回可操作的、用户安全消息
- 仅在运行时日志中记录详细后端/系统错误
- 当明确选择 ACP 路由时，切勿静默回退到正常 LLM 路径

### 重复投递仲裁

ACP 绑定回合的单一路由规则：

- 如果目标 ACP 会话和请求者上下文中存在活动的线程绑定，仅投递到该绑定线程
- 不要同时向同一回合的父频道发送
- 如果绑定目标选择模糊，则显式错误故障关闭（无隐式父级回退）
- 如果没有活动绑定，使用正常会话目标行为

### 可观测性与运营就绪

所需指标：

- 按后端和错误代码分组的 ACP spawn 成功/失败计数
- ACP 运行延迟百分位数（队列等待、运行时回合时间、投递投影时间）
- ACP Actor 重启计数和重启原因
- 过时绑定检测计数
- 幂等重放命中率
- Discord 投递重试和速率限制计数器

所需日志：

- 以 `sessionKey`, `runId`, `backend`, `threadId`, `idempotencyKey` 为键的结构化日志
- 会话和运行状态机的显式状态转换日志
- 带有脱敏安全参数和退出摘要的适配器命令日志

所需诊断：

- `/acp sessions` 包括状态、活动运行、最后错误和绑定状态
- `/acp doctor` (或等效项) 验证后端注册、存储健康和过时绑定

### 配置优先级和有效值

ACP 启用优先级：

- 账户覆盖：`channels.discord.accounts.<id>.threadBindings.spawnAcpSessions`
- 频道覆盖：`channels.discord.threadBindings.spawnAcpSessions`
- 全局 ACP 门控：`acp.enabled`
- 分发门控：`acp.dispatch.enabled`
- 后端可用性：已注册的 `acp.backend` 后端

自动启用行为：

- 当配置了 ACP 时 (`acp.enabled=true`, `acp.dispatch.enabled=true`, 或
  `acp.backend=acpx`)，插件自动启用标记 `plugins.entries.acpx.enabled=true`
  除非在拒绝列表中或明确禁用

TTL 有效值：

- `min(session ttl, discord thread binding ttl, acp runtime ttl)`

### 测试概览

单元测试：

- `src/acp/runtime/registry.test.ts` (new)
- `src/auto-reply/reply/dispatch-from-config.acp.test.ts` (new)
- `src/infra/outbound/bound-delivery-router.test.ts` (extend ACP fail-closed cases)
- `src/config/sessions/types.test.ts` 或最近的 session-store 测试 (ACP metadata persistence)

集成测试：

- `src/discord/monitor/reply-delivery.test.ts` (bound ACP delivery target behavior)
- `src/discord/monitor/message-handler.preflight*.test.ts` (bound ACP session-key routing continuity)
- backend package 中的 acpx 插件运行时测试 (service register/start/stop + event normalization)

网关 E2E 测试：

- `src/gateway/server.sessions.gateway-server-sessions-a.e2e.test.ts` (extend ACP reset/delete lifecycle coverage)
- ACP thread turn roundtrip e2e for spawn, message, stream, cancel, unfocus, restart recovery

### 发布保护

添加独立的 ACP 分发开关：

- `acp.dispatch.enabled` 默认 `false` 用于首次发布
- 当禁用时：
  - ACP spawn/focus 控制命令仍可能绑定会话
  - ACP 分发路径不激活
  - 用户收到明确消息表明 ACP 分发由策略禁用
- 金丝雀验证后，可在后续发布中将默认值翻转为 `true`

## 命令与用户体验计划

### 新命令

- `/acp spawn <agent-id> [--mode persistent|oneshot] [--thread auto|here|off]`
- `/acp cancel [session]`
- `/acp steer <instruction>`
- `/acp close [session]`
- `/acp sessions`

### 现有命令兼容性

- `/focus <sessionKey>` 继续支持 ACP 目标
- `/unfocus` 保持当前语义
- `/session idle` 和 `/session max-age` 替换旧的 TTL 覆盖

## 分阶段发布

### 第 0 阶段：ADR 和架构冻结

- 发布关于 ACP 控制平面所有权和适配器边界的 ADR
- 冻结 DB 架构 (`acp_sessions`, `acp_runs`, `acp_bindings`, `acp_events`, `acp_delivery_checkpoint`, `acp_idempotency`)
- 定义稳定的 ACP 错误码、事件契约和状态转换守卫

### 第 1 阶段：核心中的控制平面基础

- 实现 `AcpSessionManager` 和每会话 Actor 运行时
- 实现 ACP SQLite store 和事务辅助函数
- 实现幂等性存储和重放辅助函数
- 实现事件追加 + 交付检查点模块
- 将 spawn/cancel/close APIs 连接到带有事务保证的 manager

### 第 2 阶段：核心路由与生命周期集成

- 从分发流水线路由线程绑定的 ACP turns 到 ACP manager
- 当 ACP binding/session 不变量失败时强制执行 fail-closed 路由
- 集成 reset/delete/archive/unfocus 生命周期与 ACP close/unbind 事务
- 添加过期绑定检测和可选的自动解绑策略

### 第 3 阶段：acpx 后端适配器/插件

- 针对运行时契约 (`ensureSession`, `submit`, `stream`, `cancel`, `close`) 实现 `acpx` 适配器
- 添加后端健康检查和启动/销毁注册
- 将 acpx ndjson 事件标准化为 ACP 运行时事件
- 强制执行后端超时、进程监管和重启/退避策略

### 第 4 阶段：交付投影与渠道体验（优先 Discord）

- 实现带检查点恢复的事件驱动渠道投影（优先 Discord）
- 合并流式块并采用感知速率限制的刷新策略
- 确保每个运行具有精确一次最终完成消息
- 发布 `/acp spawn`, `/acp cancel`, `/acp steer`, `/acp close`, `/acp sessions`

### 第 5 阶段：迁移与切换

- 引入双写到 `SessionEntry.acp` 投影以及 ACP SQLite 单一事实来源
- 添加用于旧版 ACP 元数据行的迁移工具
- 将读取路径切换到 ACP SQLite 主库
- 移除依赖于缺失 `SessionEntry.acp` 的旧版回退路由

### 第 6 阶段：加固、SLOs 和扩展限制

- 强制执行并发限制（全局/账户/会话）、队列策略和超时预算
- 添加完整遥测、仪表盘和告警阈值
- 混沌测试崩溃恢复和重复交付抑制
- 发布后端中断、DB 损坏和过期绑定修复的操作手册

### 完整实施清单

- 核心控制平面模块和测试
- DB 迁移和回滚计划
- 跨分发和命令的 ACP manager API 集成
- 插件运行时桥接中的适配器注册接口
- acpx 适配器实现和测试
- 支持线程的渠道交付投影逻辑与检查点重放（优先 Discord）
- reset/delete/archive/unfocus 的生命周期钩子
- 过期绑定检测器和面向操作员诊断
- 所有新 ACP 键的配置验证和优先级测试
- 运维文档和故障排除手册

## 测试计划

单元测试：

- ACP DB 事务边界 (spawn/bind/enqueue 原子性，cancel, close)
- 会话和运行的 ACP 状态机转换守卫
- 所有 ACP 命令的幂等性预留/重放语义
- 每会话 Actor 序列化和队列顺序
- acpx 事件解析器和块合并器
- 运行时监管器重启和退避策略
- 配置优先级和有效 TTL 计算
- 核心 ACP 路由分支选择及后端/会话无效时的 fail-closed 行为

集成测试：

- 用于确定性流式和取消行为的模拟 ACP 适配器进程
- 带事务持久性的 ACP manager + 分发集成
- 线程绑定的入站路由到 ACP session-key
- 线程绑定的出站交付抑制父渠道重复
- 交付失败后检查点重放恢复并从最后一个事件恢复
- 插件服务注册和 ACP 运行时后端的销毁

网关 E2E 测试：

- 使用线程 spawn ACP，交换多轮提示，unfocus
- 使用持久化 ACP DB 和绑定重启网关，然后继续同一会话
- 多个线程中的并发 ACP 会话无交叉通信
- 重复命令重试（相同幂等性键）不会创建重复运行或回复
- 过期绑定场景产生明确错误和可选的自动清理行为

## 风险与缓解措施

- 过渡期间的重复交付
  - 缓解：单一目标解析器和幂等事件检查点
- 负载下的运行时进程波动
  - 缓解：长生命周期的每会话所有者 + 并发上限 + 退避
- 插件缺失或配置错误
  - 缓解：明确的操作员错误和 fail-closed ACP 路由（无隐式回退到正常会话路径）
- 子代理与 ACP 门控之间的配置混淆
  - 缓解：明确的 ACP 键和包含有效策略源的命令反馈
- 控制平面存储损坏或迁移错误
  - 缓解：WAL 模式、备份/恢复钩子、迁移冒烟测试和只读回退诊断
- Actor 死锁或邮箱饥饿
  - 缓解：看门狗定时器、Actor 健康探测和有界邮箱深度与拒绝遥测

## 验收清单

- ACP session spawn 可以在支持的渠道适配器中创建或绑定线程（目前为 Discord）
- 所有线程消息仅路由到绑定的 ACP session
- ACP 输出出现在相同的线程身份中，带有流式或批次
- 绑定的回合中父渠道无重复输出
- spawn+bind+初始入队在持久化存储中是原子的
- ACP 命令重试是幂等的且不会重复运行或输出
- cancel, close, unfocus, archive, reset, 和 delete 执行确定性清理
- 崩溃重启保留映射并恢复多轮连续性
- 并发线程绑定的 ACP 会话独立工作
- ACP 后端缺失状态产生清晰的 actionable 错误
- 过期绑定被检测并显式暴露（带可选的安全自动清理）
- 控制平面指标和诊断对操作员可用
- 新的单元测试、集成测试和 E2E 覆盖通过

## 附录：当前实施的针对性重构（状态）

这些是非阻塞的后续工作，以保持 ACP 路径在当前功能集落地后的可维护性。

### 1) 集中 ACP 分发策略评估（已完成）

- 通过 `src/acp/policy.ts` 中的共享 ACP 策略辅助函数实现
- 分发、ACP 命令生命周期处理器和 ACP spawn 路径现在消费共享策略逻辑

### 2) 按子命令域拆分 ACP 命令处理器（已完成）

- `src/auto-reply/reply/commands-acp.ts` 现在是薄路由器
- 子命令行为拆分为：
  - `src/auto-reply/reply/commands-acp/lifecycle.ts`
  - `src/auto-reply/reply/commands-acp/runtime-options.ts`
  - `src/auto-reply/reply/commands-acp/diagnostics.ts`
  - `src/auto-reply/reply/commands-acp/shared.ts` 中的共享辅助函数

### 3) 按职责拆分 ACP 会话管理器（已完成）

- 管理器拆分为：
  - `src/acp/control-plane/manager.ts` (public facade + singleton)
  - `src/acp/control-plane/manager.core.ts` (manager implementation)
  - `src/acp/control-plane/manager.types.ts` (manager types/deps)
  - `src/acp/control-plane/manager.utils.ts` (normalization + helper functions)

### 4) 可选 acpx 运行时适配器清理

- `extensions/acpx/src/runtime.ts` 可以拆分为：
- 进程执行/监管
- ndjson 事件解析/标准化
- 运行时 API 表面 (`submit`, `cancel`, `close`, 等)
- 提高可测试性并使后端行为更容易审计