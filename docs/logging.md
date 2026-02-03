---
summary: "Logging overview: file logs, console output, CLI tailing, and the Control UI"
read_when:
  - You need a beginner-friendly overview of logging
  - You want to configure log levels or formats
  - You are troubleshooting and need to find logs quickly
title: "Logging"
---
# 日志记录

OpenClaw 的日志记录在两个位置：

- **文件日志**（JSON 行格式），由网关写入。
- **控制台输出**，显示在终端和控制界面中。

本页面解释了日志存储的位置、如何阅读日志以及如何配置日志级别和格式。

## 日志存储位置

默认情况下，网关会在以下路径下写入一个滚动日志文件：

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

## 如何阅读日志

### CLI：实时尾随（推荐）

使用 CLI 通过 RPC 尾随网关日志文件：

```bash
openclaw logs --follow
```

输出模式：

- **TTY 会话**：美观、带颜色、结构化的日志行。
- **非 TTY 会话**：纯文本。
- `--json`：按行分隔的 JSON（每行一个日志事件）。
- `--plain`：在 TTY 会话中强制使用纯文本。
- `--no-color`：禁用 ANSI 颜色。

在 JSON 模式下，CLI 会输出带有 `type` 标签的对象：

- `meta`：流元数据（文件、游标、大小）
- `log`：解析后的日志条目
- `notice`：截断/旋转提示
- `raw`：未解析的日志行

如果网关不可达，CLI 会打印一个简短提示以运行：

```bash
openclaw doctor
```

### 控制界面（网页）

控制界面的 **日志** 选项卡使用 `logs.tail` 尾随相同的文件。查看 [/web/control-ui](/web/control-ui) 了解如何打开它。

### 仅频道日志

要过滤频道活动（如 WhatsApp/Telegram 等），使用：

```bash
openclaw channels logs --channel whatsapp
```

## 日志格式

### 文件日志（JSONL）

日志文件中的每一行都是一个 JSON 对象。CLI 和控制界面解析这些条目以渲染结构化输出（时间、级别、子系统、消息）。

### 控制台输出

控制台日志是 **TTY 意识的**，并为可读性进行了格式化：

- 子系统前缀（例如 `gateway/channels/whatsapp`）
- 级别着色（info/warn/error）
- 可选的紧凑或 JSON 模式

控制台格式由 `logging.consoleStyle` 控制。

## 配置日志记录

所有日志记录配置都位于 `~/.openclaw/openclaw.json` 中的 `logging` 部分。

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

- `logging.level`：**文件日志**（JSONL）级别。
- `logging.consoleLevel`：**控制台**详细程度级别。

`--verbose` 仅影响控制台输出；它不会更改文件日志级别。

### 控制台样式

`logging.consoleStyle`：

- `pretty`：人性化、带颜色、带时间戳。
- `compact`：更紧凑的输出（适合长时间会话）。
- `json`：按行分隔的 JSON（每行一个日志事件）。

### 敏感信息过滤

`redactSensitive`：控制是否过滤敏感信息。

### 过滤模式

`redactPatterns`：定义过滤的正则表达式模式。

## 诊断日志

### 诊断事件

- `model.usage`：模型使用情况。
- `webhook.received`：接收的 Webhook。
- `webhook.error`：Webhook 错误。
- `message.processed`：处理的消息。
- `session.stuck`：会话卡住。

### 指标

- `queue.depth`：队列深度。
- `queue.wait`：队列等待时间。
- `session.state`：会话状态。
- `run.attempt`：运行尝试次数。

### 采样与刷新

- 跟踪采样：`diagnostics.otel.sampleRate`（0.0–1.0，仅根跟踪）。
- 指标导出间隔：`diagnostics.otel.flushIntervalMs`（最小 1000ms）。

## 协议说明

- OTLP/HTTP 端点可通过 `diagnostics.otel.endpoint` 或 `OTEL_EXPORTER_OTLP_ENDPOINT` 设置。
- 如果端点已包含 `/v1/traces` 或 `/v1/metrics`，则直接使用。
- 如果端点已包含 `/v1/logs`，则直接用于日志。
- `diagnostics.otel.logs` 启用 OTLP 日志导出以供主日志器输出。

## 日志导出行为

- OTLP 日志使用写入 `logging.file` 的相同结构化记录。
- 尊重 `logging.level`（文件日志级别）。控制台过滤不适用于 OTLP 日志。
- 高流量安装应优先使用 OTLP 收集器的采样/过滤。

## 故障排除提示

- **网关不可达？** 首先运行 `openclaw doctor`。
- **日志为空？** 检查网关是否正在运行并写入 `logging.file` 中的文件路径。
- **需要更多详细信息？** 将 `logging.level` 设置为 `debug` 或 `trace` 并重试。