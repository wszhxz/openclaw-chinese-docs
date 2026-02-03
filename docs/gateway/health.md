---
summary: "Health check steps for channel connectivity"
read_when:
  - Diagnosing WhatsApp channel health
title: "Health Checks"
---
# 健康检查（CLI）

无需猜测即可验证通道连接性的简要指南。

## 快速检查

- `openclaw status` — 本地摘要：网关可达性/模式、更新提示、已链接通道认证年龄、会话 + 最近活动。
- `openclaw status --all` — 完整本地诊断（只读、带颜色、可安全粘贴用于调试）。
- `openclaw status --deep` — 同时探测正在运行的网关（在支持时按通道探测）。
- `openclaw health --json` — 向正在运行的网关请求完整健康快照（仅 WebSocket；无直接 Baileys 套接字）。
- 在 WhatsApp/WebChat 中发送 `/status` 作为独立消息，可获取状态回复而无需调用代理。
- 日志：查看 `/tmp/openclaw/openclaw-*.log` 并过滤 `web-heartbeat`、`web-reconnect`、`web-auto-reply`、`web-inbound`。

## 深度诊断

- 磁盘上的凭证：`ls -l ~/.openclaw/credentials/whatsapp/<accountId>/creds.json`（mtime 应为近期）。
- 会话存储：`ls -l ~/.openclaw/agents/<agentId>/sessions/sessions.json`（路径可在配置中覆盖）。计数和最近收件人通过 `status` 显示。
- 重新链接流程：当状态码 409–515 或 `loggedOut` 出现在日志中时，执行 `openclaw channels logout && openclaw channels login --verbose`。（注意：QR 登录流程在配对后状态码 515 时会自动重启一次。）

## 当出现问题时

- `logged out` 或状态码 409–515 → 使用 `openclaw channels logout` 然后 `openclaw channels login` 重新链接。
- 网关不可达 → 启动网关：`openclaw gateway --port 18789`（如果端口被占用，使用 `--force`）。
- 无入站消息 → 确认已链接的手机在线且发送方被允许（`channels.whatsapp.allowFrom`）；对于群聊，确保允许列表 + 提及规则匹配（`channels.whatsapp.groups`、`agents.list[].groupChat.mentionPatterns`）。

## 专用的 "health" 命令

`openclaw health --json` 会向正在运行的网关请求其健康快照（CLI 不会直接使用通道套接字）。它会报告可用的已链接凭证/认证年龄、每通道探测摘要、会话存储摘要和探测持续时间。如果网关不可达或探测失败/超时，它将退出非零状态。使用 `--timeout <ms>` 可覆盖默认的 10 秒超时时间。