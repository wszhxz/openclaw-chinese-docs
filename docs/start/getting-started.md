---
summary: "Beginner guide: from zero to first message (wizard, auth, channels, pairing)"
read_when:
  - First time setup from zero
  - You want the fastest path from install → onboarding → first message
title: "Getting Started"
---
.open<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context and the key terms. The document is about setting up OpenClaw, a chat application, with various steps and commands. 

First, I'll note the structure: sections like "Getting Started," "Prereqs," "Install the CLI," etc. Each section has subpoints with instructions, commands, and links. The user wants only the translated text, so I need to make sure not to include any extra explanations or markdown formatting.

I should pay attention to technical terms like "CLI onboarding wizard," "OAuth," "API keys," "WhatsApp," "Telegram," "Discord," "Mattermost," and specific commands like `openclaw onboard`, `pnpm install`, etc. These need to be accurately translated to maintain the technical accuracy. 

Some parts have code blocks and JSON configurations. I need to ensure that the code remains unchanged but the surrounding text is translated. For example, the JSON snippet about the sandbox mode should be translated but the keys and values should stay in English. 

Also, there are links like [Dashboard](/web/dashboard) which should remain as is, but the text before the link, like "Docs: [Dashboard](/web/dashboard)", needs to be translated. 

I need to be careful with the formatting. The original uses headings with ##, ###, etc., which should be preserved in Chinese. Also, the warnings and tips should be clearly marked, maybe using the same symbols like ⚠️. 

Some phrases are in all caps or have specific emphasis, like "Recommended path" or "Fastest chat." These should be translated to maintain their emphasis. 

I'll start translating section by section, ensuring that each command and instruction is correctly rendered in Chinese. For example, "Run `openclaw dashboard` and chat in the browser" becomes "运行 `openclaw dashboard` 并在浏览器中聊天". 

I should also check for consistency in terminology. For instance, "gateway" is translated as "网关" throughout. Proper nouns like "OpenClaw" and "WhatsApp" remain in English. 

After translating, I'll review the entire text to ensure that the flow is natural in Chinese and that technical terms are correctly used. I'll also verify that all links and code blocks are intact and properly formatted. 

Finally, I'll make sure there are no markdown elements like bold or italics, as the user specified only the translated text. The final output should be clean, accurate, and maintain the original structure and technical details.
</think>

# 入门指南

目标：尽快从 **零** → **第一个可运行的聊天界面**（带合理的默认设置）。

最快方式：打开控制界面（无需通道设置）。运行 `openclaw dashboard` 并在浏览器中聊天，或在网关主机上打开 `http://127.0.0.1:18789/`。文档：[仪表盘](/web/dashboard) 和 [控制界面](/web/control-ui)。

推荐路径：使用 **CLI 入门向导** (`openclaw onboard`)。它会设置：

- 模型/认证（推荐 OAuth）
- 网关设置
- 通道（WhatsApp/Telegram/Discord/Mattermost（插件）/...）
- 配对默认值（安全的私聊）
- 工作区初始化 + 技能
- 可选的后台服务

如果你想查看更深入的参考页面，请跳转至：[向导](/start/wizard)、[设置](/start/setup)、[配对](/start/pairing)、[安全](/gateway/security)。

沙箱说明：`agents.defaults.sandbox.mode: "non-main"` 使用 `session.mainKey`（默认 `"main"`），因此群组/频道会话会被沙箱隔离。如果你想让主代理始终在主机上运行，请设置每个代理的显式覆盖：

```json
{
  "routing": {
    "agents": {
      "main": {
        "workspace": "~/.openclaw/workspace",
        "sandbox": { "mode": "off" }
      }
    }
  }
}
```

## 0) 先决条件

- Node `>=22`
- `pnpm`（可选；如果从源代码构建推荐）
- **推荐：** Brave 搜索 API 密钥用于网络搜索。最简单的方式：
  `openclaw configure --section web`（存储 `tools.web.search.apiKey`）。
  查看 [Web 工具](/tools/web)。

macOS：如果你计划构建应用程序，请安装 Xcode / CLT。仅用于 CLI + 网关时，Node 即可。
Windows：使用 **WSL2**（推荐 Ubuntu）。WSL2 强烈推荐；原生 Windows 未测试，问题更多，且工具兼容性较差。先安装 WSL2，然后在 WSL 中运行 Linux 步骤。查看 [Windows (WSL2)](/platforms/windows)。

## 1) 安装 CLI（推荐）

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

安装选项（安装方法、非交互式、从 GitHub）：[安装](/install)。

Windows（PowerShell）：

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

替代方案（全局安装）：

```bash
npm install -g openclaw@latest
```

```bash
pnpm add -g openclaw@latest
```

## 2) 运行入门向导（并安装服务）

```bash
openclaw onboard --install-daemon
```

你将选择：

- **本地 vs 远程** 网关
- **认证**：OpenAI Code（Codex）订阅（OAuth）或 API 密钥。对于 Anthropic，推荐使用 API 密钥；`claude setup-token` 也支持。
- **提供商**：WhatsApp QR 登录、Telegram/Discord 机器人令牌、Mattermost 插件令牌等。
- **守护进程**：后台安装（launchd/systemd；WSL2 使用 systemd）
  - **运行时**：Node（推荐；WhatsApp/Telegram 所需）。Bun **不推荐**。
- **网关令牌**：向导默认生成一个（即使是在回环地址上）并存储在 `gateway.auth.token`。

向导文档：[向导](/start/wizard)

### 认证：在哪里（重要）

- **推荐的 Anthropic 路径**：设置 API 密钥（向导可以存储用于服务使用）。`claude setup-token` 也支持，如果你想重用 Claude Code 凭据。

- OAuth 凭据（旧版导入）：`~/.openclaw/credentials/oauth.json`
- 认证配置文件（OAuth + API 密钥）：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`

无头/服务器提示：首先在普通机器上进行 OAuth，然后将 `oauth.json` 复制到网关主机。

## 3) 启动网关

如果你在入门时安装了服务，网关应该已经运行：

```bash
openclaw gateway status
```

手动运行（前台）：

```bash
openclaw gateway --port 18789 --verbose
```

仪表盘（本地回环）：`http://127.0.0.1:18789/`
如果配置了令牌，请将其粘贴到控制界面设置中（存储为 `connect.params.auth.token`）。

⚠️ **Bun 警告（WhatsApp + Telegram）：** Bun 对这些通道有已知问题。如果你使用 WhatsApp 或 Telegram，请使用 **Node** 运行网关。

## 3.5) 快速验证（2 分钟）

```bash
openclaw status
openclaw health
openclaw security audit --deep
```

## 4) 配对 + 连接你的第一个聊天界面

### WhatsApp（QR 登录）

```bash
openclaw channels login
```

通过 WhatsApp 扫描 → 设置 → 链接设备。

WhatsApp 文档：[WhatsApp](/channels/whatsapp)

### Telegram / Discord / 其他

向导可以为你写入令牌/配置。如果你更喜欢手动配置，从以下开始：

- Telegram：[Telegram](/channels/telegram)
- Discord：[Discord](/channels/discord)
- Mattermost（插件）：[Mattermost](/channels/mattermost)

**Telegram 私聊提示：** 你的第一个私聊将返回一个配对代码。批准它（见下一步）或机器人将不会响应。

## 5) 私聊安全（配对批准）

默认姿态：未知私聊会收到一个短代码，消息在批准前不会处理。如果你的第一个私聊没有回复，请批准配对：

```bash
openclaw pairing list whatsapp
openclaw pairing approve whatsapp <code>
```

配对文档：[配对](/start/pairing)

## 从源代码（开发）

如果你正在修改 OpenClaw 本身，请从源代码运行：

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build # 第一次运行时自动安装 UI 依赖
pnpm build
openclaw onboard --install-da