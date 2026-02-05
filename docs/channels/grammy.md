---
summary: "Telegram Bot API integration via grammY with setup notes"
read_when:
  - Working on Telegram or grammY pathways
title: grammY
---
# grammY 集成 (Telegram Bot API)

# 为什么选择 grammY

- 以 TypeScript 为主的 Bot API 客户端，内置了长轮询 + Webhook 辅助工具、中间件、错误处理、速率限制器。
- 比手动编写 fetch + FormData 更简洁的媒体辅助工具；支持所有 Bot API 方法。
- 可扩展：通过自定义 fetch 支持代理、会话中间件（可选）、类型安全的上下文。

# 我们发布了什么

- **单一客户端路径：** 基于 fetch 的实现已移除；gramY 现在是唯一的 Telegram 客户端（发送 + 网关），默认启用 grammY 节流器。
- **网关：** `monitorTelegramProvider` 构建一个 grammY `Bot`，连接提及/白名单网关，通过 `getFile`/`download` 下载媒体，并使用 `sendMessage/sendPhoto/sendVideo/sendAudio/sendDocument` 发送回复。支持通过 `webhookCallback` 进行长轮询或 Webhook。
- **代理：** 可选的 `channels.telegram.proxy` 通过 grammY 的 `client.baseFetch` 使用 `undici.ProxyAgent`。
- **Webhook 支持：** `webhook-set.ts` 包装 `setWebhook/deleteWebhook`；`webhook.ts` 承载回调并提供健康检查 + 平滑关闭。当设置 `channels.telegram.webhookUrl` + `channels.telegram.webhookSecret` 时，网关启用 Webhook 模式（否则使用长轮询）。
- **会话：** 直接聊天合并到代理主会话 (`agent:<agentId>:<mainKey>`)；群组使用 `agent:<agentId>:telegram:group:<chatId>`；回复路由回同一频道。
- **配置选项：** `channels.telegram.botToken`，`channels.telegram.dmPolicy`，`channels.telegram.groups`（白名单 + 提及默认值），`channels.telegram.allowFrom`，`channels.telegram.groupAllowFrom`，`channels.telegram.groupPolicy`，`channels.telegram.mediaMaxMb`，`channels.telegram.linkPreview`，`channels.telegram.proxy`，`channels.telegram.webhookSecret`，`channels.telegram.webhookUrl`。
- **草稿流式传输：** 可选的 `channels.telegram.streamMode` 在私有主题聊天中使用 `sendMessageDraft`（Bot API 9.3+）。这与频道块流式传输分开。
- **测试：** grammy 模拟涵盖了 DM + 群组提及网关和外发发送；仍然欢迎更多的媒体/Webhook 测试用例。

开放问题

- 如果遇到 Bot API 429 错误，是否需要可选的 grammY 插件（节流器）。
- 添加更多结构化的媒体测试（贴纸、语音消息）。
- 使 webhook 监听端口可配置（当前固定为 8787，除非通过网关连接）。