---
summary: "Matrix support status, capabilities, and configuration"
read_when:
  - Working on Matrix channel features
title: "Matrix"
---
# Matrix（插件）

Matrix 是一种开放、去中心化的消息协议。OpenClaw 以 Matrix **用户**身份连接至任意 homeserver，因此你需要为该机器人准备一个 Matrix 账户。登录成功后，你可以直接向机器人发送私信（DM），或将其邀请至房间（Matrix 中的“群组”）。Beeper 也是一个有效的客户端选项，但要求启用端到端加密（E2EE）。

状态：通过插件（`@vector-im/matrix-bot-sdk`）支持。支持私信、房间、会话线程（threads）、媒体、反应（reactions）、投票（可发送文本形式的 `poll-start` 及发起投票）、位置信息和端到端加密（需启用加密支持）。

## 需要安装插件

Matrix 以插件形式提供，不包含在核心安装包中。

通过 CLI 安装（npm 仓库）：

```bash
openclaw plugins install @openclaw/matrix
```

本地检出（当从 Git 仓库运行时）：

```bash
openclaw plugins install ./extensions/matrix
```

若你在配置/初始设置流程中选择 Matrix，且检测到 Git 检出，OpenClaw 将自动提供本地安装路径。

详情参见：[插件](/tools/plugin)

## 设置步骤

1. 安装 Matrix 插件：
   - 从 npm 安装：`openclaw plugins install @openclaw/matrix`
   - 从本地检出安装：`openclaw plugins install ./extensions/matrix`
2. 在 homeserver 上创建一个 Matrix 账户：
   - 浏览托管选项：[https://matrix.org/ecosystem/hosting/](https://matrix.org/ecosystem/hosting/)
   - 或自行部署。
3. 获取机器人的访问令牌（access token）：
   - 使用 Matrix 登录 API，在你的 homeserver 上调用 `curl`：

   ```bash
   curl --request POST \
     --url https://matrix.example.org/_matrix/client/v3/login \
     --header 'Content-Type: application/json' \
     --data '{
     "type": "m.login.password",
     "identifier": {
       "type": "m.id.user",
       "user": "your-user-name"
     },
     "password": "your-password"
   }'
   ```

   - 将 `matrix.example.org` 替换为你的 homeserver URL。
   - 或设置 `channels.matrix.userId` + `channels.matrix.password`：OpenClaw 将调用相同的登录端点，将访问令牌存入 `~/.openclaw/credentials/matrix/credentials.json`，并在下次启动时复用。

4. 配置凭据：
   - 环境变量：`MATRIX_HOMESERVER`、`MATRIX_ACCESS_TOKEN`（或 `MATRIX_USER_ID` + `MATRIX_PASSWORD`）
   - 或配置文件：`channels.matrix.*`
   - 若两者均设置，以配置文件为准。
   - 使用访问令牌时，用户 ID 将通过 `/whoami` 自动获取。
   - 若手动指定，`channels.matrix.userId` 应为完整的 Matrix ID（例如：`@bot:example.org`）。
5. 重启网关（或完成初始设置流程）。
6. 使用任意 Matrix 客户端（Element、Beeper 等；参见 [https://matrix.org/ecosystem/clients/](https://matrix.org/ecosystem/clients/)）与机器人开启私信，或将其邀请至房间。Beeper 要求启用 E2EE，因此请设置 `channels.matrix.encryption: true` 并验证设备。

最小化配置（仅需访问令牌，用户 ID 自动获取）：

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_***",
      dm: { policy: "pairing" },
    },
  },
}
```

启用端到端加密（E2EE）的配置：

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_***",
      encryption: true,
      dm: { policy: "pairing" },
    },
  },
}
```

## 加密（E2EE）

端到端加密（E2EE）通过 Rust 加密 SDK **受支持**。

使用 `channels.matrix.encryption: true` 启用：

- 若加密模块成功加载，加密房间中的消息将自动解密。
- 向加密房间发送媒体内容时，将自动加密。
- 首次连接时，OpenClaw 将向你的其他会话请求设备验证。
- 请在另一 Matrix 客户端（如 Element 等）中验证该设备，以启用密钥共享。
- 若加密模块无法加载，E2EE 将被禁用，加密房间的消息将无法解密；OpenClaw 将记录一条警告日志。
- 若你看到缺少加密模块的错误（例如：`@matrix-org/matrix-sdk-crypto-nodejs-*`），请允许 `@matrix-org/matrix-sdk-crypto-nodejs` 的构建脚本，并运行 `pnpm rebuild @matrix-org/matrix-sdk-crypto-nodejs`，或通过 `node node_modules/@matrix-org/matrix-sdk-crypto-nodejs/download-lib.js` 获取二进制文件。

加密状态按账户 + 访问令牌分别存储于  
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/crypto/`  
（SQLite 数据库）。同步状态与之共存于 `bot-storage.json`。  
若访问令牌（设备）发生变化，则创建新的存储，并需重新验证机器人，方可继续在加密房间中解密消息。

**设备验证：**  
启用 E2EE 后，机器人将在启动时向你的其他会话发起验证请求。请打开 Element（或其他客户端），批准该验证请求以建立信任关系。验证完成后，机器人即可解密加密房间中的消息。

## 多账户支持

支持多账户：使用 `channels.matrix.accounts`，并为每个账户提供独立凭据及可选的 `name`。共享配置模式参见 [`gateway/configuration`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts)。

每个账户均作为独立的 Matrix 用户连接至任意 homeserver。各账户配置继承自顶层的 `channels.matrix` 设置，并可覆盖任意选项（如私信策略、群组策略、加密设置等）。

```json5
{
  channels: {
    matrix: {
      enabled: true,
      dm: { policy: "pairing" },
      accounts: {
        assistant: {
          name: "Main assistant",
          homeserver: "https://matrix.example.org",
          accessToken: "syt_assistant_***",
          encryption: true,
        },
        alerts: {
          name: "Alerts bot",
          homeserver: "https://matrix.example.org",
          accessToken: "syt_alerts_***",
          dm: { policy: "allowlist", allowFrom: ["@admin:example.org"] },
        },
      },
    },
  },
}
```

注意事项：

- 账户启动过程是串行化的，以避免并发模块导入引发的竞争条件。
- 环境变量（如 `MATRIX_HOMESERVER`、`MATRIX_ACCESS_TOKEN` 等）仅适用于**默认**账户。
- 基础频道设置（如私信策略、群组策略、提及触发限制等）适用于所有账户，除非为特定账户另行覆盖。
- 使用 `bindings[].match.accountId` 可将每个账户路由至不同代理（agent）。
- 加密状态按账户 + 访问令牌分别存储（各账户拥有独立的密钥存储）。

## 路由模型

- 所有回复始终返回至 Matrix。
- 私信共享代理（agent）的主会话；房间则映射至群组会话。

## 访问控制（私信）

- 默认策略：`channels.matrix.dm.policy = "pairing"`。未知发件人将收到配对码（pairing code）。
- 可通过以下方式批准：
  - `openclaw pairing list matrix`
  - `openclaw pairing approve matrix <CODE>`
- 公开私信：启用 `channels.matrix.dm.policy="open"` 并配合 `channels.matrix.dm.allowFrom=["*"]`。
- `channels.matrix.dm.allowFrom` 接受完整的 Matrix 用户 ID（例如：`@user:server`）。向导（wizard）会在目录搜索结果为唯一精确匹配时，将显示名称解析为用户 ID。
- 请勿使用显示名称或裸 localpart（例如：`"Alice"` 或 `"alice"`）。它们具有歧义性，在白名单匹配中将被忽略。请始终使用完整的 `@user:server` ID。

## 房间（群组）

- 默认策略：`channels.matrix.groupPolicy = "allowlist"`（提及触发式）。若未设置，可用 `channels.defaults.groupPolicy` 覆盖默认值。
- 运行时说明：若 `channels.matrix` 完全缺失，运行时将回退至 `groupPolicy="allowlist"` 进行房间检查（即使已设置 `channels.defaults.groupPolicy`）。
- 使用 `channels.matrix.groups` 白名单指定允许的房间（支持房间 ID 或别名；名称将在目录搜索结果为唯一精确匹配时解析为 ID）：

```json5
{
  channels: {
    matrix: {
      groupPolicy: "allowlist",
      groups: {
        "!roomId:example.org": { allow: true },
        "#alias:example.org": { allow: true },
      },
      groupAllowFrom: ["@owner:example.org"],
    },
  },
}
```

- `requireMention: false` 启用该房间内的自动回复。
- `groups."*"` 可跨房间统一设置提及触发的默认行为。
- `groupAllowFrom` 限制可在房间中触发机器人的发件人（须为完整 Matrix 用户 ID）。
- 每个房间的 `users` 白名单可进一步限制特定房间内允许的发件人（须使用完整 Matrix 用户 ID）。
- 配置向导将提示输入房间白名单（支持房间 ID、别名或名称），且仅在名称精确、唯一匹配时进行解析。
- 启动时，OpenClaw 将把白名单中的房间/用户名称解析为 ID 并记录映射关系；无法解析的条目将在白名单匹配中被忽略。
- 默认自动接受邀请；可通过 `channels.matrix.autoJoin` 和 `channels.matrix.autoJoinAllowlist` 控制。
- 若要禁止加入**任何房间**，请设置 `channels.matrix.groupPolicy: "disabled"`（或保持白名单为空）。
- 遗留配置项：`channels.matrix.rooms`（结构与 `groups` 相同）。

## 会话线程（Threads）

- 支持回复线程（reply threading）。
- `channels.matrix.threadReplies` 控制回复是否保留在线程内：
  - `off`、`inbound`（默认）、`always`
- `channels.matrix.replyToMode` 控制非线程内回复时的“回复目标”元数据（reply-to metadata）：
  - `off`（默认）、`first`、`all`

## 功能能力

| 功能             | 状态                                                                                |
| ---------------- | ----------------------------------------------------------------------------------- |
| 直接消息           | ✅ 已支持                                                                           |
| 房间              | ✅ 已支持                                                                           |
| 主题（Threads）    | ✅ 已支持                                                                           |
| 媒体              | ✅ 已支持                                                                           |
| 端到端加密（E2EE）  | ✅ 已支持（需启用 crypto 模块）                                                     |
| 表情反应（Reactions） | ✅ 已支持（可通过工具发送/读取）                                                    |
| 投票（Polls）      | ✅ 支持发送；入站投票启动将被转换为文本（响应与结束事件被忽略）                      |
| 位置信息           | ✅ 已支持（geo URI 格式；海拔信息被忽略）                                            |
| 原生命令           | ✅ 已支持                                                                           |

## 故障排查

请首先运行以下命令序列：

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

如有需要，再确认直接消息（DM）配对状态：

```bash
openclaw pairing list matrix
```

常见故障情形：

- 已登录但房间消息被忽略：该房间被 `groupPolicy` 或房间白名单屏蔽。
- 直接消息被忽略：当 `channels.matrix.dm.policy="pairing"` 时，发信人尚待批准。
- 加密房间失败：加密支持未启用或加密设置不匹配。

有关分类诊断流程，请参阅：[/channels/troubleshooting](/channels/troubleshooting)。

## 配置参考（Matrix）

完整配置说明：[Configuration](/gateway/configuration)

提供商选项：

- `channels.matrix.enabled`：启用/禁用通道启动。
- `channels.matrix.homeserver`：Home Server 地址（URL）。
- `channels.matrix.userId`：Matrix 用户 ID（若提供访问令牌则为可选）。
- `channels.matrix.accessToken`：访问令牌（access token）。
- `channels.matrix.password`：用于登录的密码（令牌将被保存）。
- `channels.matrix.deviceName`：设备显示名称。
- `channels.matrix.encryption`：启用端到端加密（E2EE）（默认值：false）。
- `channels.matrix.initialSyncLimit`：初始同步限制数量。
- `channels.matrix.threadReplies`：`off | inbound | always`（默认值：inbound）。
- `channels.matrix.textChunkLimit`：出站文本分块大小（字符数）。
- `channels.matrix.chunkMode`：`length`（默认）或 `newline`，表示在按长度分块前，先按空行（段落边界）进行切分。
- `channels.matrix.dm.policy`：`pairing | allowlist | open | disabled`（默认值：pairing）。
- `channels.matrix.dm.allowFrom`：直接消息白名单（需填写完整的 Matrix 用户 ID）。`open` 需要启用 `"*"`。向导会在可能的情况下将用户名解析为对应 ID。
- `channels.matrix.groupPolicy`：`allowlist | open | disabled`（默认值：allowlist）。
- `channels.matrix.groupAllowFrom`：群组消息的白名单发送者（需填写完整的 Matrix 用户 ID）。
- `channels.matrix.allowlistOnly`：强制对直接消息和房间应用白名单规则。
- `channels.matrix.groups`：群组白名单及各房间独立设置的映射表。
- `channels.matrix.rooms`：旧版群组白名单/配置。
- `channels.matrix.replyToMode`：线程/标签的回复目标模式（reply-to mode）。
- `channels.matrix.mediaMaxMb`：入站/出站媒体容量上限（MB）。
- `channels.matrix.autoJoin`：邀请处理方式（`always | allowlist | off`，默认值：always）。
- `channels.matrix.autoJoinAllowlist`：允许自动加入的房间 ID 或别名列表。
- `channels.matrix.accounts`：以账户 ID 为键的多账户配置（每个账户继承顶层配置）。
- `channels.matrix.actions`：按操作类型进行的工具访问控制（reactions/messages/pins/memberInfo/channelInfo）。