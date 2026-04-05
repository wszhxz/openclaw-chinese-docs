---
summary: "CLI reference for `openclaw models` (status/list/set/scan, aliases, fallbacks, auth)"
read_when:
  - You want to change default models or view provider auth status
  - You want to scan available models/providers and debug auth profiles
title: "models"
---
# `openclaw models`

模型发现、扫描和配置（默认模型、回退方案、认证配置文件）。

相关：

- 提供商与模型：[模型](/providers/models)
- 提供商认证设置：[入门](/start/getting-started)

## 常用命令

```bash
openclaw models status
openclaw models list
openclaw models set <model-or-alias>
openclaw models scan
```

`openclaw models status` 显示解析后的默认值/回退方案以及认证概览。
当提供程序使用快照可用时，OAuth/API-key 状态部分包括提供程序使用窗口和配额快照。
当前使用窗口提供商：Anthropic, GitHub Copilot, Gemini CLI, OpenAI Codex, MiniMax, Xiaomi, 和 z.ai。
使用认证来自特定于提供程序的钩子（如果可用）；否则 OpenClaw 从认证配置文件、环境变量或配置中回退到匹配的 OAuth/API-key 凭据。
添加 `--probe` 以对每个配置的提供程序配置文件运行实时认证探测。
探测是真实请求（可能会消耗令牌并触发速率限制）。
使用 `--agent <id>` 检查已配置代理的模型/认证状态。如果省略，该命令使用 `OPENCLAW_AGENT_DIR`/`PI_CODING_AGENT_DIR`（如果已设置），否则使用配置的默认代理。
探测行可以来自认证配置文件、环境变量或 `models.json`。

注意：

- `models set <model-or-alias>` 接受 `provider/model` 或别名。
- 模型引用通过按 **第一个** `/` 分割来解析。如果模型 ID 包含 `/`（OpenRouter 风格），请包含提供程序前缀（示例：`openrouter/moonshotai/kimi-k2`）。
- 如果您省略了提供程序，OpenClaw 首先将输入解析为别名，然后作为该确切模型 ID 的唯一配置提供程序匹配，最后才回退到配置的默认提供程序并发出弃用警告。
- 如果该提供程序不再暴露配置的默认模型，OpenClaw 将回退到第一个配置的提供程序/模型，而不是显示过时的已移除提供程序默认值。
- `models status` 在认证输出中可能显示 `marker(<value>)` 用于非秘密占位符（例如 `OPENAI_API_KEY`, `secretref-managed`, `minimax-oauth`, `oauth:chutes`, `ollama-local`），而不是将它们屏蔽为秘密。

### `models status`

选项：

- `--json`
- `--plain`
- `--check`（退出码 1=过期/缺失，2=即将过期）
- `--probe`（对配置的认证配置文件进行实时探测）
- `--probe-provider <name>`（探测一个提供程序）
- `--probe-profile <id>`（重复或逗号分隔的配置文件 ID）
- `--probe-timeout <ms>`
- `--probe-concurrency <n>`
- `--probe-max-tokens <n>`
- `--agent <id>`（配置的代理 ID；覆盖 `OPENCLAW_AGENT_DIR`/`PI_CODING_AGENT_DIR`）

探测状态类别：

- `ok`
- `auth`
- `rate_limit`
- `billing`
- `timeout`
- `format`
- `unknown`
- `no_model`

预期探测详细信息/原因代码情况：

- `excluded_by_auth_order`: 存在存储的配置文件，但显式的 `auth.order.<provider>` 将其省略，因此探测报告排除项而不是尝试它。
- `missing_credential`, `invalid_expires`, `expired`, `unresolved_ref`: 配置文件存在但不符合条件/无法解析。
- `no_model`: 存在提供程序认证，但 OpenClaw 无法为该提供程序解析可探测的模型候选项。

## 别名 + 回退方案

```bash
openclaw models aliases list
openclaw models fallbacks list
```

## 认证配置文件

```bash
openclaw models auth add
openclaw models auth login --provider <id>
openclaw models auth setup-token --provider <id>
openclaw models auth paste-token
```

`models auth add` 是交互式认证助手。根据您选择的提供程序，它可以启动提供程序认证流程（OAuth/API key）或引导您手动粘贴令牌。

`models auth login` 运行提供程序插件的认证流程（OAuth/API key）。使用 `openclaw plugins list` 查看安装了哪些提供程序。

示例：

```bash
openclaw models auth login --provider anthropic --method cli --set-default
openclaw models auth login --provider openai-codex --set-default
```

注意：

- `login --provider anthropic --method cli --set-default` 重用本地 Claude CLI 登录并将主要 Anthropic 默认模型路径重写为规范的 `claude-cli/claude-*` 引用。
- `setup-token` 和 `paste-token` 保留为暴露令牌认证方法的提供程序的通用令牌命令。
- `setup-token` 需要交互式 TTY 并运行提供程序的令牌认证方法（当它暴露该方法时默认为该提供程序的 `setup-token` 方法）。
- `paste-token` 接受在其他地方生成或来自自动化的令牌字符串。
- `paste-token` 需要 `--provider`，提示输入令牌值，并将其写入默认配置文件 ID `<provider>:manual`，除非您传递 `--profile-id`。
- `paste-token --expires-in <duration>` 从相对持续时间（如 `365d` 或 `12h`）存储绝对令牌过期时间。
- Anthropic 计费说明：Anthropic 的公开 Claude Code 文档仍将直接 Claude Code 终端使用包含在 Claude 计划限制内。此外，Anthropic 于 **2026 年 4 月 4 日下午 12:00 PT / 晚上 8:00 BST** 通知 OpenClaw 用户，**OpenClaw** Claude 登录路径算作第三方工具集使用，需要 **额外用量** 单独计费。
- Anthropic `setup-token` / `paste-token` 再次作为遗留/手动 OpenClaw 路径可用。使用它们时请预期 Anthropic 已告知 OpenClaw 用户此路径需要 **额外用量**。