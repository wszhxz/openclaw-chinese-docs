---
summary: "Zalo bot support status, capabilities, and configuration"
read_when:
  - Working on Zalo features or webhooks
title: "Zalo"
---
# Zalo（Bot API）

状态：实验性。支持私信（DM）；群组处理需通过显式的群组策略控制。

## 需要安装插件

Zalo 以插件形式提供，不包含在核心安装包中。

- 通过 CLI 安装：`openclaw plugins install @openclaw/zalo`  
- 或在初始配置向导中选择 **Zalo** 并确认安装提示  
- 详情参见：[插件](/tools/plugin)

## 快速入门（新手）

1. 安装 Zalo 插件：  
   - 从源码检出安装：`openclaw plugins install ./extensions/zalo`  
   - 从 npm 安装（如已发布）：`openclaw plugins install @openclaw/zalo`  
   - 或在初始配置向导中选择 **Zalo** 并确认安装提示  
2. 设置 token：  
   - 环境变量方式：`ZALO_BOT_TOKEN=...`  
   - 或配置文件方式：`channels.zalo.botToken: "..."`  
3. 重启网关（或完成初始配置）。  
4. 私信访问默认启用配对机制；首次联系时需批准配对码。

最小化配置示例：

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

## 功能说明

Zalo 是一款面向越南市场的即时通讯应用；其 Bot API 允许网关运行一个用于一对一（1:1）对话的机器人。当您需要将消息确定性地路由回 Zalo 时（例如客服支持或通知场景），该方案尤为适用。

- 一条由网关拥有的 Zalo Bot API 通道。  
- 确定性路由：所有回复均返回至同一 Zalo 聊天窗口；模型不会自主选择通道。  
- 私信共享代理的主会话。  
- 群组支持受策略控制（`groupPolicy` + `groupAllowFrom`），默认采用“拒绝优先”的白名单行为。

## 快速配置流程

### 1）创建机器人 token（Zalo Bot Platform）

1. 访问 [https://bot.zaloplatforms.com](https://bot.zaloplatforms.com) 并登录。  
2. 创建新机器人并配置其设置。  
3. 复制机器人 token（格式为：`12345689:abc-xyz`）。

### 2）配置 token（环境变量或配置文件）

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

环境变量方式：`ZALO_BOT_TOKEN=...`（仅适用于默认账号）。

多账号支持：使用 `channels.zalo.accounts` 配置各账号专属 token，并可选配置 `name`。

3. 重启网关。当成功解析到 token（来自环境变量或配置文件）后，Zalo 通道即自动启动。  
4. 私信访问默认启用配对机制；机器人首次被联系时，请批准配对码。

## 工作原理（行为说明）

- 入站消息被标准化为统一通道信封格式，并含媒体占位符。  
- 所有回复始终路由回同一 Zalo 聊天窗口。  
- 默认采用长轮询（long-polling）；启用 webhook 模式需配置 `channels.zalo.webhookUrl`。

## 限制条件

- 出站文本按 2000 字符分块发送（Zalo API 限制）。  
- 媒体文件下载/上传受 `channels.zalo.mediaMaxMb` 限制（默认值为 5）。  
- 流式响应（streaming）默认禁用，因 2000 字符限制使其实用性较低。

## 访问控制（私信）

### 私信访问

- 默认行为：`channels.zalo.dmPolicy = "pairing"`。未知发件人将收到配对码；消息在获准前被忽略（配对码 1 小时后过期）。  
- 批准方式包括：  
  - `openclaw pairing list zalo`  
  - `openclaw pairing approve zalo <CODE>`  
- 配对是默认的令牌交换机制。详情参见：[配对](/channels/pairing)  
- `channels.zalo.allowFrom` 接受纯数字用户 ID（不支持用户名查询）。

## 访问控制（群组）

- `channels.zalo.groupPolicy` 控制群组入站消息处理逻辑：`open | allowlist | disabled`。  
- 默认行为为“拒绝优先”：`allowlist`。  
- `channels.zalo.groupAllowFrom` 限制可在群组中触发机器人的发件人 ID 列表。  
- 若未设置 `groupAllowFrom`，Zalo 将回退至 `allowFrom` 进行发件人校验。  
- `groupPolicy: "disabled"` 将屏蔽全部群组消息。  
- `groupPolicy: "open"` 允许任意群组成员（需 @ 提及才触发）。  
- 运行时说明：若完全缺失 `channels.zalo`，运行时仍将安全地回退至 `groupPolicy="allowlist"`。

## 长轮询 vs Webhook

- 默认模式：长轮询（无需公网 URL）。  
- Webhook 模式：需设置 `channels.zalo.webhookUrl` 和 `channels.zalo.webhookSecret`。  
  - Webhook 密钥长度必须为 8–256 字符。  
  - Webhook URL 必须使用 HTTPS。  
  - Zalo 发送事件时携带 `X-Bot-Api-Secret-Token` 请求头用于验证。  
  - 网关 HTTP 服务在 `channels.zalo.webhookPath` 处理 webhook 请求（默认路径与 webhook URL 路径一致）。  
  - 请求必须使用 `Content-Type: application/json`（或 `+json`）媒体类型。  
  - 在短时间重放窗口内，重复事件（`event_name + message_id`）将被忽略。  
  - 突发流量按路径/来源进行速率限制，可能返回 HTTP 429。

**注意：** 根据 Zalo API 文档，`getUpdates`（轮询）与 webhook 模式互斥。

## 支持的消息类型

- **文本消息**：完整支持，按 2000 字符分块。  
- **图片消息**：支持下载并处理入站图片；通过 `sendPhoto` 发送图片。  
- **贴纸（Stickers）**：记录日志，但未完全处理（代理无响应）。  
- **不支持的类型**：记录日志（例如来自受保护用户的消息）。

## 功能能力

| 功能             | 状态                                                   |
| ---------------- | ------------------------------------------------------ |
| 私信（Direct messages） | ✅ 已支持                                             |
| 群组（Groups）         | ⚠️ 已支持，需策略控制（默认为白名单）                  |
| 媒体（图片）           | ✅ 已支持                                             |
| 表情反应（Reactions）   | ❌ 不支持                                             |
| 子话题（Threads）      | ❌ 不支持                                             |
| 投票（Polls）          | ❌ 不支持                                             |
| 原生命令（Native commands） | ❌ 不支持                                             |
| 流式响应（Streaming）   | ⚠️ 已禁用（受限于 2000 字符限制）                      |

## 投递目标（CLI / 定时任务）

- 使用聊天 ID（chat id）作为目标。  
- 示例：`openclaw message send --channel zalo --target 123456789 --message "hi"`。

## 故障排查

**机器人无响应：**

- 检查 token 是否有效：`openclaw channels status --probe`  
- 确认发件人已被批准（已完成配对或列入 `allowFrom`）  
- 查看网关日志：`openclaw logs --follow`

**Webhook 未收到事件：**

- 确保 webhook URL 使用 HTTPS  
- 验证密钥长度为 8–256 字符  
- 确认网关 HTTP 端点在所配置路径上可达  
- 检查 `getUpdates` 轮询是否未运行（二者互斥）

## 配置参考（Zalo）

完整配置说明：[配置](/gateway/configuration)

提供商选项：

- `channels.zalo.enabled`：启用/禁用通道启动。  
- `channels.zalo.botToken`：来自 Zalo Bot Platform 的机器人 token。  
- `channels.zalo.tokenFile`：从文件路径读取 token。  
- `channels.zalo.dmPolicy`：`pairing | allowlist | open | disabled`（默认：`pairing`）。  
- `channels.zalo.allowFrom`：私信白名单（用户 ID）。`open` 要求启用 `"*"`。向导将提示输入数字 ID。  
- `channels.zalo.groupPolicy`：`open | allowlist | disabled`（默认：`allowlist`）。  
- `channels.zalo.groupAllowFrom`：群组发件人白名单（用户 ID）。若未设置，则回退至 `allowFrom`。  
- `channels.zalo.mediaMaxMb`：入站/出站媒体容量上限（MB，默认为 5）。  
- `channels.zalo.webhookUrl`：启用 webhook 模式（需 HTTPS）。  
- `channels.zalo.webhookSecret`：webhook 密钥（8–256 字符）。  
- `channels.zalo.webhookPath`：网关 HTTP 服务器上的 webhook 路径。  
- `channels.zalo.proxy`：API 请求所用代理 URL。

多账号选项：

- `channels.zalo.accounts.<id>.botToken`：各账号专属 token。  
- `channels.zalo.accounts.<id>.tokenFile`：各账号 token 文件路径。  
- `channels.zalo.accounts.<id>.name`：显示名称。  
- `channels.zalo.accounts.<id>.enabled`：启用/禁用该账号。  
- `channels.zalo.accounts.<id>.dmPolicy`：各账号私信策略。  
- `channels.zalo.accounts.<id>.allowFrom`：各账号私信白名单。  
- `channels.zalo.accounts.<id>.groupPolicy`：各账号群组策略。  
- `channels.zalo.accounts.<id>.groupAllowFrom`：各账号群组发件人白名单。  
- `channels.zalo.accounts.<id>.webhookUrl`：各账号 webhook URL。  
- `channels.zalo.accounts.<id>.webhookSecret`：各账号 webhook 密钥。  
- `channels.zalo.accounts.<id>.webhookPath`：各账号 webhook 路径。  
- `channels.zalo.accounts.<id>.proxy`：各账号代理 URL。