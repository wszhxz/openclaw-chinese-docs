---
summary: "Proposal: long-term command authorization model for ACP-bound conversations"
read_when:
  - Designing native command auth behavior in Telegram/Discord ACP-bound channels/topics
title: "ACP Bound Command Authorization (Proposal)"
---
# ACP Bound Command Authorization (Proposal)

状态：Proposed, **not implemented yet**.

本文档描述了 native commands 在 ACP-bound conversations 中的长期 authorization model。这是一个 experiments proposal，并不替换当前的 production behavior。

对于实现的 behavior，请阅读 source 和 tests：

- `src/telegram/bot-native-commands.ts`
- `src/discord/monitor/native-command.ts`
- `src/auto-reply/reply/commands-core.ts`

## Problem

今天我们有 command-specific checks（例如 `/new` 和 `/reset`），这些需要即使在 allowlists 为空的情况下也能在 ACP-bound channels/topics 内工作。这解决了 immediate UX pain，但 command-name-based exceptions 无法 scale。

## Long-term shape

将 command authorization 从 ad-hoc handler logic 移动到 command metadata plus a shared policy evaluator。

### 1) Add auth policy metadata to command definitions

每个 command definition 应该声明一个 auth policy。Example shape：

```ts
type CommandAuthPolicy =
  | { mode: "owner_or_allowlist" } // default, current strict behavior
  | { mode: "bound_acp_or_owner_or_allowlist" } // allow in explicitly bound ACP conversations
  | { mode: "owner_only" };
```

`/new` 和 `/reset` 会使用 `bound_acp_or_owner_or_allowlist`。大多数其他 commands 将保持 `owner_or_allowlist`。

### 2) Share one evaluator across channels

引入一个 helper 来使用以下项评估 command auth：

- command policy metadata
- sender authorization state
- resolved conversation binding state

Both Telegram and Discord native handlers 都应该调用相同的 helper 以避免 behavior drift。

### 3) Use binding-match as the bypass boundary

当 policy 允许 bound ACP bypass 时，仅当为当前 conversation 解析了 configured binding match 时才 authorize（而不仅仅是因为 current session key 看起来像 ACP-like）。

这 keeps the boundary explicit 并 minimizes accidental widening。

## Why this is better

- Scales to future commands without adding more command-name conditionals。
- Keeps behavior consistent across channels。
- Preserves current security model by requiring explicit binding match。
- Keeps allowlists optional hardening instead of a universal requirement。

## Rollout plan (future)

1. 向 command registry types 和 command data 添加 command auth policy field。
2. 实现 shared evaluator 并迁移 Telegram + Discord native handlers。
3. 将 `/new` 和 `/reset` 移动到 metadata-driven policy。
4. 按 policy mode 和 channel surface 添加 tests。

## Non-goals

- 此 proposal 不改变 ACP session lifecycle behavior。
- 此 proposal 不需要所有 ACP-bound commands 的 allowlists。
- 此 proposal 不改变现有的 route binding semantics。

## Note

此 proposal 是 intentionally additive 且不删除或替换现有的 experiments documents。