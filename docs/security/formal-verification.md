---
title: Formal Verification (Security Models)
summary: Machine-checked security models for OpenClaw’s highest-risk paths.
permalink: /security/formal-verification/
---
# 形式验证（安全模型）

此页面跟踪OpenClaw的**形式安全模型**（目前为TLA+/TLC；根据需要添加更多）。

> 注意：某些旧链接可能引用之前的项目名称。

**目标（北极星）：** 提供一个机器可检查的论据，证明OpenClaw在其预期的安全策略（授权、会话隔离、工具门控和误配置安全性）下运行，基于明确的假设。

**这是什么（今天）：** 一个可执行的、攻击者驱动的**安全回归套件**：

- 每个声明都有一个在有限状态空间上的可运行模型检查。
- 许多声明都有一个配对的**负面模型**，可以生成现实错误类别的反例跟踪。

**这不是什么（还）：** 一个证明“OpenClaw在所有方面都是安全的”或完整TypeScript实现正确的证明。

## 模型存放位置

模型维护在一个单独的仓库中：[vignesh07/openclaw-formal-models](https://github.com/vignesh07/openclaw-formal-models)。

## 重要注意事项

- 这些是**模型**，不是完整的TypeScript实现。模型和代码之间可能存在差异。
- 结果受TLC探索的状态空间限制；“绿色”并不意味着超出建模假设和界限的安全性。
- 某些声明依赖于显式的环境假设（例如，正确的部署，正确的配置输入）。

## 复现结果

今天，通过本地克隆模型仓库并运行TLC来复现结果（见下文）。未来迭代可以提供：

- CI运行的模型，带有公共工件（反例跟踪，运行日志）
- 托管的“运行此模型”工作流程，适用于小型、有界的检查

入门：

```bash
git clone https://github.com/vignesh07/openclaw-formal-models
cd openclaw-formal-models

# Java 11+ required (TLC runs on the JVM).
# The repo vendors a pinned `tla2tools.jar` (TLA+ tools) and provides `bin/tlc` + Make targets.

make <target>
```

### 网关暴露和开放网关误配置

**声明：** 在没有身份验证的情况下绑定到回环之外可能会使远程攻击成为可能/增加暴露；令牌/密码阻止未经授权的攻击者（根据模型假设）。

- 绿色运行：
  - `make gateway-exposure-v2`
  - `make gateway-exposure-v2-protected`
- 红色（预期）：
  - `make gateway-exposure-v2-negative`

另见：模型仓库中的`docs/gateway-exposure-matrix.md`。

### Nodes.run管道（最高风险功能）

**声明：** `nodes.run`需要（a）节点命令白名单加上声明的命令和（b）配置时的实时批准；批准被标记化以防止重放（在模型中）。

- 绿色运行：
  - `make nodes-pipeline`
  - `make approvals-token`
- 红色（预期）：
  - `make nodes-pipeline-negative`
  - `make approvals-token-negative`

### 配对存储（DM门控）

**声明：** 配对请求尊重TTL和待处理请求上限。

- 绿色运行：
  - `make pairing`
  - `make pairing-cap`
- 红色（预期）：
  - `make pairing-negative`
  - `make pairing-cap-negative`

### 入站门控（提及 + 控制命令绕过）

**声明：** 在需要提及的组上下文中，未经授权的“控制命令”不能绕过提及门控。

- 绿色：
  - `make ingress-gating`
- 红色（预期）：
  - `make ingress-gating-negative`

### 路由/会话密钥隔离

**声明：** 来自不同对等体的DM不会合并到同一个会话中，除非显式链接/配置。

- 绿色：
  - `make routing-isolation`
- 红色（预期）：
  - `make routing-isolation-negative`

## v1++：附加的有界模型（并发、重试、跟踪正确性）

这些后续模型围绕现实世界故障模式（非原子更新、重试和消息扇出）提高了保真度。

### 配对存储并发性 / 幂等性

**声明：** 配对存储应在交错情况下强制执行`MaxPending`和幂等性（即，“检查-然后写入”必须是原子/锁定的；刷新不应创建重复项）。

这意味着：

- 在并发请求下，您不能超过`MaxPending`的通道限制。
- 对同一`(channel, sender)`的重复请求/刷新不应创建重复的活动待处理行。

- 绿色运行：
  - `make pairing-race`（原子/锁定的限制检查）
  - `make pairing-idempotency`
  - `make pairing-refresh`
  - `make pairing-refresh-race`
- 红色（预期）：
  - `make pairing-race-negative`（非原子开始/提交限制竞争）
  - `make pairing-idempotency-negative`
  - `make pairing-refresh-negative`
  - `make pairing-refresh-race-negative`

### 入站跟踪关联 / 幂等性

**声明：** 摄取应跨扇出保持跟踪关联，并在提供者重试下保持幂等性。

这意味着：

- 当一个外部事件变成多个内部消息时，每个部分保持相同的跟踪/事件标识。
- 重试不会导致双重处理。
- 如果提供者事件ID缺失，去重将回退到一个安全键（例如，跟踪ID），以避免丢弃不同的事件。

- 绿色：
  - `make ingress-trace`
  - `make ingress-trace2`
  - `make ingress-idempotency`
  - `make ingress-dedupe-fallback`
- 红色（预期）：
  - `make ingress-trace-negative`
  - `make ingress-trace2-negative`
  - `make ingress-idempotency-negative`
  - `make ingress-dedupe-fallback-negative`

### 路由 dmScope优先级 + identityLinks

**声明：** 路由必须默认隔离DM会话，并且仅在显式配置时合并会话（通道优先级 + 身份链接）。

这意味着：

- 特定通道的dmScope覆盖必须优于全局默认值。
- identityLinks应在显式链接的组内合并，而不是跨不相关的对等体。

- 绿色：
  - `make routing-precedence`
  - `make routing-identitylinks`
- 红色（预期）：
  - `make routing-precedence-negative`
  - `make routing-identitylinks-negative`