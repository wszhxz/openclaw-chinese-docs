---
summary: "Fast channel level troubleshooting with per channel failure signatures and fixes"
read_when:
  - Channel transport says connected but replies fail
  - You need channel specific checks before deep provider docs
title: "Channel Troubleshooting"
---
# 通道故障排查

当通道已连接但行为异常时，请使用本页面。

## 命令执行顺序

请按以下顺序首先运行这些命令：

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

健康基线状态：

- `Runtime: running`
- `RPC probe: ok`
- 通道探针显示已连接/就绪

## WhatsApp

### WhatsApp 故障特征

| 症状                         | 最快检查方式                                       | 解决方法                                                     |
| ------------------------------- | --------------------------------------------------- | ------------------------------------------------------- |
| 已连接但无私信回复     | `openclaw pairing list whatsapp`                    | 批准发信人，或切换私信策略/白名单。           |
| 群组消息被忽略          | 检查 `requireMention` + 配置中的提及模式 | 在群组中@机器人，或为该群组放宽提及策略。 |
| 随机断连/重复登录循环 | `openclaw channels status --probe` + 日志           | 重新登录，并确认凭据目录状态正常。   |

完整故障排查指南：[/channels/whatsapp#troubleshooting-quick](/channels/whatsapp#troubleshooting-quick)

## Telegram

### Telegram 故障特征

| 症状                           | 最快检查方式                                   | 解决方法                                                                         |
| --------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------- |
| `/start` 但无可用的回复流程 | `openclaw pairing list telegram`                | 批准配对，或更改私信策略。                                        |
| 机器人在线但群组保持沉默 | 验证提及要求和机器人隐私模式 | 为群组可见性禁用隐私模式，或在群组中@机器人。                   |
| 发送失败并伴随网络错误 | 检查日志中 Telegram API 调用失败记录     | 修复 DNS/IPv6/代理路由至 `api.telegram.org`。                           |
| 升级后白名单阻止了访问 | `openclaw security audit` 和配置白名单 | 运行 `openclaw doctor --fix`，或用数字发信人 ID 替换 `@username`。 |

完整故障排查指南： [/channels/telegram#troubleshooting](/channels/telegram#troubleshooting)

## Discord

### Discord 故障特征

| 症状                         | 最快检查方式                       | 解决方法                                                       |
| ------------------------------- | ----------------------------------- | --------------------------------------------------------- |
| 机器人在线但无服务器回复 | `openclaw channels status --probe`  | 允许服务器/频道，并验证消息内容意图。    |
| 群组消息被忽略          | 检查日志中因提及限制而丢弃的消息 | @机器人，或设置服务器/频道 `requireMention: false`。 |
| 私信回复缺失              | `openclaw pairing list discord`     | 批准私信配对，或调整私信策略。                   |

完整故障排查指南： [/channels/discord#troubleshooting](/channels/discord#troubleshooting)

## Slack

### Slack 故障特征

| 症状                                | 最快检查方式                             | 解决方法                                               |
| -------------------------------------- | ----------------------------------------- | ------------------------------------------------- |
| Socket 模式已连接但无响应 | `openclaw channels status --probe`        | 验证应用令牌 + 机器人令牌及所需作用域。 |
| 私信被阻止                            | `openclaw pairing list slack`             | 批准配对，或放宽私信策略。               |
| 频道消息被忽略                | 检查 `groupPolicy` 和频道白名单 | 允许该频道，或切换策略至 `open`。     |

完整故障排查指南： [/channels/slack#troubleshooting](/channels/slack#troubleshooting)

## iMessage 和 BlueBubbles

### iMessage 和 BlueBubbles 故障特征

| 症状                          | 最快检查方式                                                           | 解决方法                                                   |
| -------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------- |
| 无入站事件                | 验证 Webhook/服务器可达性及应用权限                  | 修复 Webhook URL 或 BlueBubbles 服务状态。          |
| 可发送但 macOS 上无法接收 | 检查 macOS 中“信息”自动化相关的隐私权限                 | 重新授予 TCC 权限并重启通道进程。 |
| 私信发信人被阻止         | `openclaw pairing list imessage` 或 `openclaw pairing list bluebubbles` | 批准配对或更新白名单。                  |

完整故障排查指南：

- [/channels/imessage#troubleshooting-macos-privacy-and-security-tcc](/channels/imessage#troubleshooting-macos-privacy-and-security-tcc)
- [/channels/bluebubbles#troubleshooting](/channels/bluebubbles#troubleshooting)

## Signal

### Signal 故障特征

| 症状                         | 最快检查方式                              | 解决方法                                                      |
| ------------------------------- | ------------------------------------------ | -------------------------------------------------------- |
| 守护进程可访问但机器人静默 | `openclaw channels status --probe`         | 验证 `signal-cli` 守护进程 URL/账户及接收模式。 |
| 私信被阻止                      | `openclaw pairing list signal`             | 批准发信人或调整私信策略。                      |
| 群组回复未触发    | 检查群组白名单和提及模式 | 添加发信人/群组，或放宽触发限制。                       |

完整故障排查指南： [/channels/signal#troubleshooting](/channels/signal#troubleshooting)

## Matrix

### Matrix 故障特征

| 症状                             | 最快检查方式                                | 解决方法                                             |
| ----------------------------------- | -------------------------------------------- | ----------------------------------------------- |
| 已登录但忽略房间消息 | `openclaw channels status --probe`           | 检查 `groupPolicy` 和房间白名单。         |
| 私信不处理                  | `openclaw pairing list matrix`               | 批准发信人或调整私信策略。             |
| 加密房间失败                | 验证加密模块和加密设置 | 启用加密支持，并重新加入/同步房间。 |

完整故障排查指南： [/channels/matrix#troubleshooting](/channels/matrix#troubleshooting)