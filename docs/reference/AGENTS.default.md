---
summary: "Default OpenClaw agent instructions and skills roster for the personal assistant setup"
read_when:
  - Starting a new OpenClaw agent session
  - Enabling or auditing default skills
---
# AGENTS.md — OpenClaw 个人助手（默认）

## 首次运行（推荐）

OpenClaw 为代理使用专用的工作区目录。默认值：`~/.openclaw/workspace`（可通过 `agents.defaults.workspace` 配置）。

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

3. 可选：如果您想要个人助手技能列表，请用此文件替换 AGENTS.md：

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
- 不要向外部消息界面发送部分/流式回复（仅发送最终回复）。

## 会话开始（必需）

- 读取 `SOUL.md`、`USER.md`、`memory.md` 和 `memory/` 中的今天+昨天内容。
- 在回复之前执行此操作。

## 灵魂（必需）

- `SOUL.md` 定义身份、语调和边界。保持其最新状态。
- 如果您更改了 `SOUL.md`，请告知用户。
- 您在每个会话中都是一个新实例；连续性存在于这些文件中。

## 共享空间（推荐）

- 您不是用户的声音；在群聊或公共频道中小心行事。
- 不要分享私人数据、联系信息或内部笔记。

## 记忆系统（推荐）

- 每日日志：`memory/YYYY-MM-DD.md`（如需要创建 `memory/`）。
- 长期记忆：`memory.md` 用于持久化事实、偏好和决策。
- 会话开始时，读取今天 + 昨天 + 如存在则读取 `memory.md`。
- 捕获：决策、偏好、约束、未完成事项。
- 除非明确要求，否则避免机密信息。

## 工具与技能

- 工具存在于技能中；需要时遵循每个技能的 `SKILL.md`。
- 在 `TOOLS.md`（技能笔记）中保存环境特定的注释。

## 备份提示（推荐）

如果您将此工作区视为 Clawd 的"记忆"，请将其设为 git 仓库（理想情况下是私有的），以便 `AGENTS.md` 和您的记忆文件得到备份。

```bash
cd ~/.openclaw/workspace
git init
git add AGENTS.md
git commit -m "Add Clawd workspace"
# Optional: add a private remote + push
```

## OpenClaw 的功能

- 运行 WhatsApp 网关 + Pi 编码代理，使助手能够读写聊天、获取上下文并通过主机 Mac 运行技能。
- macOS 应用管理权限（屏幕录制、通知、麦克风）并通过其捆绑的二进制文件公开 `openclaw` CLI。
- 直接聊天默认折叠到代理的 `main` 会话中；群组保持隔离为 `agent:<agentId>:<channel>:group:<id>`（房间/频道：`agent:<agentId>:<channel>:channel:<id>`）；心跳保持后台任务活跃。

## 核心技能（在设置 → 技能中启用）

- **mcporter** — 用于管理外部技能后端的工具服务器运行时/CLI。
- **Peekaboo** — 快速 macOS 截图，可选 AI 视觉分析。
- **camsnap** — 从 RTSP/ONVIF 安防摄像头捕获帧、片段或运动警报。
- **oracle** — 准备就绪的 OpenAI 代理 CLI，具有会话重放和浏览器控制功能。
- **eightctl** — 从终端控制您的睡眠。
- **imsg** — 发送、读取、流式传输 iMessage 和 SMS。
- **wacli** — WhatsApp CLI：同步、搜索、发送。
- **discord** — Discord 操作：反应、贴纸、投票。使用 `user:<id>` 或 `channel:<id>` 目标（纯数字 ID 存在歧义）。
- **gog** — Google 套件 CLI：Gmail、Calendar、Drive、Contacts。
- **spotify-player** — 终端 Spotify 客户端，用于搜索/排队/控制播放。
- **sag** — ElevenLabs 语音，具有 mac 风格的 say 用户体验；默认流式传输到扬声器。
- **Sonos CLI** — 从脚本控制 Sonos 扬声器（发现/状态/播放/音量/分组）。
- **blucli** — 从脚本播放、分组和自动化 BluOS 播放器。
- **OpenHue CLI** — 飞利浦 Hue 照明控制，用于场景和自动化。
- **OpenAI Whisper** — 本地语音转文本，用于快速听写和语音邮件转录。
- **Gemini CLI** — 来自终端的 Google Gemini 模型，用于快速问答。
- **bird** — X/Twitter CLI，无需浏览器即可发推、回复、阅读话题和搜索。
- **agent-tools** — 用于自动化和辅助脚本的实用工具包。

## 使用说明

- 脚本编写时优先使用 `openclaw` CLI；mac 应用处理权限。
- 从技能标签页运行安装；如果已存在二进制文件，它会隐藏按钮。
- 保持心跳启用，以便助手可以安排提醒、监控收件箱并触发摄像头捕获。
- Canvas UI 以全屏运行，带有原生覆盖层。避免在左上角/右上角/底部边缘放置关键控件；在布局中添加明确的边距，不要依赖安全区域插入。
- 对于浏览器驱动的验证，使用 `openclaw browser`（标签页/状态/截图）和 OpenClaw 管理的 Chrome 配置文件。
- 对于 DOM 检查，使用 `openclaw browser eval|query|dom|snapshot`（以及需要机器输出时使用 `--json`/`--out`）。
- 对于交互，使用 `openclaw browser click|type|hover|drag|select|upload|press|wait|navigate|back|evaluate|run`（点击/输入需要快照引用；使用 `evaluate` 进行 CSS 选择器）。