---
summary: "Signal support via signal-cli (JSON-RPC + SSE), setup paths, and number model"
read_when:
  - Setting up Signal support
  - Debugging Signal send/receive
title: "Signal"
---
# Signal (signal-cli)

状态: 外部CLI集成。网关通过HTTP JSON-RPC + SSE与`signal-cli`通信。

## 前提条件

- 在您的服务器上安装了OpenClaw（以下Linux流程在Ubuntu 24上测试过）。
- 主机上运行网关的地方有可用的`signal-cli`。
- 一个可以接收一条验证短信的电话号码（用于短信注册路径）。
- 注册期间需要浏览器访问Signal验证码(`signalcaptchas.org`)。

## 快速设置（初学者）

1. 为机器人使用一个**单独的Signal号码**（推荐）。
2. 安装`signal-cli`（如果使用JVM构建，则需要Java）。
3. 选择一个设置路径：
   - **路径A（二维码链接）：** `signal-cli link -n "OpenClaw"`并用Signal扫描。
   - **路径B（短信注册）：** 使用验证码+短信验证注册一个专用号码。
4. 配置OpenClaw并重启网关。
5. 发送第一条私信并批准配对(`openclaw pairing approve signal <CODE>`)。

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

字段参考：

| 字段       | 描述                                       |
| ----------- | ------------------------------------------------- |
| `account`   | 机器人电话号码，E.164格式 (`+15551234567`) |
| `cliPath`   | `signal-cli`的路径 (`signal-cli` 如果在`PATH`)  |
| `dmPolicy`  | 私信访问策略 (`pairing` 推荐)          |
| `allowFrom` | 允许发送私信的电话号码或`uuid:<id>`值 |

## 这是什么

- 通过`signal-cli`的Signal通道（不是嵌入式libsignal）。
- 确定性路由：回复总是回到Signal。
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
- 如果您在**自己的Signal账户**上运行机器人，它将忽略您自己的消息（循环保护）。
- 对于“我给机器人发短信，它回复”，请使用一个**单独的机器人号码**。

## 设置路径A：链接现有Signal账户（二维码）

1. 安装`signal-cli`（JVM或原生构建）。
2. 链接一个机器人账户：
   - `signal-cli link -n "OpenClaw"`然后在Signal中扫描二维码。
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

多账户支持：使用 `channels.signal.accounts` 并配合每个账户的配置以及可选的 `name`。请参阅[`gateway/configuration`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 以了解共享模式。

## 设置路径 B：注册专用机器人号码（短信，Linux）

当您希望使用专用机器人号码而不是链接现有的Signal应用账户时，请使用此方法。

1. 获取一个可以接收短信（或固话的语音验证）的号码。
   - 使用专用机器人号码以避免账户/会话冲突。
2. 在网关主机上安装 `signal-cli`：

```bash
VERSION=$(curl -Ls -o /dev/null -w %{url_effective} https://github.com/AsamK/signal-cli/releases/latest | sed -e 's/^.*\/v//')
curl -L -O "https://github.com/AsamK/signal-cli/releases/download/v${VERSION}/signal-cli-${VERSION}-Linux-native.tar.gz"
sudo tar xf "signal-cli-${VERSION}-Linux-native.tar.gz" -C /opt
sudo ln -sf /opt/signal-cli /usr/local/bin/
signal-cli --version
```

如果您使用的是JVM构建 (`signal-cli-${VERSION}.tar.gz`)，请先安装JRE 25+。
保持 `signal-cli` 更新；上游说明旧版本可能会因Signal服务器API的变化而失效。

3. 注册并验证号码：

```bash
signal-cli -a +<BOT_PHONE_NUMBER> register
```

如果需要验证码：

1. 打开 `https://signalcaptchas.org/registration/generate.html`。
2. 完成验证码，从“打开Signal”中复制 `signalcaptcha://...` 链接目标。
3. 尽可能从与浏览器会话相同的外部IP运行。
4. 立即重新运行注册（验证码令牌很快过期）：

```bash
signal-cli -a +<BOT_PHONE_NUMBER> register --captcha '<SIGNALCAPTCHA_URL>'
signal-cli -a +<BOT_PHONE_NUMBER> verify <VERIFICATION_CODE>
```

4. 配置OpenClaw，重启网关，验证通道：

```bash
# If you run the gateway as a user systemd service:
systemctl --user restart openclaw-gateway

# Then verify:
openclaw doctor
openclaw channels status --probe
```

5. 配对您的DM发送者：
   - 向机器人号码发送任何消息。
   - 在服务器上批准代码：`openclaw pairing approve signal <PAIRING_CODE>`。
   - 将机器人号码保存为手机上的联系人以避免“未知联系人”。

重要提示：使用 `signal-cli` 注册电话号码账户可能会使该号码的主要Signal应用会话失效。建议使用专用机器人号码，或者如果需要保留现有手机应用设置，则使用QR链接模式。

上游参考：

- `signal-cli` README: `https://github.com/AsamK/signal-cli`
- 验证码流程: `https://github.com/AsamK/signal-cli/wiki/Registration-with-captcha`
- 链接流程: `https://github.com/AsamK/signal-cli/wiki/Linking-other-devices-(Provisioning)`

## 外部守护进程模式 (httpUrl)

如果您希望自行管理 `signal-cli`（慢速JVM冷启动、容器初始化或共享CPU），请单独运行守护进程并让OpenClaw指向它：

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

这会跳过OpenClaw中的自动启动和启动等待。对于自动启动时的慢启动情况，请设置`channels.signal.startupTimeoutMs`。

## 访问控制（私信 + 群组）

私信：

- 默认：`channels.signal.dmPolicy = "pairing"`。
- 未知发送者会收到一个配对码；消息会被忽略直到被批准（码在1小时后过期）。
- 通过以下方式批准：
  - `openclaw pairing list signal`
  - `openclaw pairing approve signal <CODE>`
- 配对是Signal私信的默认令牌交换方式。详情：[配对](/channels/pairing)
- 仅UUID发送者（来自`sourceUuid`）存储为`uuid:<id>`在`channels.signal.allowFrom`中。

群组：

- `channels.signal.groupPolicy = open | allowlist | disabled`。
- `channels.signal.groupAllowFrom`控制谁可以在群组中触发，当`allowlist`被设置时。

## 工作原理（行为）

- `signal-cli`作为守护进程运行；网关通过SSE读取事件。
- 入站消息被标准化为共享频道信封。
- 回复总是路由回相同的号码或群组。

## 媒体 + 限制

- 发送的文本被分块为`channels.signal.textChunkLimit`（默认4000）。
- 可选换行符分块：设置`channels.signal.chunkMode="newline"`以在长度分块之前按空白行（段落边界）拆分。
- 支持附件（从`signal-cli`获取的base64）。
- 默认媒体上限：`channels.signal.mediaMaxMb`（默认8）。
- 使用`channels.signal.ignoreAttachments`跳过下载媒体。
- 群组历史上下文使用`channels.signal.historyLimit`（或`channels.signal.accounts.*.historyLimit`），回退到`messages.groupChat.historyLimit`。设置`0`以禁用（默认50）。

## 正在输入 + 已读回执

- **正在输入指示器**：OpenClaw通过`signal-cli sendTyping`发送正在输入信号，并在回复运行时刷新它们。
- **已读回执**：当`channels.signal.sendReadReceipts`为真时，OpenClaw转发允许的私信的已读回执。
- Signal-cli不公开群组的已读回执。

## 反应（消息工具）

- 使用`message action=react`与`channel=signal`。
- 目标：发送者E.164或UUID（使用配对输出中的`uuid:<id>`；裸UUID也可以）。
- `messageId`是你正在反应的消息的Signal时间戳。
- 群组反应需要`targetAuthor`或`targetAuthorUuid`。

示例：

```
message action=react channel=signal target=uuid:123e4567-e89b-12d3-a456-426614174000 messageId=1737630212345 emoji=🔥
message action=react channel=signal target=+15551234567 messageId=1737630212345 emoji=🔥 remove=true
message action=react channel=signal target=signal:group:<groupId> targetAuthor=uuid:<sender-uuid> messageId=1737630212345 emoji=✅
```

配置：

- `channels.signal.actions.reactions`: 启用/禁用反应操作（默认为true）。
- `channels.signal.reactionLevel`: `off | ack | minimal | extensive`.
  - `off`/`ack` 禁用代理反应（消息工具 `react` 将出错）。
  - `minimal`/`extensive` 启用代理反应并设置指导级别。
- 按账户覆盖：`channels.signal.accounts.<id>.actions.reactions`, `channels.signal.accounts.<id>.reactionLevel`。

## 交付目标（CLI/cron）

- 直接消息：`signal:+15551234567`（或纯E.164）。
- UUID 直接消息：`uuid:<id>`（或裸UUID）。
- 群组：`signal:group:<groupId>`。
- 用户名：`username:<name>`（如果您的Signal账户支持）。

## 故障排除

首先运行这个梯子：

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

然后根据需要确认直接消息配对状态：

```bash
openclaw pairing list signal
```

常见故障：

- 守护进程可达但没有回复：验证账户/守护进程设置 (`httpUrl`, `account`) 和接收模式。
- 忽略直接消息：发送者正在等待配对批准。
- 忽略群组消息：群组发送者/提及门控阻止了传递。
- 编辑后的配置验证错误：运行 `openclaw doctor --fix`。
- 诊断中缺少Signal：确认 `channels.signal.enabled: true`。

额外检查：

```bash
openclaw pairing list signal
pgrep -af signal-cli
grep -i "signal" "/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log" | tail -20
```

用于故障排除流程：[/channels/troubleshooting](/channels/troubleshooting)。

## 安全说明

- `signal-cli` 本地存储账户密钥（通常是 `~/.local/share/signal-cli/data/`）。
- 在服务器迁移或重建之前备份Signal账户状态。
- 除非您明确希望更广泛的直接消息访问，否则保留 `channels.signal.dmPolicy: "pairing"`。
- 短信验证仅在注册或恢复流程中需要，但失去对该号码/账户的控制可能会使重新注册复杂化。

## 配置参考（Signal）

完整配置：[Configuration](/gateway/configuration)

提供商选项：

- `channels.signal.enabled`: 启用/禁用通道启动。
- `channels.signal.account`: 机器人的E.164账号。
- `channels.signal.cliPath`: `signal-cli`的路径。
- `channels.signal.httpUrl`: 守护进程完整URL（覆盖主机/端口）。
- `channels.signal.httpHost`, `channels.signal.httpPort`: 守护进程绑定（默认127.0.0.1:8080）。
- `channels.signal.autoStart`: 自动启动守护进程（如果未设置`httpUrl`，默认为true）。
- `channels.signal.startupTimeoutMs`: 启动等待超时时间（毫秒），上限120000。
- `channels.signal.receiveMode`: `on-start | manual`。
- `channels.signal.ignoreAttachments`: 跳过附件下载。
- `channels.signal.ignoreStories`: 忽略来自守护进程的故事。
- `channels.signal.sendReadReceipts`: 转发已读回执。
- `channels.signal.dmPolicy`: `pairing | allowlist | open | disabled`（默认：pairing）。
- `channels.signal.allowFrom`: 直接消息白名单（E.164或`uuid:<id>`）。`open`需要`"*"`。Signal没有用户名；使用电话/UUID ID。
- `channels.signal.groupPolicy`: `open | allowlist | disabled`（默认：allowlist）。
- `channels.signal.groupAllowFrom`: 群组发送者白名单。
- `channels.signal.historyLimit`: 作为上下文包含的最大群组消息数（0禁用）。
- `channels.signal.dmHistoryLimit`: 每用户直接消息历史记录限制。每个用户的重写：`channels.signal.dms["<phone_or_uuid>"].historyLimit`。
- `channels.signal.textChunkLimit`: 出站块大小（字符）。
- `channels.signal.chunkMode`: `length`（默认）或`newline`在长度分块之前按空白行（段落边界）拆分。
- `channels.signal.mediaMaxMb`: 入站/出站媒体限制（MB）。

相关全局选项：

- `agents.list[].groupChat.mentionPatterns`（Signal不支持原生提及）。
- `messages.groupChat.mentionPatterns`（全局回退）。
- `messages.responsePrefix`。