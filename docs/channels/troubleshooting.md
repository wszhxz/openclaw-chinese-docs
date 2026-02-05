---
summary: "Channel-specific troubleshooting shortcuts (Discord/Telegram/WhatsApp)"
read_when:
  - A channel connects but messages don’t flow
  - Investigating channel misconfiguration (intents, permissions, privacy mode)
title: "Channel Troubleshooting"
---
# 通道故障排除

从以下开始：

```bash
openclaw doctor
openclaw channels status --probe
```

`channels status --probe` 在检测到常见的通道误配置时会打印警告，并包括一些小型实时检查（凭据、某些权限/成员身份）。

## 通道

- Discord: [/channels/discord#troubleshooting](/channels/discord#troubleshooting)
- Telegram: [/channels/telegram#troubleshooting](/channels/telegram#troubleshooting)
- WhatsApp: [/channels/whatsapp#troubleshooting-quick](/channels/whatsapp#troubleshooting-quick)

## Telegram 快速修复

- 日志显示 `HttpError: Network request for 'sendMessage' failed` 或 `sendChatAction` → 检查 IPv6 DNS。如果 `api.telegram.org` 首先解析为 IPv6 而主机缺乏 IPv6 出站连接，请强制使用 IPv4 或启用 IPv6。参见 [/channels/telegram#troubleshooting](/channels/telegram#troubleshooting)。
- 日志显示 `setMyCommands failed` → 检查到 `api.telegram.org` 的出站 HTTPS 和 DNS 可达性（常见于锁定的 VPS 或代理）。