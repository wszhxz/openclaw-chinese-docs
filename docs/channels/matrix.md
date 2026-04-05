---
summary: "Matrix support status, setup, and configuration examples"
read_when:
  - Setting up Matrix in OpenClaw
  - Configuring Matrix E2EE and verification
title: "Matrix"
---
# Matrix

Matrix 是 OpenClaw 的 Matrix 捆绑频道插件。
它使用官方的 `matrix-js-sdk` 并支持 DM、房间、线程、媒体、反应、投票、位置和 E2EE。

## 捆绑插件

Matrix 作为捆绑插件随当前 OpenClaw 版本发布，因此普通的打包构建不需要单独安装。

如果您使用的是旧版构建或排除了 Matrix 的自定义安装，请手动安装：

从 npm 安装：

```bash
openclaw plugins install @openclaw/matrix
```

从本地检出安装：

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

有关插件行为和安装规则，请参阅 [Plugins](/tools/plugin)。

## 设置

1. 确保 Matrix 插件可用。
   - 当前打包的 OpenClaw 版本已经捆绑了它。
   - 旧版/自定义安装可以使用上述命令手动添加它。
2. 在您的 homeserver 上创建 Matrix 账户。
3. 配置 `channels.matrix`，使用以下任一方式：
   - `homeserver` + `accessToken`，或
   - `homeserver` + `userId` + `password`。
4. 重启网关。
5. 与机器人开始 DM 或将其邀请到房间。

交互式设置路径：

```bash
openclaw channels add
openclaw configure --section channels
```

Matrix 向导实际要求的内容：

- homeserver URL
- 认证方法：访问令牌或密码
- 仅当您选择密码认证时提供用户 ID
- 可选的设备名称
- 是否启用 E2EE
- 是否现在配置 Matrix 房间访问权限

重要的向导行为：

- 如果所选账户的 Matrix 认证环境变量已存在，且该账户尚未在配置中保存认证信息，向导将提供环境变量快捷方式，并且只为该账户写入 `enabled: true`。
- 当您交互式添加另一个 Matrix 账户时，输入的账户名称会被规范化为配置和环境变量中使用的账户 ID。例如，`Ops Bot` 变为 `ops-bot`。
- DM 白名单提示立即接受完整的 `@user:server` 值。显示名称仅在实时目录查找找到一个确切匹配时有效；否则向导会要求您重试并使用完整的 Matrix ID。
- 房间白名单提示直接接受房间 ID 和别名。它们也可以实时解析加入的房间名称，但未解析的名称仅在设置期间按原样保留，并在运行时白名单解析中被忽略。首选 `!room:server` 或 `#alias:server`。
- 运行时房间/会话身份使用稳定的 Matrix 房间 ID。房间声明的别名仅用作查找输入，不作为长期会话密钥或稳定的组身份。
- 要在保存前解析房间名称，请使用 `openclaw channels resolve --channel matrix "Project Room"`。

基于令牌的极简设置：

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      dm: { policy: "pairing" },
    },
  },
}
```

基于密码的设置（登录后会缓存令牌）：

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      userId: "@bot:example.org",
      password: "replace-me", // pragma: allowlist secret
      deviceName: "OpenClaw Gateway",
    },
  },
}
```

Matrix 将缓存的凭据存储在 `~/.openclaw/credentials/matrix/` 中。
默认账户使用 `credentials.json`；命名账户使用 `credentials-<account>.json`。

环境变量等效项（当配置键未设置时使用）：

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

对于非默认账户，请使用账户作用域的环境变量：

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

账户 `ops` 的示例：

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

对于规范化后的账户 ID `ops-bot`，使用：

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

Matrix 转义账户 ID 中的标点符号以保持作用域环境变量无冲突。
例如，`-` 变为 `_X2D_`，因此 `ops-prod` 映射为 `MATRIX_OPS_X2D_PROD_*`。

交互式向导仅提供环境变量快捷方式，前提是这些认证环境变量已存在，且所选账户尚未在配置中保存 Matrix 认证。

## 配置示例

这是一个实用的基线配置，包含 DM 配对、房间白名单和启用的 E2EE：

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,

      dm: {
        policy: "pairing",
        threadReplies: "off",
      },

      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },

      autoJoin: "allowlist",
      autoJoinAllowlist: ["!roomid:example.org"],
      threadReplies: "inbound",
      replyToMode: "off",
      streaming: "partial",
    },
  },
}
```

## 流式预览

Matrix 回复流式传输是可选的。

设置 `channels.matrix.streaming` 为 `"partial"`，以便 OpenClaw 发送单个草稿回复，
在模型生成文本时就地编辑该草稿，并在回复完成后定稿：

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` 是默认值。OpenClaw 等待最终回复并只发送一次。
- `streaming: "partial"` 为当前助手块创建一个可编辑的预览消息，而不是发送多个部分消息。
- `blockStreaming: true` 启用单独的 Matrix 进度消息。使用 `streaming: "partial"` 时，Matrix 保留当前块的实时草稿，并将完成的块保留为单独的消息。
- 当 `streaming: "partial"` 和 `blockStreaming` 关闭时，Matrix 仅编辑实时草稿，并在该块或回合完成后发送一次完成的回复。
- 如果预览不再适合单个 Matrix 事件，OpenClaw 将停止预览流式传输并回退到正常的最终交付。
- 媒体回复仍正常发送附件。如果过期的预览不再能安全重用，OpenClaw 将在发送最终媒体回复之前将其删除。
- 预览编辑需要额外的 Matrix API 调用。如果您希望最保守的速率限制行为，请关闭流式传输。

`blockStreaming` 本身不启用草稿预览。
使用 `streaming: "partial"` 进行预览编辑；然后仅当您也希望完成的助手块保持可见作为单独的进度消息时，再添加 `blockStreaming: true`。

## 加密和验证

在加密（E2EE）房间中，出站图像事件使用 `thumbnail_file`，以便图像预览与完整附件一起加密。未加密的房间仍使用明文 `thumbnail_url`。无需配置——插件会自动检测 E2EE 状态。

### 机器人对机器人房间

默认情况下，来自其他配置的 OpenClaw Matrix 账户的 Matrix 消息将被忽略。

当您需要有意进行代理间 Matrix 流量时使用 `allowBots`：

```json5
{
  channels: {
    matrix: {
      allowBots: "mentions", // true | "mentions"
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

- `allowBots: true` 允许接收来自其他配置的 Matrix 机器人账户的消息（在允许的房间和 DM 中）。
- `allowBots: "mentions"` 仅当它们在房间中明显提及此机器人时才接受这些消息。DM 仍然允许。
- `groups.<room>.allowBots` 覆盖一个房间的账户级别设置。
- OpenClaw 仍会忽略来自同一 Matrix 用户 ID 的消息，以避免自回复循环。
- Matrix 在此处不暴露原生机器人标志；OpenClaw 将“机器人撰写”视为“由本 OpenClaw 网关上的另一个配置的 Matrix 账户发送”。

在共享房间中启用机器人对机器人流量时，请使用严格的房间白名单和提及要求。

启用加密：

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,
      dm: { policy: "pairing" },
    },
  },
}
```

检查验证状态：

```bash
openclaw matrix verify status
```

详细状态（完整诊断）：

```bash
openclaw matrix verify status --verbose
```

在机器可读输出中包含存储的恢复密钥：

```bash
openclaw matrix verify status --include-recovery-key --json
```

引导交叉签名和验证状态：

```bash
openclaw matrix verify bootstrap
```

多账户支持：使用 `channels.matrix.accounts` 配合每个账户的凭据和可选的 `name`。有关共享模式，请参阅 [Configuration reference](/gateway/configuration-reference#multi-account-all-channels)。

详细的引导诊断：

```bash
openclaw matrix verify bootstrap --verbose
```

在引导之前强制重置交叉签名身份：

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

使用恢复密钥验证此设备：

```bash
openclaw matrix verify device "<your-recovery-key>"
```

详细的设备验证详情：

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

检查房间密钥备份健康状态：

```bash
openclaw matrix verify backup status
```

详细的备份健康诊断：

```bash
openclaw matrix verify backup status --verbose
```

从服务器备份恢复房间密钥：

```bash
openclaw matrix verify backup restore
```

详细的恢复诊断：

```bash
openclaw matrix verify backup restore --verbose
```

删除当前的服务器备份并创建新的备份基线。如果无法干净地加载存储的备份密钥，此重置还可以重新创建秘密存储，以便未来的冷启动可以加载新的备份密钥：

```bash
openclaw matrix verify backup reset --yes
```

所有 `verify` 命令默认简洁（包括静默的内部 SDK 日志），仅在启用 `--verbose` 时显示详细诊断。
在脚本中使用 `--json` 获取完整的机器可读输出。

在多账户设置中，Matrix CLI 命令使用隐式的 Matrix 默认账户，除非你传递 `--account <id>`。
如果你配置了多个命名账户，请先设置 `channels.matrix.defaultAccount`，否则那些隐式 CLI 操作将停止并要求你显式选择账户。
当你希望验证或设备操作明确针对某个命名账户时，请使用 `--account`：

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

当加密对某个命名账户被禁用或不可用时，Matrix 警告和验证错误会指向该账户的配置键，例如 `channels.matrix.accounts.assistant.encryption`。

### “已验证”的含义

OpenClaw 仅在通过你自己的交叉签名身份验证时，才将此 Matrix 设备视为已验证。
实际上，`openclaw matrix verify status --verbose` 暴露了三个信任信号：

- `Locally trusted`：此设备仅受当前客户端信任
- `Cross-signing verified`：SDK 报告该设备已通过交叉签名验证
- `Signed by owner`：该设备由你自己的自签名密钥签名

只有在存在交叉签名验证或所有者签名时，`Verified by owner` 才会变为 `yes`。
仅凭本地信任不足以让 OpenClaw 将该设备视为完全验证。

### Bootstrap 的作用

`openclaw matrix verify bootstrap` 是用于加密 Matrix 账户的修复和设置命令。
它按顺序执行以下所有操作：

- 引导秘密存储，尽可能重用现有的恢复密钥
- 引导交叉签名并上传缺失的公共交叉签名密钥
- 尝试标记并对当前设备进行交叉签名
- 如果不存在，则创建新的服务器端房间密钥备份

如果 Homeserver 需要交互式认证来上传交叉签名密钥，OpenClaw 首先尝试不带认证的上传，然后使用 `m.login.dummy`，当配置了 `channels.matrix.password` 时使用 `m.login.password`。
仅当你有意要丢弃当前的交叉签名身份并创建一个新身份时，才使用 `--force-reset-cross-signing`。

如果你有意要丢弃当前的房间密钥备份并为未来消息开始一个新的备份基线，请使用 `openclaw matrix verify backup reset --yes`。
仅在你接受无法恢复的旧加密历史将保持不可用，且如果当前备份密钥无法安全加载则 OpenClaw 可能会重新创建秘密存储时，才执行此操作。

### 新的备份基线

如果你希望保留未来的加密消息功能并接受丢失无法恢复的旧历史，请按顺序运行这些命令：

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

当你希望明确针对某个命名 Matrix 账户时，在每个命令中添加 `--account <id>`。

### 启动行为

当 `encryption: true` 时，Matrix 默认将 `startupVerification` 设置为 `"if-unverified"`。
启动时，如果此设备仍未验证，Matrix 将在另一个 Matrix 客户端请求自我验证，当一个请求已挂起时跳过重复请求，并在重启后重试前应用本地冷却期。
失败的请求尝试默认比成功的请求创建更早重试。
设置 `startupVerification: "off"` 以禁用自动启动请求，或者调整 `startupVerificationCooldownHours` 以获得更短或更长的重试窗口。

启动还会自动执行保守的加密引导过程。
该过程首先尝试重用当前的秘密存储和交叉签名身份，并且除非你运行明确的引导修复流程，否则避免重置交叉签名。
如果启动发现损坏的引导状态且配置了 `channels.matrix.password`，OpenClaw 可以尝试更严格的修复路径。
如果当前设备已经是所有者签名，OpenClaw 会保留该身份而不是自动重置它。

从之前的公共 Matrix 插件升级：

- OpenClaw 在可能时自动重用相同的 Matrix 账户、访问令牌和设备身份。
- 在任何可操作的 Matrix 迁移更改运行之前，OpenClaw 会在 `~/Backups/openclaw-migrations/` 下创建或重用恢复快照。
- 如果你使用多个 Matrix 账户，请在从旧的扁平存储布局升级之前设置 `channels.matrix.defaultAccount`，以便 OpenClaw 知道哪个账户应该接收该共享的遗留状态。
- 如果之前的插件在本地存储了 Matrix 房间密钥备份解密密钥，启动或 `openclaw doctor --fix` 将自动将其导入新的恢复密钥流程。
- 如果在准备迁移后 Matrix 访问令牌发生了变化，启动现在会在放弃自动备份恢复之前扫描兄弟令牌哈希存储根以查找待处理的遗留恢复状态。
- 如果稍后相同账户、Homeserver 和用户更改了 Matrix 访问令牌，OpenClaw 现在更喜欢重用现有最完整的令牌哈希存储根，而不是从空的 Matrix 状态目录开始。
- 在下一次网关启动时，备份的房间密钥会自动恢复到新的加密存储中。
- 如果旧插件有从未备份过的仅本地房间密钥，OpenClaw 将发出清晰警告。这些密钥无法从前一个 Rust 加密存储中自动导出，因此一些旧的加密历史可能在手动恢复之前保持不可用。
- 有关完整的升级流程、限制、恢复命令和常见迁移消息，请参阅 [Matrix 迁移](/install/migrating-matrix)。

加密运行时状态组织在 `~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/` 下的每个账户、每个用户的令牌哈希根下。
当使用这些功能时，该目录包含同步存储 (`bot-storage.json`)、加密存储 (`crypto/`)、恢复密钥文件 (`recovery-key.json`)、IndexedDB 快照 (`crypto-idb-snapshot.json`)、线程绑定 (`thread-bindings.json`) 和启动验证状态 (`startup-verification.json`)。
当令牌更改但账户身份保持不变时，OpenClaw 重用该账户/Homeserver/用户元组的最佳现有根，以便先前的同步状态、加密状态、线程绑定和启动验证状态保持可见。

### Node 加密存储模型

本插件中的 Matrix E2EE 使用 Node 中官方的 `matrix-js-sdk` Rust 加密路径。
当你希望加密状态在重启后存活时，该路径期望基于 IndexedDB 的持久化。

OpenClaw 目前在 Node 中通过以下方式提供：

- 使用 `fake-indexeddb` 作为 SDK 预期的 IndexedDB API 适配器
- 在 `initRustCrypto` 之前从 `crypto-idb-snapshot.json` 恢复 Rust 加密 IndexedDB 内容
- 在初始化期间和运行时将更新的 IndexedDB 内容持久化回 `crypto-idb-snapshot.json`
- 对 `crypto-idb-snapshot.json` 进行快照恢复和持久化的序列化，并使用建议性文件锁，以防止网关运行时持久化和 CLI 维护在同一快照文件上竞争

这是兼容性/存储管道，不是自定义加密实现。
快照文件是敏感的运行时状态，并以限制性文件权限存储。
在 OpenClaw 的安全模型下，网关主机和本地 OpenClaw 状态目录已经在可信操作员边界内，因此这主要是操作持久性问题，而不是单独的远程信任边界。

计划改进：

- 为持久化 Matrix 密钥材料添加 SecretRef 支持，以便恢复密钥和相关存储加密密钥可以从 OpenClaw 密钥提供者获取，而不仅仅是本地文件

## 个人资料管理

使用以下命令更新选定账户的 Matrix 个人资料：

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

当你希望明确针对某个命名 Matrix 账户时，添加 `--account <id>`。

Matrix 直接接受 `mxc://` 头像 URL。当你传递 `http://` 或 `https://` 头像 URL 时，OpenClaw 首先将其上传到 Matrix，并将解析后的 `mxc://` URL 存储回 `channels.matrix.avatarUrl`（或选定的账户覆盖）。

## 自动验证通知

Matrix 现在将验证生命周期通知直接发布到严格的 DM 验证房间，作为 `m.notice` 消息。
包括：

- 验证请求通知
- 验证就绪通知（带有明确的“通过表情符号验证”指导）
- 验证开始和完成通知
- SAS 详细信息（表情符号和十进制数）（如可用）

来自另一个 Matrix 客户端的传入验证请求会被跟踪并由 OpenClaw 自动接受。
对于自我验证流程，当表情符号验证可用并确认其自身一侧时，OpenClaw 也会自动启动 SAS 流程。
对于来自另一个 Matrix 用户/设备的验证请求，OpenClaw 自动接受请求，然后等待 SAS 流程正常进行。
你仍然需要在你的 Matrix 客户端中比较表情符号或十进制 SAS，并在那里确认“它们匹配”以完成验证。

OpenClaw 不会盲目自动接受自行发起的重复流程。当已有自我验证请求挂起时，启动会跳过创建新请求。
验证协议/系统通知不会转发到代理聊天管道，因此它们不会产生 `NO_REPLY`。

### 设备维护

旧的 OpenClaw 管理的 Matrix 设备可能会在账户上积累，并使加密房间的信任关系更难理清。
列出它们：

```bash
openclaw matrix devices list
```

删除过时的 OpenClaw 管理设备：

```bash
openclaw matrix devices prune-stale
```

### 直接房间修复

如果直接消息状态不同步，OpenClaw 可能会保留过时的 `m.direct` 映射，指向旧的单人房间而不是当前的 DM。使用以下命令检查对等体的当前映射：

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

使用以下命令修复它：

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

修复操作将 Matrix 特定的逻辑保留在插件内部：

- 它优先选择已经在 `m.direct` 中映射的严格 1:1 DM
- 否则回退到与该用户的任何当前已加入的严格 1:1 DM
- 如果不存在健康的 DM，则创建一个全新的直接房间并重写 `m.direct` 以指向它

修复流程不会自动删除旧房间。它只选择健康的 DM 并更新映射，以便新的 Matrix 发送、验证通知和其他直接消息流再次指向正确的房间。

## 线程

Matrix 支持用于自动回复和消息工具发送的原生 Matrix 线程。

- `threadReplies: "off"` 保持回复为顶层，并将入站线程消息保持在父会话上。
- `threadReplies: "inbound"` 仅当入站消息已在该线程中时才在线程内回复。
- `threadReplies: "always"` 将房间回复保持在根植于触发消息的线程中，并通过来自第一个触发消息的匹配线程作用域会话路由该对话。
- `dm.threadReplies` 仅覆盖 DM 的顶层设置。例如，您可以保持房间线程隔离，同时保持 DM 扁平。
- 入站线程消息包括线程根消息作为额外的代理上下文。
- 消息工具发送现在在目标为同一房间或同一 DM 用户目标时自动继承当前 Matrix 线程，除非提供了显式的 `threadId`。
- 支持 Matrix 的运行时线程绑定。`/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age` 以及线程绑定的 `/acp spawn` 现在可在 Matrix 房间和 DM 中工作。
- 顶层 Matrix 房间/DM `/focus` 在 `threadBindings.spawnSubagentSessions=true` 时创建新的 Matrix 线程并将其绑定到目标会话。
- 在现有 Matrix 线程内运行 `/focus` 或 `/acp spawn --thread here` 将绑定该当前线程。

## ACP 对话绑定

Matrix 房间、DM 和现有的 Matrix 线程可以转换为持久的 ACP 工作区，而无需更改聊天界面。

快速操作员流程：

- 在您希望继续使用的 Matrix DM、房间或现有线程内运行 `/acp spawn codex --bind here`。
- 在顶层 Matrix DM 或房间中，当前 DM/房间保持为聊天界面，未来的消息路由到生成的 ACP 会话。
- 在现有 Matrix 线程内，`--bind here` 就地绑定该当前线程。
- `/new` 和 `/reset` 就地重置相同的已绑定 ACP 会话。
- `/acp close` 关闭 ACP 会话并移除绑定。

注意：

- `--bind here` 不创建子 Matrix 线程。
- `threadBindings.spawnAcpSessions` 仅对 `/acp spawn --thread auto|here` 是必需的，其中 OpenClaw 需要创建或绑定子 Matrix 线程。

### 线程绑定配置

Matrix 从 `session.threadBindings` 继承全局默认值，也支持每通道覆盖：

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Matrix 线程绑定生成标志是需手动启用的：

- 设置 `threadBindings.spawnSubagentSessions: true` 以允许顶层 `/focus` 创建并绑定新的 Matrix 线程。
- 设置 `threadBindings.spawnAcpSessions: true` 以允许 `/acp spawn --thread auto|here` 将 ACP 会话绑定到 Matrix 线程。

## 反应

Matrix 支持出站反应操作、入站反应通知和入站确认反应。

- 出站反应工具由 `channels["matrix"].actions.reactions` 控制。
- `react` 向特定 Matrix 事件添加反应。
- `reactions` 列出特定 Matrix 事件的当前反应摘要。
- `emoji=""` 移除机器人账户在该事件上的自身反应。
- `remove: true` 仅从机器人账户移除指定的表情符号反应。

确认反应使用标准的 OpenClaw 解析顺序：

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- 代理身份表情符号回退

确认反应范围按此顺序解析：

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

反应通知模式按此顺序解析：

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- 默认：`own`

当前行为：

- `reactionNotifications: "own"` 转发针对机器人撰写的 Matrix 消息添加的 `m.reaction` 事件。
- `reactionNotifications: "off"` 禁用反应系统事件。
- 反应移除仍未合成为系统事件，因为 Matrix 将这些显示为撤回，而不是独立的 `m.reaction` 移除。

## 历史上下文

- `channels.matrix.historyLimit` 控制在 Matrix 房间消息触发代理时包含多少条最近的房间消息作为 `InboundHistory`。
- 它回退到 `messages.groupChat.historyLimit`。设置 `0` 以禁用。
- Matrix 房间历史仅限房间。DM 继续使用正常会话历史。
- Matrix 房间历史仅限待处理：OpenClaw 缓冲尚未触发回复的房间消息，然后在提及或其他触发到达时对该窗口进行快照。
- 当前触发消息不包含在 `InboundHistory` 中；它保留在该轮次的主入站正文中。
- 同一 Matrix 事件的重试重用原始历史快照，而不是漂移到更新的房间消息。

## 上下文可见性

Matrix 支持共享的 `contextVisibility` 控制，用于补充房间上下文，例如获取的回复文本、线程根和待处理历史。

- `contextVisibility: "all"` 是默认值。补充上下文保持接收原样。
- `contextVisibility: "allowlist"` 过滤补充上下文至活动房间/用户允许列表检查允许的发送者。
- `contextVisibility: "allowlist_quote"` 行为类似于 `allowlist`，但仍保留一个显式的引用回复。

此设置影响补充上下文可见性，不影响入站消息本身是否可以触发回复。
触发授权仍来自 `groupPolicy`、`groups`、`groupAllowFrom` 和 DM 策略设置。

## DM 和房间策略示例

```json5
{
  channels: {
    matrix: {
      dm: {
        policy: "allowlist",
        allowFrom: ["@admin:example.org"],
        threadReplies: "off",
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

参见 [群组](/channels/groups) 了解提及门控和允许列表行为。

Matrix DM 配对示例：

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

如果未批准的 Matrix 用户在批准前继续向您发消息，OpenClaw 会重用相同的待处理配对代码，并在短暂冷却后可能再次发送提醒回复，而不是生成新代码。

参见 [配对](/channels/pairing) 了解共享 DM 配对流程和存储布局。

## 执行批准

Matrix 可以作为 Matrix 账户的执行批准客户端。

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers`（可选；回退到 `channels.matrix.dm.allowFrom`）
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`，默认：`dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

批准者必须是 Matrix 用户 ID，例如 `@owner:example.org`。当 `enabled` 未设置或 `"auto"` 且至少可以解析一个批准者（来自 `execApprovals.approvers` 或 `channels.matrix.dm.allowFrom`）时，Matrix 会自动启用原生执行批准。设置 `enabled: false` 可显式禁用 Matrix 作为原生批准客户端。否则，批准请求将回退到其他配置的批准路由或执行批准后备策略。

原生 Matrix 路由目前仅限执行：

- `channels.matrix.execApprovals.*` 仅控制执行批准的原生 DM/通道路由。
- 插件批准仍使用共享的同聊天 `/approve` 加上任何配置的 `approvals.plugin` 转发。
- Matrix 仍可在安全推断批准者时复用 `channels.matrix.dm.allowFrom` 进行插件批准授权，但它不暴露单独的原生插件批准 DM/通道扇出路径。

交付规则：

- `target: "dm"` 将批准提示发送到批准者 DM
- `target: "channel"` 将提示发送回源 Matrix 房间或 DM
- `target: "both"` 发送到批准者 DM 和源 Matrix 房间或 DM

Matrix 目前使用文本批准提示。批准者通过 `/approve <id> allow-once`、`/approve <id> allow-always` 或 `/approve <id> deny` 解决它们。

只有已解析的批准者才能批准或拒绝。通道交付包括命令文本，因此仅在受信任的房间中启用 `channel` 或 `both`。

Matrix 批准提示重用共享的核心批准规划器。Matrix 特定的原生界面仅用于执行批准的传输：房间/DM 路由和消息发送/更新/删除行为。

每账户覆盖：

- `channels.matrix.accounts.<account>.execApprovals`

相关文档：[执行批准](/tools/exec-approvals)

## 多账户示例

```json5
{
  channels: {
    matrix: {
      enabled: true,
      defaultAccount: "assistant",
      dm: { policy: "pairing" },
      accounts: {
        assistant: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_assistant_xxx",
          encryption: true,
        },
        alerts: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_alerts_xxx",
          dm: {
            policy: "allowlist",
            allowFrom: ["@ops:example.org"],
            threadReplies: "off",
          },
        },
      },
    },
  },
}
```

顶级 `channels.matrix` 值作为命名账户的默认值，除非账户对其进行覆盖。
您可以使用 `groups.<room>.account`（或遗留的 `rooms.<room>.account`）将继承的房间条目限定到单个 Matrix 账户。
没有 `account` 的条目在所有 Matrix 账户间保持共享，而带有 `account: "default"` 的条目在直接在顶级 `channels.matrix.*` 上配置默认账户时仍然有效。
部分共享认证默认值本身不会创建单独的隐式默认账户。
OpenClaw 仅在默认账户拥有新鲜认证时合成顶级 `default` 账户（`homeserver` 加上 `accessToken`，或 `homeserver` 加上 `userId` 和 `password`）；当缓存凭据稍后满足认证时，命名账户仍可从 `homeserver` 加上 `userId` 被发现。
如果 Matrix 已经恰好有一个命名账户，或者 `defaultAccount` 指向现有的命名账户键，单账户到多账户的修复/设置提升将保留该账户，而不是创建新的 `accounts.default` 条目。
只有 Matrix 认证/引导键移动到该提升的账户；共享交付策略键保持在顶级。
当您希望 OpenClaw 为隐式路由、探测和 CLI 操作优先选择一个命名 Matrix 账户时，设置 `defaultAccount`。
如果您配置了多个命名账户，请设置 `defaultAccount` 或在依赖隐式账户选择的 CLI 命令中传递 `--account <id>`。
当您想为一个命令覆盖该隐式选择时，向 `openclaw matrix verify ...` 和 `openclaw matrix devices ...` 传递 `--account <id>`。

## Private/LAN homeservers

默认情况下，为了 SSRF 保护，OpenClaw 会阻止私有/内部 Matrix Homeservers，除非您
显式地按账户选择加入。

如果您的 Homeserver 运行在 localhost、LAN/Tailscale IP 或内部主机名上，启用
`allowPrivateNetwork` 为该 Matrix 账户：

```json5
{
  channels: {
    matrix: {
      homeserver: "http://matrix-synapse:8008",
      allowPrivateNetwork: true,
      accessToken: "syt_internal_xxx",
    },
  },
}
```

CLI 设置示例：

```bash
openclaw matrix account add \
  --account ops \
  --homeserver http://matrix-synapse:8008 \
  --allow-private-network \
  --access-token syt_ops_xxx
```

此选择加入仅允许受信任的私有/内部目标。公共明文 Homeservers 例如
`http://matrix.example.org:8008` 仍被阻止。尽可能优先使用 `https://`。

## Proxying Matrix traffic

如果您的 Matrix 部署需要明确的出站 HTTP(S) 代理，设置 `channels.matrix.proxy`：

```json5
{
  channels: {
    matrix: {
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
    },
  },
}
```

命名账户可以使用 `channels.matrix.accounts.<id>.proxy` 覆盖顶级默认值。
OpenClaw 对运行时 Matrix 流量和账户状态探测使用相同的代理设置。

## Target resolution

在任何 OpenClaw 要求您提供房间或用户目标的地方，Matrix 接受这些目标形式：

- 用户：`@user:server`、`user:@user:server` 或 `matrix:user:@user:server`
- 房间：`!room:server`、`room:!room:server` 或 `matrix:room:!room:server`
- 别名：`#alias:server`、`channel:#alias:server` 或 `matrix:channel:#alias:server`

实时目录查找使用登录的 Matrix 账户：

- 用户查找查询该 Homeserver 上的 Matrix 用户目录。
- 房间查找直接接受显式的房间 ID 和别名，然后回退到搜索该账户的已加入房间名称。
- 已加入房间名称查找是尽力而为的。如果房间名称无法解析为 ID 或别名，它将被运行时白名单解析忽略。

## Configuration reference

- `enabled`：启用或禁用通道。
- `name`：账户的可选标签。
- `defaultAccount`：配置多个 Matrix 账户时的首选账户 ID。
- `homeserver`：Homeserver URL，例如 `https://matrix.example.org`。
- `allowPrivateNetwork`：允许此 Matrix 账户连接到私有/内部 Homeservers。当 Homeserver 解析为 `localhost`、LAN/Tailscale IP 或内部主机（如 `matrix-synapse`）时启用此项。
- `proxy`：Matrix 流量的可选 HTTP(S) 代理 URL。命名账户可以使用自己的 `proxy` 覆盖顶级默认值。
- `userId`：完整的 Matrix 用户 ID，例如 `@bot:example.org`。
- `accessToken`：基于令牌的认证访问令牌。支持 `channels.matrix.accessToken` 和 `channels.matrix.accounts.<id>.accessToken` 的明文值和 SecretRef 值，适用于 env/file/exec 提供者。请参阅 [Secrets Management](/gateway/secrets)。
- `password`：基于密码登录的密码。支持明文值和 SecretRef 值。
- `deviceId`：显式 Matrix 设备 ID。
- `deviceName`：密码登录的设备显示名称。
- `avatarUrl`：用于个人资料同步和 `set-profile` 更新的存储自我头像 URL。
- `initialSyncLimit`：启动同步事件限制。
- `encryption`：启用 E2EE。
- `allowlistOnly`：强制 DM 和房间的仅白名单行为。
- `allowBots`：允许来自其他配置的 OpenClaw Matrix 账户的消息（`true` 或 `"mentions"`）。
- `groupPolicy`：`open`、`allowlist` 或 `disabled`。
- `contextVisibility`：补充房间上下文可见性模式（`all`、`allowlist`、`allowlist_quote`）。
- `groupAllowFrom`：房间流量的用户 ID 白名单。
- `groupAllowFrom` 条目应为完整的 Matrix 用户 ID。未解析的名称在运行时被忽略。
- `historyLimit`：包含为群组历史记录上下文的最大房间消息数。回退到 `messages.groupChat.historyLimit`。设置 `0` 以禁用。
- `replyToMode`：`off`、`first` 或 `all`。
- `markdown`：出站 Matrix 文本的可选 Markdown 渲染配置。
- `streaming`：`off`（默认）、`partial`、`true` 或 `false`。`partial` 和 `true` 启用带原位编辑更新的单消息草稿预览。
- `blockStreaming`：`true` 在草稿预览流式传输活动时为完成的助手块启用单独的进度消息。
- `threadReplies`：`off`、`inbound` 或 `always`。
- `threadBindings`：线程绑定会话路由和生命周期的每通道覆盖。
- `startupVerification`：启动时的自动自我验证请求模式（`if-unverified`、`off`）。
- `startupVerificationCooldownHours`：重试自动启动验证请求前的冷却时间。
- `textChunkLimit`：出站消息块大小。
- `chunkMode`：`length` 或 `newline`。
- `responsePrefix`：出站回复的可选消息前缀。
- `ackReaction`：此通道/账户的可选确认反应覆盖。
- `ackReactionScope`：可选确认反应范围覆盖（`group-mentions`、`group-all`、`direct`、`all`、`none`、`off`）。
- `reactionNotifications`：入站反应通知模式（`own`、`off`）。
- `mediaMaxMb`：Matrix 媒体处理的媒体大小上限（MB）。它适用于出站发送和入站媒体处理。
- `autoJoin`：邀请自动加入策略（`always`、`allowlist`、`off`）。默认值：`off`。
- `autoJoinAllowlist`：当 `autoJoin` 为 `allowlist` 时允许的房间/别名。别名条目在邀请处理期间解析为房间 ID；OpenClaw 不信任受邀房间声称的别名状态。
- `dm`：DM 策略块（`enabled`、`policy`、`allowFrom`、`threadReplies`）。
- `dm.allowFrom` 条目应为完整的 Matrix 用户 ID，除非您已经通过实时目录查找解析了它们。
- `dm.threadReplies`：仅 DM 线程策略覆盖（`off`、`inbound`、`always`）。它覆盖了顶级的 `threadReplies` 设置，包括 DM 中的回复放置和会话隔离。
- `execApprovals`：原生 Matrix 执行批准交付（`enabled`、`approvers`、`target`、`agentFilter`、`sessionFilter`）。
- `execApprovals.approvers`：允许批准执行请求的 Matrix 用户 ID。当 `dm.allowFrom` 已标识批准者时为可选。
- `execApprovals.target`：`dm | channel | both`（默认值：`dm`）。
- `accounts`：按名称的每账户覆盖。顶级 `channels.matrix` 值作为这些条目的默认值。
- `groups`：每房间策略映射。优先使用房间 ID 或别名；未解析的房间名称在运行时被忽略。会话/组身份在解析后使用稳定的房间 ID，而人类可读的标签仍来自房间名称。
- `groups.<room>.account`：在多账户设置中将一个继承的房间条目限制到特定的 Matrix 账户。
- `groups.<room>.allowBots`：配置机器人发送者的房间级别覆盖（`true` 或 `"mentions"`）。
- `groups.<room>.users`：每房间发送者白名单。
- `groups.<room>.tools`：每房间工具允许/拒绝覆盖。
- `groups.<room>.autoReply`：房间级别提及门禁覆盖。`true` 禁用该房间的提及要求；`false` 强制将其重新开启。
- `groups.<room>.skills`：可选的房间级别技能过滤器。
- `groups.<room>.systemPrompt`：可选的房间级别系统提示片段。
- `rooms`：`groups` 的旧版别名。
- `actions`：按动作的工具门禁（`messages`、`reactions`、`pins`、`profile`、`memberInfo`、`channelInfo`、`verification`）。

## Related

- [通道概览](/channels) — 所有支持的通道
- [配对](/channels/pairing) — DM 认证和配对流程
- [群组](/channels/groups) — 群聊行为和提及门禁
- [通道路由](/channels/channel-routing) — 消息的会话路由
- [安全](/gateway/security) — 访问模型和加固