---
title: Formal Verification (Security Models)
summary: Machine-checked security models for OpenClaw’s highest-risk paths.
permalink: /security/formal-verification/
---
# 形式化验证（安全模型）

本页面跟踪 OpenClaw 的 **形式化安全模型**（当前为 TLA+/TLC；按需添加更多内容）。

> 注意：某些旧链接可能指向之前的项目名称。

**目标（北极星）：** 提供一个机器可验证的论证，证明 OpenClaw 在明确假设下强制执行其预期的安全策略（授权、会话隔离、工具限制和误配置安全）。

**当前是什么：** 一个可执行的、由攻击者驱动的 **安全回归测试套件**：

- 每个声明都有一个可在有限状态空间中运行的模型检查。
- 许多声明配有 **负向模型**，可生成针对现实漏洞类别的反例追踪。

**当前不是（尚且）：** 证明“OpenClaw 在所有方面都安全”或完整的 TypeScript 实现是正确的。

## 模型所在位置

模型维护在单独的仓库中：[vignesh07/openclaw-formal-models](https://github.com/vignesh07/openclaw-formal-models)。

## 重要注意事项

- 这些是 **模型**，而非完整的 TypeScript 实现。模型与代码之间可能存在差异。
- 结果受 TLC 探索的状态空间限制；“绿色”并不意味着超出建模假设和边界的安全性。
- 某些声明依赖于显式的环境假设（例如，正确的部署、正确的配置输入）。

## 重现结果

目前，通过本地克隆模型仓库并运行 TLC 来重现结果（见下文）。未来可能提供：

- 公开工件（反例追踪、运行日志）的 CI 运行模型
- 用于小规模、有限检查的托管“运行此模型”工作流

入门指南：

```bash
git clone https://github.com/vignesh07/openclaw-formal-models
cd openclaw-formal-models

# 需要 Java 11+（TLC 在 JVM 上运行）。
# 仓库内嵌了一个固定版本的 `tla2tools.jar`（TLA+ 工具）并提供 `bin/tlc` + Make 目标。

make <target>
```

### 网关暴露和开放网关配置错误

**声明：** 超出环回接口的绑定且无认证可能使远程入侵成为可能/增加暴露；令牌/密码可阻止未授权攻击者（根据模型假设）。

- 绿色运行：
  - `make gateway-exposure-v2`
  - `make gateway-exposure-v2-protected`
- 红色（预期）：
  - `make gateway-exposure-v2-negative`

详见：模型仓库中的 `docs/gateway-exposure-matrix.md`。

### nodes.run 管道（最高风险功能）

**声明：** `nodes.run` 需要（a）节点命令白名单加声明命令，以及（b）配置时的实时批准；批准通过令牌化防止重放（在模型中）。

- 绿色运行：
  - `make nodes-pipeline`
  - `make approvals-token`
- 红色（预期）：
  - `make nodes-pipeline-negative`
  - `make approvals-token-negative`

### 配对存储（DM 限制）

**声明：** 配对请求需遵守 TTL 和待处理请求上限。

- 绿色运行：
  - `make pairing`
  - `make pairing-cap`
- 红色（预期）：
  - `make pairing-negative`
  - `make pairing-cap-negative`

### 入口限制（提及 + 控制命令绕过）

**声明：** 在需要提及的组上下文中，未经授权的“控制命令”无法绕过提及限制。

- 绿色：
  - `make ingress-gating`
- 红色（预期）：
  - `make ingress-gating-negative`

### 路由/会话密钥隔离

**声明：** 来自不同对等方的 DM 不会合并到同一会话中，除非显式关联/配置。

- 绿色：
  - `make routing-isolation`
- 红色（预期）：
  - `make routing-isolation-negative`

## v1++：附加有限模型（并发、重试、跟踪正确性）

这些是后续模型，旨在更精确地模拟现实中的故障模式（非原子更新、重试和消息广播）。

### 配对存储并发 / 唯一性

**声明：** 配对存储即使在交错请求下也应强制执行 `MaxPending` 和唯一性（即，“检查后写入”必须原子/锁定；刷新不应创建重复项）。

含义：

- 在并发请求下，不能超过某个通道的 `MaxPending`。
- 对于相同 `(channel, sender)` 的重复请求/刷新不应创建重复的待处理行。

- 绿色运行：
  - `make pairing-race`（原子/锁定上限检查）
  - `make pairing-idempotency`
  - `make pairing-refresh`
  - `make pairing-refresh-race`
- 红色（预期）：
  - `make pairing-race-negative`（非原子的开始/提交上限竞争）
  - `make pairing-idempotency-negative`
  - `make pairing-refresh-negative`
  - `make pairing-refresh-race-negative`

### 入口跟踪关联 / 唯一性

**声明：** 入口应保留跟踪关联性，即使在广播中也应唯一。

含义：

- 当一个外部事件变成多个内部消息时，每个部分都保持相同的跟踪/事件标识。
- 重试不会导致双重处理。
- 如果提供者事件 ID 缺失，去重将回退到安全键（例如，跟踪 ID）以避免丢弃不同事件。

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

### 路由 dmScope 优先级 + 身份链接

**声明：** 路由必须默认隔离 DM 会话，仅在显式配置时合并会话（通道优先级 + 身份链接）。

含义：

- 通道特定的 dmScope 覆盖必须胜过全局默认值。
- identityLinks 应仅在显式链接的组内合并，而不是跨无关对等方。

- 绿色：
  - `make routing-precedence`
  - `make routing-