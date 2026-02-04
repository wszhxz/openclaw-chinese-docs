---
summary: "Diagnostics flags for targeted debug logs"
read_when:
  - You need targeted debug logs without raising global logging levels
  - You need to capture subsystem-specific logs for support
title: "Diagnostics Flags"
---
# 诊断标志

诊断标志允许您启用有针对性的调试日志，而无需在全局范围内启用详细日志记录。标志是可选的，除非子系统检查它们，否则不会产生任何效果。

## 工作原理

- 标志是字符串（不区分大小写）。
- 您可以通过配置或环境变量覆盖来启用标志。
- 支持通配符：
  - `telegram.*` 匹配 `telegram.http`
  - `*` 启用所有标志

## 通过配置启用

```json
{
  "diagnostics": {
    "flags": ["telegram.http"]
  }
}
```

多个标志：

```json
{
  "diagnostics": {
    "flags": ["telegram.http", "gateway.*"]
  }
}
```

更改标志后重启网关。

## 环境变量覆盖（一次性）

```bash
OPENCLAW_DIAGNOSTICS=telegram.http,telegram.payload
```

禁用所有标志：

```bash
OPENCLAW_DIAGNOSTICS=0
```

## 日志输出位置

标志将日志输出到标准的诊断日志文件。默认情况下：

```
/tmp/openclaw/openclaw-YYYY-MM-DD.log
```

如果您设置了 `logging.file`，则使用该路径。日志格式为 JSONL（每行一个 JSON 对象）。根据 `logging.redactSensitive` 进行脱敏仍然适用。

## 提取日志

选择最新的日志文件：

```bash
ls -t /tmp/openclaw/openclaw-*.log | head -n 1
```

过滤 Telegram HTTP 诊断：

```bash
rg "telegram http error" /tmp/openclaw/openclaw-*.log
```

或者在重现问题时实时查看：

```bash
tail -f /tmp/openclaw/openclaw-$(date +%F).log | rg "telegram http error"
```

对于远程网关，您还可以使用 `openclaw logs --follow`（参见 [/cli/logs](/cli/logs))。

## 注意事项

- 如果 `logging.level` 设置得高于 `warn`，这些日志可能会被抑制。默认的 `info` 是合适的。
- 标志可以安全地保持启用状态；它们仅会影响特定子系统的日志量。
- 使用 [/logging](/logging) 更改日志目标、级别和脱敏设置。