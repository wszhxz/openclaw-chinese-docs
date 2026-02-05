---
summary: "Debugging tools: watch mode, raw model streams, and tracing reasoning leakage"
read_when:
  - You need to inspect raw model output for reasoning leakage
  - You want to run the Gateway in watch mode while iterating
  - You need a repeatable debugging workflow
title: "Debugging"
---
# 调试

本页面涵盖流式输出的调试辅助工具，特别是当提供商将推理混入正常文本时。

## 运行时调试覆盖

在聊天中使用 `/debug` 来设置**仅运行时**配置覆盖（内存，非磁盘）。
`/debug` 默认被禁用；使用 `commands.debug: true` 启用。
当你需要切换模糊设置而无需编辑 `openclaw.json` 时，这很方便。

示例：

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug unset messages.responsePrefix
/debug reset
```

`/debug reset` 清除所有覆盖并返回到磁盘上的配置。

## 网关监视模式

为了快速迭代，在文件监视器下运行网关：

```bash
pnpm gateway:watch --force
```

这映射到：

```bash
tsx watch src/entry.ts gateway --force
```

在 `gateway:watch` 之后添加任何网关CLI标志，它们将在每次重启时传递。

## 开发配置文件 + 开发网关（--dev）

使用开发配置文件来隔离状态并启动安全、可丢弃的调试设置。有**两个** `--dev` 标志：

- **全局 `--dev`（配置文件）：** 在 `~/.openclaw-dev` 下隔离状态并将网关端口默认设置为 `19001`（派生端口随之移动）。
- **`gateway --dev`：告诉网关在缺失时自动创建默认配置+工作区**（并跳过BOOTSTRAP.md）。

推荐流程（开发配置文件 + 开发引导）：

```bash
pnpm gateway:dev
OPENCLAW_PROFILE=dev openclaw tui
```

如果你还没有全局安装，请通过 `pnpm openclaw ...` 运行CLI。

这会做什么：

1. **配置文件隔离**（全局 `--dev`）
   - `OPENCLAW_PROFILE=dev`
   - `OPENCLAW_STATE_DIR=~/.openclaw-dev`
   - `OPENCLAW_CONFIG_PATH=~/.openclaw-dev/openclaw.json`
   - `OPENCLAW_GATEWAY_PORT=19001`（浏览器/画布相应移动）

2. **开发引导**（`gateway --dev`）
   - 如果缺失则写入最小配置（`gateway.mode=local`，绑定回环）。
   - 将 `agent.workspace` 设置为开发工作区。
   - 设置 `agent.skipBootstrap=true`（无BOOTSTRAP.md）。
   - 如果缺失则播种工作区文件：
     `AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`。
   - 默认身份：**C3‑PO**（协议机器人）。
   - 在开发模式下跳过频道提供商（`OPENCLAW_SKIP_CHANNELS=1`）。

重置流程（全新开始）：

```bash
pnpm gateway:dev:reset
```

注意：`--dev` 是一个**全局**配置文件标志，会被一些运行器吞掉。
如果你需要明确写出，请使用环境变量形式：

```bash
OPENCLAW_PROFILE=dev openclaw gateway --dev --reset
```

`--reset` 擦除配置、凭据、会话和开发工作区（使用
`trash`，而非 `rm`），然后重新创建默认开发设置。

提示：如果非开发网关已在运行（launchd/systemd），请先停止它：

```bash
openclaw gateway stop
```

## 原始流日志记录（OpenClaw）

OpenClaw 可以在任何过滤/格式化之前记录**原始助手流**。
这是查看推理是否作为纯文本增量到达（或作为单独的思考块）的最佳方式。

通过CLI启用：

```bash
pnpm gateway:watch --force --raw-stream
```

可选路径覆盖：

```bash
pnpm gateway:watch --force --raw-stream --raw-stream-path ~/.openclaw/logs/raw-stream.jsonl
```

等效环境变量：

```bash
OPENCLAW_RAW_STREAM=1
OPENCLAW_RAW_STREAM_PATH=~/.openclaw/logs/raw-stream.jsonl
```

默认文件：

`~/.openclaw/logs/raw-stream.jsonl`

## 原始块日志记录（pi-mono）

为了在解析成块之前捕获**原始OpenAI兼容块**，
pi-mono 提供了一个单独的日志记录器：

```bash
PI_RAW_STREAM=1
```

可选路径：

```bash
PI_RAW_STREAM_PATH=~/.pi-mono/logs/raw-openai-completions.jsonl
```

默认文件：

`~/.pi-mono/logs/raw-openai-completions.jsonl`

> 注意：这只由使用 pi-mono 的
> `openai-completions` 提供商的进程发出。

## 安全注意事项

- 原始流日志可能包含完整提示、工具输出和用户数据。
- 将日志保留在本地并在调试后删除它们。
- 如果你分享日志，请先清除机密信息和个人身份信息。