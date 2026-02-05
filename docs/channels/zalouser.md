---
summary: "Zalo personal account support via zca-cli (QR login), capabilities, and configuration"
read_when:
  - Setting up Zalo Personal for OpenClaw
  - Debugging Zalo Personal login or message flow
title: "Zalo Personal"
---
# Zalo Personal (非官方)

状态：实验中。此集成通过 `zca-cli` 自动化一个 **个人 Zalo 账户**。

> **警告：** 这是一个非官方集成，可能会导致账户被暂停/封禁。请自行承担风险。

## 需要插件

Zalo Personal 作为一个插件提供，并不包含在核心安装包中。

- 通过 CLI 安装：`openclaw plugins install @openclaw/zalouser`
- 或者从源码检出：`openclaw plugins install ./extensions/zalouser`
- 详情：[插件](/plugin)

## 先决条件：zca-cli

网关机器必须在 `PATH` 中有可用的 `zca` 二进制文件。

- 验证：`zca --version`
- 如果缺失，请安装 zca-cli（参见 `extensions/zalouser/README.md` 或上游 zca-cli 文档）。

## 快速设置（初学者）

1. 安装插件（见上文）。
2. 登录（二维码，在网关机器上）：
   - `openclaw channels login --channel zalouser`
   - 使用 Zalo 移动应用扫描终端中的二维码。
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

4. 重启网关（或完成入站设置）。
5. 默认情况下，直接消息访问需要配对；在首次联系时批准配对代码。

## 什么是它

- 使用 `zca listen` 接收传入消息。
- 使用 `zca msg ...` 发送回复（文本/媒体/链接）。
- 专为 Zalo Bot API 不可用的“个人账户”使用场景设计。

## 命名

通道 ID 是 `zalouser` 以明确这是自动化一个 **个人 Zalo 用户账户**（非官方）。我们保留 `zalo` 用于潜在的未来官方 Zalo API 集成。

## 查找 ID（目录）

使用目录 CLI 发现对等体/群组及其 ID：

```bash
openclaw directory self --channel zalouser
openclaw directory peers list --channel zalouser --query "name"
openclaw directory groups list --channel zalouser --query "work"
```

## 限制

- 发送的文本被分块为约 2000 字符（Zalo 客户端限制）。
- 默认情况下阻止流式传输。

## 访问控制（直接消息）

`channels.zalouser.dmPolicy` 支持：`pairing | allowlist | open | disabled`（默认：`pairing`）。
`channels.zalouser.allowFrom` 接受用户 ID 或名称。向导在可用时通过 `zca friend find` 将名称解析为 ID。

通过以下方式批准：

- `openclaw pairing list zalouser`
- `openclaw pairing approve zalouser <code>`

## 群组访问（可选）

- 默认：`channels.zalouser.groupPolicy = "open"`（允许群组）。当未设置时，使用 `channels.defaults.groupPolicy` 覆盖默认值。
- 使用白名单限制：
  - `channels.zalouser.groupPolicy = "allowlist"`
  - `channels.zalouser.groups`（键是群组 ID 或名称）
- 阻止所有群组：`channels.zalouser.groupPolicy = "disabled"`。
- 配置向导可以提示输入群组白名单。
- 启动时，OpenClaw 将白名单中的群组/用户名解析为 ID 并记录映射；无法解析的条目将保持原样。

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

## 多账户

账户映射到 zca 配置文件。示例：

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

## 故障排除

**未找到 `zca`：**

- 安装 zca-cli 并确保它在 `PATH` 中供网关进程使用。

**登录不持久：**

- `openclaw channels status --probe`
- 重新登录：`openclaw channels logout --channel zalouser && openclaw channels login --channel zalouser`