---
summary: "Proposal: long-term command authorization model for ACP-bound conversations"
read_when:
  - Designing native command auth behavior in Telegram/Discord ACP-bound channels/topics
title: "ACP Bound Command Authorization (Proposal)"
---
# ACP 绑定命令授权（提案）

状态：已提出，**尚未实现**。

本文档描述了一种面向 ACP 绑定对话中原生命令的长期授权模型。这是一项实验性提案，并不替代当前生产环境中的行为。

如需了解已实现的行为，请参阅以下源码和测试：

- `src/telegram/bot-native-commands.ts`
- `src/discord/monitor/native-command.ts`
- `src/auto-reply/reply/commands-core.ts`

## 问题

目前我们采用命令特定的检查机制（例如 `/new` 和 `/reset`），这些检查需在允许列表为空时，仍能在 ACP 绑定的频道/主题内正常工作。该方案可缓解当前的用户体验痛点，但基于命令名称的例外处理方式不具备可扩展性。

## 长期架构

将命令授权逻辑从临时性的处理器逻辑，迁移至命令元数据 + 共享策略评估器的组合模式。

### 1) 在命令定义中添加授权策略元数据

每个命令定义都应声明其授权策略。示例结构如下：

```ts
type CommandAuthPolicy =
  | { mode: "owner_or_allowlist" } // default, current strict behavior
  | { mode: "bound_acp_or_owner_or_allowlist" } // allow in explicitly bound ACP conversations
  | { mode: "owner_only" };
```

`/new` 和 `/reset` 将使用 `bound_acp_or_owner_or_allowlist`。  
其余大多数命令则保持为 `owner_or_allowlist`。

### 2) 在各频道间共享一个评估器

引入一个统一的辅助函数，用于基于以下三项进行命令授权评估：

- 命令策略元数据  
- 发送方的授权状态  
- 已解析的会话绑定状态  

Telegram 和 Discord 的原生处理器均应调用该同一辅助函数，以避免行为偏差。

### 3) 使用 binding-match 作为绕过边界

当策略允许绕过绑定的 ACP 时，仅当为当前会话成功解析出配置的 binding match 时才予以授权（而不仅因当前会话密钥“看似”符合 ACP 格式）。

此举可使边界保持显式化，并最大限度减少意外放宽权限的风险。

## 此方案的优势

- 可扩展至未来新增命令，无需再增加基于命令名称的条件判断。  
- 保障各频道间行为的一致性。  
- 通过强制要求显式的 binding match，维持当前的安全模型。  
- 允许列表仍为可选的强化措施，而非普遍必需项。

## 上线计划（未来）

1. 向命令注册类型及命令数据中添加命令授权策略字段。  
2. 实现共享评估器，并迁移 Telegram 与 Discord 的原生处理器。  
3. 将 `/new` 和 `/reset` 迁移至基于元数据驱动的策略。  
4. 针对每种策略模式及各频道接口分别补充测试。

## 非目标事项

- 本提案不改变 ACP 会话生命周期行为。  
- 本提案不要求所有 ACP 绑定命令均启用允许列表。  
- 本提案不更改现有路由绑定语义。

## 说明

本提案刻意采用增量式设计，不会删除或替代任何现有的实验性文档。