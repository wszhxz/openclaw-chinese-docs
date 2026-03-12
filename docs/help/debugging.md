---
summary: "Debugging tools: watch mode, raw model streams, and tracing reasoning leakage"
read_when:
  - You need to inspect raw model output for reasoning leakage
  - You want to run the Gateway in watch mode while iterating
  - You need a repeatable debugging workflow
title: "Debugging"
---
# 调试

本页介绍用于流式输出调试的辅助工具，尤其适用于提供方将推理内容混入普通文本的场景。

## 运行时调试覆盖

在聊天中使用 `/debug` 来设置**仅限运行时**的配置覆盖（内存中生效，不写入磁盘）。  
`/debug` 默认处于禁用状态；可通过 `commands.debug: true` 启用。  
当你需要快速切换一些冷门设置、又不想修改 `openclaw.json` 时，该功能非常便捷。

示例：

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug unset messages.responsePrefix
/debug reset
```

`/debug reset` 将清除所有覆盖项，并恢复为磁盘上的配置。

## 网关监听模式（Gateway watch mode）

为实现快速迭代，可在文件监听器下运行网关：

```bash
pnpm gateway:watch
```

其等价于：

```bash
node --watch-path src --watch-path tsconfig.json --watch-path package.json --watch-preserve-output scripts/run-node.mjs gateway --force
```

在 `gateway:watch` 后添加任意网关 CLI 标志，这些标志将在每次重启时透传。

## 开发者配置文件 + 开发者网关（--dev）

使用开发者配置文件（dev profile）来隔离状态，并快速启动一个安全、可随时丢弃的调试环境。共有 **两个** `--dev` 标志：

- **全局 `--dev`（配置文件）：** 将状态隔离至 `~/.openclaw-dev` 下，  
  并将网关端口默认设为 `19001`（派生端口会随之偏移）。
- **`gateway --dev`：** 告知网关在缺失时自动创建默认配置和工作区（同时跳过 BOOTSTRAP.md）。

推荐流程（开发者配置文件 + 开发者引导）：

```bash
pnpm gateway:dev
OPENCLAW_PROFILE=dev openclaw tui
```

若尚未进行全局安装，请通过 `pnpm openclaw ...` 运行 CLI。

该流程的作用如下：

1. **配置文件隔离**（全局 `--dev`）
   - `OPENCLAW_PROFILE=dev`
   - `OPENCLAW_STATE_DIR=~/.openclaw-dev`
   - `OPENCLAW_CONFIG_PATH=~/.openclaw-dev/openclaw.json`
   - `OPENCLAW_GATEWAY_PORT=19001`（浏览器/画布界面相应调整）

2. **开发者引导**（`gateway --dev`）
   - 若缺失，则写入最小化配置（`gateway.mode=local`，绑定回环地址）。
   - 将 `agent.workspace` 设为开发工作区。
   - 设置 `agent.skipBootstrap=true`（跳过 BOOTSTRAP.md）。
   - 若工作区文件缺失，则初始化以下文件：  
     `AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`。
   - 默认身份：**C3‑PO**（协议机器人）。
   - 在开发模式下跳过通道提供方（`OPENCLAW_SKIP_CHANNELS=1`）。

重置流程（全新开始）：

```bash
pnpm gateway:dev:reset
```

注意：`--dev` 是一个**全局**配置文件标志，某些运行器会将其“吞掉”。  
如需显式指定，请改用环境变量形式：

```bash
OPENCLAW_PROFILE=dev openclaw gateway --dev --reset
```

`--reset` 将清除配置、凭据、会话及开发工作区（使用 `trash`，而非 `rm`），然后重新创建默认开发环境。

提示：若已有非开发版网关正在运行（例如通过 launchd/systemd 启动），请先将其停止：

```bash
openclaw gateway stop
```

## 原始流日志（OpenClaw）

OpenClaw 可记录**原始助手流（raw assistant stream）**，即在任何过滤或格式化操作之前的数据。  
这是判断推理内容是以纯文本增量（plain text deltas）形式到达、还是以独立思考块（separate thinking blocks）形式到达的最佳方式。

通过 CLI 启用：

```bash
pnpm gateway:watch --raw-stream
```

可选路径覆盖：

```bash
pnpm gateway:watch --raw-stream --raw-stream-path ~/.openclaw/logs/raw-stream.jsonl
```

等效的环境变量：

```bash
OPENCLAW_RAW_STREAM=1
OPENCLAW_RAW_STREAM_PATH=~/.openclaw/logs/raw-stream.jsonl
```

默认文件：

`~/.openclaw/logs/raw-stream.jsonl`

## 原始分块日志（pi-mono）

为捕获**原始 OpenAI 兼容分块（raw OpenAI-compat chunks）**（即在解析为语义块之前），pi-mono 提供了一个独立的日志器：

```bash
PI_RAW_STREAM=1
```

可选路径：

```bash
PI_RAW_STREAM_PATH=~/.pi-mono/logs/raw-openai-completions.jsonl
```

默认文件：

`~/.pi-mono/logs/raw-openai-completions.jsonl`

> 注意：此日志**仅由使用 pi-mono 的 `openai-completions` 提供方**的进程生成。

## 安全说明

- 原始流日志可能包含完整提示词、工具输出及用户数据。  
- 请将日志保存在本地，并在调试完成后及时删除。  
- 若需共享日志，请务必先脱敏密钥和隐私信息（PII）。