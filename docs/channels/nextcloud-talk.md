---
summary: "Nextcloud Talk support status, capabilities, and configuration"
read_when:
  - Working on Nextcloud Talk channel features
title: "Nextcloud Talk"
---
# Nextcloud Talk

状态：捆绑插件（Webhook Bot）。支持直接消息、房间、反应和 Markdown 消息。

## 捆绑插件

Nextcloud Talk 作为捆绑插件随当前 OpenClaw 版本发布，因此常规打包构建无需单独安装。

如果您使用的是旧版本构建或排除了 Nextcloud Talk 的自定义安装，请手动安装：

通过 CLI 安装（npm 注册表）：

```bash
openclaw plugins install @openclaw/nextcloud-talk
```

本地检出（当从 git 仓库运行时）：

```bash
openclaw plugins install ./path/to/local/nextcloud-talk-plugin
```

详情：[插件](/tools/plugin)

## 快速设置（初学者）

1. 确保 Nextcloud Talk 插件可用。
   - 当前打包的 OpenClaw 版本已包含它。
   - 旧版/自定义安装可使用上述命令手动添加。
2. 在您的 Nextcloud 服务器上创建一个机器人：

   ```bash
   ./occ talk:bot:install "OpenClaw" "<shared-secret>" "<webhook-url>" --feature reaction
   ```

3. 在目标房间设置中启用机器人。
4. 配置 OpenClaw：
   - 配置：`channels.nextcloud-talk.baseUrl` + `channels.nextcloud-talk.botSecret`
   - 或环境变量：`NEXTCLOUD_TALK_BOT_SECRET`（仅限默认账户）
5. 重启网关（或完成设置）。

最小化配置：

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

- 机器人无法发起 DMs。用户必须先向机器人发送消息。
- Webhook URL 必须能被网关访问；如果在代理后面，请设置 `webhookPublicUrl`。
- 机器人 API 不支持媒体上传；媒体以 URL 形式发送。
- Webhook 负载不区分 DMs 与房间；设置 `apiUser` + `apiPassword` 以启用房间类型查找（否则 DMs 将被视为房间）。

## 访问控制 (DMs)

- 默认：`channels.nextcloud-talk.dmPolicy = "pairing"`。未知发送者会收到配对码。
- 通过以下方式批准：
  - `openclaw pairing list nextcloud-talk`
  - `openclaw pairing approve nextcloud-talk <CODE>`
- 公开 DMs：`channels.nextcloud-talk.dmPolicy="open"` 加上 `channels.nextcloud-talk.allowFrom=["*"]`。
- `allowFrom` 仅匹配 Nextcloud 用户 ID；显示名称被忽略。

## 房间（群组）

- 默认：`channels.nextcloud-talk.groupPolicy = "allowlist"`（提及门控）。
- 使用 `channels.nextcloud-talk.rooms` 允许列表房间：

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

- 若要不允许任何房间，请保持允许列表为空或设置 `channels.nextcloud-talk.groupPolicy="disabled"`。

## 功能特性

| 功能 | 状态 |
| --------------- | ------------- |
| 直接消息 | 支持 |
| 房间 | 支持 |
| 线程 | 不支持 |
| 媒体 | 仅 URL |
| 反应 | 支持 |
| 原生命令 | 不支持 |

## 配置参考 (Nextcloud Talk)

完整配置：[配置](/gateway/configuration)

提供者选项：

- `channels.nextcloud-talk.enabled`：启用/禁用频道启动。
- `channels.nextcloud-talk.baseUrl`：Nextcloud 实例 URL。
- `channels.nextcloud-talk.botSecret`：机器人共享密钥。
- `channels.nextcloud-talk.botSecretFile`：常规文件密钥路径。符号链接将被拒绝。
- `channels.nextcloud-talk.apiUser`：用于房间查找的 API 用户（DM 检测）。
- `channels.nextcloud-talk.apiPassword`：用于房间查找的 API/应用密码。
- `channels.nextcloud-talk.apiPasswordFile`：API 密码文件路径。
- `channels.nextcloud-talk.webhookPort`：Webhook 监听端口（默认：8788）。
- `channels.nextcloud-talk.webhookHost`：Webhook 主机（默认：0.0.0.0）。
- `channels.nextcloud-talk.webhookPath`：Webhook 路径（默认：/nextcloud-talk-webhook）。
- `channels.nextcloud-talk.webhookPublicUrl`：外部可访问的 Webhook URL。
- `channels.nextcloud-talk.dmPolicy`：`pairing | allowlist | open | disabled`。
- `channels.nextcloud-talk.allowFrom`：DM 允许列表（用户 ID）。`open` 需要 `"*"`。
- `channels.nextcloud-talk.groupPolicy`：`allowlist | open | disabled`。
- `channels.nextcloud-talk.groupAllowFrom`：群组允许列表（用户 ID）。
- `channels.nextcloud-talk.rooms`：每房间设置和允许列表。
- `channels.nextcloud-talk.historyLimit`：群组历史记录限制（0 表示禁用）。
- `channels.nextcloud-talk.dmHistoryLimit`：DM 历史记录限制（0 表示禁用）。
- `channels.nextcloud-talk.dms`：每 DM 覆盖设置（historyLimit）。
- `channels.nextcloud-talk.textChunkLimit`：出站文本块大小（字符数）。
- `channels.nextcloud-talk.chunkMode`：`length`（默认）或 `newline` 以便在按长度分块之前在空行（段落边界）处分割。
- `channels.nextcloud-talk.blockStreaming`：为此频道禁用块流式传输。
- `channels.nextcloud-talk.blockStreamingCoalesce`：块流式传输合并调整。
- `channels.nextcloud-talk.mediaMaxMb`：入站媒体上限（MB）。

## 相关

- [频道概览](/channels) — 所有支持的频道
- [配对](/channels/pairing) — DM 认证和配对流程
- [群组](/channels/groups) — 群聊行为和提及门控
- [频道路由](/channels/channel-routing) — 消息会话路由
- [安全](/gateway/security) — 访问模型和加固