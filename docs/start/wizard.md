---
summary: "CLI onboarding wizard: guided setup for gateway, workspace, channels, and skills"
read_when:
  - Running or configuring the onboarding wizard
  - Setting up a new machine
title: "Onboarding Wizard"
---
# 引导向导（CLI）

引导向导是推荐的在 macOS、Linux 或 Windows（通过 WSL2；强烈推荐）上设置 OpenClaw 的方式。它会引导式地配置本地网关或远程网关连接，以及频道、技能和工作区默认设置。

主要入口点：

```bash
openclaw onboard
```

最快开始聊天：打开控制界面（无需设置频道）。运行 `openclaw dashboard` 并在浏览器中聊天。文档：[仪表盘](/web/dashboard)。

后续重新配置：

```bash
openclaw configure
```

推荐：设置 Brave 搜索 API 密钥，以便代理可以使用 `web_search`（`web_fetch` 无需密钥）。最简单路径：`openclaw configure --section web`，它会存储 `tools.web.search.apiKey`。文档：[网络工具](/tools/web)。

## 快速入门 vs 高级模式

引导向导从 **快速入门**（默认设置）开始，与 **高级模式**（完全控制）相对。

**快速入门** 保留默认设置：

- 本地网关（环回）
- 工作区默认（或现有工作区）
- 网关端口 **18789**
- 网关认证 **Token**（自动生成，即使在环回中）
- Tailscale 暴露 **关闭**
- Telegram + WhatsApp 的 DM 默认为 **白名单**（您将被提示输入手机号）

**高级模式** 暴露每一步（模式、工作区、网关、频道、守护进程、技能）。

## 引导向导执行的内容

**本地模式（默认）** 会引导您完成以下步骤：

- 模型/认证：选择模型和认证方式
- 网关配置：设置网关端口和绑定地址
- 守护进程安装：安装守护进程
- 技能跳过：跳过技能安装

**远程模式** 会引导您完成以下步骤：

- 选择远程网关
- 配置远程网关连接
- 设置频道认证密钥

## 引导向导流程详情

引导向导会逐步引导您完成以下步骤：

1. 选择模式（本地/远程）
2. 选择认证方式（API 密钥/其他）
3. 输入认证密钥
4. 设置网关端口和绑定地址
5. 安装守护进程
6. 选择技能安装方式
7. 完成配置

## 远程模式

远程模式会引导您完成以下步骤：

1. 选择远程网关
2. 配置远程网关连接
3. 设置频道认证密钥
4. 完成配置

## 添加代理

您可以使用以下命令添加代理：

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.2 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## 非交互模式

使用 `--non-interactive` 可以自动化或脚本化引导：

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

Gemini 示例：

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice gemini-api-key \
  --gemini-api-key "$GEMINI_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback
```

Z.AI 示例：

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice zai-api-key \
  --zai-api-key "$ZAI_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback
```

Vercel AI Gateway 示例：

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice ai-gateway-api-key \
  --ai-gateway-api-key "$AI_GATEWAY_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback
```

Moonshot 示例：

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice moonshot-api-key \
  --moonshot-api-key "$MOONSHOT_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback
```

Synthetic 示例：

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice synthetic-api-key \
  --synthetic-api-key "$SYNTHETIC_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback
```

OpenCode Zen 示例：

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice opencode-zen \
  --opencode-zen-api-key "$OPENCODE_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback
```

添加代理（非交互）示例：

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.2 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## 网关引导向导 RPC

网关通过 RPC 暴露引导向导流程（`wizard.start`、`wizard.next`、`wizard.cancel`、`wizard.status`）。客户端（macOS 应用、控制界面）可以在不重新实现引导逻辑的情况下渲染步骤。

## Signal 设置（signal-cli）

引导向导可以从 GitHub 发布中安装 `signal-cli`：

- 下载适当的发布资产。
- 存储在 `~/.openclaw/tools/signal-cli/<version>/`。
- 将 `channels.signal.cliPath` 写入您的配置。

注意：

- JVM 构建需要 **Java 21**。
- 有可用的原生构建时使用。
- Windows 使用 WSL2；signal-cli 安装遵循 WSL 中的 Linux 流程。

## 引导向导写入的内容

`~/.openclaw/openclaw.json` 中的典型字段：

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers`（如果选择了 Minimax）
- `gateway.*`（模式、绑定、认证、Tailscale）
- `channels.telegram.botToken`、`channels.discord.token`、`channels.signal.*`、`channels.imessage.*`