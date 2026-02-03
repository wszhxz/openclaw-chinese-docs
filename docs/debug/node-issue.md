---
summary: Node + tsx "__name is not a function" crash notes and workarounds
read_when:
  - Debugging Node-only dev scripts or watch mode failures
  - Investigating tsx/esbuild loader crashes in OpenClaw
title: "Node + tsx Crash"
---
.<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context and the key points. The main issue is about a crash in OpenClaw when using Node with tsx, specifically the "__name is not a function" error. The user mentions switching from Bun to tsx, and the problem started after that commit. There are sections on environment, reproduction steps, notes, regression history, workarounds, references, and next steps.

First, I'll translate the title and section headers. Terms like "Node + tsx" should stay as is, but maybe add a note if needed. The error message "TypeError: __name is not a function" needs to be accurately translated. I should ensure technical terms like "esbuild", "tsx", and "Bun" are kept in English since they are specific tools or names.

For the summary section, I need to convey that running OpenClaw via Node with tsx fails at startup with the given error. The commit hash and date should remain unchanged. The environment section lists Node, tsx, and OS versions; these should be translated but keep the version numbers as they are. 

In the repro steps, the bash commands need to be translated, but the actual commands should stay in English as they are code. The same applies to the minimal repro in the repo. The Node version check section lists different versions; I'll translate the descriptions but keep the version numbers. 

The notes/hypothesis section explains that tsx uses esbuild and the __name helper. I need to make sure the technical explanation is clear in Chinese. The regression history mentions specific commits and dates; these should be translated but the commit hash and dates remain. 

Workarounds include using Bun, Node + tsc, disabling esbuild keepNames, and testing LTS versions. These steps should be translated clearly, ensuring that the commands are correctly formatted. References are URLs, so they stay as is. 

Next steps involve testing on different Node versions, checking tsx nightly, and filing a repro. These should be translated to maintain the same meaning. 

I need to be careful with technical terms and ensure that the structure of the document is preserved. Also, maintaining the code blocks and commands in their original form is important. I'll check for any specific jargon that might not have a direct translation and decide whether to keep them in English or find an appropriate Chinese equivalent. 

Finally, I'll review the translated text to ensure that all sections are accurately translated, the technical details are preserved, and the formatting (like code blocks and lists) is maintained. Making sure that the user's intent and the problem description are clear in Chinese is crucial for the translation to be effective.
</think>

# Node + tsx "__name 不是函数" 崩溃

## 概述

通过 Node 运行 OpenClaw 时，使用 `tsx` 会在启动时失败，报错如下：

```
[openclaw] 启动 CLI 失败: TypeError: __name 不是函数
    at createSubsystemLogger (.../src/logging/subsystem.ts:203:25)
    at .../src/agents/auth-profiles/constants.ts:25:20
```

此问题始于将开发脚本从 Bun 切换为 `tsx`（提交 `2871657e`，2026-01-06）。使用相同运行时路径时，Bun 可正常运行。

## 环境

- Node: v25.x（观察到 v25.3.0）
- tsx: 4.21.0
- OS: macOS（其他运行 Node 25 的平台也可能复现）

## 仅 Node 的复现步骤

```bash
# 在仓库根目录
node --version
pnpm install
node --import tsx src/entry.ts status
```

## 仓库中的最小复现步骤

```bash
node --import tsx scripts/repro/tsx-name-repro.ts
```

## Node 版本检查

- Node 25.3.0: 失败
- Node 22.22.0（Homebrew `node@22`）: 失败
- Node 24: 未在此安装，需验证

## 说明/假设

- `tsx` 使用 esbuild 来转换 TS/ESM。esbuild 的 `keepNames` 会生成 `__name` 辅助函数，并用 `__name(...)` 包裹函数定义。
- 崩溃表明 `__name` 存在但运行时不是函数，这表明在 Node 25 的加载路径中，该模块的辅助函数缺失或被覆盖。
- 其他 esbuild 用户也报告过类似 `__name` 辅助函数缺失或被重写的错误。

## 回退历史

- `2871657e`（2026-01-06）: 将脚本从 Bun 切换为 tsx 以使 Bun 变为可选。
- 之前（Bun 路径）`openclaw status` 和 `gateway:watch` 可正常运行。

## 解决方法

- 使用 Bun 运行开发脚本（当前临时回退）。
- 使用 Node + tsc 监控，然后运行编译后的输出：
  ```bash
  pnpm exec tsc --watch --preserveWatchOutput
  node --watch openclaw.mjs status
  ```
- 本地验证：`pnpm exec tsc -p tsconfig.json` + `node openclaw.mjs status` 在 Node 25 上可运行。
- 如果可能，禁用 TS 加载器中的 esbuild keepNames（防止 `__name` 辅助函数插入）；tsx 当前未公开此功能。
- 使用 `tsx` 测试 Node LTS（22/24）以确认问题是否为 Node 25 特有。

## 参考

- https://opennext.js.org/cloudflare/howtos/keep_names
- https://esbuild.github.io/api/#keep-names
- https://github.com/evanw/esbuild/issues/1031

## 下一步

- 在 Node 22/24 上复现以确认 Node 25 的回归问题。
- 如果已知存在回归问题，测试 `tsx` 夜间构建或固定到早期版本。
- 如果在 Node LTS 上复现，提交包含 `__name` 堆栈跟踪的最小复现问题到上游。