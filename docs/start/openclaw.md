---
summary: "End-to-end guide for running OpenClaw as a personal assistant with safety cautions"
read_when:
  - Onboarding a new assistant instance
  - Reviewing safety/permission implications
title: "Personal Assistant Setup"
---
# 使用 OpenClaw 构建个人助手

OpenClaw 是一个 WhatsApp + Telegram + Discord + iMessage 的网关，专为 **Pi** 代理设计。插件支持 Mattermost。本指南是“个人助手”设置：一个专用的 WhatsApp 号码，其行为如同您的始终在线的代理。

## ⚠️ 安全第一

您将代理置于以下位置：

- 在您的机器上运行命令（取决于您的 Pi 工具设置）
- 在您的工作区中读写文件
- 通过 WhatsApp/Telegram/Discord/Mattermost（插件）发送消息回传

请保守设置：

- 始终设置 `channels.whatsapp.allowFrom`（不要在个人 Mac 上运行开放到世界的设置）。
- 使用专用的 WhatsApp 号码作为助手。
- 心跳现在默认每 30 分钟一次。在您信任设置前禁用，设置 `agents.defaults.heartbeat.every: "0m"`。

## 先决条件

- Node **22+**
- OpenClaw 在 PATH 中可用（推荐：全局安装）
- 用于助手的第二部手机号码（SIM/eSIM/预付费）

```bash
npm install -g openclaw@latest
# 或者: pnpm add -g openclaw@latest
```

从源代码（开发）：

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build # 首次运行时自动安装 UI 依赖
pnpm build
pnpm link --global
```

## 两部手机设置（推荐）

您想要的是：

```
您的手机（个人）          第二部手机（助手）
┌─────────────────┐           ┌─────────────────┐
│  您的 WhatsApp  │  ──────▶  │  助手 WA   │
│  +1-555-YOU     │  消息  │  +1-555-ASSIST  │
└─────────────────┘           └────────┬────────┘
                                       │ 通过 QR 码连接
                                       ▼
                              ┌─────────────────┐
                              │  您的 Mac       │
                              │  (openclaw)      │
                              │    Pi 代理     │
                              └─────────────────┘
```

如果您将个人 WhatsApp 与 OpenClaw 关联，那么发给您的每条消息都会成为“代理输入”。这通常不是您想要的。

## 5 分钟快速入门

1. 配对 WhatsApp Web（显示 QR 码；使用助手手机扫描）：

```bash
openclaw channels login
```

2. 启动网关（保持运行）：

```bash
openclaw gateway --port 18789
```

3. 在 `~/.openclaw/openclaw.json` 中放入一个最小配置：

```json5
{
  channels: { whatsapp: { allowFrom: ["+15555550123"] } },
}
```

现在从您的允许列表手机向助手号码发送消息。

当注册完成时，我们会自动打开仪表板并使用您的网关令牌打印令牌化链接。之后重新打开：`openclaw dashboard`。

## 为代理提供一个工作区（AGENTS）

OpenClaw 从其工作区目录读取操作指令和“记忆”。

默认情况下，OpenClaw 使用 `~/.openclaw/workspace` 作为代理工作区，并在设置/首次代理运行时自动创建它（加上初始的 `AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`）。`BOOTSTRAP.md` 只有在工作区全新时创建（删除后不应再出现）。

提示：将此文件夹视为 OpenClaw 的“记忆”，并将其作为 git 仓库（最好是私有）以备份您的 `AGENTS.md` + 记忆文件。如果已安装 git，全新的工作区会自动初始化。

```bash
openclaw setup
```

完整的工作区布局 + 备份指南：[Agent workspace](/concepts/agent-workspace)
记忆工作流：[Memory](/concepts/memory)

可选：使用 `agents.defaults.workspace` 选择不同的工作区（支持 `~`）。

```json5
{
  agent: {
    workspace: "~/.openclaw/workspace",
  },
}
```

如果您已经从仓库中自带自己的工作区文件，可以完全禁用启动文件的创建：

```json5
{
  agent: {
    skipBootstrap: true,
  },
}
```

## 将其转化为“助手”的配置

OpenClaw 默认设置为一个良好的助手配置，但您通常希望调整：

- `SOUL.md` 中的个性/指令
- 思考默认值（如需）
- 心跳（一旦您信任它）

示例：

```json5
{
  logging: { level: "info" },
  agent: {
    model: "anthropic/claude-opus-4-5",
    workspace: "~/.openclaw/workspace",
    thinkingDefault: "high",
    timeoutSeconds: 1800,
    // 初始设为 0；之后启用。
    heartbeat: { every: "0m" },
  },
  channels: {
    whatsapp: {
      allowFrom: ["+15555550123"],
      groups: {
        "*": { requireMention: true },
      },
    },
  },
  routing: {
    groupChat: {
      mentionPatterns: ["@openclaw", "openclaw"],
    },
  },
  session: