---
summary: "Signal support via signal-cli (JSON-RPC + SSE), setup, and number model"
read_when:
  - Setting up Signal support
  - Debugging Signal send/receive
title: "Signal"
---
# 信号（signal-cli）

状态：外部命令行界面（CLI）集成。网关通过 HTTP JSON-RPC + SSE 与 `signal-cli` 通信。

## 快速设置（初学者）

1. 为机器人使用一个独立的 Signal 号码（推荐）。
2. 安装 `signal-cli`（需要 Java）。
3. 链接机器人设备并启动守护进程：
   - `signal-cli link -n "OpenClaw"`
4. 配置 OpenClaw 并启动网关。

最小配置：

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15551234567",
      cliPath: "signal-cli",
      dmPolicy: "pairing",
      allowFrom: ["+15557654321"],
    },
  },
}
```

## 它是什么

- 通过 `signal-cli` 实现的 Signal 通道（不是嵌入式 libsignal）。
- 确定性路由：回复总是返回到 Signal。
- 单聊共享代理的主要会话；群组是隔离的（`agent:<agentId>:signal:group:<groupId>`）。

## 配置写入

默认情况下，允许 Signal 写入由 `/config set|unset` 触发的配置更新（需要 `commands.config: true`）。

禁用方式：

```json5
{
  channels: { signal: { configWrites: false } },
}
```

## 号码模型（重要）

- 网关连接到一个 **Signal 设备**（即 `signal-cli` 账户）。
- 如果你在 **你的个人 Signal 账户** 上运行机器人，它将忽略你自己的消息（循环保护）。
- 要实现“我发消息给机器人，它回复”，请使用 **独立的机器人号码**。

## 设置（快速路径）

1. 安装 `signal-cli`（需要 Java）。
2. 链接机器人账户：
   - `signal-cli link -n "OpenClaw"` 然后扫描 Signal 中的二维码。
3. 配置 Signal 并启动网关。

示例：

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15551234567",
      cliPath: "signal-cli",
      dmPolicy: "pairing",
      allowFrom: ["+15557654321"],
    },
  },
}
```

多账户支持：使用 `channels.signal.accounts` 配置每个账户，并可选地使用 `name`。查看 [`gateway/configuration`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 了解共享模式。

## 外部守护进程模式（httpUrl）

如果你想自己管理 `signal-cli`（慢 JVM 冷启动、容器初始化或共享 CPU），请单独运行守护进程并让 OpenClaw 指向它：

```json5
{
  channels: {
    signal: {
      httpUrl: "http://127.0.0.1:8080",
      autoStart: false,
    },
  },
}
```

这会跳过自动启动和 OpenClaw 内部的启动等待。对于自动启动时的慢启动，设置 `channels.signal.startupTimeoutMs`。

## 访问控制（单聊 + 群组）

单聊：

- 默认：`channels.signal.dmPolicy = "pairing"`。
- 未知发送者会收到配对码；消息在批准前被忽略（码在 1 小时后过期）。
- 批准方式：
  - `openclaw pairing list signal`
  - `openclaw pairing approve signal <CODE>`
- 配对是 Signal 单聊的默认令牌交换。详情：[配对](/start/pairing)
- 仅 UUID 发送者（来自 `sourceUuid`）存储为 `uuid:<id>` 在 `channels.signal.allowFrom` 中。

群组：

- `channels.signal.groupPolicy = open | allowlist | disabled`。
- `channels.signal.groupAllowFrom` 控制在设置为 `allowlist` 时谁可以触发群组中的消息。

## 工作原理（行为）

- `signal-cli` 作为守护进程运行；网关通过 SSE 读取事件。
- 入站消息被规范化为共享通道信封。
- 回复总是返回到相同的号码或群组。

## 媒体 + 限制

- 出站文本被分块到 `channels.signal.textChunkLimit`（默认 4000）。
- 可选换行分块：设置 `channels.signal.chunkMode="newline"` 以在长度分块前按空白行（段落边界）分割。
- 支持附件（从 `signal-cli` 获取 base64）。
- 默认媒体上限：`channels.signal.mediaMaxMb`（默认 8）。
- 使用 `channels.signal.ignoreAttachments` 跳过下载媒体。
- 群组历史上下文使用 `channels.signal.historyLimit`（或 `channels.signal.accounts.*.historyLimit`），回退到 `messages.groupChat.historyLimit`。设置为 `0` 以禁用（默认 50）。

## 输入 + 已读回执

- **输入提示**：OpenClaw 通过 `signal-cli sendTyping` 发送输入信号，并在回复运行时刷新它们。
- **已读回执**：当 `channels.signal.sendReadReceipts` 为 true 时，OpenClaw 会转发允许的单聊的已读回执。
- Signal-cli 不暴露群组的已读回执。

## 反应（消息工具）

- 使用 `message action=react` 并设置 `channel=signal`。
- 目标：发送者 E.164 或 UUID（使用 `uuid:<id>` 从配对输出；裸 UUID 也有效）。
- `messageId` 是你正在反应的消息的 Signal 时间戳。
- 群组反应需要 `targetAuthor` 或 `targetAuthorUuid`。

示例：

```
message action=react channel=signal target=uuid:123e4