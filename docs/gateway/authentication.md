---
summary: "Model authentication: OAuth, API keys, and setup-token"
read_when:
  - Debugging model auth or OAuth expiry
  - Documenting authentication or credential storage
title: "Authentication"
---
# 身份验证

OpenClaw 支持 OAuth 和 API 密钥两种方式，用于模型提供商的身份验证。对于始终在线的网关主机，API 密钥通常是可预测性最高的选项。当您的提供商账户模型匹配时，也支持订阅/OAuth 流程。

有关完整的 OAuth 流程及存储布局，请参阅 [/concepts/oauth](/concepts/oauth)。  
对于基于 SecretRef 的身份验证（适用于 `env`/`file`/`exec` 提供商），请参阅 [密钥管理](/gateway/secrets)。  
有关 `models status --probe` 所使用的凭据资格/原因码规则，请参阅 [身份验证凭据语义](/auth-credential-semantics)。

## 推荐配置（API 密钥，任意提供商）

如果您运行的是长期存活的网关，请为所选提供商首先配置一个 API 密钥。  
特别地，对于 Anthropic，API 密钥身份验证是安全路径，推荐优先于订阅制 setup-token 身份验证。

1. 在您的提供商控制台中创建一个 API 密钥。  
2. 将其放置在 **网关主机**（即运行 `openclaw gateway` 的机器）上。

```bash
export <PROVIDER>_API_KEY="..."
openclaw models status
```

3. 如果网关运行在 systemd/launchd 下，建议将密钥存放在 `~/.openclaw/.env` 中，以便守护进程可读取：

```bash
cat >> ~/.openclaw/.env <<'EOF'
<PROVIDER>_API_KEY=...
EOF
```

然后重启守护进程（或重启您的网关进程），并重新检查：

```bash
openclaw models status
openclaw doctor
```

如果您不希望自行管理环境变量，入门向导可为您将 API 密钥存储供守护进程使用：`openclaw onboard`。

有关环境变量继承（`env.shellEnv`、`~/.openclaw/.env`、systemd/launchd）的详细信息，请参阅 [帮助](/help)。

## Anthropic：setup-token（订阅身份验证）

如果您使用 Claude 订阅服务，则支持 setup-token 流程。请在 **网关主机** 上运行：

```bash
claude setup-token
```

然后将其粘贴至 OpenClaw：

```bash
openclaw models auth setup-token --provider anthropic
```

如果该令牌是在其他机器上生成的，请手动粘贴：

```bash
openclaw models auth paste-token --provider anthropic
```

若您遇到类似以下的 Anthropic 错误：

```
This credential is only authorized for use with Claude Code and cannot be used for other API requests.
```

……请改用 Anthropic API 密钥。

<Warning>
Anthropic setup-token support is technical compatibility only. Anthropic has blocked
some subscription usage outside Claude Code in the past. Use it only if you decide
the policy risk is acceptable, and verify Anthropic's current terms yourself.
</Warning>

手动输入令牌（适用于任意提供商；写入 `auth-profiles.json` 并更新配置）：

```bash
openclaw models auth paste-token --provider anthropic
openclaw models auth paste-token --provider openrouter
```

静态凭据也支持身份验证配置文件引用：

- `api_key` 凭据可使用 `keyRef: { source, provider, id }`  
- `token` 凭据可使用 `tokenRef: { source, provider, id }`

面向自动化的检查（凭据过期或缺失时退出码为 `1`，即将过期时退出码为 `2`）：

```bash
openclaw models status --check
```

可选的运维脚本（systemd/Termux）文档见此处：  
[/automation/auth-monitoring](/automation/auth-monitoring)

> `claude setup-token` 需要交互式 TTY。

## 检查模型身份验证状态

```bash
openclaw models status
openclaw doctor
```

## API 密钥轮换行为（网关）

部分提供商支持在 API 请求遭遇速率限制时，尝试使用备用密钥重试请求。

- 优先级顺序如下：  
  - `OPENCLAW_LIVE_<PROVIDER>_KEY`（单一覆盖）  
  - `<PROVIDER>_API_KEYS`  
  - `<PROVIDER>_API_KEY`  
  - `<PROVIDER>_API_KEY_*`  
- Google 提供商还额外包含 `GOOGLE_API_KEY` 作为补充回退选项。  
- 使用前会对同一密钥列表去重。  
- OpenClaw 仅在发生速率限制错误时（例如 `429`、`rate_limit`、`quota`、`resource exhausted`）才使用下一个密钥重试。  
- 非速率限制类错误不会使用备用密钥重试。  
- 若所有密钥均失败，则返回最后一次尝试的最终错误。

## 控制所使用的凭据

### 按会话（聊天命令）

使用 `/model <alias-or-id>@<profileId>` 可为当前会话固定指定提供商的凭据（示例配置文件 ID：`anthropic:default`、`anthropic:work`）。

使用 `/model`（或 `/model list`）可调出简洁选择器；使用 `/model status` 可查看完整视图（含候选凭据 + 下一身份验证配置文件，以及已配置的提供商端点详情）。

### 按智能体（CLI 覆盖）

为某个智能体显式设置身份验证配置文件顺序覆盖（保存在该智能体的 `auth-profiles.json` 中）：

```bash
openclaw models auth order get --provider anthropic
openclaw models auth order set --provider anthropic anthropic:default
openclaw models auth order clear --provider anthropic
```

使用 `--agent <id>` 可指定目标智能体；若省略，则使用已配置的默认智能体。

## 故障排除

### “未找到凭据”

如果 Anthropic 令牌配置文件缺失，请在 **网关主机** 上运行 `claude setup-token`，然后重新检查：

```bash
openclaw models status
```

### 令牌即将过期/已过期

运行 `openclaw models status` 确认哪个配置文件即将过期。若该配置文件缺失，请重新运行 `claude setup-token` 并再次粘贴令牌。

## 要求

- Anthropic 订阅账户（用于 `claude setup-token`）  
- 已安装 Claude Code CLI（需可执行 `claude` 命令）