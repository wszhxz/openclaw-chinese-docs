---
summary: "Matrix support status, capabilities, and configuration"
read_when:
  - Working on Matrix channel features
title: "Matrix"
---
# Matrix (插件)

Matrix 是一个开放的、去中心化的消息传递协议。OpenClaw 在任何 homeserver 上作为 Matrix **用户** 连接，因此你需要为机器人创建一个 Matrix 账户。登录之后，你可以直接 DM 机器人或邀请它加入房间（Matrix“群组”）。Beeper 也是一个有效的客户端选项，但它需要启用 E2EE。

状态：通过插件支持 (@vector-im/matrix-bot-sdk)。私信、房间、线程、媒体、反应、投票（send + poll-start 作为文本）、位置以及 E2EE（带 crypto 支持）。

## 需要插件

Matrix 以插件形式发布，未捆绑在核心安装中。

通过 CLI 安装（npm registry）：

```bash
openclaw plugins install @openclaw/matrix
```

本地检出（当从 git 仓库运行时）：

```bash
openclaw plugins install ./extensions/matrix
```

如果你在配置/入门过程中选择 Matrix 并检测到 git checkout，
OpenClaw 将自动提供本地安装路径。

详情：[插件](/tools/plugin)

## 设置

1. 安装 Matrix 插件：
   - 从 npm：`openclaw plugins install @openclaw/matrix`
   - 从本地检出：`openclaw plugins install ./extensions/matrix`
2. 在 homeserver 上创建 Matrix 账户：
   - 浏览托管选项：[https://matrix.org/ecosystem/hosting/](https://matrix.org/ecosystem/hosting/)
   - 或者自己托管。
3. 获取机器人的 access token：
   - 在你的 homeserver 上使用 Matrix 登录 API 配合 `curl`：

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
   - 或者设置 `channels.matrix.userId` + `channels.matrix.password`：OpenClaw 调用相同的登录端点，将 access token 存储在 `~/.openclaw/credentials/matrix/credentials.json`，
     并在下次启动时重用。

4. 配置凭据：
   - 环境变量：`MATRIX_HOMESERVER`, `MATRIX_ACCESS_TOKEN`（或 `MATRIX_USER_ID` + `MATRIX_PASSWORD`）
   - 或者配置文件：`channels.matrix.*`
   - 如果两者都设置了，配置文件优先。
   - 使用 access token：user ID 将通过 `/whoami` 自动获取。
   - 当设置时，`channels.matrix.userId` 应该是完整的 Matrix ID（示例：`@bot:example.org`）。
5. 重启网关（或完成入门流程）。
6. 与机器人开始 DM 或从任何 Matrix 客户端邀请它加入房间
   （Element、Beeper 等；参见 [https://matrix.org/ecosystem/clients/](https://matrix.org/ecosystem/clients/)）。Beeper 需要 E2EE，
   所以设置 `channels.matrix.encryption: true` 并验证设备。

最小配置（access token，user ID 自动获取）：

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

E2EE 配置（端到端加密启用）：

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

## 加密 (E2EE)

端到端加密通过 Rust crypto SDK **支持**。

使用 `channels.matrix.encryption: true` 启用：

- 如果 crypto 模块加载成功，加密的房间会自动解密。
- 向加密房间发送时，出站媒体会被加密。
- 首次连接时，OpenClaw 会请求来自你其他会话的设备验证。
- 在另一个 Matrix 客户端（Element 等）中验证设备以启用密钥共享。
- 如果无法加载 crypto 模块，E2EE 将被禁用，加密的房间将无法解密；
  OpenClaw 会记录警告。
- 如果你看到缺失 crypto 模块的错误（例如，`@matrix-org/matrix-sdk-crypto-nodejs-*`），允许 `@matrix-org/matrix-sdk-crypto-nodejs` 的构建脚本并运行
  `pnpm rebuild @matrix-org/matrix-sdk-crypto-nodejs` 或使用 `node node_modules/@matrix-org/matrix-sdk-crypto-nodejs/download-lib.js` 获取二进制文件。

加密状态按账户 + access token 存储在
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/crypto/`
（SQLite 数据库）中。同步状态与其一起存储在 `bot-storage.json` 中。
如果 access token（设备）更改，将创建新存储，并且必须重新验证机器人以用于加密房间。

**设备验证：**
当启用 E2EE 时，机器人将在启动时请求来自你其他会话的验证。
打开 Element（或另一个客户端）并批准验证请求以建立信任。
验证后，机器人可以解密加密房间中的消息。

## 多账户

多账户支持：使用 `channels.matrix.accounts` 配合每个账户的凭据和可选的 `name`。有关共享模式，请参见 [`gateway/configuration`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts)。

每个账户在任何 homeserver 上作为独立的 Matrix 用户运行。每个账户的配置继承自顶层 `channels.matrix` 设置，并可以覆盖任何选项（DM 策略、群组、加密等）。

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

注意：

- 账户启动是序列化的，以避免并发模块导入时的竞态条件。
- 环境变量（`MATRIX_HOMESERVER`, `MATRIX_ACCESS_TOKEN` 等）仅适用于 **默认** 账户。
- 基础频道设置（DM 策略、群组策略、提及门控等）适用于所有账户，除非按账户覆盖。
- 使用 `bindings[].match.accountId` 将每个账户路由到不同的 agent。
- 加密状态按账户 + access token 存储（每个账户有单独的密钥存储）。

## 路由模型

- 回复总是返回到 Matrix。
- DM 共享 agent 的主会话；房间映射到群组会话。

## 访问控制 (DMs)

- 默认：`channels.matrix.dm.policy = "pairing"`。未知发件人获得配对码。
- 通过以下方式批准：
  - `openclaw pairing list matrix`
  - `openclaw pairing approve matrix <CODE>`
- 公开 DM：`channels.matrix.dm.policy="open"` 加上 `channels.matrix.dm.allowFrom=["*"]`。
- `channels.matrix.dm.allowFrom` 接受完整的 Matrix user ID（示例：`@user:server`）。当目录搜索找到单个精确匹配时，向导会将 display names 解析为 user IDs。
- 不要使用 display names 或裸 localparts（示例：`"Alice"` 或 `"alice"`）。它们具有歧义性，在 allowlist 匹配中被忽略。使用完整的 `@user:server` ID。

## 房间 (群组)

- 默认：`channels.matrix.groupPolicy = "allowlist"`（mention-gated）。当未设置时，使用 `channels.defaults.groupPolicy` 覆盖默认值。
- 运行时注意：如果 `channels.matrix` 完全缺失，运行时回退到 `groupPolicy="allowlist"` 进行房间检查（即使 `channels.defaults.groupPolicy` 已设置）。
- 使用 `channels.matrix.groups` 允许房间（room IDs 或 aliases；当目录搜索找到单个精确匹配时，名称被解析为 IDs）：

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

- `requireMention: false` 在该房间启用自动回复。
- `groups."*"` 可以设置跨房间的 mention gating 默认值。
- `groupAllowFrom` 限制哪些发件人可以在房间中触发机器人（完整 Matrix user IDs）。
- 每个房间的 `users` allowlists 可以进一步限制特定房间内的发件人（使用完整 Matrix user IDs）。
- 配置向导提示输入房间 allowlists（room IDs, aliases, 或 names），并且仅在精确唯一匹配时解析名称。
- 启动时，OpenClaw 将 allowlists 中的房间/用户名称解析为 IDs 并记录映射；未解析的条目在 allowlist 匹配中被忽略。
- 邀请默认自动加入；使用 `channels.matrix.autoJoin` 和 `channels.matrix.autoJoinAllowlist` 控制。
- 若要允许 **无房间**，设置 `channels.matrix.groupPolicy: "disabled"`（或保留空 allowlist）。
- 旧键：`channels.matrix.rooms`（与 `groups` 形状相同）。

## 线程

- 支持回复线程。
- `channels.matrix.threadReplies` 控制回复是否保持在线程中：
  - `off`, `inbound`（默认）, `always`
- `channels.matrix.replyToMode` 控制不在线程中回复时的回复元数据：
  - `off`（默认）, `first`, `all`

## 功能

| 功能         | 状态                                                                                |
| ------------ | ----------------------------------------------------------------------------------- |
| 直接消息     | ✅ 支持                                                                             |
| 房间         | ✅ 支持                                                                             |
| 线程         | ✅ 支持                                                                             |
| 媒体         | ✅ 支持                                                                             |
| E2EE         | ✅ 支持（需要加密模块）                                                             |
| 反应         | ✅ 支持（通过工具发送/读取）                                                        |
| 投票         | ✅ 支持发送；传入的投票开始转换为文本（响应/结束被忽略）                            |
| 位置         | ✅ 支持（Geo URI；忽略海拔）                                                        |
| 原生命令     | ✅ 支持                                                                             |

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
openclaw pairing list matrix
```

常见故障：

- 已登录但房间消息被忽略：房间被 `groupPolicy` 或房间白名单阻止。
- 私信被忽略：当 `channels.matrix.dm.policy="pairing"` 时，发件人待批准。
- 加密房间失败：加密支持或加密设置不匹配。

对于排查流程：[/channels/troubleshooting](/channels/troubleshooting)。

## 配置参考 (Matrix)

完整配置：[配置](/gateway/configuration)

提供程序选项：

- `channels.matrix.enabled`: 启用/禁用频道启动。
- `channels.matrix.homeserver`: 主服务器 URL。
- `channels.matrix.userId`: Matrix 用户 ID（使用访问令牌时为可选）。
- `channels.matrix.accessToken`: 访问令牌。
- `channels.matrix.password`: 登录密码（存储令牌）。
- `channels.matrix.deviceName`: 设备显示名称。
- `channels.matrix.encryption`: 启用 E2EE（默认值：false）。
- `channels.matrix.initialSyncLimit`: 初始同步限制。
- `channels.matrix.threadReplies`: `off | inbound | always`（默认值：传入）。
- `channels.matrix.textChunkLimit`: 出站文本块大小（字符数）。
- `channels.matrix.chunkMode`: `length`（默认值）或 `newline` 以在空行处拆分（段落边界），然后再进行长度分块。
- `channels.matrix.dm.policy`: `pairing | allowlist | open | disabled`（默认值：配对）。
- `channels.matrix.dm.allowFrom`: 私信白名单（完整的 Matrix 用户 ID）。`open` 需要 `"*"`。向导在可能时将名称解析为 ID。
- `channels.matrix.groupPolicy`: `allowlist | open | disabled`（默认值：白名单）。
- `channels.matrix.groupAllowFrom`: 群消息的白名单发件人（完整的 Matrix 用户 ID）。
- `channels.matrix.allowlistOnly`: 强制对私信和房间应用白名单规则。
- `channels.matrix.groups`: 群组白名单 + 每房间设置映射。
- `channels.matrix.rooms`: 旧版群组白名单/配置。
- `channels.matrix.replyToMode`: 线程/标签的回复模式。
- `channels.matrix.mediaMaxMb`: 传入/传出媒体上限（MB）。
- `channels.matrix.autoJoin`: 邀请处理（`always | allowlist | off`，默认值：始终）。
- `channels.matrix.autoJoinAllowlist`: 允许自动加入的房间 ID/别名。
- `channels.matrix.accounts`: 按账户 ID 键控的多账户配置（每个账户继承顶层设置）。
- `channels.matrix.actions`: 按操作的工具门控（反应/消息/置顶/成员信息/频道信息）。