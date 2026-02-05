---
summary: Node + tsx "__name is not a function" crash notes and workarounds
read_when:
  - Debugging Node-only dev scripts or watch mode failures
  - Investigating tsx/esbuild loader crashes in OpenClaw
title: "Node + tsx Crash"
---
# Node + tsx "__name is not a function" 崩溃

## 概述

通过 Node 运行 OpenClaw 时使用 `tsx` 在启动时失败，错误信息为：

```
[openclaw] Failed to start CLI: TypeError: __name is not a function
    at createSubsystemLogger (.../src/logging/subsystem.ts:203:25)
    at .../src/agents/auth-profiles/constants.ts:25:20
```

在将开发脚本从 Bun 切换到 `tsx` 后开始出现此问题（提交 `2871657e`，2026-01-06）。相同的运行路径在 Bun 上可以正常工作。

## 环境

- Node: v25.x（在 v25.3.0 上观察到）
- tsx: 4.21.0
- OS: macOS（其他运行 Node 25 的平台也可能复现）

## 复现（仅限 Node）

```bash
# in repo root
node --version
pnpm install
node --import tsx src/entry.ts status
```

## 仓库中的最小复现

```bash
node --import tsx scripts/repro/tsx-name-repro.ts
```

## Node 版本检查

- Node 25.3.0: 失败
- Node 22.22.0 (Homebrew `node@22`)：失败
- Node 24: 尚未在此处安装；需要验证

## 注意事项 / 假设

- `tsx` 使用 esbuild 转换 TS/ESM。esbuild 的 `keepNames` 发射一个 `__name` 辅助函数，并用 `__name(...)` 包装函数定义。
- 崩溃表明 `__name` 存在但在运行时不是一个函数，这意味着该辅助函数在此模块的 Node 25 加载路径中缺失或被覆盖。
- 其他 esbuild 消费者也报告过类似的 `__name` 辅助函数问题，当辅助函数缺失或被重写时。

## 回归历史

- `2871657e` (2026-01-06): 脚本从 Bun 更改为 tsx 以使 Bun 成为可选。
- 在此之前（Bun 路径），`openclaw status` 和 `gateway:watch` 可以正常工作。

## 解决方案

- 使用 Bun 进行开发脚本（当前临时回退）。
- 使用 Node + tsc watch，然后运行编译输出：
  ```bash
  pnpm exec tsc --watch --preserveWatchOutput
  node --watch openclaw.mjs status
  ```
- 本地确认：`pnpm exec tsc -p tsconfig.json` + `node openclaw.mjs status` 在 Node 25 上可以正常工作。
- 如果可能，禁用 TS 加载器中的 esbuild keepNames（防止插入 `__name` 辅助函数）；tsx 目前不支持此操作。
- 使用 Node LTS (22/24) 测试 `tsx` 以查看问题是否特定于 Node 25。

## 参考资料

- https://opennext.js.org/cloudflare/howtos/keep_names
- https://esbuild.github.io/api/#keep-names
- https://github.com/evanw/esbuild/issues/1031

## 下一步

- 在 Node 22/24 上复现以确认 Node 25 回归。
- 测试 `tsx` 的 nightly 版本或固定到早期版本，如果存在已知回归。
- 如果在 Node LTS 上复现，请使用 `__name` 的堆栈跟踪向上游提交最小复现。