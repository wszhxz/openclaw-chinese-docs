---
summary: "How to run tests locally (vitest) and when to use force/coverage modes"
read_when:
  - Running or fixing tests
title: "Tests"
---
# 测试

- 完整测试套件（套件、实时、Docker）：[Testing](/testing)

- `pnpm test:force`：终止任何占用默认控制端口的残留网关进程，然后使用隔离的网关端口运行完整的Vitest套件，以便服务器测试不会与正在运行的实例冲突。当之前的网关运行占用了端口18789时，请使用此选项。
- `pnpm test:coverage`：使用V8覆盖率运行Vitest。全局阈值为70%的行/分支/函数/语句。覆盖率排除了集成密集型入口点（CLI连接、网关/电报桥接、webchat静态服务器），以将目标集中在可进行单元测试的逻辑上。
- `pnpm test:e2e`：运行网关端到端冒烟测试（多实例WS/HTTP/node配对）。
- `pnpm test:live`：运行提供程序实时测试（minimax/zai）。需要API密钥和`LIVE=1`（或特定于提供程序的`*_LIVE_TEST=1`）来取消跳过。

## 模型延迟基准测试（本地密钥）

脚本：[`scripts/bench-model.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-model.ts)

用法：

- `source ~/.profile && pnpm tsx scripts/bench-model.ts --runs 10`
- 可选环境变量：`MINIMAX_API_KEY`、`MINIMAX_BASE_URL`、`MINIMAX_MODEL`、`ANTHROPIC_API_KEY`
- 默认提示："Reply with a single word: ok. No punctuation or extra text."

上次运行（2025-12-31，20次运行）：

- minimax 中位数 1279毫秒（最小 1114，最大 2431）
- opus 中位数 2454毫秒（最小 1224，最大 3170）

## 入门E2E（Docker）

Docker是可选的；这只在需要容器化入门冒烟测试时才需要。

在干净的Linux容器中的完整冷启动流程：

```bash
scripts/e2e/onboard-docker.sh
```

此脚本通过伪tty驱动交互式向导，验证配置/工作区/会话文件，然后启动网关并运行`openclaw health`。

## QR导入冒烟测试（Docker）

确保`qrcode-terminal`在Docker中Node 22+下加载：

```bash
pnpm test:docker:qr
```