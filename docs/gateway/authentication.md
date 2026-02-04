---
summary: "Model authentication: OAuth, API keys, and setup-token"
read_when:
  - Debugging model auth or OAuth expiry
  - Documenting authentication or credential storage
title: "Authentication"
---
# 认证

OpenClaw 支持 OAuth 和 API 密钥用于模型提供商。对于 Anthropic 账户，我们建议使用 **API 密钥**。对于 Claude 订阅访问，请使用由 `claude setup-token` 创建的长期令牌。

有关完整的 OAuth 流程和存储布局，请参见 [/concepts/oauth](/concepts/oauth)。

## 推荐的 Anthropic 设置（API 密钥）

如果您直接使用 Anthropic，请使用 API 密钥。

1. 在 Anthropic 控制台中创建一个 API 密钥。
2. 将其放在 **网关主机**（运行 `openclaw gateway` 的机器）上。

```bash
export ANTHROPIC_API_KEY="..."
openclaw models status
```

3. 如果网关在 systemd/launchd 下运行，建议将密钥放在 `~/.openclaw/.env` 中，以便守护进程可以读取它：

```bash
cat >> ~/.openclaw/.env <<'EOF'
ANTHROPIC_API_KEY=...
EOF
```

然后重启守护进程（或重启您的网关进程），并重新检查：

```bash
openclaw models status
openclaw doctor
```

如果您不想自己管理环境变量，入站向导可以为守护进程存储 API 密钥：`openclaw onboard`。

有关环境继承的详细信息（`env.shellEnv`，`~/.openclaw/.env`，systemd/launchd），请参见 [帮助](/help)。

## Anthropic: setup-token（订阅认证）

对于 Anthropic，推荐的方法是使用 **API 密钥**。如果您使用的是 Claude 订阅，也支持 setup-token 流程。在 **网关主机** 上运行它：

```bash
claude setup-token
```

然后将其粘贴到 OpenClaw 中：

```bash
openclaw models auth setup-token --provider anthropic
```

如果令牌是在另一台机器上创建的，请手动粘贴它：

```bash
openclaw models auth paste-token --provider anthropic
```

如果您看到类似 Anthropic 的错误：

```
This credential is only authorized for use with Claude Code and cannot be used for other API requests.
```

…请改用 Anthropic API 密钥。

手动输入令牌（任何提供商；写入 `auth-profiles.json` + 更新配置）：

```bash
openclaw models auth paste-token --provider anthropic
openclaw models auth paste-token --provider openrouter
```

适合自动化的检查（令牌过期/缺失时退出 `1`，即将过期时退出 `2`）：

```bash
openclaw models status --check
```

可选的操作脚本（systemd/Termux）在此文档中：
[/automation/auth-monitoring](/automation/auth-monitoring)

> `claude setup-token` 需要交互式 TTY。

## 检查模型认证状态

```bash
openclaw models status
openclaw doctor
```

## 控制使用的凭据

### 按会话（聊天命令）

使用 `/model <alias-or-id>@<profileId>` 为当前会话固定特定提供商的凭据（示例配置文件 ID：`anthropic:default`，`anthropic:work`）。

使用 `/model`（或 `/model list`）进行紧凑选择器；使用 `/model status` 进行完整视图（候选者 + 下一个认证配置文件，以及配置时的提供商端点详细信息）。

### 按代理（CLI 覆盖）

为代理设置显式的认证配置文件顺序覆盖（存储在该代理的 `auth-profiles.json` 中）：

```bash
openclaw models auth order get --provider anthropic
openclaw models auth order set --provider anthropic anthropic:default
openclaw models auth order clear --provider anthropic
```

使用 `--agent <id>` 目标特定代理；省略它以使用配置的默认代理。

## 故障排除

### “未找到凭据”

如果缺少 Anthropic 令牌配置文件，请在 **网关主机** 上运行 `claude setup-token`，然后重新检查：

```bash
openclaw models status
```

### 令牌即将过期/已过期

运行 `openclaw models status` 确认哪个配置文件即将过期。如果配置文件丢失，请重新运行 `claude setup-token` 并再次粘贴令牌。

## 要求

- Claude Max 或 Pro 订阅（适用于 `claude setup-token`）
- 安装了 Claude Code CLI（可用 `claude` 命令）