---
summary: "Production plan for reliable interactive process supervision (PTY + non-PTY) with explicit ownership, unified lifecycle, and deterministic cleanup"
owner: "openclaw"
status: "in-progress"
last_updated: "2026-02-15"
title: "PTY and Process Supervision Plan"
---
# PTY 和进程监督计划

## 1. 问题和目标

我们需要一个可靠的生命周期来支持长时间运行的命令执行，包括：

- `exec` 前台运行
- `exec` 后台运行
- `process` 后续操作 (`poll`, `log`, `send-keys`, `paste`, `submit`, `kill`, `remove`)
- CLI代理运行子进程

目标不仅仅是支持PTY。目标是可预测的所有权、取消、超时和清理，而无需使用不安全的进程匹配启发式方法。

## 2. 范围和边界

- 在 `src/process/supervisor` 内部保持实现。
- 不要为此创建新包。
- 尽可能保持当前行为的兼容性。
- 不要扩展范围到终端重播或tmux风格的会话持久化。

## 3. 在此分支中实现的内容

### 监督器基线已经存在

- 监督器模块位于 `src/process/supervisor/*` 下。
- 执行运行时和CLI运行器已经通过监督器的spawn和wait路由。
- 注册表最终化是幂等的。

### 此次完成的内容

1. 显式PTY命令契约

- `SpawnInput` 现在是 `src/process/supervisor/types.ts` 中的一个判别联合体。
- PTY运行需要 `ptyCommand` 而不是重用通用的 `argv`。
- 监督器不再从argv连接重建PTY命令字符串，在 `src/process/supervisor/supervisor.ts` 中。
- 执行运行时现在直接在 `src/agents/bash-tools.exec-runtime.ts` 中传递 `ptyCommand`。

2. 进程层类型解耦

- 监督器类型不再从代理导入 `SessionStdin`。
- 进程本地stdin契约位于 `src/process/supervisor/types.ts` (`ManagedRunStdin`)。
- 适配器现在仅依赖于进程级别的类型：
  - `src/process/supervisor/adapters/child.ts`
  - `src/process/supervisor/adapters/pty.ts`

3. 进程工具生命周期所有权改进

- `src/agents/bash-tools.process.ts` 现在首先通过监督器请求取消。
- `process kill/remove` 现在在监督器查找失败时使用进程树回退终止。
- `remove` 通过在请求终止后立即删除正在运行的会话条目来保持确定性的移除行为。

4. 单一来源看门狗默认设置

- 在 `src/agents/cli-watchdog-defaults.ts` 中添加了共享默认设置。
- `src/agents/cli-backends.ts` 消耗共享默认设置。
- `src/agents/cli-runner/reliability.ts` 消耗相同的共享默认设置。

5. 未使用的辅助清理

- 从 `src/agents/bash-tools.shared.ts` 中移除了未使用的 `killSession` 辅助路径。

6. 添加直接监督器路径测试

- 添加了 `src/agents/bash-tools.process.supervisor.test.ts` 以覆盖通过监督器取消路由的kill和remove。

7. 完成可靠性差距修复

- `src/agents/bash-tools.process.ts` 现在在监督器查找失败时回退到真实的OS级进程终止。
- `src/process/supervisor/adapters/child.ts` 现在使用进程树终止语义作为默认取消/超时kill路径。
- 在 `src/process/kill-tree.ts` 中添加了共享进程树实用程序。

8. 添加PTY契约边缘情况覆盖

- 添加了 `src/process/supervisor/supervisor.pty-command.test.ts` 用于逐字PTY命令转发和空命令拒绝。
- 添加了 `src/process/supervisor/adapters/child.test.ts` 用于子适配器取消中的进程树kill行为。

## 4. 剩余差距和决策

### 可靠性状态

此次通过所需的两个可靠性差距现已关闭：

- `process kill/remove` 现在在监督器查找失败时具有真实的OS终止回退。
- 子取消/超时现在使用进程树kill语义作为默认kill路径。
- 为这两种行为添加了回归测试。

### 耐久性和启动协调

重启行为现在被明确定义为仅内存生命周期。

- `reconcileOrphans()` 在 `src/process/supervisor/supervisor.ts` 中设计为无操作。
- 进程重启后不会恢复活动运行。
- 为了防止部分持久化风险，此实现通过有意设置此边界。

### 可维护性后续工作

1. `runExecProcess` 在 `src/agents/bash-tools.exec-runtime.ts` 中仍然处理多个职责，可以在后续工作中拆分为专注的辅助函数。

## 5. 实施计划

所需可靠性和契约项目的实施通过已完成。

已完成：

- `process kill/remove` 回退真实终止
- 子适配器默认kill路径的进程树取消
- 回退kill和子适配器kill路径的回归测试
- 在显式的 `ptyCommand` 下的PTY命令边缘情况测试
- 显式的内存重启边界，`reconcileOrphans()` 设计为无操作

可选后续工作：

- 将 `runExecProcess` 拆分为专注的辅助函数，不改变行为

## 6. 文件映射

### 进程监督器

- 更新 `src/process/supervisor/types.ts` 以使用判别spawn输入和进程本地stdin契约。
- 更新 `src/process/supervisor/supervisor.ts` 以使用显式的 `ptyCommand`。
- 解耦 `src/process/supervisor/adapters/child.ts` 和 `src/process/supervisor/adapters/pty.ts` 与代理类型。
- 保持 `src/process/supervisor/registry.ts` 的幂等最终化不变。

### 执行和进程集成

- 更新 `src/agents/bash-tools.exec-runtime.ts` 以显式传递PTY命令并保留回退路径。
- 更新 `src/agents/bash-tools.process.ts` 以通过监督器取消并使用真实的进程树回退终止。
- 移除直接kill辅助路径 `src/agents/bash-tools.shared.ts`。

### CLI可靠性

- 添加 `src/agents/cli-watchdog-defaults.ts` 作为共享基线。
- `src/agents/cli-backends.ts` 和 `src/agents/cli-runner/reliability.ts` 现在消耗相同的默认设置。

## 7. 此次通过的验证运行

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

端到端目标：

- `pnpm test:e2e src/agents/cli-runner.e2e.test.ts`
- `pnpm test:e2e src/agents/bash-tools.exec.pty-fallback.e2e.test.ts src/agents/bash-tools.exec.background-abort.e2e.test.ts src/agents/bash-tools.process.send-keys.e2e.test.ts`

类型检查说明：

- `pnpm tsgo` 当前在此仓库中失败，由于现有的UI类型依赖问题 (`@vitest/browser-playwright` 解决方案)，与此次进程监督工作无关。

## 8. 保留的操作保证

- 执行环境加固行为保持不变。
- 批准和允许列表流程保持不变。
- 输出清理和输出限制保持不变。
- PTY适配器仍然保证在强制kill和监听器处置时等待结算。

## 9. 完成定义

1. 监督器是管理运行的生命周期所有者。
2. PTY spawn 使用显式命令契约，不进行argv重构。
3. 进程层没有对代理层的类型依赖于监督器stdin契约。
4. 看门狗默认设置单一来源。
5. 针对单元和端到端测试保持绿色。
6. 重启持久性边界已明确文档化或完全实现。

## 10. 概述

分支现在具有连贯且更安全的监督形状：

- 显式PTY契约
- 更清晰的进程分层
- 由监督器驱动的进程操作取消路径
- 监督器查找失败时的真实回退终止
- 子运行默认kill路径的进程树取消
- 统一的看门狗默认设置
- 显式的内存重启边界（在此通过中不进行跨重启的孤立协调）