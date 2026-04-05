---
summary: "QQ Bot setup, config, and usage"
read_when:
  - You want to connect OpenClaw to QQ
  - You need QQ Bot credential setup
  - You want QQ Bot group or private chat support
title: QQ Bot
---
# QQ 机器人

QQ 机器人通过官方 QQ 机器人 API（WebSocket 网关）连接到 OpenClaw。该插件支持 C2C 私聊、群组 @消息以及公会频道消息，并支持富媒体（图片、语音、视频、文件）。

状态：捆绑插件。支持直接消息、群聊、公会频道和媒体。不支持表情反应和线程。

## 捆绑插件

当前 OpenClaw 版本已捆绑 QQ 机器人，因此常规打包构建不需要单独的 `openclaw plugins install` 步骤。

## 设置

1. 前往 [QQ 开放平台](https://q.qq.com/) 并使用手机 QQ 扫描二维码进行注册/登录。
2. 点击 **创建机器人** 以创建新的 QQ 机器人。
3. 在机器人的设置页面找到 **AppID** 和 **AppSecret** 并复制它们。

> AppSecret 不以明文存储——如果您未保存就离开页面，将不得不重新生成一个新的。

4. 添加频道：

```bash
openclaw channels add --channel qqbot --token "AppID:AppSecret"
```

5. 重启网关。

交互式设置路径：

```bash
openclaw channels add
openclaw configure --section channels
```

## 配置

最小化配置：

```json5
{
  channels: {
    qqbot: {
      enabled: true,
      appId: "YOUR_APP_ID",
      clientSecret: "YOUR_APP_SECRET",
    },
  },
}
```

默认账户环境变量：

- `QQBOT_APP_ID`
- `QQBOT_CLIENT_SECRET`

基于文件的 AppSecret：

```json5
{
  channels: {
    qqbot: {
      enabled: true,
      appId: "YOUR_APP_ID",
      clientSecretFile: "/path/to/qqbot-secret.txt",
    },
  },
}
```

注意：

- 环境变量回退仅适用于默认 QQ 机器人账户。
- `openclaw channels add --channel qqbot --token-file ...` 仅提供 AppSecret；AppID 必须已在配置或 `QQBOT_APP_ID` 中设置。
- `clientSecret` 也接受 SecretRef 输入，而不仅仅是明文字符串。

### 多账户设置

在单个 OpenClaw 实例下运行多个 QQ 机器人：

```json5
{
  channels: {
    qqbot: {
      enabled: true,
      appId: "111111111",
      clientSecret: "secret-of-bot-1",
      accounts: {
        bot2: {
          enabled: true,
          appId: "222222222",
          clientSecret: "secret-of-bot-2",
        },
      },
    },
  },
}
```

每个账户启动自己的 WebSocket 连接并维护独立的令牌缓存（由 `appId` 隔离）。

通过 CLI 添加第二个机器人：

```bash
openclaw channels add --channel qqbot --account bot2 --token "222222222:secret-of-bot-2"
```

### 语音 (STT / TTS)

STT 和 TTS 支持具有优先级回退的两级配置：

| 设置 | 插件特定      | 框架回退            |
| ------- | -------------------- | ----------------------------- |
| STT     | `channels.qqbot.stt` | `tools.media.audio.models[0]` |
| TTS     | `channels.qqbot.tts` | `messages.tts`                |

```json5
{
  channels: {
    qqbot: {
      stt: {
        provider: "your-provider",
        model: "your-stt-model",
      },
      tts: {
        provider: "your-provider",
        model: "your-tts-model",
        voice: "your-voice",
      },
    },
  },
}
```

在任一上设置 `enabled: false` 即可禁用。

出站音频上传/转码行为也可以通过 `channels.qqbot.audioFormatPolicy` 进行调整：

- `sttDirectFormats`
- `uploadDirectFormats`
- `transcodeEnabled`

## 目标格式

| 格式                     | 描述        |
| -------------------------- | ------------------ |
| `qqbot:c2c:OPENID`         | 私聊 (C2C) |
| `qqbot:group:GROUP_OPENID` | 群聊         |
| `qqbot:channel:CHANNEL_ID` | 公会频道      |

> 每个机器人都有自己的一组用户 OpenID。机器人 A 接收到的 OpenID **不能**用于通过机器人 B 发送消息。

## 斜杠命令

AI 队列之前拦截的内置命令：

| 命令        | 描述                          |
| -------------- | ------------------------------------ |
| `/bot-ping`    | 延迟测试                         |
| `/bot-version` | 显示 OpenClaw 框架版本  |
| `/bot-help`    | 列出所有命令                    |
| `/bot-upgrade` | 显示 QQBot 升级指南链接    |
| `/bot-logs`    | 导出最近的网关日志为文件 |

在任何命令后附加 `?` 以获取使用帮助（例如 `/bot-upgrade ?`）。

## 故障排除

- **机器人回复“去火星了”：** 凭据未配置或网关未启动。
- **没有入站消息：** 验证 `appId` 和 `clientSecret` 是否正确，并且机器人在 QQ 开放平台上已启用。
- **使用 `--token-file` 设置仍显示未配置：** `--token-file` 仅设置 AppSecret。您仍然需要在配置或 `QQBOT_APP_ID` 中设置 `appId`。
- **主动消息未到达：** 如果用户最近没有互动，QQ 可能会拦截机器人发起的消息。
- **语音未转录：** 确保已配置 STT 且提供商可访问。