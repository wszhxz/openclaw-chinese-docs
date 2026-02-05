---
summary: "Health check steps for channel connectivity"
read_when:
  - Diagnosing WhatsApp channel health
title: "Health Checks"
---
# 健康检查 (CLI)

简要指南，用于验证通道连接性而无需猜测。

## 快速检查

- `openclaw status` — 本地摘要：网关可达性/模式、更新提示、链接通道认证年龄、会话 + 最近活动。
- `openclaw status --all` — 完整本地诊断（只读、彩色、适合调试粘贴）。
- `openclaw status --deep` — 还探测正在运行的网关（支持时按通道探测）。
- `openclaw health --json` — 请求正在运行的网关进行完整健康快照（仅限WS；无直接Baileys套接字）。
- 在WhatsApp/WebChat中单独发送`/status`以获取状态回复而不调用代理。
- 日志：跟踪`/tmp/openclaw/openclaw-*.log`并过滤`web-heartbeat`，`web-reconnect`，`web-auto-reply`，`web-inbound`。

## 深度诊断

- 磁盘上的凭据：`ls -l ~/.openclaw/credentials/whatsapp/<accountId>/creds.json`（修改时间应较近）。
- 会话存储：`ls -l ~/.openclaw/agents/<agentId>/sessions/sessions.json`（路径可以在配置中覆盖）。计数和最近收件人通过`status`显示。
- 重新链接流程：当日志中出现状态码409–515或`loggedOut`时使用`openclaw channels logout && openclaw channels login --verbose`。（注意：QR登录流程在配对后对状态515自动重启一次。）

## 当出现问题时

- `logged out` 或状态 409–515 → 使用`openclaw channels logout`然后`openclaw channels login`重新链接。
- 网关不可达 → 启动它：`openclaw gateway --port 18789`（如果端口繁忙，请使用`--force`）。
- 无入站消息 → 确认链接手机在线且发件人被允许(`channels.whatsapp.allowFrom`)；对于群聊，确保白名单+提及规则匹配(`channels.whatsapp.groups`，`agents.list[].groupChat.mentionPatterns`)。

## 专用“health”命令

`openclaw health --json`请求正在运行的网关进行其健康快照（CLI无直接通道套接字）。它报告可用时的链接凭据/认证年龄、每个通道探测摘要、会话存储摘要以及探测持续时间。如果网关不可达或探测失败/超时，则退出非零。使用`--timeout <ms>`覆盖默认的10秒。