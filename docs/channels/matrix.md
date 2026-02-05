---
summary: "Matrix support status, capabilities, and configuration"
read_when:
  - Working on Matrix channel features
title: "Matrix"
---
# Matrix (插件)

Matrix 是一个开放、去中心化的消息传递协议。OpenClaw 以 Matrix **用户**的身份连接到任何 homeserver，因此您需要一个 Matrix 账户用于机器人。一旦登录，您可以直接向机器人发送私信或邀请它加入房间（Matrix“群组”）。Beeper 也是一个有效的客户端选项，但它需要启用端到端加密（E2EE）。

状态：通过插件支持 (@vector-im/matrix-bot-sdk)。直接消息、房间、线程、媒体、反应、投票（发送 + 投票开始作为文本）、位置和 E2EE（带有加密支持）。

## 需要插件

Matrix 作为一个插件提供，不包含在核心安装中。

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
   - 或者自己托管。
3. 获取机器人的访问令牌：
   - 使用 Matrix 登录 API 在您的 homeserver 上使用 `curl`：

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
   - 如果两者都设置，配置文件优先。
   - 使用访问令牌：用户 ID 会通过 `/whoami` 自动获取。
   - 设置后，`channels.matrix.userId` 应该是完整的 Matrix ID（示例：`@bot:example.org`）。
5. 重启网关（或完成引导）。
6. 向机器人发送私信或从任何 Matrix 客户端（Element, Beeper 等；参见 https://matrix.org/ecosystem/clients/）邀请它加入房间。Beeper 需要 E2EE，
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

端到端加密通过 Rust 加密 SDK **支持**。

启用 `channels.matrix.encryption: true`：

- 如果加载了加密模块，加密房间会自动解密。
- 发送到加密房间的传出媒体会被加密。
- 首次连接时，OpenClaw 会请求其他会话验证设备。
- 在另一个 Matrix 客户端（Element 等）中验证设备以启用密钥共享。
- 如果无法加载加密模块，E2EE 将被禁用且加密房间不会解密；
  OpenClaw 会记录警告。
- 如果看到缺少加密模块错误（例如，`@matrix-org/matrix-sdk-crypto-nodejs-*`），
  允许 `@matrix-org/matrix-sdk-crypto-nodejs` 的构建脚本并运行
  `pnpm rebuild @matrix-org/matrix-sdk-crypto-nodejs` 或获取二进制文件
  `node node_modules/@matrix-org/matrix-sdk-crypto-nodejs/download-lib.js`。

加密状态按账户 + 访问令牌存储在
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/crypto/`
（SQLite 数据库）。同步状态与其相邻存储在 `bot-storage.json`。
如果访问令牌（设备）更改，会创建一个新的存储，并且机器人必须
重新验证以解密加密房间。

**设备验证：**
当启用 E2EE 时，机器人会在启动时请求其他会话验证。
打开 Element（或其他客户端）并批准验证请求以建立信任。
一旦验证，机器人可以解密加密房间中的消息。

## 路由模型

- 回复总是返回到 Matrix。
- 私信共享代理的主要会话；房间映射到群组会话。

## 访问控制（私信）

- 默认：`channels.matrix.dm.policy = "pairing"`。未知发件人会收到配对码。
- 通过以下方式批准：
  - `openclaw pairing list matrix`
  - `openclaw pairing approve matrix <CODE>`
- 公共私信：`channels.matrix.dm.policy="open"` 加上 `channels.matrix.dm.allowFrom=["*"]`。
- `channels.matrix.dm.allowFrom` 接受用户 ID 或显示名称。向导在目录搜索可用时将显示名称解析为用户 ID。

## 房间（群组）

- 默认：`channels.matrix.groupPolicy = "allowlist"`（提及门控）。使用 `channels.defaults.groupPolicy` 覆盖默认值（如果未设置）。
- 使用 `channels.matrix.groups` 允许列表房间（房间 ID、别名或名称）：

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

- `requireMention: false` 启用该房间的自动回复。
- `groups."*"` 可以跨房间设置提及门控的默认值。
- `groupAllowFrom` 限制哪些发件人可以在房间中触发机器人（可选）。
- 每个房间的 `users` 允许列表可以进一步限制特定房间内的发件人。
- 配置向导提示输入房间允许列表（房间 ID、别名或名称），并在可能的情况下解析名称。
- 启动时，OpenClaw 解析允许列表中的房间/用户名为 ID 并记录映射；无法解析的条目保持原样。
- 邀请默认自动加入；通过 `channels.matrix.autoJoin` 和 `channels.matrix.autoJoinAllowlist` 控制。
- 允许 **没有房间**，设置 `channels.matrix.groupPolicy: "disabled"`（或保持空允许列表）。
- 旧键：`channels.matrix.rooms`（与 `groups` 形状相同）。

## 线程

- 支持回复线程。
- `channels.matrix.threadReplies` 控制回复是否保留在线程中：
  - `off`, `inbound`（默认），`always`
- `channels.matrix.replyToMode` 控制不在线程中回复时的回复元数据：
  - `off`（默认），`first`, `all`

## 功能

| 功能         | 状态                                                                                |
| --------------- | ------------------------------------------------------------------------------------- |
| 直接消息 | ✅ 支持                                                                          |
| 房间           | ✅ 支持                                                                          |
| 线程         | ✅ 支持                                                                          |
| 媒体           | ✅ 支持                                                                          |
| E2EE            | ✅ 支持（需要加密模块）                                                 |
| 反应       | ✅ 支持（通过工具发送/读取）                                                    |
| 投票           | ✅ 支持发送；传入投票开始转换为文本（忽略响应/结束） |
| 位置        | ✅ 支持（geo URI；忽略海拔）                                              |
| 原生命令 | ✅ 支持                                                                          |

## 配置参考（Matrix）

完整配置：[配置](/gateway/configuration)

提供商选项：

- `channels.matrix.enabled`: 启用/禁用通道启动。
- `channels.matrix.homeserver`: homeserver URL。
- `channels.matrix.userId`: Matrix 用户 ID（有访问令牌时可选）。
- `channels.matrix.accessToken`: 访问令牌。
- `channels.matrix.password`: 登录密码（令牌存储）。
- `channels.matrix.deviceName`: 设备显示名称。
- `channels.matrix.encryption`: 启用 E2EE（默认：false）。
- `channels.matrix.initialSyncLimit`: 初始同步限制。
- `channels.matrix.threadReplies`: `off | inbound | always`（默认：传入）。
- `channels.matrix.textChunkLimit`: 传出文本块大小（字符）。
- `channels.matrix.chunkMode`: `length`（默认）或 `newline` 以在长度分块前按空白行（段落边界）拆分。
- `channels.matrix.dm.policy`: `pairing | allowlist | open | disabled`（默认：配对）。
- `channels.matrix.dm.allowFrom`: 私信允许列表（用户 ID 或显示名称）。`open` 需要 `"*"`。向导在可能的情况下将名称解析为 ID。
- `channels.matrix.groupPolicy`: `allowlist | open | disabled`（默认：允许列表）。
- `channels.matrix.groupAllowFrom`: 群组消息的允许列表发件人。
- `channels.matrix.allowlistOnly`: 强制对私信 + 房间应用允许列表规则。
- `channels.matrix.groups`: 群组允许列表 + 每个房间设置映射。
- `channels.matrix.rooms`: 旧的群组允许列表/配置。
- `channels.matrix.replyToMode`: 线程/标签的回复模式。
- `channels.matrix.mediaMaxMb`: 传入/传出媒体限制（MB）。
- `channels.matrix.autoJoin`: 邀请处理 (`always | allowlist | off`, 默认：总是)。
- `channels.matrix.autoJoinAllowlist`: 自动加入的允许房间 ID/别名。
- `channels.matrix.actions`: 按操作工具门控（反应/消息/固定/成员信息/频道信息）。