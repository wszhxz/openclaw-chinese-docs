---
summary: Node + tsx "__name is not a function" crash notes and workarounds
read_when:
  - Debugging Node-only dev scripts or watch mode failures
  - Investigating tsx/esbuild loader crashes in OpenClaw
title: "Node + tsx Crash"
---
# Node + tsx “__name 不是一个函数”崩溃

## 概述

通过 Node 运行 OpenClaw 并使用 `tsx` 时，启动即失败，报错如下：

```
[openclaw] Failed to start CLI: TypeError: __name is not a function
    at createSubsystemLogger (.../src/logging/subsystem.ts:203:25)
    at .../src/agents/auth-profiles/constants.ts:25:20
```

该问题始于开发脚本从 Bun 切换至 `tsx`（提交 `2871657e`，2026-01-06）。相同的运行路径在 Bun 下可正常工作。

## 环境

- Node：v25.x（已在 v25.3.0 上复现）
- tsx：4.21.0
- 操作系统：macOS（在其他支持 Node 25 的平台上也极可能复现）

## 复现方式（仅 Node）

```bash
# in repo root
node --version
pnpm install
node --import tsx src/entry.ts status
```

## 仓库中最小化复现

```bash
node --import tsx scripts/repro/tsx-name-repro.ts
```

## Node 版本检查

- Node 25.3.0：失败  
- Node 22.22.0（Homebrew `node@22`）：失败  
- Node 24：本地尚未安装；需进一步验证  

## 备注 / 假设

- `tsx` 使用 esbuild 转换 TypeScript/ESM。esbuild 的 `keepNames` 会生成一个 `__name` 辅助函数，并用 `__name(...)` 包裹函数定义。  
- 此崩溃表明 `__name` 在运行时存在，但并非函数类型，这意味着该模块在 Node 25 加载器路径中缺失或覆盖了该辅助函数。  
- 其他使用 esbuild 的项目也曾报告过类似的 `__name` 辅助函数问题，原因同样是辅助函数缺失或被重写。

## 回归历史

- `2871657e`（2026-01-06）：脚本由 Bun 改为 tsx，以使 Bun 变为可选依赖。  
- 此前（Bun 路径下），`openclaw status` 和 `gateway:watch` 均可正常工作。

## 临时解决方案

- 对开发脚本继续使用 Bun（当前临时回退方案）。  
- 使用 Node + `tsc --watch` 编译后运行输出文件：

  ```bash
  pnpm exec tsc --watch --preserveWatchOutput
  node --watch openclaw.mjs status
  ```

- 本地已确认：`pnpm exec tsc -p tsconfig.json` + `node openclaw.mjs status` 在 Node 25 下可正常运行。  
- 若可能，禁用 TS 加载器中的 esbuild `keepNames` 选项（可避免插入 `__name` 辅助函数）；但当前 `tsx` 尚未暴露该配置项。  
- 使用 `tsx` 测试 Node LTS（22/24）版本，以确认该问题是否仅限于 Node 25。

## 参考资料

- [https://opennext.js.org/cloudflare/howtos/keep_names](https://opennext.js.org/cloudflare/howtos/keep_names)  
- [https://esbuild.github.io/api/#keep-names](https://esbuild.github.io/api/#keep-names)  
- [https://github.com/evanw/esbuild/issues/1031](https://github.com/evanw/esbuild/issues/1031)

## 后续步骤

- 在 Node 22/24 上复现，以确认是否为 Node 25 特有的回归问题。  
- 测试 `tsx` 的 nightly 版本，或若已知存在回归，则降级至早期稳定版本。  
- 若在 Node LTS 上亦可复现，需向上游提交最小化复现案例，并附上 `__name` 堆栈跟踪信息。