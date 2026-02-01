---
summary: "使用安全注意事项的 OpenClaw 个人助手端到端指南"
read_when:
  - 配置新的助手实例时
  - 审查安全/权限影响时
title: "个人助手设置"
permalink: "/start/openclaw/"
---

# 使用 OpenClaw 构建个人助手

OpenClaw 是一个用于 **Pi** 代理的 WhatsApp + Telegram + Discord + iMessage 网关。插件可添加 Mattermost。本指南是"个人助手"设置：一个专用的 WhatsApp 号码，表现得像您的始终在线代理。

## ⚠️ 安全第一

您正在将代理置于以下位置：

- 在您的机器上运行命令（取决于您的 Pi 工具设置）
- 在您的工作空间中读写文件
- 通过 WhatsApp/Telegram/Discord/Mattermost（插件）发送消息

从保守开始：

- 始终设置 `channels.whatsapp.allowFrom`（永远不要在您的个人 Mac 上对世界开放运行）。
- 为助手使用专用的 WhatsApp 号码。
- 心跳现在默认为每 30 分钟一次。通过设置 `agents.defaults.heartbeat.every: "0m"` 在您信任设置之前禁用。

## 先决条件

- Node **22+**
- OpenClaw 可在 PATH 上使用（推荐：全局安装）
- 第二个电话号码（SIM/eSIM/预付费）用于助手

```bash
npm install -g openclaw@latest
# 或：pnpm add -g openclaw@latest
```

从源码（开发）：

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build # 首次运行时自动安装 UI 依赖
pnpm build
pnpm link --global
```

## 两手机设置（推荐）

您需要这样：

```
您的手机（个人）               第二部手机（助手）
┌─────────────────┐           ┌─────────────────┐
│  您的 WhatsApp  │  ──────▶  │  助手 WA        │
│  +1-555-YOU     │  消息     │  +1-555-ASSIST  │
└─────────────────┘           └────────┬────────┘
                                       │ 通过 QR 链接
                                       ▼
                              ┌─────────────────┐
                              │  您的 Mac       │
                              │  （openclaw）    │
                              │    Pi 代理      │
                              └─────────────────┘
```

如果您将您的个人 WhatsApp 链接到 OpenClaw，每条发给您的消息都会变成"代理输入"。这很少是您想要的。

## 5 分钟快速开始

1. 配对 WhatsApp Web（显示 QR；用助手手机扫描）：

```bash
openclaw channels login
```

2. 启动网关（保持运行）：

```bash
openclaw gateway --port 18789
```

3. 在 `~/.openclaw/openclaw.json` 中放入最小配置：

```json5
{
  channels: { whatsapp: { allowFrom: ["+15555550123"] } },
}
```

现在从您的白名单手机向助手号码发消息。

当入职完成时，我们会自动使用您的网关令牌打开仪表板并打印令牌化链接。要稍后重新打开：`openclaw dashboard`。

## 为代理提供工作空间（AGENTS）

OpenClaw 从其工作空间目录读取操作说明和"内存"。

默认情况下，OpenClaw 使用 `~/.openclaw/workspace` 作为代理工作空间，并将在设置/首次代理运行时自动创建它（加上起始 `AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`）。`BOOTSTRAP.md` 仅在工作空间全新时创建（在您删除它后不应再出现）。

提示：将此文件夹视为 OpenClaw 的"内存"，并将其设为 git 仓库（理想是私有的），以便备份您的 `AGENTS.md` + 内存文件。如果安装了 git，全新工作空间会自动初始化。

```bash
openclaw setup
```

完整工作空间布局 + 备份指南：[代理工作空间](/concepts/agent-workspace)
内存工作流：[内存](/concepts/memory)

可选：使用 `agents.defaults.workspace` 选择不同的工作空间（支持 `~`）。

```json5
{
  agent: {
    workspace: "~/.openclaw/workspace",
  },
}
```

如果您已经从仓库交付您自己的工作空间文件，您可以完全禁用引导文件创建：

```json5
{
  agent: {
    skipBootstrap: true,
  },
}
```

## 将其转变为"助手"的配置

OpenClaw 默认为良好的助手设置，但您通常需要调整：

- 在 `SOUL.md` 中的个性/说明
- 思考默认值（如果需要）
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
    // 从 0 开始；以后启用。
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
  session: {
    scope: "per-sender",
    resetTriggers: ["/new", "/reset"],
    reset: {
      mode: "daily",
      atHour: 4,
      idleMinutes: 10080,
    },
  },
}
```

## 会话和内存

- 会话文件：`~/.openclaw/agents/<agentId>/sessions/{{SessionId}}.jsonl`
- 会话元数据（令牌使用、最后路由等）：`~/.openclaw/agents/<agentId>/sessions/sessions.json`（旧版：`~/.openclaw/sessions/sessions.json`）
- `/new` 或 `/reset` 为此聊天启动一个新会话（可通过 `resetTriggers` 配置）。如果单独发送，代理会回复简短的问候以确认重置。
- `/compact [instructions]` 压缩会话上下文并报告剩余的上下文预算。

## 心跳（主动模式）

默认情况下，OpenClaw 每 30 分钟运行一次心跳，提示：
`如果存在 HEARTBEAT.md（工作空间上下文）则读取。严格遵循它。不要从先前的聊天中推断或重复旧任务。如果没有需要注意的事项，则回复 HEARTBEAT_OK。`
设置 `agents.defaults.heartbeat.every: "0m"` 以禁用。

- 如果 `HEARTBEAT.md` 存在但实际上为空（只有空行和像 `# Heading` 这样的 markdown 标题），OpenClaw 会跳过心跳运行以节省 API 调用。
- 如果文件丢失，心跳仍会运行，模型会决定做什么。
- 如果代理回复 `HEARTBEAT_OK`（可能带有简短填充；参见 `agents.defaults.heartbeat.ackMaxChars`），OpenClaw 会抑制该心跳的传出传递。
- 心跳运行完整的代理回合——较短的间隔会消耗更多令牌。

```json5
{
  agent: {
    heartbeat: { every: "30m" },
  },
}
```

## 媒体输入和输出

入站附件（图像/音频/文档）可通过模板呈现给您的命令：

- `{{MediaPath}}`（本地临时文件路径）
- `{{MediaUrl}}`（伪 URL）
- `{{Transcript}}`（如果启用了音频转录）

出站附件来自代理：在其独占行上包含 `MEDIA:<path-or-url>`（无空格）。例如：

```
这是截图。
MEDIA:https://example.com/screenshot.png
```

OpenClaw 会提取这些并在文本旁边发送它们。

## 运维清单

```bash
openclaw status          # 本地状态（凭据、会话、排队事件）
openclaw status --all    # 完整诊断（只读，可粘贴）
openclaw status --deep   # 添加网关健康探测（Telegram + Discord）
openclaw health --json   # 网关健康快照（WS）
```

日志保存在 `/tmp/openclaw/` 下（默认：`openclaw-YYYY-MM-DD.log`）。

## 下一步

- WebChat：[WebChat](/openclaw-chinese-docs/web/webchat)
- 网关运维：[网关运行手册](/openclaw-chinese-docs/gateway)
- Cron + 唤醒：[Cron 作业](/openclaw-chinese-docs/automation/cron-jobs)
- macOS 菜单栏伴侣：[OpenClaw macOS 应用](/openclaw-chinese-docs/platforms/macos)
- iOS 节点应用：[iOS 应用](/openclaw-chinese-docs/platforms/ios)
- Android 节点应用：[Android 应用](/openclaw-chinese-docs/platforms/android)
- Windows 状态：[Windows (WSL2)](/openclaw-chinese-docs/platforms/windows)
- Linux 状态：[Linux 应用](/openclaw-chinese-docs/platforms/linux)
- 安全：[安全](/openclaw-chinese-docs/gateway/security)