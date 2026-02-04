---
summary: "How the macOS app reports gateway/Baileys health states"
read_when:
  - Debugging mac app health indicators
title: "Health Checks"
---
# macOS上的健康检查

如何从菜单栏应用程序查看链接通道是否正常。

## 菜单栏

- 状态点现在反映Baileys的健康状况：
  - 绿色：已链接 + 最近打开套接字。
  - 橙色：正在连接/重试。
  - 红色：已登出或探测失败。
- 第二行显示“已链接 · 认证 12分钟”或显示失败原因。
- “运行健康检查”菜单项触发按需探测。

## 设置

- 常规选项卡新增一个健康卡片，显示：已链接认证时间、会话存储路径/数量、上次检查时间、上次错误/状态码，以及运行健康检查/显示日志的按钮。
- 使用缓存的快照，因此UI可以瞬间加载，并在网络离线时优雅地回退。
- **通道选项卡**显示通道状态以及WhatsApp/Telegram（登录二维码、登出、探测、上次断开/错误）的控制。

## 探测的工作原理

- 应用程序每隔约60秒通过`ShellExecutor`运行`openclaw health --json`，并按需运行。探测加载凭据并报告状态而不发送消息。
- 分别缓存最后一个良好的快照和最后一个错误以避免闪烁；显示每个的时间戳。

## 存疑时

- 你仍然可以使用[网关健康](/gateway/health)中的CLI流程 (`openclaw status`, `openclaw status --deep`, `openclaw health --json`) 并跟踪`/tmp/openclaw/openclaw-*.log`的`web-heartbeat` / `web-reconnect`。