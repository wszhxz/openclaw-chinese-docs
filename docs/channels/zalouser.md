---
summary: "Zalo personal account support via native zca-js (QR login), capabilities, and configuration"
read_when:
  - Setting up Zalo Personal for OpenClaw
  - Debugging Zalo Personal login or message flow
title: "Zalo Personal"
---
# Zalo 个人版（非官方）

状态：实验性。此集成通过 OpenClaw 内部的原生 `zca-js` 自动化操作 **个人 Zalo 账号**。

> **警告：** 这是一个非官方集成，可能导致账号被暂停或封禁。使用风险自负。

## 捆绑插件

Zalo Personal 作为捆绑插件随当前 OpenClaw 版本发布，因此正常的打包构建无需单独安装。

如果您使用的是旧版本构建或排除了 Zalo Personal 的自定义安装，请手动安装：

- 通过 CLI 安装：`openclaw plugins install @openclaw/zalouser`
- 或从源代码检出安装：`openclaw plugins install ./path/to/local/zalouser-plugin`
- 详情：[插件](/tools/plugin)

不需要外部 `zca`/`openzca` CLI 二进制文件。

## 快速设置（初学者）

1. 确保 Zalo Personal 插件可用。
   - 当前的 OpenClaw 打包版本已包含它。
   - 旧版本/自定义安装可以使用上述命令手动添加。
2. 登录（二维码，在网关机器上）：
   - `openclaw channels login --channel zalouser`
   - 使用 Zalo 移动应用扫描二维码。
3. 启用通道：

```json5
{
  channels: {
    zalouser: {
      enabled: true,
      dmPolicy: "pairing",
    },
  },
}
```

4. 重启网关（或完成设置）。
5. 私聊访问默认为配对；首次联系时批准配对码。

## 功能概述

- 完全通过 `zca-js` 在进程内运行。
- 使用原生事件监听器接收入站消息。
- 直接通过 JS API 发送回复（文本/媒体/链接）。
- 专为“个人账号”用例设计，适用于无法使用 Zalo Bot API 的场景。

## 命名

通道 ID 为 `zalouser`，以明确说明这是自动化操作 **个人 Zalo 用户账号**（非官方）。我们保留 `zalo` 供未来可能的官方 Zalo API 集成使用。

## 查找 ID（目录）

使用目录 CLI 发现对等方/群组及其 ID：

```bash
openclaw directory self --channel zalouser
openclaw directory peers list --channel zalouser --query "name"
openclaw directory groups list --channel zalouser --query "work"
```

## 限制

- 出站文本分块为约 2000 个字符（Zalo 客户端限制）。
- 默认阻止流式传输。

## 访问控制（私聊）

`channels.zalouser.dmPolicy` 支持：`pairing | allowlist | open | disabled`（默认：`pairing`）。

`channels.zalouser.allowFrom` 接受用户 ID 或名称。在设置期间，名称会使用插件的进程内联系人查找解析为 ID。

通过以下方式批准：

- `openclaw pairing list zalouser`
- `openclaw pairing approve zalouser <code>`

## 群组访问（可选）

- 默认：`channels.zalouser.groupPolicy = "open"`（允许群组）。未设置时使用 `channels.defaults.groupPolicy` 覆盖默认值。
- 使用以下项限制为白名单：
  - `channels.zalouser.groupPolicy = "allowlist"`
  - `channels.zalouser.groups`（键应为稳定的群组 ID；名称会在启动时尽可能解析为 ID）
  - `channels.zalouser.groupAllowFrom`（控制允许群组中的哪些发送者可以触发机器人）
- 阻止所有群组：`channels.zalouser.groupPolicy = "disabled"`。
- 配置向导可以提示群组白名单。
- 启动时，OpenClaw 将白名单中的群组/用户名称解析为 ID 并记录映射。
- 群组白名单匹配默认为仅 ID。除非启用 `channels.zalouser.dangerouslyAllowNameMatching: true`，否则未解析的名称在认证中会被忽略。
- `channels.zalouser.dangerouslyAllowNameMatching: true` 是一种应急兼容性模式，重新启用可变群组名称匹配。
- 如果 `groupAllowFrom` 未设置，运行时将回退到 `allowFrom` 进行群组发送者检查。
- 发送者检查适用于普通群组和消息以及控制命令（例如 `/new`，`/reset`）。

示例：

```json5
{
  channels: {
    zalouser: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["1471383327500481391"],
      groups: {
        "123456789": { allow: true },
        "Work Chat": { allow: true },
      },
    },
  },
}
```

### 群组提及限制

- `channels.zalouser.groups.<group>.requireMention` 控制群组回复是否需要提及。
- 解析顺序：精确群组 ID/名称 -> 规范化群组 slug -> `*` -> 默认 (`true`)。
- 这既适用于白名单群组，也适用于开放群组模式。
- 授权的控制命令（例如 `/new`）可以绕过提及限制。
- 当群组消息因需要提及而被跳过时，OpenClaw 将其存储为待处理的群组历史记录，并将其包含在下一次处理的群组消息中。
- 群组历史记录限制默认为 `messages.groupChat.historyLimit`（回退 `50`）。您可以使用 `channels.zalouser.historyLimit` 按账户覆盖。

示例：

```json5
{
  channels: {
    zalouser: {
      groupPolicy: "allowlist",
      groups: {
        "*": { allow: true, requireMention: true },
        "Work Chat": { allow: true, requireMention: false },
      },
    },
  },
}
```

## 多账号

账号映射到 OpenClaw 状态中的 `zalouser` 档案。示例：

```json5
{
  channels: {
    zalouser: {
      enabled: true,
      defaultAccount: "default",
      accounts: {
        work: { enabled: true, profile: "work" },
      },
    },
  },
}
```

## 输入状态、反应和送达确认

- OpenClaw 在发送回复之前会发送一个输入状态事件（尽力而为）。
- 消息反应操作 `react` 支持用于通道操作中的 `zalouser`。
  - 使用 `remove: true` 从消息中移除特定的反应表情符号。
  - 反应语义：[反应](/tools/reactions)
- 对于包含事件元数据的入站消息，OpenClaw 会发送已送达 + 已读确认（尽力而为）。

## 故障排除

**登录不持久：**

- `openclaw channels status --probe`
- 重新登录：`openclaw channels logout --channel zalouser && openclaw channels login --channel zalouser`

**白名单/群组名称未解析：**

- 在 `allowFrom`/`groupAllowFrom`/`groups` 中使用数字 ID，或使用确切的好友/群组名称。

**从旧的基于 CLI 的设置升级：**

- 移除任何旧的关于外部 `zca` 进程的假设。
- 该通道现在完全在 OpenClaw 内运行，无需外部 CLI 二进制文件。

## 相关

- [通道概览](/channels) — 所有支持的通道
- [配对](/channels/pairing) — 私聊认证和配对流程
- [群组](/channels/groups) — 群组聊天行为和提及限制
- [通道路由](/channels/channel-routing) — 消息会话路由
- [安全](/gateway/security) — 访问模型和加固