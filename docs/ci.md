---
title: CI Pipeline
summary: "CI job graph, scope gates, and local command equivalents"
read_when:
  - You need to understand why a CI job did or did not run
  - You are debugging failing GitHub Actions checks
---
# CI 流水线

CI 在每次推送到 ``main`` 和每次拉取请求时运行。它使用智能范围定位，仅在无关区域发生变化时跳过昂贵的任务。

## 任务概览

| 任务                      | 目的                                                                                  | 运行时机                        |
| ------------------------ | ---------------------------------------------------------------------------------------- | ----------------------------------- |
| ``preflight``              | 检测仅文档更改、范围更改、扩展更改，并构建 CI 清单  | 非草稿推送和 PR 始终运行  |
| ``security-fast``          | 私钥检测，通过 ``zizmor`` 进行工作流审计，生产依赖审计          | 非草稿推送和 PR 始终运行  |
| ``build-artifacts``        | 构建一次 ``dist/`` 和控制台 UI，为下游任务上传可重用制品     | Node 相关更改               |
| ``checks-fast-core``       | 快速 Linux 正确性通道，例如捆绑包/插件契约/协议检查             | Node 相关更改               |
| ``checks-fast-extensions`` | 在 ``checks-fast-extensions-shard`` 完成后聚合扩展分片通道       | Node 相关更改               |
| ``extension-fast``         | 仅针对已更改的捆绑插件进行聚焦测试                                       | 检测到扩展更改时 |
| ``check``                  | CI 中的主要本地关卡：``pnpm check`` 加上 ``pnpm build:strict-smoke``                       | Node 相关更改               |
| ``check-additional``       | 架构和边界守卫以及网关监控回归工具集               | Node 相关更改               |
| ``build-smoke``            | 内置 CLI 冒烟测试和启动内存冒烟                                           | Node 相关更改               |
| ``checks``                 | 更重的 Linux Node 通道：完整测试、通道测试以及仅推送的 Node 22 兼容性 | Node 相关更改               |
| ``check-docs``             | 文档格式化、Lint 和断链检查                                            | 文档更改                        |
| ``skills-python``          | 用于 Python 支持技能的 Ruff + pytest                                                   | Python 技能相关更改       |
| ``checks-windows``         | Windows 特定测试通道                                                              | Windows 相关更改            |
| ``macos-node``             | 使用共享构建制品的 macOS TypeScript 测试通道                              | macOS 相关更改              |
| ``macos-swift``            | macOS 应用的 Swift lint、构建和测试                                           | macOS 相关更改              |
| ``android``                | Android 构建和测试矩阵                                                            | Android 相关更改            |

## 快速失败顺序

任务按顺序排列，以便廉价检查在昂贵检查运行之前失败：

1. ``preflight`` 决定存在哪些通道。``docs-scope`` 和 ``changed-scope`` 逻辑是该任务内的步骤，而非独立任务。
2. ``security-fast``、``check``、``check-additional``、``check-docs`` 和 ``skills-python`` 快速失败，无需等待更重的制品和平台矩阵任务。
3. ``build-artifacts`` 与快速 Linux 通道重叠，以便下游消费者在共享构建就绪后即可开始。
4. 之后更重的平台和运行时通道展开：``checks-fast-core``、``checks-fast-extensions``、``extension-fast``、``checks``、``checks-windows``、``macos-node``、``macos-swift`` 和 ``android``。

范围逻辑位于 ``scripts/ci-changed-scope.mjs``，并由 ``src/scripts/ci-changed-scope.test.ts`` 中的单元测试覆盖。
独立的 ``install-smoke`` 工作流通过其自身的 ``preflight`` 任务重用相同的范围脚本。它从更窄的更改冒烟信号计算 ``run_install_smoke``，因此 Docker/安装冒烟测试仅针对安装、打包和容器相关更改运行。

在推送时，``checks`` 矩阵添加仅推送的 ``compat-node22`` 通道。在拉取请求中，该通道被跳过，矩阵专注于正常的测试/通道。

## 运行器

| 运行器                           | 任务                                                                                                 |
| -------------------------------- | ---------------------------------------------------------------------------------------------------- |
| ``blacksmith-16vcpu-ubuntu-2404``  | ``preflight``、``security-fast``、``build-artifacts``、Linux 检查、文档检查、Python 技能、``android`` |
| ``blacksmith-32vcpu-windows-2025`` | ``checks-windows``                                                                                     |
| ``macos-latest``                   | ``macos-node``、``macos-swift``                                                                          |

## 本地等效项

````bash
pnpm check          # types + lint + format
pnpm build:strict-smoke
pnpm test:gateway:watch-regression
pnpm test           # vitest tests
pnpm test:channels
pnpm check:docs     # docs format + lint + broken links
pnpm build          # build dist when CI artifact/build-smoke lanes matter
````