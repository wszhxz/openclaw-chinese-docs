---
summary: "CLI reference for `openclaw doctor` (health checks + guided repairs)"
read_when:
  - You have connectivity/auth issues and want guided fixes
  - You updated and want a sanity check
title: "doctor"
---
# `openclaw doctor`

针对网关和信道的健康检查 + 快速修复。

相关：

- 故障排除：[故障排除](/gateway/troubleshooting)
- 安全审计：[安全性](/gateway/security)

## 示例

```bash
openclaw doctor
openclaw doctor --repair
openclaw doctor --deep
```

注意：

- 交互式提示（如 keychain/OAuth 修复）仅在 stdin 为 TTY 且 `--non-interactive` **未** 设置时运行。无头运行（cron、Telegram、无终端）将跳过提示。
- `--fix`（`--repair` 的别名）将备份写入 `~/.openclaw/openclaw.json.bak` 并丢弃未知的配置键，列出每个移除项。
- 状态完整性检查现在可以检测 sessions 目录中的孤立 transcript 文件，并可以将它们归档为 `.deleted.<timestamp>` 以安全地回收空间。
- Doctor 包含 memory-search 就绪检查，并且在缺少 embedding credentials 时可以推荐 `openclaw configure --section model`。
- 如果启用了 sandbox mode 但 Docker 不可用，doctor 会报告一个高信号警告并提供补救措施（`install Docker` 或 `openclaw config set agents.defaults.sandbox.mode off`）。

## macOS：`launchctl` 环境变量覆盖

如果您之前运行过 `launchctl setenv OPENCLAW_GATEWAY_TOKEN ...`（或 `...PASSWORD`），该值将覆盖您的配置文件，并可能导致持续的"unauthorized"错误。

```bash
launchctl getenv OPENCLAW_GATEWAY_TOKEN
launchctl getenv OPENCLAW_GATEWAY_PASSWORD

launchctl unsetenv OPENCLAW_GATEWAY_TOKEN
launchctl unsetenv OPENCLAW_GATEWAY_PASSWORD
```