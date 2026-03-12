---
summary: "Logging surfaces, file logs, WS log styles, and console formatting"
read_when:
  - Changing logging output or formats
  - Debugging CLI or gateway output
title: "Logging"
---
# 日志记录

有关面向用户的概览（CLI + 控制界面 + 配置），请参阅 [/logging](/logging)。

OpenClaw 具有两个日志“输出面”：

- **控制台输出**（您在终端 / 调试界面中看到的内容）。
- **文件日志**（JSON 行格式），由网关日志记录器写入。

## 基于文件的日志记录器

- 默认滚动日志文件位于 `/tmp/openclaw/`（每天一个文件）：`openclaw-YYYY-MM-DD.log`
  - 日期采用网关主机的本地时区。
- 日志文件路径和日志级别可通过 `~/.openclaw/openclaw.json` 进行配置：
  - `logging.file`
  - `logging.level`

文件格式为每行一个 JSON 对象。

控制界面中的“日志”标签页通过网关（`logs.tail`）实时跟踪该文件。  
CLI 也可执行相同操作：

```bash
openclaw logs --follow
```

**详细模式（verbose）与日志级别**

- **文件日志**仅由 `logging.level` 控制。
- `--verbose` 仅影响 **控制台详细程度**（以及 WebSocket 日志样式）；它 **不会** 提升文件日志级别。
- 若要在文件日志中捕获仅限详细模式的信息，请将 `logging.level` 设为 `debug` 或 `trace`。

## 控制台捕获

CLI 捕获 `console.log/info/warn/error/debug/trace` 并将其写入文件日志，同时仍输出到 stdout/stderr。

您可独立调节控制台详细程度，方式如下：

- `logging.consoleLevel`（默认值为 `info`）
- `logging.consoleStyle`（`pretty` | `compact` | `json`）

## 工具摘要脱敏处理

详细的工具摘要（例如 `🛠️ Exec: ...`）可在其进入控制台流之前对敏感令牌进行掩码处理。此功能 **仅适用于工具**，且不会修改文件日志。

- `logging.redactSensitive`：`off` | `tools`（默认值：`tools`）
- `logging.redactPatterns`：正则表达式字符串数组（覆盖默认值）
  - 使用原始正则表达式字符串（自动 `gi`），或如需自定义标志，则使用 `/pattern/flags`。
  - 匹配项将被掩码：保留前 6 位和后 4 位字符（总长度 ≥ 18），否则使用 `***`。
  - 默认规则覆盖常见的密钥赋值、CLI 标志、JSON 字段、Bearer 请求头、PEM 数据块及主流令牌前缀。

## 网关 WebSocket 日志

网关以两种模式打印 WebSocket 协议日志：

- **常规模式（未启用 `--verbose`）**：仅打印“值得关注”的 RPC 结果：
  - 错误（`ok=false`）
  - 耗时较长的调用（默认阈值：`>= 50ms`）
  - 解析错误
- **详细模式（启用 `--verbose`）**：打印全部 WebSocket 请求/响应流量。

### WebSocket 日志样式

`openclaw gateway` 支持按网关设置样式开关：

- `--ws-log auto`（默认）：常规模式已优化；详细模式使用紧凑输出
- `--ws-log compact`：详细模式下使用紧凑输出（成对显示请求/响应）
- `--ws-log full`：详细模式下显示完整帧级输出
- `--compact`：等同于 `--ws-log compact`

示例：

```bash
# optimized (only errors/slow)
openclaw gateway

# show all WS traffic (paired)
openclaw gateway --verbose --ws-log compact

# show all WS traffic (full meta)
openclaw gateway --verbose --ws-log full
```

## 控制台格式化（子系统日志）

控制台格式化器具备 **TTY 感知能力**，输出一致且带前缀的行。  
各子系统日志记录器确保输出分组清晰、易于扫描。

行为说明：

- 每行均带有 **子系统前缀**（例如 `[gateway]`、`[canvas]`、`[tailscale]`）
- **子系统颜色**（各子系统颜色稳定）并叠加日志级别颜色
- 当输出目标为 TTY 或环境类似富终端（`TERM`/`COLORTERM`/`TERM_PROGRAM`）时启用彩色输出，并尊重 `NO_COLOR`
- **缩短的子系统前缀**：去除开头的 `gateway/` 和 `channels/`，仅保留最后两个段（例如 `whatsapp/outbound`）
- **按子系统划分的子日志记录器**（自动添加前缀 + 结构化字段 `{ subsystem }`）
- **`logRaw()`** 用于 QR/UX 输出（无前缀、无格式化）
- **控制台样式**（例如 `pretty | compact | json`）
- **控制台日志级别** 与文件日志级别相互独立（当 `logging.level` 设为 `debug`/`trace` 时，文件日志仍保留全部细节）
- **WhatsApp 消息正文** 在 `debug` 级别记录（使用 `--verbose` 可查看）

此举在保持现有文件日志稳定性的同时，显著提升交互式输出的可读性与可扫描性。