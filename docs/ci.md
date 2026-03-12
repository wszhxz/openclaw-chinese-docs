---
title: CI Pipeline
description: How the OpenClaw CI pipeline works
summary: "CI job graph, scope gates, and local command equivalents"
read_when:
  - You need to understand why a CI job did or did not run
  - You are debugging failing GitHub Actions checks
---
# CI 流水线

CI 在每次向 `main` 推送代码以及每次发起拉取请求（Pull Request）时运行。它采用智能作用域判断机制，在仅修改文档或原生代码时跳过开销较大的任务。

## 任务概览

| 任务               | 目的                                                 | 触发时机                                      |
| ----------------- | ------------------------------------------------------- | ------------------------------------------------- |
| `docs-scope`      | 检测仅涉及文档的变更                                | 始终运行                                            |
| `changed-scope`   | 检测哪些模块发生了变更（node/macos/android/windows） | 非文档类 PR                                       |
| `check`           | TypeScript 类型检查、代码规范（lint）、格式化（format）                          | 推送到 `main`，或包含 Node 相关变更的 PR |
| `check-docs`      | Markdown 规范检查 + 失效链接检测                       | 文档发生变更                                      |
| `code-analysis`   | 代码行数阈值检查（1000 行）                        | 仅限 PR                                           |
| `secrets`         | 检测是否泄露密钥                                   | 始终运行                                            |
| `build-artifacts` | 构建一次 dist 并供其他任务共享                  | 非文档类变更且涉及 Node 的变更                            |
| `release-check`   | 验证 npm pack 打包内容                              | 构建完成后                                         |
| `checks`          | Node/Bun 测试 + 协议检查                         | 非文档类变更且涉及 Node 的变更                            |
| `checks-windows`  | Windows 特定测试                                  | 非文档类变更且涉及 Windows 的变更                |
| `macos`           | Swift 规范检查/构建/测试 + TypeScript 测试                        | 包含 macOS 变更的 PR                             |
| `android`         | Gradle 构建 + 测试                                    | 非文档类变更且涉及 Android 的变更                         |

## 快速失败顺序

任务按执行成本由低到高排序，确保低成本检查先运行，并在失败时阻止高成本任务启动：

1. `docs-scope` + `code-analysis` + `check`（并行执行，耗时约 1–2 分钟）
2. `build-artifacts`（依赖上述任务完成）
3. `checks`、`checks-windows`、`macos`、`android`（依赖构建任务完成）

作用域判断逻辑位于 `scripts/ci-changed-scope.mjs` 中，并由 `src/scripts/ci-changed-scope.test.ts` 中的单元测试覆盖。

## 运行器（Runners）

| 运行器                           | 承担的任务                                       |
| -------------------------------- | ------------------------------------------ |
| `blacksmith-16vcpu-ubuntu-2404`  | 大多数 Linux 任务，包括作用域检测 |
| `blacksmith-32vcpu-windows-2025` | `checks-windows`                           |
| `macos-latest`                   | `macos`、`ios`                             |

## 本地等效命令

```bash
pnpm check          # types + lint + format
pnpm test           # vitest tests
pnpm check:docs     # docs format + lint + broken links
pnpm release:check  # validate npm pack
```