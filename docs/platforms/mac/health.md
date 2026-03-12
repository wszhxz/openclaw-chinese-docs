---
summary: "How the macOS app reports gateway/Baileys health states"
read_when:
  - Debugging mac app health indicators
title: "Health Checks"
---
# macOS上的健康检查

如何从菜单栏应用程序查看链接的频道是否健康。

## 菜单栏

- 状态点现在反映Baileys的健康状况：
  - 绿色：已链接 + 最近打开了套接字。
  - 橙色：正在连接/重试中。
  - 红色：已登出或探测失败。
- 第二行显示“linked · auth 12m”或显示失败原因。
- “运行健康检查”菜单项触发按需探测。

## 设置

- 常规选项卡增加了一个健康卡片，显示：链接认证年龄、会话存储路径/计数、上次检查时间、最后错误/状态码，以及运行健康检查/显示日志的按钮。
- 使用缓存快照，以便UI即时加载，并在离线时优雅地回退。
- **频道选项卡**显示频道状态 + WhatsApp/Telegram的控制（登录二维码、登出、探测、最后断开/错误）。

## 探测的工作原理

- 应用程序通过`openclaw health --json`每约60秒和按需通过`ShellExecutor`运行。探测加载凭证并报告状态而不发送消息。
- 分别缓存最后一次良好的快照和最后一次错误以避免闪烁；显示每个的时间戳。

## 当有疑问时

- 您仍然可以使用CLI流程在[网关健康](/gateway/health) (`openclaw status`, `openclaw status --deep`, `openclaw health --json`) 中，并跟踪`/tmp/openclaw/openclaw-*.log` 对于 `web-heartbeat` / `web-reconnect`。