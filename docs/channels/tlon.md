---
summary: "Tlon/Urbit support status, capabilities, and configuration"
read_when:
  - Working on Tlon/Urbit channel features
title: "Tlon"
---
# Tlon（插件）

Tlon 是基于 Urbit 构建的去中心化即时通讯工具。OpenClaw 连接您的 Urbit ship 并可响应 DM 和群聊消息。群组回复默认需要通过 @ 提及，并且可以通过白名单进一步限制。

状态：通过插件支持。支持 DM、群组提及、线程回复、富文本格式和图片上传。表情反应和投票尚未支持。

## 需要插件

Tlon 作为插件发布，不包含在核心安装中。

通过 CLI 安装（npm 注册表）：

```bash
openclaw plugins install @openclaw/tlon
```

本地检出（当从 git 仓库运行时）：

```bash
openclaw plugins install ./extensions/tlon
```

详情：[插件](/tools/plugin)

## 设置

1. 安装 Tlon 插件。
2. 收集您的 ship URL 和登录代码。
3. 配置 `channels.tlon`。
4. 重启网关。
5. DM 机器人或在群组频道中提及它。

最小配置（单账户）：

```json5
{
  channels: {
    tlon: {
      enabled: true,
      ship: "~sampel-palnet",
      url: "https://your-ship-host",
      code: "lidlut-tabwed-pillex-ridrup",
      ownerShip: "~your-main-ship", // recommended: your ship, always allowed
    },
  },
}
```

## 私有/LAN ship

默认情况下，OpenClaw 会阻止私有/内部主机名和 IP 范围以进行 SSRF 保护。如果您的 ship 在私有网络上运行（localhost、LAN IP 或内部主机名），您必须显式选择加入：

```json5
{
  channels: {
    tlon: {
      url: "http://localhost:8080",
      allowPrivateNetwork: true,
    },
  },
}
```

这适用于以下 URL：

- `http://localhost:8080`
- `http://192.168.x.x:8080`
- `http://my-ship.local:8080`

⚠️ 仅在您信任本地网络时启用此选项。此设置会禁用针对您的 ship URL 请求的 SSRF 保护。

## 群组频道

默认启用自动发现。您也可以手动固定频道：

```json5
{
  channels: {
    tlon: {
      groupChannels: ["chat/~host-ship/general", "chat/~host-ship/support"],
    },
  },
}
```

禁用自动发现：

```json5
{
  channels: {
    tlon: {
      autoDiscoverChannels: false,
    },
  },
}
```

## 访问控制

DM 白名单（空 = 不允许 DM，使用 `ownerShip` 进行审批流程）：

```json5
{
  channels: {
    tlon: {
      dmAllowlist: ["~zod", "~nec"],
    },
  },
}
```

群组授权（默认受限）：

```json5
{
  channels: {
    tlon: {
      defaultAuthorizedShips: ["~zod"],
      authorization: {
        channelRules: {
          "chat/~host-ship/general": {
            mode: "restricted",
            allowedShips: ["~zod", "~nec"],
          },
          "chat/~host-ship/announcements": {
            mode: "open",
          },
        },
      },
    },
  },
}
```

## 所有者与审批系统

设置一个所有者 ship，以便在未授权用户尝试交互时接收审批请求：

```json5
{
  channels: {
    tlon: {
      ownerShip: "~your-main-ship",
    },
  },
}
```

所有者 ship **在所有地方自动授权** —— DM 邀请会自动接受，且频道消息始终允许。您无需将所有者添加到 `dmAllowlist` 或 `defaultAuthorizedShips`。

设置后，所有者将收到以下 DM 通知：

- 来自不在白名单中的 ship 的 DM 请求
- 未经授权的频道提及
- 群组邀请请求

## 自动接受设置

自动接受 DM 邀请（针对 dmAllowlist 中的 ship）：

```json5
{
  channels: {
    tlon: {
      autoAcceptDmInvites: true,
    },
  },
}
```

自动接受群组邀请：

```json5
{
  channels: {
    tlon: {
      autoAcceptGroupInvites: true,
    },
  },
}
```

## 投递目标（CLI/cron）

配合 `openclaw message send` 或 cron 投递使用：

- DM: `~sampel-palnet` 或 `dm/~sampel-palnet`
- 群组：`chat/~host-ship/channel` 或 `group:~host-ship/channel`

## 捆绑技能

Tlon 插件包含一个捆绑技能（[`@tloncorp/tlon-skill`](https://github.com/tloncorp/tlon-skill)），提供对 Tlon 操作的 CLI 访问权限：

- **联系人**：获取/更新个人资料，列出联系人
- **频道**：列出、创建、发布消息、获取历史记录
- **群组**：列出、创建、管理成员
- **DM**：发送消息、对消息做出反应
- **表情反应**：添加/移除帖子和 DM 的 emoji 反应
- **设置**：通过斜杠命令管理插件权限

安装插件后，该技能自动可用。

## 功能

| 功能         | 状态                                  |
| ------------ | --------------------------------------- |
| 直接消息     | ✅ 支持                            |
| 群组/频道    | ✅ 支持（默认需提及） |
| 线程         | ✅ 支持（在线程中自动回复）   |
| 富文本       | ✅ Markdown 转换为 Tlon 格式    |
| 图片         | ✅ 上传至 Tlon 存储             |
| 表情反应     | ✅ 通过 [捆绑技能](#bundled-skill)  |
| 投票         | ❌ 尚未支持                    |
| 原生命令     | ✅ 支持（默认仅限所有者）    |

## 故障排除

首先运行此命令：

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
```

常见故障：

- **DM 被忽略**：发送者不在 `dmAllowlist` 中，且未配置 `ownerShip` 用于审批流程。
- **群组消息被忽略**：频道未被发现或发送者未授权。
- **连接错误**：检查 ship URL 是否可达；为本地 ship 启用 `allowPrivateNetwork`。
- **认证错误**：验证登录代码是否有效（代码会轮换）。

## 配置参考

完整配置：[配置](/gateway/configuration)

提供者选项：

- `channels.tlon.enabled`：启用/禁用频道启动。
- `channels.tlon.ship`：机器人的 Urbit ship 名称（例如 `~sampel-palnet`）。
- `channels.tlon.url`：ship URL（例如 `https://sampel-palnet.tlon.network`）。
- `channels.tlon.code`：ship 登录代码。
- `channels.tlon.allowPrivateNetwork`：允许 localhost/LAN URL（绕过 SSRF）。
- `channels.tlon.ownerShip`：审批系统的 owner ship（始终授权）。
- `channels.tlon.dmAllowlist`：允许 DM 的 ship（空 = 无）。
- `channels.tlon.autoAcceptDmInvites`：自动接受来自白名单 ship 的 DM。
- `channels.tlon.autoAcceptGroupInvites`：自动接受所有群组邀请。
- `channels.tlon.autoDiscoverChannels`：自动发现群组频道（默认：true）。
- `channels.tlon.groupChannels`：手动固定的频道嵌套。
- `channels.tlon.defaultAuthorizedShips`：所有频道授权的 ship。
- `channels.tlon.authorization.channelRules`：每频道授权规则。
- `channels.tlon.showModelSignature`：在消息后附加模型名称。

## 备注

- 群组回复需要提及（例如 `~your-bot-ship`）才能回复。
- 线程回复：如果传入消息在线程中，OpenClaw 在线程内回复。
- 富文本：Markdown 格式（粗体、斜体、代码、标题、列表）转换为 Tlon 的原生格式。
- 图片：URL 上传至 Tlon 存储并嵌入为图片块。