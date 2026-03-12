---
summary: "Production plan for reliable interactive process supervision (PTY + non-PTY) with explicit ownership, unified lifecycle, and deterministic cleanup"
read_when:
  - Working on exec/process lifecycle ownership and cleanup
  - Debugging PTY and non-PTY supervision behavior
owner: "openclaw"
status: "in-progress"
last_updated: "2026-02-15"
title: "PTY and Process Supervision Plan"
---
# PTY 与进程监管计划

## 1. 问题与目标

我们需要为长期运行的命令执行提供统一且可靠的生命周期管理，覆盖以下场景：

- `exec` 前台运行  
- `exec` 后台运行  
- `process` 后续操作（`poll`、`log`、`send-keys`、`paste`、`submit`、`kill`、`remove`）  
- CLI agent runner 子进程  

目标不仅限于支持 PTY。核心目标是实现可预测的所有权归属、取消、超时与清理机制，杜绝任何不安全的进程匹配启发式逻辑。

## 2. 范围与边界

- 将实现严格限定在 `src/process/supervisor` 内部。  
- 不为此新建独立包。  
- 在切实可行的前提下保持现有行为兼容性。  
- 不将范围扩展至终端回放（terminal replay）或类似 tmux 的会话持久化功能。

## 3. 本分支中已实现的内容

### 监管器基线已就位

- 监管器模块已置于 `src/process/supervisor/*` 下。  
- Exec 运行时与 CLI 运行器均已通过监管器的 `spawn` 与 `wait` 接口路由。  
- 注册表终结（registry finalization）具备幂等性。

### 本次迭代已完成事项

1. 明确的 PTY 命令契约  

- `SpawnInput` 现已成为 `src/process/supervisor/types.ts` 中的可区分联合类型（discriminated union）。  
- PTY 运行必须使用 `ptyCommand`，不得复用通用的 `argv`。  
- 监管器不再于 `src/process/supervisor/supervisor.ts` 中通过拼接 `argv` 字符串重建 PTY 命令。  
- Exec 运行时现于 `src/agents/bash-tools.exec-runtime.ts` 中直接传递 `ptyCommand`。

2. 进程层类型解耦  

- 监管器类型不再从 agents 中导入 `SessionStdin`。  
- 进程本地 stdin 契约定义于 `src/process/supervisor/types.ts`（`ManagedRunStdin`）。  
- 适配器（adapters）现仅依赖进程层级类型：  
  - `src/process/supervisor/adapters/child.ts`  
  - `src/process/supervisor/adapters/pty.ts`  

3. 进程工具生命周期所有权改进  

- `src/agents/bash-tools.process.ts` 现优先通过监管器发起取消请求。  
- `process kill/remove` 在监管器查找失败时，改用进程树（process-tree）回退终止机制。  
- `remove` 通过在请求终止后立即移除运行中会话条目，维持确定性的移除行为。

4. 单一来源的看门狗（watchdog）默认值  

- 在 `src/agents/cli-watchdog-defaults.ts` 中新增共享默认值。  
- `src/agents/cli-backends.ts` 消费该共享默认值。  
- `src/agents/cli-runner/reliability.ts` 同样消费同一套共享默认值。

5. 清理废弃辅助函数  

- 从 `src/agents/bash-tools.shared.ts` 中移除了未使用的 `killSession` 辅助函数路径。

6. 新增直连监管器路径测试  

- 新增 `src/agents/bash-tools.process.supervisor.test.ts`，覆盖经由监管器取消机制触发的 `kill` 与 `remove` 路由。

7. 可靠性缺陷修复完成  

- `src/agents/bash-tools.process.ts` 在监管器查找失败时，现回退至真实的 OS 级进程终止。  
- `src/process/supervisor/adapters/child.ts` 对默认取消/超时 kill 路径采用进程树终止语义。  
- 在 `src/process/kill-tree.ts` 中新增共享的进程树工具（process-tree utility）。

8. PTY 契约边缘情况覆盖增强  

- 新增 `src/process/supervisor/supervisor.pty-command.test.ts`，用于验证 PTY 命令的逐字转发及空命令拒绝行为。  
- 新增 `src/process/supervisor/adapters/child.test.ts`，用于验证子适配器（child adapter）取消时的进程树 kill 行为。

## 4. 待解决缺口与决策事项

### 可靠性状态

本次迭代所要求的两项可靠性缺口现已关闭：

- `process kill/remove` 在监管器查找失败时，已具备真实的 OS 终止回退能力。  
- 子进程取消/超时现对默认 kill 路径采用进程树 kill 语义。  
- 已为上述两种行为新增回归测试（regression tests）。

### 持久性与启动协调

重启行为现明确定义为仅内存生命周期（in-memory lifecycle only）。

- `reconcileOrphans()` 在 `src/process/supervisor/supervisor.ts` 中按设计保持空操作（no-op）。  
- 进程重启后，不会恢复任何活跃运行任务。  
- 此边界设定属本实现迭代的有意取舍，旨在规避部分持久化（partial persistence）风险。

### 可维护性后续事项

1. `runExecProcess` 在 `src/agents/bash-tools.exec-runtime.ts` 中仍承担多项职责，可在后续迭代中拆分为专注单一职责的辅助函数。

## 5. 实施计划

针对必需的可靠性与契约项的实施迭代已完成。

已完成：

- `process kill/remove` 回退至真实终止机制  
- 子适配器默认 kill 路径采用进程树取消机制  
- 针对回退 kill 与子适配器 kill 路径的回归测试  
- 在明确的 `ptyCommand` 下新增 PTY 命令边缘情况测试  
- 明确的内存内重启边界，且 `reconcileOrphans()` 按设计为空操作  

可选后续事项：

- 将 `runExecProcess` 拆分为多个专注单一职责的辅助函数，确保无行为漂移（no behavior drift）

## 6. 文件映射

### 进程监管器

- `src/process/supervisor/types.ts` 已更新，支持可区分的 spawn 输入及进程本地 stdin 契约。  
- `src/process/supervisor/supervisor.ts` 已更新以显式使用 `ptyCommand`。  
- `src/process/supervisor/adapters/child.ts` 与 `src/process/supervisor/adapters/pty.ts` 已与 agent 层类型解耦。  
- `src/process/supervisor/registry.ts` 的幂等终结逻辑保持不变并予以保留。

### Exec 与进程集成

- `src/agents/bash-tools.exec-runtime.ts` 已更新，显式传递 PTY 命令并保留回退路径。  
- `src/agents/bash-tools.process.ts` 已更新，通过监管器取消，并启用真实的进程树回退终止。  
- `src/agents/bash-tools.shared.ts` 中已移除直接 kill 辅助函数路径。

### CLI 可靠性

- `src/agents/cli-watchdog-defaults.ts` 已作为共享基线新增。  
- `src/agents/cli-backends.ts` 与 `src/agents/cli-runner/reliability.ts` 现消费同一套默认值。

## 7. 本次迭代的验证运行

单元测试（Unit tests）：

- `pnpm vitest src/process/supervisor/registry.test.ts`  
- `pnpm vitest src/process/supervisor/supervisor.test.ts`  
- `pnpm vitest src/process/supervisor/supervisor.pty-command.test.ts`  
- `pnpm vitest src/process/supervisor/adapters/child.test.ts`  
- `pnpm vitest src/agents/cli-backends.test.ts`  
- `pnpm vitest src/agents/bash-tools.exec.pty-cleanup.test.ts`  
- `pnpm vitest src/agents/bash-tools.process.poll-timeout.test.ts`  
- `pnpm vitest src/agents/bash-tools.process.supervisor.test.ts`  
- `pnpm vitest src/process/exec.test.ts`  

端到端测试（E2E targets）：

- `pnpm vitest src/agents/cli-runner.test.ts`  
- `pnpm vitest run src/agents/bash-tools.exec.pty-fallback.test.ts src/agents/bash-tools.exec.background-abort.test.ts src/agents/bash-tools.process.send-keys.test.ts`  

类型检查说明（Typecheck note）：

- 本仓库中请使用 `pnpm build`（完整 lint/docs 门禁则使用 `pnpm check`）。此前提及 `pnpm tsgo` 的旧说明已过时。

## 8. 保留的运行保障

- Exec 环境加固行为保持不变。  
- 审批（approval）与白名单（allowlist）流程保持不变。  
- 输出净化（output sanitization）与输出上限（output caps）保持不变。  
- PTY 适配器仍保证：在强制 kill 和监听器（listener）释放时，均能完成 `wait` 的最终结算（wait settlement）。

## 9. 完成定义（Definition of done）

1. 监管器是受管运行（managed runs）的生命周期所有者。  
2. PTY spawn 使用显式命令契约，不进行 `argv` 重建。  
3. 进程层对监管器 stdin 契约不依赖 agent 层类型。  
4. 看门狗（watchdog）默认值为单一信源。  
5. 目标单元测试与端到端测试持续通过（remain green）。  
6. 重启持久性边界已明确文档化或完全实现。

## 10. 总结

本分支现已具备一致且更安全的监管形态：

- 显式的 PTY 契约  
- 更清晰的进程分层结构  
- 由监管器驱动的进程操作取消路径  
- 监管器查找失败时的真实回退终止机制  
- 子运行（child-run）默认 kill 路径采用进程树取消机制  
- 统一的看门狗默认值  
- 明确的内存内重启边界（本迭代中不跨重启进行孤儿进程协调）