---
description: Real-world OpenClaw projects from the community
summary: 社区构建的基于 OpenClaw 的项目和集成
title: 案例展示
x-i18n:
  generated_at: "2026-02-03T10:11:36Z"
  model: claude-opus-4-6
  provider: pi
  source_hash: b3460f6a7b9948799a6082fee90fa8e5ac1d43e34872aea51ba431813dcead7a
  source_path: start/showcase.md
  workflow: 15
---
# 案例展示

来自社区的真实项目。看看大家正在用 OpenClaw 构建什么。

<Info>
**想要展示你的项目？** 在 [Discord 的 #showcase 频道](https://discord.gg/clawd) 分享或在 [X 上 @openclaw](https://x.com/openclaw)。
</Info>

## 🎥 OpenClaw 实战演示

VelvetShark 的完整设置演练（28 分钟）。

<div
  style={{
    position: "relative",
    paddingBottom: "56.25%",
    height: 0,
    overflow: "hidden",
    borderRadius: 16,
  }}
>
  <iframe
    src="https://www.youtube-nocookie.com/embed/SaWSPZoPX34"
    title="OpenClaw: The self-hosted AI that Siri should have been (Full setup)"
    style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
    frameBorder="0"
    loading="lazy"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

[在 YouTube 上观看](https://www.youtube.com/watch?v=SaWSPZoPX34)

<div
  style={{
    position: "relative",
    paddingBottom: "56.25%",
    height: 0,
    overflow: "hidden",
    borderRadius: 16,
  }}
>
  <iframe
    src="https://www.youtube-nocookie.com/embed/mMSKQvlmFuQ"
    title="OpenClaw showcase video"
    style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
    frameBorder="0"
    loading="lazy"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

[在 YouTube 上观看](https://www.youtube.com/watch?v=mMSKQvlmFuQ)

<div
  style={{
    position: "relative",
    paddingBottom: "56.25%",
    height: 0,
    overflow: "hidden",
    borderRadius: 16,
  }}
>
  <iframe
    src="https://www.youtube-nocookie.com/embed/5kkIJNUGFho"
    title="OpenClaw community showcase"
    style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
    frameBorder="0"
    loading="lazy"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowFullScreen
  />
</div>

[在 YouTube 上观看](https://www.youtube.com/watch?v=5kkIJNUGFho)

## 🤖 自动化与工作流

<CardGroup cols={2}>

<Card title="PR 审查 → Telegram 反馈" icon="code-pull-request" href="https://x.com/i/status/2010878524543131691">
  **@bangnokia** • `review` `github` `telegram`

OpenCode 完成更改 → 打开 PR → OpenClaw 审查差异并在 Telegram 中回复"小建议"加上明确的合并决定（包括需要先应用的关键修复）。

  <img src="/assets/showcase/pr-review-telegram.jpg" alt="OpenClaw PR review feedback delivered in Telegram" />
</Card>

<Card title="几分钟内创建酒窖 Skill" icon="wine-glass" href="https://x.com/i/status/2010916352454791216">
  **@prades_maxime** • `skills` `local` `csv`

向"Robby"（@openclaw）请求一个本地酒窖 skill。它请求一个示例 CSV 导出 + 存储位置，然后快速构建/测试该 skill（示例中有 962 瓶酒）。

  <img src="/assets/showcase/wine-cellar-skill.jpg" alt="OpenClaw building a local wine cellar skill from CSV" />
</Card>

<Card title="Tesco 购物自动驾驶" icon="cart-shopping" href="https://x.com/i/status/2009724862470689131">
  **@marchattonhere** • `automation` `browser` `shopping`

每周餐饮计划 → 常购商品 → 预订配送时段 → 确认订单。无需 API，仅使用浏览器控制。

  <img src="/assets/showcase/tesco-shop.jpg" alt="Tesco shop automation via chat" />
</Card>

<Card title="SNAG 截图转 Markdown" icon="scissors" href="https://github.com/am-will/snag">
  **@am-will** • `devtools` `screenshots` `markdown`

快捷键选择屏幕区域 → Gemini 视觉 → 即时 Markdown 到剪贴板。

  <img src="/assets/showcase/snag.png" alt="SNAG screenshot-to-markdown tool" />
</Card>

<Card title="Agents UI" icon="window-maximize" href="https://releaseflow.net/kitze/agents-ui">
  **@kitze** • `ui` `skills` `sync`

跨 Agents、Claude、Codex 和 OpenClaw 管理 skills/命令的桌面应用。

  <img src="/assets/showcase/agents-ui.jpg" alt="Agents UI app" />
</Card>

<Card title="Telegram 语音备忘录 (papla.media)" icon="microphone" href="https://papla.media/docs">
  **社区** • `voice` `tts` `telegram`

封装 papla.media TTS 并将结果作为 Telegram 语音备忘录发送（无烦人的自动播放）。

  <img src="/assets/showcase/papla-tts.jpg" alt="Telegram voice note output from TTS" />
</Card>

<Card title="CodexMonitor" icon="eye" href="https://clawhub.com/odrobnik/codexmonitor">
  **@odrobnik** • `devtools` `codex` `brew`

Homebrew 安装的助手工具，用于列出/检查/监视本地 OpenAI Codex 会话（CLI + VS Code）。

  <img src="/assets/showcase/codexmonitor.png" alt="CodexMonitor on ClawHub" />
</Card>

<Card title="Bambu 3D 打印机控制" icon="print" href="https://clawhub.com/tobiasbischoff/bambu-cli">
  **@tobiasbischoff** • `hardware` `3d-printing` `skill`

控制和排查 BambuLab 打印机：状态、任务、摄像头、AMS、校准等。

  <img src="/assets/showcase/bambu-cli.png" alt="Bambu CLI skill on ClawHub" />
</Card>

<Card title="维也纳交通 (Wiener Linien)" icon="train" href="https://clawhub.com/hjanuschka/wienerlinien">
  **@hjanuschka** • `travel` `transport` `skill`

维也纳公共交通的实时发车时间、中断信息、电梯状态和路线规划。

  <img src="/assets/showcase/wienerlinien.png" alt="Wiener Linien skill on ClawHub" />
</Card>

<Card title="ParentPay 学校餐食" icon="utensils" href="#">
  **@George5562** • `automation` `browser` `parenting`

通过 ParentPay 自动预订英国学校餐食。使用鼠标坐标实现可靠的表格单元格点击。
</Card>

<Card title="R2 上传 (Send Me My Files)" icon="cloud-arrow-up" href="https://clawhub.com/skills/r2-upload">
  **@julianengel** • `files` `r2` `presigned-urls`

上传到 Cloudflare R2/S3 并生成安全的预签名下载链接。非常适合远程 OpenClaw 实例。
</Card>

<Card title="通过 Telegram 开发 iOS 应用" icon="mobile" href="#">
  **@coard** • `ios` `xcode` `testflight`

构建了一个完整的带有地图和语音录制功能的 iOS 应用，完全通过 Telegram 聊天部署到 TestFlight。

  <img src="/assets/showcase/ios-testflight.jpg" alt="iOS app on TestFlight" />
</Card>

<Card title="Oura 戒指健康助手" icon="heart-pulse" href="#">
  **@AS** • `health` `oura` `calendar`

个人 AI 健康助手，将 Oura 戒指数据与日历、预约和健身房计划集成。

  <img src="/assets/showcase/oura-health.png" alt="Oura ring health assistant" />
</Card>
<Card title="Kev 的梦之队 (14+ 智能体)" icon="robot" href="https://github.com/adam91holt/orchestrated-ai-articles">
  **@adam91holt** • `multi-agent` `orchestration` `architecture` `manifesto`

一个 Gateway 网关下的 14+ 智能体，Opus 4.5 编排器将任务委派给 Codex 工作者。全面的[技术文章](https://github.com/adam91holt/orchestrated-ai-articles)涵盖梦之队阵容、模型选择、沙箱隔离、webhook、心跳和委派流程。用于智能体沙箱隔离的 [Clawdspace](https://github.com/adam91holt/clawdspace)。[博客文章](https://adams-ai-journey.ghost.io/2026-the-year-of-the-orchestrator/)。
</Card>

<Card title="Linear CLI" icon="terminal" href="https://github.com/Finesssee/linear-cli">
  **@NessZerra** • `devtools` `linear` `cli` `issues`

与智能体工作流（Claude Code、OpenClaw）集成的 Linear CLI。从终端管理问题、项目和工作流。首个外部 PR 已合并！
</Card>

<Card title="Beeper CLI" icon="message" href="https://github.com/blqke/beepcli">
  **@jules** • `messaging` `beeper` `cli` `automation`

通过 Beeper Desktop 读取、发送和归档消息。使用 Beeper 本地 MCP API，让智能体可以在一个地方管理你的所有聊天（iMessage、WhatsApp 等）。
</Card>

</CardGroup>

## 🧠 知识与记忆

<CardGroup cols={2}>

<Card title="xuezh 中文学习" icon="language" href="https://github.com/joshp123/xuezh">
  **@joshp123** • `learning` `voice` `skill`
  
  通过 OpenClaw 实现带有发音反馈和学习流程的中文学习引擎。
  
  <img src="/assets/showcase/xuezh-pronunciation.jpeg" alt="xuezh pronunciation feedback" />
</Card>

<Card title="WhatsApp 记忆库" icon="vault">
  **社区** • `memory` `transcription` `indexing`
  
  导入完整的 WhatsApp 导出，转录 1k+ 条语音备忘录，与 git 日志交叉检查，输出链接的 markdown 报告。
</Card>

<Card title="Karakeep 语义搜索" icon="magnifying-glass" href="https://github.com/jamesbrooksco/karakeep-semantic-search">
  **@jamesbrooksco** • `search` `vector` `bookmarks`
  
  使用 Qdrant + OpenAI/Ollama embeddings 为 Karakeep 书签添加向量搜索。
</Card>

<Card title="Inside-Out-2 记忆" icon="brain">
  **社区** • `memory` `beliefs` `self-model`
  
  独立的记忆管理器，将会话文件转化为记忆 → 信念 → 演化的自我模型。
</Card>

</CardGroup>

## 🎙️ 语音与电话

<CardGroup cols={2}>

<Card title="Clawdia 电话桥接" icon="phone" href="https://github.com/alejandroOPI/clawdia-bridge">
  **@alejandroOPI** • `voice` `vapi` `bridge`
  
  Vapi 语音助手 ↔ OpenClaw HTTP 桥接。与你的智能体进行近实时电话通话。
</Card>

<Card title="OpenRouter 转录" icon="microphone" href="https://clawhub.com/obviyus/openrouter-transcribe">
  **@obviyus** • `transcription` `multilingual` `skill`

通过 OpenRouter（Gemini 等）进行多语言音频转录。可在 ClawHub 获取。
</Card>

</CardGroup>

## 🏗️ 基础设施与部署

<CardGroup cols={2}>

<Card title="Home Assistant 插件" icon="home" href="https://github.com/ngutman/openclaw-ha-addon">
  **@ngutman** • `homeassistant` `docker` `raspberry-pi`
  
  在 Home Assistant OS 上运行的 OpenClaw Gateway 网关，支持 SSH 隧道和持久状态。
</Card>

<Card title="Home Assistant Skill" icon="toggle-on" href="https://clawhub.com/skills/homeassistant">
  **ClawHub** • `homeassistant` `skill` `automation`
  
  通过自然语言控制和自动化 Home Assistant 设备。
</Card>

<Card title="Nix 打包" icon="snowflake" href="https://github.com/openclaw/nix-openclaw">
  **@openclaw** • `nix` `packaging` `deployment`
  
  开箱即用的 nixified OpenClaw 配置，用于可复现的部署。
</Card>

<Card title="CalDAV 日历" icon="calendar" href="https://clawhub.com/skills/caldav-calendar">
  **ClawHub** • `calendar` `caldav` `skill`
  
  使用 khal/vdirsyncer 的日历 skill。自托管日历集成。
</Card>

</CardGroup>

## 🏠 家居与硬件

<CardGroup cols={2}>

<Card title="GoHome 自动化" icon="house-signal" href="https://github.com/joshp123/gohome">
  **@joshp123** • `home` `nix` `grafana`
  
  Nix 原生家庭自动化，以 OpenClaw 作为界面，加上漂亮的 Grafana 仪表板。
  
  <img src="/assets/showcase/gohome-g