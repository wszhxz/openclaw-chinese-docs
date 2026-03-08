---
summary: "Status and next steps for decoupling Discord gateway listeners from long-running agent turns with a Discord-specific inbound worker"
owner: "openclaw"
status: "in_progress"
last_updated: "2026-03-05"
title: "Discord Async Inbound Worker Plan"
---
# Discord 异步入站工作者计划

## 目标

通过将 Discord 入站回合设为异步，消除 Discord 监听器超时作为用户可见的故障模式：

1. 网关监听器快速接收并标准化入站事件。
2. Discord 运行队列存储序列化的任务，键值使用我们今天使用的相同排序边界。
3. 工作者在 Carbon 监听器生命周期之外执行实际的代理回合。
4. 运行完成后，回复被发送回原始频道或线程。

这是解决 `channels.discord.eventQueue.listenerTimeout` 处排队 Discord 运行超时的长期修复方案，而代理运行本身仍在进行中。

## 当前状态

本计划已部分实施。

已完成：

- Discord 监听器超时和 Discord 运行超时现在是独立的设置。
- 接受的 Discord 入站回合被排队到 `src/discord/monitor/inbound-worker.ts` 中。
- 工作者现在拥有长运行的回合，而不是 Carbon 监听器。
- 现有的每路由排序通过队列键得以保留。
- 存在针对 Discord 工作者路径的超时回归覆盖。

用通俗语言解释这意味着：

- 生产环境的超时 bug 已修复
- 长运行的回合不再仅仅因为 Discord 监听器预算过期而死亡
- 工作者架构尚未完成

仍缺失的内容：

- `DiscordInboundJob` 仍然只是部分标准化，并且仍携带实时运行时引用
- 命令语义 (`stop`, `new`, `reset`, 未来的会话控制) 尚未完全成为工作者原生
- 工作者可观测性和操作员状态仍然很少
- 仍然没有重启持久性

## 存在原因

当前行为将完整的代理回合绑定到监听器生命周期：

- `src/discord/monitor/listeners.ts` 应用超时和中止边界。
- `src/discord/monitor/message-handler.ts` 将该排队的运行保持在边界内。
- `src/discord/monitor/message-handler.process.ts` 执行媒体加载、路由、调度、输入、草稿流式和最终回复交付的内联操作。

该架构有两个不良特性：

- 长但健康的回合可能被监听器看门狗中止
- 即使下游运行时本应产生回复，用户也可能看不到回复

提高超时时间有所帮助，但不会改变故障模式。

## 非目标

- 在此轮次中不要重新设计非 Discord 频道。
- 不要在首次实施中将其扩展为通用的全通道工作者框架。
- 暂时不要提取共享的跨通道入站工作者抽象；仅在重复明显时共享低级原语。
- 除非需要安全落地，否则不要在首轮中添加持久的崩溃恢复。
- 不要在此计划中更改路由选择、绑定语义或 ACP 策略。

## 当前约束

当前的 Discord 处理路径仍依赖于一些不应保留在长期作业负载中的运行时对象：

- Carbon `Client`
- 原始 Discord 事件形状
- 内存中的 Guild 历史映射
- 线程绑定管理器回调
- 实时输入和草稿流状态

我们已将执行移至工作者队列，但标准化边界仍不完整。目前工作者是“在同一进程中稍后运行，并使用部分相同的运行时对象”，而不是完全的数据仅作业边界。

## 目标架构

### 1. 监听器阶段

``DiscordMessageListener`` 仍然是入口点，但其职责变为：

- 运行预检和政策检查
- 将接受的输入标准化为可序列化的 `DiscordInboundJob`
- 将任务排队到每会话或每频道的异步队列中
- 一旦排队成功，立即返回给 Carbon

监听器不再拥有端到端 LLM 回合的生命周期。

### 2. 标准化作业负载

引入一个可序列化的作业描述符，仅包含后续运行回合所需的数据。

最小形状：

- 路由身份
  - `agentId`
  - `sessionKey`
  - `accountId`
  - `channel`
- 交付身份
  - 目标频道 id
  - 回复目标消息 id
  - 如果存在则包含线程 id
- 发送者身份
  - 发送者 id、标签、用户名、标签
- 频道上下文
  - Guild id
  - 频道名称或 slug
  - 线程元数据
  - 解析的系统提示覆盖
- 标准化的消息正文
  - 基础文本
  - 有效消息文本
  - 附件描述符或解析的媒体引用
- 门控决策
  - @提及要求结果
  - 命令授权结果
  - 如果适用则包含绑定的会话或代理元数据

作业负载不得包含实时 Carbon 对象或可变闭包。

当前实施状态：

- 部分完成
- `src/discord/monitor/inbound-job.ts` 存在并定义了工作者交接
- 负载仍包含实时 Discord 运行时上下文，应进一步减少

### 3. 工作者阶段

添加专用的 Discord 工作者运行器，负责：

- 从 `DiscordInboundJob` 重建回合上下文
- 加载媒体和运行所需的任何其他频道元数据
- 调度代理回合
- 交付最终回复负载
- 更新状态和诊断

推荐位置：

- `src/discord/monitor/inbound-worker.ts`
- `src/discord/monitor/inbound-job.ts`

### 4. 排序模型

对于给定的路由边界，排序必须保持与今天等效。

推荐键：

- 使用与 `resolveDiscordRunQueueKey(...)` 相同的队列键逻辑

这保留了现有行为：

- 一个绑定的代理对话不会与其自身交错
- 不同的 Discord 频道仍然可以独立进展

### 5. 超时模型

切换后，有两种独立的超时类别：

- 监听器超时
  - 仅涵盖标准化和排队
  - 应该很短
- 运行超时
  - 可选，由工作者拥有，明确且用户可见
  - 不应意外继承自 Carbon 监听器设置

这消除了当前“Discord 网关监听器存活”与“代理运行健康”之间的意外耦合。

## 建议的实施阶段

### 第一阶段：标准化边界

- 状态：部分实施
- 已完成：
  - 提取了 `buildDiscordInboundJob(...)`
  - 添加了工作者交接测试
- 剩余：
  - 使 `DiscordInboundJob` 仅为纯数据
  - 将实时运行时依赖项移至工作者拥有的服务，而不是每作业负载
  - 停止通过将实时监听器引用拼接回作业来重建进程上下文

### 第二阶段：内存工作者队列

- 状态：已实施
- 已完成：
  - 添加了按解析运行队列键分组的 `DiscordInboundWorkerQueue`
  - 监听器排队任务而不是直接等待 `processDiscordMessage(...)`
  - 工作者在进程内、仅内存中执行任务

这是第一个功能切换。

### 第三阶段：进程拆分

- 状态：未开始
- 将交付、输入和草稿流式的所有权移至工作者面向的适配器后面。
- 用工作者上下文重建替换对实时预检上下文的直接使用。
- 如果需要，暂时保留 `processDiscordMessage(...)` 作为外观层，然后进行拆分。

### 第四阶段：命令语义

- 状态：未开始
确保当工作排队时，原生 Discord 命令仍能正确行为：

- `stop`
- `new`
- `reset`
- 任何未来的会话控制命令

工作者队列必须暴露足够的运行状态，以便命令可以针对活动或排队的回合。

### 第五阶段：可观测性和操作员体验

- 状态：未开始
- 将队列深度和活动工作者计数发射到监控状态
- 记录排队时间、开始时间、结束时间以及超时或取消原因
- 在工作日志中清楚地显示工作者拥有的超时或交付失败

### 第六阶段：可选的持久性后续

- 状态：未开始
仅在内存版本稳定后：

- 决定排队的 Discord 作业是否应 survive 网关重启
- 如果是，则持久化作业描述符和交付检查点
- 如果不是，则记录明确的内存边界

除非需要重启恢复才能落地，否则这应该是单独的后续步骤。

## 文件影响

当前主要文件：

- `src/discord/monitor/listeners.ts`
- `src/discord/monitor/message-handler.ts`
- `src/discord/monitor/message-handler.preflight.ts`
- `src/discord/monitor/message-handler.process.ts`
- `src/discord/monitor/status.ts`

当前工作者文件：

- `src/discord/monitor/inbound-job.ts`
- `src/discord/monitor/inbound-worker.ts`
- `src/discord/monitor/inbound-job.test.ts`
- `src/discord/monitor/message-handler.queue.test.ts`

接下来可能涉及的点：

- `src/auto-reply/dispatch.ts`
- `src/discord/monitor/reply-delivery.ts`
- `src/discord/monitor/thread-bindings.ts`
- `src/discord/monitor/native-command.ts`

## 下一步行动

下一步是将工作者边界变为真实而非部分实现。

接下来做：

1. 将实时运行时依赖项移出 `DiscordInboundJob`
2. 将这些依赖项保留在 Discord 工作者实例上
3. 将排队作业简化为纯 Discord 特定数据：
   - 路由身份
   - 交付目标
   - 发送者信息
   - 标准化消息快照
   - 门控和绑定决策
4. 在工作内部从该纯数据重建工作者执行上下文

实际上，这意味着：

- `client`
- `threadBindings`
- `guildHistories`
- `discordRestFetch`
- 其他仅运行时可变句柄

应停止驻留在每个排队作业上，而是驻留在工作者自身或工作者拥有的适配器后面。

在那之后落地，下一个后续步骤应该是针对 `stop`, `new`, 和 `reset` 的命令状态清理。

## 测试计划

保留现有的超时重现覆盖范围在：

- `src/discord/monitor/message-handler.queue.test.ts`

添加新测试用于：

1. 监听器在排队后返回而不等待完整回合
2. 保留每路由排序
3. 不同频道仍然并发运行
4. 回复被发送到原始消息目的地
5. `stop` 取消活动的 workers 拥有的运行
6. 工作者失败产生可见的诊断而不会阻塞后续作业
7. ACP 绑定的 Discord 频道在工作执行下仍然正确路由

## 风险和缓解措施

- 风险：command semantics 从当前 synchronous behavior 中发生 drift
  缓解措施：在同一个 cutover 中 land command-state plumbing，而不是稍后

- 风险：reply delivery 丢失 thread 或 reply-to context
  缓解措施：在 `DiscordInboundJob` 中将 delivery identity 作为 first-class

- 风险：retries 或 queue restarts 期间的 duplicate sends
  缓解措施：仅将 first pass 保留在 in-memory，或在 persistence 之前添加明确的 delivery idempotency

- 风险：migration 期间 `message-handler.process.ts` 变得更难 reason about
  缓解措施：在 worker cutover 之前或期间将其拆分为 normalization、execution 和 delivery helpers

## 验收标准

计划完成时：

1. Discord listener timeout 不再中止健康的 long-running turns。
2. Listener lifetime 和 agent-turn lifetime 在代码中是分离的概念。
3. 现有的 per-session ordering 得以保留。
4. ACP-bound Discord channels 通过相同的 worker path 工作。
5. `stop` 指向 worker-owned run 而不是旧的 listener-owned call stack。
6. Timeout and delivery failures 成为明确的 worker outcomes，而不是静默的 listener drops。

## 剩余落地策略

在后续的 PR 中完成此项：

1. 使 `DiscordInboundJob` 仅为 plain-data，并将 live runtime refs 移至 worker
2. 清理 `stop`、`new` 和 `reset` 的 command-state ownership
3. 添加 worker observability 和 operator status
4. 决定是否需要 durability，或明确记录 in-memory boundary

如果保持 Discord-only 并且我们继续避免过早的 cross-channel worker abstraction，这仍然是一个受限的 follow-up。