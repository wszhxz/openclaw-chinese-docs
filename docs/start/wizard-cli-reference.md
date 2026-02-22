---
summary: "Complete reference for CLI onboarding flow, auth/model setup, outputs, and internals"
read_when:
  - You need detailed behavior for openclaw onboard
  - You are debugging onboarding results or integrating onboarding clients
title: "CLI Onboarding Reference"
sidebarTitle: "CLI reference"
---
# CLI 入门参考

本页面是 `openclaw onboard` 的完整参考。
简要指南，请参阅 [入门向导 (CLI)](/start/wizard)。

## 向导的功能

本地模式（默认）会引导您完成以下步骤：

- 模型和身份验证设置（OpenAI Code 订阅 OAuth、Anthropic API 密钥或设置令牌，以及 MiniMax、GLM、Moonshot 和 AI Gateway 选项）
- 工作区位置和引导文件
- 网关设置（端口、绑定、身份验证、tailscale）
- 渠道和提供商（Telegram、WhatsApp、Discord、Google Chat、Mattermost 插件、Signal）
- 守护进程安装（LaunchAgent 或 systemd 用户单元）
- 健康检查
- 技能设置

远程模式将此机器配置为连接到其他位置的网关。
它不会在远程主机上安装或修改任何内容。

## 本地流程详情

<Steps>
  <Step title="Existing config detection">
    - If __CODE_BLOCK_1__ exists, choose Keep, Modify, or Reset.
    - Re-running the wizard does not wipe anything unless you explicitly choose Reset (or pass __CODE_BLOCK_2__).
    - If config is invalid or contains legacy keys, the wizard stops and asks you to run __CODE_BLOCK_3__ before continuing.
    - Reset uses __CODE_BLOCK_4__ and offers scopes:
      - Config only
      - Config + credentials + sessions
      - Full reset (also removes workspace)
  </Step>
  <Step title="Model and auth">
    - Full option matrix is in [Auth and model options](#auth-and-model-options).
  </Step>
  <Step title="Workspace">
    - Default __CODE_BLOCK_5__ (configurable).
    - Seeds workspace files needed for first-run bootstrap ritual.
    - Workspace layout: [Agent workspace](/concepts/agent-workspace).
  </Step>
  <Step title="Gateway">
    - Prompts for port, bind, auth mode, and tailscale exposure.
    - Recommended: keep token auth enabled even for loopback so local WS clients must authenticate.
    - Disable auth only if you fully trust every local process.
    - Non-loopback binds still require auth.
  </Step>
  <Step title="Channels">
    - [WhatsApp](/channels/whatsapp): optional QR login
    - [Telegram](/channels/telegram): bot token
    - [Discord](/channels/discord): bot token
    - [Google Chat](/channels/googlechat): service account JSON + webhook audience
    - [Mattermost](/channels/mattermost) plugin: bot token + base URL
    - [Signal](/channels/signal): optional __CODE_BLOCK_6__ install + account config
    - [BlueBubbles](/channels/bluebubbles): recommended for iMessage; server URL + password + webhook
    - [iMessage](/channels/imessage): legacy __CODE_BLOCK_7__ CLI path + DB access
    - DM security: default is pairing. First DM sends a code; approve via
      __CODE_BLOCK_8__ or use allowlists.
  </Step>
  <Step title="Daemon install">
    - macOS: LaunchAgent
      - Requires logged-in user session; for headless, use a custom LaunchDaemon (not shipped).
    - Linux and Windows via WSL2: systemd user unit
      - Wizard attempts __CODE_BLOCK_9__ so gateway stays up after logout.
      - May prompt for sudo (writes __CODE_BLOCK_10__); it tries without sudo first.
    - Runtime selection: Node (recommended; required for WhatsApp and Telegram). Bun is not recommended.
  </Step>
  <Step title="Health check">
    - Starts gateway (if needed) and runs __CODE_BLOCK_11__.
    - __CODE_BLOCK_12__ adds gateway health probes to status output.
  </Step>
  <Step title="Skills">
    - Reads available skills and checks requirements.
    - Lets you choose node manager: npm or pnpm (bun not recommended).
    - Installs optional dependencies (some use Homebrew on macOS).
  </Step>
  <Step title="Finish">
    - Summary and next steps, including iOS, Android, and macOS app options.
  </Step>
</Steps>

<Note>
If no GUI is detected, the wizard prints SSH port-forward instructions for the Control UI instead of opening a browser.
If Control UI assets are missing, the wizard attempts to build them; fallback is __CODE_BLOCK_13__ (auto-installs UI deps).
</Note>

## 远程模式详情

远程模式将此机器配置为连接到其他位置的网关。

<Info>
Remote mode does not install or modify anything on the remote host.
</Info>

您设置的内容：

- 远程网关 URL (`ws://...`)
- 如果远程网关需要身份验证，则设置令牌（推荐）

<Note>
- If gateway is loopback-only, use SSH tunneling or a tailnet.
- Discovery hints:
  - macOS: Bonjour (__CODE_BLOCK_15__)
  - Linux: Avahi (__CODE_BLOCK_16__)
</Note>

## 身份验证和模型选项

<AccordionGroup>
  <Accordion title="Anthropic API key (recommended)">
    Uses __CODE_BLOCK_17__ if present or prompts for a key, then saves it for daemon use.
  </Accordion>
  <Accordion title="Anthropic OAuth (Claude Code CLI)">
    - macOS: checks Keychain item "Claude Code-credentials"
    - Linux and Windows: reuses __CODE_BLOCK_18__ if present

    On macOS, choose "Always Allow" so launchd starts do not block.

  </Accordion>
  <Accordion title="Anthropic token (setup-token paste)">
    Run __CODE_BLOCK_19__ on any machine, then paste the token.
    You can name it; blank uses default.
  </Accordion>
  <Accordion title="OpenAI Code subscription (Codex CLI reuse)">
    If __CODE_BLOCK_20__ exists, the wizard can reuse it.
  </Accordion>
  <Accordion title="OpenAI Code subscription (OAuth)">
    Browser flow; paste __CODE_BLOCK_21__.

    Sets __CODE_BLOCK_22__ to __CODE_BLOCK_23__ when model is unset or __CODE_BLOCK_24__.

  </Accordion>
  <Accordion title="OpenAI API key">
    Uses __CODE_BLOCK_25__ if present or prompts for a key, then saves it to
    __CODE_BLOCK_26__ so launchd can read it.

    Sets __CODE_BLOCK_27__ to __CODE_BLOCK_28__ when model is unset, __CODE_BLOCK_29__, or __CODE_BLOCK_30__.

  </Accordion>
  <Accordion title="xAI (Grok) API key">
    Prompts for __CODE_BLOCK_31__ and configures xAI as a model provider.
  </Accordion>
  <Accordion title="OpenCode Zen">
    Prompts for __CODE_BLOCK_32__ (or __CODE_BLOCK_33__).
    Setup URL: [opencode.ai/auth](https://opencode.ai/auth).
  </Accordion>
  <Accordion title="API key (generic)">
    Stores the key for you.
  </Accordion>
  <Accordion title="Vercel AI Gateway">
    Prompts for __CODE_BLOCK_34__.
    More detail: [Vercel AI Gateway](/providers/vercel-ai-gateway).
  </Accordion>
  <Accordion title="Cloudflare AI Gateway">
    Prompts for account ID, gateway ID, and __CODE_BLOCK_35__.
    More detail: [Cloudflare AI Gateway](/providers/cloudflare-ai-gateway).
  </Accordion>
  <Accordion title="MiniMax M2.1">
    Config is auto-written.
    More detail: [MiniMax](/providers/minimax).
  </Accordion>
  <Accordion title="Synthetic (Anthropic-compatible)">
    Prompts for __CODE_BLOCK_36__.
    More detail: [Synthetic](/providers/synthetic).
  </Accordion>
  <Accordion title="Moonshot and Kimi Coding">
    Moonshot (Kimi K2) and Kimi Coding configs are auto-written.
    More detail: [Moonshot AI (Kimi + Kimi Coding)](/providers/moonshot).
  </Accordion>
  <Accordion title="Custom provider">
    Works with OpenAI-compatible and Anthropic-compatible endpoints.

    Non-interactive flags:
    - __CODE_BLOCK_37__
    - __CODE_BLOCK_38__
    - __CODE_BLOCK_39__
    - __CODE_BLOCK_40__ (optional; falls back to __CODE_BLOCK_41__)
    - __CODE_BLOCK_42__ (optional)
    - __CODE_BLOCK_43__ (optional; default __CODE_BLOCK_44__)

  </Accordion>
  <Accordion title="Skip">
    Leaves auth unconfigured.
  </Accordion>
</AccordionGroup>

模型行为：

- 从检测到的选项中选择默认模型，或手动输入提供商和模型。
- 向导会运行模型检查，并在配置的模型未知或缺少身份验证时发出警告。

凭据和配置文件路径：

- OAuth 凭据：`~/.openclaw/credentials/oauth.json`
- 身份验证配置文件（API 密钥 + OAuth）：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`

<Note>
Headless and server tip: complete OAuth on a machine with a browser, then copy
__CODE_BLOCK_47__ (or __CODE_BLOCK_48__)
to the gateway host.
</Note>

## 输出和内部结构

`~/.openclaw/openclaw.json` 中的典型字段：

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers`（如果选择了 Minimax）
- `gateway.*`（模式、绑定、身份验证、tailscale）
- `channels.telegram.botToken`，`channels.discord.token`，`channels.signal.*`，`channels.imessage.*`
- 渠道白名单（Slack、Discord、Matrix、Microsoft Teams），当您在提示中选择加入时（名称尽可能解析为 ID）
- `skills.install.nodeManager`
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` 写入 `agents.list[]` 和可选的 `bindings`。

WhatsApp 凭据存储在 `~/.openclaw/credentials/whatsapp/<accountId>/` 下。
会话存储在 `~/.openclaw/agents/<agentId>/sessions/` 下。

<Note>
Some channels are delivered as plugins. When selected during onboarding, the wizard
prompts to install the plugin (npm or local path) before channel configuration.
</Note>

网关向导 RPC：

- `wizard.start`
- `wizard.next`
- `wizard.cancel`
- `wizard.status`

客户端（macOS 应用和控制界面）可以在不重新实现入门逻辑的情况下渲染步骤。

Signal 设置行为：

- 下载适当的发布资产
- 存储在 `~/.openclaw/tools/signal-cli/<version>/` 下
- 在配置中写入 `channels.signal.cliPath`
- JVM 构建需要 Java 21
- 使用可用的原生构建
- Windows 使用 WSL2 并在 WSL 内部遵循 Linux signal-cli 流程

## 相关文档

- 入门中心：[入门向导 (CLI)](/start/wizard)
- 自动化和脚本：[CLI 自动化](/start/wizard-cli-automation)
- 命令参考：[`openclaw onboard`](/cli/onboard)