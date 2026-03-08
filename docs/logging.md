---
summary: "Logging overview: file logs, console output, CLI tailing, and the Control UI"
read_when:
  - You need a beginner-friendly overview of logging
  - You want to configure log levels or formats
  - You are troubleshooting and need to find logs quickly
title: "Logging"
---
# 日志

OpenClaw 在两个位置记录日志：

- **文件日志**（JSON 行）由 Gateway 写入。
- **控制台输出**显示在终端和 Control UI 中。

本文档介绍日志的存储位置、读取方法以及如何配置日志级别和格式。

## 日志存储位置

默认情况下，Gateway 会在以下位置写入滚动日志文件：

`/tmp/openclaw/openclaw-YYYY-MM-DD.log`

日期使用网关主机的本地时区。

您可以在 `~/.openclaw/openclaw.json` 中覆盖此设置：

```json
{
  "logging": {
    "file": "/path/to/openclaw.log"
  }
}
```

## 如何读取日志

### CLI：实时跟踪（推荐）

通过 RPC 使用 CLI 跟踪 Gateway 日志文件：

```bash
openclaw logs --follow
```

输出模式：

- **TTY 会话**：美观、带颜色、结构化的日志行。
- **非 TTY 会话**：纯文本。
- `--json`: 逐行分隔的 JSON（每行一个日志事件）。
- `--plain`: 强制在 TTY 会话中使用纯文本。
- `--no-color`: 禁用 ANSI 颜色。

在 JSON 模式下，CLI 会发出带有 `type` 标签的对象：

- `meta`: 流元数据（文件、游标、大小）
- `log`: 解析后的日志条目
- `notice`: 截断/轮换提示
- `raw`: 未解析的日志行

如果无法连接 Gateway，CLI 会打印简短提示以运行：

```bash
openclaw doctor
```

### Control UI（Web）

Control UI 的 **日志** 选项卡使用 `logs.tail` 跟踪同一文件。参见 [/web/control-ui](/web/control-ui) 了解如何打开它。

### 仅频道日志

若要过滤频道活动（WhatsApp/Telegram 等），请使用：

```bash
openclaw channels logs --channel whatsapp
```

## 日志格式

### 文件日志（JSONL）

日志文件中的每一行都是一个 JSON 对象。CLI 和 Control UI 解析这些条目以呈现结构化输出（时间、级别、子系统、消息）。

### 控制台输出

控制台日志是 **感知 TTY 的**，并经过格式化以提高可读性：

- 子系统前缀（例如 `gateway/channels/whatsapp`）
- 级别着色（info/warn/error）
- 可选的紧凑或 JSON 模式

控制台格式化由 `logging.consoleStyle` 控制。

## 配置日志记录

所有日志配置位于 `logging` 下的 `~/.openclaw/openclaw.json` 中。

```json
{
  "logging": {
    "level": "info",
    "file": "/tmp/openclaw/openclaw-YYYY-MM-DD.log",
    "consoleLevel": "info",
    "consoleStyle": "pretty",
    "redactSensitive": "tools",
    "redactPatterns": ["sk-.*"]
  }
}
```

### 日志级别

- `logging.level`: **文件日志**（JSONL）级别。
- `logging.consoleLevel`: **控制台**详细程度级别。

您可以通过 **`OPENCLAW_LOG_LEVEL`** 环境变量覆盖两者（例如 `OPENCLAW_LOG_LEVEL=debug`）。环境变量优先于配置文件，因此您可以为单次运行提高详细程度而无需编辑 `openclaw.json`。您还可以传递全局 CLI 选项 **`--log-level <level>`**（例如 `openclaw --log-level debug gateway run`），这将覆盖该命令的环境变量。

`--verbose` 仅影响控制台输出；它不会更改文件日志级别。

### 控制台样式

`logging.consoleStyle`:

- `pretty`: 人类友好、带颜色、包含时间戳。
- `compact`: 更紧凑的输出（最适合长会话）。
- `json`: 每行一个 JSON（用于日志处理器）。

### 脱敏

工具摘要可以在内容到达控制台之前对敏感 Token 进行脱敏：

- `logging.redactSensitive`: `off` | `tools`（默认值：`tools`）
- `logging.redactPatterns`: 用于覆盖默认集的正则字符串列表

脱敏仅影响**控制台输出**，不会更改文件日志。

## 诊断 + OpenTelemetry

诊断是用于模型运行**和**消息流遥测（Webhooks、队列处理、会话状态）的结构化、机器可读事件。它们**不**替代日志；它们的存在是为了向指标、追踪和其他导出器提供数据。

诊断事件在进程内发出，但只有当启用诊断 + 导出器插件时，导出器才会附加。

### OpenTelemetry vs OTLP

- **OpenTelemetry (OTel)**：用于追踪、指标和日志的数据模型 + SDK。
- **OTLP**：用于将 OTel 数据导出到收集器/后端的传输协议。
- OpenClaw 目前通过 **OTLP/HTTP (protobuf)** 进行导出。

### 导出的信号

- **指标**：计数器 + 直方图（Token 使用量、消息流、队列处理）。
- **追踪**：用于模型使用 + Webhook/消息处理的 Span。
- **日志**：当启用 `diagnostics.otel.logs` 时通过 OTLP 导出。日志量可能很大；请留意 `logging.level` 和导出器过滤器。

### 诊断事件目录

模型使用情况：

- `model.usage`: Token、成本、时长、上下文、提供商/模型/渠道、会话 ID。

消息流：

- `webhook.received`: 每个渠道的 Webhook 入口。
- `webhook.processed`: Webhook 已处理 + 时长。
- `webhook.error`: Webhook 处理程序错误。
- `message.queued`: 消息已入队以供处理。
- `message.processed`: 结果 + 时长 + 可选错误。

队列 + 会话：

- `queue.lane.enqueue`: 命令队列通道入队 + 深度。
- `queue.lane.dequeue`: 命令队列通道出队 + 等待时间。
- `session.state`: 会话状态转换 + 原因。
- `session.stuck`: 会话卡住警告 + 持续时间。
- `run.attempt`: 运行重试/尝试元数据。
- `diagnostic.heartbeat`: 聚合计数器（Webhooks/队列/会话）。

### 启用诊断（无导出器）

如果您希望插件或自定义接收器能够获取诊断事件，请使用此选项：

```json
{
  "diagnostics": {
    "enabled": true
  }
}
```

### 诊断标志（定向日志）

使用标志开启额外的、定向的调试日志，而无需提升 `logging.level`。标志不区分大小写并支持通配符（例如 `telegram.*` 或 `*`）。

```json
{
  "diagnostics": {
    "flags": ["telegram.http"]
  }
}
```

环境变量覆盖（一次性）：

```
OPENCLAW_DIAGNOSTICS=telegram.http,telegram.payload
```

注意：

- 标志日志写入标准日志文件（与 `logging.file` 相同）。
- 输出仍根据 `logging.redactSensitive` 进行脱敏。
- 完整指南：[/diagnostics/flags](/diagnostics/flags)。

### 导出到 OpenTelemetry

诊断数据可以通过 `diagnostics-otel` 插件（OTLP/HTTP）导出。这
适用于任何接受 OTLP/HTTP 的 OpenTelemetry 收集器/后端。

```json
{
  "plugins": {
    "allow": ["diagnostics-otel"],
    "entries": {
      "diagnostics-otel": {
        "enabled": true
      }
    }
  },
  "diagnostics": {
    "enabled": true,
    "otel": {
      "enabled": true,
      "endpoint": "http://otel-collector:4318",
      "protocol": "http/protobuf",
      "serviceName": "openclaw-gateway",
      "traces": true,
      "metrics": true,
      "logs": true,
      "sampleRate": 0.2,
      "flushIntervalMs": 60000
    }
  }
}
```

注意：

- 您也可以通过 `openclaw plugins enable diagnostics-otel` 启用该插件。
- `protocol` 目前仅支持 `http/protobuf`。`grpc` 将被忽略。
- 指标包括令牌使用量、成本、上下文大小、运行持续时间以及消息流
  计数器和直方图（Webhooks、排队、会话状态、队列深度/等待）。
- 追踪/指标可通过 `traces` / `metrics` 切换（默认：开启）。追踪
  包括模型使用跨度以及启用时的 Webhook/消息处理跨度。
- 当您的收集器需要认证时，设置 `headers`。
- 支持的环境变量：`OTEL_EXPORTER_OTLP_ENDPOINT`，
  `OTEL_SERVICE_NAME`，`OTEL_EXPORTER_OTLP_PROTOCOL`。

### 导出的指标（名称 + 类型）

模型使用情况：

- `openclaw.tokens` (计数器，属性：`openclaw.token`，`openclaw.channel`，
  `openclaw.provider`，`openclaw.model`)
- `openclaw.cost.usd` (计数器，属性：`openclaw.channel`，`openclaw.provider`，
  `openclaw.model`)
- `openclaw.run.duration_ms` (直方图，属性：`openclaw.channel`，
  `openclaw.provider`，`openclaw.model`)
- `openclaw.context.tokens` (直方图，属性：`openclaw.context`，
  `openclaw.channel`，`openclaw.provider`，`openclaw.model`)

消息流：

- `openclaw.webhook.received` (计数器，属性：`openclaw.channel`，
  `openclaw.webhook`)
- `openclaw.webhook.error` (计数器，属性：`openclaw.channel`，
  `openclaw.webhook`)
- `openclaw.webhook.duration_ms` (直方图，属性：`openclaw.channel`，
  `openclaw.webhook`)
- `openclaw.message.queued` (计数器，属性：`openclaw.channel`，
  `openclaw.source`)
- `openclaw.message.processed` (计数器，属性：`openclaw.channel`，
  `openclaw.outcome`)
- `openclaw.message.duration_ms` (直方图，属性：`openclaw.channel`，
  `openclaw.outcome`)

队列 + 会话：

- `openclaw.queue.lane.enqueue` (计数器，属性：`openclaw.lane`)
- `openclaw.queue.lane.dequeue` (计数器，属性：`openclaw.lane`)
- `openclaw.queue.depth` (直方图，属性：`openclaw.lane` 或
  `openclaw.channel=heartbeat`)
- `openclaw.queue.wait_ms` (直方图，属性：`openclaw.lane`)
- `openclaw.session.state` (计数器，属性：`openclaw.state`，`openclaw.reason`)
- `openclaw.session.stuck` (计数器，属性：`openclaw.state`)
- `openclaw.session.stuck_age_ms` (直方图，属性：`openclaw.state`)
- `openclaw.run.attempt` (计数器，属性：`openclaw.attempt`)

### 导出的跨度（名称 + 关键属性）

- `openclaw.model.usage`
  - `openclaw.channel`, `openclaw.provider`, `openclaw.model`
  - `openclaw.sessionKey`, `openclaw.sessionId`
  - `openclaw.tokens.*` (input/output/cache_read/cache_write/total)
- `openclaw.webhook.processed`
  - `openclaw.channel`, `openclaw.webhook`, `openclaw.chatId`
- `openclaw.webhook.error`
  - `openclaw.channel`, `openclaw.webhook`, `openclaw.chatId`,
    `openclaw.error`
- `openclaw.message.processed`
  - `openclaw.channel`, `openclaw.outcome`, `openclaw.chatId`,
    `openclaw.messageId`, `openclaw.sessionKey`, `openclaw.sessionId`,
    `openclaw.reason`
- `openclaw.session.stuck`
  - `openclaw.state`, `openclaw.ageMs`, `openclaw.queueDepth`,
    `openclaw.sessionKey`, `openclaw.sessionId`

### 采样 + 刷新

- 追踪采样：`diagnostics.otel.sampleRate` (0.0–1.0, root spans only)。
- 指标导出间隔：`diagnostics.otel.flushIntervalMs` (min 1000ms)。

### 协议说明

- OTLP/HTTP 端点可通过 `diagnostics.otel.endpoint` 或
  `OTEL_EXPORTER_OTLP_ENDPOINT` 设置。
- 如果端点已包含 `/v1/traces` 或 `/v1/metrics`，则直接使用。
- 如果端点已包含 `/v1/logs`，则用于日志时直接使用。
- `diagnostics.otel.logs` 启用主日志器输出的 OTLP 日志导出。

### 日志导出行为

- OTLP 日志使用写入到 `logging.file` 的相同结构化记录。
- 遵循 `logging.level`（文件日志级别）。控制台脱敏 **不** 适用于 OTLP 日志。
- 大规模部署应优先使用 OTLP 收集器采样/过滤。

## 故障排查提示

- **网关不可达？** 请先运行 `openclaw doctor`。
- **日志为空？** 检查网关是否正在运行并向 `logging.file` 中的文件路径写入。
- **需要更多详情？** 将 `logging.level` 设置为 `debug` 或 `trace` 并重试。