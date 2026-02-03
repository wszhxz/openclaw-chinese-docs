---
summary: "Models CLI: list, set, aliases, fallbacks, scan, status"
read_when:
  - Adding or modifying models CLI (models list/set/scan/aliases/fallbacks)
  - Changing model fallback behavior or selection UX
  - Updating model scan probes (tools/images)
title: "Models CLI"
---
# 模型 CLI

查看 [/concepts/model-failover](/concepts/model-failover) 了解认证配置轮换、冷却时间以及它们如何与回退机制交互。
快速提供者概览 + 示例：[/concepts/model-providers](/concepts/model-providers)。

## 模型选择机制

OpenClaw 按以下顺序选择模型：

1. **主模型**（`agents.defaults.model.primary` 或 `agents.defaults.model`）。
2. **回退模型**在 `agents.defaults.model.fallbacks`（按顺序）。
3. **提供者认证故障转移**会在提供者内部发生，再进入下一个模型。

相关说明：

- `agents.defaults.models` 是 OpenClaw 可使用的模型白名单/目录（含别名）。
- `agents.defaults.imageModel` 仅在主模型无法接收图像时使用。
- 每个代理的默认值可通过 `agents.list[].model` 加绑定覆盖 `agents.defaults.model`（详见 [/concepts/multi-agent](/concepts/multi-agent)）。

## 快速模型选择（经验性）

- **GLM**：在编码/工具调用方面稍好。
- **MiniMax**：更适合写作和氛围。

## 设置向导（推荐）

如果您不想手动编辑配置，请运行入职向导：

```bash
openclaw onboard
```

它可为常见提供者设置模型 + 认证，包括 **OpenAI Code (Codex) 订阅**（OAuth）和 **Anthropic**（推荐 API 密钥；`claude setup-token` 也支持）。

## 配置键（概览）

- `agents.defaults.model.primary` 和 `agents.defaults.model.fallbacks`
- `agents.defaults.imageModel.primary` 和 `agents.defaults.imageModel.fallbacks`
- `agents.defaults.models`（白名单 + 别名 + 提供者参数）
- `models.providers`（写入 `models.json` 的自定义提供者）

模型引用会标准化为小写。提供者别名如 `z.ai/*` 会标准化为 `zai/*`。

提供者配置示例（包括 OpenCode Zen）位于
[/gateway/configuration](/gateway/configuration#opencode-zen-multi-model-proxy)。

## “模型不允许”（以及为何回复会停止）

如果设置了 `agents.defaults.models`，它将成为 `/model` 和会话覆盖的**白名单**。当用户选择的模型不在该白名单中时，OpenClaw 会返回：

```
模型 "provider/model" 不允许。使用 /model 列出可用模型。
```

这会在正常回复生成**之前**发生，因此消息可能感觉像“未回复”。解决方法是：

- 将模型添加到 `agents.defaults.models`，
- 清除白名单（移除 `agents.defaults.models`），
- 或从 `/model list` 中选择模型。

示例白名单配置：

```json5
{
  agent: {
    model: { primary: "anthropic/claude-sonnet-4-5" },
    models: {
      "anthropic/claude-sonnet-4-5": { alias: "Sonnet" },
      "anthropic/claude-opus-4-5": { alias: "Opus" },
    },
  },
}
```

## 聊天中切换模型 (`/model`)

您可以在不重启的情况下为当前会话切换模型：

```
/model
/model list
/model 3
/model openai/gpt-5.2
/model status
```

说明：

- `/model`（和 `/model list`）是紧凑的编号选择器（模型家族 + 可用提供者）。
- `/model <#>` 从该选择器中选择。
- `/model status` 是详细视图（认证候选和配置的提供者端点 `baseUrl` + `api` 模式）。
- 模型引用通过**第一个** `/` 分割解析。输入 `/model <ref>` 时使用 `provider/model`。
- 如果模型 ID 本身包含 `/`（OpenRouter 风格），必须包含提供者前缀（示例：`/model openrouter/moonshotai/kimi-k2`）。
- 如果省略提供者，OpenClaw 将输入视为默认提供者的别名或模型（仅在模型 ID 中无 `/` 时有效）。

完整命令行为/配置：[斜杠命令](/tools/slash-commands)。

## CLI 命令

```bash
openclaw models list
openclaw models status
openclaw models set <provider/model>
openclaw models set-image <provider/model>

openclaw models aliases list
openclaw models aliases add <alias> <provider/model>
open
```