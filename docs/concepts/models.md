---
summary: "Models CLI: list, set, aliases, fallbacks, scan, status"
read_when:
  - Adding or modifying models CLI (models list/set/scan/aliases/fallbacks)
  - Changing model fallback behavior or selection UX
  - Updating model scan probes (tools/images)
title: "Models CLI"
---
# 模型CLI

有关认证配置文件轮换、冷却期以及它们如何与回退交互的信息，请参见
[/concepts/model-failover](/concepts/model-failover)。
快速提供商概览+示例：[/concepts/model-providers](/concepts/model-providers)。

## 模型选择工作原理

OpenClaw按以下顺序选择模型：

1. **主**模型(`agents.defaults.model.primary` 或 `agents.defaults.model`)。
2. `agents.defaults.model.fallbacks`中的**回退**(按顺序)。
3. 在移动到下一个模型之前，**提供商认证故障转移**在提供商内部发生。

相关：

- `agents.defaults.models`是OpenClaw可以使用的模型白名单/目录(加上别名)。
- `agents.defaults.imageModel`仅在主模型无法接受图像时使用。
- 每个代理的默认值可以通过`agents.list[].model`加绑定覆盖`agents.defaults.model`(参见[/concepts/multi-agent](/concepts/multi-agent))。

## 快速模型选择(经验性)

- **GLM**：在编码/工具调用方面稍好一些。
- **MiniMax**：在写作和氛围方面更好。

## 设置向导(推荐)

如果您不想手动编辑配置，请运行入门向导：

```bash
openclaw onboard
```

它可以为常见提供商设置模型+认证，包括**OpenAI Code (Codex)
订阅**(OAuth)和**Anthropic**(推荐API密钥；也支持`claude
setup-token`)。

## 配置键(概览)

- `agents.defaults.model.primary` 和 `agents.defaults.model.fallbacks`
- `agents.defaults.imageModel.primary` 和 `agents.defaults.imageModel.fallbacks`
- `agents.defaults.models` (白名单+别名+提供商参数)
- `models.providers` (写入`models.json`的自定义提供商)

模型引用被标准化为小写。像`z.ai/*`这样的提供商别名标准化为
`zai/*`。

提供商配置示例(包括OpenCode Zen)位于
[/gateway/configuration](/gateway/configuration#opencode-zen-multi-model-proxy)。

## "模型不被允许"(以及为什么回复停止)

如果设置了`agents.defaults.models`，它将成为`/model`和
会话覆盖的**白名单**。当用户选择不在该白名单中的模型时，
OpenClaw返回：

```
Model "provider/model" is not allowed. Use /model to list available models.
```

这发生在正常回复生成**之前**，所以消息可能感觉像是"没有响应"。修复方法是：

- 将模型添加到`agents.defaults.models`，或者
- 清空白名单(移除`agents.defaults.models`)，或者
- 从`/model list`中选择一个模型。

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

## 在聊天中切换模型(`/model`)

您可以在不重启的情况下为当前会话切换模型：

```
/model
/model list
/model 3
/model openai/gpt-5.2
/model status
```

注意事项：

- `/model`(和`/model list`)是一个紧凑的编号选择器(模型系列+可用提供商)。
- `/model <#>`从该选择器中选择。
- `/model status`是详细视图(认证候选项，配置时还包括提供商端点`baseUrl`+`api`模式)。
- 模型引用通过在**第一个**`/`处分割来解析。输入`/model <ref>`时使用`provider/model`。
- 如果模型ID本身包含`/`(OpenRouter风格)，您必须包含提供商前缀(示例：`/model openrouter/moonshotai/kimi-k2`)。
- 如果省略提供商，OpenClaw将输入视为别名或**默认提供商**的模型(仅在模型ID中没有`/`时有效)。

完整命令行为/配置：[斜杠命令](/tools/slash-commands)。

## CLI命令

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

`openclaw models`(无子命令)是`models status`的快捷方式。

### `models list`

默认显示已配置的模型。有用的标志：

- `--all`：完整目录
- `--local`：仅本地提供商
- `--provider <name>`：按提供商过滤
- `--plain`：每行一个模型
- `--json`：机器可读输出

### `models status`

显示解析的主模型、回退、图像模型以及已配置提供商的认证概览。
它还会显示在认证存储中找到的配置文件的OAuth过期状态(默认在24小时内警告)。`--plain`仅打印
解析的主模型。
OAuth状态始终显示(并包含在`--json`输出中)。如果配置的提供商没有凭据，`models status`打印**缺少认证**部分。
JSON包含`auth.oauth`(警告窗口+配置文件)和`auth.providers`
(每个提供商的有效认证)。
自动化使用`--check`(缺少/过期时退出`1`，即将过期时退出`2`)。

首选的Anthropic认证是Claude Code CLI设置令牌(可在任何地方运行；如需要请粘贴到网关主机上)：

```bash
claude setup-token
openclaw models status
```

## 扫描(OpenRouter免费模型)

`openclaw models scan`检查OpenRouter的**免费模型目录**，可以
选择性地探测模型的工具和图像支持。

关键标志：

- `--no-probe`：跳过实时探测(仅元数据)
- `--min-params <b>`：最小参数大小(十亿)
- `--max-age-days <days>`：跳过旧模型
- `--provider <name>`：提供商前缀过滤
- `--max-candidates <n>`：回退列表大小
- `--set-default`：将`agents.defaults.model.primary`设置为第一个选择
- `--set-image`：将`agents.defaults.imageModel.primary`设置为第一个图像选择

探测需要OpenRouter API密钥(来自认证配置文件或
`OPENROUTER_API_KEY`)。没有密钥时，使用`--no-probe`仅列出候选项。

扫描结果按以下顺序排名：

1. 图像支持
2. 工具延迟
3. 上下文大小
4. 参数数量

输入

- OpenRouter `/models` 列表(过滤`:free`)
- 需要来自认证配置文件或`OPENROUTER_API_KEY`的OpenRouter API密钥(参见[/environment](/environment))
- 可选过滤器：`--max-age-days`、`--min-params`、`--provider`、`--max-candidates`
- 探测控制：`--timeout`、`--concurrency`

在TTY中运行时，您可以交互式选择回退。在非交互
模式下，传递`--yes`以接受默认值。

## 模型注册表(`models.json`)

`models.providers`中的自定义提供商写入代理目录下的`models.json`
(默认`~/.openclaw/agents/<agentId>/models.json`)。除非将`models.mode`设置为`replace`，否则默认合并此文件。