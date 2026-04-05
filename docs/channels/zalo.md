---
summary: "Zalo bot support status, capabilities, and configuration"
read_when:
  - Working on Zalo features or webhooks
title: "Zalo"
---
# Zalo (Bot API)

状态：实验性。支持私信（DM）。下方的 [功能特性](#capabilities) 部分反映了当前 Marketplace-bot 的行为。

## 捆绑插件

Zalo 作为捆绑插件随当前 OpenClaw 版本发布，因此常规打包构建无需单独安装。

如果您使用的是旧版构建或排除了 Zalo 的自定义安装，请手动安装：

- 通过 CLI 安装：`openclaw plugins install @openclaw/zalo`
- 或从源代码检出：`openclaw plugins install ./path/to/local/zalo-plugin`
- 详情：[插件](/tools/plugin)

## 快速设置（初学者）

1. 确保 Zalo 插件可用。
   - 当前打包的 OpenClaw 版本已包含它。
   - 旧版/自定义安装可使用上述命令手动添加。
2. 设置令牌：
   - 环境变量：`ZALO_BOT_TOKEN=...`
   - 或配置：`channels.zalo.accounts.default.botToken: "..."`。
3. 重启网关（或完成设置）。
4. 默认情况下，DM 访问采用配对模式；首次联系时批准配对码。

最小化配置：

```json5
{
  channels: {
    zalo: {
      enabled: true,
      accounts: {
        default: {
          botToken: "12345689:abc-xyz",
          dmPolicy: "pairing",
        },
      },
    },
  },
}
```

## 简介

Zalo 是一款专注于越南的通讯应用；其 Bot API 允许网关运行机器人进行 1:1 对话。
它非常适合需要确定性路由回 Zalo 的支持或通知场景。

此页面反映了 OpenClaw 对 **Zalo Bot Creator / Marketplace bots** 的当前行为。
**Zalo Official Account (OA) bots** 是不同的 Zalo 产品界面，行为可能不同。

- 由网关拥有的 Zalo Bot API 频道。
- 确定性路由：回复返回 Zalo；模型从不选择频道。
- DM 共享代理的主会话。
- 下方的 [功能特性](#capabilities) 部分显示了当前 Marketplace-bot 的支持情况。

## 设置（快速路径）

### 1) 创建机器人令牌（Zalo Bot Platform）

1. 前往 [https://bot.zaloplatforms.com](https://bot.zaloplatforms.com) 并登录。
2. 创建新机器人并配置其设置。
3. 复制完整的机器人令牌（通常为 `numeric_id:secret`）。对于 Marketplace bots，可用的运行时令牌可能会出现在创建后的机器人欢迎消息中。

### 2) 配置令牌（环境变量或配置）

示例：

```json5
{
  channels: {
    zalo: {
      enabled: true,
      accounts: {
        default: {
          botToken: "12345689:abc-xyz",
          dmPolicy: "pairing",
        },
      },
    },
  },
}
```

如果您后续迁移到支持群组的 Zalo 机器人界面，可以显式添加特定于群组的配置，例如 `groupPolicy` 和 `groupAllowFrom`。关于当前 Marketplace-bot 行为，请参阅 [功能特性](#capabilities)。

环境变量选项：`ZALO_BOT_TOKEN=...`（仅适用于默认账户）。

多账户支持：使用 `channels.zalo.accounts` 配合每个账户的令牌及可选的 `name`。

3. 重启网关。当解析到令牌时（环境变量或配置），Zalo 启动。
4. DM 访问默认为配对模式。当机器人首次被联系时批准代码。

## 工作原理（行为）

- 传入消息被标准化为带有媒体占位符的共享频道信封。
- 回复始终路由回同一个 Zalo 聊天。
- 默认长轮询；使用 `channels.zalo.webhookUrl` 可用 Webhook 模式。

## 限制

- 传出文本分块为 2000 字符（Zalo API 限制）。
- 媒体下载/上传受 `channels.zalo.mediaMaxMb` 限制（默认 5）。
- 默认阻止流式传输，因为 2000 字符限制使得流式传输用处不大。

## 访问控制（DM）

### DM 访问

- 默认：`channels.zalo.dmPolicy = "pairing"`。未知发送者会收到配对码；消息在批准前会被忽略（代码 1 小时后过期）。
- 通过以下方式批准：
  - `openclaw pairing list zalo`
  - `openclaw pairing approve zalo <CODE>`
- 配对是默认的令牌交换方式。详情：[配对](/channels/pairing)
- `channels.zalo.allowFrom` 接受数字用户 ID（不可用用户名查找）。

## 访问控制（群组）

对于 **Zalo Bot Creator / Marketplace bots**，实际上不支持群组，因为机器人根本无法加入群组。

这意味着下面的群组相关配置键存在于架构中，但对于 Marketplace bots 不可用：

- `channels.zalo.groupPolicy` 控制群组传入处理：`open | allowlist | disabled`。
- `channels.zalo.groupAllowFrom` 限制哪些发送者 ID 可以在群组中触发机器人。
- 如果 `groupAllowFrom` 未设置，Zalo 将回退到 `allowFrom` 进行发送者检查。
- 运行时注意：如果 `channels.zalo` 完全缺失，运行时仍会回退到 `groupPolicy="allowlist"` 以确保安全。

群组策略值（当您的机器人界面可用群组访问时）为：

- `groupPolicy: "disabled"` — 阻止所有群组消息。
- `groupPolicy: "open"` — 允许任何群组成员（提及门控）。
- `groupPolicy: "allowlist"` — 失败关闭默认值；仅接受允许的发送者。

如果您使用的是不同的 Zalo 机器人产品界面并已验证了群组行为正常工作，请单独记录，而不是假设它与 Marketplace-bot 流程匹配。

## 长轮询与 Webhook

- 默认：长轮询（不需要公共 URL）。
- Webhook 模式：设置 `channels.zalo.webhookUrl` 和 `channels.zalo.webhookSecret`。
  - Webhook 密钥必须为 8-256 个字符。
  - Webhook URL 必须使用 HTTPS。
  - Zalo 发送带有 `X-Bot-Api-Secret-Token` 头的事件以进行验证。
  - 网关 HTTP 在 `channels.zalo.webhookPath` 处理 Webhook 请求（默认为 Webhook URL 路径）。
  - 请求必须使用 `Content-Type: application/json`（或 `+json` 媒体类型）。
  - 重复事件 (`event_name + message_id`) 在短暂的回放窗口内被忽略。
  - 突发流量按路径/源进行速率限制，并可能返回 HTTP 429。

**注意：** 根据 Zalo API 文档，getUpdates（轮询）和 webhook 是互斥的。

## 支持的消息类型

如需快速了解支持情况，请参阅 [功能特性](#capabilities)。以下注释在行为需要额外上下文时提供详细信息。

- **文本消息**：完全支持，2000 字符分块。
- **文本中的纯 URL**：表现为普通文本输入。
- **链接预览 / 富链接卡片**：查看 [功能特性](#capabilities) 中的 Marketplace-bot 状态；它们无法可靠地触发回复。
- **图片消息**：查看 [功能特性](#capabilities) 中的 Marketplace-bot 状态；传入图片处理不可靠（有输入指示但最终无回复）。
- **贴纸**：查看 [功能特性](#capabilities) 中的 Marketplace-bot 状态。
- **语音笔记 / 音频文件 / 视频 / 通用文件附件**：查看 [功能特性](#capabilities) 中的 Marketplace-bot 状态。
- **不支持的类型**：已记录（例如，来自受保护用户的消息）。

## 功能特性

此表总结了 OpenClaw 中当前 **Zalo Bot Creator / Marketplace bot** 的行为。

| 功能                      | 状态                                      |
| ------------------------- | ----------------------------------------- |
| 直接消息                  | ✅ 支持                                   |
| 群组                      | ❌ Marketplace bots 不可用                |
| 媒体（传入图片）          | ⚠️ 有限制 / 请在您的环境中验证           |
| 媒体（传出图片）          | ⚠️ 未针对 Marketplace bots 重新测试      |
| 文本中的纯 URL            | ✅ 支持                                   |
| 链接预览                  | ⚠️ Marketplace bots 不可靠               |
| 反应                      | ❌ 不支持                                 |
| 贴纸                      | ⚠️ Marketplace bots 无代理回复           |
| 语音笔记 / 音频 / 视频    | ⚠️ Marketplace bots 无代理回复           |
| 文件附件                  | ⚠️ Marketplace bots 无代理回复           |
| 线程                      | ❌ 不支持                                 |
| 投票                      | ❌ 不支持                                 |
| 原生命令                  | ❌ 不支持                                 |
| 流式传输                  | ⚠️ 已阻止（2000 字符限制）               |

## 投递目标（CLI/cron）

- 使用聊天 ID 作为目标。
- 示例：`openclaw message send --channel zalo --target 123456789 --message "hi"`。

## 故障排除

**机器人不响应：**

- 检查令牌是否有效：`openclaw channels status --probe`
- 验证发送者是否已批准（配对或 allowFrom）
- 检查网关日志：`openclaw logs --follow`

**Webhook 未接收事件：**

- 确保 Webhook URL 使用 HTTPS
- 验证密钥令牌为 8-256 个字符
- 确认网关 HTTP 端点在配置的路径上可访问
- 检查 getUpdates 轮询是否未运行（它们互斥）

## 配置参考（Zalo）

完整配置：[配置](/gateway/configuration)

扁平化的顶级键（`channels.zalo.botToken`、`channels.zalo.dmPolicy` 等）是遗留的单账户简写。新配置建议使用 `channels.zalo.accounts.<id>.*`。这两种形式在此处均有记录，因为它们存在于架构中。

提供商选项：

- `channels.zalo.enabled`: 启用/禁用频道启动。
- `channels.zalo.botToken`: 来自 Zalo Bot Platform 的机器人 token。
- `channels.zalo.tokenFile`: 从常规文件路径读取 token。拒绝符号链接。
- `channels.zalo.dmPolicy`: `pairing | allowlist | open | disabled`（默认：pairing）。
- `channels.zalo.allowFrom`: DM 白名单（用户 ID）。`open` 需要 `"*"`。向导将要求输入数字 ID。
- `channels.zalo.groupPolicy`: `open | allowlist | disabled`（默认：allowlist）。存在于配置中；有关当前 Marketplace-bot 行为，请参阅 [功能](#capabilities) 和 [访问控制（群组）](#access-control-groups)。
- `channels.zalo.groupAllowFrom`: 群组发送者白名单（用户 ID）。未设置时回退到 `allowFrom`。
- `channels.zalo.mediaMaxMb`: 入站/出站媒体限制（MB，默认 5）。
- `channels.zalo.webhookUrl`: 启用 webhook 模式（需要 HTTPS）。
- `channels.zalo.webhookSecret`: webhook secret（8-256 个字符）。
- `channels.zalo.webhookPath`: 网关 HTTP 服务器上的 webhook 路径。
- `channels.zalo.proxy`: API 请求的 proxy URL。

多账户选项：

- `channels.zalo.accounts.<id>.botToken`: 每账户 token。
- `channels.zalo.accounts.<id>.tokenFile`: 每账户常规 token 文件。拒绝符号链接。
- `channels.zalo.accounts.<id>.name`: 显示名称。
- `channels.zalo.accounts.<id>.enabled`: 启用/禁用账户。
- `channels.zalo.accounts.<id>.dmPolicy`: 每账户 DM 策略。
- `channels.zalo.accounts.<id>.allowFrom`: 每账户白名单。
- `channels.zalo.accounts.<id>.groupPolicy`: 每账户群组策略。存在于配置中；有关当前 Marketplace-bot 行为，请参阅 [功能](#capabilities) 和 [访问控制（群组）](#access-control-groups)。
- `channels.zalo.accounts.<id>.groupAllowFrom`: 每账户群组发送者白名单。
- `channels.zalo.accounts.<id>.webhookUrl`: 每账户 webhook URL。
- `channels.zalo.accounts.<id>.webhookSecret`: 每账户 webhook secret。
- `channels.zalo.accounts.<id>.webhookPath`: 每账户 webhook 路径。
- `channels.zalo.accounts.<id>.proxy`: 每账户 proxy URL。

## 相关

- [频道概览](/channels) — 所有支持的频道
- [配对](/channels/pairing) — DM 认证和配对流程
- [群组](/channels/groups) — 群聊行为和提及限制
- [频道路由](/channels/channel-routing) — 消息会话路由
- [安全](/gateway/security) — 访问模型和加固