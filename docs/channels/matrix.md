---
summary: "Matrix support status, capabilities, and configuration"
read_when:
  - Working on Matrix channel features
title: "Matrix"
---
# Matrix (插件)

Matrix 是一个开放、去中心化的消息传递协议。OpenClaw 以 Matrix **用户**的身份连接到任何 homeserver，因此你需要一个 Matrix 账户用于机器人。一旦登录，你可以直接与机器人发送私信或邀请它加入房间（Matrix “群组”）。Beeper 也是一个有效的客户端选项，但它需要启用 E2EE。

状态：通过插件支持 (@vector-im/matrix-bot-sdk)。直接消息、房间、线程、媒体、反应、投票（以文本形式发送 + poll-start）、位置和 E2EE（带有加密支持）。

## 需要插件

Matrix 作为插件提供，不包含在核心安装中。

通过 CLI 安装（npm 仓库）：

```bash
openclaw plugins install @openclaw/matrix
```

本地检出（当从 git 仓库运行时）：

```bash
openclaw plugins install ./extensions/matrix
```

如果你在配置/引导过程中选择 Matrix 并检测到 git 检出，
OpenClaw 将自动提供本地安装路径。

详情：[插件](/tools/plugin)

## 设置

1. 安装 Matrix 插件：
   - 从 npm: `openclaw plugins install @openclaw/matrix`
   - 从本地检出: `openclaw plugins install ./extensions/matrix`
2. 在 homeserver 上创建一个 Matrix 账户：
   - 浏览托管选项 [https://matrix.org/ecosystem/hosting/](https://matrix.org/ecosystem/hosting/)
   - 或者自己托管。
3. 获取机器人的访问令牌：
   - 使用 Matrix 登录 API 和 `curl` 在你的 homeserver 上：

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
   - 或设置 `channels.matrix.userId` + `channels.matrix.password`: OpenClaw 调用相同的
     登录端点，将访问令牌存储在 `~/.openclaw/credentials/matrix/credentials.json` 中，
     并在下次启动时重用。

4. 配置凭据：
   - 环境变量: `MATRIX_HOMESERVER`, `MATRIX_ACCESS_TOKEN` (或 `MATRIX_USER_ID` + `MATRIX_PASSWORD`)
   - 或配置文件: `channels.matrix.*`
   - 如果两者都设置，配置文件优先。
   - 使用访问令牌：用户 ID 会通过 `/whoami` 自动获取。
   - 设置后，`channels.matrix.userId` 应该是完整的 Matrix ID（示例：`@bot:example.org`）。
5. 重启网关（或完成引导）。
6. 从任何 Matrix 客户端（Element, Beeper 等；参见 [https://matrix.org/ecosystem/clients/](https://matrix.org/ecosystem/clients/)）开始与机器人发送私信或邀请它加入房间。Beeper 需要 E2EE，
   因此设置 `channels.matrix.encryption: true` 并验证设备。

最小配置（访问令牌，用户 ID 自动获取）：

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

E2EE 配置（启用端到端加密）：

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

通过 Rust crypto SDK 支持端到端加密。

使用 `channels.matrix.encryption: true` 启用：

- 如果加载了加密模块，则会自动解密加密房间。
- 发送至加密房间的媒体数据会被加密。
- 在首次连接时，OpenClaw 会请求从您的其他会话验证设备。
- 在另一个 Matrix 客户端（如 Element 等）中验证设备以启用密钥共享。
- 如果无法加载加密模块，则禁用 E2EE 并且加密房间将无法解密；
  OpenClaw 会记录警告。
- 如果您看到缺少加密模块的错误（例如，`@matrix-org/matrix-sdk-crypto-nodejs-*`），
  允许 `@matrix-org/matrix-sdk-crypto-nodejs` 的构建脚本并运行
  `pnpm rebuild @matrix-org/matrix-sdk-crypto-nodejs` 或使用
  `node node_modules/@matrix-org/matrix-sdk-crypto-nodejs/download-lib.js` 获取二进制文件。

加密状态存储在每个账户 + 访问令牌的
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/crypto/`
（SQLite 数据库）中。同步状态与其并存于 `bot-storage.json`。
如果访问令牌（设备）更改，则会创建一个新的存储，并且机器人必须
重新验证以解密加密房间的消息。

**设备验证：**
当启用 E2EE 时，机器人会在启动时请求从您的其他会话进行验证。
打开 Element（或其他客户端）并批准验证请求以建立信任。
一旦验证完成，机器人可以解密加密房间中的消息。

## 多账户

多账户支持：使用 `channels.matrix.accounts` 和每个账户的凭据以及可选的 `name`。参见 [`gateway/configuration`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 了解共享模式。

每个账户在任何 homeserver 上作为单独的 Matrix 用户运行。每个账户的配置
继承自顶级 `channels.matrix` 设置，并且可以覆盖任何选项
（DM 策略、群组、加密等）。

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

- 账户启动是串行化的，以避免与并发模块导入的竞争条件。
- 环境变量 (`MATRIX_HOMESERVER`, `MATRIX_ACCESS_TOKEN` 等) 仅适用于 **默认** 账户。
- 基础频道设置（DM 策略、群组策略、提及门控等）适用于所有账户，除非每个账户单独覆盖。
- 使用 `bindings[].match.accountId` 将每个账户路由到不同的代理。
- 加密状态按账户 + 访问令牌存储（每个账户单独的密钥库）。

## 路由模型

- 回复总是返回到 Matrix。
- DM 共享代理的主要会话；房间映射到群组会话。

## 访问控制（DM）

- 默认：`channels.matrix.dm.policy = "pairing"`。未知发送者会收到配对码。
- 通过以下方式批准：
  - `openclaw pairing list matrix`
  - `openclaw pairing approve matrix <CODE>`
- 公共 DM：`channels.matrix.dm.policy="open"` 加上 `channels.matrix.dm.allowFrom=["*"]`。
- `channels.matrix.dm.allowFrom` 接受完整的 Matrix 用户 ID（示例：`@user:server`）。向导在目录搜索找到单个精确匹配时将显示名称解析为用户 ID。
- 不要使用显示名称或裸本地部分（示例：`"Alice"` 或 `"alice"`）。它们是模糊的，并且在白名单匹配中会被忽略。使用完整的 `@user:server` ID。

## 房间（群组）

- 默认：`channels.matrix.groupPolicy = "allowlist"`（提及门控）。使用 `channels.defaults.groupPolicy` 在未设置时覆盖默认值。
- 使用 `channels.matrix.groups` 白名单房间（房间 ID 或别名；当目录搜索找到单个精确匹配时，名称会被解析为 ID）：

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
- `groups."*"` 可以为多个房间设置提及门控的默认值。
- `groupAllowFrom` 限制哪些发送者可以在房间中触发机器人（完整的 Matrix 用户 ID）。
- 每个房间的 `users` 白名单可以进一步限制特定房间中的发送者（使用完整的 Matrix 用户 ID）。
- 配置向导提示输入房间白名单（房间 ID、别名或名称），并且仅在精确唯一匹配时解析名称。
- 启动时，OpenClaw 将允许名单中的房间/用户名称解析为 ID 并记录映射；无法解析的条目在白名单匹配中被忽略。
- 邀请默认自动加入；使用 `channels.matrix.autoJoin` 和 `channels.matrix.autoJoinAllowlist` 进行控制。
- 要允许 **没有房间**，设置 `channels.matrix.groupPolicy: "disabled"`（或保持空白名单）。
- 旧版密钥：`channels.matrix.rooms`（与 `groups` 形状相同）。

## 线程

- 支持回复线程。
- `channels.matrix.threadReplies` 控制回复是否保留在线程中：
  - `off`, `inbound`（默认），`always`
- `channels.matrix.replyToMode` 控制不在线程中回复时的回复元数据：
  - `off`（默认），`first`, `all`

## 功能

| 特性          | 状态                                                                                |
| --------------- | ------------------------------------------------------------------------------------- |
| 直接消息      | ✅ 支持                                                                          |
| 房间          | ✅ 支持                                                                          |
| 线程          | ✅ 支持                                                                          |
| 媒体          | ✅ 支持                                                                          |
| 端到端加密    | ✅ 支持（需要加密模块）                                                 |
| 表情符号      | ✅ 支持（通过工具发送/读取）                                                    |
| 投票          | ✅ 支持发送；传入投票开始会被转换为文本（忽略响应/结束） |
| 位置          | ✅ 支持（geo URI；忽略海拔）                                              |
| 原生命令      | ✅ 支持                                                                          |

## 故障排除

首先运行这个梯子：

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

然后如果需要，确认直接消息配对状态：

```bash
openclaw pairing list matrix
```

常见故障：

- 登录但房间消息被忽略：房间被 `groupPolicy` 阻塞或在房间白名单中。
- 直接消息被忽略：当 `channels.matrix.dm.policy="pairing"` 时，发送者待批准。
- 加密房间失败：加密支持或加密设置不匹配。

用于排查流程：[/channels/troubleshooting](/channels/troubleshooting)。

## 配置参考（Matrix）

完整配置：[Configuration](/gateway/configuration)

提供商选项：

- `channels.matrix.enabled`: 启用/禁用频道启动。
- `channels.matrix.homeserver`: 主服务器URL。
- `channels.matrix.userId`: Matrix用户ID（可选，与访问令牌一起使用）。
- `channels.matrix.accessToken`: 访问令牌。
- `channels.matrix.password`: 登录密码（令牌已存储）。
- `channels.matrix.deviceName`: 设备显示名称。
- `channels.matrix.encryption`: 启用E2EE（默认：false）。
- `channels.matrix.initialSyncLimit`: 初始同步限制。
- `channels.matrix.threadReplies`: `off | inbound | always`（默认：inbound）。
- `channels.matrix.textChunkLimit`: 出站文本块大小（字符数）。
- `channels.matrix.chunkMode`: `length`（默认）或`newline`在长度分块之前按空白行（段落边界）拆分。
- `channels.matrix.dm.policy`: `pairing | allowlist | open | disabled`（默认：pairing）。
- `channels.matrix.dm.allowFrom`: DM白名单（完整的Matrix用户ID）。`open`需要`"*"`。向导会在可能的情况下将名称解析为ID。
- `channels.matrix.groupPolicy`: `allowlist | open | disabled`（默认：allowlist）。
- `channels.matrix.groupAllowFrom`: 群组消息的白名单发送者（完整的Matrix用户ID）。
- `channels.matrix.allowlistOnly`: 强制DM和房间的白名单规则。
- `channels.matrix.groups`: 群组白名单+每个房间的设置映射。
- `channels.matrix.rooms`: 旧版群组白名单/配置。
- `channels.matrix.replyToMode`: 线程/标签的回复模式。
- `channels.matrix.mediaMaxMb`: 入站/出站媒体限制（MB）。
- `channels.matrix.autoJoin`: 邀请处理（`always | allowlist | off`，默认：always）。
- `channels.matrix.autoJoinAllowlist`: 自动加入的允许房间ID/别名。
- `channels.matrix.accounts`: 按账户ID键入的多账户配置（每个账户继承顶级设置）。
- `channels.matrix.actions`: 按操作的工具门控（反应/消息/固定/成员信息/频道信息）。