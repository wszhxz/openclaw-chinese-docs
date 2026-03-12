---
summary: "Integrate ACP coding agents via a first-class ACP control plane in core and plugin-backed runtimes (acpx first)"
owner: "onutc"
status: "draft"
last_updated: "2026-02-25"
title: "ACP Thread Bound Agents"
---
# ACP 线程绑定代理

## 概述

本计划定义了 OpenClaw 应如何在支持线程的通道（首选 Discord）中以生产级生命周期与恢复能力支持 ACP 编码代理。

相关文档：

- [统一运行时流式处理重构计划](/experiments/plans/acp-unified-streaming-refactor)

目标用户体验：

- 用户在某一线程中启动或聚焦一个 ACP 会话  
- 用户在该线程中的消息被路由至已绑定的 ACP 会话  
- 代理输出流式返回至同一“线程身份”（thread persona）  
- 会话可为持久化或一次性，且提供显式的清理控制机制  

## 决策摘要

长期推荐采用混合架构：

- OpenClaw 核心负责 ACP 控制平面相关职责  
  - 会话身份与元数据管理  
  - 线程绑定与路由决策  
  - 投递不变性保障与重复抑制  
  - 生命周期清理与恢复语义  
- ACP 运行时后端可插拔  
  - 首个后端为基于 acpx 的插件服务  
  - 运行时负责 ACP 传输、排队、取消与重连  

OpenClaw 核心不应重新实现 ACP 传输内部逻辑。  
OpenClaw 不应依赖纯插件拦截路径来完成路由。

## 终极架构（圣杯目标）

将 ACP 视为 OpenClaw 中的一等控制平面，支持可插拔的运行时适配器。

不可妥协的不变性约束：

- 每个 ACP 线程绑定均引用一个有效的 ACP 会话记录  
- 每个 ACP 会话具有明确的生命周期状态（``creating``、``idle``、``running``、``cancelling``、``closed``、``error``）  
- 每次 ACP 执行具有明确的运行状态（``queued``、``running``、``completed``、``failed``、``cancelled``）  
- 启动（spawn）、绑定（bind）与初始入队（enqueue）操作必须是原子性的  
- 命令重试必须幂等（不得产生重复执行或重复的 Discord 输出）  
- 绑定线程通道的输出仅为 ACP 运行事件的投影，绝非临时副作用  

长期所有权模型：

- ``AcpSessionManager`` 是唯一的 ACP 写入者与协调器  
- 协调器初始部署于网关进程内；后续可迁移至专用 sidecar，但保持相同接口  
- 每个 ACP 会话密钥对应一个内存中 actor（串行化命令执行）  
- 适配器（``acpx`` 及未来后端）仅负责传输/运行时实现  

长期持久化模型：

- 将 ACP 控制平面状态迁移至 OpenClaw 状态目录下的专用 SQLite 存储（WAL 模式）  
- 在迁移期间保留 ``SessionEntry.acp`` 作为兼容性投影，而非事实来源（source-of-truth）  
- ACP 事件以追加写入（append-only）方式存储，以支持重放、崩溃恢复与确定性投递  

### 投递策略（通往圣杯的桥梁）

- 短期过渡方案  
  - 保留当前线程绑定机制及现有 ACP 配置界面  
  - 修复元数据缺失缺陷，并将 ACP 对话轮次（turns）统一经由单一核心 ACP 分支路由  
  - 立即引入幂等性密钥与“失败即关闭”（fail-closed）路由检查  
- 长期切换方案  
  - 将 ACP 事实来源迁移至控制平面数据库 + actors  
  - 使绑定线程的投递完全基于事件投影  
  - 移除依赖机会主义会话入口元数据（opportunistic session-entry metadata）的传统回退行为  

## 为何不采用纯插件方案

当前插件钩子不足以在不修改核心的前提下，实现端到端的 ACP 会话路由。

- 来自线程绑定的入站路由首先在核心分发逻辑中解析为会话密钥  
- 消息钩子为“即发即弃”（fire-and-forget），无法短路主回复路径  
- 插件命令适用于控制类操作，但无法替代核心每轮次（per-turn）分发流程  

结果：

- ACP 运行时可插件化  
- ACP 路由分支必须存在于核心中  

## 可复用的现有基础

以下功能已实现，且应保持其规范地位：

- 线程绑定目标支持 ``subagent`` 和 ``acp``  
- 入站线程路由覆写（override）在常规分发前先依据绑定关系解析  
- 出站线程身份通过回复投递中的 webhook 实现  
- ``/focus`` 和 ``/unfocus`` 流程已兼容 ACP 目标  
- 持久化绑定存储，支持启动时恢复  
- 在归档、删除、失焦、重置与彻底删除时触发解绑生命周期  

本计划在此基础上进行扩展，而非替换。

## 架构

### 边界模型

核心（必须置于 OpenClaw 核心中）：

- 回复流水线中的 ACP 会话模式分发分支  
- 投递仲裁机制，避免父通道与线程通道重复投递  
- ACP 控制平面持久化（迁移期间保留 ``SessionEntry.acp`` 兼容性投影）  
- 与会话重置/删除绑定的生命周期解绑及运行时分离语义  

插件后端（acpx 实现）：

- ACP 运行时工作器（worker）监管  
- acpx 进程调用与事件解析  
- ACP 命令处理器（``/acp ...``）及操作员 UX  
- 后端专属配置默认值与诊断能力  

### 运行时所有权模型

- 单一网关进程拥有 ACP 编排状态  
- ACP 执行运行于 acpx 后端所监管的子进程中  
- 进程策略为：每个活跃 ACP 会话密钥长期驻留一个进程，而非每条消息启动一个进程  

此举可避免每次提示（prompt）都产生启动开销，并确保取消与重连语义的可靠性。

### 核心运行时契约

新增核心 ACP 运行时契约，使路由代码不依赖 CLI 细节，且可在不更改分发逻辑的前提下切换后端：

````ts
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
````

实现细节：

- 首个后端：``AcpxRuntime`` 作为插件服务发布  
- 核心通过注册表解析运行时；若无可用 ACP 运行时后端，则报出明确的操作员错误  

### 控制平面数据模型与持久化

长期事实来源为专用 ACP SQLite 数据库（WAL 模式），以支持事务性更新与崩溃安全恢复：

- ``acp_sessions``  
  - ``session_key``（主键）、``backend``、``agent``、``mode``、``cwd``、``state``、``created_at``、``updated_at``、``last_error``  
- ``acp_runs``  
  - ``run_id``（主键）、``session_key``（外键）、``state``、``requester_message_id``、``idempotency_key``、``started_at``、``ended_at``、``error_code``、``error_message``  
- ``acp_bindings``  
  - ``binding_key``（主键）、``thread_id``、``channel_id``、``account_id``、``session_key``（外键）、``expires_at``、``bound_at``  
- ``acp_events``  
  - ``event_id``（主键）、``run_id``（外键）、``seq``、``kind``、``payload_json``、``created_at``  
- ``acp_delivery_checkpoint``  
  - ``run_id``（主键/外键）、``last_event_seq``、``last_discord_message_id``、``updated_at``  
- ``acp_idempotency``  
  - ``scope``、``idempotency_key``、``result_json``、``created_at``、唯一 ``(scope, idempotency_key)``  

````ts
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
````

存储规则：

- 迁移期间保留 ``SessionEntry.acp`` 作为兼容性投影  
- 进程 ID 与套接字仅驻留内存  
- 持久化的生命周期与运行状态存于 ACP 数据库，而非通用会话 JSON  
- 若运行时所有者崩溃，网关将从 ACP 数据库重建状态，并从检查点继续执行  

### 路由与投递

入站：

- 保留当前线程绑定查找作为首要路由步骤  
- 若绑定目标为 ACP 会话，则路由至 ACP 运行时分支，而非 ``getReplyFromConfig``  
- 显式 ``/acp steer`` 命令使用 ``mode: "steer"``  

出站：

- ACP 事件流被标准化为 OpenClaw 回复块（reply chunks）  
- 投递目标通过既有的绑定目标路径解析  
- 当该会话轮次处于活跃绑定线程时，父通道的完成投递将被抑制  

流式策略：

- 采用聚合窗口（coalescing window）流式发送部分输出  
- 可配置最小间隔与最大分块字节数，以符合 Discord 速率限制  
- 最终消息总是在完成或失败时发出  

### 状态机与事务边界

会话状态机：

- ``creating -> idle -> running -> idle``  
- ``running -> cancelling -> idle | error``  
- ``idle -> closed``  
- ``error -> idle | closed``  

运行状态机：

- ``queued -> running -> completed``  
- ``running -> failed | cancelled``  
- ``queued -> cancelled``  

必需的事务边界：

- 启动事务  
  - 创建 ACP 会话行  
  - 创建/更新 ACP 线程绑定行  
  - 入队初始运行行  
- 关闭事务  
  - 标记会话为已关闭  
  - 删除/过期绑定行  
  - 写入最终关闭事件  
- 取消事务  
  - 使用幂等性密钥标记目标运行为“正在取消”/“已取消”  

上述边界内不允许部分成功。

### 每会话 Actor 模型

``AcpSessionManager`` 为每个 ACP 会话密钥运行一个 actor：

- actor 邮箱对 ``submit``、``cancel``、``close`` 与 ``stream`` 副作用进行串行化  
- actor 拥有该会话的运行时句柄初始化与运行时适配器进程生命周期管理权  
- actor 在任何 Discord 投递前，按序写入运行事件（``seq``）  
- actor 在成功完成出站发送后更新投递检查点  

此举消除了跨轮次竞态条件，并防止线程输出重复或乱序。

### 幂等性与交付投影

所有外部 ACP 操作都必须携带幂等性密钥：

- spawn 幂等性密钥  
- prompt/steer 幂等性密钥  
- cancel 幂等性密钥  
- close 幂等性密钥  

交付规则：

- Discord 消息由 `acp_events` 和 `acp_delivery_checkpoint` 共同推导得出  
- 重试从检查点恢复，不会重复发送已成功交付的分块  
- 最终回复的发出在投影逻辑中每轮运行严格保证“恰好一次”  

### 恢复与自愈能力

网关启动时：

- 加载非终止态的 ACP 会话（`creating`、`idle`、`running`、`cancelling`、`error`）  
- 在首次收到入站事件时惰性重建 Actor；或在配置上限内主动预加载  
- 对缺失心跳信号的 `running` 运行进行协调，并将 `failed` 标记为失效，或通过适配器执行恢复  

收到入站 Discord 主题消息时：

- 若绑定存在但 ACP 会话丢失，则以明确的“过期绑定”消息执行失败关闭（fail closed）  
- 可选：在经操作员安全验证后自动解绑过期绑定  
- 绝不允许将过期的 ACP 绑定静默路由至常规 LLM 路径  

### 生命周期与安全性

支持的操作：

- 取消当前运行：`/acp cancel`  
- 解绑主题：`/unfocus`  
- 关闭 ACP 会话：`/acp close`  
- 按有效 TTL 自动关闭空闲会话  

TTL 策略：

- 有效 TTL 取以下各项的最小值：  
  - 全局/会话级 TTL  
  - Discord 主题绑定 TTL  
  - ACP 运行时所有者 TTL  

安全控制：

- 按名称白名单限定可使用的 ACP Agent  
- 限制 ACP 会话可访问的工作区根路径  
- 环境变量白名单透传机制  
- 每账户及全局范围内最大并发 ACP 会话数限制  
- 运行时崩溃后的重启退避时间上限  

## 配置面（Config surface）

核心配置项：

- `acp.enabled`  
- `acp.dispatch.enabled`（独立 ACP 路由的全局开关）  
- `acp.backend`（默认 `acpx`）  
- `acp.defaultAgent`  
- `acp.allowedAgents[]`  
- `acp.maxConcurrentSessions`  
- `acp.stream.coalesceIdleMs`  
- `acp.stream.maxChunkChars`  
- `acp.runtime.ttlMinutes`  
- `acp.controlPlane.store`（默认为 `sqlite`）  
- `acp.controlPlane.storePath`  
- `acp.controlPlane.recovery.eagerActors`  
- `acp.controlPlane.recovery.reconcileRunningAfterMs`  
- `acp.controlPlane.checkpoint.flushEveryEvents`  
- `acp.controlPlane.checkpoint.flushEveryMs`  
- `acp.idempotency.ttlHours`  
- `channels.discord.threadBindings.spawnAcpSessions`  

插件/后端配置项（acpx 插件节）：

- 后端命令/路径覆盖配置  
- 后端环境变量白名单  
- 按 Agent 预设的后端配置  
- 后端启动/停止超时设置  
- 每个会话允许的最大并发运行数  

## 实现规范

### 控制平面模块（新增）

在核心中添加专用 ACP 控制平面模块：

- `src/acp/control-plane/manager.ts`  
  - 管理 ACP Actor、生命周期状态迁移及命令序列化  
- `src/acp/control-plane/store.ts`  
  - SQLite 模式管理、事务处理与查询辅助工具  
- `src/acp/control-plane/events.ts`  
  - 类型化的 ACP 事件定义与序列化逻辑  
- `src/acp/control-plane/checkpoint.ts`  
  - 持久化交付检查点与重放游标  
- `src/acp/control-plane/idempotency.ts`  
  - 幂等性密钥预留及响应重放机制  
- `src/acp/control-plane/recovery.ts`  
  - 启动时协调与 Actor 重建计划  

兼容性桥接模块：

- `src/acp/runtime/session-meta.ts`  
  - 暂时保留，用于向 `SessionEntry.acp` 投影数据  
  - 迁移切换完成后，不得再作为唯一可信数据源  

### 必须保障的不变量（需在代码中强制实施）

- ACP 会话创建与主题绑定必须是原子操作（单事务）  
- 每个 ACP 会话 Actor 同一时刻最多仅有一个活跃运行  
- 事件 `seq` 在每次运行中严格递增  
- 交付检查点绝不可超越最后已提交事件的位置  
- 幂等性重放对重复命令密钥必须返回此前成功的响应载荷  
- 过期/缺失的 ACP 元数据绝不可被路由至常规非 ACP 回复路径  

### 核心触点

需修改的核心文件：

- `src/auto-reply/reply/dispatch-from-config.ts`  
  - ACP 分支调用 `AcpSessionManager.submit` 并执行事件投影交付  
  - 移除绕过控制平面不变量的直接 ACP 回退逻辑  
- `src/auto-reply/reply/inbound-context.ts`（或最近的标准化上下文边界）  
  - 暴露标准化的路由键与幂等性种子，供 ACP 控制平面使用  
- `src/config/sessions/types.ts`  
  - 保留 `SessionEntry.acp` 作为仅用于投影兼容性的字段  
- `src/gateway/server-methods/sessions.ts`  
  - 重置/删除/归档操作必须调用 ACP 管理器的 close/unbind 事务路径  
- `src/infra/outbound/bound-delivery-router.ts`  
  - 对已绑定 ACP 的会话回合，强制执行失败即关闭（fail-closed）的目标行为  
- `src/discord/monitor/thread-bindings.ts`  
  - 添加 ACP 过期绑定校验辅助函数，并接入控制平面查询逻辑  
- `src/auto-reply/reply/commands-acp.ts`  
  - 将 spawn/cancel/close/steer 操作统一通过 ACP 管理器 API 路由  
- `src/agents/acp-spawn.ts`  
  - 停止临时元数据写入；改由 ACP 管理器 spawn 事务完成  
- `src/plugin-sdk/**` 及插件运行时桥接模块  
  - 清晰暴露 ACP 后端注册与健康状态语义  

明确**不替换**的核心文件：

- `src/discord/monitor/message-handler.preflight.ts`  
  - 保留主题绑定覆盖行为，作为权威的会话键解析器  

### ACP 运行时注册表 API

新增一个核心注册表模块：

- `src/acp/runtime/registry.ts`  

必需 API：

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

行为说明：

- `requireAcpRuntimeBackend` 在后端不可用时抛出类型化的 ACP 后端缺失错误  
- 插件服务在 `start` 上注册后端，并在 `stop` 上注销  
- 运行时查找为只读且限于本进程内  

### acpx 运行时插件契约（实现细节）

针对首个生产级后端（`extensions/acpx`），OpenClaw 与 acpx 之间采用严格的命令契约：

- 后端 ID：`acpx`  
- 插件服务 ID：`acpx-runtime`  
- 运行时句柄编码格式：`runtimeSessionName = acpx:v1:<base64url(json)>`  
- 编码后载荷字段：  
  - `name`（acpx 命名会话；复用 OpenClaw 的 `sessionKey`）  
  - `agent`（acpx Agent 命令）  
  - `cwd`（会话工作区根路径）  
  - `mode`（`persistent | oneshot`）  

命令映射：

- 确保会话存在：  
  - `acpx --format json --json-strict --cwd <cwd> <agent> sessions ensure --name <name>`  
- Prompt 轮次：  
  - `acpx --format json --json-strict --cwd <cwd> <agent> prompt --session <name> --file -`  
- 取消：  
  - `acpx --format json --json-strict --cwd <cwd> <agent> cancel --session <name>`  
- 关闭：  
  - `acpx --format json --json-strict --cwd <cwd> <agent> sessions close <name>`  

流式传输：

- OpenClaw 从 `acpx --format json --json-strict` 消费 ndjson 事件  
- `text` ⇒ `text_delta/output`  
- `thought` ⇒ `text_delta/thought`  
- `tool_call` ⇒ `tool_call`  
- `done` ⇒ `done`  
- `error` ⇒ `error`  

### 会话模式补丁

对 `SessionEntry` 在 `src/config/sessions/types.ts` 中打补丁：

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

- 阶段 A：双写（`acp` 投影 + ACP SQLite 作为唯一可信源）  
- 阶段 B：主读取来自 ACP SQLite，降级读取来自旧版 `SessionEntry.acp`  
- 阶段 C：迁移命令从有效的旧版条目中回填缺失的 ACP 行  
- 阶段 D：移除降级读取逻辑，仅保留投影作为可选 UX 支持  
- 旧字段（`cliSessionIds`、`claudeCliSessionId`）保持不变  

### 错误契约

新增稳定的 ACP 错误码及面向用户的提示消息：

- `ACP_BACKEND_MISSING`  
  - 消息：`ACP runtime backend is not configured. Install and enable the acpx runtime plugin.`  
- `ACP_BACKEND_UNAVAILABLE`  
  - 消息：`ACP runtime backend is currently unavailable. Try again in a moment.`  
- `ACP_SESSION_INIT_FAILED`  
  - 消息：`Could not initialize ACP session runtime.`  
- `ACP_TURN_FAILED`  
  - 消息：`ACP turn failed before completion.`  

规则：

- 在线程内返回用户可操作的安全提示消息  
- 详细的后端/系统错误仅记录于运行时日志中  
- 当显式选择 ACP 路由时，绝不静默回退至常规 LLM 路径  

### 重复交付仲裁

ACP 绑定回合的单一路由规则：

- 若目标 ACP 会话与请求者上下文存在活跃的主题绑定，则仅向该绑定主题交付  
- 不得在同一回合中额外发送至父频道  
- 若绑定目标选择存在歧义，则以明确错误执行失败关闭（无隐式父频道回退）  
- 若不存在活跃绑定，则采用常规会话目标行为  

### 可观测性与运维就绪度

必需指标：

- 按后端与错误码统计的 ACP spawn 成功/失败次数  
- ACP 运行延迟百分位（排队等待时间、运行时轮次耗时、交付投影耗时）  
- ACP Actor 重启次数及重启原因  
- 过期绑定检测次数  
- 幂等性重放命中率  
- Discord 交付重试与限流计数器  

必需日志：

- 结构化日志，按 `sessionKey`、`runId`、`backend`、`threadId`、`idempotencyKey` 关键字段索引  
- 显式记录会话与运行状态机的状态转换日志  
- 适配器命令日志，含参数脱敏与退出摘要  

必需诊断能力：

- `/acp sessions` 包含状态、当前活跃运行、最近错误及绑定状态  
- `/acp doctor`（或等效机制）验证后端注册状态、存储健康状况及过期绑定情况  

### 配置优先级与有效值

ACP 启用优先级：

- 账户覆盖：`channels.discord.accounts.<id>.threadBindings.spawnAcpSessions`  
- 渠道覆盖：`channels.discord.threadBindings.spawnAcpSessions`  
- 全局 ACP 门控：`acp.enabled`  
- 分发门控：`acp.dispatch.enabled`  
- 后端可用性：已注册的后端用于 `acp.backend`  

自动启用行为：  

- 当配置了 ACP（`acp.enabled=true`、`acp.dispatch.enabled=true` 或 `acp.backend=acpx`）时，插件自动启用会标记 `plugins.entries.acpx.enabled=true`，除非其被列入拒绝列表或被显式禁用  

TTL 有效值：  

- `min(session ttl, discord thread binding ttl, acp runtime ttl)`  

### 测试映射  

单元测试：  

- `src/acp/runtime/registry.test.ts`（新增）  
- `src/auto-reply/reply/dispatch-from-config.acp.test.ts`（新增）  
- `src/infra/outbound/bound-delivery-router.test.ts`（扩展 ACP 故障关闭场景）  
- `src/config/sessions/types.test.ts` 或最邻近的 session-store 测试（ACP 元数据持久化）  

集成测试：  

- `src/discord/monitor/reply-delivery.test.ts`（绑定 ACP 投递目标行为）  
- `src/discord/monitor/message-handler.preflight*.test.ts`（绑定 ACP 会话密钥路由连续性）  
- backend 包中的 acpx 插件运行时测试（服务注册/启动/停止 + 事件标准化）  

网关端到端测试：  

- `src/gateway/server.sessions.gateway-server-sessions-a.e2e.test.ts`（扩展 ACP 重置/删除生命周期覆盖范围）  
- ACP 线程轮转端到端测试，涵盖 spawn、message、stream、cancel、unfocus、restart 恢复  

### 上线防护机制  

添加独立的 ACP 分发开关：  

- `acp.dispatch.enabled` 默认为 `false`（首次发布）  
- 当该开关禁用时：  
  - ACP spawn/focus 控制命令仍可绑定会话  
  - ACP 分发路径不会激活  
  - 用户将收到明确提示：“ACP 分发已被策略禁用”  
- 在金丝雀验证通过后，后续版本中默认值可切换为 `true`  

## 命令与用户体验计划  

### 新增命令  

- `/acp spawn <agent-id> [--mode persistent|oneshot] [--thread auto|here|off]`  
- `/acp cancel [session]`  
- `/acp steer <instruction>`  
- `/acp close [session]`  
- `/acp sessions`  

### 现有命令兼容性  

- `/focus <sessionKey>` 继续支持 ACP 目标  
- `/unfocus` 保持当前语义  
- `/session idle` 和 `/session max-age` 替代旧的 TTL 覆盖机制  

## 分阶段上线  

### 第 0 阶段：ADR 与模式冻结  

- 发布 ACP 控制平面所有权及适配器边界的架构决策记录（ADR）  
- 冻结数据库模式（`acp_sessions`、`acp_runs`、`acp_bindings`、`acp_events`、`acp_delivery_checkpoint`、`acp_idempotency`）  
- 定义稳定的 ACP 错误码、事件契约及状态转换防护机制  

### 第 1 阶段：核心中控制平面基础建设  

- 实现 `AcpSessionManager` 及每会话 Actor 运行时  
- 实现 ACP SQLite 存储及事务辅助工具  
- 实现幂等性存储及重放辅助工具  
- 实现事件追加 + 投递检查点模块  
- 将 spawn/cancel/close API 以事务保证方式接入管理器  

### 第 2 阶段：核心路由与生命周期集成  

- 将线程绑定的 ACP 轮次从分发流水线路由至 ACP 管理器  
- 当 ACP 绑定/会话不变量失败时，强制执行故障关闭式路由  
- 将 reset/delete/archive/unfocus 生命周期操作与 ACP close/unbind 事务集成  
- 添加陈旧绑定检测及可选的自动解绑策略  

### 第 3 阶段：acpx 后端适配器/插件  

- 针对运行时契约（`ensureSession`、`submit`、`stream`、`cancel`、`close`）实现 `acpx` 适配器  
- 添加后端健康检查及启动/销毁注册机制  
- 将 acpx ndjson 事件标准化为 ACP 运行时事件  
- 强制执行后端超时、进程监管及重启/退避策略  

### 第 4 阶段：投递投影与渠道用户体验（优先 Discord）  

- 实现事件驱动的渠道投影，并支持检查点恢复（优先 Discord）  
- 结合限流感知刷新策略聚合流式数据块  
- 保证每次运行仅生成一条最终完成消息（精确一次）  
- 发布 `/acp spawn`、`/acp cancel`、`/acp steer`、`/acp close`、`/acp sessions`  

### 第 5 阶段：迁移与切换  

- 引入双写机制：同时写入 `SessionEntry.acp` 投影与 ACP SQLite 权威源  
- 添加针对遗留 ACP 元数据行的迁移工具  
- 将读取路径切换至 ACP SQLite 主库  
- 移除依赖缺失 `SessionEntry.acp` 的遗留回退路由  

### 第 6 阶段：加固、服务等级目标（SLO）与规模限制  

- 强制执行并发限制（全局/账户/会话）、队列策略及超时预算  
- 添加完整遥测能力、仪表盘及告警阈值  
- 进行混沌测试，验证崩溃恢复与重复投递抑制能力  
- 发布针对后端中断、数据库损坏及陈旧绑定修复的操作手册  

### 完整实现清单  

- 核心控制平面模块及测试  
- 数据库迁移及回滚方案  
- ACP 管理器 API 在分发与命令路径中的集成  
- 插件运行时桥接器中的适配器注册接口  
- acpx 适配器实现及测试  
- 支持线程的渠道投递投影逻辑（含检查点重放，优先 Discord）  
- reset/delete/archive/unfocus 生命周期钩子  
- 陈旧绑定检测器及面向运维人员的诊断能力  
- 所有新 ACP 配置项的配置校验与优先级测试  
- 运维文档及故障排查手册  

## 测试计划  

单元测试：  

- ACP 数据库事务边界（spawn/bind/enqueue 原子性、cancel、close）  
- ACP 会话与运行实例的状态机转换防护  
- 所有 ACP 命令的幂等性预留/重放语义  
- 每会话 Actor 序列化与队列排序  
- acpx 事件解析器与数据块聚合器  
- 运行时监管器重启与退避策略  
- 配置优先级与有效 TTL 计算  
- 核心 ACP 路由分支选择，以及后端/会话无效时的故障关闭行为  

集成测试：  

- 使用模拟 ACP 适配器进程，实现确定性的流式传输与 cancel 行为  
- ACP 管理器与分发模块集成，具备事务持久化能力  
- 线程绑定的入站路由至 ACP 会话密钥  
- 线程绑定的出站投递抑制父级渠道重复内容  
- 检查点重放可在投递失败后恢复，并从最后一个事件继续  
- 插件服务注册与 ACP 运行时后端的销毁流程  

网关端到端测试：  

- 使用线程 spawn ACP、交换多轮提示、unfocus  
- 网关重启（保留 ACP 数据库与绑定），继续同一会话  
- 多个线程中并发的 ACP 会话互不干扰  
- 重复命令重试（相同幂等性键）不会创建重复运行实例或回复  
- 陈旧绑定场景返回明确错误，并支持可选的安全自动清理行为  

## 风险与缓解措施  

- 过渡期间重复投递  
  - 缓解：单一目标解析器 + 幂等事件检查点  
- 高负载下运行时进程频繁启停  
  - 缓解：长期存活的每会话所有者 + 并发上限 + 退避机制  
- 插件缺失或配置错误  
  - 缓解：面向运维人员的明确错误提示 + 故障关闭式 ACP 路由（无隐式回退至普通会话路径）  
- 子代理与 ACP 门控之间的配置混淆  
  - 缓解：明确的 ACP 配置键 + 命令反馈中包含生效策略来源  
- 控制平面存储损坏或迁移缺陷  
  - 缓解：WAL 模式 + 备份/恢复钩子 + 迁移冒烟测试 + 只读回退诊断  
- Actor 死锁或邮箱饥饿  
  - 缓解：看门狗定时器 + Actor 健康探针 + 有界邮箱深度 + 拒绝遥测  

## 验收清单  

- ACP 会话 spawn 可在受支持的渠道适配器（当前为 Discord）中创建或绑定线程  
- 所有线程消息仅路由至已绑定的 ACP 会话  
- ACP 输出以相同线程身份呈现（支持流式或批量）  
- 已绑定轮次不会在父级渠道中产生重复输出  
- spawn+bind+初始入队在持久化存储中具有原子性  
- ACP 命令重试具备幂等性，不会重复创建运行实例或输出  
- cancel、close、unfocus、archive、reset 和 delete 执行确定性清理  
- 崩溃重启后保留映射关系并恢复多轮连续性  
- 并发线程绑定的 ACP 会话彼此独立运行  
- ACP 后端缺失状态产生清晰、可操作的错误提示  
- 陈旧绑定被检测并明确上报（支持可选的安全自动清理）  
- 控制平面指标与诊断能力对运维人员开放  
- 新增的单元测试、集成测试和端到端测试全部通过  

## 附录：针对当前实现的定向重构（状态）  

这些是非阻塞的后续工作，旨在当前功能集落地后持续保障 ACP 路径的可维护性。  

### 1）集中化 ACP 分发策略评估（已完成）  

- 通过 `src/acp/policy.ts` 中共享的 ACP 策略辅助函数实现  
- 分发模块、ACP 命令生命周期处理器及 ACP spawn 路径现均复用统一策略逻辑  

### 2）按子命令领域拆分 ACP 命令处理器（已完成）  

- `src/auto-reply/reply/commands-acp.ts` 现为轻量级路由层  
- 子命令行为已拆分为：  
  - `src/auto-reply/reply/commands-acp/lifecycle.ts`  
  - `src/auto-reply/reply/commands-acp/runtime-options.ts`  
  - `src/auto-reply/reply/commands-acp/diagnostics.ts`  
  - `src/auto-reply/reply/commands-acp/shared.ts` 中的共享辅助函数  

### 3）按职责拆分 ACP 会话管理器（已完成）  

- 管理器已拆分为：  
  - `src/acp/control-plane/manager.ts`（公共外观 + 单例）  
  - `src/acp/control-plane/manager.core.ts`（管理器实现）  
  - `src/acp/control-plane/manager.types.ts`（管理器类型/依赖）  
  - `src/acp/control-plane/manager.utils.ts`（标准化 + 辅助函数）  

### 4）可选的 acpx 运行时适配器清理  

- `extensions/acpx/src/runtime.ts` 可进一步拆分为：  
  - 进程执行/监管  
  - ndjson 事件解析/标准化  
  - 运行时 API 接口面（`submit`、`cancel`、`close` 等）  
- 提升可测试性，并使后端行为更易于审计