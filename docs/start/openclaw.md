---
summary: "End-to-end guide for running OpenClaw as a personal assistant with safety cautions"
read_when:
  - Onboarding a new assistant instance
  - Reviewing safety/permission implications
title: "Personal Assistant Setup"
---
# 使用OpenClaw构建个人助手

OpenClaw是一个WhatsApp + Telegram + Discord + iMessage网关，适用于**Pi**代理。插件增加了Mattermost支持。本指南是“个人助手”设置：一个专用的WhatsApp号码，行为类似于您的始终在线代理。

## ⚠️ 安全第一

您将代理置于以下位置：

- 在您的机器上运行命令（取决于您的Pi工具设置）
- 读取/写入工作区中的文件
- 通过WhatsApp/Telegram/Discord/Mattermost（插件）发送消息

从保守开始：

- 始终设置`channels.whatsapp.allowFrom`（永远不要在个人Mac上运行开放到世界的设置）。
- 为助手使用专用的WhatsApp号码。
- 心跳现在默认每30分钟一次。通过设置`agents.defaults.heartbeat.every: "0m"`禁用，直到您信任该设置。

## 先决条件

- Node **22+**
- OpenClaw在PATH中可用（推荐：全局安装）
- 一个辅助电话号码（SIM/eSIM/预付费）用于助手

```bash
npm install -g openclaw@latest
# or: pnpm add -g openclaw@latest
```

从源码（开发）：

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build # auto-installs UI deps on first run
pnpm build
pnpm link --global
```

## 两手机设置（推荐）

您需要这个：

```
Your Phone (personal)          Second Phone (assistant)
┌─────────────────┐           ┌─────────────────┐
│  Your WhatsApp  │  ──────▶  │  Assistant WA   │
│  +1-555-YOU     │  message  │  +1-555-ASSIST  │
└─────────────────┘           └────────┬────────┘
                                       │ linked via QR
                                       ▼
                              ┌─────────────────┐
                              │  Your Mac       │
                              │  (openclaw)      │
                              │    Pi agent     │
                              └─────────────────┘
```

如果您将个人WhatsApp链接到OpenClaw，发给您的每条消息都会成为“代理输入”。这通常不是您想要的。

## 5分钟快速入门

1. 配对WhatsApp Web（显示QR码；使用助手手机扫描）：

```bash
openclaw channels login
```

2. 启动网关（让它运行）：

```bash
openclaw gateway --port 18789
```

3. 在`~/.openclaw/openclaw.json`中放置最小配置：

```json5
{
  channels: { whatsapp: { allowFrom: ["+15555550123"] } },
}
```

现在从您的白名单手机向助手号码发送消息。

当入职完成时，我们会自动打开仪表板并打印带有网关令牌的令牌化链接。稍后重新打开：`openclaw dashboard`。

## 给代理一个工作区（AGENTS）

OpenClaw从其工作区目录读取操作指令和“记忆”。

默认情况下，OpenClaw使用`~/.openclaw/workspace`作为代理工作区，并将在设置/首次代理运行时自动创建它（加上启动器`AGENTS.md`，`SOUL.md`，`TOOLS.md`，`IDENTITY.md`，`USER.md`）。只有当工作区是全新的时才会创建`BOOTSTRAP.md`（删除后不应再次出现）。

提示：将此文件夹视为OpenClaw的“记忆”，并将其作为一个git仓库（理想情况下是私有的），以便备份您的`AGENTS.md` + 内存文件。如果已安装git，全新工作区会自动初始化。

```bash
openclaw setup
```

完整的工作区布局 + 备份指南：[代理工作区](/concepts/agent-workspace)
内存工作流程：[内存](/concepts/memory)

可选：使用`agents.defaults.workspace`选择不同的工作区（支持`~`）。

```json5
{
  agent: {
    workspace: "~/.openclaw/workspace",
  },
}
```

如果您已经从仓库部署自己的工作区文件，可以完全禁用引导文件创建：

```json5
{
  agent: {
    skipBootstrap: true,
  },
}
```

## 将其变成“助手”的配置

OpenClaw默认提供一个良好的助手设置，但您通常需要调整：

- 代理/指令中的个性`SOUL.md`
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
    // Start with 0; enable later.
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

## 会话和记忆

- 会话文件：`~/.openclaw/agents/<agentId>/sessions/{{SessionId}}.jsonl`
- 会话元数据（令牌使用情况、最后路由等）：`~/.openclaw/agents/<agentId>/sessions/sessions.json`（旧版：`~/.openclaw/sessions/sessions.json`）
- `/new` 或 `/reset` 为该聊天启动一个新的会话（可通过`resetTriggers`配置）。如果单独发送，代理会回复简短的问候以确认重置。
- `/compact [instructions]` 压缩会话上下文并报告剩余的上下文预算。

## 心跳（主动模式）

默认情况下，OpenClaw每30分钟运行一次心跳，提示如下：
`Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`
设置`agents.defaults.heartbeat.every: "0m"`以禁用。

- 如果`HEARTBEAT.md`存在但实际上是空的（只有空白行和markdown标题如`# Heading`），OpenClaw会跳过心跳运行以节省API调用。
- 如果文件丢失，心跳仍然运行，模型决定要做什么。
- 如果代理回复`HEARTBEAT_OK`（可选带有简短填充；参见`agents.defaults.heartbeat.ackMaxChars`），OpenClaw会抑制该心跳的外发传递。
- 心跳运行完整的代理轮次 — 更短的时间间隔会消耗更多令牌。

```json5
{
  agent: {
    heartbeat: { every: "30m" },
  },
}
```

## 媒体输入和输出

传入附件（图片/音频/文档）可以通过模板呈现给您的命令：

- `{{MediaPath}}`（本地临时文件路径）
- `{{MediaUrl}}`（伪URL）
- `{{Transcript}}`（如果启用了音频转录）

代理发出的传出附件：在单独一行中包含`MEDIA:<path-or-url>`（无空格）。示例：

```
Here’s the screenshot.
MEDIA:https://example.com/screenshot.png
```

OpenClaw提取这些文件并将其作为媒体与文本一起发送。

## 操作检查清单

```bash
openclaw status          # local status (creds, sessions, queued events)
openclaw status --all    # full diagnosis (read-only, pasteable)
openclaw status --deep   # adds gateway health probes (Telegram + Discord)
openclaw health --json   # gateway health snapshot (WS)
```

日志位于`/tmp/openclaw/`下（默认：`openclaw-YYYY-MM-DD.log`）。

## 下一步

- WebChat：[WebChat](/web/webchat)
- 网关操作：[网关运行手册](/gateway)
- Cron + 唤醒：[Cron作业](/automation/cron-jobs)
- macOS菜单栏伴侣：[OpenClaw macOS应用](/platforms/macos)
- iOS节点应用：[iOS应用](/platforms/ios)
- Android节点应用：[Android应用](/platforms/android)
- Windows状态：[Windows (WSL2)](/platforms/windows)
- Linux状态：[Linux应用](/platforms/linux)
- 安全性：[安全性](/gateway/security)