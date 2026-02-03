---
summary: "Telegram Bot API integration via grammY with setup notes"
read_when:
  - Working on Telegram or grammY pathways
title: grammY
---
。
<think>
Okay, I need to translate this English text about grammY integration with Telegram Bot API into Chinese. Let me start by reading through the entire text to understand the context and key points. 

First, the title is "# grammY Integration (Telegram Bot API)" which should be translated as "# grammY 集成（Telegram Bot API）". 

Under "Why grammY", there are bullet points. I'll need to make sure technical terms like "long-poll", "webhook helpers", "middleware", "error handling", "rate limiter" are accurately translated. For example, "long-poll" is "长轮询" and "webhook helpers" could be "Webhook 辅助工具". 

The second bullet mentions "media helpers" and "FormData". I should translate "media helpers" as "媒体辅助工具" and "FormData" as "FormData" since it's a technical term. 

The third bullet talks about extensibility with proxy support, session middleware, and type-safe context. "Proxy support via custom fetch" becomes "通过自定义 fetch 实现的代理支持", "session middleware" is "会话中间件", and "type-safe context" is "类型安全上下文".

Moving to "What we shipped", the first point is about the single client path. "fetch-based implementation removed" translates to "移除了基于 fetch 的实现", and "grammY throttler enabled by default" is "默认启用 grammY 流量控制".

The Gateway section mentions "monitorTelegramProvider" which should stay as is since it's a specific function name. Terms like "mention/allowlist gating" need to be translated carefully. "Mention/allowlist gating" could be "提及/允许列表控制", and "media download via getFile/download" becomes "通过 getFile/download 进行媒体下载".

Proxy section: "undici.ProxyAgent" is a technical term, so I'll keep it as is. "webhookCallback" should be "webhookCallback".

Webhook support part has several terms. "webhook-set.ts" and "webhook.ts" are filenames, so they stay. "health + graceful shutdown" translates to "健康检查 + 平滑关闭". 

Sessions section: "direct chats collapse into the agent main session" becomes "直接聊天会合并到代理主会话中". "groups use" is "群组使用", and "replies route back" is "回复会返回到同一频道".

Config knobs list a lot of parameters. I need to ensure each key is translated correctly, like "botToken" as "机器人令牌", "dmPolicy" as "私聊策略", "groups" as "群组", etc. 

Draft streaming mentions "sendMessageDraft" which is a method name, so it stays. "channel block streaming" is "频道块流".

Tests section: "grammy mocks" becomes "grammy 模拟", "DM + group mention gating" is "私聊 + 群组提及控制", and "outbound send" is "出站发送".

Open questions: "Optional grammY plugins (throttler)" translates to "可选 grammY 插件（流量控制）", "structured media tests" is "结构化媒体测试", "stickers, voice notes" are "贴纸、语音消息".

I need to make sure all technical terms are correctly translated and that the structure of the document is maintained. Also, check for consistency in terminology throughout the translation. Avoid literal translations that might not make sense in Chinese. For example, "rate limiter" is "流量控制" instead of a direct translation. 

I should also pay attention to the formatting, like keeping the bullet points and section headers as they are. Ensure that code terms like "webhookCallback" are not translated but kept in English. 

Finally, review the entire translation to ensure clarity and accuracy, making sure that the technical details are preserved and the document reads naturally in Chinese.
</think>

# grammY 集成（Telegram Bot API）

# 为什么选择 grammY

- 以 TypeScript 优先的 Bot API 客户端，内置长轮询 + Webhook 辅助工具、中间件、错误处理、流量控制。
- 比手动实现 fetch + FormData 更干净的媒体辅助工具；支持所有 Bot API 方法。
- 可扩展：通过自定义 fetch 实现代理支持，可选会话中间件，类型安全上下文。

# 我们已发布的功能

- **单一客户端路径：** 移除了基于 fetch 的实现；grammY 现在是唯一的 Telegram 客户端（发送 + 网关），默认启用 grammY 流量控制。
- **网关：** `monitorTelegramProvider` 构建一个 grammY `Bot`，连接提及/允许列表控制，通过 `getFile`/`download` 进行媒体下载，并通过 `sendMessage/sendPhoto/sendVideo/sendAudio/sendDocument` 发送回复。支持长轮询或 Webhook 通过 `webhookCallback`。
- **代理：** 可选 `channels.telegram.proxy` 使用 `undici.ProxyAgent` 通过 grammY 的 `client.baseFetch`。
- **Webhook 支持：** `webhook-set.ts` 包装 `setWebhook/deleteWebhook`；`web,ebhook.ts` 主持回调并包含健康检查 + 平滑关闭。当设置 `channels.telegram.webhookUrl` + `channels.telegram.webhookSecret` 时，网关启用 Webhook 模式（否则使用长轮询）。
- **会话：** 直接聊天合并到代理主会话（`agent:<agentId>:<mainKey>`）；群组使用 `agent:<agentId>:telegram:group:<chatId>`；回复返回到同一频道。
- **配置选项：** `channels.telegram.botToken`，`channels.telegram.dmPolicy`，`channels.telegram.groups`（允许列表 + 提及默认值），`channels.telegram.allowFrom`，`channels.telegram.groupAllowFrom`，`channels.telegram.groupPolicy`，`channels.telegram.mediaMaxMb`，`channels.telegram.linkPreview`，`channels.telegram.proxy`，`channels.telegram.webhookSecret`，`channels.telegram.webhookUrl`。
- **草稿流：** 可选 `channels.telegram.streamMode` 在私聊主题中使用 `sendMessageDraft`（Bot API 9.3+）。这与频道块流无关。
- **测试：** grammY 模拟覆盖私聊 + 群组提及控制和出站发送；欢迎更多媒体/Webhook 测试用例。

待解决的问题

- 如果遇到 Bot API 429 错误，是否需要可选 grammY 插件（流量控制）。
- 添加更多结构化的媒体测试（贴纸、语音消息）。
- 使 Webhook 监听端口可配置（当前固定为 8787，除非通过网关设置）。