---

read_when:
  - 运行或配置新手引导向导
  - 设置新机器
summary: CLI 新手引导向导：Gateway网关、工作区、渠道和 Skills 的引导式设置
title: 新手引导向导
x-i18n:
  generated_at: "2026-02-01T13:49:20Z"
  model: claude-opus-4-5
  provider: pi
  source_hash: 571302dcf63a0c700cab6b54964e524d75d98315d3b35fafe7232d2ce8199e83
  source_path: start/wizard.md
  workflow: 9

---
# 新手引导向导 (CLI)

请使用以下命令启动新手引导流程：

```bash
control-ui
```

## 主要入口
```bash
openclaw onboard
```

## 新手引导向导说明
新手引导向导是一个交互式流程，用于配置您的环境。它会引导您完成以下步骤：

1. 设置本地 Gateway 网关
2. 配置通信渠道（如 WhatsApp、Telegram 等）
3. 安装必要的工具和依赖项
4. 验证系统健康状态
5. 配置 Skills（可选）

## 交互式流程
### 1. 本地 Gateway 网关设置
- 本地 Gateway 网关（local loopback）
- 远程 Gateway 网关（需提供 URL）
- 认证令牌（如需）

### 2. 通信渠道配置
- WhatsApp 凭据存储在 `~/.openclaw/credentials/whatsapp/<accountId>/` 下
- 会话存储在 `~/.openclaw/agents/<agentId>/sessions/` 中
- 频道允许名单（Slack/Discord/Matrix/Microsoft Teams）在提示期间选择启用时生效（名称会尽可能解析为 ID）

### 3. 工具和依赖项安装
- Node.js（推荐；WhatsApp/Telegram 需要）
- Bun（不推荐）
- Homebrew（部分依赖项在 macOS 上使用）

### 4. 系统健康检查
- 启动 Gateway 网关（如需）
- 运行 `openclaw health` 健康检查
- 提示：`openclaw status --deep` 将 Gateway 网关健康探测添加到状态输出中（需要可达的 Gateway 网关）

### 5. Skills 配置
- 读取可用 Skills 并检查依赖条件
- 选择 Node 管理器：npm / pnpm（不推荐 bun）
- 安装可选依赖项（部分在 macOS 上使用 Homebrew）

## 非交互模式
使用 `--non-interactive` 用于自动化或脚本化新手引导：

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

添加智能体（非交互）示例：

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.2 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## Gateway 网关向导 RPC
Gateway 网关通过 RPC 暴露向导流程（`wizard.start`, `wizard.next`, `wizard.cancel`, `wizard.status`)。客户端（macOS 应用、Control UI）可以渲染步骤而无需重新实现新手引导逻辑。

## Signal 设置 (signal-cli)
向导可以安装 `signal-cli`(从 GitHub 发布版本)：

- 下载相应的发布资源
- 将其存储在 `~/.openclaw/tools/signal-cli/<version>/`
- 写入 `channels.signal.cliPath` 到您的配置中

注意事项：
- JVM 构建需要 **Java 21**
- 如有原生构建则优先使用
- Windows 使用 WSL2；signal-cli 安装遵循 WSL 内的 Linux 流程

## 向导写入的内容
中的典型字段 `~/.openclaw/openclaw.json`：

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers`（如果选择了 Minimax）
- `gateway.*`(模式、绑定、认证、Tailscale)
- `channels.telegram.botToken`, `channels.discord.token`, `channels.signal.*`, `channels.imessage.*`
- 渠道允许名单（Slack/Discord/Matrix/Microsoft Teams），在提示期间选择启用时生效（名称会尽可能解析为 ID）
- `skills.install.nodeManager`
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` 写入 `agents.list[]` 和可选的 `bindings`。

## 相关文档
- macOS 应用新手引导： [新手引导](/start/onboarding)
- 配置参考： [Gateway 网关配置](/gateway/configuration)
- 提供商： [WhatsApp](/channels/whatsapp)， [Telegram](/channels/telegram)， [Discord](/channels/discord)， [Google Chat](/channels/googlechat)， [Signal](/channels/signal)， [iMessage](/channels/imessage)
- Skills： [Skills](/tools/skills)， [Skills 配置](/tools/skills-config)