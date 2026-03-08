---
summary: "CLI onboarding wizard: guided setup for gateway, workspace, channels, and skills"
read_when:
  - Running or configuring the onboarding wizard
  - Setting up a new machine
title: "Onboarding Wizard (CLI)"
sidebarTitle: "Onboarding: CLI"
---
# 入门向导 (CLI)

入门向导是在 macOS、Linux 或 Windows（通过 WSL2；强烈推荐）上设置 OpenClaw 的**推荐**方式。
它在一个引导流程中配置本地 Gateway 或远程 Gateway 连接，以及 Channels、Skills 和 Workspace 默认值。

```bash
openclaw onboard
```

<Info>
Fastest first chat: open the Control UI (no channel setup needed). Run
__CODE_BLOCK_1__ and chat in the browser. Docs: [Dashboard](/web/dashboard).
</Info>

若要稍后重新配置：

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
__CODE_BLOCK_3__ does not imply non-interactive mode. For scripts, use __CODE_BLOCK_4__.
</Note>

<Tip>
The onboarding wizard includes a web search step where you can pick a provider
(Perplexity, Brave, Gemini, Grok, or Kimi) and paste your API key so the agent
can use __CODE_BLOCK_5__. You can also configure this later with
__CODE_BLOCK_6__. Docs: [Web tools](/tools/web).
</Tip>

## 快速开始与高级

向导以**快速开始**（默认值）或**高级**（完全控制）开始。

<Tabs>
  <Tab title="QuickStart (defaults)">
    - Local gateway (loopback)
    - Workspace default (or existing workspace)
    - Gateway port **18789**
    - Gateway auth **Token** (auto‑generated, even on loopback)
    - Tool policy default for new local setups: __CODE_BLOCK_7__ (existing explicit profile is preserved)
    - DM isolation default: local onboarding writes __CODE_BLOCK_8__ when unset. Details: [CLI Onboarding Reference](/start/wizard-cli-reference#outputs-and-internals)
    - Tailscale exposure **Off**
    - Telegram + WhatsApp DMs default to **allowlist** (you'll be prompted for your phone number)
  </Tab>
  <Tab title="Advanced (full control)">
    - Exposes every step (mode, workspace, gateway, channels, daemon, skills).
  </Tab>
</Tabs>

## 向导配置的内容

**本地模式（默认）**将引导您完成以下步骤：

1. **模型/认证** — 选择任何支持的提供商/认证流程（API key、OAuth 或 setup-token），包括 Custom Provider
   （兼容 OpenAI、兼容 Anthropic 或未知自动检测）。选择一个默认模型。
   安全提示：如果此代理将运行工具或处理 webhook/hooks 内容，请优先使用可用的最强最新一代模型，并保持工具策略严格。较弱/较旧的层级更容易受到提示注入攻击。
   对于非交互式运行，`--secret-input-mode ref` 在 auth profiles 中存储基于 env 的引用，而不是明文 API key 值。
   在非交互式 `ref` 模式下，必须设置 provider env var；如果不设置该 env var 而传递内联 key 标志，会快速失败。
   在交互式运行中，选择秘密引用模式允许您指向环境变量或配置的 provider ref（`file` 或 `exec`），并在保存前进行快速预检验证。
2. **Workspace** — 代理文件的位置（默认 `~/.openclaw/workspace`）。初始化种子文件。
3. **Gateway** — 端口、绑定地址、认证模式、Tailscale 暴露。
   在交互式令牌模式下，选择默认的明文令牌存储或选择启用 SecretRef。
   非交互式令牌 SecretRef 路径：`--gateway-token-ref-env <ENV_VAR>`。
4. **Channels** — WhatsApp、Telegram、Discord、Google Chat、Mattermost、Signal、BlueBubbles 或 iMessage。
5. **Daemon** — 安装 LaunchAgent（macOS）或 systemd 用户单元（Linux/WSL2）。
   如果令牌认证需要令牌且 `gateway.auth.token` 由 SecretRef 管理，则 Daemon 安装会验证它，但不会将解析后的令牌持久化到 supervisor 服务环境元数据中。
   如果令牌认证需要令牌且配置的令牌 SecretRef 未解析，则 Daemon 安装会被阻止，并提供可操作的指导。
   如果同时配置了 `gateway.auth.token` 和 `gateway.auth.password` 且 `gateway.auth.mode` 未设置，则 Daemon 安装会被阻止，直到明确设置模式。
6. **健康检查** — 启动 Gateway 并验证其正在运行。
7. **Skills** — 安装推荐的 Skills 和可选依赖项。

<Note>
Re-running the wizard does **not** wipe anything unless you explicitly choose **Reset** (or pass __CODE_BLOCK_19__).
CLI __CODE_BLOCK_20__ defaults to config, credentials, and sessions; use __CODE_BLOCK_21__ to include workspace.
If the config is invalid or contains legacy keys, the wizard asks you to run __CODE_BLOCK_22__ first.
</Note>

**远程模式**仅配置本地客户端连接到其他位置的 Gateway。
它**不**会在远程主机上安装或更改任何内容。

## 添加另一个代理

使用 `openclaw agents add <name>` 创建一个具有自己 Workspace、Sessions 和 Auth Profiles 的独立代理。
运行不带 `--workspace` 的命令将启动向导。

它设置的内容：

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

注意：

- 默认 Workspace 遵循 `~/.openclaw/workspace-<agentId>`。
- 添加 `bindings` 以路由传入消息（向导可以执行此操作）。
- 非交互式标志：`--model`、`--agent-dir`、`--bind`、`--non-interactive`。

## 完整参考

有关详细的逐步分解、非交互式脚本、Signal 设置、RPC API 以及向导写入的配置字段完整列表，请参阅 [向导参考](/reference/wizard)。

## 相关文档

- CLI 命令参考：[`openclaw onboard`](/cli/onboard)
- 入门概览：[Onboarding Overview](/start/onboarding-overview)
- macOS 应用入门：[Onboarding](/start/onboarding)
- 代理首次运行流程：[Agent Bootstrapping](/start/bootstrapping)