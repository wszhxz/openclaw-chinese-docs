---
summary: "Complete reference for CLI onboarding flow, auth/model setup, outputs, and internals"
read_when:
  - You need detailed behavior for openclaw onboard
  - You are debugging onboarding results or integrating onboarding clients
title: "CLI Onboarding Reference"
sidebarTitle: "CLI reference"
---
# CLI 引导参考

本页是 `openclaw onboard` 的完整参考。
简短指南请参阅 [Onboarding Wizard (CLI)](/start/wizard)。

## 向导的功能

本地模式（默认）将引导您完成：

- 模型和 auth 设置（OpenAI Code subscription OAuth, Anthropic API key or setup token, plus MiniMax, GLM, Moonshot, and AI Gateway options）
- 工作区位置和 bootstrap 文件
- gateway 设置（port, bind, auth, tailscale）
- 渠道和 providers（Telegram, WhatsApp, Discord, Google Chat, Mattermost plugin, Signal）
- Daemon 安装（LaunchAgent 或 systemd user unit）
- 健康检查
- Skills 设置

远程模式配置此机器以连接到其他地方的 gateway。
它不会在远程主机上安装或修改任何内容。

## 本地流程详情

<Steps>
  <Step title="Existing config detection">
    - If __CODE_BLOCK_1__ exists, choose Keep, Modify, or Reset.
    - Re-running the wizard does not wipe anything unless you explicitly choose Reset (or pass __CODE_BLOCK_2__).
    - CLI __CODE_BLOCK_3__ defaults to __CODE_BLOCK_4__; use __CODE_BLOCK_5__ to also remove workspace.
    - If config is invalid or contains legacy keys, the wizard stops and asks you to run __CODE_BLOCK_6__ before continuing.
    - Reset uses __CODE_BLOCK_7__ and offers scopes:
      - Config only
      - Config + credentials + sessions
      - Full reset (also removes workspace)
  </Step>
  <Step title="Model and auth">
    - Full option matrix is in [Auth and model options](#auth-and-model-options).
  </Step>
  <Step title="Workspace">
    - Default __CODE_BLOCK_8__ (configurable).
    - Seeds workspace files needed for first-run bootstrap ritual.
    - Workspace layout: [Agent workspace](/concepts/agent-workspace).
  </Step>
  <Step title="Gateway">
    - Prompts for port, bind, auth mode, and tailscale exposure.
    - Recommended: keep token auth enabled even for loopback so local WS clients must authenticate.
    - In token mode, interactive onboarding offers:
      - **Generate/store plaintext token** (default)
      - **Use SecretRef** (opt-in)
    - In password mode, interactive onboarding also supports plaintext or SecretRef storage.
    - Non-interactive token SecretRef path: __CODE_BLOCK_9__.
      - Requires a non-empty env var in the onboarding process environment.
      - Cannot be combined with __CODE_BLOCK_10__.
    - Disable auth only if you fully trust every local process.
    - Non-loopback binds still require auth.
  </Step>
  <Step title="Channels">
    - [WhatsApp](/channels/whatsapp): optional QR login
    - [Telegram](/channels/telegram): bot token
    - [Discord](/channels/discord): bot token
    - [Google Chat](/channels/googlechat): service account JSON + webhook audience
    - [Mattermost](/channels/mattermost) plugin: bot token + base URL
    - [Signal](/channels/signal): optional __CODE_BLOCK_11__ install + account config
    - [BlueBubbles](/channels/bluebubbles): recommended for iMessage; server URL + password + webhook
    - [iMessage](/channels/imessage): legacy __CODE_BLOCK_12__ CLI path + DB access
    - DM security: default is pairing. First DM sends a code; approve via
      __CODE_BLOCK_13__ or use allowlists.
  </Step>
  <Step title="Daemon install">
    - macOS: LaunchAgent
      - Requires logged-in user session; for headless, use a custom LaunchDaemon (not shipped).
    - Linux and Windows via WSL2: systemd user unit
      - Wizard attempts __CODE_BLOCK_14__ so gateway stays up after logout.
      - May prompt for sudo (writes __CODE_BLOCK_15__); it tries without sudo first.
    - Runtime selection: Node (recommended; required for WhatsApp and Telegram). Bun is not recommended.
  </Step>
  <Step title="Health check">
    - Starts gateway (if needed) and runs __CODE_BLOCK_16__.
    - __CODE_BLOCK_17__ adds gateway health probes to status output.
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
If Control UI assets are missing, the wizard attempts to build them; fallback is __CODE_BLOCK_18__ (auto-installs UI deps).
</Note>

## 远程模式详情

远程模式配置此机器以连接到其他地方的 gateway。

<Info>
Remote mode does not install or modify anything on the remote host.
</Info>

您设置的内容：

- 远程 gateway URL (`ws://...`)
- 如果需要远程 gateway auth，则提供 Token（推荐）

<Note>
- If gateway is loopback-only, use SSH tunneling or a tailnet.
- Discovery hints:
  - macOS: Bonjour (__CODE_BLOCK_20__)
  - Linux: Avahi (__CODE_BLOCK_21__)
</Note>

## Auth 和模型选项

<AccordionGroup>
  <Accordion title="Anthropic API key">
    Uses __CODE_BLOCK_22__ if present or prompts for a key, then saves it for daemon use.
  </Accordion>
  <Accordion title="Anthropic OAuth (Claude Code CLI)">
    - macOS: checks Keychain item "Claude Code-credentials"
    - Linux and Windows: reuses __CODE_BLOCK_23__ if present

    On macOS, choose "Always Allow" so launchd starts do not block.

  </Accordion>
  <Accordion title="Anthropic token (setup-token paste)">
    Run __CODE_BLOCK_24__ on any machine, then paste the token.
    You can name it; blank uses default.
  </Accordion>
  <Accordion title="OpenAI Code subscription (Codex CLI reuse)">
    If __CODE_BLOCK_25__ exists, the wizard can reuse it.
  </Accordion>
  <Accordion title="OpenAI Code subscription (OAuth)">
    Browser flow; paste __CODE_BLOCK_26__.

    Sets __CODE_BLOCK_27__ to __CODE_BLOCK_28__ when model is unset or __CODE_BLOCK_29__.

  </Accordion>
  <Accordion title="OpenAI API key">
    Uses __CODE_BLOCK_30__ if present or prompts for a key, then stores the credential in auth profiles.

    Sets __CODE_BLOCK_31__ to __CODE_BLOCK_32__ when model is unset, __CODE_BLOCK_33__, or __CODE_BLOCK_34__.

  </Accordion>
  <Accordion title="xAI (Grok) API key">
    Prompts for __CODE_BLOCK_35__ and configures xAI as a model provider.
  </Accordion>
  <Accordion title="OpenCode Zen">
    Prompts for __CODE_BLOCK_36__ (or __CODE_BLOCK_37__).
    Setup URL: [opencode.ai/auth](https://opencode.ai/auth).
  </Accordion>
  <Accordion title="API key (generic)">
    Stores the key for you.
  </Accordion>
  <Accordion title="Vercel AI Gateway">
    Prompts for __CODE_BLOCK_38__.
    More detail: [Vercel AI Gateway](/providers/vercel-ai-gateway).
  </Accordion>
  <Accordion title="Cloudflare AI Gateway">
    Prompts for account ID, gateway ID, and __CODE_BLOCK_39__.
    More detail: [Cloudflare AI Gateway](/providers/cloudflare-ai-gateway).
  </Accordion>
  <Accordion title="MiniMax M2.5">
    Config is auto-written.
    More detail: [MiniMax](/providers/minimax).
  </Accordion>
  <Accordion title="Synthetic (Anthropic-compatible)">
    Prompts for __CODE_BLOCK_40__.
    More detail: [Synthetic](/providers/synthetic).
  </Accordion>
  <Accordion title="Moonshot and Kimi Coding">
    Moonshot (Kimi K2) and Kimi Coding configs are auto-written.
    More detail: [Moonshot AI (Kimi + Kimi Coding)](/providers/moonshot).
  </Accordion>
  <Accordion title="Custom provider">
    Works with OpenAI-compatible and Anthropic-compatible endpoints.

    Interactive onboarding supports the same API key storage choices as other provider API key flows:
    - **Paste API key now** (plaintext)
    - **Use secret reference** (env ref or configured provider ref, with preflight validation)

    Non-interactive flags:
    - __CODE_BLOCK_41__
    - __CODE_BLOCK_42__
    - __CODE_BLOCK_43__
    - __CODE_BLOCK_44__ (optional; falls back to __CODE_BLOCK_45__)
    - __CODE_BLOCK_46__ (optional)
    - __CODE_BLOCK_47__ (optional; default __CODE_BLOCK_48__)

  </Accordion>
  <Accordion title="Skip">
    Leaves auth unconfigured.
  </Accordion>
</AccordionGroup>

模型行为：

- 从检测到的选项中选择默认模型，或手动输入 provider 和 model。
- 向导运行模型检查，如果配置的模型未知或缺少 auth，则发出警告。

凭据和配置文件路径：

- OAuth credentials: `~/.openclaw/credentials/oauth.json`
- Auth profiles (API keys + OAuth): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`

凭据存储模式：

- 默认引导行为会将 API 密钥以明文值形式持久化存储到认证配置文件中。
- `--secret-input-mode ref` 启用引用模式，而非明文密钥存储。
  在交互式引导过程中，您可以选择以下任一方式：
  - 环境变量引用（例如 `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`）
  - 已配置的提供者引用（`file` 或 `exec`），包含提供者别名和 ID
- 交互式引用模式会在保存前运行快速的预检验证。
  - 环境变量引用：验证当前引导环境中的变量名和非空值。
  - 提供者引用：验证提供者配置并解析请求的 ID。
  - 如果预检失败，引导流程将显示错误并允许您重试。
- 在非交互式模式下，`--secret-input-mode ref` 仅支持环境变量支持。
  - 在引导进程环境中设置提供者环境变量。
  - 内联密钥标志（例如 `--openai-api-key`）要求设置该环境变量；否则引导流程将快速失败。
  - 对于自定义提供者，非交互式 `ref` 模式将 `models.providers.<id>.apiKey` 存储为 `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }`。
  - 在该自定义提供者情况下，`--custom-api-key` 要求设置 `CUSTOM_API_KEY`；否则引导流程将快速失败。
- 网关身份验证凭据在交互式引导中支持明文和 SecretRef 选项：
  - Token 模式：**生成/存储明文令牌**（默认）或 **使用 SecretRef**。
  - 密码模式：明文或 SecretRef。
- 非交互式令牌 SecretRef 路径：`--gateway-token-ref-env <ENV_VAR>`。
- 现有的明文配置继续按原样工作。

<Note>
Headless and server tip: complete OAuth on a machine with a browser, then copy
__CODE_BLOCK_12__ (or __CODE_BLOCK_13__)
to the gateway host.
</Note>

## 输出与内部结构

`~/.openclaw/openclaw.json` 中的典型字段：

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers`（如果选择 Minimax）
- `tools.profile`（本地引导未设置时默认为 `"coding"`；保留现有的显式值）
- `gateway.*`（模式、绑定、认证、tailscale）
- `session.dmScope`（本地引导未设置时默认为此项 `per-channel-peer`；保留现有的显式值）
- `channels.telegram.botToken`, `channels.discord.token`, `channels.signal.*`, `channels.imessage.*`
- 频道白名单（Slack、Discord、Matrix、Microsoft Teams），当您通过提示选择加入时使用（名称尽可能解析为 ID）
- `skills.install.nodeManager`
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` 写入 `agents.list[]` 和可选的 `bindings`。

WhatsApp 凭据位于 `~/.openclaw/credentials/whatsapp/<accountId>/` 下。
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

客户端（macOS 应用和控制界面）可以在不重新实现引导逻辑的情况下渲染步骤。

Signal 设置行为：

- 下载相应的发布资源
- 将其存储在 `~/.openclaw/tools/signal-cli/<version>/` 下
- 在配置中写入 `channels.signal.cliPath`
- JVM 构建需要 Java 21
- 当可用时使用原生构建
- Windows 使用 WSL2 并在 WSL 内部遵循 Linux signal-cli 流程

## 相关文档

- 引导中心：[引导向导 (CLI)](/start/wizard)
- 自动化和脚本：[CLI 自动化](/start/wizard-cli-automation)
- 命令参考：[`openclaw onboard`](/cli/onboard)