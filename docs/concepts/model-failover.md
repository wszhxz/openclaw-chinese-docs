---
summary: "How OpenClaw rotates auth profiles and falls back across models"
read_when:
  - Diagnosing auth profile rotation, cooldowns, or model fallback behavior
  - Updating failover rules for auth profiles or models
title: "Model Failover"
---
# 模型故障转移

OpenClaw 处理故障分为两个阶段：

1. 在当前提供商内的 **身份验证配置文件轮换**。
2. 切换到 `agents.defaults.model.fallbacks` 中的下一个模型进行 **模型回退**。

本文档解释了运行时规则及其支持的数据。

## 身份验证存储（密钥 + OAuth）

OpenClaw 使用 **身份验证配置文件** 来处理 API 密钥和 OAuth 令牌。

- 密钥存储在 `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` 中（旧版：`~/.openclaw/agent/auth-profiles.json`）。
- 配置 `auth.profiles` / `auth.order` 仅包含 **元数据 + 路由**（不包含密钥）。
- 仅用于导入的旧版 OAuth 文件：`~/.openclaw/credentials/oauth.json`（首次使用时导入到 `auth-profiles.json`）。

更多详情：[/concepts/oauth](/concepts/oauth)

凭证类型：

- `type: "api_key"` → `{ provider, key }`
- `type: "oauth"` → `{ provider, access, refresh, expires, email? }` (+ `projectId`/`enterpriseUrl` 对于某些提供商）

## 配置文件 ID

OAuth 登录会创建不同的配置文件，以便多个账户可以共存。

- 默认：当没有电子邮件时为 `provider:default`。
- 带有电子邮件的 OAuth：`provider:<email>`（例如 `google-antigravity:user@gmail.com`）。

配置文件存储在 `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` 下的 `profiles` 中。

## 轮换顺序

当一个提供商有多个配置文件时，OpenClaw 会选择如下顺序：

1. **显式配置**：`auth.order[provider]`（如果已设置）。
2. **配置的配置文件**：按提供商过滤后的 `auth.profiles`。
3. **存储的配置文件**：`auth-profiles.json` 中该提供商的条目。

如果没有显式顺序配置，OpenClaw 使用循环顺序：

- **主键**：配置文件类型（**OAuth 优先于 API 密钥**）。
- **次键**：`usageStats.lastUsed`（按时间顺序，每种类型中最旧的优先）。
- **冷却/禁用的配置文件** 移动到最后，按最早过期时间排序。

### 会话粘性（缓存友好）

OpenClaw **为每个会话固定选择的身份验证配置文件** 以保持提供商缓存热。
它不会在每个请求上旋转。固定的配置文件会被重用直到：

- 会话被重置 (`/new` / `/reset`)
- 完成一次压缩（压缩计数增加）
- 配置文件处于冷却/禁用状态

通过 `/model …@<profileId>` 手动选择会为该会话设置一个 **用户覆盖**，并且不会自动旋转，直到开始新会话。

自动固定的配置文件（由会话路由器选择）被视为一种 **偏好**：
它们首先被尝试，但如果遇到速率限制/超时，OpenClaw 可能会切换到另一个配置文件。
用户固定的配置文件会锁定到该配置文件；如果失败且配置了模型回退，OpenClaw 会移动到下一个模型而不是切换配置文件。

### 为什么 OAuth 可能“丢失”

如果您为同一提供商同时拥有 OAuth 配置文件和 API 密钥配置文件，除非固定，否则循环会在消息之间在这两者之间切换。要强制使用单个配置文件：

- 使用 `auth.order[provider] = ["provider:profileId"]` 固定，或
- 通过 `/model …` 使用会话级覆盖并指定配置文件覆盖（当您的 UI/聊天界面支持时）。

## 冷却

当由于身份验证/速率限制错误（或看起来像是速率限制的超时）导致配置文件失败时，OpenClaw 会将其标记为冷却并切换到下一个配置文件。
格式/无效请求错误（例如 Cloud Code Assist 工具调用 ID 验证失败）被视为可故障转移的，并使用相同的冷却机制。

冷却使用指数退避：

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

计费/信用失败（例如“信用不足”/“信用余额太低”）被视为可故障转移的，但通常不是暂时性的。与其使用短暂的冷却，OpenClaw 会将配置文件标记为 **禁用**（具有更长的退避时间），并切换到下一个配置文件/提供商。

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

- 计费退避从 **5 小时** 开始，每次计费失败翻倍，并上限为 **24 小时**。
- 如果配置文件 **24 小时** 内没有失败，则退避计数器重置（可配置）。

## 模型回退

如果某个提供商的所有配置文件都失败，OpenClaw 会切换到 `agents.defaults.model.fallbacks` 中的下一个模型。这适用于身份验证失败、速率限制以及耗尽配置文件轮换的超时（其他错误不会推进回退）。

当使用模型覆盖启动运行（钩子或 CLI）时，即使尝试了任何配置的回退，回退也会在 `agents.defaults.model.primary` 结束。

## 相关配置

参见 [网关配置](/gateway/configuration) 了解：

- `auth.profiles` / `auth.order`
- `auth.cooldowns.billingBackoffHours` / `auth.cooldowns.billingBackoffHoursByProvider`
- `auth.cooldowns.billingMaxHours` / `auth.cooldowns.failureWindowHours`
- `agents.defaults.model.primary` / `agents.defaults.model.fallbacks`
- `agents.defaults.imageModel` 路由

参见 [模型](/concepts/models) 了解更广泛的模型选择和回退概述。