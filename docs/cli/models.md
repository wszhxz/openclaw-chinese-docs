---
summary: "CLI reference for `openclaw models` (status/list/set/scan, aliases, fallbacks, auth)"
read_when:
  - You want to change default models or view provider auth status
  - You want to scan available models/providers and debug auth profiles
title: "models"
---
# `openclaw models`

模型发现、扫描与配置（默认模型、回退机制、认证配置文件）。

相关文档：

- 提供商 + 模型：[模型](/providers/models)  
- 提供商认证配置：[入门指南](/start/getting-started)

## 常用命令

```bash
openclaw models status
openclaw models list
openclaw models set <model-or-alias>
openclaw models scan
```

`openclaw models status` 显示已解析的默认模型/回退模型，以及认证概览。  
当存在提供商使用快照时，OAuth/令牌状态部分将包含提供商使用标头。  
添加 `--probe` 可对每个已配置的提供商配置文件执行实时认证探测。  
探测为真实请求（可能消耗令牌并触发速率限制）。  
使用 `--agent <id>` 可检查已配置智能体的模型/认证状态。若未指定智能体，该命令将优先使用 `OPENCLAW_AGENT_DIR`/`PI_CODING_AGENT_DIR`（如已设置），否则使用已配置的默认智能体。

注意事项：

- `models set <model-or-alias>` 接受 `provider/model` 或别名。  
- 模型引用通过在**第一个** `/` 处分割进行解析。若模型 ID 包含 `/`（OpenRouter 风格），请包含提供商前缀（例如：`openrouter/moonshotai/kimi-k2`）。  
- 若省略提供商，OpenClaw 将把输入视为别名或**默认提供商**的模型（仅在模型 ID 中不包含 `/` 时有效）。  
- `models status` 在认证输出中可能显示 `marker(<value>)` 以表示非密钥占位符（例如 `OPENAI_API_KEY`、`secretref-managed`、`minimax-oauth`、`qwen-oauth`、`ollama-local`），而非将其作为密钥屏蔽。

### `models status`

选项：

- `--json`  
- `--plain`  
- `--check`（退出码 1 = 已过期/缺失，2 = 即将过期）  
- `--probe`（对已配置的认证配置文件执行实时探测）  
- `--probe-provider <name>`（仅探测一个提供商）  
- `--probe-profile <id>`（可重复指定或以逗号分隔的配置文件 ID）  
- `--probe-timeout <ms>`  
- `--probe-concurrency <n>`  
- `--probe-max-tokens <n>`  
- `--agent <id>`（已配置的智能体 ID；覆盖 `OPENCLAW_AGENT_DIR`/`PI_CODING_AGENT_DIR`）

## 别名 + 回退机制

```bash
openclaw models aliases list
openclaw models fallbacks list
```

## 认证配置文件

```bash
openclaw models auth add
openclaw models auth login --provider <id>
openclaw models auth setup-token
openclaw models auth paste-token
```

`models auth login` 执行提供商插件的认证流程（OAuth/API 密钥）。使用 `openclaw plugins list` 查看已安装的提供商列表。

注意事项：

- `setup-token` 将提示输入 setup-token 值（可在任意机器上通过运行 `claude setup-token` 生成）。  
- `paste-token` 接受在其他位置或通过自动化方式生成的令牌字符串。  
- Anthropic 政策说明：setup-token 支持仅为技术兼容性目的。Anthropic 过去曾限制部分订阅服务在 Claude Code 之外的使用，因此在广泛使用前，请务必确认当前条款。