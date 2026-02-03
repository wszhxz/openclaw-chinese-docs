---
summary: "CLI reference for `openclaw doctor` (health checks + guided repairs)"
read_when:
  - You have connectivity/auth issues and want guided fixes
  - You updated and want a sanity check
title: "doctor"
---
# `openclaw doctor`

健康检查 + 网关和通道的快速修复。

相关：

- 故障排除：[故障排除](/gateway/troubleshooting)
- 安全审计：[安全](/gateway/security)

## 示例

```bash
openclaw doctor
openclaw doctor --repair
openclaw doctor --deep
```

说明：

- 交互式提示（如密钥链/OAuth修复）仅在标准输入为TTY且未设置`--non-interactive`时运行。无头运行（如cron、Telegram、无终端环境）将跳过提示。
- `--fix`（等同于`--repair`）会将备份写入`~/.openclaw/openclaw.json.bak`，并删除未知配置键，列出每个被删除的键。

## macOS: `launchctl` 环境变量覆盖

如果你之前运行过`launchctl setenv OPENCLAW_GATEWAY_TOKEN ...`（或`...PASSWORD`），该值将覆盖你的配置文件，可能导致持续的“未授权”错误。

```bash
launchctl getenv OPENCLAW_GATEWAY_TOKEN
launchctl getenv OPENCLAW_GATEWAY_PASSWORD

launchctl unsetenv OPENCLAW_GATEWAY_TOKEN
launchctl unsetenv OPENCLAW_GATEWAY_PASSWORD
```