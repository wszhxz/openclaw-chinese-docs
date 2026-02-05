---
summary: "Logging surfaces, file logs, WS log styles, and console formatting"
read_when:
  - Changing logging output or formats
  - Debugging CLI or gateway output
title: "Logging"
---
# 日志记录

对于面向用户的概述（CLI + 控制UI + 配置），请参阅 [/logging](/logging)。

OpenClaw 有两个日志“表面”：

- **控制台输出**（你在终端/调试UI中看到的内容）。
- **文件日志**（JSON 行）由网关日志器写入。

## 基于文件的日志记录器

- 默认滚动日志文件位于 `/tmp/openclaw/`（每天一个文件）：`openclaw-YYYY-MM-DD.log`
  - 日期使用网关主机的本地时区。
- 日志文件路径和级别可以通过 `~/.openclaw/openclaw.json` 进行配置：
  - `logging.file`
  - `logging.level`

文件格式是每行一个 JSON 对象。

控制UI 的日志选项卡通过网关跟踪此文件 (`logs.tail`)。
CLI 也可以这样做：

```bash
openclaw logs --follow
```

**详细模式与日志级别**

- **文件日志** 仅由 `logging.level` 控制。
- `--verbose` 仅影响 **控制台详细程度**（和 WS 日志样式）；它不会提高文件日志级别。
- 要在文件日志中捕获仅详细的日志信息，请将 `logging.level` 设置为 `debug` 或
  `trace`。

## 控制台捕获

CLI 捕获 `console.log/info/warn/error/debug/trace` 并将其写入文件日志，
同时仍打印到 stdout/stderr。

你可以独立调整控制台详细程度：

- `logging.consoleLevel`（默认 `info`）
- `logging.consoleStyle` (`pretty` | `compact` | `json`)

## 工具摘要重写

详细的工具摘要（例如 `🛠️ Exec: ...`）可以在它们到达控制台流之前屏蔽敏感令牌。这仅适用于 **工具**，不会更改文件日志。

- `logging.redactSensitive`: `off` | `tools`（默认: `tools`）
- `logging.redactPatterns`: 正则表达式字符串数组（覆盖默认值）
  - 使用原始正则表达式字符串（自动 `gi`），或者如果需要自定义标志则使用 `/pattern/flags`。
  - 匹配项通过保留前 6 和最后 4 个字符进行屏蔽（长度 >= 18），否则 `***`。
  - 默认值涵盖常见的密钥分配、CLI 标志、JSON 字段、承载头、PEM 块和流行的令牌前缀。

## 网关 WebSocket 日志

网关以两种模式打印 WebSocket 协议日志：

- **正常模式（无 `--verbose`）**：仅打印“有趣”的 RPC 结果：
  - 错误 (`ok=false`)
  - 慢调用（默认阈值: `>= 50ms`）
  - 解析错误
- **详细模式 (`--verbose`)**：打印所有 WS 请求/响应流量。

### WS 日志样式

`openclaw gateway` 支持每个网关的样式切换：

- `--ws-log auto`（默认）：正常模式进行了优化；详细模式使用紧凑输出
- `--ws-log compact`：详细模式下使用配对的请求/响应紧凑输出
- `--ws-log full`：详细模式下使用完整的帧输出
- `--compact`：`--ws-log compact` 的别名

示例：

```bash
# optimized (only errors/slow)
openclaw gateway

# show all WS traffic (paired)
openclaw gateway --verbose --ws-log compact

# show all WS traffic (full meta)
openclaw gateway --verbose --ws-log full
```

## 控制台格式化（子系统日志记录）

控制台格式化程序是 **终端感知** 的，并打印一致的、带有前缀的行。
子系统日志记录器保持输出分组且可扫描。

行为：

- **每行的子系统前缀**（例如 `[gateway]`，`[canvas]`，`[tailscale]`）
- **子系统颜色**（每个子系统稳定）加上级别着色
- **当输出是终端或环境看起来像富终端时使用颜色** (`TERM`/`COLORTERM`/`TERM_PROGRAM`)，尊重 `NO_COLOR`
- **缩短的子系统前缀**：丢弃前面的 `gateway/` + `channels/`，保留最后两个段（例如 `whatsapp/outbound`）
- **按子系统划分的子日志记录器**（自动前缀 + 结构化字段 `{ subsystem }`）
- **`logRaw()`** 用于 QR/UX 输出（无前缀，无格式）
- **控制台样式**（例如 `pretty | compact | json`）
- **控制台日志级别** 与文件日志级别分开（文件在 `logging.level` 设置为 `debug`/`trace` 时保留完整细节）
- **WhatsApp 消息正文** 记录在 `debug`（使用 `--verbose` 查看它们）

这保持现有文件日志的稳定性，同时使交互式输出可扫描。