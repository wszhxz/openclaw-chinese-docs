---
summary: "Zalo bot support status, capabilities, and configuration"
read_when:
  - Working on Zalo features or webhooks
title: "Zalo"
---
5<think>
Okay, I need to translate this technical document about the Zalo Bot API into Chinese. Let me start by reading through the entire text to understand the context and key terms. The document covers installation, configuration, setup steps, supported features, and troubleshooting. 

First, I'll note the technical terms like "Zalo Bot API," "token," "webhook," "long-polling," and specific configuration parameters. These should be translated accurately to maintain the technical accuracy. For example, "botToken" might be translated as "机器人令牌" and "webhookUrl" as "Webhook地址."

I should also pay attention to the structure, such as headings and lists, to ensure the translated document maintains its original format. Terms like "Direct messages" become "单聊" and "groups" as "群组." 

Some sections mention specific URLs, like "https://bot.zaloplatforms.com," which should remain unchanged. The note about the 2000 character limit for outbound text needs to be clear in Chinese, so I'll use "2000字符限制" for that.

I need to be careful with the configuration examples. The JSON5 code blocks should have their keys translated, but the actual values like "12345689:abc-xyz" stay the same. Also, the table of capabilities has status indicators like ✅ and ❌; these should be kept as is, but the text next to them translated.

The troubleshooting section has specific commands like "openclaw pairing list zalo" which are CLI commands and should remain in English. However, the explanations around them need to be in Chinese. 

I'll also check for consistency in terminology throughout the document. For instance, "pairing code" is translated as "配对码" and should be used consistently. 

Some parts mention "multi-account support," which translates to "多账号支持." I need to ensure that all technical terms are consistently translated and that the document flows naturally in Chinese while preserving the original meaning.

Lastly, I'll review the entire translation to make sure there are no grammatical errors and that the technical details are accurately conveyed. This includes checking that all instructions are clear and that the structure mirrors the original document for easy reference.
</think>

# Zalo（机器人API）

状态：实验性。仅支持单聊；群组功能即将推出（根据Zalo文档）。

## 必需插件

Zalo作为插件提供，不包含在核心安装包中。

- 通过CLI安装：`openclaw plugins install @openclaw/zalo`
- 或在引导过程中选择**Zalo**并确认安装提示
- 详情：[插件](/plugin)

## 快速设置（入门用户）

1. 安装Zalo插件：
   - 从源码仓库中：`openclaw plugins install ./extensions/zalo`
   - 从npm（若已发布）：`openclaw plugins install @openclaw/zalo`
   - 或在引导过程中选择**Zalo**并确认安装提示
2. 设置令牌：
   - 环境变量：`ZALO_BOT_TOKEN=...`
   - 或配置：`channels.zalo.botToken: "..."`.
3. 重启网关（或完成引导）。
4. 默认情况下，单聊访问需要配对；首次联系时需批准配对码。

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

Zalo是一款以越南为中心的即时通讯应用；其机器人API允许网关为一对一聊天运行机器人。它非常适合需要将消息确定性地路由回Zalo的客服或通知场景。

- 由网关拥有的Zalo机器人API通道。
- 确定性路由：回复会返回Zalo；模型不会选择通道。
- 单聊共享代理的主要会话。
- 群组功能尚未支持（Zalo文档称“即将推出”）。

## 设置（快速路径）

### 1) 创建机器人令牌（Zalo机器人平台）

1. 访问**https://bot.zaloplatforms.com**并登录。
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

多账号支持：使用`channels.zalo.accounts`配合每个账号的令牌和可选的`name`。

3. 重启网关。当令牌解析（环境变量或配置）后Zalo开始运行。
4. 默认情况下，单聊访问为配对模式。首次联系机器人时需批准配对码。

## 工作原理（行为）

- 入站消息被标准化为共享通道信封，包含媒体占位符。
- 回复始终返回到相同的Zalo聊天。
- 默认使用长轮询；可通过`channels.zalo.webhookUrl`启用Webhook模式。

## 限制

- 出站文本按2000字符分块（Zalo API限制）。
- 媒体下载/上传受`channels.zalo.mediaMaxMb`限制（默认5MB）。
- 默认禁用流式传输，因2000字符限制使流式传输实用性较低。

## 访问控制（单聊）

### 单聊访问

- 默认：`channels.zalo.dmPolicy = "pairing"`。未知发送者会收到配对码；消息在批准前被忽略（码在1小时后过期）。
- 批准方式：
  - `openclaw pairing list zalo`
  - `openclaw pairing approve zalo <CODE>`
- 配对是默认的令牌交换方式。详情：[配对](/start/pairing)
- `channels.zalo.allowFrom`接受数字用户ID（无用户名查找功能）。

## 长轮询 vs Webhook

- 默认：长轮询（无需公开URL）。
- Webhook模式：设置`channels.zalo.webhookUrl`和`channels.zalo.webhookSecret`。
  - Webhook密钥必须为8-256字符。
  - Webhook URL必须使用HTTPS。
  - Zalo通过`X-Bot-Api-Secret-Token`头发送事件进行验证。
  - 网关HTTP在`channels.zalo.webhookPath`处理Webhook请求（默认为Webhook URL路径）。

**注意：** 根据Zalo API文档，getUpdates（轮询）和Webhook互斥。

## 支持的消息类型

- **文本消息**：支持完整功能，按2000字符分块。
- **图片消息**：下载并处理入站图片；通过`sendPhoto`发送图片。
- **贴纸**：记录但未完全处理（无代理响应）。
- **不支持类型**：记录（例如来自受保护用户的消息）。

## 功能

| 功能         | 状态                         |
| ----------- | ------------------------------ |
| 单聊         | ✅ 支持                   |
| 群组          | ❌ 即将推出（根据Zalo文档） |
| 媒体（图片）  | ✅ 支持                   |
| 反馈         | ❌ 不支持               |
| 线程         | ❌ 不支持               |
| 投票           | ❌ 不支持               |
| 原生命令       | ❌ 不支持               |
| 流式传输       | ⚠️ 被阻止（2000字符限制）   |

## 交付目标（CLI/定时任务）

- 使用聊天ID作为目标。
- 示例：`openclaw message send --channel zalo --target 123456789 --message "hi"`。

## 故障排除

**机器人未响应：**

- 检查令牌是否有效：`openclaw channels status --probe`
- 确认发送者已批准（配对或allowFrom）
- 检查网关日志：`openclaw logs --follow`

**Webhook未接收事件：**

- 确保Webhook URL使用HTTPS
- 验证密钥令牌为8-256字符
- 确认网关HTTP端点在配置路径上可访问
- 检查getUpdates轮询未运行（它们互斥）

## 配置参考（Zalo）

完整配置：[配置](/gateway/configuration)

提供选项：

- `channels.zalo.enabled`：启用/禁用通道启动。
- `channels.zalo.botToken`：来自Zalo机器人平台的机器人令牌。
- `channels.zalo.tokenFile`：从文件路径读取令牌。
- `channels.zalo.dmPolicy`：`pairing | allowlist | open | disabled`（默认：pairing）。
- `channels.zalo.allowFrom`：单聊允许列表（用户ID）。`open`要求`"*"`。向导会要求数字ID