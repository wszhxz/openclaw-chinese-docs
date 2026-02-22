---
summary: "Fast channel level troubleshooting with per channel failure signatures and fixes"
read_when:
  - Channel transport says connected but replies fail
  - You need channel specific checks before deep provider docs
title: "Channel Troubleshooting"
---
# 通道故障排除

当通道连接但行为不正确时，请使用此页面。

## 命令梯级

按顺序运行这些命令：

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
- 通道探测显示已连接/就绪

## WhatsApp

### WhatsApp 故障迹象

| 症状                         | 最快检查                                       | 修复                                                     |
| ------------------------------- | --------------------------------------------------- | ------------------------------------------------------- |
| 已连接但没有DM回复     | `openclaw pairing list whatsapp`                    | 批准发送者或切换DM策略/允许列表。           |
| 忽略群组消息          | 检查 `requireMention` + 配置中的提及模式 | 提及机器人或放宽该群组的提及策略。 |
| 随机断开/重新登录循环 | `openclaw channels status --probe` + 日志           | 重新登录并验证凭据目录是否正常。   |

完整故障排除：[/channels/whatsapp#troubleshooting-quick](/channels/whatsapp#troubleshooting-quick)

## Telegram

### Telegram 故障迹象

| 症状                           | 最快检查                                   | 修复                                                                         |
| --------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------- |
| `/start` 但没有可用的回复流 | `openclaw pairing list telegram`                | 批准配对或更改DM策略。                                        |
| 机器人在线但群组保持沉默 | 验证提及要求和机器人隐私模式 | 禁用群组可见性的隐私模式或提及机器人。                   |
| 发送失败伴有网络错误 | 检查日志中的Telegram API调用失败     | 修复DNS/IPv6/代理路由到 `api.telegram.org`。                           |
| 升级后允许列表阻止你 | `openclaw security audit` 和配置允许列表 | 运行 `openclaw doctor --fix` 或将 `@username` 替换为数字发送者ID。 |

完整故障排除：[/channels/telegram#troubleshooting](/channels/telegram#troubleshooting)

## Discord

### Discord 故障迹象

| 症状                         | 最快检查                       | 修复                                                       |
| ------------------------------- | ----------------------------------- | --------------------------------------------------------- |
| 机器人在线但没有公会回复 | `openclaw channels status --probe`  | 允许公会/频道并验证消息内容意图。    |
| 忽略群组消息          | 检查日志中的提及门控丢弃 | 提及机器人或设置公会/频道 `requireMention: false`。 |
| 缺少DM回复              | `openclaw pairing list discord`     | 批准DM配对或调整DM策略。                   |

完整故障排除：[/channels/discord#troubleshooting](/channels/discord#troubleshooting)

## Slack

### Slack 故障迹象

| 症状                                | 最快检查                             | 修复                                               |
| -------------------------------------- | ----------------------------------------- | ------------------------------------------------- |
| 套接字模式已连接但没有响应 | `openclaw channels status --probe`        | 验证应用令牌+机器人令牌和所需范围。 |
| 阻止DM                            | `openclaw pairing list slack`             | 批准配对或放宽DM策略。               |
| 频道消息被忽略                | 检查 `groupPolicy` 和频道允许列表 | 允许频道或切换策略到 `open`。     |

完整故障排除：[/channels/slack#troubleshooting](/channels/slack#troubleshooting)

## iMessage 和 BlueBubbles

### iMessage 和 BlueBubbles 故障迹象

| 症状                          | 最快检查                                                           | 修复                                                   |
| -------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------- |
| 没有传入事件                | 验证webhook/服务器可达性和应用程序权限                  | 修复webhook URL或BlueBubbles服务器状态。          |
| 可以发送但在macOS上无法接收 | 检查macOS隐私权限以进行Messages自动化                 | 重新授予TCC权限并重启通道进程。 |
| 阻止DM发送者                | `openclaw pairing list imessage` 或 `openclaw pairing list bluebubbles` | 批准配对或更新允许列表。                  |

完整故障排除：

- [/channels/imessage#troubleshooting-macos-privacy-and-security-tcc](/channels/imessage#troubleshooting-macos-privacy-and-security-tcc)
- [/channels/bluebubbles#troubleshooting](/channels/bluebubbles#troubleshooting)

## Signal

### Signal 故障迹象

| 症状                         | 最快检查                              | 修复                                                      |
| ------------------------------- | ------------------------------------------ | -------------------------------------------------------- |
| 守护进程可达但机器人静默 | `openclaw channels status --probe`         | 验证 `signal-cli` 守护进程URL/账户和接收模式。 |
| 阻止DM                      | `openclaw pairing list signal`             | 批准发送者或调整DM策略。                      |
| 群组回复未触发    | 检查群组允许列表和提及模式 | 添加发送者/群组或放宽门控。                       |

完整故障排除：[/channels/signal#troubleshooting](/channels/signal#troubleshooting)

## Matrix

### Matrix 故障迹象

| 症状                             | 最快检查                                | 修复                                             |
| ----------------------------------- | -------------------------------------------- | ----------------------------------------------- |
| 登录但忽略房间消息 | `openclaw channels status --probe`           | 检查 `groupPolicy` 和房间允许列表。         |
| DM未处理                  | `openclaw pairing list matrix`               | 批准发送者或调整DM策略。             |
| 加密房间失败                | 验证加密模块和加密设置 | 启用加密支持并重新加入/同步房间。 |

完整故障排除：[/channels/matrix#troubleshooting](/channels/matrix#troubleshooting)