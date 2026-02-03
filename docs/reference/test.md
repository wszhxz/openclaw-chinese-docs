---
summary: "How to run tests locally (vitest) and when to use force/coverage modes"
read_when:
  - Running or fixing tests
title: "Tests"
---
# 测试

- 完整测试套件（套件、实时、Docker）：[测试](/testing)

- `pnpm test:force`：终止任何仍在占用默认控制端口的网关进程，然后使用隔离的网关端口运行完整的 Vitest 套件，以防止服务器测试与正在运行的实例冲突。当先前的网关运行占用了端口 18789 时使用此命令。
- `pnpm test:coverage`：使用 V8 覆盖功能运行 Vitest。全局阈值为 70% 的行/分支/函数/语句覆盖率。覆盖率排除集成度高的入口点（CLI 连接、网关/Telegram 桥接、网页聊天静态服务器），以保持目标专注于单元测试逻辑。
- `pnpm test:e2e`：运行网关端到端冒烟测试（多实例 WS/HTTP/node 配对）。
- `pnpm test:live`：运行提供方实时测试（minimax/zai）。需要 API 密钥和 `LIVE=1`（或提供方特定的 `*_LIVE_TEST=1`）以取消跳过测试。

## 模型延迟基准测试（本地密钥）

脚本： [`scripts/bench-model.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-model.ts)

用法：

- `source ~/.profile && pnpm tsx scripts/bench-model.ts --runs 10`
- 可选环境变量：`MINIMAX_API_KEY`，`MINIMAX_BASE_URL`，`MINIMAX_MODEL`，`ANTHROPIC_API_KEY`
- 默认提示：“用一个单词回复：ok。不要标点符号或额外文本。”

上次运行（2025-12-31，20 次运行）：

- minimax 中位数 1279ms（最小 1114，最大 2431）
- opus 中位数 2454ms（最小 1224，最大 3170）

## 入门 E2E（Docker）

Docker 是可选的；这仅在容器化入门冒烟测试时需要。

在一个干净的 Linux 容器中执行完整的冷启动流程：

```bash
scripts/e2e/onboard-docker.sh
```

此脚本通过伪终端驱动交互式向导，验证配置/工作区/会话文件，然后启动网关并运行 `openclaw health`。

## QR 导入冒烟测试（Docker）

确保 `qrcode-terminal` 在 Docker 中 Node 22+ 下加载：

```bash
pnpm test:docker:qr
```