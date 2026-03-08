---
title: CI Pipeline
description: How the OpenClaw CI pipeline works
summary: "CI job graph, scope gates, and local command equivalents"
read_when:
  - You need to understand why a CI job did or did not run
  - You are debugging failing GitHub Actions checks
---
# CI 流水线

CI 在每次推送到 `main` 以及每次拉取请求时运行。它使用智能作用域，仅在仅更改文档或原生代码时跳过耗时任务。

## 任务概览

| Job               | Purpose                                                 | When it runs                                      |
| ----------------- | ------------------------------------------------------- | ------------------------------------------------- |
| `docs-scope`      | 检测仅文档的更改                                | 始终                                            |
| `changed-scope`   | 检测哪些区域发生了更改（node/macos/android/windows） | 非文档 PR                                      |
| `check`           | TypeScript 类型、lint、format                          | 推送到 `main`，或包含 Node 相关更改的 PR |
| `check-docs`      | Markdown lint + 损坏链接检查                       | 文档已更改                                      |
| `code-analysis`   | LOC 阈值检查（1000 行）                        | 仅限 PR                                          |
| `secrets`         | 检测泄露的密钥                                   | 始终                                            |
| `build-artifacts` | 构建一次 dist，与其他任务共享                  | 非文档，node 更改                            |
| `release-check`   | 验证 npm pack 内容                              | 构建后                                       |
| `checks`          | Node/Bun 测试 + 协议检查                         | 非文档，node 更改                            |
| `checks-windows`  | Windows 特定测试                                  | 非文档，windows 相关更改                |
| `macos`           | Swift lint/build/test + TS 测试                        | 包含 macos 更改的 PR                            |
| `android`         | Gradle 构建 + 测试                                    | 非文档，android 更改                         |

## 快速失败顺序

任务按顺序排列，以便轻量级检查在耗时任务运行前失败：

1. `docs-scope` + `code-analysis` + `check`（并行，约 1-2 分钟）
2. `build-artifacts`（阻塞于上述任务）
3. `checks`, `checks-windows`, `macos`, `android`（阻塞于构建）

作用域逻辑位于 `scripts/ci-changed-scope.mjs`，并由 `src/scripts/ci-changed-scope.test.ts` 中的单元测试覆盖。

## 运行器

| Runner                           | Jobs                                       |
| -------------------------------- | ------------------------------------------ |
| `blacksmith-16vcpu-ubuntu-2404`  | 大多数 Linux 任务，包括作用域检测 |
| `blacksmith-32vcpu-windows-2025` | `checks-windows`                           |
| `macos-latest`                   | `macos`, `ios`                             |

## 本地等效操作

```bash
pnpm check          # types + lint + format
pnpm test           # vitest tests
pnpm check:docs     # docs format + lint + broken links
pnpm release:check  # validate npm pack
```