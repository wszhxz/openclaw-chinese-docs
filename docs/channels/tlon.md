---
summary: "Tlon/Urbit support status, capabilities, and configuration"
read_when:
  - Working on Tlon/Urbit channel features
title: "Tlon"
---
# Tlon（插件）

Tlon 是基于 Urbit 构建的去中心化即时通讯工具。OpenClaw 可连接到您的 Urbit 飞船，并可回复私信和群聊消息。默认情况下，群组回复需要 @ 提及，也可以通过允许列表进一步限制。

状态：通过插件支持。私信、群组提及、线程回复和纯文本媒体回退（URL 附加到标题）。表情、投票和原生媒体上传不被支持。

## 所需插件

Tlon 作为插件提供，不包含在核心安装中。

通过 CLI（npm 注册表）安装：

```bash
openclaw plugins install @openclaw/tlon
```

本地检出（当从 git 仓库运行时）：

```bash
openclaw plugins install ./extensions/tlon
```

详情：[插件](/plugin)

## 配置

1. 安装 Tlon 插件。
2. 收集您的飞船 URL 和登录代码。
3. 配置 `channels.tlon`。
4. 重启网关。
5. 向机器人发送私信或在群组频道中提及它。

最小配置（单账户）：

```json5
{
  channels: {
    t.
    tlon: {
      enabled: true,
      ship: "~sampel-palnet",
      url: "https://your-ship-host",
      code: "lidlut-tabwed-pillex-ridrup",
    },
  },
}
```

## 群组频道

默认启用自动发现。您也可以手动固定频道：

```json5
{
  channels: {
    tlon: {
      groupChannels: ["chat/~host-ship/general", "chat/~host-ship/support"],
    },
  },
}
```

禁用自动发现：

```json5
{
  channels: {
    tlon: {
      autoDiscoverChannels: false,
    },
  },
}
```

## 访问控制

私信允许列表（空 = 允许所有）：

```json5
{
  channels: {
    tlon: {
      dmAllowlist: ["~zod", "~nec"],
    },
  },
}
```

群组授权（默认受限）：

```json5
{
  channels: {
    tlon: {
      defaultAuthorizedShips: ["~zod"],
      authorization: {
        channelRules: {
          "chat/~host-ship/general": {
            mode: "restricted",
            allowedShips: ["~zod", "~nec"],
          },
          "chat/~host-ship/announcements": {
            mode: "open",
          },
        },
      },
    },
  },
}
```

## 交付目标（CLI/定时任务）

使用 `openclaw message send` 或定时任务交付：

- 私信：`~sampel-palnet` 或 `dm/~sampel-palnet`
- 群组：`chat/~host-ship/channel` 或 `group:~host-ship/channel`

## 注意事项

- 群组回复需要提及（例如 `~your-bot-ship`）才能响应。
- 线程回复：如果入站消息在某个线程中，OpenClaw 会在该线程内回复。
- 媒体：`sendMedia` 会回退为文本 + URL（不支持原生上传）。