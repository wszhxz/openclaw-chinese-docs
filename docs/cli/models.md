---

summary: "CLI reference for `openclaw models` (status/list/set/scan, aliases, fallbacks, auth)"
read_when:
  - You want to change default models or view provider auth status
  - You want to scan available models/providers and debug auth profiles
title: "models"

---
# `openclaw models`

模型发现、扫描和配置（默认模型、回退设置、认证配置文件）。

相关链接：

- 提供商 + 模型：[模型](/providers/models)
- 提供商认证设置：[入门指南](/start/getting-started)

## 常用命令

```bash
openclaw models status
openclaw models list
openclaw models set <model-or-alias>
openclaw models scan
```

`openclaw models status` 显示解析后的默认/回退设置以及认证概览。
当提供商使用快照可用时，OAuth/token 状态部分包含提供商使用头信息。
添加 `--probe` 以针对每个配置的提供商配置文件运行实时认证探针。
探针是真实请求（可能会消耗令牌并触发速率限制）。
使用 `--agent <id>` 检查配置的代理的模型/认证状态。若省略该命令，
则使用 `OPENCLAW_AGENT_DIR`/`PI_CODING_AGENT_DIR`（若已设置），否则使用配置的默认代理。

注意：

- `models set <model-or-alias>` 接受 `provider/model` 或别名。
- 模型引用通过按 **第一个** `/` 分割进行解析。如果模型 ID 包含 `/`（OpenRouter 风格），需包含提供商前缀（示例：`openrouter/moonshotai/kimi-k2`）。
- 如果省略提供商，OpenClaw 会将输入视为默认提供商的别名或模型（仅在模型 ID 中无 `/` 时有效）。

### `models status`

选项：

- `--json`
- `--plain`
- `--check`（退出码 1=过期/缺失，2=即将过期）
- `--probe`（配置的认证配置文件实时探针）
- `--probe-provider <name>`（探针单个提供商）
- `--probe-profile <id>`（重复或逗号分隔的配置文件 ID）
- `--probe-timeout <ms>`
- `--probe-concurrency <n>`
- `--probe-max-tokens <n>`
- `--agent <id>`（配置的代理 ID；覆盖 `OPENCLAW_AGENT_DIR`/`PI_CODING_AGENT_DIR`）

## 别名 + 回退设置

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

`models auth login` 运行提供商插件的认证流程（OAuth/API 密钥）。使用
`openclaw plugins list` 查看已安装的提供商。

注意：

- `setup-token` 会提示输入设置令牌值（在任意机器上使用 `claude setup-token` 生成）。
- `paste-token` 接受在其他地方生成的令牌字符串或来自自动化的令牌。