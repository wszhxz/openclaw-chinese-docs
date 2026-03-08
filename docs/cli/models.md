---
summary: "CLI reference for `openclaw models` (status/list/set/scan, aliases, fallbacks, auth)"
read_when:
  - You want to change default models or view provider auth status
  - You want to scan available models/providers and debug auth profiles
title: "models"
---
# `openclaw models`

模型发现、扫描和配置（默认模型、fallbacks、auth profiles）。

相关：

- 提供商 + 模型：[模型](/providers/models)
- 提供商认证设置：[入门指南](/start/getting-started)

## 常用命令

```bash
openclaw models status
openclaw models list
openclaw models set <model-or-alias>
openclaw models scan
```

`openclaw models status` 显示解析后的默认值/fallbacks 以及 auth 概览。
当提供商使用快照可用时，OAuth/token 状态部分包含
提供商使用标头。
添加 `--probe` 以针对每个配置的提供商配置文件运行实时 auth 探测。
探测是真实请求（可能会消耗 token 并触发速率限制）。
使用 `--agent <id>` 检查配置的 agent 的模型/auth 状态。省略时，
命令会使用 `OPENCLAW_AGENT_DIR`/`PI_CODING_AGENT_DIR`（如果已设置），否则使用
配置的默认 agent。

注意：

- `models set <model-or-alias>` 接受 `provider/model` 或别名。
- 模型引用通过在 **第一个** `/` 处分割进行解析。如果模型 ID 包含 `/`（OpenRouter 风格），请包含提供商前缀（示例：`openrouter/moonshotai/kimi-k2`）。
- 如果省略提供商，OpenClaw 会将输入视为别名或 **默认提供商** 的模型（仅当模型 ID 中没有 `/` 时有效）。
- `models status` 可能在 auth 输出中为非秘密占位符显示 `marker(<value>)`（例如 `OPENAI_API_KEY`、`secretref-managed`、`minimax-oauth`、`qwen-oauth`、`ollama-local`），而不是将它们作为秘密掩码。

### `models status`

选项：

- `--json`
- `--plain`
- `--check` (退出 1=过期/缺失，2=即将过期)
- `--probe` (配置的 auth profiles 的实时探测)
- `--probe-provider <name>` (探测一个提供商)
- `--probe-profile <id>` (重复或以逗号分隔的配置文件 id)
- `--probe-timeout <ms>`
- `--probe-concurrency <n>`
- `--probe-max-tokens <n>`
- `--agent <id>` (配置的 agent id；覆盖 `OPENCLAW_AGENT_DIR`/`PI_CODING_AGENT_DIR`)

## 别名 + fallbacks

```bash
openclaw models aliases list
openclaw models fallbacks list
```

## Auth profiles

```bash
openclaw models auth add
openclaw models auth login --provider <id>
openclaw models auth setup-token
openclaw models auth paste-token
```

`models auth login` 运行提供商插件的 auth 流程（OAuth/API key）。使用
`openclaw plugins list` 查看已安装哪些提供商。

注意：

- `setup-token` 提示输入 setup-token 值（在任何机器上使用 `claude setup-token` 生成）。
- `paste-token` 接受在其他地方生成或来自自动化的 token 字符串。
- Anthropic 政策注意：setup-token 支持属于技术兼容性。Anthropic 过去曾阻止过 Claude Code 之外的一些订阅用法，因此在广泛使用之前请验证当前条款。