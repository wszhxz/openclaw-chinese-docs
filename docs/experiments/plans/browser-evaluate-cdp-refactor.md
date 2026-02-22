---
summary: "Plan: isolate browser act:evaluate from Playwright queue using CDP, with end-to-end deadlines and safer ref resolution"
owner: "openclaw"
status: "draft"
last_updated: "2026-02-10"
title: "Browser Evaluate CDP Refactor"
---
# 浏览器评估 CDP 重构计划

## 上下文

`act:evaluate` 在页面中执行用户提供的 JavaScript。今天它通过 Playwright
(`page.evaluate` 或 `locator.evaluate`) 运行。Playwright 按页面序列化 CDP 命令，因此一个
卡住或长时间运行的评估可以阻塞页面命令队列，并使该标签页上的每个后续操作看起来“卡住”。

PR #13498 添加了一个实用的安全网（有界评估、中止传播和最佳努力恢复）。本文档描述了一个更大的重构，使 `act:evaluate` 本质上与 Playwright 隔离，因此卡住的评估不会阻塞正常的 Playwright 操作。

## 目标

- `act:evaluate` 不能永久阻止同一标签页上的后续浏览器操作。
- 超时是端到端的单一真实来源，因此调用者可以依赖预算。
- 中止和超时在 HTTP 和进程内分派中以相同方式处理。
- 评估的元素定位支持无需切换到 Playwright 之外。
- 维护现有调用者和负载的向后兼容性。

## 非目标

- 将所有浏览器操作（点击、输入、等待等）替换为 CDP 实现。
- 移除 PR #13498 引入的现有安全网（它仍然是有用的后备方案）。
- 引入现有 `browser.evaluateEnabled` 网关之外的新不安全功能。
- 为评估添加进程隔离（工作进程/线程）。如果在此次重构后仍然看到难以恢复的卡住状态，这是一个后续想法。

## 当前架构（为什么它会卡住）

高层次概述：

- 调用者将 `act:evaluate` 发送到浏览器控制服务。
- 路由处理器调用 Playwright 执行 JavaScript。
- Playwright 序列化页面命令，因此一个永远不会完成的评估会阻塞队列。
- 卡住的队列意味着该标签页上的后续点击/输入/等待操作可能会看起来挂起。

## 提议的架构

### 1. 截止时间传播

引入一个单一预算概念并从中推导出所有内容：

- 调用者设置 `timeoutMs`（或未来的截止时间）。
- 外部请求超时、路由处理器逻辑和页面内的执行预算都使用相同的预算，在需要的地方留有少量余量以应对序列化开销。
- 在所有地方将中止传播为 `AbortSignal` 以便取消一致。

实现方向：

- 添加一个小助手（例如 `createBudget({ timeoutMs, signal })`)，返回：
  - `signal`: 关联的 AbortSignal
  - `deadlineAtMs`: 绝对截止时间
  - `remainingMs()`: 子操作的剩余预算
- 在以下位置使用此助手：
  - `src/browser/client-fetch.ts`（HTTP 和进程内分派）
  - `src/node-host/runner.ts`（代理路径）
  - 浏览器操作实现（Playwright 和 CDP）

### 2. 分离评估引擎（CDP 路径）

添加一个基于 CDP 的评估实现，不共享 Playwright 的每页命令队列。关键属性是评估传输是一个单独的 WebSocket 连接和附加到目标的单独 CDP 会话。

实现方向：

- 新模块，例如 `src/browser/cdp-evaluate.ts`，它：
  - 连接到配置的 CDP 端点（浏览器级别套接字）。
  - 使用 `Target.attachToTarget({ targetId, flatten: true })` 获取 `sessionId`。
  - 运行以下任一项：
    - `Runtime.evaluate` 用于页面级别的评估，或
    - `DOM.resolveNode` 加上 `Runtime.callFunctionOn` 用于元素评估。
  - 在超时或中止时：
    - 对会话发送 `Runtime.terminateExecution` 最佳努力。
    - 关闭 WebSocket 并返回清晰的错误。

注意：

- 这仍然在页面中执行 JavaScript，因此终止可能有副作用。优点是它不会阻塞 Playwright 队列，并且可以通过终止 CDP 会话在传输层取消。

### 3. 示例故事（无需完全重写的目标元素定位）

困难的部分是元素定位。CDP 需要 DOM 句柄或 `backendDOMNodeId`，而今天大多数浏览器操作使用基于快照引用的 Playwright 定位器。

推荐方法：保留现有引用，但附加一个可选的 CDP 可解析 ID。

#### 3.1 扩展存储的引用信息

扩展存储的角色引用元数据以可选地包含 CDP ID：

- 今天：`{ role, name, nth }`
- 提议：`{ role, name, nth, backendDOMNodeId?: number }`

这保持了所有现有的基于 Playwright 的操作正常工作，并允许 CDP 评估接受相同的 `ref` 值当 `backendDOMNodeId` 可用时。

#### 3.2 在快照生成时填充 backendDOMNodeId

在生成角色快照时：

1. 如今天一样生成现有的角色引用映射（角色、名称、第 n 个）。
2. 通过 CDP 获取 AX 树 (`Accessibility.getFullAXTree`) 并使用相同的重复处理规则计算 `(role, name, nth) -> backendDOMNodeId` 的并行映射。
3. 将 ID 合并回当前标签页的存储引用信息中。

如果某个引用的映射失败，则将 `backendDOMNodeId` 留为未定义。这使得该功能最佳努力并且安全推出。

#### 3.3 具有引用的评估行为

在 `act:evaluate` 中：

- 如果 `ref` 存在并且具有 `backendDOMNodeId`，则通过 CDP 进行元素评估。
- 如果 `ref` 存在但没有 `backendDOMNodeId`，则回退到 Playwright 路径（带有安全网）。

可选的逃生舱：

- 扩展请求形状以直接接受 `backendDOMNodeId` 用于高级调用者（以及调试），同时保持 `ref` 作为主要接口。

### 4. 保留最后的恢复路径

即使使用 CDP 评估，还有其他方法可以卡住标签页或连接。保留现有的恢复机制（终止执行 + 断开 Playwright）作为最后的手段：

- 旧版调用者
- 阻止 CDP 附加的环境
- 不预期的 Playwright 边缘情况

## 实施计划（单次迭代）

### 交付成果

- 一个基于 CDP 的评估引擎，运行在 Playwright 每页命令队列之外。
- 调用者和处理程序一致使用的单一端到端超时/中止预算。
- 可选地携带 `backendDOMNodeId` 用于元素评估的引用元数据。
- `act:evaluate` 尽可能优先使用 CDP 引擎并在无法使用时回退到 Playwright。
- 证明卡住的评估不会阻塞后续操作的测试。
- 使故障和回退可见的日志/指标。

### 实施检查清单

1. 添加一个共享的“预算”助手，将 `timeoutMs` + 上游 `AbortSignal` 链接为：
   - 单一 `AbortSignal`
   - 绝对截止时间
   - 下游操作的 `remainingMs()` 助手
2. 更新所有调用路径以使用该助手，因此 `timeoutMs` 在任何地方都意味着相同的东西：
   - `src/browser/client-fetch.ts`（HTTP 和进程内分派）
   - `src/node-host/runner.ts`（节点代理路径）
   - 调用 `/act` 的 CLI 包装器（向 `browser evaluate` 添加 `--timeout-ms`）
3. 实现 `src/browser/cdp-evaluate.ts`：
   - 连接到浏览器级别的 CDP 套接字
   - `Target.attachToTarget` 获取 `sessionId`
   - 运行 `Runtime.evaluate` 进行页面评估
   - 运行 `DOM.resolveNode` + `Runtime.callFunctionOn` 进行元素评估
   - 在超时/中止时：最佳努力 `Runtime.terminateExecution` 然后关闭套接字
4. 扩展存储的角色引用元数据以可选地包含 `backendDOMNodeId`：
   - 为 Playwright 操作保留现有的 `{ role, name, nth }` 行为
   - 为 CDP 元素定位添加 `backendDOMNodeId?: number`
5. 在创建快照期间填充 `backendDOMNodeId`（最佳努力）：
   - 通过 CDP 获取 AX 树 (`Accessibility.getFullAXTree`)
   - 计算 `(role, name, nth) -> backendDOMNodeId` 并合并到存储的引用映射中
   - 如果映射不明确或缺失，则将 ID 留为未定义
6. 更新 `act:evaluate` 路由：
   - 如果没有 `ref`：始终使用 CDP 评估
   - 如果 `ref` 解析为 `backendDOMNodeId`：使用 CDP 元素评估
   - 否则：回退到 Playwright 评估（仍然有界且可中止）
7. 保留现有的“最后手段”恢复路径作为回退，而不是默认路径。
8. 添加测试：
   - 卡住的评估在预算内超时并且下一个点击/输入成功
   - 中止取消评估（客户端断开或超时）并解除后续操作的阻塞
   - 映射失败干净地回退到 Playwright
9. 添加可观测性：
   - 评估持续时间和超时计数器
   - terminateExecution 使用情况
   - 回退率（CDP -> Playwright）及其原因

### 接受标准

- 故意挂起的 `act:evaluate` 在调用者预算内返回并且不会阻塞后续操作的标签页。
- `timeoutMs` 在 CLI、代理工具、节点代理和进程内调用中表现一致。
- 如果 `ref` 可以映射到 `backendDOMNodeId`，则元素评估使用 CDP；否则回退路径仍然有界且可恢复。

## 测试计划

- 单元测试：
  - 角色引用和 AX 树节点之间的 `(role, name, nth)` 匹配逻辑。
  - 预算助手行为（余量、剩余时间计算）。
- 集成测试：
  - CDP 评估超时在预算内返回并且不会阻止下一个操作。
  - 中止取消评估并触发最佳努力终止。
- 合同测试：
  - 确保 `BrowserActRequest` 和 `BrowserActResponse` 保持兼容。

## 风险及缓解措施

- 映射不完美：
  - 缓解措施：最佳努力映射，回退到 Playwright 评估，并添加调试工具。
- `Runtime.terminateExecution` 有副作用：
  - 缓解措施：仅在超时/中止时使用，并在错误中记录行为。
- 额外开销：
  - 缓解措施：仅在请求快照时获取 AX 树，按目标缓存，并保持 CDP 会话短生命周期。
- 扩展中继限制：
  - 缓解措施：在每页套接字不可用时使用浏览器级别的附加 API，并保持当前的 Playwright 路径作为回退。

## 开放问题

- 新引擎应配置为 `playwright`、`cdp` 还是 `auto`？
- 是否要为高级用户公开新的“nodeRef”格式，还是仅保留 `ref`？
- 框架快照和选择器范围快照如何参与 AX 映射？