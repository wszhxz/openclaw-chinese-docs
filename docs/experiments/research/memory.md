---
summary: "Research notes: offline memory system for Clawd workspaces (Markdown source-of-truth + derived index)"
read_when:
  - Designing workspace memory (~/.openclaw/workspace) beyond daily Markdown logs
  - Deciding: standalone CLI vs deep OpenClaw integration
  - Adding offline recall + reflection (retain/recall/reflect)
title: "Workspace Memory Research"
---
# 工作区记忆 v2（离线）：研究笔记

目标：Clawd 风格的工作区（``agents.defaults.workspace``，默认 ``~/.openclaw/workspace``），其中“记忆”以每日一个 Markdown 文件的形式存储（``memory/YYYY-MM-DD.md``），外加一组少量稳定文件（例如 ``memory.md``、``SOUL.md``）。

本文档提出一种**以离线为优先**的记忆架构：将 Markdown 作为权威的、可供人工审阅的真相来源，同时通过一个派生索引实现**结构化回忆能力**（搜索、实体摘要、置信度更新）。

## 为何要改变？

当前设置（每日一个文件）在以下方面表现优异：

- “仅追加式”日记记录
- 人工编辑
- 基于 Git 的持久性 + 可审计性
- 低摩擦信息捕获（“只需写下来即可”）

但在以下方面存在不足：

- 高召回率检索（“我们关于 X 的决定是什么？”、“上次尝试 Y 是什么时候？”）
- 以实体为中心的回答（“告诉我关于 Alice / The Castle / warelay 的情况”），而无需重读大量文件
- 观点/偏好稳定性（及其变化时的依据）
- 时间约束（“2025 年 11 月期间哪些内容为真？”）与冲突解决

## 设计目标

- **离线可用**：无需网络；可在笔记本电脑或 Castle 上运行；不依赖云服务。
- **可解释**：检索到的条目应可归因（文件 + 位置），且与推理过程分离。
- **低仪式感**：日常日志仍保持 Markdown 格式，无需繁重的模式设计工作。
- **渐进式演进**：v1 版本仅靠全文搜索（FTS）即具实用价值；语义/向量检索及图谱为可选升级项。
- **对智能体友好**：便于在 token 预算内完成回忆（返回精简的事实集合）。

## 北极星模型（Hindsight × Letta）

融合两个关键组件：

1. **Letta/MemGPT 风格的控制循环**

- 始终将少量“核心”内容保留在上下文中（角色设定 + 关键用户事实）
- 其余所有内容均位于上下文之外，并通过工具进行检索
- 记忆写入是显式的工具调用（追加/替换/插入），持久化后于下一轮重新注入

2. **Hindsight 风格的记忆底层架构**

- 明确区分所观察到的内容、所相信的内容与所总结的内容
- 支持保留（Retain）、回忆（Recall）、反思（Reflect）
- 具备置信度支撑的观点，能随新证据演化
- 支持以实体为中心的检索 + 时间查询（即使尚未构建完整知识图谱）

## 提议的架构（Markdown 为真相源 + 派生索引）

### 权威存储（Git 友好）

将 ``~/.openclaw/workspace`` 保持为权威的人类可读记忆。

建议的工作区布局如下：

````
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
````

说明：

- **每日日志仍是每日日志**。无需将其转为 JSON。
- ``bank/`` 文件是**经人工整理的**，由反思任务生成，但仍支持手工编辑。
- ``memory.md`` 保持“体量小 + 核心性强”的特性：即你希望 Clawd 在每次会话中都看到的内容。

### 派生存储（机器级回忆）

在工作区下添加一个派生索引（不一定纳入 Git 跟踪）：

````
~/.openclaw/workspace/.memory/index.sqlite
````

其后端支持包括：

- SQLite 模式，用于存储事实 + 实体链接 + 观点元数据
- SQLite **FTS5**，用于词法级回忆（快速、轻量、离线）
- 可选的嵌入表，用于语义级回忆（仍为离线）

该索引始终**可从 Markdown 文件重建**。

## 保留 / 回忆 / 反思（操作闭环）

### 保留（Retain）：将每日日志规范化为“事实”

Hindsight 在此处的关键洞见是：存储**叙事性、自包含的事实**，而非零散片段。

针对 ``memory/YYYY-MM-DD.md`` 的实操规则：

- 在每日结束时（或过程中），添加一个 ``## Retain`` 小节，包含 2–5 个要点，要求：
  - 具有叙事性（跨轮次上下文得以保留）
  - 自包含（日后单独阅读也具意义）
  - 标注类型 + 实体提及

示例：

````
## Retain
- W @Peter: Currently in Marrakech (Nov 27–Dec 1, 2025) for Andy’s birthday.
- B @warelay: I fixed the Baileys WS crash by wrapping connection.update handlers in try/catch (see memory/2025-11-27.md).
- O(c=0.95) @Peter: Prefers concise replies (&lt;1500 chars) on WhatsApp; long content goes into files.
````

最小化解析规则：

- 类型前缀：``W``（世界）、``B``（经历/传记）、``O``（观点）、``S``（观察/摘要；通常由系统生成）
- 实体：``@Peter``、``@warelay`` 等（slug 映射至 ``bank/entities/*.md``）
- 观点置信度：``O(c=0.0..1.0)``（可选）

若不希望作者手动处理：反思任务可从日志其余部分自动推断这些要点；但显式设立 ``## Retain`` 小节是最易掌控的“质量杠杆”。

### 回忆（Recall）：对派生索引执行查询

回忆功能应支持：

- **词法级**：“查找确切术语 / 名称 / 命令”（使用 FTS5）
- **实体级**：“告诉我关于 X 的情况”（实体页面 + 实体关联的事实）
- **时间级**：“11 月 27 日前后发生了什么？” / “自上周以来……”
- **观点级**：“Peter 更偏好什么？”（附带置信度 + 依据）

返回格式应便于智能体使用，并注明信息来源：

- ``kind``（``world|experience|opinion|observation``）
- ``timestamp``（来源日期，或如存在则提取的时间范围）
- ``entities``（``["Peter","warelay"]``）
- ``content``（叙事性事实）
- ``source``（``memory/2025-11-27.md#L12`` 等）

### 反思（Reflect）：生成稳定页面 + 更新信念

反思是一个定时任务（每日或心跳触发 ``ultrathink``），负责：

- 从近期事实中更新 ``bank/entities/*.md``（实体摘要）
- 基于强化/矛盾证据更新 ``bank/opinions.md`` 的置信度
- 可选地向 ``memory.md``（“核心性”持久事实）提出编辑建议

观点演化（简洁、可解释）：

- 每个观点包含：
  - 表述
  - 置信度 ``c ∈ [0,1]``
  - 最后更新时间
  - 证据链接（支持性 + 矛盾性事实 ID）
- 当新事实到达时：
  - 通过实体重叠 + 相似性匹配候选观点（先用 FTS，再用嵌入）
  - 以小幅增量更新置信度；大幅跃变需强矛盾证据 + 多次重复验证

## CLI 集成：独立运行 vs 深度集成

建议：**在 OpenClaw 中深度集成**，但保留一个可分离的核心库。

### 为何集成进 OpenClaw？

- OpenClaw 已知悉：
  - 工作区路径（``agents.defaults.workspace``）
  - 会话模型 + 心跳机制
  - 日志记录 + 故障排查模式
- 你希望智能体自身调用这些工具：
  - ``openclaw memory recall "…" --k 25 --since 30d``
  - ``openclaw memory reflect --since 7d``

### 为何仍需拆分出独立库？

- 使记忆逻辑可在无网关/运行时环境下独立测试
- 可复用于其他场景（本地脚本、未来桌面应用等）

形态设想：
记忆工具集预期为一个轻量级 CLI + 库层，但目前仅为探索性阶段。

## “S-Collide” / SuCo：何时使用？（研究方向）

若“S-Collide”指代 **SuCo（子空间碰撞）**：这是一种近似最近邻（ANN）检索方法，通过在子空间中采用学习所得/结构化碰撞策略，优化召回率与延迟之间的权衡（论文：arXiv 2411.14754，2024）。

面向 ``~/.openclaw/workspace`` 的务实建议：

- **不要起步就用 SuCo**。
- 从 SQLite FTS +（可选）简单嵌入开始；你将立即获得大部分用户体验提升。
- 仅当满足以下条件时，才考虑 SuCo/HNSW/ScaNN 类方案：
  - 语料库规模庞大（数万至数十万文本块）
  - 暴力嵌入搜索变得过慢
  - 词法搜索已明显成为召回质量瓶颈

离线友好型替代方案（按复杂度递增排列）：

- SQLite FTS5 + 元数据过滤器（零机器学习）
- 嵌入 + 暴力搜索（若文本块数量较少，效果出人意料地好）
- HNSW 索引（通用、稳健；需绑定对应库）
- SuCo（研究级；若已有成熟可嵌入实现，则颇具吸引力）

待解问题：

- 在你的设备（笔记本电脑 + 台式机）上，面向“个人助理记忆”场景，**最佳的离线嵌入模型是什么？**
  - 若你已安装 Ollama：使用本地模型生成嵌入；否则，在工具链中内置一个轻量级嵌入模型。

## 最小可行试点

若你希望一个最小但仍有实用价值的版本：

- 添加 ``bank/`` 实体页面，并在每日日志中加入 ``## Retain`` 小节。
- 使用 SQLite FTS 进行带引用（路径 + 行号）的回忆。
- 仅当回忆质量或数据规模提出更高要求时，再引入嵌入。

## 参考文献

- Letta / MemGPT 概念：“核心记忆块” + “归档记忆” + 工具驱动的自我编辑记忆。
- Hindsight 技术报告：“保留 / 回忆 / 反思”，四网络记忆架构，叙事性事实抽取，观点置信度演化。
- SuCo：arXiv 2411.14754（2024）：“子空间碰撞”近似最近邻检索。