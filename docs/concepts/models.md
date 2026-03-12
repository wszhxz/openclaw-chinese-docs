---
summary: "Models CLI: list, set, aliases, fallbacks, scan, status"
read_when:
  - Adding or modifying models CLI (models list/set/scan/aliases/fallbacks)
  - Changing model fallback behavior or selection UX
  - Updating model scan probes (tools/images)
title: "Models CLI"
---
# 模型 CLI

有关认证配置文件轮换、冷却时间以及其与回退机制交互的说明，请参阅 [/concepts/model-failover](/concepts/model-failover)。  
快速提供商概览及示例：[/concepts/model-providers](/concepts/model-providers)。

## 模型选择机制

OpenClaw 按以下顺序选择模型：

1. **主用**模型（`agents.defaults.model.primary` 或 `agents.defaults.model`）。
2. `agents.defaults.model.fallbacks` 中定义的**回退模型**（按顺序执行）。
3. **提供商认证故障转移**在切换至下一个模型前，于同一提供商内部完成。

相关说明：

- `agents.defaults.models` 是 OpenClaw 可用模型的白名单/目录（含别名）。
- `agents.defaults.imageModel` **仅在**主用模型无法处理图像时启用。
- 每个智能体的默认设置可通过 `agents.list[].model` 加绑定方式覆盖 `agents.defaults.model`（参见 [/concepts/multi-agent](/concepts/multi-agent)）。

## 快速模型策略

- 将主用模型设为您可访问的最强最新一代模型。
- 对成本/延迟敏感的任务及低风险对话，使用回退模型。
- 对支持工具的智能体或不可信输入，避免使用较旧/较弱的模型层级。

## 设置向导（推荐）

如您不希望手动编辑配置，请运行入门向导：

```bash
openclaw onboard
```

该向导可为常见提供商配置模型与认证，包括 **OpenAI Code（Codex）订阅**（OAuth）和 **Anthropic**（API 密钥或 `claude setup-token`）。

## 配置项（概览）

- `agents.defaults.model.primary` 和 `agents.defaults.model.fallbacks`
- `agents.defaults.imageModel.primary` 和 `agents.defaults.imageModel.fallbacks`
- `agents.defaults.models`（白名单 + 别名 + 提供商参数）
- `models.providers`（自定义提供商，直接写入 `models.json`）

模型引用统一转为小写。提供商别名（如 `z.ai/*`）将标准化为 `zai/*`。

提供商配置示例（含 OpenCode Zen）位于  
[/gateway/configuration](/gateway/configuration#opencode-zen-multi-model-proxy)。

## “模型未被允许”（及为何回复中断）

若设置了 `agents.defaults.models`，它将成为 `/model` 及会话覆盖的**白名单**。当用户选择的模型不在该白名单中时，OpenClaw 返回：

```
Model "provider/model" is not allowed. Use /model to list available models.
```

此操作发生在正常回复生成**之前**，因此消息可能看似“无响应”。解决方法为以下任一：

- 将该模型加入 `agents.defaults.models`；
- 清空白名单（移除 `agents.defaults.models`）；
- 从 `/model list` 中选择一个模型。

白名单配置示例：

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

## 在聊天中切换模型（`/model`）

您可在不重启会话的前提下，为当前会话切换模型：

```
/model
/model list
/model 3
/model openai/gpt-5.2
/model status
```

注意事项：

- `/model`（及 `/model list`）为紧凑型编号选择器（含模型族与可用提供商）。
- 在 Discord 中，`/model` 和 `/models` 将打开交互式选择器，含提供商与模型下拉菜单及提交步骤。
- `/model <#>` 用于从此选择器中选取。
- `/model status` 为详细视图（含认证候选者，以及配置后提供商端点 `baseUrl` 与 `api` 模式）。
- 模型引用通过拆分**首个** `/` 解析。输入 `/model <ref>` 时请使用 `provider/model`。
- 若模型 ID 本身包含 `/`（OpenRouter 风格），则必须包含提供商前缀（例如：`/model openrouter/moonshotai/kimi-k2`）。
- 若省略提供商，OpenClaw 将把输入视为别名或**默认提供商**的模型（仅当模型 ID 中不含 `/` 时有效）。

完整命令行为/配置详见：[斜杠命令](/tools/slash-commands)。

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

默认显示已配置的模型。常用标志：

- `--all`：完整目录
- `--local`：仅本地提供商
- `--provider <name>`：按提供商筛选
- `--plain`：每行一个模型
- `--json`：机器可读输出

### `models status`

显示已解析的主用模型、回退模型、图像模型，以及已配置提供商的认证概览。同时展示认证存储中发现的 OAuth 过期状态（默认在 24 小时内发出警告）。`--plain` 仅打印已解析的主用模型。  
OAuth 状态始终显示（且包含在 `--json` 输出中）。若某已配置提供商无凭证，`models status` 将打印 **缺失认证** 区段。  
JSON 输出包含 `auth.oauth`（警告窗口 + 配置文件）和 `auth.providers`（各提供商的有效认证）。  
使用 `--check` 实现自动化（缺失/过期时退出码为 `1`，即将过期时退出码为 `2`）。

认证方式取决于提供商/账户。对于常驻网关主机，API 密钥通常最稳定；也支持订阅令牌流程。

示例（Anthropic setup-token）：

```bash
claude setup-token
openclaw models status
```

## 扫描（OpenRouter 免费模型）

`openclaw models scan` 检查 OpenRouter 的**免费模型目录**，并可选探测模型对工具及图像的支持能力。

关键标志：

- `--no-probe`：跳过实时探测（仅元数据）
- `--min-params <b>`：最小参数量（单位：十亿）
- `--max-age-days <days>`：跳过旧模型
- `--provider <name>`：提供商前缀筛选
- `--max-candidates <n>`：回退列表大小
- `--set-default`：将 `agents.defaults.model.primary` 设为首个选择项
- `--set-image`：将 `agents.defaults.imageModel.primary` 设为首个图像选择项

探测需提供 OpenRouter API 密钥（来自认证配置文件或 `OPENROUTER_API_KEY`）。无密钥时，请使用 `--no-probe` 仅列出候选模型。

扫描结果按以下优先级排序：

1. 图像支持
2. 工具延迟
3. 上下文长度
4. 参数数量

输入要求：

- OpenRouter `/models` 列表（过滤器 `:free`）
- 需从认证配置文件或 `OPENROUTER_API_KEY` 获取 OpenRouter API 密钥（参见 [/environment](/help/environment)）
- 可选过滤器：`--max-age-days`、`--min-params`、`--provider`、`--max-candidates`
- 探测控制：`--timeout`、`--concurrency`

在 TTY 环境中运行时，可交互式选择回退模型。非交互模式下，请传入 `--yes` 以接受默认值。

## 模型注册表（`models.json`）

`models.providers` 中的自定义提供商将写入代理目录下的 `models.json`（默认为 `~/.openclaw/agents/<agentId>/models.json`）。除非将 `models.mode` 设为 `replace`，否则该文件默认参与合并。

匹配提供商 ID 的合并模式优先级如下：

- 若代理 `models.json` 中已存在非空的 `baseUrl`，则其优先生效。
- 若代理 `models.json` 中的 `apiKey` 非空，且该提供商在当前配置/认证配置文件上下文中**未被 SecretRef 管理**，则其优先生效。
- SecretRef 管理的提供商 `apiKey` 值将从源标记刷新（环境引用为 `ENV_VAR_NAME`，文件/执行引用为 `secretref-managed`），而非持久化已解析的密钥。
- 若代理 `apiKey`/`baseUrl` 为空或缺失，则回退至配置中的 `models.providers`。
- 其他提供商字段将从配置及标准化目录数据中刷新。

此基于标记的持久化机制适用于 OpenClaw 重新生成 `models.json` 的所有场景，包括命令驱动路径（如 `openclaw agent`）。