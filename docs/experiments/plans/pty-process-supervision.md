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

我们需要一个可靠的生命周期，用于跨以下场景的长运行命令执行：

- `exec` 前台运行
- `exec` 后台运行
- `process` 后续操作 (`poll`, `log`, `send-keys`, `paste`, `submit`, `kill`, `remove`)
- CLI 代理运行器子进程

目标不仅仅是支持 PTY。目标是可预测的所有权、取消、超时和清理，且无需不安全的进程匹配启发式规则。

## 2. 范围与边界

- 将实现保持在 `src/process/supervisor` 内部。
- 不要为此创建新包。
- 在可行的情况下保持当前行为兼容性。
- 不要将范围扩大到终端回放或 tmux 风格的会话持久化。

## 3. 本分支已实现内容

### 监管基线已存在

- 监管模块已位于 `src/process/supervisor/*` 下。
- 执行运行时和 CLI 运行器已通过监管器的 spawn 和 wait 路由。
- 注册表最终化是幂等的。

### 本次迭代完成

1. 显式 PTY 命令契约

- `SpawnInput` 现在在 `src/process/supervisor/types.ts` 中是一个区分联合。
- PTY 运行需要 `ptyCommand` 而不是重用通用的 `argv`。
- 监管器不再在 `src/process/supervisor/supervisor.ts` 中从 argv joins 重建 PTY 命令字符串。
- 执行运行时现在在 `src/agents/bash-tools.exec-runtime.ts` 中直接传递 `ptyCommand`。

2. 进程层类型解耦

- 监管器类型不再从 agents 导入 `SessionStdin`。
- 进程本地 stdin 契约位于 `src/process/supervisor/types.ts` (`ManagedRunStdin`)。
- 适配器现在仅依赖于进程级类型：
  - `src/process/supervisor/adapters/child.ts`
  - `src/process/supervisor/adapters/pty.ts`

3. 进程工具生命周期所有权改进

- `src/agents/bash-tools.process.ts` 现在首先通过监管器请求取消。
- `process kill/remove` 现在在监管器查找失败时使用进程树回退终止。
- `remove` 通过在请求终止后立即丢弃运行中的会话条目来保持确定的删除行为。

4. 单一来源 Watchdog 默认值

- 在 `src/agents/cli-watchdog-defaults.ts` 中添加共享默认值。
- `src/agents/cli-backends.ts` 消费共享默认值。
- `src/agents/cli-runner/reliability.ts` 消费相同的共享默认值。

5. 死辅助清理

- 从 `src/agents/bash-tools.shared.ts` 中移除未使用的 `killSession` 辅助路径。

6. 添加直接监管器路径测试

- 添加 `src/agents/bash-tools.process.supervisor.test.ts` 以覆盖通过监管器取消的 kill 和 remove 路由。

7. 可靠性差距修复完成

- `src/agents/bash-tools.process.ts` 现在在监管器查找失败时回退到真实的 OS 级进程终止。
- `src/process/supervisor/adapters/child.ts` 现在为默认 cancel/timeout kill 路径使用进程树终止语义。
- 在 `src/process/kill-tree.ts` 中添加共享进程树工具。

8. 添加 PTY 契约边缘情况覆盖

- 添加 `src/process/supervisor/supervisor.pty-command.test.ts` 用于逐字 PTY 命令转发和空命令拒绝。
- 添加 `src/process/supervisor/adapters/child.test.ts` 用于子适配器取消中的进程树 kill 行为。

## 4. 剩余差距与决策

### 可靠性状态

本次迭代所需的两个可靠性差距现已关闭：

- `process kill/remove` 现在在监管器查找失败时具有真实的 OS 终止回退。
- 子 cancel/timeout 现在为默认 kill 路径使用进程树 kill 语义。
- 两种行为均添加了回归测试。

### 持久性与启动协调

重启行为现在明确定义为仅限内存生命周期。

- `reconcileOrphans()` 在 `src/process/supervisor/supervisor.ts` 中按设计保持为 no-op。
- 进程重启后不恢复活动运行。
- 此边界是本实施迭代的有意为之，以避免部分持久化风险。

### 可维护性后续工作

1. `src/agents/bash-tools.exec-runtime.ts` 中的 `runExecProcess` 仍处理多个职责，可以在后续工作中拆分为专注的辅助函数。

## 5. 实施计划

所需可靠性和契约项目的实施迭代已完成。

已完成：

- `process kill/remove` 回退真实终止
- 子适配器默认 kill 路径的进程树取消
- 回退 kill 和子适配器 kill 路径的回归测试
- 显式 `ptyCommand` 下的 PTY 命令边缘情况测试
- 带有 `reconcileOrphans()` 按设计 no-op 的显式内存重启边界

可选后续工作：

- 拆分 `runExecProcess` 为专注的辅助函数，无行为漂移

## 6. 文件映射

### 进程监管器

- `src/process/supervisor/types.ts` 更新为包含区分 spawn 输入和进程本地 stdin 契约。
- `src/process/supervisor/supervisor.ts` 更新为使用显式 `ptyCommand`。
- `src/process/supervisor/adapters/child.ts` 和 `src/process/supervisor/adapters/pty.ts` 与 agent 类型解耦。
- `src/process/supervisor/registry.ts` 幂等 finalize 保持不变并保留。

### 执行与进程集成

- `src/agents/bash-tools.exec-runtime.ts` 更新为显式传递 PTY 命令并保持回退路径。
- `src/agents/bash-tools.process.ts` 更新为通过监管器取消并使用真实进程树回退终止。
- `src/agents/bash-tools.shared.ts` 移除直接 kill 辅助路径。

### CLI 可靠性

- `src/agents/cli-watchdog-defaults.ts` 添加为共享基线。
- `src/agents/cli-backends.ts` 和 `src/agents/cli-runner/reliability.ts` 现在消费相同的默认值。

## 7. 本次迭代验证运行

单元测试：

- `pnpm vitest src/process/supervisor/registry.test.ts`
- `pnpm vitest src/process/supervisor/supervisor.test.ts`
- `pnpm vitest src/process/supervisor/supervisor.pty-command.test.ts`
- `pnpm vitest src/process/supervisor/adapters/child.test.ts`
- `pnpm vitest src/agents/cli-backends.test.ts`
- `pnpm vitest src/agents/bash-tools.exec.pty-cleanup.test.ts`
- `pnpm vitest src/agents/bash-tools.process.poll-timeout.test.ts`
- `pnpm vitest src/agents/bash-tools.process.supervisor.test.ts`
- `pnpm vitest src/process/exec.test.ts`

E2E 目标：

- `pnpm vitest src/agents/cli-runner.test.ts`
- `pnpm vitest run src/agents/bash-tools.exec.pty-fallback.test.ts src/agents/bash-tools.exec.background-abort.test.ts src/agents/bash-tools.process.send-keys.test.ts`

类型检查说明：

- 在此仓库中使用 `pnpm build`（以及 `pnpm check` 用于完整的 lint/docs 门禁）。提及 `pnpm tsgo` 的旧说明已过时。

## 8. 保留的操作保证

- 执行环境加固行为未变。
- 审批和允许列表流程未变。
- 输出清理和输出限制未变。
- PTY 适配器仍保证在强制 kill 和监听器销毁上等待结算。

## 9. 完成定义

1. 监管器是管理运行的生命周期所有者。
2. PTY spawn 使用显式命令契约，无 argv 重建。
3. 进程层对于监管器 stdin 契约没有对 agent 层的类型依赖。
4. Watchdog 默认值为单一来源。
5. 针对性的单元和 e2e 测试保持绿色。
6. 重启持久性边界已明确文档化或完全实现。

## 10. 总结

该分支现在具有连贯且更安全的监管形态：

- 显式 PTY 契约
- 更清晰的进程分层
- 进程操作的监管器驱动取消路径
- 监管器查找失败时的真实回退终止
- 子运行默认 kill 路径的进程树取消
- 统一的 Watchdog 默认值
- 显式内存重启边界（本次迭代中重启间无孤儿协调）