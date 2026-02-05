---
summary: "How the macOS app reports gateway/Baileys health states"
read_when:
  - Debugging mac app health indicators
title: "Health Checks"
---
# macOS 上的健康检查

如何从菜单栏应用程序查看链接的通道是否健康。

## 菜单栏

- 状态点现在反映 Baileys 健康状况：
  - 绿色：已链接 + 套接字最近打开。
  - 橙色：正在连接/重试。
  - 红色：已登出或探测失败。
- 第二行显示"linked · auth 12m"或显示失败原因。
- "Run Health Check"菜单项触发按需探测。

## 设置

- 常规选项卡增加了一个健康卡片，显示：链接认证时间、会话存储路径/数量、上次检查时间、上次错误/状态码，以及运行健康检查/显示日志的按钮。
- 使用缓存快照以便 UI 立即加载并在离线时优雅回退。
- **通道选项卡** 显示通道状态以及 WhatsApp/Telegram 的控制功能（登录二维码、登出、探测、上次断开连接/错误）。

## 探测工作原理

- 应用程序每约 60 秒并通过 `ShellExecutor` 运行 `openclaw health --json`。探测加载凭据并报告状态而不发送消息。
- 分别缓存最后一次良好快照和最后一次错误以避免闪烁；显示每个的时间戳。

## 如有疑问

- 您仍可在 [网关健康](/gateway/health) 中使用 CLI 流程 (`openclaw status`, `openclaw status --deep`, `openclaw health --json`) 并监控 `/tmp/openclaw/openclaw-*.log` 以获取 `web-heartbeat` / `web-reconnect`。