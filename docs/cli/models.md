---
summary: "CLI reference for `openclaw models` (status/list/set/scan, aliases, fallbacks, auth)"
read_when:
  - You want to change default models or view provider auth status
  - You want to scan available models/providers and debug auth profiles
title: "models"
---
# `openclaw 模型`

模型发现、扫描和配置（默认模型、回退选项、认证配置文件）。

相关链接：

- 提供者 + 模型：[模型](/providers/models)
- 提供者认证设置：[入门指南](/start/getting-started)

## 常用命令

```bash
openclaw models status
openclaw models list
openclaw models set <模型或别名>
openclaw models scan
```

`openclaw models status` 显示解析后的默认/回退选项以及认证概览。
当提供者使用快照可用时，OAuth/令牌状态部分会包含提供者使用量头信息。
添加 `--probe` 可针对每个配置的提供者配置文件运行实时认证探针。
探针是真实请求（可能会消耗令牌并触发速率限制）。
使用 `--agent <id>` 可检查配置的代理的模型/认证状态。若未指定，则命令使用 `OPENCLAW_AGENT_DIR`/`PI_CODING_AGENT_DIR`（如果已设置），否则使用配置的默认代理。

注意事项：

- `models set <模型或别名>` 接受 `提供者/模型` 或别名。
- 模型引用通过 **第一个** `/` 分割解析。如果模型 ID 包含 `/`（OpenRouter 风格），需包含提供者前缀（示例：`openrouter/moonshotai/kimi-k2`）。
- 如果未指定提供者，OpenClaw 会将输入视为默认提供者的别名或模型（仅在模型 ID 中无 `/` 时有效）。

### `models status`

选项：

- `--json`
- `--plain`
- `--check`（退出码 1=过期/缺失，2=即将过期）
- `--probe`（对配置的认证配置文件运行实时探针）
- `--probe-provider <名称>`（探针单个提供者）
- `--probe-profile <ID>`（重复或逗号分隔的配置文件 ID）
- `--probe-timeout <毫秒>`
- `--probe-concurrency <n>`
- `--probe-max-tokens <n>`
- `--agent <ID>`（配置的代理 ID；覆盖 `OPENCLAW_AGENT_DIR`/`PI_CODING_AGENT_DIR`）

## 别名 + 回退

```bash
openclaw models aliases list
openclaw models fallbacks list
```

## 认证配置文件

```bash
openclaw models auth add
openclaw models auth login --provider <ID>
openclaw models auth setup-token
openclaw models auth paste-token
```

`models auth login` 运行提供者插件的认证流程（OAuth/API 密钥）。使用
`openclaw plugins list` 查看已安装的提供者。

注意事项：

- `setup-token` 会提示输入设置令牌的值（可在任何机器上使用 `claude setup-token` 生成）。
- `paste-token` 接受在其他地方或自动化流程中生成的令牌字符串。