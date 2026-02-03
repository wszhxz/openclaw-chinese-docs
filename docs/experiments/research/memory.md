---
summary: "Research notes: offline memory system for Clawd workspaces (Markdown source-of-truth + derived index)"
read_when:
  - Designing workspace memory (~/.openclaw/workspace) beyond daily Markdown logs
  - Deciding: standalone CLI vs deep OpenClaw integration
  - Adding offline recall + reflection (retain/recall/reflect)
title: "Workspace Memory Research"
---
# 工作区记忆 v2（离线）：研究笔记

目标：Clawd 风格的工作区（`agents.defaults.workspace`，默认 `~/.openclaw/workspace`），其中“记忆”以每天一个 Markdown 文件（`memory/YYYY-MM-DD.md`）形式存储，加上一组小型稳定文件（例如 `memory.md`、`SOUL.md`）。

本文档提出了一种**以离线优先**的记忆架构，将 Markdown 作为规范、可审核的真相来源，但通过派生索引添加了**结构化回忆**（搜索、实体摘要、置信度更新）功能。

## 为何更改？

当前设置（每天一个文件）适用于：

- “只追加”式日记记录
- 人工编辑
- 基于 Git 的持久性 + 可审计性
- 低摩擦记录（“只需写下来”）

其弱点在于：

- 高召回检索（“我们关于 X 做了什么决定？”、“上次尝试 Y 是什么情况？”）
- 以实体为中心的答案（“告诉我关于 Alice / The Castle / warelay 的信息”）而无需重新阅读多个文件
- 观点/偏好稳定性（以及变化时的证据）
- 时间限制（“2025 年 11 月期间什么属实？”）和冲突解决

## 设计目标

- **离线**：无需网络即可运行；可在笔记本电脑/Castle 上运行；无云依赖。
- **可解释性**：检索到的项目应可追溯（文件 + 位置），并可与推理分离。
- **低仪式感**：每日日志保持 Markdown 格式，无需复杂模式工作。
- **渐进式**：v1 仅需全文搜索即可使用；语义/向量和图是可选的升级。
- **适合代理**：使“在 token 预算内回忆”变得容易（返回小事实包）。

## 北极星模型（Hindsight × Letta）

需要融合的两个部分：

1. **Letta/MemGPT 风格的控制循环**

- 保持一个小型“核心”始终在上下文中（人格 + 关键用户事实）
- 其余内容为上下文外，通过工具检索
- 记忆写入是显式工具调用（追加/替换/插入），持久化后在下一轮重新注入

2. **Hindsight 风格的记忆基质**

- 区分观察内容、信念内容和摘要内容
- 支持保留/回忆/反思
- 可随证据演变的带有置信度的观点
- 实体感知检索 + 时间查询（即使没有完整知识图谱）

## 提议的架构（Markdown 真实来源 + 派生索引）

### 规范存储（适合 Git）

保持 `~/.openclaw/workspace` 作为规范的可读记忆。

建议的工作区布局：

```
~/.openclaw/workspace/
  memory.md                    # 小型：持久事实 + 偏好（核心）
  memory/
    YYYY-MM-DD.md              # 每日日志（追加；叙事）
  bank/                        # “类型化”记忆页面（稳定、可审查）
    world.md                   # 关于世界的客观事实
    experience.md              # 代理所做的事（第一人称）
    opinions.md                # 主观偏好/判断 + 置信度 + 证据指针
    entities/
      Peter.md
      The-Castle.md
      warelay.md
      ...
```

说明：

- **每日日志保持每日日志**。无需将其转换为 JSON。
- `bank/` 文件是**精心策划**的，由反思任务生成，仍可手动编辑。
- `memory.md` 保持“小 + 核心”：你希望 Clawd 每次会话都看到的内容。

### 派生存储（机器回忆）

在工作区下添加一个派生索引（不一定需要 Git 跟踪）：

```
~/.openclaw/workspace/.memory/index.sqlite
```

支持以下内容：

- SQLite 模式用于事实 + 实体链接 + 观点元数据
- SQLite **FTS5** 用于词汇回忆（快速、小巧、离线）
- 可选的嵌入表用于语义回忆（仍为离线）

该索引始终**可从 Markdown 重建**。

## 保留 / 回忆 / 反思（操作循环）

### 保留：将每日日志规范化为“事实”

Hindsight 的关键洞察是：存储**叙事、自包含的事实**，而非零碎片段。

`memory/YYYY-MM-DD.md` 的实用规则：

- 在一天结束（或期间）添加一个 `## 保留` 部分，包含 2–5 个项目，这些项目：
  - 叙事（跨回合上下文保留）
  - 自包含（稍后独立有意义）
  - 附加类型 + 实体提及标签

示例：

```
## 保留
- W @Peter: 当前在马拉喀什（2025 年 11 月 27 日至 12 月 1 日）为 Andy 的生日。
- B @warelay: 我通过将 connection.update 处理程序包裹在 try/catch 中修复了 Baileys WS 崩溃（参见 memory/2025-11-27.md）。
- O(c=0.95) @Peter: 偏好 WhatsApp 上简洁的回复（<1500 字符）；长内容存入文件。
```

最小解析：

- 类型前缀：`W`（世界）、`B`（经历/传记）、`O`（观点）、`S`（观察/摘要；通常生成）
- 实体：`@Peter`、`@warelay` 等（slug 映射到 `bank/entities/*.md`）
- 观点置信度：`O(c=0.0..1.0)` 可选

如果你不想让作者思考：反射任务可以从日志其余部分推断这些项目，但拥有显式的 `## 保留` 部分是“质量杠杆”的最简单方式。

### 回忆：对派生索引的查询

回忆应支持：

- **词汇**：“查找精确术语/名称/命令”（FTS5）
- **实体**：“告诉我关于 X”（实体页面 + 实体链接事实）
- **时间**：“2025 年 11 月期间什么属实？”（时间查询）
- **观点**：“关于 X 的观点”（观点置信度演变）

### 反思：对记忆的深度分析

反思应支持：

- **保留**：“保留事实”（叙事事实提取）
- **回忆**：“回忆事实”（四网络记忆）
- **观点**：“观点置信度演变”（观点置信度演变）

## CLI 集成

命令如 `