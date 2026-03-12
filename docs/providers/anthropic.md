---
summary: "Use Anthropic Claude via API keys or setup-token in OpenClaw"
read_when:
  - You want to use Anthropic models in OpenClaw
  - You want setup-token instead of API keys
title: "Anthropic"
---
# Anthropic（Claude）

Anthropic 公司开发了 **Claude** 模型系列，并通过 API 提供访问支持。  
在 OpenClaw 中，您可使用 API 密钥或 **setup-token** 进行身份验证。

## 选项 A：Anthropic API 密钥

**最适合场景：** 标准 API 访问及按用量计费。  
请在 Anthropic 控制台中创建您的 API 密钥。

### CLI 配置

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
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## 思维模式默认值（Claude 4.6）

- 当未显式设置思维级别时，Anthropic Claude 4.6 模型在 OpenClaw 中默认启用 `adaptive` 思维模式。  
- 您可以按消息覆盖该设置（`/think:<level>`），或在模型参数中统一配置：  
  `agents.defaults.models["anthropic/<model>"].params.thinking`。  
- 相关 Anthropic 文档：  
  - [自适应思维（Adaptive thinking）](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)  
  - [扩展思维（Extended thinking）](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

## 提示缓存（Anthropic API）

OpenClaw 支持 Anthropic 的提示缓存（prompt caching）功能。此功能**仅适用于 API 访问方式**；订阅认证（subscription auth）不支持缓存设置。

### 配置方式

在模型配置中使用 `cacheRetention` 参数：

| 值         | 缓存持续时间 | 描述                             |
| ---------- | ------------ | -------------------------------- |
| `none`  | 不缓存       | 禁用提示缓存                     |
| `short` | 5 分钟       | API 密钥认证的默认值             |
| `long`  | 1 小时       | 扩展缓存（需启用 beta 标志）     |

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

### 默认行为

当使用 Anthropic API 密钥进行身份验证时，OpenClaw 会自动为所有 Anthropic 模型应用 `cacheRetention: "short"`（5 分钟缓存）。您可通过在配置中显式设置 `cacheRetention` 覆盖该默认值。

### 按 Agent 覆盖 cacheRetention 设置

以模型级参数作为基准，再通过 `agents.list[].params` 对特定 Agent 进行覆盖。

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-opus-4-6" },
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" }, // baseline for most agents
        },
      },
    },
    list: [
      { id: "research", default: true },
      { id: "alerts", params: { cacheRetention: "none" } }, // override for this agent only
    ],
  },
}
```

与缓存相关的参数合并顺序如下：

1. `agents.defaults.models["provider/model"].params`  
2. `agents.list[].params`（匹配 `id`，按键覆盖）

这使得同一模型下的某个 Agent 可维持长期缓存，而另一个 Agent 则可禁用缓存，从而避免突发性/低复用流量带来的写入成本。

### Bedrock 上的 Claude 注意事项

- 在 AWS Bedrock 上运行的 Anthropic Claude 模型（`amazon-bedrock/*anthropic.claude*`）在配置后支持 `cacheRetention` 直通参数。  
- 非 Anthropic 的 Bedrock 模型在运行时将被强制设为 `cacheRetention: "none"`。  
- Anthropic API 密钥的智能默认值还会在未显式指定时，为 Claude-on-Bedrock 模型引用预设 `cacheRetention: "short"`。

### 已弃用参数

旧版 `cacheControlTtl` 参数仍受支持，以确保向后兼容性：

- `"5m"` 映射至 `short`  
- `"1h"` 映射至 `long`  

我们建议迁移至新版 `cacheRetention` 参数。

OpenClaw 为 Anthropic API 请求内置了 `extended-cache-ttl-2025-04-11` beta 标志；若您覆盖了 provider headers（参见 [/gateway/configuration](/gateway/configuration)），请保留该标志。

## 100 万上下文窗口（Anthropic beta 功能）

Anthropic 的 100 万上下文窗口功能处于 beta 阶段，受 beta 门控限制。在 OpenClaw 中，您需对支持的 Opus/Sonnet 模型单独启用该功能，方法是设置 `params.context1m: true`。

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { context1m: true },
        },
      },
    },
  },
}
```

OpenClaw 将其映射为 Anthropic 请求中的 `anthropic-beta: context-1m-2025-08-07`。

该功能仅在为对应模型显式将 `params.context1m` 设为 `true` 时才会激活。

前提要求：Anthropic 必须允许该凭证使用长上下文（通常为 API 密钥计费方式，或已启用“额外用量（Extra Usage）”的订阅账户）。否则 Anthropic 将返回：  
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`。

注意：Anthropic 当前在使用 OAuth/订阅令牌（`sk-ant-oat-*`）时，会拒绝带 `context-1m-*` beta 标志的请求。OpenClaw 会自动跳过 OAuth 认证下的 context1m beta 请求头，并保留必需的 OAuth 相关 beta 标志。

## 选项 B：Claude setup-token

**最适合场景：** 使用您的 Claude 订阅服务。

### 如何获取 setup-token

setup-token 由 **Claude Code CLI** 生成，而非 Anthropic 控制台。您可在**任意机器**上运行该命令：

```bash
claude setup-token
```

将生成的 token 粘贴至 OpenClaw（向导中选择：**Anthropic token（粘贴 setup-token）**），或直接在网关主机上运行：

```bash
openclaw models auth setup-token --provider anthropic
```

若您是在其他机器上生成的 token，请粘贴如下：

```bash
openclaw models auth paste-token --provider anthropic
```

### CLI 配置（setup-token）

```bash
# Paste a setup-token during onboarding
openclaw onboard --auth-choice setup-token
```

### 配置片段（setup-token）

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## 注意事项

- 请使用 `claude setup-token` 生成 setup-token 并粘贴，或在网关主机上运行 `openclaw models auth setup-token`。  
- 若在 Claude 订阅中看到 “OAuth token refresh failed …”，请重新使用 setup-token 进行身份验证。详见 [/gateway/troubleshooting#oauth-token-refresh-failed-anthropic-claude-subscription](/gateway/troubleshooting#oauth-token-refresh-failed-anthropic-claude-subscription)。  
- 身份验证详情及复用规则详见 [/concepts/oauth](/concepts/oauth)。

## 故障排查

**401 错误 / token 突然失效**

- Claude 订阅认证可能已过期或被撤销。请重新运行 `claude setup-token`，并将结果粘贴至**网关主机**。  
- 若 Claude CLI 登录操作发生在另一台机器上，请在网关主机上运行 `openclaw models auth paste-token --provider anthropic`。

**未找到提供方 "anthropic" 的 API 密钥**

- 身份验证是**按 Agent 进行的**。新创建的 Agent 不会继承主 Agent 的密钥。  
- 请为该 Agent 重新运行初始化流程，或在网关主机上粘贴 setup-token / API 密钥，然后使用 `openclaw models status` 验证。

**未找到配置文件 `anthropic:default` 的凭据**

- 运行 `openclaw models status` 查看当前激活的认证配置文件。  
- 请重新运行初始化流程，或为该配置文件粘贴 setup-token / API 密钥。

**无可用认证配置文件（全部处于冷却期/不可用状态）**

- 检查 `openclaw models status --json` 中的 `auth.unusableProfiles`。  
- 添加另一个 Anthropic 配置文件，或等待冷却期结束。

更多帮助：[/gateway/troubleshooting](/gateway/troubleshooting) 和 [/help/faq](/help/faq)。