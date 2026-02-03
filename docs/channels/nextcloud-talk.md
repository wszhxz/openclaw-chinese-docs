---
summary: "Nextcloud Talk support status, capabilities, and configuration"
read_when:
  - Working on Nextcloud Talk channel features
title: "Nextcloud Talk"
---
化<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context. The content is about setting up Nextcloud Talk as a plugin, including installation steps, configuration details, and various settings. 

First, I'll go through each section and translate the headings and subheadings. For example, "Nextcloud Talk (plugin)" becomes "Nextcloud Talk（插件）". I need to make sure technical terms like "webhook bot" are accurately translated. "Webhook bot" could be "Webhook机器人" in Chinese.

Next, the installation instructions. The CLI commands should remain in code format but with Chinese comments. For instance, the command to install the plugin via npm should be translated, but the code itself stays the same. I'll check if there are any specific terms that need to be kept in English, like "shared-secret" or "webhook-url".

The configuration section has JSON examples. I need to ensure that the JSON structure is preserved, and the keys are translated appropriately. Terms like "baseUrl" might be translated to "基础URL", but sometimes it's better to keep the original term if it's a standard API term. I'll have to decide on consistency here.

There are also notes about access control and room policies. Phrases like "pairing code" should be translated to "配对码". I need to be careful with technical jargon to maintain clarity. For example, "mention-gated" could be "提及门控" or "提及限制", but I'll check for the most common translation in this context.

The capabilities table lists features and their status. I'll translate each feature name and status, ensuring that terms like "Native commands" become "原生命令" and "URL-only" becomes "仅URL".

I should also pay attention to the configuration reference section. Each configuration option needs to be translated, but the parameter names might stay in English. For example, "channels.nextcloud-talk.enabled" would be "启用通道启动" but the key remains as is.

I need to make sure that all instructions are clear and that the translated text maintains the original meaning. For instance, when talking about the webhook URL needing to be reachable by the Gateway, the translation should convey that the URL must be accessible from the Gateway's perspective.

Another point is the use of terms like "DMs" which are "Direct Messages". In Chinese, "DM" is often used as is, but sometimes translated to "直接消息". I'll check if there's a standard term used in the context of Nextcloud Talk.

I should also verify that all the code blocks and commands are correctly formatted in the translation. The backticks and code syntax should remain unchanged, but the comments and explanations should be in Chinese.

Lastly, I'll review the entire translation to ensure consistency in terminology and that the flow of information is logical. Making sure that technical terms are consistently translated and that the instructions are clear for the target audience.
</think>

# Nextcloud Talk（插件）

状态：通过插件支持（Webhook机器人）。支持直接消息、房间、反应和Markdown消息。

## 所需插件

Nextcloud Talk 作为插件提供，不包含在核心安装中。

通过 CLI（npm 注册表）安装：

```bash
openclaw plugins install @openclaw/nextcloud-talk
```

本地检出（从 git 仓库运行时）：

```bash
openclaw plugins install ./extensions/nextcloud-talk
```

如果在配置/引导过程中选择 Nextcloud Talk 并检测到 git 检出，
OpenClaw 将自动提供本地安装路径。

详情：[插件](/plugin)

## 快速设置（初学者）

1. 安装 Nextcloud Talk 插件。
2. 在您的 Nextcloud 服务器上创建一个机器人：
   ```bash
   ./occ talk:bot:install "OpenClaw" "<shared-secret>" "<webhook-url>" --feature reaction
   ```
3. 在目标房间设置中启用机器人。
4. 配置 OpenClaw：
   - 配置：`channels.nextcloud-talk.baseUrl` + `channels.nextcloud-talk.botSecret`
   - 或环境变量：`NEXTCLOUD_TALK_BOT_SECRET`（仅默认账户）
5. 重启网关（或完成引导）。

最小配置：

```json5
{
  channels: {
    "nextcloud-talk": {
      enabled: true,
      baseUrl: "https://cloud.example.com",
      botSecret: "shared-secret",
      dmPolicy: "pairing",
    },
  },
}
```

## 注意事项

- 机器人无法主动发起 DM。用户必须首先向机器人发送消息。
- Webhook URL 必须可由网关访问；如果使用代理，请设置 `webhookPublicUrl`。
- 机器人 API 不支持媒体上传；媒体以 URL 形式发送。
- Webhook 负载无法区分 DM 与房间；设置 `apiUser` + `apiPassword` 以启用房间类型查找（否则 DM 被视为房间）。

## 访问控制（DM）

- 默认：`channels.nextcloud-talk.dmPolicy = "pairing"`。未知发送者将获得配对码。
- 通过以下方式批准：
  - `openclaw pairing list nextcloud-talk`
  - `openclaw pairing approve nextcloud-talk <CODE>`
- 公开 DM：`channels.nextcloud-talk.dmPolicy="open"` 加上 `channels.nextcloud-talk.allowFrom=["*"]`。

## 房间（群组）

- 默认：`channels.nextcloud-talk.groupPolicy = "allowlist"`（提及门控）。
- 允许列表房间通过 `channels.nextcloud-talk.rooms`：

```json5
{
  channels: {
    "nextcloud-talk": {
      rooms: {
        "room-token": { requireMention: true },
      },
    },
  },
}
```

- 若要允许无房间，保持允许列表为空或设置 `channels.nextcloud-talk.groupPolicy="disabled"`。

## 功能

| 功能         | 状态        |
| ----------- | ------------- |
| 直接消息     | 支持         |
| 房间         | 支持         |
| 线程         | 不支持       |
| 媒体         | 仅 URL      |
| 反应         | 支持         |
| 原生命令     | 不支持       |

## 配置参考（Nextcloud Talk）

完整配置：[配置](/gateway/configuration)

提供选项：

- `channels.nextcloud-talk.enabled`: 启用/禁用通道启动。
- `channels.nextcloud-talk.baseUrl`: Nextcloud 实例 URL。
- `channels.nextcloud-talk.botSecret`: 机器人共享密钥。
- `channels.nextcloud-talk.botSecretFile`: 密钥文件路径。
- `channels.nextcloud-talk.apiUser`: 用于房间查找（DM 检测）的 API 用户。
- `channels.nextcloud-talk.apiPassword`: 用于房间查找的 API/应用密码。
- `channels.nextcloud-talk.apiPasswordFile`: API 密码文件路径。
- `channels.nextcloud-talk.webhookPort`: Webhook 监听端口（默认：8788）。
- `channels.nextcloud-talk.webhookHost`: Webhook 主机（默认：0.0.0.0）。
- `channels.nextcloud-talk.webhookPath`: Webhook 路径（默认：/nextcloud-talk-webhook）。
- `channels.nextcloud-talk.webhookPublicUrl`: 可从外部访问的 Webhook URL。
- `channels.nextcloud-talk.dmPolicy`: `pairing | allowlist | open | disabled`。
- `channels.nextcloud-talk.allowFrom`: DM 允许列表（用户 ID）。`open` 需要 `"*"`。
- `channels.nextcloud-talk.groupPolicy`: `allowlist | open | disabled`。
- `channels.nextcloud-talk.groupAllowFrom`: 群组允许列表（用户 ID）。
- `channels.nextcloud-talk.rooms`: 每个房间的设置和允许列表。
- `channels.nextcloud-talk.historyLimit`: 群组历史记录限制（0 禁用）。
- `channels.nextcloud-talk.dmHistoryLimit`: DM 历史记录限制（0 禁用）。
- `channels.nextcloud-talk.dms`: 每个 DM 的覆盖（historyLimit）。
- `channels.nextcloud-talk.textChunkLimit`: 出站文本块大小（字符）。
- `channels.nextcloud-talk.chunkMode`: `length`（默认）或 `newline` 以在长度分块前按空白行（段落边界）拆分。
- `channels.nextcloud-talk.blockStreaming`: 禁用此通道的块流。
- `channels.nextcloud-talk.blockStreamingCoalesce`: 块流合并调优。
- `channels.nextcloud-talk.mediaMaxMb`: 入站媒体上限（MB）。