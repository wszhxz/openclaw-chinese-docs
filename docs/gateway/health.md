---
summary: "Health check steps for channel connectivity"
read_when:
  - Diagnosing WhatsApp channel health
title: "Health Checks"
---
# 健康检查（CLI）

无需猜测即可快速验证通道连接状态的简明指南。

## 快速检查

- `openclaw status` — 本地摘要：网关可达性/模式、更新提示、已关联通道的认证时效、会话数 + 最近活动。
- `openclaw status --all` — 完整本地诊断（只读、带颜色输出，可安全粘贴用于调试）。
- `openclaw status --deep` — 同时探测正在运行的网关（在支持时按通道分别探测）。
- `openclaw health --json` — 向正在运行的网关请求完整的健康快照（仅限 WebSocket；不直接访问 Baileys socket）。
- 在 WhatsApp/WebChat 中单独发送 `/status` 消息，即可获得状态回复，无需调用代理。
- 日志：执行 `tail `/tmp/openclaw/openclaw-*.log`` 并筛选关键词 `web-heartbeat`、`web-reconnect`、`web-auto-reply`、`web-inbound`。

## 深度诊断

- 磁盘上的凭据：检查 `ls -l ~/.openclaw/credentials/whatsapp/<accountId>/creds.json`（修改时间应为近期）。
- 会话存储：检查 `ls -l ~/.openclaw/agents/<agentId>/sessions/sessions.json`（路径可在配置中覆盖）。会话数量与最近接收方信息可通过 `status` 获取。
- 重新关联流程：当日志中出现状态码 409–515 或 `loggedOut` 时，执行 `openclaw channels logout && openclaw channels login --verbose`。（注意：QR 登录流程在配对后，若遇到状态码 515 会自动重试一次。）

## 出现故障时

- 遇到 `logged out` 或状态码 409–515 → 使用 `openclaw channels logout` 重新关联，然后执行 `openclaw channels login`。
- 网关不可达 → 启动网关：运行 `openclaw gateway --port 18789`（若端口被占用，请改用 `--force`）。
- 无入站消息 → 确认已关联的手机在线，且发送方已被允许（`channels.whatsapp.allowFrom`）；对于群聊，请确保白名单及提及规则匹配（`channels.whatsapp.groups`、`agents.list[].groupChat.mentionPatterns`）。

## 专用 “health” 命令

`openclaw health --json` 向正在运行的网关请求其健康快照（CLI 不直接建立通道 socket）。它会在可用时报告已关联的凭据/认证时效、各通道探测摘要、会话存储摘要以及探测耗时。若网关不可达或探测失败/超时，则以非零退出码退出。使用 `--timeout <ms>` 可覆盖默认的 10 秒超时。