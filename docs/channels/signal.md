---
summary: "Signal support via signal-cli (JSON-RPC + SSE), setup, and number model"
read_when:
  - Setting up Signal support
  - Debugging Signal send/receive
title: "Signal"
---
# Signal (signal-cli)

状态：外部CLI集成。网关通过HTTP JSON-RPC + SSE与`signal-cli`通信。

## 快速设置（初学者）

1. 为机器人使用一个**独立的Signal号码**（推荐）。
2. 安装`signal-cli`（需要Java）。
3. 链接机器人设备并启动守护进程：
   - `signal-cli link -n "OpenClaw"`
4. 配置OpenClaw并启动网关。

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

## 什么是它

- 通过`signal-cli`的Signal通道（不是嵌入的libsignal）。
- 确定性路由：回复总是返回到Signal。
- 私信共享代理的主要会话；群组是隔离的(`agent:<agentId>:signal:group:<groupId>`)。

## 配置写入

默认情况下，Signal允许由`/config set|unset`触发的配置更新写入（需要`commands.config: true`）。

禁用方法：

```json5
{
  channels: { signal: { configWrites: false } },
}
```

## 号码模型（重要）

- 网关连接到一个**Signal设备**（即`signal-cli`账户）。
- 如果你在**你的个人Signal账户**上运行机器人，它会忽略你自己的消息（循环保护）。
- 对于“我给机器人发消息然后它回复”，使用一个**独立的机器人号码**。

## 设置（快速路径）

1. 安装`signal-cli`（需要Java）。
2. 链接一个机器人账户：
   - `signal-cli link -n "OpenClaw"` 然后在Signal中扫描二维码。
3. 配置Signal并启动网关。

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

多账户支持：使用`channels.signal.accounts`配合每个账户的配置和可选的`name`。参见[`gateway/configuration`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts)了解共享模式。

## 外部守护进程模式（httpUrl）

如果你想自己管理`signal-cli`（慢JVM冷启动、容器初始化或共享CPU），单独运行守护进程并指向OpenClaw：

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

这跳过了自动启动和OpenClaw中的启动等待时间。对于自动启动时的慢启动，设置`channels.signal.startupTimeoutMs`。

## 访问控制（私信+群组）

私信：

- 默认：`channels.signal.dmPolicy = "pairing"`。
- 未知发送者会收到配对码；消息会被忽略直到批准（码过期时间为1小时）。
- 批准方式：
  - `openclaw pairing list signal`
  - `openclaw pairing approve signal <CODE>`
- 配对是Signal私信的默认令牌交换方式。详情：[配对](/start/pairing)
- 仅UUID发送者（来自`sourceUuid`）存储为`uuid:<id>`在`channels.signal.allowFrom`中。

群组：

- `channels.signal.groupPolicy = open | allowlist | disabled`。
- `channels.signal.groupAllowFrom` 控制谁可以在群组中触发，当`allowlist`被设置时。

## 工作原理（行为）

- `signal-cli` 作为守护进程运行；网关通过SSE读取事件。
- 入站消息被标准化为共享频道信封。
- 回复总是路由回相同的号码或群组。

## 媒体+限制

- 发送的文本被分块为`channels.signal.textChunkLimit`（默认4000）。
- 可选换行符分块：设置`channels.signal.chunkMode="newline"`以在长度分块之前按空白行（段落边界）拆分。
- 支持附件（从`signal-cli`获取base64）。
- 默认媒体上限：`channels.signal.mediaMaxMb`（默认8）。
- 使用`channels.signal.ignoreAttachments`跳过下载媒体。
- 群组历史上下文使用`channels.signal.historyLimit`（或`channels.signal.accounts.*.historyLimit`），回退到`messages.groupChat.historyLimit`。设置`0`以禁用（默认50）。

## 正在输入+已读回执

- **正在输入指示器**：OpenClaw通过`signal-cli sendTyping`发送正在输入信号，并在回复运行期间刷新它们。
- **已读回执**：当`channels.signal.sendReadReceipts`为真时，OpenClaw转发允许的私信的已读回执。
- Signal-cli不暴露群组的已读回执。

## 反应（消息工具）

- 使用`message action=react`与`channel=signal`。
- 目标：发送者的E.164或UUID（使用配对输出中的`uuid:<id>`；裸UUID也可以）。
- `messageId` 是你要反应的消息的Signal时间戳。
- 群组反应需要`targetAuthor` 或 `targetAuthorUuid`。

示例：

```
message action=react channel=signal target=uuid:123e4567-e89b-12d3-a456-426614174000 messageId=1737630212345 emoji=🔥
message action=react channel=signal target=+15551234567 messageId=1737630212345 emoji=🔥 remove=true
message action=react channel=signal target=signal:group:<groupId> targetAuthor=uuid:<sender-uuid> messageId=1737630212345 emoji=✅
```

配置：

- `channels.signal.actions.reactions`：启用/禁用反应操作（默认true）。
- `channels.signal.reactionLevel`：`off | ack | minimal | extensive`。
  - `off`/`ack` 禁用代理反应（消息工具`react`将出错）。
  - `minimal`/`extensive` 启用代理反应并设置指导级别。
- 按账户覆盖：`channels.signal.accounts.<id>.actions.reactions`，`channels.signal.accounts.<id>.reactionLevel`。

## 交付目标（CLI/cron）

- 私信：`signal:+15551234567`（或纯E.164）。
- UUID私信：`uuid:<id>`（或裸UUID）。
- 群组：`signal:group:<groupId>`。
- 用户名：`username:<name>`（如果你的Signal账户支持）。

## 配置参考（Signal）

完整配置：[配置](/gateway/configuration)

提供商选项：

- `channels.signal.enabled`：启用/禁用通道启动。
- `channels.signal.account`：机器人的E.164号码。
- `channels.signal.cliPath`：`signal-cli`的路径。
- `channels.signal.httpUrl`：完整的守护进程URL（覆盖主机/端口）。
- `channels.signal.httpHost`，`channels.signal.httpPort`：守护进程绑定（默认127.0.0.1:8080）。
- `channels.signal.autoStart`：自动启动守护进程（如果未设置`httpUrl`则默认为true）。
- `channels.signal.startupTimeoutMs`：启动等待超时时间（毫秒），最大值120000。
- `channels.signal.receiveMode`：`on-start | manual`。
- `channels.signal.ignoreAttachments`：跳过附件下载。
- `channels.signal.ignoreStories`：忽略守护进程中的故事。
- `channels.signal.sendReadReceipts`：转发已读回执。
- `channels.signal.dmPolicy`：`pairing | allowlist | open | disabled`（默认：配对）。
- `channels.signal.allowFrom`：私信白名单（E.164或`uuid:<id>`）。`open`需要`"*"`。Signal没有用户名；使用电话/UUID ID。
- `channels.signal.groupPolicy`：`open | allowlist | disabled`（默认：白名单）。
- `channels.signal.groupAllowFrom`：群组发送者白名单。
- `channels.signal.historyLimit`：包含在上下文中的最大群组消息数（0禁用）。
- `channels.signal.dmHistoryLimit`：用户轮次的私信历史限制。按用户覆盖：`channels.signal.dms["<phone_or_uuid>"].historyLimit`。
- `channels.signal.textChunkLimit`：出站分块大小（字符）。
- `channels.signal.chunkMode`：`length`（默认）或`newline` 在长度分块之前按空白行（段落边界）拆分。
- `channels.signal.mediaMaxMb`：入站/出站媒体上限（MB）。

相关全局选项：

- `agents.list[].groupChat.mentionPatterns`（Signal不支持原生提及）。
- `messages.groupChat.mentionPatterns`（全局回退）。
- `messages.responsePrefix`。