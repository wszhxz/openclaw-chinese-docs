---
summary: "What the OpenClaw system prompt contains and how it is assembled"
read_when:
  - Editing system prompt text, tools list, or time/heartbeat sections
  - Changing workspace bootstrap or skills injection behavior
title: "System Prompt"
---
# 系统提示

OpenClaw 为每个代理运行构建自定义系统提示。该提示由 **OpenClaw 拥有**，不使用 pi-coding-agent 的默认提示。

该提示由 OpenClaw 组装并注入到每个代理运行中。

## 结构

该提示故意简洁，并使用固定部分：

- **工具**: 当前工具列表 + 简短描述。
- **安全**: 短暂的安全提醒，避免寻求权力行为或绕过监督。
- **技能**（如有）: 告诉模型如何按需加载技能指令。
- **OpenClaw 自更新**: 如何运行 `config.apply` 和 `update.run`。
- **工作区**: 工作目录 (`agents.defaults.workspace`)。
- **文档**: OpenClaw 文档（仓库或 npm 包）的本地路径以及何时阅读。
- **工作区文件（注入）**: 表示包含以下引导文件。
- **沙盒**（如启用）: 表示沙盒化运行时、沙盒路径以及是否可用提升执行。
- **当前日期和时间**: 用户本地时间、时区和时间格式。
- **回复标签**: 支持提供者的可选回复标签语法。
- **心跳**: 心跳提示和确认行为。
- **运行时**: 主机、操作系统、节点、模型、仓库根目录（如检测到）、思考级别（一行）。
- **推理**: 当前可见性级别 + /reasoning 切换提示。

系统提示中的安全护栏是建议性的。它们指导模型行为但不强制执行策略。使用工具策略、执行批准、沙盒化和频道白名单进行硬性执行；操作员可以按设计禁用这些功能。

## 提示模式

OpenClaw 可以为子代理渲染更小的系统提示。运行时为每次运行设置一个
`promptMode`（不是用户界面配置）：

- `full`（默认）: 包含上述所有部分。
- `minimal`: 用于子代理；省略 **技能**、**记忆回溯**、**OpenClaw 自更新**、**模型别名**、**用户身份**、**回复标签**、**消息传递**、**静默回复** 和 **心跳**。工具、**安全**、工作区、沙盒、当前日期和时间（已知时）、运行时和注入上下文保持可用。
- `none`: 仅返回基本身份行。

当 `promptMode=minimal` 时，额外注入的提示标记为 **子代理上下文** 而不是 **群聊上下文**。

## 工作区引导注入

引导文件被修剪并附加在 **项目上下文** 下，因此模型可以在不需要显式读取的情况下看到身份和个人资料上下文：

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（仅在全新工作区时）
- `MEMORY.md` 和/或 `memory.md`（当工作区中存在时；可以注入其中一个或两个）

所有这些文件都会在每次轮次中 **注入到上下文窗口**，这意味着它们会消耗令牌。保持简明扼要 — 尤其是 `MEMORY.md`，它可以随着时间增长导致意外的高上下文使用率和更频繁的压缩。

> **注意:** `memory/*.md` 日文件不会 **自动注入**。它们通过 `memory_search` 和 `memory_get` 工具按需访问，因此除非模型显式读取它们，否则不会计入上下文窗口。

大文件会被截断并带有标记。每文件最大大小由 `agents.defaults.bootstrapMaxChars` 控制（默认：20000）。跨文件注入的引导内容总量由 `agents.defaults.bootstrapTotalMaxChars` 限制（默认：150000）。缺失的文件注入一个简短的缺失文件标记。

子代理会话仅注入 `AGENTS.md` 和 `TOOLS.md`（其他引导文件被过滤掉以保持子代理上下文较小）。

内部钩子可以通过 `agent:bootstrap` 拦截此步骤以修改或替换注入的引导文件（例如用替代角色交换 `SOUL.md`）。

要检查每个注入文件的贡献情况（原始 vs 注入、截断以及工具架构开销），使用 `/context list` 或 `/context detail`。参见 [上下文](/concepts/context)。

## 时间处理

当用户时区已知时，系统提示包含一个专用的 **当前日期和时间** 部分。为了保持提示缓存稳定，它现在仅包含 **时区**（无动态时钟或时间格式）。

当代理需要当前时间时使用 `session_status`；状态卡片包含一个时间戳行。

配置方式：

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat` (`auto` | `12` | `24`)

参见 [日期和时间](/date-time) 获取完整行为细节。

## 技能

当存在符合条件的技能时，OpenClaw 注入一个紧凑的 **可用技能列表** (`formatSkillsForPrompt`)，其中包含每个技能的 **文件路径**。提示指示模型使用 `read` 加载列出位置（工作区、管理或捆绑包）的 SKILL.md。如果没有符合条件的技能，则省略技能部分。

```
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
```

这保持了基础提示的简洁性，同时仍然允许有针对性地使用技能。

## 文档

当可用时，系统提示包含一个 **文档** 部分，指向本地 OpenClaw 文档目录（仓库工作区中的 `docs/` 或捆绑包文档），并注明公共镜像、源仓库、社区 Discord 和 ClawHub ([https://clawhub.com](https://clawhub.com)) 以供技能发现。提示指示模型首先咨询本地文档以了解 OpenClaw 的行为、命令、配置或架构，并尽可能运行 `openclaw status` 本身（仅在缺乏访问权限时询问用户）。