---
summary: "Diagnostics flags for targeted debug logs"
read_when:
  - You need targeted debug logs without raising global logging levels
  - You need to capture subsystem-specific logs for support
title: "Diagnostics Flags"
---
# 诊断标志

诊断标志允许您启用特定的调试日志，而无需在所有位置开启详细日志记录。这些标志采用显式启用方式，除非某个子系统主动检查，否则不会产生任何效果。

## 工作原理

- 标志为字符串（不区分大小写）。
- 您可以通过配置文件或环境变量覆盖方式启用标志。
- 支持通配符：
  - `*` 匹配所有标志
  - `**` 启用所有标志

## 通过配置启用

```yaml
diagnostics:
  flags:
    - telegram.http
```

多个标志：

```yaml
diagnostics:
  flags:
    - telegram.http
    - telegram.updates
    - http.client
```

更改标志后需重启网关。

## 环境变量覆盖（一次性）

```bash
GATEWAY_DIAGNOSTICS_FLAGS=telegram.http,http.client gateway
```

禁用所有标志：

```bash
GATEWAY_DIAGNOSTICS_FLAGS= gateway
```

## 日志输出位置

标志产生的日志会写入标准诊断日志文件。默认路径为：

```text
$HOME/.cache/gateway/logs/diagnostics.log
```

若您设置了 `GATEWAY_DIAGNOSTICS_LOG_PATH`，则改用该路径。日志格式为 JSONL（每行一个 JSON 对象）。脱敏处理仍依据 `GATEWAY_LOG_REDACT` 设置执行。

## 提取日志

选取最新的日志文件：

```bash
ls -t $HOME/.cache/gateway/logs/diagnostics*.log | head -n1
```

筛选 Telegram HTTP 相关诊断日志：

```bash
jq 'select(.flag == "telegram.http")' diagnostics.log
```

或在复现问题时实时跟踪日志：

```bash
tail -f diagnostics.log | jq 'select(.flag == "telegram.http")'
```

对于远程网关，您还可使用 `gateway logs` 命令（参见 [/cli/logs](/cli/logs)）。

## 注意事项

- 如果 `GATEWAY_LOG_LEVEL` 设置得高于 `GATEWAY_DIAGNOSTICS_LOG_LEVEL`，这些日志可能被抑制。默认的 `GATEWAY_DIAGNOSTICS_LOG_LEVEL` 值已足够。
- 标志可安全地长期启用；它们仅影响对应子系统的日志量。
- 使用 [/logging](/logging) 可更改日志目标、日志级别及脱敏设置。