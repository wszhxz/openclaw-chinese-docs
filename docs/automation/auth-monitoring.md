---
summary: "Monitor OAuth expiry for model providers"
read_when:
  - Setting up auth expiry monitoring or alerts
  - Automating Claude Code / Codex OAuth refresh checks
title: "Auth Monitoring"
---
# 认证监控

OpenClaw 通过 `openclaw models status` 暴露 OAuth 过期健康状态。使用该功能进行自动化和告警；脚本是手机工作流程的可选附加项。

## 推荐：CLI 检查（便携）

```bash
openclaw models status --check
```

退出码：

- `0`: 正常
- `1`: 凭证过期或缺失
- `2`: 即将过期（24小时内）

这适用于 cron/systemd，且无需额外脚本。

## 可选脚本（运维 / 手机工作流程）

这些脚本位于 `scripts/` 下，并且是**可选**的。它们假设可以访问网关主机的 SSH，并针对 systemd + Termux 进行了优化。

- `scripts/claude-auth-status.sh` 现在使用 `openclaw models status --json` 作为
  真实来源（如果 CLI 不可用，则回退到直接文件读取），因此请在定时器中保留 `openclaw` 在 `PATH` 上。
- `scripts/auth-monitor.sh`: cron/systemd 定时器目标；发送告警（ntfy 或手机）。
- `scripts/systemd/openclaw-auth-monitor.{service,timer}`: systemd 用户定时器。
- `scripts/claude-auth-status.sh`: Claude Code + OpenClaw 认证检查器（full/json/simple）。
- `scripts/mobile-reauth.sh`: 通过 SSH 的引导重新认证流程。
- `scripts/termux-quick-auth.sh`: 单击小部件状态 + 打开认证 URL。
- `scripts/termux-auth-widget.sh`: 完整的引导小部件流程。
- `scripts/termux-sync-widget.sh`: 同步 Claude Code 凭证 → OpenClaw。

如果您不需要手机自动化或 systemd 定时器，请跳过这些脚本。