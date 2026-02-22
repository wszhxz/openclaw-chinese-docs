---
title: CI Pipeline
description: How the OpenClaw CI pipeline works
---
# CI Pipeline

CI 在每次推送到 `main` 和每次拉取请求时运行。它使用智能范围来跳过仅文档或本地代码更改时的昂贵任务。

## Job 概述

| Job               | 目的                                         | 运行时机              |
| ----------------- | ----------------------------------------------- | ------------------------- |
| `docs-scope`      | 检测仅文档更改                        | 始终                    |
| `changed-scope`   | 检测哪些区域更改（node/macos/android） | 非文档 PRs              |
| `check`           | TypeScript 类型、lint、格式                  | 非文档更改          |
| `check-docs`      | Markdown lint + 断链检查               | 文档更改              |
| `code-analysis`   | LOC 阈值检查（1000 行）                | 仅 PRs                  |
| `secrets`         | 检测泄露的密钥                           | 始终                    |
| `build-artifacts` | 构建 dist 一次，与其他任务共享          | 非文档、node 更改    |
| `release-check`   | 验证 npm pack 内容                      | 构建之后               |
| `checks`          | Node/Bun 测试 + 协议检查                 | 非文档、node 更改    |
| `checks-windows`  | Windows 特定测试                          | 非文档、node 更改    |
| `macos`           | Swift lint/build/test + TS 测试                | 包含 macos 更改的 PRs    |
| `android`         | Gradle 构建 + 测试                            | 非文档、android 更改 |

## 快速失败顺序

任务按顺序排列，以便在运行昂贵任务之前先失败廉价检查：

1. `docs-scope` + `code-analysis` + `check` (并行, ~1-2 分钟)
2. `build-artifacts` (依赖于上述任务)
3. `checks`, `checks-windows`, `macos`, `android` (依赖于构建)

## 运行器

| 运行器                           | 任务                                       |
| -------------------------------- | ------------------------------------------ |
| `blacksmith-16vcpu-ubuntu-2404`  | 大多数 Linux 任务，包括范围检测 |
| `blacksmith-16vcpu-windows-2025` | `checks-windows`                           |
| `macos-latest`                   | `macos`, `ios`                             |

## 本地等效

```bash
pnpm check          # types + lint + format
pnpm test           # vitest tests
pnpm check:docs     # docs format + lint + broken links
pnpm release:check  # validate npm pack
```