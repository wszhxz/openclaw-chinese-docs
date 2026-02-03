---
summary: "Use Anthropic Claude via API keys or setup-token in OpenClaw"
read_when:
  - You want to use Anthropic models in OpenClaw
  - You want setup-token instead of API keys
title: "Anthropic"
---
# 安托尼普（Claude）

安托尼普构建了 **Claude** 模型系列，并通过 API 提供访问。
在 OpenClaw 中，您可以使用 API 密钥或 **设置令牌** 进行身份验证。

## 选项 A：安托尼普 API 密钥

**适用于：** 标准 API 访问和按使用量计费。
在安托尼普控制台中创建您的 API 密钥。

### CLI 设置

```bash
openclaw onboard
# 选择：安托尼普 API 密钥

# 或非交互式
openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
```

### 配置片段

```json5
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-5" } } },
}
```

## 提示缓存（安托尼普 API）

OpenClaw 支持安托尼普的提示缓存功能。此功能为 **仅 API**；订阅认证不支持缓存设置。

### 配置

在模型配置中使用 `cacheRetention` 参数：

| 值   | 缓存持续时间 | 描述                         |
| ------- | ---------- | ---------------------- |
| `none`  | 无缓存     | 禁用提示缓存              |
| `short` | 5 分钟      | API 密钥认证的默认值            |
| `long`  | 1 小时     | 延长缓存（需要 beta 标志） |

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

### 默认值

当使用安托尼普 API 密钥认证时，OpenClaw 会自动为所有安托尼普模型应用 `cacheRetention: "short"`（5 分钟缓存）。您可以通过在配置中显式设置 `cacheRetention` 来覆盖此默认值。

### 旧参数

旧的 `cacheControlTtl` 参数仍支持以确保向后兼容：

- `"5m"` 映射到 `short`
- `"1h"` 映射到 `long`

我们建议迁移到新的 `cacheRetention` 参数。

OpenClaw 包含用于安托尼普 API 请求的 `extended-cache-ttl-2025-04-11` beta 标志；如果覆盖了提供者头信息（参见 [/gateway/configuration](/gateway/configuration)），请保留它。

## 选项 B：Claude 设置令牌

**适用于：** 使用您的 Claude 订阅。

### 如何获取设置令牌

设置令牌由 **Claude 代码 CLI** 创建，而不是安托尼普控制台。您可以在 **任何机器** 上运行此命令：

```bash
claude setup-token
```

将令牌粘贴到 OpenClaw（向导：**安托尼普令牌（粘贴设置令牌）**），或者在网关主机上运行：

```bash
openclaw models auth setup-token --provider anthropic
```

如果您在另一台机器上生成了令牌，请粘贴它：

```bash
openclaw models auth paste-token --provider anthropic
```

### CLI 设置

```bash
# 在注册过程中粘贴设置令牌
openclaw onboard --auth-choice setup-token
```

### 配置片段

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-5" } } },
}
```

## 注意事项

- 使用 `claude setup-token` 生成设置令牌并粘贴，或在网关主机上运行 `openclaw models auth setup-token`。
- 如果您在 Claude 订阅中看到 “OAuth 令牌刷新失败 …”，请使用设置令牌重新认证。参见 [/gateway/troubleshooting#oauth-token-refresh-failed-anthropic-claude-subscription](/gateway/troubleshooting#oauth-token-refresh-failed-anthropic-claude-subscription)。
- 认证详情 + 重用规则请参见 [/concepts/oauth](/concepts/oauth)。

## 故障排除

**401 错误 / 令牌突然失效**

- Claude 订阅认证可能过期或被撤销。重新运行 `claude setup-token` 并将令牌粘贴到 **网关主机**。
- 如果 Claude CLI 登录在另一台机器上，请在网关主机上使用 `openclaw models auth paste-token --provider anthropic`。

**未找到提供者 "anthropic" 的 API 密钥**

- 认证是 **按代理** 进行的。新代理不会继承主代理的密钥。
- 为该代理重新运行注册流程，或在网关主机上粘贴设置令牌 / API 密钥，然后使用 `openclaw models status` 验证。

**未找到配置文件 `anthropic:default` 的凭据**

- 运行 `openclaw models status` 查看当前的认证配置文件。
- 重新运行注册流程，或为该配置文件粘贴设置令牌 / API 密钥。

**没有可用的认证配置文件（所有均处于冷却/不可用状态）**

- 检查 `openclaw models status --json` 中的 `auth.unusableProfiles`。
- 添加另一个安托尼普配置文件或等待冷却期结束。

更多信息：[/gateway/troubleshooting](/gateway/troubleshooting) 和 [/help/faq](/help/faq)。