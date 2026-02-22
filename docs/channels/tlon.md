---
summary: "Tlon/Urbit support status, capabilities, and configuration"
read_when:
  - Working on Tlon/Urbit channel features
title: "Tlon"
---
# Tlon (插件)

Tlon 是一个基于 Urbit 的去中心化消息传递工具。OpenClaw 连接到你的 Urbit 船只，并可以响应私信和群组聊天消息。默认情况下，群组回复需要使用 @ 提及，并且可以通过白名单进一步限制。

状态：通过插件支持。支持私信、群组提及、线程回复以及仅文本媒体回退（URL 添加到标题）。不支持反应、投票和原生媒体上传。

## 需要插件

Tlon 作为插件提供，不包含在核心安装中。

通过 CLI 安装（npm 仓库）：

```bash
openclaw plugins install @openclaw/tlon
```

本地检出（从 git 仓库运行时）：

```bash
openclaw plugins install ./extensions/tlon
```

详情：[插件](/tools/plugin)

## 设置

1. 安装 Tlon 插件。
2. 获取你的船只 URL 和登录代码。
3. 配置 `channels.tlon`。
4. 重启网关。
5. 私信机器人或在群组频道中提及它。

最小配置（单个账户）：

```json5
{
  channels: {
    tlon: {
      enabled: true,
      ship: "~sampel-palnet",
      url: "https://your-ship-host",
      code: "lidlut-tabwed-pillex-ridrup",
    },
  },
}
```

私有/LAN 船只 URL（高级）：

默认情况下，OpenClaw 会阻止此插件的私有/内部主机名和 IP 范围（SSRF 硬化）。
如果你的船只 URL 在私有网络上（例如 `http://192.168.1.50:8080` 或 `http://localhost:8080`），
你必须显式选择加入：

```json5
{
  channels: {
    tlon: {
      allowPrivateNetwork: true,
    },
  },
}
```

## 群组频道

默认启用自动发现。你也可以手动固定频道：

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

私信白名单（空 = 允许所有）：

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

## 交付目标（CLI/cron）

与 `openclaw message send` 或 cron 交付一起使用：

- 私信：`~sampel-palnet` 或 `dm/~sampel-palnet`
- 群组：`chat/~host-ship/channel` 或 `group:~host-ship/channel`

## 注意事项

- 群组回复需要提及（例如 `~your-bot-ship`）才能响应。
- 线程回复：如果传入消息在一个线程中，OpenClaw 将在线程中回复。
- 媒体：`sendMedia` 回退到文本 + URL（无原生上传）。