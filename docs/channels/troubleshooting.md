---
summary: "Fast channel level troubleshooting with per channel failure signatures and fixes"
read_when:
  - Channel transport says connected but replies fail
  - You need channel specific checks before deep provider docs
title: "Channel Troubleshooting"
---
# 频道故障排查

当频道已连接但行为异常时，请使用本页面。

## 命令阶梯

首先按顺序运行这些命令：

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

健康基线：

- `Runtime: running`
- `RPC probe: ok`
- 通道探测显示传输层已连接，以及在受支持的情况下，`works` 或 `audit ok`

## WhatsApp

### WhatsApp 故障特征

| 现象                         | 最快检查项                                       | 修复方案                                                     |
| ------------------------------- | --------------------------------------------------- | ------------------------------------------------------- |
| 已连接但无 DM 回复     | `openclaw pairing list whatsapp`                    | 批准发送者或切换 DM 策略/白名单。           |
| 群组消息被忽略          | 检查 `requireMention` + 配置中的提及模式 | 提及机器人或放宽该群组的提及策略。 |
| 随机断开/重连循环 | `openclaw channels status --probe` + 日志           | 重新登录并验证凭证目录是否健康。   |

完整故障排查：[/channels/whatsapp#troubleshooting](/channels/whatsapp#troubleshooting)

## Telegram

### Telegram 故障特征

| 现象                             | 最快检查项                                   | 修复方案                                                                         |
| ----------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------- |
| `/start` 但无可用回复流   | `openclaw pairing list telegram`                | 批准配对或更改 DM 策略。                                        |
| 机器人在线但群组保持静默   | 验证提及要求和机器人隐私模式 | 禁用隐私模式以启用群组可见性或提及机器人。                   |
| 因网络错误导致发送失败   | 检查日志中的 Telegram API 调用失败     | 修复 DNS/IPv6/代理路由至 `api.telegram.org`。                           |
| `setMyCommands` 在启动时被拒绝 | 检查日志中的 `BOT_COMMANDS_TOO_MUCH`        | 减少插件/技能/自定义 Telegram 命令或禁用原生菜单。       |
| 升级后白名单阻止了你   | `openclaw security audit` 和配置白名单 | 运行 `openclaw doctor --fix` 或将 `@username` 替换为数字发送者 ID。 |

完整故障排查：[/channels/telegram#troubleshooting](/channels/telegram#troubleshooting)

## Discord

### Discord 故障特征

| 现象                         | 最快检查项                       | 修复方案                                                       |
| ------------------------------- | ----------------------------------- | --------------------------------------------------------- |
| 机器人在线但无服务器回复 | `openclaw channels status --probe`  | 允许服务器/频道并验证消息内容意图。    |
| 群组消息被忽略          | 检查日志中的提及限制丢弃情况 | 提及机器人或设置服务器/频道 `requireMention: false`。 |
| 缺少 DM 回复              | `openclaw pairing list discord`     | 批准 DM 配对或调整 DM 策略。                   |

完整故障排查：[/channels/discord#troubleshooting](/channels/discord#troubleshooting)

## Slack

### Slack 故障特征

| 现象                                | 最快检查项                             | 修复方案                                                                                                                                                  |
| -------------------------------------- | ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Socket 模式已连接但无响应 | `openclaw channels status --probe`        | 验证应用令牌 + 机器人令牌及所需作用域；注意基于 SecretRef 的部署中的 `botTokenStatus` / `appTokenStatus = configured_unavailable`。 |
| DM 被阻止                            | `openclaw pairing list slack`             | 批准配对或放宽 DM 策略。                                                                                                                  |
| 频道消息被忽略                | 检查 `groupPolicy` 和频道白名单 | 允许该频道或将策略切换为 `open`。                                                                                                        |

完整故障排查：[/channels/slack#troubleshooting](/channels/slack#troubleshooting)

## iMessage 和 BlueBubbles

### iMessage 和 BlueBubbles 故障特征

| 现象                          | 最快检查项                                                           | 修复方案                                                   |
| -------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------- |
| 无入站事件                | 验证 Webhook/服务器可达性及应用权限                  | 修复 Webhook URL 或 BlueBubbles 服务器状态。          |
| 可以发送但在 macOS 上无法接收 | 检查 macOS 上消息自动化的隐私权限                 | 重新授予 TCC 权限并重启频道进程。 |
| DM 发送者被阻止                | `openclaw pairing list imessage` 或 `openclaw pairing list bluebubbles` | 批准配对或更新白名单。                  |

完整故障排查：

- [/channels/imessage#troubleshooting](/channels/imessage#troubleshooting)
- [/channels/bluebubbles#troubleshooting](/channels/bluebubbles#troubleshooting)

## Signal

### Signal 故障特征

| 现象                         | 最快检查项                              | 修复方案                                                      |
| ------------------------------- | ------------------------------------------ | -------------------------------------------------------- |
| 守护进程可达但机器人无响应 | `openclaw channels status --probe`         | 验证 `signal-cli` 守护进程 URL/账户及接收模式。 |
| DM 被阻止                      | `openclaw pairing list signal`             | 批准发送者或调整 DM 策略。                      |
| 群组回复未触发               | 检查群组白名单和提及模式 | 添加发送者/群组或放宽限制。                       |

完整故障排查：[/channels/signal#troubleshooting](/channels/signal#troubleshooting)

## QQ Bot

### QQ Bot 故障特征

| 现象                         | 最快检查项                               | 修复方案                                                             |
| ------------------------------- | ------------------------------------------- | --------------------------------------------------------------- |
| 机器人回复“去火星了”      | 验证配置中的 `appId` 和 `clientSecret` | 设置凭证或重启网关。                         |
| 无入站消息             | `openclaw channels status --probe`          | 在 QQ 开放平台验证凭证。                     |
| 语音未转录           | 检查 STT 提供商配置                   | 配置 `channels.qqbot.stt` 或 `tools.media.audio`。          |
| 主动消息未到达 | 检查 QQ 平台交互要求  | QQ 可能会阻止无最近交互的机器人发起的消息。 |

完整故障排查：[/channels/qqbot#troubleshooting](/channels/qqbot#troubleshooting)

## Matrix

### Matrix 故障特征

| 现象                             | 最快检查项                          | 修复方案                                                                       |
| ----------------------------------- | -------------------------------------- | ------------------------------------------------------------------------- |
| 已登录但忽略房间消息 | `openclaw channels status --probe`     | 检查 `groupPolicy`、房间白名单和提及限制。                  |
| DM 未处理                  | `openclaw pairing list matrix`         | 批准发送者或调整 DM 策略。                                       |
| 加密房间失败                | `openclaw matrix verify status`        | 重新验证设备，然后检查 `openclaw matrix verify backup status`。  |
| 备份恢复待定/损坏    | `openclaw matrix verify backup status` | 运行 `openclaw matrix verify backup restore` 或使用恢复密钥重新运行。 |
| 交叉签名/引导看起来不正确 | `openclaw matrix verify bootstrap`     | 一次性修复密钥存储、交叉签名和备份状态。       |

完整设置和配置：[Matrix](/channels/matrix)