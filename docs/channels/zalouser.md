---
summary: "Zalo personal account support via native zca-js (QR login), capabilities, and configuration"
read_when:
  - Setting up Zalo Personal for OpenClaw
  - Debugging Zalo Personal login or message flow
title: "Zalo Personal"
---
# Zalo Personal (非官方)

状态：实验性。此集成通过 OpenClaw 内的原生 `zca-js` 自动化 **个人 Zalo 账户**。

> **警告：** 这是一个非官方集成，可能导致账户暂停/封禁。请自行承担风险。

## 需要插件

Zalo Personal 作为插件提供，不包含在核心安装中。

- 通过 CLI 安装：`openclaw plugins install @openclaw/zalouser`
- 或者从源码检出：`openclaw plugins install ./extensions/zalouser`
- 详情：[插件](/tools/plugin)

不需要外部 `zca`/`openzca` CLI 二进制文件。

## 快速设置（初学者）

1. 安装插件（见上文）。
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

4. 重启网关（或完成入门引导）。
5. DM 访问默认为配对；首次联系时批准配对码。

## 功能说明

- 完全通过 `zca-js` 在进程内运行。
- 使用原生事件监听器接收传入消息。
- 直接通过 JS API 发送回复（文本/媒体/链接）。
- 专为“个人账户”用例设计，适用于无法使用 Zalo Bot API 的情况。

## 命名

通道 ID 为 `zalouser`，以明确表明这是自动化 **个人 Zalo 用户账户**（非官方）。我们保留 `zalo` 用于潜在的未来官方 Zalo API 集成。

## 查找 ID（目录）

使用目录 CLI 发现对等方/组及其 ID：

```bash
openclaw directory self --channel zalouser
openclaw directory peers list --channel zalouser --query "name"
openclaw directory groups list --channel zalouser --query "work"
```

## 限制

- 出站文本被分块为约 2000 个字符（Zalo 客户端限制）。
- 默认阻止流式传输。

## 访问控制（DM）

`channels.zalouser.dmPolicy` 支持：`pairing | allowlist | open | disabled`（默认：`pairing`）。

`channels.zalouser.allowFrom` 接受用户 ID 或名称。在入门期间，名称使用插件的进程内联系人查找解析为 ID。

批准方式：

- `openclaw pairing list zalouser`
- `openclaw pairing approve zalouser <code>`

## 组访问（可选）

- 默认：`channels.zalouser.groupPolicy = "open"`（允许组）。当未设置时使用 `channels.defaults.groupPolicy` 覆盖默认值。
- 使用以下限制为白名单：
  - `channels.zalouser.groupPolicy = "allowlist"`
  - `channels.zalouser.groups`（键为组 ID 或名称）
- 阻止所有组：`channels.zalouser.groupPolicy = "disabled"`。
- 配置向导可以提示组白名单。
- 启动时，OpenClaw 将白名单中的组/用户名称解析为 ID 并记录映射；未解析的条目保持原样输入。

示例：

```json5
{
  channels: {
    zalouser: {
      groupPolicy: "allowlist",
      groups: {
        "123456789": { allow: true },
        "Work Chat": { allow: true },
      },
    },
  },
}
```

### 组提及门控

- `channels.zalouser.groups.<group>.requireMention` 控制组回复是否需要提及。
- 解析顺序：精确组 id/名称 -> 标准化组 slug -> `*` -> 默认 (`true`)。
- 这适用于白名单组和开放组模式。

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

## 多账户

账户映射到 OpenClaw 状态中的 `zalouser` 配置文件。示例：

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

## 输入状态、表情和送达确认

- OpenClaw 在发送回复前发送输入事件（尽力而为）。
- 频道操作中的 `zalouser` 支持消息反应动作 `react`。
  - 使用 `remove: true` 从消息中移除特定反应表情符号。
  - 反应语义：[表情](/tools/reactions)
- 对于包含事件元数据的传入消息，OpenClaw 发送已送达 + 已读确认（尽力而为）。

## 故障排除

**登录状态无法保持：**

- `openclaw channels status --probe`
- 重新登录：`openclaw channels logout --channel zalouser && openclaw channels login --channel zalouser`

**白名单/组名称未解析：**

- 在 `allowFrom`/`groups` 中使用数字 ID，或确切的好友/组名称。

**从旧基于 CLI 的设置升级：**

- 移除任何旧的外部 `zca` 进程假设。
- 该通道现在完全在 OpenClaw 内运行，无需外部 CLI 二进制文件。