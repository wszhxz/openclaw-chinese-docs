---
summary: "Signal support via signal-cli (JSON-RPC + SSE), setup paths, and number model"
read_when:
  - Setting up Signal support
  - Debugging Signal send/receive
title: "Signal"
---
# Signal (signal-cli)

状态：外部 CLI 集成。网关通过 HTTP JSON-RPC + SSE 与 `signal-cli` 通信。

## 前置条件

- 服务器上已安装 OpenClaw（以下 Linux 流程已在 Ubuntu 24 上测试）。
- 运行网关的主机上需有 `signal-cli`。
- 一个可接收一条验证短信的电话号码（用于短信注册路径）。
- 注册期间可通过浏览器访问 Signal 验证码 (`signalcaptchas.org`)。

## 快速设置（初学者）

1. 为机器人使用**独立的 Signal 号码**（推荐）。
2. 安装 `signal-cli`（如果使用 JVM 构建版本，需要 Java）。
3. 选择一种设置路径：
   - **路径 A（QR 链接）：** `signal-cli link -n "OpenClaw"` 并用 Signal 扫描。
   - **路径 B（短信注册）：** 使用验证码 + 短信验证注册专用号码。
4. 配置 OpenClaw 并重启网关。
5. 发送第一条私信并批准配对 (`openclaw pairing approve signal <CODE>`)。

最小化配置：

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

| 字段 | 描述 |
| ----------- | ------------------------------------------------- |
| `account` | E.164 格式的机器人电话号码 (`+15551234567`) |
| `cliPath` | `signal-cli` 的路径（如果在 `PATH` 上则为 `signal-cli`） |
| `dmPolicy` | 私信访问策略（推荐 `pairing`） |
| `allowFrom` | 允许私信的电话号码或 `uuid:<id>` 值 |

## 功能说明

- 通过 `signal-cli` 的 Signal 通道（非嵌入式 libsignal）。
- 确定性路由：回复始终返回至 Signal。
- 私信共享代理的主会话；群组是隔离的 (`agent:<agentId>:signal:group:<groupId>`)。

## 配置写入

默认情况下，允许 Signal 写入由 `/config set|unset` 触发的配置更新（需要 `commands.config: true`）。

禁用方法：

```json5
{
  channels: { signal: { configWrites: false } },
}
```

## 号码模型（重要）

- 网关连接到一个 **Signal 设备**（即 `signal-cli` 账户）。
- 如果您在**个人 Signal 账户**上运行机器人，它将忽略您自己的消息（循环保护）。
- 对于“我发短信给机器人，它回复”的场景，请使用**独立的机器人号码**。

## 设置路径 A：链接现有 Signal 账户（QR）

1. 安装 `signal-cli`（JVM 或原生构建版）。
2. 链接机器人账户：
   - `signal-cli link -n "OpenClaw"` 然后在 Signal 中扫描二维码。
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

多账户支持：使用 `channels.signal.accounts` 配合每个账户的配置以及可选的 `name`。请参阅 [`gateway/configuration`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 了解通用模式。

## 设置路径 B：注册专用机器人号码（短信，Linux）

当您想要一个专用机器人号码而不是链接现有的 Signal 应用账户时，请使用此方法。

1. 获取一个可以接收短信的号码（固话可使用语音验证）。
   - 使用专用机器人号码以避免账户/会话冲突。
2. 在网关主机上安装 `signal-cli`：

```bash
VERSION=$(curl -Ls -o /dev/null -w %{url_effective} https://github.com/AsamK/signal-cli/releases/latest | sed -e 's/^.*\/v//')
curl -L -O "https://github.com/AsamK/signal-cli/releases/download/v${VERSION}/signal-cli-${VERSION}-Linux-native.tar.gz"
sudo tar xf "signal-cli-${VERSION}-Linux-native.tar.gz" -C /opt
sudo ln -sf /opt/signal-cli /usr/local/bin/
signal-cli --version
```

如果您使用 JVM 构建版 (`signal-cli-${VERSION}.tar.gz`)，请先安装 JRE 25+。
保持 `signal-cli` 更新；上游指出随着 Signal 服务器 API 的变化，旧版本可能会失效。

3. 注册并验证号码：

```bash
signal-cli -a +<BOT_PHONE_NUMBER> register
```

如果需要验证码：

1. 打开 `https://signalcaptchas.org/registration/generate.html`。
2. 完成验证码，从"Open Signal"复制 `signalcaptcha://...` 链接目标。
3. 尽可能在与浏览器会话相同的公网 IP 上运行。
4. 立即再次运行注册（验证码令牌过期很快）：

```bash
signal-cli -a +<BOT_PHONE_NUMBER> register --captcha '<SIGNALCAPTCHA_URL>'
signal-cli -a +<BOT_PHONE_NUMBER> verify <VERIFICATION_CODE>
```

4. 配置 OpenClaw，重启网关，验证通道：

```bash
# If you run the gateway as a user systemd service:
systemctl --user restart openclaw-gateway

# Then verify:
openclaw doctor
openclaw channels status --probe
```

5. 配对您的私信发送者：
   - 向机器人号码发送任何消息。
   - 在服务器上批准代码：`openclaw pairing approve signal <PAIRING_CODE>`。
   - 将机器人号码保存为您手机上的联系人，以避免显示“未知联系人”。

注意：使用 `signal-cli` 注册电话号码账户可能会导致该号码的主要 Signal 应用会话登出。建议使用专用机器人号码，或者如果您需要保留现有的手机应用设置，请使用 QR 链接模式。

上游参考：

- `signal-cli` README: `https://github.com/AsamK/signal-cli`
- 验证码流程：`https://github.com/AsamK/signal-cli/wiki/Registration-with-captcha`
- 链接流程：`https://github.com/AsamK/signal-cli/wiki/Linking-other-devices-(Provisioning)`

## 外部守护进程模式 (httpUrl)

如果您想自行管理 `signal-cli`（慢速 JVM 冷启动、容器初始化或共享 CPU），请单独运行守护进程并将 OpenClaw 指向它：

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

这将跳过 OpenClaw 内的自动启动和启动等待。如果自动启动时启动缓慢，请设置 `channels.signal.startupTimeoutMs`。

## 访问控制（私信 + 群组）

私信：

- 默认：`channels.signal.dmPolicy = "pairing"`。
- 未知发送者会收到配对码；消息将被忽略直到被批准（代码 1 小时后过期）。
- 批准方式：
  - `openclaw pairing list signal`
  - `openclaw pairing approve signal <CODE>`
- 配对是 Signal 私信的默认令牌交换方式。详情：[Pairing](/channels/pairing)
- 仅 UUID 发送者（来自 `sourceUuid`）存储为 `uuid:<id>` 在 `channels.signal.allowFrom` 中。

群组：

- `channels.signal.groupPolicy = open | allowlist | disabled`。
- 当设置 `allowlist` 时，`channels.signal.groupAllowFrom` 控制谁可以在群组中触发。
- 运行时注意：如果完全缺少 `channels.signal`，运行时将回退到 `groupPolicy="allowlist"` 进行群组检查（即使设置了 `channels.defaults.groupPolicy`）。

## 工作原理（行为）

- `signal-cli` 作为守护进程运行；网关通过 SSE 读取事件。
- 传入消息被规范化为共享通道信封。
- 回复始终路由回相同的号码或群组。

## 媒体 + 限制

- 出站文本分块为 `channels.signal.textChunkLimit`（默认 4000）。
- 可选的新行分块：设置 `channels.signal.chunkMode="newline"` 以便在长度分块之前按空行（段落边界）分割。
- 支持附件（base64 从 `signal-cli` 获取）。
- 默认媒体上限：`channels.signal.mediaMaxMb`（默认 8）。
- 使用 `channels.signal.ignoreAttachments` 跳过下载媒体。
- 群组历史上下文使用 `channels.signal.historyLimit`（或 `channels.signal.accounts.*.historyLimit`），回退到 `messages.groupChat.historyLimit`。设置 `0` 以禁用（默认 50）。

## 输入提示 + 已读回执

- **输入指示器**：OpenClaw 通过 `signal-cli sendTyping` 发送输入信号，并在回复运行时刷新它们。
- **已读回执**：当 `channels.signal.sendReadReceipts` 为 true 时，OpenClaw 转发允许私信的已读回执。
- Signal-cli 不公开群组的已读回执。

## 反应（消息工具）

- 使用 `message action=react` 配合 `channel=signal`。
- 目标：发送者 E.164 或 UUID（使用配对输出中的 `uuid:<id>`；裸 UUID 也可以）。
- `messageId` 是您要反应的信号的时间戳。
- 群组反应需要 `targetAuthor` 或 `targetAuthorUuid`。

示例：

```
message action=react channel=signal target=uuid:123e4567-e89b-12d3-a456-426614174000 messageId=1737630212345 emoji=🔥
message action=react channel=signal target=+15551234567 messageId=1737630212345 emoji=🔥 remove=true
message action=react channel=signal target=signal:group:<groupId> targetAuthor=uuid:<sender-uuid> messageId=1737630212345 emoji=✅
```

配置：

- `channels.signal.actions.reactions`：启用/禁用反应操作（默认 true）。
- `channels.signal.reactionLevel`：`off | ack | minimal | extensive`。
  - `off`/`ack` 禁用代理反应（消息工具 `react` 将报错）。
  - `minimal`/`extensive` 启用代理反应并设置指导级别。
- 每账户覆盖：`channels.signal.accounts.<id>.actions.reactions`, `channels.signal.accounts.<id>.reactionLevel`。

## 投递目标（CLI/cron）

- 私信：`signal:+15551234567`（或纯 E.164）。
- UUID 私信：`uuid:<id>`（或裸 UUID）。
- 群组：`signal:group:<groupId>`。
- 用户名：`username:<name>`（如果您的 Signal 账户支持）。

## 故障排除

首先运行此步骤：

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

然后根据需要确认私信配对状态：

```bash
openclaw pairing list signal
```

常见故障：

- 守护进程可达但无回复：验证账户/守护进程设置 (`httpUrl`, `account`) 和接收模式。
- 私信被忽略：发送者正在等待配对批准。
- 群组消息被忽略：群组发送者/提及门控阻止了投递。
- 编辑后配置验证错误：运行 `openclaw doctor --fix`。
- 诊断中缺少 Signal：确认 `channels.signal.enabled: true`。

额外检查：

```bash
openclaw pairing list signal
pgrep -af signal-cli
grep -i "signal" "/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log" | tail -20
```

对于分流流程：[/channels/troubleshooting](/channels/troubleshooting)。

## 安全注意事项

- `signal-cli` 将账户密钥本地存储（通常在 `~/.local/share/signal-cli/data/`）。
- 在服务器迁移或重建之前，备份 Signal 账户状态。
- 除非您明确需要更广泛的 DM 访问权限，否则请保留 `channels.signal.dmPolicy: "pairing"`。
- 短信验证仅用于注册或恢复流程，但失去对号码/账户的控制可能会使重新注册变得复杂。

## 配置参考（Signal）

完整配置：[配置](/gateway/configuration)

提供程序选项：

- `channels.signal.enabled`：启用/禁用频道启动。
- `channels.signal.account`：机器人账户的 E.164 格式。
- `channels.signal.cliPath`：`signal-cli` 的路径。
- `channels.signal.httpUrl`：完整的 daemon URL（覆盖主机/端口）。
- `channels.signal.httpHost`, `channels.signal.httpPort`：daemon 绑定（默认 127.0.0.1:8080）。
- `channels.signal.autoStart`：自动启动 daemon（如果 `httpUrl` 未设置则默认为 true）。
- `channels.signal.startupTimeoutMs`：启动等待超时时间（毫秒），上限 120000。
- `channels.signal.receiveMode`：`on-start | manual`。
- `channels.signal.ignoreAttachments`：跳过附件下载。
- `channels.signal.ignoreStories`：忽略来自 daemon 的动态。
- `channels.signal.sendReadReceipts`：转发已读回执。
- `channels.signal.dmPolicy`：`pairing | allowlist | open | disabled`（默认：配对）。
- `channels.signal.allowFrom`：DM 白名单（E.164 或 `uuid:<id>`）。`open` 需要 `"*"`。Signal 没有用户名；请使用电话/UUID ID。
- `channels.signal.groupPolicy`：`open | allowlist | disabled`（默认：白名单）。
- `channels.signal.groupAllowFrom`：群发件人白名单。
- `channels.signal.historyLimit`：作为上下文包含的最大群消息数（0 表示禁用）。
- `channels.signal.dmHistoryLimit`：DM 历史记录限制（以用户轮次计）。按用户覆盖：`channels.signal.dms["<phone_or_uuid>"].historyLimit`。
- `channels.signal.textChunkLimit`：出站块大小（字符）。
- `channels.signal.chunkMode`：`length`（默认）或 `newline`，以便在长度分块前按空行（段落边界）分割。
- `channels.signal.mediaMaxMb`：入站/出站媒体上限（MB）。

相关全局选项：

- `agents.list[].groupChat.mentionPatterns`（Signal 不支持原生提及）。
- `messages.groupChat.mentionPatterns`（全局回退）。
- `messages.responsePrefix`。