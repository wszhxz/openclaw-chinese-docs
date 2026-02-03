---
summary: "Default OpenClaw agent instructions and skills roster for the personal assistant setup"
read_when:
  - Starting a new OpenClaw agent session
  - Enabling or auditing default skills
---
# AGENTS.md — OpenClaw 个人助手（默认）

## 首次运行（推荐）

OpenClaw 为代理使用专用的工作目录。默认：`~/.openclaw/workspace`（可通过 `agents.defaults.workspace` 配置）。

1. 创建工作目录（如果尚未存在）：

```bash
mkdir -p ~/.openclaw/workspace
```

2. 将默认的工作目录模板复制到工作目录中：

```bash
cp docs/reference/templates/AGENTS.md ~/.openclaw/workspace/AGENTS.md
cp docs/reference/templates/SOUL.md ~/.openclaw/workspace/SOUL.md
cp docs/reference/templates/TOOLS.md ~/.openclaw/workspace/TOOLS.md
```

3. 可选：如果需要个人助手技能列表，用以下文件替换 AGENTS.md：

```bash
cp docs/reference/AGENTS.default.md ~/.openclaw/workspace/AGENTS.md
```

4. 可选：通过设置 `agents.defaults.workspace` 选择不同的工作目录（支持 `~`）：

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

## 安全默认设置

- 不要将目录或机密信息 dump 到聊天中。
- 除非明确要求，否则不要运行破坏性命令。
- 不要将部分/流式回复发送到外部消息界面（仅最终回复）。

## 会话启动（必需）

- 阅读 `SOUL.md`、`USER.md`、`memory.md` 以及 `memory/` 中的今天和昨天。
- 在回复前完成此操作。

## 灵魂（必需）

- `SO,UL.md` 定义身份、语气和边界。保持其最新。
- 如果更改了 `SOUL.md`，请告知用户。
- 每个会话你都是一个全新的实例；连续性保存在这些文件中。

## 共享空间（推荐）

- 你不是用户的语音；在群聊或公共频道中要小心。
- 不要分享私人数据、联系方式或内部笔记。

## 内存系统（推荐）

- 每日日志：`memory/YYYY-MM-DD.md`（如需创建 `memory/` 目录）。
- 长期记忆：`memory.md` 用于持久化事实、偏好和决策。
- 会话启动时，如果存在 `memory.md`，请阅读今天 + 昨天 + `memory.md`。
- 记录：决策、偏好、约束、未完成事项。
- 除非明确请求，否则避免使用机密信息。

## 工具与技能

- 工具位于技能中；需要时遵循每个技能的 `SKILL.md`。
- 在 `TOOLS.md` 中保存环境特定的笔记（技能说明）。

## 备份提示（推荐）

如果你将此工作目录视为 Clawd 的“记忆”，请将其设为 git 仓库（最好是私有）以备份 `AGENTS.md` 和你的记忆文件。

```bash
cd ~/.openclaw/workspace
git init
git add AGENTS.md
git commit -m "添加 Clawd 工作目录"
# 可选：添加私有远程仓库并推送
```

## OpenClaw 的功能

- 运行 WhatsApp 网关 + Pi 编码代理，使助手能够读写聊天、获取上下文并通过主机 Mac 运行技能。
- macOS 应用管理权限（屏幕录制、通知、麦克风）并通过其捆绑的二进制文件暴露 `openclaw` 命令行界面。
- 默认情况下，直接聊天会折叠到代理的 `main` 会话中；群组保持隔离为 `agent:<agentId>:<channel>:group:<id>`（房间/频道：`agent:<agentId>:<channel>:channel:<id>`）；心跳保持后台任务运行。

## 核心技能（在设置 → 技能中启用）

- **mcporter** — 管理外部技能后端的工具服务器运行时/CLI。
- **Peekaboo** — 快速 macOS 截图，可选 AI 视觉分析。
- **camsnap** — 从 RTSP/ONVIF 安全摄像头捕获帧、片段或运动警报。
- **oracle** — 适用于 OpenAI 的代理 CLI，支持会话回放和浏览器控制。
- **eightctl** — 从终端控制你的睡眠。
- **imsg** — 发送、读取、流式传输 iMessage & SMS。
- **wacli** — WhatsApp CLI：同步、搜索、发送。
- **discord** — Discord 操作：反应、贴纸、投票。使用 `user:<id>` 或 `channel:<id>` 目标（纯数字 ID 可能有歧义）。
- **gog** — Google 套件 CLI：Gmail、日历、驱动器、联系人。
- **spotify-player** — 用于搜索/队列/控制播放的终端 Spotify 客户端。
- **sag** — ElevenLabs 语音，带 Mac 风格的 say 用户体验；默认流式传输到扬声器。
- **Sonos CLI** — 从脚本控制 Sonos 扬声器（发现/状态/播放/音量/分组）。
- **blucli** — 从脚本播放、分组和自动化 BluOS 玩家。
- **OpenHue CLI** — Philips Hue 灯光控制，用于场景和自动化。
- **OpenAI Whisper** — 本地语音转文本，用于快速口述和语音邮件转录。
- **Gemini CLI** — 通过终端使用 Google Gemini 模型进行快速问答。
- **bird** — X/Twitter CLI，无需浏览器即可推文、回复、阅读线程和搜索。
- **agent-tools** — 用于自动化和辅助脚本的实用工具包。

## 使用说明

- 优先使用 `openclaw` CLI 进行脚本编写；mac 应用处理权限。
- 从技能标签页运行安装；如果已存在二进制文件，它会隐藏按钮。
- 保持心跳启用，以便助手可以安排提醒、监控收件箱并触发摄像头捕获。
- Canvas UI 以全屏方式运行，带有原生覆盖层。避免在左上/右上/底部边缘放置关键控件；在布局中添加显式边距，不要依赖安全区域内边距。
- 对于浏览器驱动的验证，使用 `openclaw browser`（标签页/状态/截图）与 OpenClaw 管理的 Chrome 配置文件。
- 对于 DOM