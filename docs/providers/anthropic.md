---
summary: "Use Anthropic Claude via API keys or setup-token in OpenClaw"
read_when:
  - You want to use Anthropic models in OpenClaw
  - You want setup-token instead of API keys
title: "Anthropic"
---
# Anthropic (Claude)

Anthropic 构建了 **Claude** 模型系列并通过 API 提供访问。
在 OpenClaw 中，您可以使用 API 密钥或 **setup-token** 进行身份验证。

## 选项 A: Anthropic API 密钥

**适用场景:** 标准 API 访问和基于使用的计费。
在 Anthropic 控制台中创建您的 API 密钥。

### CLI 设置

```bash
openclaw onboard
# choose: Anthropic API key

# or non-interactive
openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
```

### 配置片段

```json5
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-5" } } },
}
```

## 提示缓存（Anthropic API）

OpenClaw 支持 Anthropic 的提示缓存功能。此功能仅限 **API**；订阅身份验证不遵守缓存设置。

### 配置

在您的模型配置中使用 `cacheRetention` 参数：

| 值    | 缓存持续时间 | 描述                         |
| ----- | ------------ | ---------------------------- |
| `none`  | 无缓存     | 禁用提示缓存              |
| `short` | 5 分钟      | API 密钥身份验证的默认值            |
| `long`  | 1 小时         | 扩展缓存（需要 beta 标志） |

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-5": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

### 默认设置

当使用 Anthropic API 密钥身份验证时，OpenClaw 自动对所有 Anthropic 模型应用 `cacheRetention: "short"`（5 分钟缓存）。您可以通过在配置中显式设置 `cacheRetention` 来覆盖此设置。

### 旧参数

为了向后兼容，仍然支持较旧的 `cacheControlTtl` 参数：

- `"5m"` 映射到 `short`
- `"1h"` 映射到 `long`

我们建议迁移到新的 `cacheRetention` 参数。

OpenClaw 包含 Anthropic API 请求的 `extended-cache-ttl-2025-04-11` beta 标志；如果您覆盖了提供商头信息，请保留它（参见 [/gateway/configuration](/gateway/configuration))。

## 选项 B: Claude setup-token

**适用场景:** 使用您的 Claude 订阅。

### 如何获取 setup-token

Setup-token 是由 **Claude Code CLI** 创建的，而不是 Anthropic 控制台。您可以在 **任何机器** 上运行此命令：

```bash
claude setup-token
```

将令牌粘贴到 OpenClaw 中（向导：**Anthropic 令牌（粘贴 setup-token）**），或在网关主机上运行：

```bash
openclaw models auth setup-token --provider anthropic
```

如果您在不同的机器上生成了令牌，请粘贴它：

```bash
openclaw models auth paste-token --provider anthropic
```

### CLI 设置

```bash
# Paste a setup-token during onboarding
openclaw onboard --auth-choice setup-token
```

### 配置片段

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-5" } } },
}
```

## 注意事项

- 使用 `claude setup-token` 生成 setup-token 并粘贴，或在网关主机上运行 `openclaw models auth setup-token`。
- 如果在 Claude 订阅中看到“OAuth 令牌刷新失败 …”，请使用 setup-token 重新进行身份验证。参见 [/gateway/troubleshooting#oauth-token-refresh-failed-anthropic-claude-subscription](/gateway/troubleshooting#oauth-token-refresh-failed-anthropic-claude-subscription)。
- 身份验证详细信息 + 重用规则在 [/concepts/oauth](/concepts/oauth) 中。

## 故障排除

**401 错误 / 令牌突然无效**

- Claude 订阅身份验证可能会过期或被撤销。重新运行 `claude setup-token`
  并将其粘贴到 **网关主机**。
- 如果 Claude CLI 登录位于不同的机器上，请在网关主机上使用
  `openclaw models auth paste-token --provider anthropic`。

**未找到提供程序 "anthropic" 的 API 密钥**

- 身份验证是 **按代理** 进行的。新代理不会继承主代理的密钥。
- 为该代理重新运行入职流程，或在网关主机上粘贴 setup-token / API 密钥，然后使用 `openclaw models status` 进行验证。

**未找到配置文件 `anthropic:default` 的凭据**

- 运行 `openclaw models status` 查看哪个身份验证配置文件处于活动状态。
- 重新运行入职流程，或为该配置文件粘贴 setup-token / API 密钥。

**没有可用的身份验证配置文件（全部冷却/不可用）**

- 检查 `openclaw models status --json` 中的 `auth.unusableProfiles`。
- 添加另一个 Anthropic 配置文件或等待冷却。

更多信息: [/gateway/troubleshooting](/gateway/troubleshooting) 和 [/help/faq](/help/faq)。