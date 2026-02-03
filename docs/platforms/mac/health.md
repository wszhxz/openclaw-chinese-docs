---
summary: "How the macOS app reports gateway/Baileys health states"
read_when:
  - Debugging mac app health indicators
title: "Health Checks"
---
# macOS上的健康检查

如何通过菜单栏应用查看已连接频道是否健康。

## 菜单栏

- 状态点现在反映Baileys健康状态：
  - 绿色：已连接 + 最近打开socket。
  - 橙色：正在连接/重试中。
  - 红色：已登出或探测失败。
- 第二行显示“已连接 · 认证 12分钟”或显示失败原因。
- “运行健康检查”菜单项触发按需探测。

## 设置

- 通用标签页新增健康卡，显示：已连接认证时长、会话存储路径/数量、上次检查时间、上次错误/状态码，以及“运行健康检查” / “显示日志”按钮。
- 使用缓存快照以确保界面瞬间加载，并在离线时优雅降级。
- **频道标签页**展示频道状态 + WhatsApp/Telegram的控制功能（登录二维码、登出、探测、最后断开/错误）。

## 探测工作原理

- 应用通过ShellExecutor每约60秒运行一次`openclaw health --json`，并支持按需触发。探测加载凭据并报告状态，无需发送消息。
- 分别缓存最后一次成功的快照和最后一次错误，以避免闪烁；显示每个时间戳。

## 不确定时

- 仍可使用[网关健康](/gateway/health)中的CLI流程（`openclaw status`、`openclaw status --deep`、`openclaw health --json`），并尾随`/tmp/openclaw/openclaw-*.log`查看`web-heartbeat` / `web-reconnect`。