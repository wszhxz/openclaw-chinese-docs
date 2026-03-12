---
summary: "Zalo personal account support via native zca-js (QR login), capabilities, and configuration"
read_when:
  - Setting up Zalo Personal for OpenClaw
  - Debugging Zalo Personal login or message flow
title: "Zalo Personal"
---
# Zalo 个人版（非官方）

状态：实验性。该集成通过 OpenClaw 内置的原生 `zca-js` 自动化一个**个人 Zalo 账户**。

> **警告：** 这是一个非官方集成，可能导致账户被暂停或封禁。请自行承担使用风险。

## 所需插件

Zalo 个人版以插件形式提供，不包含在核心安装包中。

- 通过 CLI 安装：`openclaw plugins install @openclaw/zalouser`  
- 或从源码检出安装：`openclaw plugins install ./extensions/zalouser`  
- 详情参见：[插件](/tools/plugin)

无需依赖外部的 `zca`/`openzca` CLI 二进制文件。

## 快速配置（新手向）

1. 安装插件（见上文）。
2. 登录（扫码方式，在网关机器上执行）：
   - `openclaw channels login --channel zalouser`  
   - 使用 Zalo 移动端应用扫描二维码。
3. 启用该通道：

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

4. 重启网关（或完成初始配置流程）。
5. 私信（DM）访问默认采用配对机制；首次联系时需批准配对码。

## 功能说明

- 完全以内联方式运行，基于 `zca-js`。
- 使用原生事件监听器接收入站消息。
- 直接通过 JS API 发送回复（文本/媒体/链接）。
- 面向“个人账户”使用场景设计，适用于无法使用 Zalo Bot API 的情况。

## 命名规范

通道 ID 为 `zalouser`，以明确表示其用于自动化一个**个人 Zalo 用户账户**（非官方）。我们保留 `zalo` 供未来可能推出的官方 Zalo API 集成使用。

## 查找 ID（通讯录）

使用通讯录 CLI 发现联系人/群组及其 ID：

```bash
openclaw directory self --channel zalouser
openclaw directory peers list --channel zalouser --query "name"
openclaw directory groups list --channel zalouser --query "work"
```

## 限制条件

- 出站文本将被分块至约 2000 字符（受 Zalo 客户端限制）。
- 默认禁用流式传输（streaming）。

## 访问控制（私信）

`channels.zalouser.dmPolicy` 支持以下选项：`pairing | allowlist | open | disabled`（默认值：`pairing`）。

`channels.zalouser.allowFrom` 接受用户 ID 或姓名。在初始配置过程中，姓名将通过插件内置的进程内联系人查询功能解析为对应 ID。

批准方式包括：

- `openclaw pairing list zalouser`  
- `openclaw pairing approve zalouser <code>`

## 群组访问（可选）

- 默认：`channels.zalouser.groupPolicy = "open"`（允许加入群组）。当未显式设置时，可通过 `channels.defaults.groupPolicy` 覆盖默认行为。
- 仅允许指定群组访问，请配置：
  - `channels.zalouser.groupPolicy = "allowlist"`  
  - `channels.zalouser.groups`（键为群组 ID 或名称）
- 禁止所有群组访问：`channels.zalouser.groupPolicy = "disabled"`。
- 配置向导可在初始化时提示输入群组白名单。
- 启动时，OpenClaw 将白名单中的群组/用户名称解析为 ID 并记录映射关系；未能解析的条目将保持原始输入形式。

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

### 群组提及门控（Mention Gating）

- `channels.zalouser.groups.<group>.requireMention` 控制群组内回复是否必须包含提及（@）。
- 解析顺序为：精确匹配群组 ID/名称 → 标准化后的群组 slug → `*` → 默认值（`true`）。
- 此规则同时适用于白名单群组和开放群组模式。

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

## 多账户支持

每个账户对应 OpenClaw 状态中的一个 `zalouser` 配置文件。例如：

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

## 输入状态、表情反应与送达回执

- OpenClaw 在发送回复前会发出输入中（typing）事件（尽力而为）。
- 消息表情反应操作 `react` 已支持，可用于通道动作中的 `zalouser`。
  - 使用 `remove: true` 可移除某条消息上的特定表情符号。
  - 表情反应语义详见：[表情反应](/tools/reactions)
- 对于携带事件元数据的入站消息，OpenClaw 将发送已送达（delivered）及已读（seen）回执（尽力而为）。

## 故障排查

**登录状态无法保持：**

- `openclaw channels status --probe`  
- 重新登录：`openclaw channels logout --channel zalouser && openclaw channels login --channel zalouser`

**白名单/群组名称未能成功解析：**

- 请在 `allowFrom`/`groups` 中使用数字 ID，或使用精确匹配的好友/群组名称。

**从旧版基于 CLI 的配置升级而来：**

- 移除所有旧版外部 `zca` 进程相关假设。
- 当前通道完全在 OpenClaw 内部运行，不再依赖任何外部 CLI 二进制文件。