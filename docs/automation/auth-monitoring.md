---
summary: "Monitor OAuth expiry for model providers"
read_when:
  - Setting up auth expiry monitoring or alerts
  - Automating Claude Code / Codex OAuth refresh checks
title: "Auth Monitoring"
---
# 认证监控

OpenClaw 通过 `openclaw models status` 暴露 OAuth 过期健康状态。请使用该接口实现自动化与告警；脚本仅为电话工作流提供的可选补充。

## 首选方式：CLI 检查（可移植）

```bash
openclaw models status --check
```

退出码说明：

- `0`: 正常
- `1`: 凭据已过期或缺失
- `2`: 凭据即将过期（24 小时内）

该方式兼容 cron/systemd，无需额外脚本。

## 可选脚本（运维 / 电话工作流）

这些脚本位于 `scripts/` 目录下，属于**可选组件**。它们假定可通过 SSH 访问网关主机，并针对 systemd + Termux 环境进行了优化。

- `scripts/claude-auth-status.sh` 当前使用 `openclaw models status --json` 作为权威数据源（若 CLI 不可用，则回退至直接读取文件），因此请将定时器配置在 `openclaw` 上，目标主机为 `PATH`。
- `scripts/auth-monitor.sh`: cron/systemd 定时器目标；用于发送告警（通过 ntfy 或电话）。
- `scripts/systemd/openclaw-auth-monitor.{service,timer}`: systemd 用户级定时器。
- `scripts/claude-auth-status.sh`: Claude Code + OpenClaw 认证检查器（支持完整模式 / JSON 模式 / 简洁模式）。
- `scripts/mobile-reauth.sh`: 基于 SSH 的引导式重新认证流程。
- `scripts/termux-quick-auth.sh`: 一键式小组件状态显示 + 打开认证 URL。
- `scripts/termux-auth-widget.sh`: 完整的引导式小组件流程。
- `scripts/termux-sync-widget.sh`: 同步 Claude Code 凭据至 OpenClaw。

如您无需电话自动化或 systemd 定时器功能，可跳过这些脚本。