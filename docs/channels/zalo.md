---
summary: "Zalo bot support status, capabilities, and configuration"
read_when:
  - Working on Zalo features or webhooks
title: "Zalo"
---
# Zalo (Bot API)

状态：实验中。仅支持直接消息；群组功能即将推出，详见Zalo文档。

## 需要插件

Zalo作为一个插件提供，并未包含在核心安装包中。

- 通过CLI安装：`openclaw plugins install @openclaw/zalo`
- 或者在首次设置期间选择**Zalo**并确认安装提示
- 详情：[Plugins](/plugin)

## 快速设置（初学者）

1. 安装Zalo插件：
   - 从源码安装：`openclaw plugins install ./extensions/zalo`
   - 从npm安装（如果已发布）：`openclaw plugins install @openclaw/zalo`
   - 或者在首次设置期间选择**Zalo**并确认安装提示
2. 设置令牌：
   - 环境变量：`ZALO_BOT_TOKEN=...`
   - 或者配置文件：`channels.zalo.botToken: "..."`。
3. 重启网关（或完成首次设置）。
4. 默认情况下，直接消息访问需要配对；首次联系时批准配对代码。

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

## 什么是Zalo

Zalo是一款面向越南市场的即时通讯应用；其Bot API允许网关运行用于一对一对话的机器人。
它非常适合需要确定路由回传至Zalo的支持或通知场景。

- 由网关拥有的Zalo Bot API通道。
- 确定性路由：回复会发送回Zalo；模型不会选择通道。
- 直接消息共享代理的主要会话。
- 群组功能尚未支持（Zalo文档中说明“即将推出”）。

## 设置（快速路径）

### 1) 创建机器人令牌（Zalo Bot Platform）

1. 访问**https://bot.zaloplatforms.com**并登录。
2. 创建一个新的机器人并配置其设置。
3. 复制机器人令牌（格式：`12345689:abc-xyz`）。

### 2) 配置令牌（环境变量或配置文件）

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

多账户支持：使用`channels.zalo.accounts`配合每个账户的令牌和可选的`name`。

3. 重启网关。当解析到令牌（环境变量或配置文件）时，Zalo启动。
4. 默认情况下，直接消息访问需要配对。首次联系机器人时批准代码。

## 工作原理（行为）

- 入站消息被标准化为带有媒体占位符的共享通道信封。
- 回复总是路由回相同的Zalo聊天。
- 默认使用长轮询；通过`channels.zalo.webhookUrl`可用Webhook模式。

## 限制

- 发送的文本消息会被分块为2000个字符（Zalo API限制）。
- 媒体下载/上传限制为`channels.zalo.mediaMaxMb`（默认5）。
- 由于2000字符限制，默认情况下阻止流式传输，使其不太有用。

## 访问控制（直接消息）

### 直接消息访问

- 默认：`channels.zalo.dmPolicy = "pairing"`。未知发送者会收到配对代码；消息会被忽略直到批准（代码在一小时后过期）。
- 通过以下方式批准：
  - `openclaw pairing list zalo`
  - `openclaw pairing approve zalo <CODE>`
- 配对是默认的令牌交换方式。详情：[Pairing](/start/pairing)
- `channels.zalo.allowFrom`接受数字用户ID（无用户名查找功能）。

## 长轮询与Webhook

- 默认：长轮询（无需公共URL）。
- Webhook模式：设置`channels.zalo.webhookUrl`和`channels.zalo.webhookSecret`。
  - Webhook密钥必须为8-256个字符。
  - Webhook URL必须使用HTTPS。
  - Zalo通过`X-Bot-Api-Secret-Token`头发送事件以进行验证。
  - 网关HTTP处理程序在`channels.zalo.webhookPath`接收Webhook请求（默认为Webhook URL路径）。

**注意：** 根据Zalo API文档，getUpdates（轮询）和Webhook是互斥的。

## 支持的消息类型

- **文本消息**：完全支持，分块大小为2000个字符。
- **图像消息**：下载并处理入站图像；通过`sendPhoto`发送图像。
- **贴纸**：记录但不完全处理（无代理响应）。
- **不支持的类型**：记录（例如，来自受保护用户的消息）。

## 功能

| 功能         | 状态                         |
| --------------- | ------------------------------ |
| 直接消息 | ✅ 支持                   |
| 群组          | ❌ 即将推出（见Zalo文档） |
| 媒体（图像）  | ✅ 支持                   |
| 反应       | ❌ 不支持               |
| 线程         | ❌ 不支持               |
| 投票           | ❌ 不支持               |
| 原生命令 | ❌ 不支持               |
| 流式传输       | ⚠️ 阻止（2000字符限制）   |

## 交付目标（CLI/cron）

- 使用聊天ID作为目标。
- 示例：`openclaw message send --channel zalo --target 123456789 --message "hi"`。

## 故障排除

**机器人没有响应：**

- 检查令牌是否有效：`openclaw channels status --probe`
- 验证发送者是否已被批准（配对或allowFrom）
- 检查网关日志：`openclaw logs --follow`

**Webhook未接收事件：**

- 确保Webhook URL使用HTTPS
- 验证密钥令牌为8-256个字符
- 确认网关HTTP端点在配置路径上可访问
- 检查getUpdates轮询是否正在运行（它们是互斥的）

## 配置参考（Zalo）

完整配置：[Configuration](/gateway/configuration)

提供商选项：

- `channels.zalo.enabled`：启用/禁用通道启动。
- `channels.zalo.botToken`：来自Zalo Bot Platform的机器人令牌。
- `channels.zalo.tokenFile`：从文件路径读取令牌。
- `channels.zalo.dmPolicy`：`pairing | allowlist | open | disabled`（默认：配对）。
- `channels.zalo.allowFrom`：直接消息白名单（用户ID）。`open`需要`"*"`。向导会要求输入数字ID。
- `channels.zalo.mediaMaxMb`：入站/出站媒体限制（MB，默认5）。
- `channels.zalo.webhookUrl`：启用Webhook模式（需要HTTPS）。
- `channels.zalo.webhookSecret`：Webhook密钥（8-256个字符）。
- `channels.zalo.webhookPath`：网关HTTP服务器上的Webhook路径。
- `channels.zalo.proxy`：API请求的代理URL。

多账户选项：

- `channels.zalo.accounts.<id>.botToken`：每个账户的令牌。
- `channels.zalo.accounts.<id>.tokenFile`：每个账户的令牌文件。
- `channels.zalo.accounts.<id>.name`：显示名称。
- `channels.zalo.accounts.<id>.enabled`：启用/禁用账户。
- `channels.zalo.accounts.<id>.dmPolicy`：每个账户的直接消息策略。
- `channels.zalo.accounts.<id>.allowFrom`：每个账户的白名单。
- `channels.zalo.accounts.<id>.webhookUrl`：每个账户的Webhook URL。
- `channels.zalo.accounts.<id>.webhookSecret`：每个账户的Webhook密钥。
- `channels.zalo.accounts.<id>.webhookPath`：每个账户的Webhook路径。
- `channels.zalo.accounts.<id>.proxy`：每个账户的代理URL。