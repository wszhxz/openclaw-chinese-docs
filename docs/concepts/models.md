---
summary: "Models CLI: list, set, aliases, fallbacks, scan, status"
read_when:
  - Adding or modifying models CLI (models list/set/scan/aliases/fallbacks)
  - Changing model fallback behavior or selection UX
  - Updating model scan probes (tools/images)
title: "Models CLI"
---
# 模型 CLI

有关认证配置文件轮换、冷却期以及它们如何与回退机制交互的说明，请参阅 [/concepts/model-failover](/concepts/model-failover)。
快速了解提供者概览及示例：[/concepts/model-providers](/concepts/model-providers)。

## 模型选择工作原理

OpenClaw 按以下顺序选择模型：

1. **主**模型 (`agents.defaults.model.primary` 或 `agents.defaults.model`)。
2. `agents.defaults.model.fallbacks` 中的**回退**项（按顺序）。
3. **提供者认证故障转移**发生在切换到下一个模型之前，在提供者内部进行。

相关：

- `agents.defaults.models` 是 OpenClaw 可使用模型的允许列表/目录（包括别名）。
- `agents.defaults.imageModel` **仅在**主模型无法接受图像时使用。
- 每个代理的默认值可以通过 `agents.list[].model` 加上绑定来覆盖 `agents.defaults.model`（参见 [/concepts/multi-agent](/concepts/multi-agent)）。

## 快速模型策略

- 将您的主模型设置为可用的最强最新一代模型。
- 对于成本/延迟敏感的任务和低风险聊天，使用回退模型。
- 对于启用工具的代理或不受信任的输入，避免使用较旧/较弱的模型层级。

## 设置向导（推荐）

如果您不想手动编辑配置，请运行入门向导：

```bash
openclaw onboard
```

它可以为常见提供者设置模型和认证，包括 **OpenAI Code (Codex) 订阅** (OAuth) 和 **Anthropic** (API 密钥或 `claude setup-token`)。

## 配置键（概览）

- `agents.defaults.model.primary` 和 `agents.defaults.model.fallbacks`
- `agents.defaults.imageModel.primary` 和 `agents.defaults.imageModel.fallbacks`
- `agents.defaults.models`（允许列表 + 别名 + 提供者参数）
- `models.providers`（自定义提供者写入到 `models.json`）

模型引用标准化为小写。像 `z.ai/*` 这样的提供者别名标准化为 `zai/*`。

提供者配置示例（包括 OpenCode Zen）位于 [/gateway/configuration](/gateway/configuration#opencode-zen-multi-model-proxy)。

## “模型不允许”（以及为何回复停止）

如果设置了 `agents.defaults.models`，它将成为 `/model` 和会话覆盖的**允许列表**。当用户选择一个不在该允许列表中的模型时，OpenClaw 返回：

```
Model "provider/model" is not allowed. Use /model to list available models.
```

这发生在生成正常回复**之前**，因此消息可能感觉“没有响应”。修复方法如下：

- 将模型添加到 `agents.defaults.models`，或者
- 清除允许列表（移除 `agents.defaults.models`），或者
- 从 `/model list` 中选择模型。

允许列表配置示例：

```json5
{
  agent: {
    model: { primary: "anthropic/claude-sonnet-4-5" },
    models: {
      "anthropic/claude-sonnet-4-5": { alias: "Sonnet" },
      "anthropic/claude-opus-4-6": { alias: "Opus" },
    },
  },
}
```

## 在聊天中切换模型 (`/model`)

您可以在不重启的情况下为当前会话切换模型：

```
/model
/model list
/model 3
/model openai/gpt-5.2
/model status
```

注意：

- `/model`（和 `/model list`）是一个紧凑的编号选择器（模型系列 + 可用提供者）。
- 在 Discord 上，`/model` 和 `/models` 打开一个交互式选择器，包含提供者和模型下拉菜单以及提交步骤。
- `/model <#>` 从该选择器中选择。
- `/model status` 是详细视图（认证候选者，以及配置时的提供者端点 `baseUrl` + `api` 模式）。
- 模型引用通过分割**第一个** `/` 来解析。输入 `/model <ref>` 时使用 `provider/model`。
- 如果模型 ID 本身包含 `/`（OpenRouter 风格），您必须包含提供者前缀（示例：`/model openrouter/moonshotai/kimi-k2`）。
- 如果您省略提供者，OpenClaw 会将输入视为别名或**默认提供者**的模型（仅当模型 ID 中没有 `/` 时有效）。

完整命令行为/配置：[斜杠命令](/tools/slash-commands)。

## CLI 命令

```bash
openclaw models list
openclaw models status
openclaw models set <provider/model>
openclaw models set-image <provider/model>

openclaw models aliases list
openclaw models aliases add <alias> <provider/model>
openclaw models aliases remove <alias>

openclaw models fallbacks list
openclaw models fallbacks add <provider/model>
openclaw models fallbacks remove <provider/model>
openclaw models fallbacks clear

openclaw models image-fallbacks list
openclaw models image-fallbacks add <provider/model>
openclaw models image-fallbacks remove <provider/model>
openclaw models image-fallbacks clear
```

`openclaw models`（无子命令）是 `models status` 的快捷方式。

### `models list`

默认显示配置的模型。有用的标志：

- `--all`：完整目录
- `--local`：仅限本地提供者
- `--provider <name>`：按提供者过滤
- `--plain`：每行一个模型
- `--json`：机器可读输出

### `models status`

显示解析后的主模型、回退项、图像模型以及配置提供者的认证概览。它还显示在认证存储中发现的资料的 OAuth 过期状态（默认 24 小时内警告）。`--plain` 仅打印解析后的主模型。
OAuth 状态始终显示（并包含在 `--json` 输出中）。如果配置的提供者没有凭据，`models status` 会打印**缺失认证**部分。
JSON 包含 `auth.oauth`（警告窗口 + 资料）和 `auth.providers`（每个提供者的有效认证）。
使用 `--check` 进行自动化（缺失/过期时退出 `1`，即将过期时 `2`）。

认证选择取决于提供者/账户。对于常驻网关主机，API 密钥通常是最可预测的；也支持订阅令牌流。

示例（Anthropic setup-token）：

```bash
claude setup-token
openclaw models status
```

## 扫描（OpenRouter 免费模型）

`openclaw models scan` 检查 OpenRouter 的**免费模型目录**，并可可选地探测模型的工具和图像支持。

关键标志：

- `--no-probe`：跳过实时探测（仅元数据）
- `--min-params <b>`：最小参数量（十亿级）
- `--max-age-days <days>`：跳过旧模型
- `--provider <name>`：提供者前缀过滤
- `--max-candidates <n>`：回退列表大小
- `--set-default`：将 `agents.defaults.model.primary` 设置为第一个选择
- `--set-image`：将 `agents.defaults.imageModel.primary` 设置为第一个图像选择

探测需要 OpenRouter API 密钥（来自认证资料或 `OPENROUTER_API_KEY`）。没有密钥，使用 `--no-probe` 仅列出候选项。

扫描结果排名依据：

1. 图像支持
2. 工具延迟
3. 上下文大小
4. 参数量

输入

- OpenRouter `/models` 列表（过滤 `:free`）
- 需要来自认证资料或 `OPENROUTER_API_KEY` 的 OpenRouter API 密钥（参见 [/environment](/help/environment)）
- 可选过滤器：`--max-age-days`, `--min-params`, `--provider`, `--max-candidates`
- 探测控制：`--timeout`, `--concurrency`

在 TTY 中运行时，您可以交互式地选择回退项。在非交互模式下，传递 `--yes` 以接受默认值。

## 模型注册表 (`models.json`)

`models.providers` 中的自定义提供者被写入代理目录下的 `models.json`（默认 `~/.openclaw/agents/<agentId>/models.json`）。除非 `models.mode` 设置为 `replace`，否则此文件默认会被合并。

匹配提供者 ID 的合并模式优先级：

- 代理 `models.json` 中已存在的非空 `baseUrl` 胜出。
- 代理 `models.json` 中的非空 `apiKey` 仅在当前配置/认证资料上下文中该提供者不由 SecretRef 管理时胜出。
- SecretRef 管理的提供者 `apiKey` 值从源标记刷新（`ENV_VAR_NAME` 用于环境引用，`secretref-managed` 用于文件/执行引用），而不是持久化解析后的密钥。
- 空或缺失的代理 `apiKey`/`baseUrl` 回退到配置 `models.providers`。
- 其他提供者字段从配置和标准化目录数据刷新。

这种基于标记的持久化适用于 OpenClaw 重新生成 `models.json` 的任何时候，包括像 `openclaw agent` 这样的命令驱动路径。