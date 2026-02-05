---
summary: "What the OpenClaw system prompt contains and how it is assembled"
read_when:
  - Editing system prompt text, tools list, or time/heartbeat sections
  - Changing workspace bootstrap or skills injection behavior
title: "System Prompt"
---
# 系统提示

OpenClaw 为每个代理运行构建自定义系统提示。该提示由 **OpenClaw** 拥有，并不使用 p-coding-agent 的默认提示。

该提示由 OpenClaw 组装并注入到每个代理运行中。

## 结构

该提示故意简洁，并使用固定部分：

- **Tooling**: 当前工具列表 + 简短描述。
- **Safety**: 避免寻求权力行为或绕过监督的简短防护栏提醒。
- **Skills**（如有）: 告诉模型如何按需加载技能指令。
- **OpenClaw Self-Update**: 如何运行 `config.apply` 和 `update.run`。
- **Workspace**: 工作目录 (`agents.defaults.workspace`)。
- **Documentation**: OpenClaw 文档的本地路径（仓库或 npm 包）以及何时阅读。
- **Workspace Files (injected)**: 表示下方包含引导文件。
- **Sandbox**（如启用）: 表示沙盒化运行时、沙盒路径以及是否可用提升执行。
- **Current Date & Time**: 用户本地时间、时区和时间格式。
- **Reply Tags**: 支持的提供商的可选回复标签语法。
- **Heartbeats**: 心跳提示和确认行为。
- **Runtime**: 主机、OS、节点、模型、仓库根目录（如检测到）、思考级别（一行）。
- **Reasoning**: 当前可见性级别 + /reasoning 切换提示。

系统提示中的安全防护栏是建议性的。它们指导模型行为但不强制执行策略。使用工具策略、执行批准、沙盒化和频道白名单进行硬性执行；操作员可以按设计禁用这些功能。

## 提示模式

OpenClaw 可以为子代理渲染更小的系统提示。运行时为每次运行设置一个
`promptMode`（不是用户界面配置）：

- `full`（默认）: 包含上述所有部分。
- `minimal`: 用于子代理；省略 **Skills**、**Memory Recall**、**OpenClaw
  Self-Update**、**Model Aliases**、**User Identity**、**Reply Tags**、
  **Messaging**、**Silent Replies** 和 **Heartbeats**。工具、**Safety**、
  工作区、沙盒、当前日期和时间（已知时）、运行时和注入上下文保持可用。
- `none`: 仅返回基础身份行。

当 `promptMode=minimal` 时，额外注入的提示标记为 **Subagent
Context** 而不是 **Group Chat Context**。

## 工作区引导注入

引导文件被修剪并附加在 **Project Context** 下，因此模型可以看到身份和个人资料上下文而无需显式读取：

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（仅在全新工作区时）

大文件会被截断并带有标记。每文件最大大小由
`agents.defaults.bootstrapMaxChars` 控制（默认：20000）。缺失的文件注入一个
简短的缺失文件标记。

内部钩子可以通过 `agent:bootstrap` 拦截此步骤以修改或替换
注入的引导文件（例如用替代角色交换 `SOUL.md`）。

要检查每个注入文件的贡献程度（原始与注入、截断加上工具架构开销），使用 `/context list` 或 `/context detail`。参见 [Context](/concepts/context)。

## 时间处理

当用户时区已知时，系统提示包含一个专用的 **Current Date & Time** 部分。为了保持提示缓存稳定，它现在仅包含
**时区**（无动态时钟或时间格式）。

当代理需要当前时间时使用 `session_status`；状态卡片包含一个时间戳行。

配置方式：

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat` (`auto` | `12` | `24`)

参见 [Date & Time](/date-time) 获取完整行为细节。

## 技能

当存在符合条件的技能时，OpenClaw 注入一个紧凑的 **可用技能列表**
(`formatSkillsForPrompt`)，其中包含每个技能的 **文件路径**。提示指示模型使用 `read` 加载列出位置的 SKILL.md（工作区、管理或捆绑）。如果没有符合条件的技能，则省略 Skills 部分。

```
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
```

这使基础提示保持较小，同时仍然支持有针对性的技能使用。

## 文档

当可用时，系统提示包含一个 **Documentation** 部分，指向本地 OpenClaw 文档目录（仓库工作区中的 `docs/` 或捆绑的 npm 包文档），并注明公共镜像、源仓库、社区 Discord 和
ClawHub (https://clawhub.com) 以供技能发现。提示指示模型首先查阅本地文档了解 OpenClaw 的行为、命令、配置或架构，并尽可能运行
`openclaw status` 本身（仅在缺乏访问权限时询问用户）。