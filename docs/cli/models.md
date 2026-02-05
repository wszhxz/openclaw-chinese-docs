---
summary: "CLI reference for `openclaw models` (status/list/set/scan, aliases, fallbacks, auth)"
read_when:
  - You want to change default models or view provider auth status
  - You want to scan available models/providers and debug auth profiles
title: "models"
---
# `openclaw models`

模型发现、扫描和配置（默认模型、回退选项、认证配置文件）。

相关链接：

- 提供商 + 模型：[Models](/providers/models)
- 提供商认证设置：[Getting started](/start/getting-started)

## 常用命令

```bash
openclaw models status
openclaw models list
openclaw models set <model-or-alias>
openclaw models scan
```

`openclaw models status` 显示解析后的默认/回退选项以及认证概览。
当提供商使用快照可用时，OAuth/token 状态部分包括提供商使用头信息。
添加 `--probe` 对每个配置的提供商配置文件运行实时认证探测。
探测是真实的请求（可能会消耗令牌并触发速率限制）。
使用 `--agent <id>` 检查配置代理的模型/认证状态。当省略时，
该命令使用 `OPENCLAW_AGENT_DIR`/`PI_CODING_AGENT_DIR` 如果已设置，否则使用
配置的默认代理。

注意事项：

- `models set <model-or-alias>` 接受 `provider/model` 或别名。
- 模型引用通过在 **第一个** `/` 处拆分进行解析。如果模型ID包含 `/`（OpenRouter风格），请包含提供商前缀（示例：`openrouter/moonshotai/kimi-k2`）。
- 如果省略提供商，OpenClaw 将输入视为别名或 **默认提供商** 的模型（仅在模型ID中没有 `/` 时有效）。

### `models status`

选项：

- `--json`
- `--plain`
- `--check`（退出 1=过期/缺失，2=即将过期）
- `--probe`（配置的认证配置文件的实时探测）
- `--probe-provider <name>`（探测一个提供商）
- `--probe-profile <id>`（重复或逗号分隔的配置文件ID）
- `--probe-timeout <ms>`
- `--probe-concurrency <n>`
- `--probe-max-tokens <n>`
- `--agent <id>`（配置的代理ID；覆盖 `OPENCLAW_AGENT_DIR`/`PI_CODING_AGENT_DIR`）

## 别名 + 回退选项

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

`models auth login` 运行提供商插件的认证流程（OAuth/API密钥）。使用
`openclaw plugins list` 查看哪些提供商已安装。

注意事项：

- `setup-token` 提示输入 setup-token 值（在任何机器上使用 `claude setup-token` 生成）。
- `paste-token` 接受从其他地方或自动化生成的令牌字符串。