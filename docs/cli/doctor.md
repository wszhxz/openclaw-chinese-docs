---
summary: "CLI reference for `openclaw doctor` (health checks + guided repairs)"
read_when:
  - You have connectivity/auth issues and want guided fixes
  - You updated and want a sanity check
title: "doctor"
---
# `openclaw doctor`

网关和通道的健康检查及快速修复。

相关文档：

- 故障排除：[Troubleshooting](/gateway/troubleshooting)
- 安全审计：[Security](/gateway/security)

## 示例

```bash
openclaw doctor
openclaw doctor --repair
openclaw doctor --deep
```

注意事项：

- 交互式提示（如钥匙串/OAuth修复）仅在stdin是TTY且`--non-interactive`未设置时运行。无头运行（cron、Telegram、无终端）将跳过提示。
- `--fix`（`--repair`的别名）会将备份写入`~/.openclaw/openclaw.json.bak`并删除未知配置键，列出每次移除的内容。

## macOS: `launchctl` 环境变量覆盖

如果您之前运行了`launchctl setenv OPENCLAW_GATEWAY_TOKEN ...`（或`...PASSWORD`），该值将覆盖您的配置文件，并可能导致持续的“未授权”错误。

```bash
launchctl getenv OPENCLAW_GATEWAY_TOKEN
launchctl getenv OPENCLAW_GATEWAY_PASSWORD

launchctl unsetenv OPENCLAW_GATEWAY_TOKEN
launchctl unsetenv OPENCLAW_GATEWAY_PASSWORD
```