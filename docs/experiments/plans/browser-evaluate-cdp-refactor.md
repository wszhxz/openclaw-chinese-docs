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
# 浏览器 Evaluate CDP 重构计划

## 背景

`act:evaluate` 在页面中执行用户提供的 JavaScript。当前它通过 Playwright（`page.evaluate` 或 `locator.evaluate`）运行。Playwright 按页面序列化 CDP 命令，因此一个卡住或长时间运行的 evaluate 会阻塞该页面的命令队列，导致后续在该标签页上的所有操作看起来都“卡住”。

PR #13498 引入了一个务实的安全网（带时限的 evaluate、中止传播、尽力恢复）。本文档描述了一项更大规模的重构，使 `act:evaluate` 与 Playwright 天然隔离，从而避免卡住的 evaluate 拖累正常的 Playwright 操作。

## 目标

- `act:evaluate` 不得永久阻塞同一标签页上后续的浏览器操作。
- 超时是端到端唯一的事实来源，调用方可以依赖统一的时间预算。
- 中止（abort）和超时（timeout）在 HTTP 和进程内分发路径中被一致处理。
- evaluate 的元素定位功能得到支持，且无需将全部逻辑从 Playwright 迁移。
- 维持对现有调用方及有效载荷的向后兼容性。

## 非目标

- 不以 CDP 实现全面替代所有浏览器操作（如 click、type、wait 等）。
- 不移除 PR #13498 中引入的现有安全网（它仍是一个有用的备用方案）。
- 不在现有 `browser.evaluateEnabled` 闸门之外引入新的不安全能力。
- 不为 evaluate 引入进程隔离（工作进程/线程）。若本次重构后仍出现难以恢复的卡死状态，这将作为后续议题考虑。

## 当前架构（为何会卡住）

高层视角如下：

- 调用方向浏览器控制服务发送 `act:evaluate`。
- 路由处理器调用 Playwright 执行 JavaScript。
- Playwright 对页面命令进行串行化，因此一个永不结束的 evaluate 将阻塞命令队列。
- 卡住的队列意味着后续在该标签页上的 click/type/wait 等操作可能表现为挂起。

## 提议的架构

### 1. 截止时间（Deadline）传播

引入单一预算概念，并从中派生所有相关行为：

- 调用方设置 `timeoutMs`（或未来的截止时间）。
- 外层请求超时、路由处理器逻辑以及页面内部执行预算均使用同一预算，仅在必要时为序列化开销预留少量余量。
- 中止（abort）在各处均以 `AbortSignal` 形式传播，确保取消行为的一致性。

实现方向：

- 添加一个轻量级辅助函数（例如 `createBudget({ timeoutMs, signal })`），返回：
  - `signal`：关联的 AbortSignal
  - `deadlineAtMs`：绝对截止时间
  - `remainingMs()`：子操作剩余预算
- 在以下位置使用该辅助函数：
  - `src/browser/client-fetch.ts`（HTTP 和进程内分发）
  - `src/node-host/runner.ts`（代理路径）
  - 浏览器操作实现（Playwright 和 CDP）

### 2. 独立的 Evaluate 引擎（CDP 路径）

新增一个基于 CDP 的 evaluate 实现，该实现不共享 Playwright 的每页命令队列。关键特性在于：evaluate 的传输通道是一条独立的 WebSocket 连接，并附属于目标页面的独立 CDP 会话。

实现方向：

- 新建模块（例如 `src/browser/cdp-evaluate.ts`），其功能包括：
  - 连接到配置的 CDP 端点（浏览器级 socket）。
  - 使用 `Target.attachToTarget({ targetId, flatten: true })` 获取一个 `sessionId`。
  - 执行以下任一操作：
    - `Runtime.evaluate` 用于页面级 evaluate；
    - `DOM.resolveNode` 加 `Runtime.callFunctionOn` 用于元素级 evaluate。
  - 在超时或中止时：
    - 尽力向该会话发送 `Runtime.terminateExecution`；
    - 关闭 WebSocket 并返回明确错误。

说明：

- 此方式仍在页面中执行 JavaScript，因此终止操作可能产生副作用。其优势在于：不会卡住 Playwright 队列，且可在传输层通过关闭 CDP 会话实现可取消性。

### 3. 迁移策略（无需全面重写即可支持元素定位）

难点在于元素定位。CDP 需要 DOM 句柄或 `backendDOMNodeId`，而当前大多数浏览器操作使用基于快照引用的 Playwright 定位器。

推荐方法：保留现有引用，但为其附加一个可选的、CDP 可解析的 ID。

#### 3.1 扩展已存储的引用信息

扩展已存储的角色引用元数据，使其可选地包含 CDP ID：

- 当前格式：`{ role, name, nth }`
- 提议格式：`{ role, name, nth, backendDOMNodeId?: number }`

此举可确保所有现有基于 Playwright 的操作继续正常工作，并允许 CDP evaluate 在 `backendDOMNodeId` 可用时接受相同的 `ref` 值。

#### 3.2 在快照生成时填充 backendDOMNodeId

生成角色快照时：

1. 按当前方式生成角色引用映射（role、name、nth）。
2. 通过 CDP（`Accessibility.getFullAXTree`）获取 AX 树，并按相同去重规则计算并行的 `(role, name, nth) -> backendDOMNodeId` 映射。
3. 将该 ID 合并回当前标签页所存储的引用信息中。

若某引用映射失败，则保持 `backendDOMNodeId` 为 undefined。此设计使该功能为尽力而为（best-effort），且可安全灰度发布。

#### 3.3 带引用的 Evaluate 行为

在 `act:evaluate` 中：

- 若 `ref` 存在且含 `backendDOMNodeId`，则通过 CDP 执行元素级 evaluate。
- 若 `ref` 存在但不含 `backendDOMNodeId`，则回退至 Playwright 路径（仍启用安全网）。

可选逃生舱口（escape hatch）：

- 扩展请求结构，支持高级调用方（及调试用途）直接传入 `backendDOMNodeId`，同时保持 `ref` 为主要接口。

### 4. 保留最终兜底恢复路径

即使采用 CDP evaluate，仍存在其他导致标签页或连接卡死的方式。因此，应保留现有恢复机制（终止执行 + 断开 Playwright 连接）作为最终兜底方案，适用于：

- 遗留调用方
- CDP attach 被屏蔽的环境
- 意外的 Playwright 边界情况

## 实施计划（单次迭代）

### 交付成果

- 一个基于 CDP 的 evaluate 引擎，运行于 Playwright 每页命令队列之外。
- 一个统一的端到端超时/中止预算，在调用方与处理器中一致使用。
- 可选携带 `backendDOMNodeId` 的引用元数据，用于元素级 evaluate。
- `act:evaluate` 在可行时优先使用 CDP 引擎，不可行时回退至 Playwright。
- 验证卡住的 evaluate 不会阻碍后续操作的测试用例。
- 使失败与回退行为可见的日志/指标。

### 实施检查清单

1. 添加共享的“预算”辅助函数，将 `timeoutMs` + 上游 `AbortSignal` 统一整合为：
   - 单一 `AbortSignal`
   - 绝对截止时间
   - 供下游操作使用的 `remainingMs()` 辅助函数
2. 更新所有调用路径，统一使用该辅助函数，确保 `timeoutMs` 在各处语义一致：
   - `src/browser/client-fetch.ts`（HTTP 和进程内分发）
   - `src/node-host/runner.ts`（Node 代理路径）
   - 调用 `/act` 的 CLI 封装器（向 `--timeout-ms` 添加 `browser evaluate`）
3. 实现 `src/browser/cdp-evaluate.ts`：
   - 连接浏览器级 CDP socket
   - 使用 `Target.attachToTarget` 获取 `sessionId`
   - 执行 `Runtime.evaluate` 实现页面级 evaluate
   - 执行 `DOM.resolveNode` + `Runtime.callFunctionOn` 实现元素级 evaluate
   - 在超时/中止时：尽力执行 `Runtime.terminateExecution`，随后关闭 socket
4. 扩展已存储的角色引用元数据，使其可选包含 `backendDOMNodeId`：
   - 保留现有 `{ role, name, nth }` 行为以支持 Playwright 操作
   - 新增 `backendDOMNodeId?: number` 以支持 CDP 元素定位
5. 在快照创建期间（尽力而为）填充 `backendDOMNodeId`：
   - 通过 CDP（`Accessibility.getFullAXTree`）获取 AX 树
   - 计算 `(role, name, nth) -> backendDOMNodeId` 并合并进已存储的引用映射
   - 若映射存在歧义或缺失，则保持该 ID 为 undefined
6. 更新 `act:evaluate` 路由逻辑：
   - 若无 `ref`：始终使用 CDP evaluate
   - 若 `ref` 可解析为 `backendDOMNodeId`：使用 CDP 元素级 evaluate
   - 否则：回退至 Playwright evaluate（仍受时限约束且可中止）
7. 将现有“最终兜底”恢复路径保留为备用方案，而非默认路径。
8. 添加测试：
   - 卡住的 evaluate 在预算内超时，且后续 click/type 成功执行
   - 中止（客户端断连或超时）可取消 evaluate 并解除后续操作阻塞
   - 映射失败时能干净地回退至 Playwright
9. 添加可观测性能力：
   - evaluate 执行时长与超时计数器
   - terminateExecution 使用统计
   - 回退率（CDP → Playwright）及其原因

### 接受标准

- 故意挂起的 `act:evaluate` 在调用方设定的预算内返回，且不会导致标签页后续操作卡住。
- `timeoutMs` 在 CLI、Agent 工具、Node 代理及进程内调用中行为一致。
- 若 `ref` 可映射为 `backendDOMNodeId`，则元素级 evaluate 使用 CDP；否则回退路径仍受时限约束且可恢复。

## 测试计划

- 单元测试：
  - 角色引用与 AX 树节点之间的 `(role, name, nth)` 匹配逻辑。
  - 预算辅助函数行为（余量计算、剩余时间运算）。
- 集成测试：
  - CDP evaluate 超时在预算内返回，且不阻塞下一次操作。
  - 中止可取消 evaluate 并尽力触发终止。
- 合约测试（Contract tests）：
  - 确保 `BrowserActRequest` 和 `BrowserActResponse` 保持兼容性。

## 风险与缓解措施

- 映射不完美：
  - 缓解：采用尽力而为映射、回退至 Playwright evaluate，并添加调试工具。
- `Runtime.terminateExecution` 具有副作用：
  - 缓解：仅在超时/中止时使用，并在错误信息中明确记录该行为。
- 额外开销：
  - 缓解：仅在请求快照时获取 AX 树、按目标缓存、保持 CDP 会话生命周期短暂。
- 扩展中继（extension relay）限制：
  - 缓解：当每页 socket 不可用时，使用浏览器级 attach API；并将当前 Playwright 路径保留为回退方案。

## 待解决问题

- 新引擎是否应配置为 `playwright`、`cdp` 或 `auto`？
- 是否需为高级用户暴露新的 “nodeRef” 格式，还是仅保留 `ref`？
- 框架快照（frame snapshots）与选择器作用域快照（selector scoped snapshots）应如何参与 AX 映射？