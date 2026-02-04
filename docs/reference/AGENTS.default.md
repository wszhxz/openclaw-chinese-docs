---
summary: "Default OpenClaw agent instructions and skills roster for the personal assistant setup"
read_when:
  - Starting a new OpenClaw agent session
  - Enabling or auditing default skills
---
# AGENTS.md — OpenClaw Personal Assistant (default)

## 首次运行（推荐）

OpenClaw 使用专用的工作区目录来存放代理文件。默认值: `~/.openclaw/workspace` （可通过 `agents.defaults.workspace` 进行配置）。

1. 创建工作区（如果它尚不存在）：

```bash
mkdir -p ~/.openclaw/workspace
```

2. 将默认的工作区模板复制到工作区：

```bash
cp docs/reference/templates/AGENTS.md ~/.openclaw/workspace/AGENTS.md
cp docs/reference/templates/SOUL.md ~/.openclaw/workspace/SOUL.md
cp docs/reference/templates/TOOLS.md ~/.openclaw/workspace/TOOLS.md
```

3. 可选：如果你想使用个人助理技能列表，请将 AGENTS.md 替换为此文件：

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

- 不要将目录或机密信息转储到聊天中。
- 除非明确要求，否则不要运行破坏性命令。
- 不要向外部消息平台发送部分或流式回复（仅发送最终回复）。

## 会话开始（必需）

- 在响应之前，阅读 `SOUL.md`，`USER.md`，`memory.md`，以及 `memory/` 中的今天和昨天的内容。

## 灵魂（必需）

- `SOUL.md` 定义身份、语气和界限。保持其最新。
- 如果更改了 `SOUL.md`，请告知用户。
- 每个会话你都是一个新实例；连续性存在于这些文件中。

## 共享空间（推荐）

- 你不是用户的代言人；在群聊或公共频道中要小心。
- 不要分享私人数据、联系信息或内部笔记。

## 记忆系统（推荐）

- 日志记录：`memory/YYYY-MM-DD.md`（如有需要创建 `memory/`）。
- 长期记忆：`memory.md` 用于持久的事实、偏好和决策。
- 在会话开始时，阅读今天 + 昨天 + 如果存在则读取 `memory.md`。
- 捕获：决策、偏好、约束、开放循环。
- 除非明确请求，否则避免机密信息。

## 工具与技能

- 工具位于技能中；需要时遵循每个技能的 `SKILL.md`。
- 将特定于环境的笔记保存在 `TOOLS.md`（技能笔记）中。

## 备份提示（推荐）

如果你将此工作区视为 Clawd 的“记忆”，请将其作为 git 仓库（最好是私有的），以便备份 `AGENTS.md` 和你的记忆文件。

```bash
cd ~/.openclaw/workspace
git init
git add AGENTS.md
git commit -m "Add Clawd workspace"
# Optional: add a private remote + push
```

## OpenClaw 的功能

- 运行 WhatsApp 网关 + Pi 编码代理，使助手可以读写聊天、获取上下文并通过主机 Mac 运行技能。
- macOS 应用程序管理权限（屏幕录制、通知、麦克风）并通过其捆绑的二进制文件公开 `openclaw` CLI。
- 默认情况下，直接聊天合并到代理的 `main` 会话中；群组保持隔离作为 `agent:<agentId>:<channel>:group:<id>`（房间/频道：`agent:<agentId>:<channel>:channel:<id>`）；心跳保持后台任务活跃。

## 核心技能（在 设置 → 技能 中启用）

- **mcporter** — 用于管理外部技能后端的工具服务器运行时/CLI。
- **Peekaboo** — 带有可选 AI 视觉分析的快速 macOS 截图。
- **camsnap** — 从 RTSP/ONVIF 安全摄像头捕获帧、片段或运动警报。
- **oracle** — 准备好用于 OpenAI 的代理 CLI，带有会话重播和浏览器控制。
- **eightctl** — 从终端控制睡眠。
- **imsg** — 发送、读取、流式传输 iMessage 和 SMS。
- **wacli** — WhatsApp CLI：同步、搜索、发送。
- **discord** — Discord 动作：反应、贴纸、投票。使用 `user:<id>` 或 `channel:<id>` 目标（纯数字 ID 是模糊的）。
- **gog** — Google Suite CLI：Gmail、日历、驱动器、联系人。
- **spotify-player** — 终端 Spotify 客户端用于搜索/排队/控制播放。
- **sag** — 带有 mac 风格 say UX 的 ElevenLabs 语音；默认流式传输到扬声器。
- **Sonos CLI** — 从脚本控制 Sonos 扬声器（发现/状态/播放/音量/分组）。
- **blucli** — 从脚本播放、分组和自动化 BluOS 播放器。
- **OpenHue CLI** — 用于场景和自动化的 Philips Hue 照明控制。
- **OpenAI Whisper** — 本地语音转文本用于快速速记和语音邮件转录。
- **Gemini CLI** — 从终端使用的 Google Gemini 模型进行快速问答。
- **bird** — X/Twitter CLI 用于发推文、回复、阅读线程和搜索而无需浏览器。
- **agent-tools** — 自动化和辅助脚本的实用工具包。

## 使用说明

- 脚本编写时优先使用 `openclaw` CLI；mac 应用程序处理权限。
- 从技能选项卡运行安装；如果已存在二进制文件，则隐藏按钮。
- 保持心跳开启，以便助手可以安排提醒、监控收件箱并触发相机捕获。
- 画布 UI 以全屏模式运行，并带有原生叠加层。避免在顶部左侧/右侧/底部边缘放置关键控件；在布局中添加显式的边距，不要依赖安全区域插入。
- 对于基于浏览器的验证，使用 `openclaw browser`（标签/状态/截图）与 OpenClaw 管理的 Chrome 配置文件。
- 对于 DOM 检查，使用 `openclaw browser eval|query|dom|snapshot`（以及需要机器输出时使用 `--json`/`--out`）。
- 对于交互，使用 `openclaw browser click|type|hover|drag|select|upload|press|wait|navigate|back|evaluate|run`（点击/类型需要快照引用；对于 CSS 选择器使用 `evaluate`）。