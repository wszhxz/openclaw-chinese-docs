---
summary: "Research notes: offline memory system for Clawd workspaces (Markdown source-of-truth + derived index)"
read_when:
  - Designing workspace memory (~/.openclaw/workspace) beyond daily Markdown logs
  - Deciding: standalone CLI vs deep OpenClaw integration
  - Adding offline recall + reflection (retain/recall/reflect)
title: "Workspace Memory Research"
---
# 工作区内存 v2 (离线): 研究笔记

目标: Clawd 风格的工作区 (`agents.defaults.workspace`, 默认 `~/.openclaw/workspace`)，其中“内存”以每天一个 Markdown 文件的形式存储 (`memory/YYYY-MM-DD.md`) 加上一组稳定的文件 (例如 `memory.md`, `SOUL.md`)。

本文档提出了一种**以离线为主**的内存架构，保持 Markdown 作为权威、可审查的事实来源，但通过派生索引添加**结构化回忆**（搜索、实体摘要、置信度更新）。

## 为什么改变？

当前设置（每天一个文件）非常适合：

- “仅追加”日记记录
- 人工编辑
- 基于 git 的持久性和可审计性
- 低摩擦捕获（“只需写下来”）

它较弱的地方在于：

- 高召回检索（“我们对 X 的决定是什么？”，“上次尝试 Y 是什么情况？”）
- 实体中心的答案（“告诉我关于 Alice / The Castle / warelay 的信息”）而无需重新阅读许多文件
- 意见/偏好稳定性（以及变化时的证据）
- 时间限制（“2025 年 11 月的情况是什么？”）和冲突解决

## 设计目标

- **离线**: 不需要网络；可以在笔记本电脑/Castle 上运行；没有云依赖。
- **可解释性**: 检索的项目应可追溯（文件 + 位置），并与其推理结果分开。
- **低仪式**: 日常日志保持 Markdown 格式，不需要复杂的模式工作。
- **增量**: v1 仅使用 FTS 即可有用；语义/向量和图是可选升级。
- **代理友好**: 使“在令牌预算内回忆”变得容易（返回小的事实包）。

## 北斗星模型 (Hindsight × Letta)

两个部分结合：

1. **Letta/MemGPT 风格的控制循环**

- 保持一个小的“核心”始终在上下文中（角色 + 关键用户事实）
- 其余内容均在上下文之外并通过工具检索
- 内存写入是显式的工具调用（追加/替换/插入），持久化，然后在下一轮重新注入

2. **Hindsight 风格的内存底座**

- 分离观察到的内容与相信的内容与总结的内容
- 支持保留/回忆/反思
- 带有置信度的意见可以根据证据演变
- 实体感知检索 + 时间查询（即使没有完整的知识图谱）

## 提议的架构（Markdown 源事实 + 派生索引）

### 规范存储（git 友好）

保持 `~/.openclaw/workspace` 作为规范的人类可读内存。

建议的工作区布局：

```
~/.openclaw/workspace/
  memory.md                    # small: durable facts + preferences (core-ish)
  memory/
    YYYY-MM-DD.md              # daily log (append; narrative)
  bank/                        # “typed” memory pages (stable, reviewable)
    world.md                   # objective facts about the world
    experience.md              # what the agent did (first-person)
    opinions.md                # subjective prefs/judgments + confidence + evidence pointers
    entities/
      Peter.md
      The-Castle.md
      warelay.md
      ...
```

注意：

- **日常日志保持日常日志**。不需要将其转换为 JSON。
- `bank/` 文件是**策划**的，由反思任务生成，仍然可以手动编辑。
- `memory.md` 保持“小 + 核心”的：你希望 Clawd 在每次会话中看到的东西。

### 派生存储（机器回忆）

在工作区下添加一个派生索引（不一定被 git 跟踪）：

```
~/.openclaw/workspace/.memory/index.sqlite
```

使用以下支持：

- SQLite 模式用于事实 + 实体链接 + 意见元数据
- SQLite **FTS5** 用于词法回忆（快速、小巧、离线）
- 可选的嵌入表用于语义回忆（仍然离线）

索引总是可以从 Markdown **重建**。

## 保留 / 回忆 / 反思（操作循环）

### 保留: 将日常日志规范化为“事实”

Hindsight 的关键见解：存储**叙述性的、自包含的事实**，而不是小片段。

`memory/YYYY-MM-DD.md` 的实用规则：

- 在一天结束时（或期间），添加一个 `## Retain` 部分，包含 2–5 个要点，这些要点是：
  - 叙述性的（跨回合上下文保留）
  - 自包含的（单独看有意义）
  - 标记类型 + 实体提及

示例：

```
## Retain
- W @Peter: Currently in Marrakech (Nov 27–Dec 1, 2025) for Andy’s birthday.
- B @warelay: I fixed the Baileys WS crash by wrapping connection.update handlers in try/catch (see memory/2025-11-27.md).
- O(c=0.95) @Peter: Prefers concise replies (&lt;1500 chars) on WhatsApp; long content goes into files.
```

最小解析：

- 类型前缀: `W` (世界), `B` (经验/传记), `O` (意见), `S` (观察/摘要；通常生成)
- 实体: `@Peter`, `@warelay` 等（slug 映射到 `bank/entities/*.md`）
- 意见置信度: `O(c=0.0..1.0)` 可选

如果你不想让作者考虑这些：反射任务可以从日志的其余部分推断这些要点，但有一个明确的 `## Retain` 部分是最简单的“质量杠杆”。

### 回忆: 对派生索引进行查询

回忆应支持：

- **词法**: “查找确切的术语 / 名称 / 命令” (FTS5)
- **实体**: “告诉我关于 X 的信息” (实体页面 + 实体链接的事实)
- **时间**: “11 月 27 日左右发生了什么” / “自从上周以来”
- **意见**: “Peter 更喜欢什么？” (带有置信度 + 证据)

返回格式应代理友好并引用来源：

- `kind` (`world|experience|opinion|observation`)
- `timestamp` (源日期，或如果存在则提取的时间范围)
- `entities` (`["Peter","warelay"]`)
- `content` (叙述性事实)
- `source` (`memory/2025-11-27.md#L12` 等)

### 反思: 生成稳定页面 + 更新信念

反思是一个计划任务（每日或心跳 `ultrathink`），它：

- 从最近的事实更新 `bank/entities/*.md`（实体摘要）
- 根据强化/矛盾更新 `bank/opinions.md` 置信度
- 可选地建议对 `memory.md` 进行编辑（“核心”的持久事实）

意见演变（简单、可解释）：

- 每个意见都有：
  - 陈述
  - 置信度 `c ∈ [0,1]`
  - 最后更新时间
  - 证据链接（支持 + 反对的事实 ID）
- 当新事实到达时：
  - 通过实体重叠 + 相似性找到候选意见（首先使用 FTS，稍后使用嵌入）
  - 通过小增量更新置信度；大跳跃需要强烈矛盾 + 重复证据

## CLI 集成：独立 vs 深度集成

建议：在 OpenClaw 中进行**深度集成**，但保持一个可分离的核心库。

### 为什么集成到 OpenClaw？

- OpenClaw 已经知道：
  - 工作区路径 (`agents.defaults.workspace`)
  - 会话模型 + 心跳
  - 日志记录 + 故障排除模式
- 你希望代理本身调用工具：
  - `openclaw memory recall "…" --k 25 --since 30d`
  - `openclaw memory reflect --since 7d`

### 为什么仍然拆分一个库？

- 保持内存逻辑在没有网关/运行时的情况下可测试
- 从其他上下文重用（本地脚本、未来的桌面应用程序等）

形状：
内存工具旨在成为一个小型 CLI + 库层，但这只是探索性的。

## “S-Collide” / SuCo: 何时使用它（研究）

如果“S-Collide”指的是 **SuCo (Subspace Collision)**：这是一种 ANN 检索方法，通过在子空间中使用学习/结构化的碰撞来实现强召回/延迟权衡（论文: arXiv 2411.14754, 2024）。

`~/.openclaw/workspace` 的务实观点：

- **不要从** SuCo 开始。
- 从 SQLite FTS + （可选）简单嵌入开始；你会立即获得大部分 UX 改进。
- 仅在以下情况下考虑 SuCo/HNSW/ScaNN 类解决方案：
  - 语料库很大（数万到数十万块）
  - 暴力嵌入搜索变得太慢
  - 召回质量显著受词法搜索瓶颈

离线友好的替代方案（按复杂性递增）：

- SQLite FTS5 + 元数据过滤器（零 ML）
- 嵌入 + 暴力搜索（如果块数量较低，效果出乎意料的好）
- HNSW 索引（常见，稳健；需要库绑定）
- SuCo（研究级；如果有一个可靠的实现可以嵌入，则具有吸引力）

开放问题：

- 你机器（笔记本电脑 + 桌面）上“个人助理内存”的**最佳**离线嵌入模型是什么？
  - 如果你已经有 Ollama：使用本地模型嵌入；否则在工具链中附带一个小的嵌入模型。

## 最小有用的试点

如果你想有一个最小但仍然有用的版本：

- 添加 `bank/` 实体页面和每日日志中的 `## Retain` 部分。
- 使用 SQLite FTS 进行带引用的回忆（路径 + 行号）。
- 仅在回忆质量和规模需求时添加嵌入。

## 参考资料

- Letta / MemGPT 概念：“核心记忆块” + “归档记忆” + 工具驱动的自我编辑记忆。
- Hindsight 技术报告：“保留 / 回忆 / 反思”，四网络记忆，叙述性事实提取，意见置信度演变。
- SuCo: arXiv 2411.14754 (2024): “子空间碰撞”近邻检索。