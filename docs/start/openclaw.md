---
summary: "End-to-end guide for running OpenClaw as a personal assistant with safety cautions"
read_when:
  - Onboarding a new assistant instance
  - Reviewing safety/permission implications
title: "Personal Assistant Setup"
---
# 使用 OpenClaw 构建个人助理

OpenClaw 是一个 WhatsApp + Telegram + Discord + iMessage 网关，适用于 **Pi** 代理。插件支持 Mattermost。本指南是“个人助理”设置：一个专用的 WhatsApp 号码，表现得像你的始终在线代理。

## ⚠️ 安全第一

你将代理置于以下位置：

- 在你的机器上运行命令（取决于你的 Pi 工具设置）
- 读取/写入工作区中的文件
- 通过 WhatsApp/Telegram/Discord/Mattermost（插件）发送消息

从保守开始：

- 始终设置 `channels.whatsapp.allowFrom`（永远不要在个人 Mac 上运行开放到世界的设置）。
- 为助手使用一个专用的 WhatsApp 号码。
- 心跳现在默认每 30 分钟一次。在信任设置之前通过设置 `agents.defaults.heartbeat.every: "0m"` 禁用。

## 先决条件

- 已安装并注册 OpenClaw — 如果尚未完成，请参阅 [入门](/start/getting-started)
- 一个辅助电话号码（SIM/eSIM/预付费）用于助手

## 两手机设置（推荐）

你需要这个：

```mermaid
flowchart TB
    A["<b>Your Phone (personal)<br></b><br>Your WhatsApp<br>+1-555-YOU"] -- message --> B["<b>Second Phone (assistant)<br></b><br>Assistant WA<br>+1-555-ASSIST"]
    B -- linked via QR --> C["<b>Your Mac (openclaw)<br></b><br>Pi agent"]
```

如果你将个人 WhatsApp 链接到 OpenClaw，发给你的每条消息都会成为“代理输入”。这通常不是你想要的。

## 5 分钟快速入门

1. 配对 WhatsApp Web（显示 QR 码；用助手手机扫描）：

```bash
openclaw channels login
```

2. 启动网关（让它一直运行）：

```bash
openclaw gateway --port 18789
```

3. 在 `~/.openclaw/openclaw.json` 中放入最小配置：

```json5
{
  channels: { whatsapp: { allowFrom: ["+15555550123"] } },
}
```

现在从你的白名单手机向助手号码发送消息。

当注册完成后，我们会自动打开仪表板并打印一个干净的（非标记化的）链接。如果提示需要身份验证，请将 `gateway.auth.token` 中的令牌粘贴到控制 UI 设置中。要稍后重新打开：`openclaw dashboard`。

## 给代理一个工作区（AGENTS）

OpenClaw 从其工作区目录读取操作指令和“记忆”。

默认情况下，OpenClaw 使用 `~/.openclaw/workspace` 作为代理工作区，并会在设置/首次代理运行时自动创建它（加上启动器 `AGENTS.md`，`SOUL.md`，`TOOLS.md`，`IDENTITY.md`，`USER.md`，`HEARTBEAT.md`）。`BOOTSTRAP.md` 仅在工作区全新创建时创建（删除后不应再次出现）。`MEMORY.md` 是可选的（不会自动创建）；当存在时，它会加载到正常会话中。子代理会话仅注入 `AGENTS.md` 和 `TOOLS.md`。

提示：将此文件夹视为 OpenClaw 的“记忆”，并将其作为一个 git 仓库（理想情况下是私有的），以便备份你的 `AGENTS.md` + 记忆文件。如果已安装 git，全新工作区会自动初始化。

```bash
openclaw setup
```

完整的工作区布局 + 备份指南：[代理工作区](/concepts/agent-workspace)
记忆工作流程：[记忆](/concepts/memory)

可选：使用 `agents.defaults.workspace` 选择不同的工作区（支持 `~`）。

```json5
{
  agent: {
    workspace: "~/.openclaw/workspace",
  },
}
```

如果你已经从仓库分发自己的工作区文件，可以完全禁用引导文件创建：

```json5
{
  agent: {
    skipBootstrap: true,
  },
}
```

## 将其转变为“一个助理”的配置

OpenClaw 默认提供一个良好的助理设置，但你通常需要调整：

- 代理/指令中的 `SOUL.md`
- 思考默认值（如果需要）
- 心跳（一旦你信任它）

示例：

```json5
{
  logging: { level: "info" },
  agent: {
    model: "anthropic/claude-opus-4-6",
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
- `/new` 或 `/reset` 为该聊天启动一个新的会话（可通过 `resetTriggers` 配置）。如果单独发送，代理会回复一个简短的问候以确认重置。
- `/compact [instructions]` 压缩会话上下文并报告剩余的上下文预算。

## 心跳（主动模式）

默认情况下，OpenClaw 每 30 分钟运行一次心跳，提示如下：
`Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`
设置 `agents.defaults.heartbeat.every: "0m"` 以禁用。

- 如果 `HEARTBEAT.md` 存在但实际上是空的（只有空白行和 markdown 标题如 `# Heading`），OpenClaw 跳过心跳运行以节省 API 调用。
- 如果文件丢失，心跳仍然运行，模型决定要做什么。
- 如果代理回复 `HEARTBEAT_OK`（可选带有简短填充；见 `agents.defaults.heartbeat.ackMaxChars`），OpenClaw 抑制该心跳的外发传递。
- 心跳运行完整的代理轮次 — 更短的时间间隔会消耗更多令牌。

```json5
{
  agent: {
    heartbeat: { every: "30m" },
  },
}
```

## 媒体输入和输出

传入附件（图片/音频/文档）可以通过模板呈现给你的命令：

- `{{MediaPath}}`（本地临时文件路径）
- `{{MediaUrl}}`（伪 URL）
- `{{Transcript}}`（如果启用了音频转录）

代理发出的传出附件：在单独的一行中包含 `MEDIA:<path-or-url>`（无空格）。示例：

```
Here’s the screenshot.
MEDIA:https://example.com/screenshot.png
```

OpenClaw 提取这些文件并将其作为媒体与文本一起发送。

## 操作检查清单

```bash
openclaw status          # local status (creds, sessions, queued events)
openclaw status --all    # full diagnosis (read-only, pasteable)
openclaw status --deep   # adds gateway health probes (Telegram + Discord)
openclaw health --json   # gateway health snapshot (WS)
```

日志位于 `/tmp/openclaw/` 下（默认：`openclaw-YYYY-MM-DD.log`）。

## 下一步

- WebChat：[WebChat](/web/webchat)
- 网关操作：[网关运行手册](/gateway)
- Cron + 唤醒：[Cron 作业](/automation/cron-jobs)
- macOS 菜单栏伴侣：[OpenClaw macOS 应用](/platforms/macos)
- iOS 节点应用：[iOS 应用](/platforms/ios)
- Android 节点应用：[Android 应用](/platforms/android)
- Windows 状态：[Windows (WSL2)](/platforms/windows)
- Linux 状态：[Linux 应用](/platforms/linux)
- 安全性：[安全性](/gateway/security)