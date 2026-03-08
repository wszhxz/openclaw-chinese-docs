---
title: Formal Verification (Security Models)
summary: Machine-checked security models for OpenClaw’s highest-risk paths.
read_when:
  - Reviewing formal security model guarantees or limits
  - Reproducing or updating TLA+/TLC security model checks
permalink: /security/formal-verification/
---
# 形式化验证（Security Models）

本页面追踪 OpenClaw 的 **形式化安全模型**（目前为 TLA+/TLC；后续按需扩展）。

> 注意：某些旧链接可能指向该项目之前的名称。

**目标（北极星指标）：** 在明确假设下，提供机器检查的论证，证明 OpenClaw 强制执行其预期的安全策略（authorization、session isolation、tool gating 和 misconfiguration safety）。

**这是什么（目前）：** 一个可执行的、由攻击者驱动的 **安全回归测试套件**：

- 每个 claim 都有一个在有限状态空间上可运行的 model-check。
- 许多 claim 都有一个配对的 **负面模型**，可为现实世界的 bug 类生成 counterexample trace。

**这不是什么（尚未）：** 证明"OpenClaw 在所有方面都是安全的”或完整的 TypeScript 实现是正确的。

## Where the models live

模型维护在一个独立的 repo 中：[vignesh07/openclaw-formal-models](https://github.com/vignesh07/openclaw-formal-models)。

## Important caveats

- 这些是 **模型**，而非完整的 TypeScript 实现。模型与代码之间可能存在 drift。
- 结果受 TLC 探索的 state space 限制；"green"并不意味着超出 modeled assumptions 和 bounds 的安全性。
- 某些 claims 依赖于明确的环境假设（例如，正确的 deployment、正确的 configuration inputs）。

## Reproducing results

目前，通过本地克隆 models repo 并运行 TLC 来复现结果（见下文）。未来的迭代可能提供：

- 运行 CI 的模型，带有公共 artifacts（counterexample traces、run logs）
- 用于小型、有界检查的托管"run this model"workflow

Getting started:

```bash
git clone https://github.com/vignesh07/openclaw-formal-models
cd openclaw-formal-models

# Java 11+ required (TLC runs on the JVM).
# The repo vendors a pinned `tla2tools.jar` (TLA+ tools) and provides `bin/tlc` + Make targets.

make <target>
```

### Gateway exposure and open gateway misconfiguration

**Claim：** 在无 auth 的情况下 binding 到 loopback 之外可能导致 remote compromise/增加 exposure；token/password 可阻止 unauth attackers（根据模型假设）。

- Green runs:
  - `make gateway-exposure-v2`
  - `make gateway-exposure-v2-protected`
- Red（预期）:
  - `make gateway-exposure-v2-negative`

另见：模型 repo 中的 `docs/gateway-exposure-matrix.md`。

### Nodes.run pipeline (highest-risk capability)

**Claim：** `nodes.run` 需要 (a) node command allowlist 加上 declared commands 以及 (b) 配置时的 live approval；approvals 被 tokenized 以防止 replay（在模型中）。

- Green runs:
  - `make nodes-pipeline`
  - `make approvals-token`
- Red（预期）:
  - `make nodes-pipeline-negative`
  - `make approvals-token-negative`

### Pairing store (DM gating)

**Claim：** pairing requests 遵守 TTL 和 pending-request caps。

- Green runs:
  - `make pairing`
  - `make pairing-cap`
- Red（预期）:
  - `make pairing-negative`
  - `make pairing-cap-negative`

### Ingress gating (mentions + control-command bypass)

**Claim：** 在需要 mention 的 group contexts 中，未经授权的"control command"无法 bypass mention gating。

- Green:
  - `make ingress-gating`
- Red（预期）:
  - `make ingress-gating-negative`

### Routing/session-key isolation

**Claim：** 来自不同 peers 的 DMs 不会 collapse 到同一个 session 中，除非明确 linked/configured。

- Green:
  - `make routing-isolation`
- Red（预期）:
  - `make routing-isolation-negative`

## v1++: additional bounded models (concurrency, retries, trace correctness)

这些是后续模型，旨在提高对现实世界 failure modes（non-atomic updates、retries 和 message fan-out）的 fidelity。

### Pairing store concurrency / idempotency

**Claim：** pairing store 应强制执行 `MaxPending` 和 idempotency，即使在 interleavings 下（即"check-then-write"必须是 atomic / locked；refresh 不应创建 duplicates）。

这意味着：

- 在 concurrent requests 下，你不能超过通道的 `MaxPending`。
- 对同一 `(channel, sender)` 的重复 requests/refreshes 不应创建重复的 live pending rows。

- Green runs:
  - `make pairing-race` (atomic/locked cap check)
  - `make pairing-idempotency`
  - `make pairing-refresh`
  - `make pairing-refresh-race`
- Red（预期）:
  - `make pairing-race-negative` (non-atomic begin/commit cap race)
  - `make pairing-idempotency-negative`
  - `make pairing-refresh-negative`
  - `make pairing-refresh-race-negative`

### Ingress trace correlation / idempotency

**Claim：** ingestion 应在 fan-out 之间保留 trace correlation，并在 provider retries 下保持 idempotent。

这意味着：

- 当一个 external event 变为多个 internal messages 时，每个部分保持相同的 trace/event identity。
- Retries 不会导致 double-processing。
- 如果 provider event IDs 缺失，dedupe 会 fallback 到安全 key（例如 trace ID）以避免 dropping distinct events。

- Green:
  - `make ingress-trace`
  - `make ingress-trace2`
  - `make ingress-idempotency`
  - `make ingress-dedupe-fallback`
- Red（预期）:
  - `make ingress-trace-negative`
  - `make ingress-trace2-negative`
  - `make ingress-idempotency-negative`
  - `make ingress-dedupe-fallback-negative`

### Routing dmScope precedence + identityLinks

**Claim：** routing 必须默认保持 DM sessions 隔离，仅在明确配置时 collapse sessions（channel precedence + identity links）。

这意味着：

- Channel-specific dmScope overrides 必须胜过 global defaults。
- identityLinks 应仅在明确 linked groups 内 collapse，而不跨越不相关的 peers。

- Green:
  - `make routing-precedence`
  - `make routing-identitylinks`
- Red（预期）:
  - `make routing-precedence-negative`
  - `make routing-identitylinks-negative`