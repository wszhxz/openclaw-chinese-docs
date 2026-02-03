---
summary: "Logging surfaces, file logs, WS log styles, and console formatting"
read_when:
  - Changing logging output or formats
  - Debugging CLI or gateway output
title: "Logging"
---
# 日志记录

对于面向用户的概览（CLI + 控制界面 + 配置），请参见 [/logging](/logging)。

OpenClaw 有两个日志“输出面”：

- **控制台输出**（你在终端/调试界面看到的内容）。
- **文件日志**（JSON 行格式），由网关日志记录器写入。

## 文件日志记录器

- 默认滚动日志文件位于 `/tmp/openclaw/`（每天一个文件）：`openclaw-YYYY-MM-DD.log`
  - 日期使用网关主机的本地时区。
- 日志文件路径和级别可通过 `~/.openclaw/openclaw.json` 配置：
  - `logging.file`
  - `logging.level`

文件格式为每行一个 JSON 对象。

控制界面日志标签通过网关（`logs.tail`）实时查看该文件。
CLI 也可以执行相同操作：

```bash
openclaw logs --follow
```

**详细模式 vs 日志级别**

- **文件日志**仅由 `logging.level` 控制。
- `--verbose` 仅影响 **控制台输出的详细程度**（以及 WS 日志格式）；它 **不会** 提高文件日志级别。
- 若要在文件日志中捕获仅详细模式的详细信息，请将 `logging.level` 设置为 `debug` 或 `trace`。

## 控制台捕获

CLI 捕获 `console.log/info/warn/error/debug/trace` 并将其写入文件日志，同时仍打印到 stdout/stderr。

你可以通过以下方式独立调整控制台输出的详细程度：

- `logging.consoleLevel`（默认 `info`）
- `logging.consoleStyle`（`pretty` | `compact` | `json`）

## 工具摘要内容过滤

详细工具摘要（例如 `🛠️ Exec: ...`）会在到达控制台流之前屏蔽敏感令牌。这是 **仅工具相关** 的功能，不会更改文件日志。

- `logging.redactSensitive`: `off` | `tools`（默认：`tools`）
- `logging.redactPatterns`: 一个正则表达式字符串数组（覆盖默认值）
  - 使用原始正则表达式字符串（自动 `gi`），或 `/pattern/flags` 如果需要自定义标志。
  - 匹配内容会保留前 6 个字符和后 4 个字符（长度 >= 18），否则用 `***` 替代。
  - 默认值覆盖常见的密钥分配、CLI 标志、JSON 字段、Bearer 头部、PEM 块以及流行的令牌前缀。

## 网关 WebSocket 日志

网关以两种模式打印 WebSocket 协议日志：

- **正常模式（无 `--verbose`）**：仅打印“有趣”的 RPC 结果：
  - 错误（`ok=false`）
  - 慢调用（默认阈值：`>= 50ms`）
  - 解析错误
- **详细模式（`--verbose`）**：打印所有 WS 请求/响应流量。

### WS 日志格式

`openclaw gateway` 支持每个网关的格式切换：

- `--ws-log auto`（默认）：正常模式优化；详细模式使用紧凑输出
- `--ws-log compact`：详细模式下紧凑输出（配对的请求/响应）
- `--ws-log full`：详细模式下每帧完整输出
- `--compact`：`--ws-log compact` 的别名

示例：

```bash
# 优化（仅错误/慢调用）
openclaw gateway

# 显示所有 WS 流量（配对）
openclaw gateway --verbose --ws-log compact

# 显示所有 WS 流量（完整元数据）
openclaw gateway --verbose --ws-log full
```

## 控制台格式化（子系统日志记录）

控制台格式化器 **终端感知**，并打印一致、带前缀的行。
子系统日志记录器保持输出分组且易于扫描。

行为：

- **每行的子系统前缀**（例如 `[gateway]`、`[canvas]`、`[tailscale]`）
- **子系统颜色**（每个子系统稳定）加上日志级别颜色
- **当输出是 TTY 或环境看起来像富终端时使用颜色**（`TERM`/`COLORTERM`/`TERM_PROGRAM`），尊重 `NO_COLOR`
- **缩短的子系统前缀**：去掉前缀 `gateway/` + `channels/`，保留最后两个段（例如 `whatsapp/outbound`）
- **按子系统分的日志记录器**（自动前缀 + 结构化字段 `{ subsystem }`）
- **`logRaw()`** 用于 QR/UX 输出（无前缀，无格式化）
- **控制台样式**（例如 `pretty | compact | json`）
- **控制台日志级别**与文件日志级别独立（当 `logging.level` 设置为 `debug`/`trace` 时，文件保留完整细节）
- **WhatsApp 消息正文**在 `debug` 级别记录（使用 `--verbose` 可查看）

这在保持现有文件日志稳定的同时，使交互式输出易于扫描。