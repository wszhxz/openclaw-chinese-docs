---
summary: "Zalo bot support status, capabilities, and configuration"
read_when:
  - Working on Zalo features or webhooks
title: "Zalo"
---
# Zalo (Bot API)

状态：实验性。支持 DM；群组处理可用，但需显式群组策略控制。

## 需要插件

Zalo 作为插件提供，不包含在核心安装中。

- 通过 CLI 安装：`openclaw plugins install @openclaw/zalo`
- 或在入门向导中选择 **Zalo** 并确认安装提示
- 详情：[插件](/tools/plugin)

## 快速设置（初学者）

1. 安装 Zalo 插件：
   - 从源码检出：`openclaw plugins install ./extensions/zalo`
   - 从 npm（如果已发布）：`openclaw plugins install @openclaw/zalo`
   - 或在入门向导中选择 **Zalo** 并确认安装提示
2. 设置令牌：
   - 环境变量：`ZALO_BOT_TOKEN=...`
   - 或配置：`channels.zalo.botToken: "..."`。
3. 重启网关（或完成入门向导）。
4. DM 访问默认配对；首次联系时批准配对码。

最小配置：

```json5
{
  channels: {
    zalo: {
      enabled: true,
      botToken: "12345689:abc-xyz",
      dmPolicy: "pairing",
    },
  },
}
```

## 它是什么

Zalo 是一款面向越南的即时通讯应用；其 Bot API 允许网关为 1:1 对话运行机器人。
它非常适合支持或通知场景，其中您需要确定性的路由回 Zalo。

- 由网关拥有的 Zalo Bot API 频道。
- 确定性路由：回复返回到 Zalo；模型从不选择频道。
- DM 共享坐席的主会话。
- 支持群组，带有策略控制 (`groupPolicy` + `groupAllowFrom`)，默认为故障关闭的白名单行为。

## 设置（快速路径）

### 1) 创建机器人令牌（Zalo Bot Platform）

1. 前往 [https://bot.zaloplatforms.com](https://bot.zaloplatforms.com) 并登录。
2. 创建新机器人并配置其设置。
3. 复制机器人令牌（格式：`12345689:abc-xyz`）。

### 2) 配置令牌（环境变量或配置）

示例：

```json5
{
  channels: {
    zalo: {
      enabled: true,
      botToken: "12345689:abc-xyz",
      dmPolicy: "pairing",
    },
  },
}
```

环境变量选项：`ZALO_BOT_TOKEN=...`（仅适用于默认账户）。

多账户支持：使用 `channels.zalo.accounts` 配合每账户令牌和可选的 `name`。

3. 重启网关。当解析到令牌时（环境变量或配置），Zalo 启动。
4. DM 访问默认为配对。首次联系机器人时批准代码。

## 工作原理（行为）

- 传入消息被标准化为共享频道信封，包含媒体占位符。
- 回复始终路由回相同的 Zalo 聊天。
- 默认长轮询；使用 `channels.zalo.webhookUrl` 可用 Webhook 模式。

## 限制

- 出站文本分块为 2000 个字符（Zalo API 限制）。
- 媒体下载/上传受 `channels.zalo.mediaMaxMb` 限制（默认 5）。
- 流式传输默认被阻止，因为 2000 字符限制使得流式传输用处不大。

## 访问控制（DM）

### DM 访问

- 默认：`channels.zalo.dmPolicy = "pairing"`。未知发送者收到配对码；消息在批准前被忽略（代码 1 小时后过期）。
- 通过以下方式批准：
  - `openclaw pairing list zalo`
  - `openclaw pairing approve zalo <CODE>`
- 配对是默认的令牌交换。详情：[配对](/channels/pairing)
- `channels.zalo.allowFrom` 接受数字用户 ID（不支持用户名查找）。

## 访问控制（群组）

- `channels.zalo.groupPolicy` 控制群组传入处理：`open | allowlist | disabled`。
- 默认行为是故障关闭：`allowlist`。
- `channels.zalo.groupAllowFrom` 限制哪些发送者 ID 可以在群组中触发机器人。
- 如果未设置 `groupAllowFrom`，Zalo 回退到 `allowFrom` 进行发送者检查。
- `groupPolicy: "disabled"` 阻止所有群组消息。
- `groupPolicy: "open"` 允许任何群组成员（提及门禁）。
- 运行时注意：如果完全缺少 `channels.zalo`，运行时仍回退到 `groupPolicy="allowlist"` 以确保安全。

## 长轮询与 Webhook

- 默认：长轮询（不需要公共 URL）。
- Webhook 模式：设置 `channels.zalo.webhookUrl` 和 `channels.zalo.webhookSecret`。
  - Webhook 密钥必须为 8-256 个字符。
  - Webhook URL 必须使用 HTTPS。
  - Zalo 发送带有 `X-Bot-Api-Secret-Token` 头的事件用于验证。
  - 网关 HTTP 在 `channels.zalo.webhookPath` 处理 Webhook 请求（默认为 Webhook URL 路径）。
  - 请求必须使用 `Content-Type: application/json`（或 `+json` 媒体类型）。
  - 重复事件 (`event_name + message_id`) 在短重放窗口内被忽略。
  - 突发流量按路径/源限流，可能返回 HTTP 429。

**注意：** 根据 Zalo API 文档，getUpdates（轮询）和 Webhook 互斥。

## 支持的消息类型

- **文本消息**：完全支持，带 2000 字符分块。
- **图片消息**：下载和处理传入图片；通过 `sendPhoto` 发送图片。
- **贴纸**：已记录但未完全处理（无坐席响应）。
- **不支持的类型**：已记录（例如，来自受保护用户的消息）。

## 功能

| 功能         | 状态                                                   |
| ------------ | -------------------------------------------------------- |
| 直接消息     | ✅ 支持                                             |
| 群组         | ⚠️ 支持，带策略控制（默认为白名单） |
| 媒体（图片） | ✅ 支持                                             |
| 反应         | ❌ 不支持                                         |
| 线程         | ❌ 不支持                                         |
| 投票         | ❌ 不支持                                         |
| 原生命令     | ❌ 不支持                                         |
| 流式传输     | ⚠️ 阻止（2000 字符限制）                             |

## 交付目标（CLI/cron）

- 使用聊天 ID 作为目标。
- 示例：`openclaw message send --channel zalo --target 123456789 --message "hi"`。

## 故障排除

**机器人无响应：**

- 检查令牌是否有效：`openclaw channels status --probe`
- 验证发送者已获批准（配对或 allowFrom）
- 检查网关日志：`openclaw logs --follow`

**Webhook 未接收事件：**

- 确保 Webhook URL 使用 HTTPS
- 验证密钥令牌为 8-256 个字符
- 确认网关 HTTP 端点在配置的路径上可访问
- 检查 getUpdates 轮询是否未运行（它们互斥）

## 配置参考（Zalo）

完整配置：[配置](/gateway/configuration)

提供者选项：

- `channels.zalo.enabled`：启用/禁用频道启动。
- `channels.zalo.botToken`：来自 Zalo Bot Platform 的机器人令牌。
- `channels.zalo.tokenFile`：从文件路径读取令牌。
- `channels.zalo.dmPolicy`：`pairing | allowlist | open | disabled`（默认：配对）。
- `channels.zalo.allowFrom`：DM 白名单（用户 ID）。`open` 需要 `"*"`。向导将询问数字 ID。
- `channels.zalo.groupPolicy`：`open | allowlist | disabled`（默认：白名单）。
- `channels.zalo.groupAllowFrom`：群组发送者白名单（用户 ID）。未设置时回退到 `allowFrom`。
- `channels.zalo.mediaMaxMb`：传入/传出媒体上限（MB，默认 5）。
- `channels.zalo.webhookUrl`：启用 Webhook 模式（需要 HTTPS）。
- `channels.zalo.webhookSecret`：Webhook 密钥（8-256 字符）。
- `channels.zalo.webhookPath`：网关 HTTP 服务器上的 Webhook 路径。
- `channels.zalo.proxy`：API 请求的代理 URL。

多账户选项：

- `channels.zalo.accounts.<id>.botToken`：每账户令牌。
- `channels.zalo.accounts.<id>.tokenFile`：每账户令牌文件。
- `channels.zalo.accounts.<id>.name`：显示名称。
- `channels.zalo.accounts.<id>.enabled`：启用/禁用账户。
- `channels.zalo.accounts.<id>.dmPolicy`：每账户 DM 策略。
- `channels.zalo.accounts.<id>.allowFrom`：每账户白名单。
- `channels.zalo.accounts.<id>.groupPolicy`：每账户群组策略。
- `channels.zalo.accounts.<id>.groupAllowFrom`：每账户群组发送者白名单。
- `channels.zalo.accounts.<id>.webhookUrl`：每账户 Webhook URL。
- `channels.zalo.accounts.<id>.webhookSecret`：每账户 Webhook 密钥。
- `channels.zalo.accounts.<id>.webhookPath`：每账户 Webhook 路径。
- `channels.zalo.accounts.<id>.proxy`：每账户代理 URL。