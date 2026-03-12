---
summary: "Full reference for the CLI onboarding wizard: every step, flag, and config field"
read_when:
  - Looking up a specific wizard step or flag
  - Automating onboarding with non-interactive mode
  - Debugging wizard behavior
title: "Onboarding Wizard Reference"
sidebarTitle: "Wizard Reference"
---
# 入门向导参考

这是 `openclaw onboard` CLI 向导的完整参考文档。  
如需概览，请参阅 [入门向导](/start/wizard)。

## 流程详情（本地模式）

<Steps>
  <Step title="Existing config detection">
    - If __CODE_BLOCK_1__ exists, choose **Keep / Modify / Reset**.
    - Re-running the wizard does **not** wipe anything unless you explicitly choose **Reset**
      (or pass __CODE_BLOCK_2__).
    - CLI __CODE_BLOCK_3__ defaults to __CODE_BLOCK_4__; use __CODE_BLOCK_5__
      to also remove workspace.
    - If the config is invalid or contains legacy keys, the wizard stops and asks
      you to run __CODE_BLOCK_6__ before continuing.
    - Reset uses __CODE_BLOCK_7__ (never __CODE_BLOCK_8__) and offers scopes:
      - Config only
      - Config + credentials + sessions
      - Full reset (also removes workspace)
  </Step>
  <Step title="Model/Auth">
    - **Anthropic API key**: uses __CODE_BLOCK_9__ if present or prompts for a key, then saves it for daemon use.
    - **Anthropic OAuth (Claude Code CLI)**: on macOS the wizard checks Keychain item "Claude Code-credentials" (choose "Always Allow" so launchd starts don't block); on Linux/Windows it reuses __CODE_BLOCK_10__ if present.
    - **Anthropic token (paste setup-token)**: run __CODE_BLOCK_11__ on any machine, then paste the token (you can name it; blank = default).
    - **OpenAI Code (Codex) subscription (Codex CLI)**: if __CODE_BLOCK_12__ exists, the wizard can reuse it.
    - **OpenAI Code (Codex) subscription (OAuth)**: browser flow; paste the __CODE_BLOCK_13__.
      - Sets __CODE_BLOCK_14__ to __CODE_BLOCK_15__ when model is unset or __CODE_BLOCK_16__.
    - **OpenAI API key**: uses __CODE_BLOCK_17__ if present or prompts for a key, then stores it in auth profiles.
    - **xAI (Grok) API key**: prompts for __CODE_BLOCK_18__ and configures xAI as a model provider.
    - **OpenCode Zen (multi-model proxy)**: prompts for __CODE_BLOCK_19__ (or __CODE_BLOCK_20__, get it at https://opencode.ai/auth).
    - **API key**: stores the key for you.
    - **Vercel AI Gateway (multi-model proxy)**: prompts for __CODE_BLOCK_21__.
    - More detail: [Vercel AI Gateway](/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**: prompts for Account ID, Gateway ID, and __CODE_BLOCK_22__.
    - More detail: [Cloudflare AI Gateway](/providers/cloudflare-ai-gateway)
    - **MiniMax M2.5**: config is auto-written.
    - More detail: [MiniMax](/providers/minimax)
    - **Synthetic (Anthropic-compatible)**: prompts for __CODE_BLOCK_23__.
    - More detail: [Synthetic](/providers/synthetic)
    - **Moonshot (Kimi K2)**: config is auto-written.
    - **Kimi Coding**: config is auto-written.
    - More detail: [Moonshot AI (Kimi + Kimi Coding)](/providers/moonshot)
    - **Skip**: no auth configured yet.
    - Pick a default model from detected options (or enter provider/model manually). For best quality and lower prompt-injection risk, choose the strongest latest-generation model available in your provider stack.
    - Wizard runs a model check and warns if the configured model is unknown or missing auth.
    - API key storage mode defaults to plaintext auth-profile values. Use __CODE_BLOCK_24__ to store env-backed refs instead (for example __CODE_BLOCK_25__).
    - OAuth credentials live in __CODE_BLOCK_26__; auth profiles live in __CODE_BLOCK_27__ (API keys + OAuth).
    - More detail: [/concepts/oauth](/concepts/oauth)
    <Note>
    Headless/server tip: complete OAuth on a machine with a browser, then copy
    __CODE_BLOCK_28__ (or __CODE_BLOCK_29__) to the
    gateway host.
    </Note>
  </Step>
  <Step title="Workspace">
    - Default __CODE_BLOCK_30__ (configurable).
    - Seeds the workspace files needed for the agent bootstrap ritual.
    - Full workspace layout + backup guide: [Agent workspace](/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - Port, bind, auth mode, tailscale exposure.
    - Auth recommendation: keep **Token** even for loopback so local WS clients must authenticate.
    - In token mode, interactive onboarding offers:
      - **Generate/store plaintext token** (default)
      - **Use SecretRef** (opt-in)
      - Quickstart reuses existing __CODE_BLOCK_31__ SecretRefs across __CODE_BLOCK_32__, __CODE_BLOCK_33__, and __CODE_BLOCK_34__ providers for onboarding probe/dashboard bootstrap.
      - If that SecretRef is configured but cannot be resolved, onboarding fails early with a clear fix message instead of silently degrading runtime auth.
    - In password mode, interactive onboarding also supports plaintext or SecretRef storage.
    - Non-interactive token SecretRef path: __CODE_BLOCK_35__.
      - Requires a non-empty env var in the onboarding process environment.
      - Cannot be combined with __CODE_BLOCK_36__.
    - Disable auth only if you fully trust every local process.
    - Non‑loopback binds still require auth.
  </Step>
  <Step title="Channels">
    - [WhatsApp](/channels/whatsapp): optional QR login.
    - [Telegram](/channels/telegram): bot token.
    - [Discord](/channels/discord): bot token.
    - [Google Chat](/channels/googlechat): service account JSON + webhook audience.
    - [Mattermost](/channels/mattermost) (plugin): bot token + base URL.
    - [Signal](/channels/signal): optional __CODE_BLOCK_37__ install + account config.
    - [BlueBubbles](/channels/bluebubbles): **recommended for iMessage**; server URL + password + webhook.
    - [iMessage](/channels/imessage): legacy __CODE_BLOCK_38__ CLI path + DB access.
    - DM security: default is pairing. First DM sends a code; approve via __CODE_BLOCK_39__ or use allowlists.
  </Step>
  <Step title="Web search">
    - Pick a provider: Perplexity, Brave, Gemini, Grok, or Kimi (or skip).
    - Paste your API key (QuickStart auto-detects keys from env vars or existing config).
    - Skip with __CODE_BLOCK_40__.
    - Configure later: __CODE_BLOCK_41__.
  </Step>
  <Step title="Daemon install">
    - macOS: LaunchAgent
      - Requires a logged-in user session; for headless, use a custom LaunchDaemon (not shipped).
    - Linux (and Windows via WSL2): systemd user unit
      - Wizard attempts to enable lingering via __CODE_BLOCK_42__ so the Gateway stays up after logout.
      - May prompt for sudo (writes __CODE_BLOCK_43__); it tries without sudo first.
    - **Runtime selection:** Node (recommended; required for WhatsApp/Telegram). Bun is **not recommended**.
    - If token auth requires a token and __CODE_BLOCK_44__ is SecretRef-managed, daemon install validates it but does not persist resolved plaintext token values into supervisor service environment metadata.
    - If token auth requires a token and the configured token SecretRef is unresolved, daemon install is blocked with actionable guidance.
    - If both __CODE_BLOCK_45__ and __CODE_BLOCK_46__ are configured and __CODE_BLOCK_47__ is unset, daemon install is blocked until mode is set explicitly.
  </Step>
  <Step title="Health check">
    - Starts the Gateway (if needed) and runs __CODE_BLOCK_48__.
    - Tip: __CODE_BLOCK_49__ adds gateway health probes to status output (requires a reachable gateway).
  </Step>
  <Step title="Skills (recommended)">
    - Reads the available skills and checks requirements.
    - Lets you choose a node manager: **npm / pnpm** (bun not recommended).
    - Installs optional dependencies (some use Homebrew on macOS).
  </Step>
  <Step title="Finish">
    - Summary + next steps, including iOS/Android/macOS apps for extra features.
  </Step>
</Steps>

<Note>
If no GUI is detected, the wizard prints SSH port-forward instructions for the Control UI instead of opening a browser.
If the Control UI assets are missing, the wizard attempts to build them; fallback is __CODE_BLOCK_50__ (auto-installs UI deps).
</Note>

## 非交互模式

使用 `--non-interactive` 自动化或脚本化入门流程：

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

添加 `--json` 以获取机器可读的摘要。

非交互模式下的网关令牌 SecretRef：

```bash
export OPENCLAW_GATEWAY_TOKEN="your-token"
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice skip \
  --gateway-auth token \
  --gateway-token-ref-env OPENCLAW_GATEWAY_TOKEN
```

`--gateway-token` 和 `--gateway-token-ref-env` 互斥。

<Note>
__CODE_BLOCK_57__ does **not** imply non-interactive mode. Use __CODE_BLOCK_58__ (and __CODE_BLOCK_59__) for scripts.
</Note>

<AccordionGroup>
  <Accordion title="Gemini example">
    __CODE_BLOCK_0__
  </Accordion>
  <Accordion title="Z.AI example">
    __CODE_BLOCK_1__
  </Accordion>
  <Accordion title="Vercel AI Gateway example">
    __CODE_BLOCK_2__
  </Accordion>
  <Accordion title="Cloudflare AI Gateway example">
    __CODE_BLOCK_3__
  </Accordion>
  <Accordion title="Moonshot example">
    __CODE_BLOCK_4__
  </Accordion>
  <Accordion title="Synthetic example">
    __CODE_BLOCK_5__
  </Accordion>
  <Accordion title="OpenCode Zen example">
    __CODE_BLOCK_6__
  </Accordion>
</AccordionGroup>

### 添加代理（非交互式）

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.2 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## 网关向导 RPC

网关通过 RPC 暴露向导流程（`wizard.start`、`wizard.next`、`wizard.cancel`、`wizard.status`）。  
客户端（macOS 应用、控制界面）可在无需重新实现入网逻辑的前提下渲染各步骤。

## Signal 配置（signal-cli）

向导可从 GitHub 发布版本中安装 `signal-cli`：

- 下载对应版本的发布资源；
- 将其存储于 `~/.openclaw/tools/signal-cli/<version>/` 目录下；
- 向您的配置中写入 `channels.signal.cliPath`。

注意事项：

- JVM 构建版本要求 **Java 21**；
- 在可用时优先使用原生构建版本；
- Windows 平台使用 WSL2；signal-cli 的安装流程在 WSL 内部遵循 Linux 流程。

## 向导写入的内容

`~/.openclaw/openclaw.json` 中的典型字段包括：

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers`（若选择 Minimax）
- `tools.profile`（本地入网默认为 `"coding"`，当该值未设置时；已显式设置的现有值将被保留）
- `gateway.*`（模式、绑定、认证、Tailscale）
- `session.dmScope`（行为细节：[CLI 入网参考](/start/wizard-cli-reference#outputs-and-internals)）
- `channels.telegram.botToken`、`channels.discord.token`、`channels.signal.*`、`channels.imessage.*`
- 当您在提示过程中选择启用时，Slack / Discord / Matrix / Microsoft Teams 等渠道的允许列表（名称在可能的情况下解析为 ID）；
- `skills.install.nodeManager`
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` 写入 `agents.list[]` 及可选的 `bindings`。

WhatsApp 凭据存放在 `~/.openclaw/credentials/whatsapp/<accountId>/` 下。  
会话数据存放在 `~/.openclaw/agents/<agentId>/sessions/` 下。

部分渠道以插件形式提供。当您在入网过程中选择某一渠道时，向导将在其可配置之前提示您安装该插件（支持 npm 或本地路径）。

## 相关文档

- 向导概述：[入网向导](/start/wizard)  
- macOS 应用入网：[入网](/start/onboarding)  
- 配置参考：[网关配置](/gateway/configuration)  
- 渠道支持：[WhatsApp](/channels/whatsapp)、[Telegram](/channels/telegram)、[Discord](/channels/discord)、[Google Chat](/channels/googlechat)、[Signal](/channels/signal)、[BlueBubbles](/channels/bluebubbles)（iMessage）、[iMessage](/channels/imessage)（旧版）  
- 技能：[技能](/tools/skills)、[技能配置](/tools/skills-config)