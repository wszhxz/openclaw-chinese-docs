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

OpenClaw 支持通过 OAuth 进行“subscription auth”，适用于提供该功能的提供商（特别是 **OpenAI Codex (ChatGPT OAuth)**）。对于 Anthropic 订阅，请使用 **setup-token** flow。过去 Anthropic 订阅在 Claude Code 之外的使用已被部分用户限制，因此请将其视为用户选择风险并自行核实当前 Anthropic policy。OpenAI Codex OAuth 明确支持在 OpenClaw 等外部工具中使用。本页说明：

对于生产环境中的 Anthropic，API key auth 是比 subscription setup-token auth 更安全、更推荐的路径。

- OAuth **token exchange** 的工作原理（PKCE）
- tokens 的 **stored** 位置（及原因）
- 如何处理 **multiple accounts**（profiles + per-session overrides）

OpenClaw 还支持 **provider plugins**，其自带 OAuth 或 API-key flows。通过以下方式运行它们：

```bash
openclaw models auth login --provider <id>
```

## The token sink（为什么存在）

OAuth 提供商通常在 login/refresh flows 期间生成一个 **new refresh token**。某些提供商（或 OAuth clients）在为同一 user/app 发放新 token 时可能会使旧的 refresh tokens 失效。

实际 symptom：

- 你通过 OpenClaw _和_ Claude Code / Codex CLI log in → 其中之一随后会随机被“logged out”

为了减少这种情况，OpenClaw 将 `auth-profiles.json` 视为 **token sink**：

- runtime 从 **one place** 读取 credentials
- 我们可以保留多个 profiles 并确定性地 route 它们

## Storage（tokens 在哪里）

Secrets 按 **per-agent** 存储：

- Auth profiles（OAuth + API keys + 可选的 value-level refs）：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- Legacy compatibility file：`~/.openclaw/agents/<agentId>/agent/auth.json`
  （发现时会 scrub 静态 `api_key` entries）

Legacy import-only file（仍受支持，但不是主 store）：

- `~/.openclaw/credentials/oauth.json`（首次使用时 imported 到 `auth-profiles.json`）

上述所有内容也 respect `$OPENCLAW_STATE_DIR`（state dir override）。完整参考：[/gateway/configuration](/gateway/configuration#auth-storage-oauth--api-keys)

有关 static secret refs 和 runtime snapshot activation behavior，请参阅 [Secrets Management](/gateway/secrets)。

## Anthropic setup-token（subscription auth）

<Warning>
Anthropic setup-token support is technical compatibility, not a policy guarantee.
Anthropic has blocked some subscription usage outside Claude Code in the past.
Decide for yourself whether to use subscription auth, and verify Anthropic's current terms.
</Warning>

在任何机器上运行 `claude setup-token`，然后将其 paste 到 OpenClaw：

```bash
openclaw models auth setup-token --provider anthropic
```

如果在其他地方 generated 了 token，请手动 paste 它：

```bash
openclaw models auth paste-token --provider anthropic
```

Verify：

```bash
openclaw models status
```

## OAuth exchange（login 工作原理）

OpenClaw 的 interactive login flows 在 `@mariozechner/pi-ai` 中 implemented，并 wired 到 wizards/commands。

### Anthropic setup-token

Flow shape：

1. run `claude setup-token`
2. paste token 到 OpenClaw
3. store 为 token auth profile（no refresh）

Wizard path 是 `openclaw onboard` → auth choice `setup-token`（Anthropic）。

### OpenAI Codex (ChatGPT OAuth)

OpenAI Codex OAuth 明确支持在 Codex CLI 之外使用，包括 OpenClaw workflows。

Flow shape（PKCE）：

1. generate PKCE verifier/challenge + 随机 `state`
2. open `https://auth.openai.com/oauth/authorize?...`
3. try 在 `http://127.0.0.1:1455/auth/callback` 捕获 callback
4. 如果 callback 不能 bind（或你是 remote/headless），paste 重定向 URL/code
5. exchange 在 `https://auth.openai.com/oauth/token`
6. extract `accountId` 从 access token 并 store `{ access, refresh, expires, accountId }`

Wizard path 是 `openclaw onboard` → auth choice `openai-codex`。

## Refresh + expiry

Profiles store 一个 `expires` timestamp。

At runtime：

- 如果 `expires` 在未来 → 使用 stored access token
- 如果 expired → refresh（在 file lock 下）并 overwrite stored credentials

Refresh flow 是 automatic；通常不需要手动 manage tokens。

## Multiple accounts (profiles) + routing

两种 patterns：

### 1) Preferred: separate agents

如果你希望“personal”和“work”永不 interact，使用 isolated agents（separate sessions + credentials + workspace）：

```bash
openclaw agents add work
openclaw agents add personal
```

然后 configure auth per-agent（wizard）并将 chats route 到正确的 agent。

### 2) Advanced: multiple profiles in one agent

`auth-profiles.json` supports 同一 provider 的多个 profile IDs。

Pick 使用哪个 profile：

- 全局通过 config ordering（`auth.order`）
- per-session 通过 `/model ...@<profileId>`

Example（session override）：

- `/model Opus@anthropic:work`

如何查看存在的 profile IDs：

- `openclaw channels list --json`（shows `auth[]`）

Related docs：

- [/concepts/model-failover](/concepts/model-failover)（rotation + cooldown rules）
- [/tools/slash-commands](/tools/slash-commands)（command surface）