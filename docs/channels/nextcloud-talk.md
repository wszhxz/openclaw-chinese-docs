---
summary: "Nextcloud Talk support status, capabilities, and configuration"
read_when:
  - Working on Nextcloud Talk channel features
title: "Nextcloud Talk"
---
# Nextcloud Talk（插件）

状态：通过插件（Webhook 机器人）支持。支持私信、聊天室、消息反应及 Markdown 消息。

## 需要安装插件

Nextcloud Talk 以插件形式提供，不包含在核心安装包中。

通过 CLI（npm 仓库）安装：

```bash
openclaw plugins install @openclaw/nextcloud-talk
```

本地检出（当从 Git 仓库运行时）：

```bash
openclaw plugins install ./extensions/nextcloud-talk
```

若在配置/初始设置过程中选择 Nextcloud Talk 且检测到 Git 检出，
OpenClaw 将自动提供本地安装路径。

详情参见：[插件](/tools/plugin)

## 快速设置（新手）

1. 安装 Nextcloud Talk 插件。
2. 在您的 Nextcloud 服务器上创建一个机器人：

   ```bash
   ./occ talk:bot:install "OpenClaw" "<shared-secret>" "<webhook-url>" --feature reaction
   ```

3. 在目标聊天室设置中启用该机器人。
4. 配置 OpenClaw：
   - 配置项：`channels.nextcloud-talk.baseUrl` + `channels.nextcloud-talk.botSecret`
   - 或环境变量：`NEXTCLOUD_TALK_BOT_SECRET`（仅适用于默认账户）
5. 重启网关（或完成初始设置流程）。

最小化配置示例：

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

- 机器人无法主动发起私信（DM）。用户必须先向机器人发送消息。
- Webhook URL 必须可被网关访问；若处于代理之后，请设置 `webhookPublicUrl`。
- 机器人 API 不支持媒体上传；媒体将以 URL 形式发送。
- Webhook 负载未区分私信与聊天室；需设置 `apiUser` + `apiPassword` 以启用按房间类型查询（否则私信将被当作聊天室处理）。

## 访问控制（私信）

- 默认行为：`channels.nextcloud-talk.dmPolicy = "pairing"`。未知发送者将收到配对码。
- 批准方式包括：
  - `openclaw pairing list nextcloud-talk`
  - `openclaw pairing approve nextcloud-talk <CODE>`
- 公开私信：启用 `channels.nextcloud-talk.dmPolicy="open"` 并配合 `channels.nextcloud-talk.allowFrom=["*"]`。
- `allowFrom` 仅匹配 Nextcloud 用户 ID；显示名称将被忽略。

## 聊天室（群组）

- 默认行为：`channels.nextcloud-talk.groupPolicy = "allowlist"`（需提及才触发）。
- 使用 `channels.nextcloud-talk.rooms` 设置允许加入的聊天室：

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

- 若禁止所有聊天室，请保持允许列表为空，或设置 `channels.nextcloud-talk.groupPolicy="disabled"`。

## 功能支持情况

| 功能             | 状态         |
| ---------------- | ------------ |
| 私信             | 已支持       |
| 聊天室           | 已支持       |
| 主题（Threads）  | 不支持       |
| 媒体             | 仅支持 URL   |
| 消息反应         | 已支持       |
| 原生命令         | 不支持       |

## 配置参考（Nextcloud Talk）

完整配置说明请参见：[配置](/gateway/configuration)

提供商选项：

- `channels.nextcloud-talk.enabled`：启用/禁用频道启动。
- `channels.nextcloud-talk.baseUrl`：Nextcloud 实例 URL。
- `channels.nextcloud-talk.botSecret`：机器人共享密钥。
- `channels.nextcloud-talk.botSecretFile`：密钥文件路径。
- `channels.nextcloud-talk.apiUser`：用于房间查询（私信检测）的 API 用户。
- `channels.nextcloud-talk.apiPassword`：用于房间查询的 API/应用密码。
- `channels.nextcloud-talk.apiPasswordFile`：API 密码文件路径。
- `channels.nextcloud-talk.webhookPort`：Webhook 监听端口（默认：8788）。
- `channels.nextcloud-talk.webhookHost`：Webhook 主机地址（默认：0.0.0.0）。
- `channels.nextcloud-talk.webhookPath`：Webhook 路径（默认：/nextcloud-talk-webhook）。
- `channels.nextcloud-talk.webhookPublicUrl`：外部可访问的 Webhook URL。
- `channels.nextcloud-talk.dmPolicy`：`pairing | allowlist | open | disabled`。
- `channels.nextcloud-talk.allowFrom`：私信允许列表（用户 ID）。启用 `open` 需要同时启用 `"*"`。
- `channels.nextcloud-talk.groupPolicy`：`allowlist | open | disabled`。
- `channels.nextcloud-talk.groupAllowFrom`：群组允许列表（用户 ID）。
- `channels.nextcloud-talk.rooms`：每个房间的设置与允许列表。
- `channels.nextcloud-talk.historyLimit`：群组历史记录限制（0 表示禁用）。
- `channels.nextcloud-talk.dmHistoryLimit`：私信历史记录限制（0 表示禁用）。
- `channels.nextcloud-talk.dms`：每个私信的覆盖设置（historyLimit）。
- `channels.nextcloud-talk.textChunkLimit`：出站文本分块大小（字符数）。
- `channels.nextcloud-talk.chunkMode`：`length`（默认）或 `newline`（在按长度分块前，按空行——即段落边界——进行切分）。
- `channels.nextcloud-talk.blockStreaming`：为此频道禁用块流式传输。
- `channels.nextcloud-talk.blockStreamingCoalesce`：块流式传输合并调优参数。
- `channels.nextcloud-talk.mediaMaxMb`：入站媒体大小上限（MB）。