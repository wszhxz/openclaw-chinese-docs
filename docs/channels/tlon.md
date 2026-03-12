---
summary: "Tlon/Urbit support status, capabilities, and configuration"
read_when:
  - Working on Tlon/Urbit channel features
title: "Tlon"
---
# Tlon（插件）

Tlon 是一个基于 Urbit 构建的去中心化即时通讯工具。OpenClaw 可连接至您的 Urbit 飞船，并响应私信（DM）及群组聊天消息。默认情况下，群组回复需通过 `@` 提及触发，还可进一步通过白名单进行限制。

状态：通过插件支持。已支持私信、群组提及、线程内回复、富文本格式化以及图片上传。尚不支持表情反应与投票功能。

## 需安装插件

Tlon 以插件形式提供，未包含在核心安装包中。

通过 CLI 安装（npm 仓库）：

```bash
openclaw plugins install @openclaw/tlon
```

本地检出（从 Git 仓库运行时）：

```bash
openclaw plugins install ./extensions/tlon
```

详情参见：[插件](/tools/plugin)

## 设置步骤

1. 安装 Tlon 插件。
2. 获取您的飞船 URL 和登录码。
3. 配置 `channels.tlon`。
4. 重启网关。
5. 向机器人发送私信，或在群组频道中提及它。

最小化配置（单账户）：

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

## 私有网络 / 局域网（LAN）飞船

默认情况下，OpenClaw 为防止 SSRF 攻击，会屏蔽私有/内部主机名和 IP 地址段。  
若您飞船运行于私有网络中（如 `localhost`、局域网 IP 或内部主机名），则必须显式启用该选项：

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

此设置适用于如下 URL 示例：

- `http://localhost:8080`
- `http://192.168.x.x:8080`
- `http://my-ship.local:8080`

⚠️ 仅当您信任本地网络环境时才应启用此选项。该设置将禁用针对您飞船 URL 的 SSRF 防护机制。

## 群组频道

默认启用自动发现功能。您也可手动固定频道：

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

私信白名单（空值 = 不允许任何私信；如需审批流程，请使用 `ownerShip`）：

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

设置一个所有者飞船，以便在未授权用户尝试交互时接收审批请求：

```json5
{
  channels: {
    tlon: {
      ownerShip: "~your-main-ship",
    },
  },
}
```

所有者飞船将**自动获得全局授权**——私信邀请自动接受，频道消息始终允许。您无需将其添加至 `dmAllowlist` 或 `defaultAuthorizedShips`。

启用后，所有者将收到以下情形的私信通知：

- 来自未列入白名单飞船的私信请求；
- 在未获授权频道中的提及；
- 群组邀请请求。

## 自动接受设置

自动接受私信邀请（仅限 `dmAllowlist` 中的飞船）：

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

## 投递目标（CLI / cron）

配合 `openclaw message send` 或 cron 投递方式使用：

- 私信：`~sampel-palnet` 或 `dm/~sampel-palnet`
- 群组：`chat/~host-ship/channel` 或 `group:~host-ship/channel`

## 内置技能（Bundled skill）

Tlon 插件附带一个内置技能（[[`@tloncorp/tlon-skill`](https://github.com/tloncorp/tlon-skill)]），提供 CLI 接口以执行 Tlon 相关操作：

- **联系人**：获取/更新个人资料、列出联系人；
- **频道**：列出、创建、发布消息、获取历史记录；
- **群组**：列出、创建、管理成员；
- **私信**：发送消息、对消息添加表情反应；
- **表情反应**：为帖子及私信添加/移除 Emoji 表情；
- **设置**：通过斜杠命令管理插件权限。

插件安装后，该技能将自动可用。

## 功能支持情况

| 功能             | 状态                                      |
| ---------------- | ----------------------------------------- |
| 私信             | ✅ 已支持                                 |
| 群组/频道        | ✅ 已支持（默认需通过 `@` 提及触发）      |
| 线程             | ✅ 已支持（自动在线程内回复）            |
| 富文本           | ✅ Markdown 转换为 Tlon 原生格式         |
| 图片             | ✅ 上传至 Tlon 存储并嵌入为图片区块      |
| 表情反应         | ✅ 通过 [内置技能](#bundled-skill) 实现 |
| 投票             | ❌ 尚未支持                               |
| 原生命令         | ✅ 已支持（默认仅所有者可用）             |

## 故障排查

请首先运行以下诊断流程：

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
```

常见失败原因：

- **私信被忽略**：发送方未列入 `dmAllowlist`，且未配置 `ownerShip` 用于审批流程。
- **群组消息被忽略**：频道未被发现，或发送方未获授权。
- **连接错误**：检查飞船 URL 是否可达；若为本地飞船，请启用 `allowPrivateNetwork`。
- **认证错误**：确认登录码是否有效（登录码会定期轮换）。

## 配置参考

完整配置说明详见：[配置](/gateway/configuration)

提供商选项：

- `channels.tlon.enabled`：启用/禁用频道启动。
- `channels.tlon.ship`：机器人的 Urbit 飞船名称（例如：`~sampel-palnet`）。
- `channels.tlon.url`：飞船 URL（例如：`https://sampel-palnet.tlon.network`）。
- `channels.tlon.code`：飞船登录码。
- `channels.tlon.allowPrivateNetwork`：允许 `localhost` / 局域网 URL（绕过 SSRF 防护）。
- `channels.tlon.ownerShip`：审批系统的所有者飞船（始终授权）。
- `channels.tlon.dmAllowlist`：允许发送私信的飞船列表（空值 = 无）。
- `channels.tlon.autoAcceptDmInvites`：对白名单中的飞船自动接受私信。
- `channels.tlon.autoAcceptGroupInvites`：自动接受全部群组邀请。
- `channels.tlon.autoDiscoverChannels`：自动发现群组频道（默认：启用）。
- `channels.tlon.groupChannels`：手动固定的频道路径（nests）。
- `channels.tlon.defaultAuthorizedShips`：被授权访问所有频道的飞船列表。
- `channels.tlon.authorization.channelRules`：按频道设定的授权规则。
- `channels.tlon.showModelSignature`：在消息末尾附加模型名称。

## 注意事项

- 群组回复需通过提及触发（例如：`~your-bot-ship`）。
- 线程内回复：若收到的消息处于某一线程中，OpenClaw 将在线程内回复。
- 富文本：Markdown 格式（加粗、斜体、代码块、标题、列表等）将转换为 Tlon 原生格式。
- 图片：URL 将上传至 Tlon 存储，并以内嵌图片区块形式呈现。