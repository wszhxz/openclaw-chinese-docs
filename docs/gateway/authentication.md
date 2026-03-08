---
summary: "Model authentication: OAuth, API keys, and setup-token"
read_when:
  - Debugging model auth or OAuth expiry
  - Documenting authentication or credential storage
title: "Authentication"
---
# 认证

OpenClaw 支持模型提供商的 OAuth 和 API keys。对于始终在线的 gateway 主机，API keys 通常是最可预测的选项。当 Subscription/OAuth 流程与您的提供商账户模型匹配时，也支持这些流程。

请参阅 [/concepts/oauth](/concepts/oauth) 了解完整的 OAuth 流程和存储布局。
对于基于 SecretRef 的 auth（`env`/`file`/`exec` 提供商），请参阅 [Secrets Management](/gateway/secrets)。
关于 `models status --probe` 使用的 credential eligibility/reason-code 规则，请参阅 [Auth Credential Semantics](/auth-credential-semantics)。

## 推荐设置（API key，任何提供商）

如果您运行的是长期存在的 gateway，请从所选提供商的 API key 开始。
特别是对于 Anthropic，API key auth 是安全路径，推荐优于 subscription setup-token auth。

1. 在您的提供商 console 中创建 API key。
2. 将其放在 **gateway 主机** 上（运行 `openclaw gateway` 的机器）。

```bash
export <PROVIDER>_API_KEY="..."
openclaw models status
```

3. 如果 Gateway 在 systemd/launchd 下运行，建议将 key 放在
   `~/.openclaw/.env` 以便 daemon 可以读取它：

```bash
cat >> ~/.openclaw/.env <<'EOF'
<PROVIDER>_API_KEY=...
EOF
```

然后重启 daemon（或重启您的 Gateway 进程）并重新检查：

```bash
openclaw models status
openclaw doctor
```

如果您不想自己管理 env vars，onboarding wizard 可以存储 API keys 供 daemon 使用：`openclaw onboard`。

请参阅 [Help](/help) 了解 env inheritance 的详细信息（`env.shellEnv`，
`~/.openclaw/.env`, systemd/launchd）。

## Anthropic: setup-token (subscription auth)

如果您使用 Claude subscription，支持 setup-token 流程。运行
它在 **gateway 主机** 上：

```bash
claude setup-token
```

然后将其粘贴到 OpenClaw 中：

```bash
openclaw models auth setup-token --provider anthropic
```

如果 token 是在另一台机器上创建的，请手动粘贴：

```bash
openclaw models auth paste-token --provider anthropic
```

如果您看到类似这样的 Anthropic 错误：

```
This credential is only authorized for use with Claude Code and cannot be used for other API requests.
```

…请改用 Anthropic API key。

<Warning>
Anthropic setup-token support is technical compatibility only. Anthropic has blocked
some subscription usage outside Claude Code in the past. Use it only if you decide
the policy risk is acceptable, and verify Anthropic's current terms yourself.
</Warning>

手动 token 输入（任何提供商；写入 `auth-profiles.json` + 更新 config）：

```bash
openclaw models auth paste-token --provider anthropic
openclaw models auth paste-token --provider openrouter
```

Auth profile refs 也支持用于 static credentials：

- `api_key` credentials 可以使用 `keyRef: { source, provider, id }`
- `token` credentials 可以使用 `tokenRef: { source, provider, id }`

自动化友好检查（expired/missing 时退出 `1`，expiring 时退出 `2`）：

```bash
openclaw models status --check
```

可选的 ops scripts (systemd/Termux) 记录在此处：
[/automation/auth-monitoring](/automation/auth-monitoring)

> `claude setup-token` 需要交互式 TTY。

## 检查模型 auth 状态

```bash
openclaw models status
openclaw doctor
```

## API key rotation 行为 (gateway)

当 API call 命中提供商 rate limit 时，某些提供商支持使用备用 keys 重试 request。

- 优先级顺序：
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (single override)
  - `<PROVIDER>_API_KEYS`
  - `<PROVIDER>_API_KEY`
  - `<PROVIDER>_API_KEY_*`
- Google 提供商还包括 `GOOGLE_API_KEY` 作为额外的 fallback。
- 相同的 key list 在使用前会进行 deduplicated。
- OpenClaw 仅针对 rate-limit 错误使用下一个 key 重试（例如
  `429`, `rate_limit`, `quota`, `resource exhausted`)。
- Non-rate-limit 错误不会使用备用 keys 重试。
- 如果所有 keys 都失败，则返回最后一次 attempt 的最终 error。

## 控制使用哪个 credential

### 每 session (chat command)

使用 `/model <alias-or-id>@<profileId>` 为当前 session pin 住特定的 provider credential（示例 profile ids: `anthropic:default`, `anthropic:work`）。

使用 `/model`（或 `/model list`）用于 compact picker；使用 `/model status` 用于完整视图（candidates + next auth profile，加上配置时的 provider endpoint 详细信息）。

### 每 agent (CLI override)

为 agent 设置明确的 auth profile 顺序 override（存储在该 agent 的 `auth-profiles.json` 中）：

```bash
openclaw models auth order get --provider anthropic
openclaw models auth order set --provider anthropic anthropic:default
openclaw models auth order clear --provider anthropic
```

使用 `--agent <id>` 定位特定 agent；省略它以使用配置的默认 agent。

## 故障排除

### "No credentials found"

如果 Anthropic token profile 缺失，在
**gateway 主机** 上运行 `claude setup-token`，然后重新检查：

```bash
openclaw models status
```

### Token expiring/expired

运行 `openclaw models status` 确认哪个 profile 正在 expiring。如果 profile
缺失，重新运行 `claude setup-token` 并再次粘贴 token。

## 要求

- Anthropic subscription 账户（用于 `claude setup-token`）
- 已安装 Claude Code CLI（`claude` 命令可用）