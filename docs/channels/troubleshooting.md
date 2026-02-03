---
summary: "Channel-specific troubleshooting shortcuts (Discord/Telegram/WhatsApp)"
read_when:
  - A channel connects but messages don’t flow
  - Investigating channel misconfiguration (intents, permissions, privacy mode)
title: "Channel Troubleshooting"
---
# 通道故障排除

首先执行以下命令：

```bash
openclaw doctor
openclaw channels status --probe
```

`channels status --probe` 会在检测到常见的通道配置错误时打印警告，并包含一些小型实时检查（凭证、部分权限/成员资格）。

## 通道

- Discord: [/channels/discord#troubleshooting](/channels/discord#troubleshooting)
- Telegram: [/channels/telegram#troubleshooting](/channels/telegram#troubleshooting)
- WhatsApp: [/channels/whatsapp#troubleshooting-quick](/channels/whatsapp#troubleshooting-quick)

## Telegram 快速修复

- 日志显示 `HttpError: Network request for 'sendMessage' failed` 或 `sendChatAction` → 检查 IPv6 DNS。如果 `api.telegram.org` 优先解析为 IPv6 且主机缺乏 IPv6 出站连接，可强制使用 IPv4 或启用 IPv6。详见 [/channels/telegram#troubleshooting](/channels/telegram#troubleshooting)。
- 日志显示 `setMyCommands failed` → 检查对 `api.telegram.org` 的 outbound HTTPS 和 DNS 可达性（常见于受限的 VPS 或代理环境）。