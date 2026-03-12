---
summary: "How to run tests locally (vitest) and when to use force/coverage modes"
read_when:
  - Running or fixing tests
title: "Tests"
---
# 测试

- 完整测试套件（测试集、实时测试、Docker）：[测试](/help/testing)

- `pnpm test:force`：终止任何占用默认控制端口的残留网关进程，然后以隔离的网关端口运行完整的 Vitest 测试套件，避免服务器测试与正在运行的实例发生端口冲突。当先前的网关运行导致端口 18789 被占用时，请使用此命令。
- `pnpm test:coverage`：运行单元测试套件并启用 V8 覆盖率（通过 `vitest.unit.config.ts`）。全局覆盖率阈值为：行数/分支/函数/语句均达 70%。覆盖率排除了集成度较高的入口点（CLI 绑定、网关/Telegram 桥接器、Webchat 静态服务器），以确保目标聚焦于可进行单元测试的逻辑。
- `pnpm test`（Node 24+ 环境下）：OpenClaw 自动禁用 Vitest 的 `vmForks`，改用 `forks`，以规避 `ERR_VM_MODULE_LINK_FAILURE` / `module is already linked`。您可通过设置 `OPENCLAW_TEST_VM_FORKS=0|1` 强制指定行为。
- `pnpm test`：默认运行快速核心单元测试通道，用于本地快速反馈。
- `pnpm test:channels`：运行通道相关性较强的测试套件。
- `pnpm test:extensions`：运行扩展/插件测试套件。
- 网关集成测试：需通过 `OPENCLAW_TEST_INCLUDE_GATEWAY=1 pnpm test` 或 `pnpm test:gateway` 显式启用。
- `pnpm test:e2e`：运行网关端到端冒烟测试（多实例 WebSocket/HTTP/Node 配对）。默认采用 `vmForks` + `vitest.e2e.config.ts` 中的自适应工作线程；可通过 `OPENCLAW_E2E_WORKERS=<n>` 进行调优，并设置 `OPENCLAW_E2E_VERBOSE=1` 获取详细日志输出。
- `pnpm test:live`：运行提供商实时测试（minimax/zai）。需要 API 密钥及 `LIVE=1`（或提供商专用的 `*_LIVE_TEST=1`）以解除跳过限制。

## 本地 PR 门禁检查

执行本地 PR 合并/门禁检查时，请运行：

- `pnpm check`
- `pnpm build`
- `pnpm test`
- `pnpm check:docs`

若 `pnpm test` 在高负载主机上偶发失败（flakes），请先重试一次，再将其视为回归问题；随后使用 `pnpm vitest run <path/to/test>` 进行隔离分析。对于内存受限的主机，请使用：

- `OPENCLAW_TEST_PROFILE=low OPENCLAW_TEST_SERIAL_GATEWAY=1 pnpm test`

## 模型延迟基准测试（本地密钥）

脚本：[`scripts/bench-model.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-model.ts)

用法：

- `source ~/.profile && pnpm tsx scripts/bench-model.ts --runs 10`
- 可选环境变量：`MINIMAX_API_KEY`、`MINIMAX_BASE_URL`、`MINIMAX_MODEL`、`ANTHROPIC_API_KEY`
- 默认提示词：“仅回复一个单词：ok。不带标点符号，也不含额外文本。”

最近一次运行（2025-12-31，共 20 次）：

- minimax 中位延迟 1279ms（最小 1114ms，最大 2431ms）
- opus 中位延迟 2454ms（最小 1224ms，最大 3170ms）

## CLI 启动基准测试

脚本：[`scripts/bench-cli-startup.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-cli-startup.ts)

用法：

- `pnpm tsx scripts/bench-cli-startup.ts`
- `pnpm tsx scripts/bench-cli-startup.ts --runs 12`
- `pnpm tsx scripts/bench-cli-startup.ts --entry dist/entry.js --timeout-ms 45000`

该基准测试涵盖以下命令：

- `--version`
- `--help`
- `health --json`
- `status --json`
- `status`

输出内容包括每个命令的平均耗时、p50、p95、最小/最大耗时，以及退出码/信号分布情况。

## 入门端到端测试（Docker）

Docker 为可选依赖；仅在执行容器化入门冒烟测试时需要。

在干净的 Linux 容器中执行完整冷启动流程：

```bash
scripts/e2e/onboard-docker.sh
```

该脚本通过伪终端（pseudo-tty）驱动交互式向导，验证配置/工作区/会话文件，随后启动网关并运行 `openclaw health`。

## QR 导入冒烟测试（Docker）

确保 `qrcode-terminal` 在 Node 22+ 环境下的 Docker 中正常加载：

```bash
pnpm test:docker:qr
```