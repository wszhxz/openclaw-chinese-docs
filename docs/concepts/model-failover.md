---
summary: "How OpenClaw rotates auth profiles and falls back across models"
read_when:
  - Diagnosing auth profile rotation, cooldowns, or model fallback behavior
  - Updating failover rules for auth profiles or models
title: "Model Failover"
---
# 模型故障转移

OpenClaw 通过两个阶段处理故障：

1. **当前提供者的认证配置文件轮换**。
2. **切换到 `agents.defaults.model.fallbacks` 中的下一个模型**。

本文档解释了运行时规则以及支持这些规则的数据。

## 认证存储（密钥 + OAuth）

OpenClaw 使用 **认证配置文件** 来管理 API 密钥和 OAuth 令牌。

- 密钥存储在 `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`（旧版：`~/.openclaw/agent/auth-profiles.json`）。
- 配置 `auth.profiles` / `auth.order` 仅用于 **元数据和路由**（不包含密钥）。
- 仅用于导入的 OAuth 文件：`~/.openclaw/credentials/oauth.json`（首次使用时会导入到 `auth-profiles.json`）。

更多详情：[/concepts/oauth](/concepts/oauth)

凭证类型：

- `type: "api_key"` → `{ provider, key }`
- `type: "oauth"` → `{ provider, access, refresh, expires, email? }`（部分提供者还包含 `projectId`/`enterpriseUrl`）

## 配置文件 ID

OAuth 登录会创建独立的配置文件，以便多个账户共存。

- 默认：当没有可用邮箱时为 `provider:default`。
- 带邮箱的 OAuth：`provider:<email>`（例如 `google-antigravity:user@gmail.com`）。

配置文件存储在 `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` 的 `profiles` 字段下。

## 轮换顺序

当一个提供者有多个配置文件时，OpenClaw 会按照以下顺序选择：

1. **显式配置**：`auth.order[provider]`（如果已设置）。
2. **配置的配置文件**：`auth.profiles` 过滤后的提供者相关配置。
3. **存储的配置文件**：`auth-profiles.json` 中的提供者相关条目。

如果没有显式配置顺序，OpenClaw 会使用 **轮询顺序**：

- **主要排序键**：配置文件类型（**OAuth 在 API 密钥之前**）。
- **次要排序键**：`usageStats.lastUsed`（每个类型内按最早使用时间排序）。
- **冷却期/禁用的配置文件** 会被移到最后，按最近过期时间排序。

### 会话粘性（缓存友好）

OpenClaw **为每个会话固定选定的认证配置文件**，以保持提供者的缓存处于活跃状态。它不会在每次请求时轮换。固定配置文件会重复使用，直到：

- 会话被重置（`/new` / `/reset`）
- 完成压缩操作（压缩计数增加）
- 配置文件处于冷却期/禁用状态

通过 `/model …@<profileId>` 手动选择会为该会话设置 **用户覆盖**，并在新会话开始前不会自动轮换。

由会话路由器选择的自动固定配置文件被视为 **偏好**：它们会首先尝试，但 OpenClaw 在达到速率限制/超时时可能会切换到其他配置文件。用户固定的配置文件会锁定到该配置文件；如果该配置文件失败且已配置模型回退，OpenClaw 会切换到下一个模型而不是更换配置文件。

### 为什么 OAuth 可能“看起来丢失”

如果你为同一提供者同时拥有 OAuth 配置文件和 API 密钥配置文件，轮询可能在消息之间切换它们，除非固定。要强制使用单一配置文件：

- 使用 `auth.order[provider] = ["provider:profileId"]` 进行固定，或
- 通过 `/model …` 使用会话覆盖（需 UI/聊天界面支持）。

## 冷却期

当配置文件因认证/速率限制错误（或看起来像速率限制的超时）而失败时，OpenClaw 会将其标记为冷却期，并切换到下一个配置文件。格式/无效请求错误（例如 Cloud Code Assist 工具调用 ID 验证失败）被视为可切换的故障，使用相同的冷却期。

冷却期使用指数退避：

- 1 分钟
- 5 分钟
- 25 分钟
- 1 小时（上限）

状态存储在 `auth-profiles.json` 的 `usageStats` 中：

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

计费/信用失败（例如“信用不足” / “信用余额过低”）被视为可切换的故障，但通常不是瞬时的。OpenClaw 会将配置文件标记为 **禁用**（使用更长的退避时间），并切换到下一个配置文件/提供者。

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

- 计费退避从 **5 小时** 开始，每次计费失败时翻倍，上限为 **24 小时**。
- 如果配置文件在 **24 小时** 内未失败，退避计数器会重置（可配置）。

## 模型回退

如果某个提供者的所有配置文件都失败，OpenClaw 会切换到 `agents.defaults.model.fallbacks` 中的下一个模型。这适用于认证失败、速率限制和耗尽配置文件轮换的超时（其他错误不会触发回退）。

当运行时使用模型覆盖（钩子或 CLI）启动时，回退仍会在尝试所有配置的回退后结束于 `agents.defaults.model.primary`。

## 相关配置

查看 [网关配置](/gateway/configuration) 以获取以下内容：

- `auth.profiles` / `auth.order`
- `auth.cooldowns.billingBackoffHours` / `auth.cooldowns.billingBackoffHoursByProvider`
- `auth.cooldowns.billingMaxHours` / `auth.cooldowns.failureWindowHours`
- `agents.defaults.model.primary` / `agents.defaults.model.fallbacks`
- `agents.defaults.imageModel` 路由

查看 [模型](/concepts/models) 以获取更广泛的模型选择和回退概述。