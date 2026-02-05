---
summary: "How OpenClaw rotates auth profiles and falls back across models"
read_when:
  - Diagnosing auth profile rotation, cooldowns, or model fallback behavior
  - Updating failover rules for auth profiles or models
title: "Model Failover"
---
# 模型故障转移

OpenClaw 在两个阶段处理故障：

1. 当前提供商内的**认证配置文件轮换**。
2. 回退到 `agents.defaults.model.fallbacks` 中的下一个模型。

本文档说明了运行时规则和支撑它们的数据。

## 认证存储（密钥 + OAuth）

OpenClaw 为 API 密钥和 OAuth 令牌使用**认证配置文件**。

- 密钥存储在 `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`（旧版：`~/.openclaw/agent/auth-profiles.json`）。
- 配置 `auth.profiles` / `auth.order` 仅用于**元数据 + 路由**（不包含密钥）。
- 旧版仅导入 OAuth 文件：`~/.openclaw/credentials/oauth.json`（首次使用时导入到 `auth-profiles.json`）。

更多详情：[/concepts/oauth](/concepts/oauth)

凭证类型：

- `type: "api_key"` → `{ provider, key }`
- `type: "oauth"` → `{ provider, access, refresh, expires, email? }` (+ `projectId`/`enterpriseUrl` 对于某些提供商)

## 配置文件 ID

OAuth 登录创建不同的配置文件，以便多个账户可以共存。

- 默认：当没有可用邮箱时为 `provider:default`。
- 带邮箱的 OAuth：`provider:<email>`（例如 `google-antigravity:user@gmail.com`）。

配置文件存储在 `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` 下的 `profiles` 中。

## 轮换顺序

当提供商有多个配置文件时，OpenClaw 按如下方式选择顺序：

1. **显式配置**：`auth.order[provider]`（如果设置）。
2. **已配置的配置文件**：按提供商过滤的 `auth.profiles`。
3. **已存储的配置文件**：提供商的 `auth-profiles.json` 中的条目。

如果没有配置显式顺序，OpenClaw 使用轮询顺序：

- **主键**：配置文件类型（**OAuth 在 API 密钥之前**）。
- **次键**：`usageStats.lastUsed`（每种类型内按最老优先）。
- **冷却/禁用的配置文件**被移到末尾，按最近到期时间排序。

### 会话粘性（缓存友好）

OpenClaw **按会话固定所选的认证配置文件**以保持提供商缓存活跃。
它**不会**在每个请求上轮换。固定的配置文件会被重用直到：

- 会话重置（`/new` / `/reset`）
- 压缩完成（压缩计数递增）
- 配置文件处于冷却/禁用状态

通过 `/model …@<profileId>` 进行的手动选择为此会话设置**用户覆盖**
并在新会话开始前不会自动轮换。

自动固定的配置文件（由会话路由器选择）被视为**偏好**：
它们首先被尝试，但 OpenClaw 可能在速率限制/超时时轮换到另一个配置文件。
用户固定的配置文件锁定到该配置文件；如果它失败且配置了模型回退，
OpenClaw 会转到下一个模型而不是切换配置文件。

### 为什么 OAuth 可能"看起来丢失"

如果你对同一提供商既有 OAuth 配置文件又有 API 密钥配置文件，在消息之间除非固定，轮询可能会在它们之间切换。要强制使用单个配置文件：

- 用 `auth.order[provider] = ["provider:profileId"]` 固定，或
- 通过 `/model …` 使用会话覆盖和配置文件覆盖（当你的 UI/聊天界面支持时）。

## 冷却期

当配置文件由于认证/速率限制错误（或看起来像速率限制的超时）而失败时，
OpenClaw 将其标记为冷却并转到下一个配置文件。
格式/无效请求错误（例如 Cloud Code Assist 工具调用 ID
验证失败）被视为值得故障转移并使用相同的冷却期。

冷却期使用指数退避：

- 1 分钟
- 5 分钟
- 25 分钟
- 1 小时（上限）

状态存储在 `auth-profiles.json` 下的 `usageStats` 中：

```json
{
  "usageStats": {
    "provider:profile": {
      "lastUsed": 1736160000000,
      "cooldownUntil": 1736160600000,
      "errorCount": 2
    }
  }
}
```

## 计费禁用

计费/信用失败（例如"积分不足"/"信用余额过低"）被视为值得故障转移，但通常不是临时的。OpenClaw 不使用短冷却期，而是将配置文件标记为**禁用**（使用更长的退避）并转到下一个配置文件/提供商。

状态存储在 `auth-profiles.json` 中：

```json
{
  "usageStats": {
    "provider:profile": {
      "disabledUntil": 1736178000000,
      "disabledReason": "billing"
    }
  }
}
```

默认值：

- 计费退避从**5 小时**开始，每次计费失败翻倍，上限为**24 小时**。
- 如果配置文件在**24 小时**内未失败（可配置），退避计数器重置。

## 模型回退

如果提供商的所有配置文件都失败，OpenClaw 会转到
`agents.defaults.model.fallbacks` 中的下一个模型。这适用于认证失败、速率限制和
耗尽配置文件轮换的超时（其他错误不会推进回退）。

当运行以模型覆盖开始（钩子或 CLI）时，回退仍然在尝试任何配置的回退后结束于
`agents.defaults.model.primary`。

## 相关配置

参见 [网关配置](/gateway/configuration) 了解：

- `auth.profiles` / `auth.order`
- `auth.cooldowns.billingBackoffHours` / `auth.cooldowns.billingBackoffHoursByProvider`
- `auth.cooldowns.billingMaxHours` / `auth.cooldowns.failureWindowHours`
- `agents.defaults.model.primary` / `agents.defaults.model.fallbacks`
- `agents.defaults.imageModel` 路由

参见 [模型](/concepts/models) 了解更广泛的模型选择和回退概述。