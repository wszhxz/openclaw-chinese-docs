---
summary: "CLI onboarding wizard: guided setup for gateway, workspace, channels, and skills"
read_when:
  - Running or configuring the onboarding wizard
  - Setting up a new machine
title: "Onboarding Wizard (CLI)"
sidebarTitle: "Onboarding: CLI"
---
# 入门向导 (CLI)

入门向导是**推荐**的方式，在 macOS、Linux 或 Windows（通过 WSL2；强烈推荐）上设置 OpenClaw。
它通过一个引导流程配置本地网关或远程网关连接，以及通道、技能和工作区默认设置。

```bash
openclaw onboard
```

<Info>
Fastest first chat: open the Control UI (no channel setup needed). Run
__CODE_BLOCK_1__ and chat in the browser. Docs: [Dashboard](/web/dashboard).
</Info>

要稍后重新配置：

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
__CODE_BLOCK_3__ does not imply non-interactive mode. For scripts, use __CODE_BLOCK_4__.
</Note>

<Tip>
Recommended: set up a Brave Search API key so the agent can use __CODE_BLOCK_5__
(__CODE_BLOCK_6__ works without a key). Easiest path: __CODE_BLOCK_7__
which stores __CODE_BLOCK_8__. Docs: [Web tools](/tools/web).
</Tip>

## 快速开始 vs 高级

向导从**快速开始**（默认）或**高级**（完全控制）开始。

<Tabs>
  <Tab title="QuickStart (defaults)">
    - Local gateway (loopback)
    - Workspace default (or existing workspace)
    - Gateway port **18789**
    - Gateway auth **Token** (auto‑generated, even on loopback)
    - Tailscale exposure **Off**
    - Telegram + WhatsApp DMs default to **allowlist** (you'll be prompted for your phone number)
  </Tab>
  <Tab title="Advanced (full control)">
    - Exposes every step (mode, workspace, gateway, channels, daemon, skills).
  </Tab>
</Tabs>

## 向导配置的内容

**本地模式（默认）**会引导您完成这些步骤：

1. **模型/认证** — Anthropic API 密钥（推荐），OpenAI 或自定义提供商
   （与 OpenAI 兼容、与 Anthropic 兼容或自动检测未知）。选择一个默认模型。
2. **工作区** — 代理文件的位置（默认 `~/.openclaw/workspace`）。播种引导文件。
3. **网关** — 端口、绑定地址、认证模式、Tailscale 暴露。
4. **通道** — WhatsApp、Telegram、Discord、Google Chat、Mattermost、Signal、BlueBubbles 或 iMessage。
5. **守护进程** — 安装 LaunchAgent（macOS）或 systemd 用户单元（Linux/WSL2）。
6. **健康检查** — 启动网关并验证其正在运行。
7. **技能** — 安装推荐的技能和可选依赖项。

<Note>
Re-running the wizard does **not** wipe anything unless you explicitly choose **Reset** (or pass __CODE_BLOCK_10__).
If the config is invalid or contains legacy keys, the wizard asks you to run __CODE_BLOCK_11__ first.
</Note>

**远程模式**仅配置本地客户端以连接到其他位置的网关。
它**不**在远程主机上安装或更改任何内容。

## 添加另一个代理

使用 `openclaw agents add <name>` 创建一个具有自己工作区、
会话和认证配置文件的单独代理。不带 `--workspace` 运行将启动向导。

它设置的内容：

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

注意事项：

- 默认工作区遵循 `~/.openclaw/workspace-<agentId>`。
- 添加 `bindings` 以路由传入消息（向导可以完成此操作）。
- 非交互式标志：`--model`，`--agent-dir`，`--bind`，`--non-interactive`。

## 完整参考

有关详细的逐步分解、非交互式脚本编写、Signal 设置、
RPC API 以及向导编写的配置字段完整列表，请参阅
[向导参考](/reference/wizard)。

## 相关文档

- CLI 命令参考：[`openclaw onboard`](/cli/onboard)
- 入门概述：[入门概述](/start/onboarding-overview)
- macOS 应用入门：[入门](/start/onboarding)
- 代理首次运行仪式：[代理引导](/start/bootstrapping)