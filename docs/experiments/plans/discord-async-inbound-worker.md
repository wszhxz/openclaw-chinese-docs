---
summary: "Status and next steps for decoupling Discord gateway listeners from long-running agent turns with a Discord-specific inbound worker"
owner: "openclaw"
status: "in_progress"
last_updated: "2026-03-05"
title: "Discord Async Inbound Worker Plan"
---
# Discord 异步入站工作器方案

## 目标

通过将 Discord 入站回合（turn）异步化，消除 Discord 监听器超时这一面向用户的失败模式：

1. 网关监听器快速接收并标准化入站事件。
2. Discord 运行队列以我们当前使用的相同顺序边界为键，存储序列化的任务。
3. 工作器在 Carbon 监听器生命周期之外执行实际的智能体（agent）回合。
4. 回复在运行完成后交付回原始频道或线程。

这是针对排队的 Discord 运行在 ``channels.discord.eventQueue.listenerTimeout`` 超时时中断、而智能体运行本身仍在正常推进这一问题的长期修复方案。

## 当前状态

该方案已部分实现。

已完成事项：

- Discord 监听器超时与 Discord 运行超时现已成为两个独立配置项。
- 已接受的入站 Discord 回合被入队至 ``src/discord/monitor/inbound-worker.ts``。
- 长时间运行的回合现由工作器负责，而非 Carbon 监听器。
- 现有按路由的顺序性通过队列键得以保留。
- 已为 Discord 工作器路径提供超时回归覆盖。

通俗解释如下：

- 生产环境中的超时缺陷已修复；
- 长时间运行的回合不再因 Discord 监听器预算耗尽而意外终止；
- 工作器架构尚未最终完成。

仍缺失内容：

- ``DiscordInboundJob`` 仍仅部分标准化，且仍携带运行时活动引用；
- 命令语义（``stop``、``new``、``reset``，以及未来会话控制指令）尚未完全适配工作器原生模型；
- 工作器可观测性与运维状态支持仍极为有限；
- 尚无重启持久性保障。

## 设计动因

当前行为将完整智能体回合与监听器生命周期强绑定：

- ``src/discord/monitor/listeners.ts`` 应用超时与中止边界；
- ``src/discord/monitor/message-handler.ts`` 将排队运行保留在该边界内；
- ``src/discord/monitor/message-handler.process.ts`` 内联执行媒体加载、路由、分发、输入提示（typing）、草稿流式传输及最终回复投递。

该架构存在两大缺陷：

- 健康但耗时较长的回合可能被监听器看门狗中止；
- 即使下游运行时本可生成回复，用户也可能收不到任何响应。

提高超时阈值虽有帮助，但无法改变根本的失败模式。

## 非目标事项

- 本次迭代不重构非 Discord 渠道；
- 初期实现中不将此方案扩展为通用全渠道工作器框架；
- 暂不提取跨渠道共享的入站工作器抽象；仅在明显存在重复时共享底层基础组件；
- 初期不添加持久化崩溃恢复能力，除非为安全上线所必需；
- 本方案不变更路由选择逻辑、绑定语义或 ACP 策略。

## 当前约束

当前 Discord 处理路径仍依赖若干不应长期驻留于长期任务载荷中的运行时对象：

- Carbon ``Client``
- 原始 Discord 事件结构
- 内存中服务器历史映射表（guild history map）
- 线程绑定管理器回调函数
- 活跃的输入提示（typing）与草稿流状态

我们已将执行迁移至工作器队列，但标准化边界仍未完备。目前工作器实质上是“稍后在同一进程中、携带部分相同活跃对象执行”，而非真正仅含数据的完整任务边界。

## 目标架构

### 1. 监听器阶段

``DiscordMessageListener`` 仍为入口点，但其职责变为：

- 执行预检与策略校验；
- 将已接受输入标准化为可序列化的 ``DiscordInboundJob``；
- 将任务入队至按会话或按频道划分的异步队列；
- 一旦入队成功，立即返回 Carbon。

监听器不应再承担端到端大语言模型（LLM）回合的全生命周期管理。

### 2. 标准化任务载荷

引入一个仅含后续执行所需数据的可序列化任务描述符。

最小结构应包含：

- 路由标识
  - ``agentId``
  - ``sessionKey``
  - ``accountId``
  - ``channel``
- 投递标识
  - 目标频道 ID
  - 回复目标消息 ID
  - 如存在则包含线程 ID
- 发送方标识
  - 发送方 ID、标签、用户名、标签（tag）
- 渠道上下文
  - 服务器（guild）ID
  - 频道名称或 slug
  - 线程元数据
  - 已解析的系统提示词覆盖项
- 标准化消息正文
  - 基础文本
  - 实际生效的消息文本
  - 附件描述符或已解析的媒体引用
- 门控决策（gating decisions）
  - @提及要求判定结果
  - 命令授权判定结果
  - 如适用，则包含已绑定会话或智能体元数据

任务载荷不得包含任何活跃的 Carbon 对象或可变闭包。

当前实现状态：

- 已部分完成；
- ``src/discord/monitor/inbound-job.ts`` 已存在，并定义了工作器交接逻辑；
- 当前载荷仍包含活跃的 Discord 运行时上下文，需进一步精简。

### 3. 工作器阶段

新增专用于 Discord 的工作器运行器，负责：

- 从 ``DiscordInboundJob`` 重建回合上下文；
- 加载媒体及运行所需的其他频道元数据；
- 分发智能体回合；
- 投递最终回复载荷；
- 更新状态与诊断信息。

推荐位置：

- ``src/discord/monitor/inbound-worker.ts``
- ``src/discord/monitor/inbound-job.ts``

### 4. 排序模型

对任一路由边界，排序行为必须与当前保持一致。

推荐键值：

- 使用与 ``resolveDiscordRunQueueKey(...)`` 相同的队列键逻辑。

此举可确保既有行为不变：

- 单一绑定智能体的对话不会发生自我交错；
- 不同 Discord 频道仍可独立并行推进。

### 5. 超时模型

切换完成后，将存在两类独立的超时机制：

- 监听器超时
  - 仅覆盖标准化与入队阶段；
  - 应设置为较短时限；
- 运行超时
  - 可选、由工作器自主管理、显式声明且对用户可见；
  - 不应意外继承自 Carbon 监听器配置。

此举消除了当前“Discord 网关监听器持续存活”与“智能体运行健康”之间的隐式耦合。

## 推荐实施阶段

### 第一阶段：标准化边界

- 状态：已部分实现；
- 已完成：
  - 提取 ``buildDiscordInboundJob(...)``；
  - 添加工作器交接测试；
- 待完成：
  - 使 ``DiscordInboundJob`` 成为纯数据结构；
  - 将活跃运行时依赖项迁移至工作器自有服务，而非每个任务载荷中；
  - 停止通过拼接活跃监听器引用重建进程上下文。

### 第二阶段：内存内工作器队列

- 状态：已实现；
- 已完成：
  - 添加 ``DiscordInboundWorkerQueue``，并以已解析的运行队列键为索引；
  - 监听器改为入队任务，而非直接等待 ``processDiscordMessage(...)``；
  - 工作器在进程内、仅内存中执行任务。

这是首个功能完备的切换节点。

### 第三阶段：进程拆分

- 状态：尚未启动；
- 将投递、输入提示（typing）与草稿流式传输的所有权移交至面向工作器的适配器；
- 以工作器上下文重建替代对活跃预检上下文的直接使用；
- 如需，可暂时保留 ``processDiscordMessage(...)`` 作为外观层（facade），随后将其拆分。

### 第四阶段：命令语义适配

- 状态：尚未启动；
- 确保当工作被排队时，原生 Discord 命令仍能正确执行：

- ``stop``
- ``new``
- ``reset``
- 任何未来会话控制类命令

工作器队列必须暴露足够多的运行状态，以便命令可精准定位至活跃或已排队的回合。

### 第五阶段：可观测性与运维体验优化

- 状态：尚未启动；
- 将队列深度与活跃工作器数量指标输出至监控状态；
- 记录入队时间、启动时间、完成时间，以及超时或取消原因；
- 在日志中清晰呈现工作器自主管理的超时或投递失败。

### 第六阶段：可选持久性跟进

- 状态：尚未启动；
  仅在内存版本稳定后开展：

- 决定排队的 Discord 任务是否应在网关重启后继续存活；
- 若需支持，则持久化任务描述符与投递检查点；
- 若无需支持，则明确记录该内存内边界的显式语义。

此项应作为独立后续工作，除非重启恢复为上线前提条件。

## 文件影响

当前主要文件：

- ``src/discord/monitor/listeners.ts``
- ``src/discord/monitor/message-handler.ts``
- ``src/discord/monitor/message-handler.preflight.ts``
- ``src/discord/monitor/message-handler.process.ts``
- ``src/discord/monitor/status.ts``

当前工作器文件：

- ``src/discord/monitor/inbound-job.ts``
- ``src/discord/monitor/inbound-worker.ts``
- ``src/discord/monitor/inbound-job.test.ts``
- ``src/discord/monitor/message-handler.queue.test.ts``

后续可能涉及的文件：

- ``src/auto-reply/dispatch.ts``
- ``src/discord/monitor/reply-delivery.ts``
- ``src/discord/monitor/thread-bindings.ts``
- ``src/discord/monitor/native-command.ts``

## 当前下一步

当前紧要任务是将工作器边界由“部分实现”转为“真实完备”。

请按以下顺序执行：

1. 将活跃运行时依赖项从 ``DiscordInboundJob`` 中移出；
2. 将这些依赖项保留在 Discord 工作器实例上；
3. 将排队任务精简为纯 Discord 特定数据：
   - 路由标识；
   - 投递目标；
   - 发送方信息；
   - 标准化消息快照；
   - 门控与绑定决策；
4. 在工作器内部，仅基于该纯数据重建工作器执行上下文。

实践中意味着：

- ``client``
- ``threadBindings``
- ``guildHistories``
- ``discordRestFetch``
- 其他仅限运行时的可变句柄

均不应再驻留于每个排队任务中，而应归属工作器自身，或置于工作器自有适配器之后。

该变更落地后，下一跟进重点应为 ``stop``、``new`` 与 ``reset`` 的命令状态清理。

## 测试方案

保留现有超时复现覆盖范围：

- ``src/discord/monitor/message-handler.queue.test.ts``

新增测试项包括：

1. 监听器在入队后即返回，不等待完整回合执行完毕；
2. 按路由的排序性得到保持；
3. 不同频道仍可并发运行；
4. 回复准确投递至原始消息目的地；
5. ``stop`` 可中止当前由工作器拥有的活跃运行；
6. 工作器故障产生清晰可观测的诊断信息，且不影响后续任务执行；
7. 在工作器执行下，受 ACP 约束的 Discord 频道仍能正确路由。

## 风险与缓解措施

- 风险：命令语义偏离当前的同步行为  
  缓解措施：在同一次切换（cutover）中完成命令状态（command-state）的底层打通，而非延后实施  

- 风险：回复投递过程中丢失线程上下文或 reply-to 上下文  
  缓解措施：在 `DiscordInboundJob` 中将投递身份（delivery identity）作为一等公民（first-class）支持  

- 风险：重试或队列重启期间发生重复发送  
  缓解措施：首轮处理仅保留在内存中，或在持久化前显式添加投递幂等性（delivery idempotency）  

- 风险：迁移过程中 `message-handler.process.ts` 变得更难推理  
  缓解措施：在工作线程（worker）切换前或切换过程中，将其拆分为归一化（normalization）、执行（execution）和投递（delivery）辅助模块  

## 验收标准  

当满足以下全部条件时，该方案视为完成：  

1. Discord 监听器超时不再中止健康的长时间运行的回合（turn）。  
2. 监听器生命周期（listener lifetime）与智能体-回合生命周期（agent-turn lifetime）在代码中为两个独立概念。  
3. 现有的按会话（per-session）顺序保证得以保留。  
4. 受 ACP 约束的 Discord 频道也通过相同的工作线程路径（worker path）运行。  
5. `stop` 明确指向由工作线程（worker）拥有的运行实例（run），而非旧监听器（listener）拥有的调用栈（call stack）。  
6. 超时与投递失败变为工作线程显式的输出结果（worker outcomes），而非静默丢弃的监听器行为（silent listener drops）。  

## 后续落地策略  

以下内容将在后续 PR 中完成：  

1. 将 `DiscordInboundJob` 改为纯数据（plain-data）结构，并将运行时引用（live runtime refs）迁移至工作线程。  
2. 清理 `stop`、`new` 和 `reset` 的命令状态（command-state）所有权。  
3. 增加工作线程可观测性（worker observability）及运维状态（operator status）。  
4. 明确判断是否需要持久化能力（durability），或显式记录当前内存边界（in-memory boundary）。  

只要保持该方案仅限于 Discord 场景，且继续避免过早引入跨频道（cross-channel）工作线程抽象，此项后续工作仍属可控范围。