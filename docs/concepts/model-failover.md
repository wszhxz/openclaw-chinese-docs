---
summary: "How OpenClaw rotates auth profiles and falls back across models"
read_when:
  - Diagnosing auth profile rotation, cooldowns, or model fallback behavior
  - Updating failover rules for auth profiles or models
title: "Model Failover"
---
# 模型故障转移

OpenClaw 在两个阶段处理故障：

1. 在当前提供方（provider）内进行 **认证配置文件（auth profile）轮换**。  
2. **模型回退（model fallback）** 至 ``agents.defaults.model.fallbacks`` 中的下一个模型。

本文档说明运行时规则及其背后的数据支撑。

## 认证存储（密钥 + OAuth）

OpenClaw 对 API 密钥和 OAuth 令牌均使用 **认证配置文件（auth profiles）**。

- 密钥存储于 ``~/.openclaw/agents/<agentId>/agent/auth-profiles.json``（旧版路径：``~/.openclaw/agent/auth-profiles.json``）。  
- 配置项 ``auth.profiles`` / ``auth.order`` **仅包含元数据与路由信息（不含任何密钥）**。  
- 旧版仅用于导入的 OAuth 文件：``~/.openclaw/credentials/oauth.json``（首次使用时将被导入至 ``auth-profiles.json``）。

更多详情参见：[/concepts/oauth](/concepts/oauth)

凭证类型：

- ``type: "api_key"`` → ``{ provider, key }``  
- ``type: "oauth"`` → ``{ provider, access, refresh, expires, email? }``（部分提供方还需 ``projectId`` / ``enterpriseUrl``）

## 配置文件 ID（Profile IDs）

OAuth 登录会创建独立的配置文件，从而支持多个账号共存。

- 默认值：当无邮箱可用时为 ``provider:default``。  
- 含邮箱的 OAuth：``provider:<email>``（例如 ``google-antigravity:user@gmail.com``）。

配置文件存储于 ``~/.openclaw/agents/<agentId>/agent/auth-profiles.json`` 下的 ``profiles`` 目录中。

## 轮换顺序（Rotation order）

当某提供方存在多个认证配置文件时，OpenClaw 按如下优先级选择顺序：

1. **显式配置**：若设置了 ``auth.order[provider]``，则以此为准。  
2. **已配置的配置文件**：从 ``auth.profiles`` 中按提供方筛选出的配置文件。  
3. **已存储的配置文件**：``auth-profiles.json`` 中属于该提供方的条目。

若未配置显式顺序，OpenClaw 将采用轮询（round-robin）方式排序：

- **主排序键**：配置文件类型（**OAuth 优先于 API 密钥**）。  
- **次排序键**：``usageStats.lastUsed``（同类型中按创建时间升序，即“最老优先”）。  
- **处于冷却期或已禁用的配置文件** 将被移至末尾，并按最早到期时间升序排列。

### 会话粘性（缓存友好型）

OpenClaw **为每个会话固定所选的认证配置文件**，以保持提供方缓存热度。  
它 **不会** 在每次请求时都轮换配置文件。该固定配置文件将持续复用，直至以下任一情况发生：

- 会话被重置（``/new`` / ``/reset``）  
- 完成一次压缩（compaction）操作（压缩计数器递增）  
- 当前配置文件进入冷却期或已被禁用  

通过 ``/model …@<profileId>`` 手动指定配置文件，将为当前会话设置一个 **用户覆盖（user override）**，  
且在新会话开始前 **不会自动轮换**。

由会话路由器自动选定的固定配置文件被视为一种 **偏好（preference）**：  
它们会被优先尝试；但若遭遇速率限制或超时，OpenClaw 可能主动轮换至其他配置文件。  
而由用户手动固定的配置文件则始终锁定于该配置文件；若其失败且已配置模型回退（model fallback），  
OpenClaw 将转向下一个模型，而非切换认证配置文件。

### 为何 OAuth 配置文件可能“看似丢失”

若您对同一提供方同时配置了 OAuth 和 API 密钥两种认证配置文件，则在未固定配置文件的情况下，  
轮询机制可能在不同消息间来回切换二者。如需强制使用单一配置文件：

- 使用 ``auth.order[provider] = ["provider:profileId"]`` 进行固定，或  
- 通过 ``/model …`` 在单个会话中设置配置文件覆盖（需您的 UI / 聊天界面支持该功能）。

## 冷却期（Cooldowns）

当某配置文件因认证失败、速率限制错误（或表现为速率限制的超时）而失败时，  
OpenClaw 将其标记为“冷却中”，并切换至下一个配置文件。  
格式错误/无效请求类错误（例如 Cloud Code Assist 工具调用 ID 校验失败）也被视为可触发故障转移的错误，  
并应用相同的冷却机制。  
兼容 OpenAI 的 stop-reason 错误（如 ``Unhandled stop reason: error``、``stop reason: error`` 和 ``reason: error``）  
同样被归类为超时/故障转移信号。

冷却期采用指数退避策略：

- 1 分钟  
- 5 分钟  
- 25 分钟  
- 1 小时（上限）

状态保存于 ``auth-profiles.json`` 下的 ``usageStats`` 中：

```
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
```

## 计费禁用（Billing disables）

计费/信用额度失败（例如 “余额不足” / “信用额度过低”）同样被视为可触发故障转移的错误，  
但此类错误通常不具备临时性。OpenClaw 不采用短时冷却，而是将该配置文件标记为 **已禁用（disabled）**（启用更长的退避周期），  
并切换至下一个配置文件或提供方。

状态保存于 ``auth-profiles.json`` 中：

```
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
```

默认行为：

- 计费退避起始时间为 **5 小时**，每次计费失败后翻倍，上限为 **24 小时**。  
- 若某配置文件在 **24 小时内未再发生失败**（该时限可配置），则其退避计数器将重置。

## 模型回退（Model fallback）

若某提供方的所有认证配置文件均失败，OpenClaw 将转向 ``agents.defaults.model.fallbacks`` 中的下一个模型。  
此机制适用于认证失败、速率限制及已耗尽所有配置文件轮换后的超时情形（其他错误不触发模型回退）。

当运行启动时指定了模型覆盖（通过 hooks 或 CLI），即使已配置回退链，最终仍将在尝试完所有回退选项后止步于 ``agents.defaults.model.primary``。

## 相关配置

请参阅 [网关配置（Gateway configuration）](/gateway/configuration) 了解以下内容：

- ``auth.profiles`` / ``auth.order``  
- ``auth.cooldowns.billingBackoffHours`` / ``auth.cooldowns.billingBackoffHoursByProvider``  
- ``auth.cooldowns.billingMaxHours`` / ``auth.cooldowns.failureWindowHours``  
- ``agents.defaults.model.primary`` / ``agents.defaults.model.fallbacks``  
- ``agents.defaults.imageModel`` 路由配置  

另请参阅 [模型（Models）](/concepts/models)，获取更全面的模型选择与回退机制概览。