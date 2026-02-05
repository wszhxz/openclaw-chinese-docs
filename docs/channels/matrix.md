---
summary: "Matrix support status, capabilities, and configuration"
read_when:
  - Working on Matrix channel features
title: "Matrix"
---
# Matrix (插件)

Matrix 是一个开放、去中心化的消息传递协议。OpenClaw 以 Matrix **用户**的身份连接到任何 homeserver，因此您需要一个 Matrix 账户用于机器人。一旦登录，您可以直接向机器人发送私信或邀请它加入房间（Matrix“群组”）。Beeper 也是一个有效的客户端选项，但它需要启用 E2EE。

状态：通过插件支持 (@vector-im/matrix-bot-sdk)。支持直接消息、房间、线程、媒体、反应、投票（以文本形式发送 + poll-start）、位置和 E2EE（带有加密支持）。

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

如果您在配置/引导过程中选择 Matrix 并检测到 git 检出，
OpenClaw 将自动提供本地安装路径。

详情：[插件](/plugin)

## 设置

1. 安装 Matrix 插件：
   - 从 npm: `openclaw plugins install @openclaw/matrix`
   - 从本地检出: `openclaw plugins install ./extensions/matrix`
2. 在 homeserver 上创建一个 Matrix 账户：
   - 浏览托管选项 [https://matrix.org/ecosystem/hosting/](https://matrix.org/ecosystem/hosting/)
   - 或者自行托管。
3. 获取机器人的访问令牌：
   - 使用 Matrix 登录 API 在您的 homeserver 上使用 `curl`:

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

   - 将 `matrix.example.org` 替换为您的 homeserver URL。
   - 或设置 `channels.matrix.userId` + `channels.matrix.password`: OpenClaw 调用相同的
     登录端点，将访问令牌存储在 `~/.openclaw/credentials/matrix/credentials.json` 中，
     并在下次启动时重用。

4. 配置凭据：
   - 环境变量: `MATRIX_HOMESERVER`, `MATRIX_ACCESS_TOKEN` (或 `MATRIX_USER_ID` + `MATRIX_PASSWORD`)
   - 或配置文件: `channels.matrix.*`
   - 如果两者都已设置，则配置文件优先。
   - 使用访问令牌：用户 ID 会通过 `/whoami` 自动获取。
   - 设置后，`channels.matrix.userId` 应该是完整的 Matrix ID（示例：`@bot:example.org`）。
5. 重启网关（或完成引导）。
6. 向机器人发送私信或从任何 Matrix 客户端（Element、Beeper 等；参见 https://matrix.org/ecosystem/clients/）邀请它加入房间。Beeper 需要 E2EE，
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

端到端加密配置（启用端到端加密）：

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
- 发送至加密房间时，外发媒体会被加密。
- 首次连接时，OpenClaw 会从您的其他会话请求设备验证。
- 在另一个 Matrix 客户端（Element 等）中验证设备以启用密钥共享。
- 如果无法加载加密模块，则禁用 E2EE 并且加密房间将无法解密；
  OpenClaw 会记录警告日志。
- 如果您看到缺少加密模块的错误（例如，`@matrix-org/matrix-sdk-crypto-nodejs-*`），
  允许 `@matrix-org/matrix-sdk-crypto-nodejs` 的构建脚本并运行
  `pnpm rebuild @matrix-org/matrix-sdk-crypto-nodejs` 或使用
  `node node_modules/@matrix-org/matrix-sdk-crypto-nodejs/download-lib.js` 获取二进制文件。

加密状态存储在每个账户 + 访问令牌的
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/crypto/`
（SQLite 数据库）中。同步状态与其并存于 `bot-storage.json`。
如果访问令牌（设备）更改，将创建一个新的存储，并且必须重新验证机器人以解密加密房间。

**设备验证：**
当启用 E2EE 时，机器人会在启动时请求来自您其他会话的验证。
打开 Element（或其他客户端）并批准验证请求以建立信任。
一旦验证完成，机器人可以解密加密房间中的消息。

## 路由模型

- 回复总是返回到 Matrix。
- 私信共享代理的主要会话；房间映射到组会话。

## 访问控制（私信）

- 默认：`channels.matrix.dm.policy = "pairing"`。未知发送者会收到配对码。
- 通过以下方式批准：
  - `openclaw pairing list matrix`
  - `openclaw pairing approve matrix <CODE>`
- 公共私信：`channels.matrix.dm.policy="open"` 加上 `channels.matrix.dm.allowFrom=["*"]`。
- `channels.matrix.dm.allowFrom` 接受完整的 Matrix 用户 ID（示例：`@user:server`）。向导会在目录搜索找到单个精确匹配时将显示名称解析为用户 ID。

## 房间（组）

- 默认：`channels.matrix.groupPolicy = "allowlist"`（提及门控）。使用 `channels.defaults.groupPolicy` 覆盖未设置时的默认值。
- 使用 `channels.matrix.groups` 允许列表房间（房间 ID 或别名；当目录搜索找到单个精确匹配时，名称会解析为 ID）：

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

- `requireMention: false` 在该房间中启用自动回复。
- `groups."*"` 可以设置跨房间提及门控的默认值。
- `groupAllowFrom` 限制哪些发送者可以在房间中触发机器人（完整的Matrix用户ID）。
- 每个房间的 `users` 允许列表可以进一步限制特定房间中的发送者（使用完整的Matrix用户ID）。
- 配置向导会提示输入房间允许列表（房间ID、别名或名称），并且仅在精确唯一匹配时解析名称。
- 启动时，OpenClaw 将允许列表中的房间/用户名解析为ID并记录映射；无法解析的条目将被忽略以进行允许列表匹配。
- 邀请默认自动加入；使用 `channels.matrix.autoJoin` 和 `channels.matrix.autoJoinAllowlist` 进行控制。
- 要允许**没有房间**，设置 `channels.matrix.groupPolicy: "disabled"`（或保持空的允许列表）。
- 旧密钥：`channels.matrix.rooms`（与 `groups` 形状相同）。

## 线程

- 支持回复线程。
- `channels.matrix.threadReplies` 控制回复是否保留在线程中：
  - `off`，`inbound`（默认），`always`
- `channels.matrix.replyToMode` 控制不在线程中回复时的回复元数据：
  - `off`（默认），`first`，`all`

## 功能

| 功能         | 状态                                                                                |
| --------------- | ------------------------------------------------------------------------------------- |
| 直接消息 | ✅ 支持                                                                          |
| 房间           | ✅ 支持                                                                          |
| 线程         | ✅ 支持                                                                          |
| 媒体           | ✅ 支持                                                                          |
| 端到端加密            | ✅ 支持（需要加密模块）                                                 |
| 反应       | ✅ 支持（通过工具发送/读取）                                                    |
| 投票           | ✅ 支持发送；传入投票开始会被转换为文本（忽略响应/结束） |
| 位置        | ✅ 支持（geo URI；忽略海拔）                                              |
| 本机命令 | ✅ 支持                                                                          |

## 配置参考（Matrix）

完整配置：[Configuration](/gateway/configuration)

提供商选项：

- `channels.matrix.enabled`: 启用/禁用频道启动。
- `channels.matrix.homeserver`: 主服务器URL。
- `channels.matrix.userId`: Matrix用户ID（可选，需访问令牌）。
- `channels.matrix.accessToken`: 访问令牌。
- `channels.matrix.password`: 登录密码（令牌已存储）。
- `channels.matrix.deviceName`: 设备显示名称。
- `channels.matrix.encryption`: 启用E2EE（默认：false）。
- `channels.matrix.initialSyncLimit`: 初始同步限制。
- `channels.matrix.threadReplies`: `off | inbound | always`（默认：inbound）。
- `channels.matrix.textChunkLimit`: 出站文本块大小（字符数）。
- `channels.matrix.chunkMode`: `length`（默认）或`newline`以在长度分块之前按空白行（段落边界）拆分。
- `channels.matrix.dm.policy`: `pairing | allowlist | open | disabled`（默认：pairing）。
- `channels.matrix.dm.allowFrom`: DM白名单（完整的Matrix用户ID）。`open`需要`"*"`。向导会在可能的情况下将名称解析为ID。
- `channels.matrix.groupPolicy`: `allowlist | open | disabled`（默认：allowlist）。
- `channels.matrix.groupAllowFrom`: 群组消息的白名单发送者（完整的Matrix用户ID）。
- `channels.matrix.allowlistOnly`: 强制DM和房间应用白名单规则。
- `channels.matrix.groups`: 群组白名单+每个房间设置映射。
- `channels.matrix.rooms`: 旧版群组白名单/配置。
- `channels.matrix.replyToMode`: 线程/标签的回复模式。
- `channels.matrix.mediaMaxMb`: 入站/出站媒体限制（MB）。
- `channels.matrix.autoJoin`: 邀请处理（`always | allowlist | off`，默认：always）。
- `channels.matrix.autoJoinAllowlist`: 自动加入的允许房间ID/别名。
- `channels.matrix.actions`: 按操作工具门控（反应/消息/固定/成员信息/频道信息）。