---
summary: "Plan: isolate browser act:evaluate from Playwright queue using CDP, with end-to-end deadlines and safer ref resolution"
read_when:
  - Working on browser `act:evaluate` timeout, abort, or queue blocking issues
  - Planning CDP based isolation for evaluate execution
owner: "openclaw"
status: "draft"
last_updated: "2026-02-10"
title: "Browser Evaluate CDP Refactor"
---
# 浏览器评估 CDP 重构计划

## 背景

``act:evaluate`` 在页面中执行用户提供的 JavaScript。今天它通过 Playwright 运行（``page.evaluate`` 或 ``locator.evaluate``）。Playwright 按页面序列化 CDP 命令，因此卡住或长时间运行的评估可能会阻塞页面命令队列，并使该标签页上的每个后续操作看起来“卡住”。

PR #13498 添加了一个实用的安全网（有界评估、中止传播和尽力而为的恢复）。本文档描述了一个更大的重构，使 ``act:evaluate`` 本质上与 Playwright 隔离，这样卡住的评估就不会阻碍正常的 Playwright 操作。

## 目标

- ``act:evaluate`` 不能永久阻塞同一标签页上后续的浏览器操作。
- 超时是端到端的单一事实来源，以便调用者可以依赖预算。
- 中止和超时在 HTTP 和进程内调度中以相同方式处理。
- 支持评估的元素定位，同时无需完全脱离 Playwright。
- 保持与现有调用者和负载的向后兼容性。

## 非目标

- 用 CDP 实现替换所有浏览器操作（点击、输入、等待等）。
- 移除 PR #13498 中引入的现有安全网（它仍然是一个有用的后备方案）。
- 引入超出现有 ``browser.evaluateEnabled`` 门控的新不安全能力。
- 为评估添加进程隔离（worker 进程/线程）。如果在此重构后我们仍看到难以恢复的卡住状态，那是后续想法。

## 当前架构（为什么会卡住）

从高层来看：

- 调用者向浏览器控制服务发送 ``act:evaluate``。
- 路由处理器调用 Playwright 来执行 JavaScript。
- Playwright 序列化页面命令，因此永远无法完成的评估会阻塞队列。
- 队列卡住意味着后续在该标签页上的点击/输入/等待操作可能看起来挂起。

## 提议的架构

### 1. 截止时间传播

引入单一的预算概念并从中派生所有内容：

- 调用者设置 ``timeoutMs``（或未来的截止时间）。
- 外部请求超时、路由处理器逻辑和页面内的执行预算都使用相同的预算，并在需要序列化开销的地方保留少量余量。
- 中止作为 ``AbortSignal`` 在所有地方传播，以便取消保持一致。

实施方向：

- 添加一个小助手（例如 ``createBudget({ timeoutMs, signal })``），返回：
  - ``signal``: 链接的 AbortSignal
  - ``deadlineAtMs``: 绝对截止时间
  - ``remainingMs()``: 子操作的剩余预算
- 在以下位置使用此助手：
  - ``src/browser/client-fetch.ts``（HTTP 和进程内调度）
  - ``src/node-host/runner.ts``（代理路径）
  - 浏览器操作实现（Playwright 和 CDP）

### 2. 独立的评估引擎（CDP 路径）

添加一个基于 CDP 的评估实现，它不共享 Playwright 的每页面命令队列。关键属性是评估传输是一个单独的 WebSocket 连接和一个附加到目标的单独 CDP 会话。

实施方向：

- 新模块，例如 ``src/browser/cdp-evaluate.ts``，它将：
  - 连接到配置的 CDP 端点（浏览器级别套接字）。
  - 使用 ``Target.attachToTarget({ targetId, flatten: true })`` 获取 ``sessionId``。
  - 运行：
    - ``Runtime.evaluate`` 用于页面级评估，或
    - ``DOM.resolveNode`` 加上 ``Runtime.callFunctionOn`` 用于元素评估。
  - 超时或中止时：
    - 为会话发送 ``Runtime.terminateExecution`` 尽力而为。
    - 关闭 WebSocket 并返回清晰的错误。

注意：

- 这仍然在页面中执行 JavaScript，所以终止可能会有副作用。优势在于它不会卡住 Playwright 队列，并且可以通过杀死 CDP 会话在传输层进行取消。

### 3. 参考故事（无需全面重写即可进行元素定位）

难点在于元素定位。CDP 需要 DOM 句柄或 ``backendDOMNodeId``，而今天大多数浏览器操作使用基于快照引用的 Playwright 定位器。

推荐方法：保留现有的 refs，但附加一个可选的 CDP 可解析 ID。

#### 3.1 扩展存储的引用信息

扩展存储的角色引用元数据以选择性地包含 CDP ID：

- 今天：``{ role, name, nth }``
- 建议：``{ role, name, nth, backendDOMNodeId?: number }``

这保持了所有现有的基于 Playwright 的操作正常工作，并允许 CDP 评估在 ``backendDOMNodeId`` 可用时接受相同的 ``ref`` 值。

#### 3.2 在快照时间填充 backendDOMNodeId

生成角色快照时：

1. 生成现有的角色引用映射（角色、名称、第 N 个）。
2. 通过 CDP 获取 AX 树（``Accessibility.getFullAXTree``）并使用相同的重复处理规则计算 ``(role, name, nth) -> backendDOMNodeId`` 的并行映射。
3. 将 ID 合并回当前标签页的存储引用信息。

如果引用的映射失败，将 ``backendDOMNodeId`` 留为未定义。这使得该功能尽力而为且安全发布。

#### 3.3 带引用的评估行为

在 ``act:evaluate`` 中：

- 如果存在 ``ref`` 并且具有 ``backendDOMNodeId``，则通过 CDP 运行元素评估。
- 如果存在 ``ref`` 但没有 ``backendDOMNodeId``，则回退到 Playwright 路径（带有安全网）。

可选的逃生舱口：

- 扩展请求形状以直接接受 ``backendDOMNodeId`` 供高级调用者（和调试）使用，同时保持 ``ref`` 为主要接口。

### 4. 保留最后手段恢复路径

即使有 CDP 评估，还有其他方法可以卡住标签页或连接。保留现有的恢复机制（终止执行 + 断开 Playwright）作为最后手段，用于：

- 遗留调用者
- CDP 附加被阻止的环境
- 意外的 Playwright 边缘情况

## 实施计划（单次迭代）

### 交付物

- 一个基于 CDP 的评估引擎，它在 Playwright 每页面命令队列之外运行。
- 一个统一的端到端超时/中止预算，由调用者和处理器一致使用。
- 可以选择携带 ``backendDOMNodeId`` 的引用元数据用于元素评估。
- ``act:evaluate`` 优先使用 CDP 引擎（如可能），否则回退到 Playwright。
- 证明卡住的评估不会阻塞后续操作的测试。
- 使故障和回退可见的日志/指标。

### 实施清单

1. 添加共享的“预算”助手以链接 ``timeoutMs`` + 上游 ``AbortSignal`` 到：
   - 单个 ``AbortSignal``
   - 绝对截止时间
   - 用于下游操作的 ``remainingMs()`` 助手
2. 更新所有调用者路径以使用该助手，使得 ``timeoutMs`` 在任何地方含义相同：
   - ``src/browser/client-fetch.ts``（HTTP 和进程内调度）
   - ``src/node-host/runner.ts``（节点代理路径）
   - 调用 ``/act`` 的 CLI 包装器（将 ``--timeout-ms`` 添加到 ``browser evaluate``）
3. 实现 ``src/browser/cdp-evaluate.ts``：
   - 连接到浏览器级别的 CDP 套接字
   - ``Target.attachToTarget`` 以获取 ``sessionId``
   - 运行 ``Runtime.evaluate`` 进行页面评估
   - 运行 ``DOM.resolveNode`` + ``Runtime.callFunctionOn`` 进行元素评估
   - 超时/中止时：尽力而为的 ``Runtime.terminateExecution`` 然后关闭套接字
4. 扩展存储的角色引用元数据以选择性地包含 ``backendDOMNodeId``：
   - 保留现有的 ``{ role, name, nth }`` 行为用于 Playwright 操作
   - 添加 ``backendDOMNodeId?: number`` 用于 CDP 元素定位
5. 在创建快照期间填充 ``backendDOMNodeId``（尽力而为）：
   - 通过 CDP 获取 AX 树（``Accessibility.getFullAXTree``）
   - 计算 ``(role, name, nth) -> backendDOMNodeId`` 并合并到存储的引用映射中
   - 如果映射不明确或缺失，将 ID 留为未定义
6. 更新 ``act:evaluate`` 路由：
   - 如果没有 ``ref``：始终使用 CDP 评估
   - 如果 ``ref`` 解析为 ``backendDOMNodeId``：使用 CDP 元素评估
   - 否则：回退到 Playwright 评估（仍有界且可中止）
7. 保留现有的“最后手段”恢复路径作为后备，而不是默认路径。
8. 添加测试：
   - 卡住的评估在预算内超时且下一次点击/输入成功
   - 中止取消评估（客户端断开连接或超时）并解锁后续操作
   - 映射失败干净地回退到 Playwright
9. 添加可观测性：
   - 评估持续时间和超时计数器
   - terminateExecution 使用情况
   - 回退率（CDP -> Playwright）及原因

### 验收标准

- 故意挂起的 ``act:evaluate`` 在调用者预算内返回，并且不会阻塞标签页以供后续操作使用。
- ``timeoutMs`` 在 CLI、代理工具、节点代理和进程内调用中表现一致。
- 如果 ``ref`` 可以映射到 ``backendDOMNodeId``，则元素评估使用 CDP；否则回退路径仍然有界且可恢复。

## 测试计划

- 单元测试：
  - ``(role, name, nth)`` 角色引用和 AX 树节点之间的匹配逻辑。
  - 预算助手行为（余量、剩余时间数学）。
- 集成测试：
  - CDP 评估超时在预算内返回且不阻塞下一个操作。
  - 中止取消评估并触发终止尽力而为。
- 契约测试：
  - 确保 ``BrowserActRequest`` 和 ``BrowserActResponse`` 保持兼容。

## 风险与缓解措施

- 映射不完美：
  - 缓解措施：尽力而为的映射，回退到 Playwright 评估，并添加调试工具。
- ``Runtime.terminateExecution`` 有副作用：
  - 缓解措施：仅在超时/中止时使用，并在错误中记录行为。
- 额外开销：
  - 缓解措施：仅在请求快照时获取 AX 树，按目标缓存，并保持 CDP 会话短生命周期。
- 扩展中继限制：
  - 缓解措施：当没有每页面套接字时使用浏览器级别附加 API，并保持当前的 Playwright 路径作为后备。

## 开放性问题

- 新引擎是否应配置为 ``playwright``、``cdp`` 或 ``auto``？
- 我们是否希望暴露新的 "nodeRef" 格式供高级用户使用，还是仅保留 ``ref``？
- 帧快照和选择器范围快照应如何参与 AX 映射？