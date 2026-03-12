---
summary: "Signal support via signal-cli (JSON-RPC + SSE), setup paths, and number model"
read_when:
  - Setting up Signal support
  - Debugging Signal send/receive
title: "Signal"
---
# Signal（signal-cli）

状态：外部 CLI 集成。网关通过 HTTP JSON-RPC + SSE 与 `signal-cli` 通信。

## 前置条件

- 服务器上已安装 OpenClaw（以下 Linux 流程在 Ubuntu 24 上测试通过）。
- 网关运行的主机上已提供 `signal-cli`。
- 一个可接收单条验证短信的手机号码（用于短信注册路径）。
- 注册期间需通过浏览器访问 Signal 图形验证码（`signalcaptchas.org`）。

## 快速设置（新手）

1. 为机器人使用**独立的 Signal 号码**（推荐）。
2. 安装 `signal-cli`（若使用 JVM 构建版本，则需预先安装 Java）。
3. 任选一种设置路径：
   - **路径 A（二维码链接）**：执行 `signal-cli link -n "OpenClaw"`，然后用 Signal 扫描二维码。
   - **路径 B（短信注册）**：使用图形验证码 + 短信验证方式注册专用号码。
4. 配置 OpenClaw 并重启网关。
5. 发送首条私信（DM），并批准配对（`openclaw pairing approve signal <CODE>`）。

最小化配置示例：

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

字段说明：

| 字段 | 描述 |
| ---- | ---- |
| `account` | 机器人手机号码（E.164 格式，`+15551234567`） |
| `cliPath` | `signal-cli` 的路径（若运行于 `PATH`，则为 `signal-cli`） |
| `dmPolicy` | 私信访问策略（推荐使用 `pairing`） |
| `allowFrom` | 允许发送私信的手机号码或 `uuid:<id>` 值 |

## 这是什么

- 通过 `signal-cli` 实现的 Signal 通道（非嵌入式 libsignal）。
- 确定性路由：回复始终返回至 Signal。
- 私信共享代理主会话；群组相互隔离（`agent:<agentId>:signal:group:<groupId>`）。

## 配置写入

默认情况下，Signal 被允许通过 `/config set|unset` 触发配置更新（需启用 `commands.config: true`）。

禁用方法：

```json5
{
  channels: { signal: { configWrites: false } },
}
```

## 号码模型（重要）

- 网关连接至一个 **Signal 设备**（即 `signal-cli` 账户）。
- 若在**您个人的 Signal 账户**上运行机器人，它将忽略您本人发送的消息（防循环机制）。
- 若希望实现“我给机器人发消息，它自动回复”，请使用**独立的机器人号码**。

## 设置路径 A：链接已有 Signal 账户（二维码）

1. 安装 `signal-cli`（JVM 或原生构建版本）。
2. 链接机器人账户：
   - 执行 `signal-cli link -n "OpenClaw"`，然后用 Signal 扫描生成的二维码。
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

多账户支持：使用 `channels.signal.accounts`，配合每个账户的独立配置及可选的 `name`。共享模式详见 [`gateway/configuration`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts)。

## 设置路径 B：注册专用机器人号码（短信方式，Linux）

当您希望使用专用机器人号码（而非链接已有 Signal 应用账户）时，请采用此方式。

1. 获取一个可接收短信的号码（固话用户可使用语音验证）。
   - 使用专用机器人号码，以避免账户/会话冲突。
2. 在网关主机上安装 `signal-cli`：

```bash
VERSION=$(curl -Ls -o /dev/null -w %{url_effective} https://github.com/AsamK/signal-cli/releases/latest | sed -e 's/^.*\/v//')
curl -L -O "https://github.com/AsamK/signal-cli/releases/download/v${VERSION}/signal-cli-${VERSION}-Linux-native.tar.gz"
sudo tar xf "signal-cli-${VERSION}-Linux-native.tar.gz" -C /opt
sudo ln -sf /opt/signal-cli /usr/local/bin/
signal-cli --version
```

若您使用 JVM 构建版本（`signal-cli-${VERSION}.tar.gz`），请先安装 JRE 25+。  
请保持 `signal-cli` 为最新版本；上游提示：旧版本可能因 Signal 服务端 API 变更而失效。

3. 注册并验证号码：

```bash
signal-cli -a +<BOT_PHONE_NUMBER> register
```

如需图形验证码：

1. 打开 `https://signalcaptchas.org/registration/generate.html`。
2. 完成验证码后，从“打开 Signal”按钮中复制 `signalcaptcha://...` 链接目标。
3. 尽可能在与浏览器会话相同的外部 IP 下执行命令。
4. 立即再次运行注册命令（验证码令牌过期极快）：

```bash
signal-cli -a +<BOT_PHONE_NUMBER> register --captcha '<SIGNALCAPTCHA_URL>'
signal-cli -a +<BOT_PHONE_NUMBER> verify <VERIFICATION_CODE>
```

4. 配置 OpenClaw，重启网关，并验证通道：

```bash
# If you run the gateway as a user systemd service:
systemctl --user restart openclaw-gateway

# Then verify:
openclaw doctor
openclaw channels status --probe
```

5. 配对您的私信发送方：
   - 向机器人号码发送任意消息。
   - 在服务器上批准验证码：`openclaw pairing approve signal <PAIRING_CODE>`。
   - 将机器人号码保存为手机联系人，以避免显示为“未知联系人”。

重要提示：使用 `signal-cli` 注册手机号账户，可能导致该号码在主 Signal 应用中的会话被注销。建议优先选用专用机器人号码；若需保留现有手机应用配置，请改用二维码链接模式。

上游参考文档：

- `signal-cli` README：`https://github.com/AsamK/signal-cli`
- 图形验证码流程：`https://github.com/AsamK/signal-cli/wiki/Registration-with-captcha`
- 链接流程：`https://github.com/AsamK/signal-cli/wiki/Linking-other-devices-(Provisioning)`

## 外部守护进程模式（httpUrl）

若您希望自行管理 `signal-cli`（例如：规避 JVM 冷启动延迟、容器初始化瓶颈或共享 CPU 场景），可单独运行守护进程，并让 OpenClaw 指向该进程：

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

此方式跳过 OpenClaw 内置的自动启动与等待逻辑。若自动启动时启动缓慢，请设置 `channels.signal.startupTimeoutMs`。

## 访问控制（私信 + 群组）

私信（DM）：

- 默认策略：`channels.signal.dmPolicy = "pairing"`。
- 未知发送者将收到配对码；其消息在获准前将被忽略（配对码 1 小时后过期）。
- 配对批准方式：
  - `openclaw pairing list signal`
  - `openclaw pairing approve signal <CODE>`
- 配对是 Signal 私信的默认令牌交换机制。详情参见：[配对](/channels/pairing)
- 来自 `sourceUuid` 的仅 UUID 发送者，将作为 `uuid:<id>` 存储于 `channels.signal.allowFrom` 中。

群组：

- `channels.signal.groupPolicy = open | allowlist | disabled`。
- 当 `allowlist` 已启用时，`channels.signal.groupAllowFrom` 控制谁可在群组中触发操作。
- 运行时说明：若 `channels.signal` 完全缺失，运行时将回退至 `groupPolicy="allowlist"` 进行群组权限检查（即使 `channels.defaults.groupPolicy` 已设置）。

## 工作原理（行为）

- `signal-cli` 以守护进程方式运行；网关通过 SSE 读取事件。
- 入站消息被标准化为统一的通道信封格式。
- 回复始终路由回原始号码或群组。

## 媒体与限制

- 出站文本按长度分块，上限为 `channels.signal.textChunkLimit`（默认 4000 字符）。
- 可选换行分块：设置 `channels.signal.chunkMode="newline"` 后，将在长度分块前按空行（段落边界）进行切分。
- 支持附件（base64 编码内容从 `signal-cli` 获取）。
- 默认媒体数量上限：`channels.signal.mediaMaxMb`（默认 8 个）。
- 使用 `channels.signal.ignoreAttachments` 可跳过媒体下载。
- 群组历史上下文使用 `channels.signal.historyLimit`（或 `channels.signal.accounts.*.historyLimit`），并回退至 `messages.groupChat.historyLimit`。设置 `0` 可禁用该功能（默认值为 50）。

## 输入提示与已读回执

- **输入提示**：OpenClaw 通过 `signal-cli sendTyping` 发送输入信号，并在回复生成过程中持续刷新。
- **已读回执**：当 `channels.signal.sendReadReceipts` 为 true 时，OpenClaw 将为获准的私信转发已读回执。
- signal-cli 不暴露群组的已读回执。

## 表情反应（消息工具）

- 使用 `message action=react` 配合 `channel=signal`。
- 目标对象：发送方 E.164 号码或 UUID（可从配对输出中获取 `uuid:<id>`；裸 UUID 同样有效）。
- `messageId` 是您要添加反应的消息在 Signal 中的时间戳。
- 群组内添加反应需提供 `targetAuthor` 或 `targetAuthorUuid`。

示例：

```
message action=react channel=signal target=uuid:123e4567-e89b-12d3-a456-426614174000 messageId=1737630212345 emoji=🔥
message action=react channel=signal target=+15551234567 messageId=1737630212345 emoji=🔥 remove=true
message action=react channel=signal target=signal:group:<groupId> targetAuthor=uuid:<sender-uuid> messageId=1737630212345 emoji=✅
```

配置项：

- `channels.signal.actions.reactions`：启用/禁用表情反应操作（默认 true）。
- `channels.signal.reactionLevel`：`off | ack | minimal | extensive`。
  - `off`/`ack` 禁用代理表情反应（此时消息工具 `react` 将报错）。
  - `minimal`/`extensive` 启用代理表情反应，并设定引导级别。
- 每账户覆盖配置：`channels.signal.accounts.<id>.actions.reactions`、`channels.signal.accounts.<id>.reactionLevel`。

## 投递目标（CLI / cron）

- 私信（DM）：`signal:+15551234567`（或纯 E.164 号码）。
- UUID 私信：`uuid:<id>`（或裸 UUID）。
- 群组：`signal:group:<groupId>`。
- 用户名：`username:<name>`（若您的 Signal 账户支持）。

## 故障排查

请首先执行以下诊断阶梯：

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

如需确认私信配对状态，请执行：

```bash
openclaw pairing list signal
```

常见失败情形：

- 守护进程可达但无回复：请验证账户/守护进程配置（`httpUrl`、`account`）及接收模式。
- 私信被忽略：发送方尚处于待配对批准状态。
- 群组消息被忽略：群组发送方/提及过滤机制阻止了投递。
- 配置编辑后出现校验错误：请运行 `openclaw doctor --fix`。
- 诊断信息中缺失 Signal：请确认 `channels.signal.enabled: true`。

额外检查项：

用于问题分类流程：[/channels/troubleshooting](/channels/troubleshooting)。

## 安全注意事项

- `signal-cli` 将账户密钥本地存储（通常位于 `~/.local/share/signal-cli/data/`）。
- 在服务器迁移或重建前，请备份 Signal 账户状态。
- 除非您明确希望扩大私信（DM）访问范围，否则请保持 `channels.signal.dmPolicy: "pairing"` 不变。
- 短信（SMS）验证仅在注册或恢复流程中需要；但若失去对手机号/账户的控制，可能使重新注册变得复杂。

## 配置参考（Signal）

完整配置：[Configuration](/gateway/configuration)

提供方选项：

- `channels.signal.enabled`：启用/禁用通道启动。
- `channels.signal.account`：机器人的 E.164 号码。
- `channels.signal.cliPath`：指向 `signal-cli` 的路径。
- `channels.signal.httpUrl`：完整的守护进程（daemon）URL（覆盖 host/port 设置）。
- `channels.signal.httpHost`、`channels.signal.httpPort`：守护进程绑定地址（默认为 127.0.0.1:8080）。
- `channels.signal.autoStart`：自动启动守护进程（若未设置 `httpUrl`，则默认为 true）。
- `channels.signal.startupTimeoutMs`：启动等待超时时间（毫秒），上限为 120000。
- `channels.signal.receiveMode`：`on-start | manual`。
- `channels.signal.ignoreAttachments`：跳过附件下载。
- `channels.signal.ignoreStories`：忽略来自守护进程的故事（stories）。
- `channels.signal.sendReadReceipts`：转发已读回执（read receipts）。
- `channels.signal.dmPolicy`：`pairing | allowlist | open | disabled`（默认值：pairing）。
- `channels.signal.allowFrom`：私信（DM）允许列表（E.164 号码或 `uuid:<id>`）。`open` 需要启用 `"*"`。Signal 不支持用户名；请使用电话号码或 UUID 标识符。
- `channels.signal.groupPolicy`：`open | allowlist | disabled`（默认值：allowlist）。
- `channels.signal.groupAllowFrom`：群组发件人允许列表。
- `channels.signal.historyLimit`：作为上下文包含的最大群组消息数（设为 0 则禁用）。
- `channels.signal.dmHistoryLimit`：私信历史记录限制（以用户轮次计）。每个用户的覆盖设置：`channels.signal.dms["<phone_or_uuid>"].historyLimit`。
- `channels.signal.textChunkLimit`：出站消息分块大小（字符数）。
- `channels.signal.chunkMode`：`length`（默认）或 `newline`（在按长度分块前，按空行切分，即按段落边界切分）。
- `channels.signal.mediaMaxMb`：入站/出站媒体文件大小上限（MB）。

相关全局选项：

- `agents.list[].groupChat.mentionPatterns`（Signal 不支持原生提及功能）。
- `messages.groupChat.mentionPatterns`（全局备用设置）。
- `messages.responsePrefix`。