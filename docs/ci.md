---
title: CI Pipeline
description: How the OpenClaw CI pipeline works
---
# CI Pipeline

CI 在每次推送到 `main` 和每次拉取请求时运行。它使用智能范围来跳过仅文档或原生代码更改时的昂贵任务。

## 任务概述

| 任务               | 目的                                         | 运行时机              |
| ----------------- | ----------------------------------------------- | ------------------------- |
| `docs-scope`      | 检测仅文档更改                        | 始终                    |
| `changed-scope`   | 检测哪些区域更改（node/macos/android） | 非文档 PRs              |
| `check`           | TypeScript 类型、lint、格式                  | 非文档更改          |
| `check-docs`      | Markdown lint + 断链检查               | 文档更改              |
| `code-analysis`   | LOC 阈值检查（1000 行）                | 仅 PRs                  |
| `secrets`         | 检测泄露的秘密                           | 始终                    |
| `build-artifacts` | 构建 dist 一次，与其他任务共享          | 非文档、node 更改    |
| `release-check`   | 验证 npm 包内容                      | 构建之后               |
| `checks`          | Node/Bun 测试 + 协议检查                 | 非文档、node 更改    |
| `checks-windows`  | Windows 特定测试                          | 非文档、node 更改    |
| `macos`           | Swift lint/build/test + TS 测试                | 包含 macos 更改的 PRs    |
| `android`         | Gradle 构建 + 测试                            | 非文档、android 更改 |

## 快速失败顺序

任务按顺序排列，以便廉价检查在昂贵任务之前失败：

1. `docs-scope` + `code-analysis` + `check` (并行, ~1-2 分钟)
2. `build-artifacts` (依赖于上述任务)
3. `checks`, `checks-windows`, `macos`, `android` (依赖于构建)

## 代码分析

`code-analysis` 任务在 PR 上运行 `scripts/analyze_code_files.py` 以强制执行代码质量：

- **LOC 阈值**: 文件超过 1000 行则构建失败
- **仅增量**: 仅检查 PR 中更改的文件，而不是整个代码库
- **推送到主分支**: 跳过（任务作为无操作通过），因此合并不会被阻止

当 `--strict` 设置时，违规会阻止所有下游任务。这可以在昂贵测试运行之前捕获膨胀的文件。

排除目录: `node_modules`, `dist`, `vendor`, `.git`, `coverage`, `Swabble`, `skills`, `.pi`

## 运行器

| 运行器                          | 任务                          |
| ------------------------------- | ----------------------------- |
| `blacksmith-4vcpu-ubuntu-2404`  | 大多数 Linux 任务               |
| `blacksmith-4vcpu-windows-2025` | `checks-windows`              |
| `macos-latest`                  | `macos`, `ios`                |
| `ubuntu-latest`                 | 范围检测（轻量级） |

## 本地等效

```bash
pnpm check          # types + lint + format
pnpm test           # vitest tests
pnpm check:docs     # docs format + lint + broken links
pnpm release:check  # validate npm pack
```