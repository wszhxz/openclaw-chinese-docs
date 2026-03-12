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

OpenClaw 通过 OAuth 支持“订阅认证”（subscription auth），适用于提供该功能的供应商（ notably **OpenAI Codex（ChatGPT OAuth）**）。对于 Anthropic 订阅，请使用 **setup-token** 流程。过去，部分用户在 Claude Code 之外使用 Anthropic 订阅已被限制，因此请将其视为用户自主选择的风险，并自行核实当前 Anthropic 政策。OpenAI Codex OAuth 明确支持在 OpenClaw 等外部工具中使用。本文档说明：

对于生产环境中的 Anthropic，相比订阅 setup-token 认证，API 密钥认证是更安全、更受推荐的方式。

- OAuth **令牌交换**（token exchange）的工作原理（PKCE）
- 令牌的**存储位置**（及原因）
- 如何处理**多个账户**（配置文件 + 每会话覆盖）

OpenClaw 还支持自带 OAuth 或 API 密钥流程的**供应商插件**（provider plugins）。可通过以下方式运行：

```bash
openclaw models auth login --provider <id>
```

## 令牌接收器（token sink）（为何存在）

OAuth 供应商在登录/刷新流程中通常会为用户颁发一个**新的刷新令牌**（refresh token）。某些供应商（或 OAuth 客户端）在为同一用户/应用颁发新刷新令牌时，可能会使旧的刷新令牌失效。

实际表现如下：

- 你同时通过 OpenClaw 和 Claude Code / Codex CLI 登录 → 其中一个客户端之后会随机“登出”

为降低此类问题发生概率，OpenClaw 将 `auth-profiles.json` 视为一个**令牌接收器（token sink）**：

- 运行时仅从**单一位置**读取凭证
- 我们可维护多个配置文件，并以确定性方式对其进行路由

## 存储（令牌存放位置）

密钥按**代理（agent）** 分别存储：

- 认证配置文件（OAuth + API 密钥 + 可选的值级引用）：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- 向后兼容的旧版文件：`~/.openclaw/agents/<agentId>/agent/auth.json`  
  （发现后将自动清除静态 `api_key` 条目）

仅用于导入的旧版文件（仍受支持，但非主存储）：

- `~/.openclaw/credentials/oauth.json`（首次使用时导入至 `auth-profiles.json`）

以上所有路径均同时尊重 `$OPENCLAW_STATE_DIR`（状态目录覆盖）。完整参考：[/gateway/configuration](/gateway/configuration#auth-storage-oauth--api-keys)

有关静态密钥引用和运行时快照激活行为，请参阅 [密钥管理（Secrets Management）](/gateway/secrets)。

## Anthropic setup-token（订阅认证）

<Warning>
Anthropic setup-token support is technical compatibility, not a policy guarantee.
Anthropic has blocked some subscription usage outside Claude Code in the past.
Decide for yourself whether to use subscription auth, and verify Anthropic's current terms.
</Warning>

在任意机器上运行 `claude setup-token`，然后将结果粘贴至 OpenClaw：

```bash
openclaw models auth setup-token --provider anthropic
```

若你在其他地方生成了该令牌，请手动粘贴：

```bash
openclaw models auth paste-token --provider anthropic
```

验证：

```bash
openclaw models status
```

## OAuth 交换（登录工作原理）

OpenClaw 的交互式登录流程实现在 `@mariozechner/pi-ai` 中，并已集成至向导（wizards）与命令中。

### Anthropic setup-token

流程结构如下：

1. 运行 `claude setup-token`
2. 将令牌粘贴至 OpenClaw
3. 作为令牌认证配置文件存储（无刷新机制）

向导路径为 `openclaw onboard` → 认证选项 `setup-token`（Anthropic）。

### OpenAI Codex（ChatGPT OAuth）

OpenAI Codex OAuth 明确支持在 Codex CLI 之外使用，包括 OpenClaw 工作流。

流程结构（PKCE）：

1. 生成 PKCE 校验器/挑战值（verifier/challenge）及随机 `state`
2. 打开 `https://auth.openai.com/oauth/authorize?...`
3. 尝试捕获 `http://127.0.0.1:1455/auth/callback` 上的回调
4. 若回调无法绑定（或你处于远程/无头环境），请粘贴重定向 URL/代码
5. 在 `https://auth.openai.com/oauth/token` 处执行交换
6. 从访问令牌中提取 `accountId`，并存储 `{ access, refresh, expires, accountId }`

向导路径为 `openclaw onboard` → 认证选项 `openai-codex`。

## 刷新与过期

配置文件中存储一个 `expires` 时间戳。

运行时：

- 若 `expires` 尚未到达 → 使用已存储的访问令牌
- 若已过期 → 在文件锁保护下执行刷新，并覆写已存储的凭证

刷新流程全自动；通常无需手动管理令牌。

## 多账户（配置文件）与路由

两种模式：

### 1）推荐方式：独立代理（separate agents）

若希望“个人”与“工作”账户完全互不干扰，请使用隔离的代理（独立会话 + 凭证 + 工作区）：

```bash
openclaw agents add work
openclaw agents add personal
```

然后为每个代理分别配置认证（通过向导），并将聊天路由至对应代理。

### 2）高级方式：单个代理内多个配置文件

`auth-profiles.json` 支持为同一供应商指定多个配置文件 ID。

选择所用配置文件的方式如下：

- 全局方式：通过配置顺序（`auth.order`）
- 每会话方式：通过 `/model ...@<profileId>`

示例（会话覆盖）：

- `/model Opus@anthropic:work`

如何查看现有配置文件 ID：

- `openclaw channels list --json`（显示 `auth[]`）

相关文档：

- [/concepts/model-failover](/concepts/model-failover)（轮换 + 冷却规则）
- [/tools/slash-commands](/tools/slash-commands)（命令界面）