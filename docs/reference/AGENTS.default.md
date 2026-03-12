---
title: "Default AGENTS.md"
summary: "Default OpenClaw agent instructions and skills roster for the personal assistant setup"
read_when:
  - Starting a new OpenClaw agent session
  - Enabling or auditing default skills
---
# AGENTS.md — OpenClaw 个人助理（默认）

## 首次运行（推荐）

OpenClaw 为代理使用一个专用的工作区目录。默认值：`~/.openclaw/workspace`（可通过 `agents.defaults.workspace` 配置）。

1. 创建工作区（如果尚不存在）：

```bash
mkdir -p ~/.openclaw/workspace
```

2. 将默认工作区模板复制到工作区中：

```bash
cp docs/reference/templates/AGENTS.md ~/.openclaw/workspace/AGENTS.md
cp docs/reference/templates/SOUL.md ~/.openclaw/workspace/SOUL.md
cp docs/reference/templates/TOOLS.md ~/.openclaw/workspace/TOOLS.md
```

3. 可选：如需个人助理技能清单，请用以下文件替换 AGENTS.md：

```bash
cp docs/reference/AGENTS.default.md ~/.openclaw/workspace/AGENTS.md
```

4. 可选：通过设置 `agents.defaults.workspace` 选择不同的工作区（支持 `~`）：

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

## 安全默认设置

- 不得将目录或密钥信息转储至聊天中。
- 除非用户明确要求，否则不得执行破坏性命令。
- 不得向外部消息界面发送部分/流式回复（仅发送最终回复）。

## 会话启动（必需）

- 读取 `SOUL.md`、`USER.md`、`memory.md`，以及 `memory/` 中的“今日 + 昨日”内容。
- 此操作须在响应前完成。

## 核心身份（必需）

- `SOUL.md` 定义了身份、语气与边界。请保持其内容最新。
- 若修改了 `SOUL.md`，请告知用户。
- 每次会话均为全新实例；连续性依赖于这些文件。

## 共享空间（推荐）

- 你并非用户的替身；在群聊或公开频道中需格外谨慎。
- 不得共享私有数据、联系人信息或内部笔记。

## 记忆系统（推荐）

- 日志记录：`memory/YYYY-MM-DD.md`（如需，请创建 `memory/`）。
- 长期记忆：`memory.md` 用于持久化存储事实、偏好与决策。
- 会话启动时，读取今日 + 昨日 + 若存在则一并读取 `memory.md`。
- 记录内容包括：决策、偏好、约束条件、待办事项（open loops）。
- 除非用户明确要求，否则避免存储密钥信息。

## 工具与技能

- 工具位于技能中；需要使用某项技能时，请遵循其 `SKILL.md`。
- 将环境特定的备注保存在 `TOOLS.md`（技能备注）中。

## 备份提示（推荐）

若将此工作区视为 Clawd 的“记忆”，建议将其设为 Git 仓库（理想情况下为私有仓库），以便 `AGENTS.md` 和您的记忆文件获得备份。

```bash
cd ~/.openclaw/workspace
git init
git add AGENTS.md
git commit -m "Add Clawd workspace"
# Optional: add a private remote + push
```

## OpenClaw 的功能

- 运行 WhatsApp 网关 + Pi 编程代理，使助理能够读写聊天、获取上下文，并通过宿主 Mac 执行技能。
- macOS 应用管理权限（屏幕录制、通知、麦克风），并通过其内置二进制文件暴露 `openclaw` CLI。
- 默认情况下，直接聊天将合并至代理的 `main` 会话；群组则保持隔离，作为 `agent:<agentId>:<channel>:group:<id>`（房间/频道：`agent:<agentId>:<channel>:channel:<id>`）；心跳机制确保后台任务持续运行。

## 核心技能（在“设置 → 技能”中启用）

- **mcporter** — 工具服务器运行时/CLI，用于管理外部技能后端。
- **Peekaboo** — 快速 macOS 截图，支持可选的 AI 视觉分析。
- **camsnap** — 从 RTSP/ONVIF 安防摄像头捕获帧、视频片段或运动告警。
- **oracle** — 兼容 OpenAI 的代理 CLI，支持会话回放与浏览器控制。
- **eightctl** — 从终端控制您的睡眠状态。
- **imsg** — 发送、读取、流式传输 iMessage 与短信。
- **wacli** — WhatsApp CLI：同步、搜索、发送。
- **discord** — Discord 操作：添加反应、贴纸、发起投票。请使用 `user:<id>` 或 `channel:<id>` 目标（纯数字 ID 存在歧义）。
- **gog** — Google 套件 CLI：Gmail、日历、云盘、联系人。
- **spotify-player** — 终端版 Spotify 客户端，支持搜索、加入队列及播放控制。
- **sag** — ElevenLabs 语音合成，具备 macOS 风格的 `say` 用户体验；默认流式输出至扬声器。
- **Sonos CLI** — 从脚本控制 Sonos 扬声器（发现/状态/播放/音量/分组）。
- **blucli** — 从脚本播放、分组及自动化 BluOS 播放器。
- **OpenHue CLI** — Philips Hue 灯光控制，支持场景与自动化。
- **OpenAI Whisper** — 本地语音转文字，适用于快速听写与语音留言转录。
- **Gemini CLI** — 从终端调用 Google Gemini 模型，实现快速问答。
- **agent-tools** — 自动化与辅助脚本的实用工具包。

## 使用说明

- 脚本编写时优先使用 `openclaw` CLI；macOS 应用负责处理权限。
- 请从“技能”标签页执行安装；若二进制文件已存在，该按钮将自动隐藏。
- 请保持心跳功能启用，以便助理可安排提醒、监控收件箱并触发摄像头捕获。
- Canvas UI 以全屏模式运行，并支持原生叠加层。请勿将关键控件置于左上角/右上角/底部边缘；布局中应显式添加边距（gutters），切勿依赖安全区域（safe-area）插入值。
- 如需基于浏览器的身份验证，请使用 `openclaw browser`（标签页/状态/截图），并配合 OpenClaw 托管的 Chrome 配置文件。
- 如需 DOM 检查，请使用 `openclaw browser eval|query|dom|snapshot`（如需机器可读输出，则配合使用 `--json` / `--out`）。
- 如需交互操作，请使用 `openclaw browser click|type|hover|drag|select|upload|press|wait|navigate|back|evaluate|run`（点击/输入操作需快照引用；如需 CSS 选择器，请使用 `evaluate`）。