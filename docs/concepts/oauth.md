---
summary: "OAuth in OpenClaw: token exchange, storage, and multi-account patterns"
read_when:
  - You want to understand OpenClaw OAuth end-to-end
  - You hit token invalidation / logout issues
  - You want setup-token or OAuth auth flows
  - You want multiple accounts or profile routing
title: "OAuth"
---
# OAuth

OpenClaw 通过 OAuth 支持“订阅认证”，适用于提供该功能的提供商（特别是 **OpenAI Codex (ChatGPT OAuth)**）。对于 Anthropic 订阅，请使用 **setup-token** 流程。本页说明：

- OAuth **token exchange** 如何工作（PKCE）
- token 存储位置（以及原因）
- 如何处理 **多个账户**（配置文件 + 每会话覆盖）

OpenClaw 还支持自带 OAuth 或 API-key 流程的 **提供商插件**。通过以下方式运行它们：

```bash
openclaw models auth login --provider <id>
```

## Token 汇集点（为什么存在）

OAuth 提供商通常在登录/刷新流程中生成一个新的 **refresh token**。某些提供商（或 OAuth 客户端）可以在为同一用户/应用程序颁发新令牌时使旧的 refresh token 失效。

实际症状：

- 你通过 OpenClaw _和_ 通过 Claude Code / Codex CLI 登录 → 其中一个稍后会随机“登出”

为了减少这种情况，OpenClaw 将 `auth-profiles.json` 视为 **token 汇集点**：

- 运行时从 **一个地方** 读取凭证
- 我们可以保持多个配置文件并确定性地路由它们

## 存储（token 存放位置）

机密信息按 **代理** 存储：

- 认证配置文件（OAuth + API 密钥）：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- 运行时缓存（自动管理；勿编辑）：`~/.openclaw/agents/<agentId>/agent/auth.json`

仅用于导入的旧文件（仍受支持，但不是主要存储）：

- `~/.openclaw/credentials/oauth.json`（首次使用时导入到 `auth-profiles.json`）

上述所有内容也尊重 `$OPENCLAW_STATE_DIR`（状态目录覆盖）。完整参考：[/gateway/configuration](/gateway/configuration#auth-storage-oauth--api-keys)

## Anthropic setup-token（订阅认证）

在任何机器上运行 `claude setup-token`，然后将其粘贴到 OpenClaw 中：

```bash
openclaw models auth setup-token --provider anthropic
```

如果你在其他地方生成了令牌，请手动粘贴：

```bash
openclaw models auth paste-token --provider anthropic
```

验证：

```bash
openclaw models status
```

## OAuth 交换（登录如何工作）

OpenClaw 的交互式登录流程在 `@mariozechner/pi-ai` 中实现，并连接到向导/命令。

### Anthropic (Claude Pro/Max) setup-token

流程形状：

1. 运行 `claude setup-token`
2. 将令牌粘贴到 OpenClaw
3. 作为令牌认证配置文件存储（无刷新）

向导路径是 `openclaw onboard` → 认证选择 `setup-token`（Anthropic）。

### OpenAI Codex (ChatGPT OAuth)

流程形状（PKCE）：

1. 生成 PKCE 验证器/挑战 + 随机 `state`
2. 打开 `https://auth.openai.com/oauth/authorize?...`
3. 尝试捕获回调在 `http://127.0.0.1:1455/auth/callback`
4. 如果回调无法绑定（或你是远程/无头），粘贴重定向 URL/代码
5. 在 `https://auth.openai.com/oauth/token` 交换
6. 从访问令牌中提取 `accountId` 并存储 `{ access, refresh, expires, accountId }`

向导路径是 `openclaw onboard` → 认证选择 `openai-codex`。

## 刷新 + 过期

配置文件存储一个 `expires` 时间戳。

运行时：

- 如果 `expires` 在未来 → 使用存储的访问令牌
- 如果已过期 → 刷新（在文件锁下）并覆盖存储的凭证

刷新流程是自动的；你通常不需要手动管理令牌。

## 多个账户（配置文件）+ 路由

两种模式：

### 1) 推荐：单独的代理

如果你想让“个人”和“工作”永不交互，请使用隔离的代理（单独的会话 + 凭证 + 工作区）：

```bash
openclaw agents add work
openclaw agents add personal
```

然后按代理配置认证（向导）并将聊天路由到正确的代理。

### 2) 高级：单个代理中的多个配置文件

`auth-profiles.json` 支持同一提供商的多个配置文件 ID。

选择使用的配置文件：

- 全局通过配置顺序 (`auth.order`)
- 每会话通过 `/model ...@<profileId>`

示例（会话覆盖）：

- `/model Opus@anthropic:work`

如何查看存在的配置文件 ID：

- `openclaw channels list --json`（显示 `auth[]`）

相关文档：

- [/concepts/model-failover](/concepts/model-failover)（轮换 + 冷却规则）
- [/tools/slash-commands](/tools/slash-commands)（命令界面）