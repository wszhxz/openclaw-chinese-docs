---
summary: "Telegram bot support status, capabilities, and configuration"
read_when:
  - Working on Telegram features or webhooks
title: "Telegram"
---
以下是您提供的查询的中文翻译：

---

**Telegram 机器人配置指南**

**翻译说明**  
以下内容为英文技术文档的中文翻译，涵盖 Telegram 机器人配置、故障排除及相关设置。请根据实际需求调整配置参数。

---

### **1. 机器人配置详解**

**1.1 基本配置**  
- `channels.telegram.enabled`: 启用/禁用通道启动。  
- `channels.telegram.botToken`: 机器人令牌（通过 BotFather 获取）。  
- `channels.telegram.tokenFile`: 从文件路径读取令牌。  
- `channels.telegram.dmPolicy`: 默认为 `pairing`（配对模式），可选 `allowlist`（允许列表）、`open`（开放）、`disabled`（禁用）。  
- `channels.telegram.allowFrom`: DM 允许列表（ID/用户名）。`open` 需要 `"*"`。  
- `channels.telegram.groupPolicy`: 默认为 `allowlist`（允许列表），可选 `open`（开放）、`disabled`（禁用）。  
- `channels.telegram.groupAllowFrom`: 群组发送者允许列表（ID/用户名）。  
- `channels.telegram.groups`: 按群组设置默认值和允许列表（使用 `"*"` 表示全局默认）。  
  - `channels.telegram.groups.<id>.requireMention`: 默认是否需要 @ 提及。  
  - `channels.telegram.groups.<id>.skills`: 技能过滤（省略表示所有技能，空表示无）。  
  - `channels.telegram.groups.<id>.allowFrom`: 按群组覆盖发送者允许列表。  
  - `channels.telegram.groups.<id>.systemPrompt`: 群组的额外系统提示。  
  - `channels.telegram.groups.<id>.enabled`: 禁用群组（设为 `false`）。  
  - `channels.telegram.groups.<id>.topics.<threadId>.*`: 按主题覆盖（同群组字段）。  
  - `channels.telegram.groups.<id>.topics.<threadId>.requireMention`: 按主题覆盖提及要求。  

**1.2 功能配置**  
- `channels.telegram.capabilities.inlineButtons`: 默认为 `allowlist`（允许列表），可选 `off`、`dm`（私聊）、`group`（群组）、`all`（全部）。  
- `channels.telegram.accounts.<account>.capabilities.inlineButtons`: 按账户覆盖。  
- `channels.telegram.replyToMode`: 默认为 `first`（首次回复），可选 `off`、`first`、`all`。  
- `channels.telegram.textChunkLimit`: 出站消息分块大小（字符数）。  
- `channels.telegram.chunkMode`: 默认为 `length`（按长度分块），或 `newline`（按换行符分段）。  
- `channels.telegram.linkPreview`: 默认开启出站消息的链接预览。  
- `channels.telegram.streamMode`: 默认为 `partial`（部分流式传输），可选 `off`、`partial`、`block`。  
- `channels.telegram.mediaMaxMb`: 入站/出站媒体大小限制（MB）。  
- `channels.telegram.retry`: 出站 Telegram API 调用的重试策略（尝试次数、最小延迟、最大延迟、抖动）。  
- `channels.telegram.network.autoSelectFamily`: 覆盖 Node 的自动 IPv4/IPv6 选择（默认在 Node 22 中禁用以避免 Happy Eyeballs 超时）。  
- `channels.telegram.proxy`: Bot API 调用的代理 URL（支持 SOCKS/HTTP）。  
- `channels.telegram.webhookUrl`: 启用 Webhook 模式（需设置 `channels.telegram.webhookSecret`）。  
- `channels.telegram.webhookSecret`: Webhook 密码（当 `webhookUrl` 设置时必填）。  
- `channels.telegram.webhookPath`: 本地 Webhook 路径（默认 `/telegram-webhook`）。  

**1.3 操作控制**  
- `channels.telegram.actions.reactions`: 控制 Telegram 反馈工具（默认启用）。  
- `channels.telegram.actions.sendMessage`: 控制消息发送工具（默认启用）。  
- `channels.telegram.actions.deleteMessage`: 控制消息删除工具（默认启用）。  
- `channels.telegram.actions.sticker`: 控制贴纸操作（发送/搜索，默认禁用）。  
- `channels.telegram.reactionNotifications`: 控制哪些反馈触发系统事件（默认 `own`）。  
- `channels.telegram.reactionLevel`: 控制代理的反馈能力（默认 `minimal`）。  

---

### **2. 故障排除指南**

**2.1 机器人无法响应群组非提及消息**  
- 如果设置了 `channels.telegram.groups.*.requireMention=false`，需在 BotFather 中禁用隐私模式（`/setprivacy` → 关闭）。  
- `openclaw channels status` 会显示警告（当配置期望未提及的群组消息时）。  
- `openclaw channels status --probe` 可检查显式群组 ID 的成员资格（无法审计 `"*"` 规则）。  
- 快速测试：`/activation always`（仅会话有效，需配置持久化）。  

**2.2 机器人完全无法接收群组消息**  
- 如果 `channels.telegram.groups` 已设置，群组必须被列出或使用 `"*"`。  
- 检查 BotFather 的隐私设置 → "Group Privacy" 必须为 **OFF**。  
- 确认机器人实际是成员（而非仅管理员无读取权限）。  
- 检查网关日志：`openclaw logs --follow`（查找 "skipping group message"）。  

**2.3 机器人响应提及但不响应 `/activation always`**  
- `/activation` 命令更新会话状态但不持久化到配置。  
- 持久