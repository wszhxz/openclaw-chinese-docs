---
summary: "What the OpenClaw system prompt contains and how it is assembled"
read_when:
  - Editing system prompt text, tools list, or time/heartbeat sections
  - Changing workspace bootstrap or skills injection behavior
title: "System Prompt"
---
# 系统提示词

OpenClaw 为每次代理运行构建自定义系统提示词。该提示词为 **OpenClaw 所有**，不使用 pi-coding-agent 默认提示词。

该提示词由 OpenClaw 组装并注入到每次代理运行中。

## 结构

提示词故意设计得紧凑并使用固定部分：

- **工具**：当前工具列表 + 简短描述。
- **安全**：简短的护栏提醒，以避免寻求权力行为或绕过监督。
- **技能**（可用时）：告知模型如何按需加载技能指令。
- **OpenClaw 自我更新**：如何运行 `config.apply` 和 `update.run`。
- **工作区**：工作目录 (`agents.defaults.workspace`)。
- **文档**：OpenClaw 文档的本地路径（repo 或 npm 包）以及何时读取它们。
- **工作区文件（注入）**：指示引导文件包含在下面。
- **沙箱**（启用时）：指示沙箱运行时、沙箱路径以及是否可用提升执行。
- **当前日期和时间**：用户本地时间、时区和时间格式。
- **回复标签**：支持提供商的可选回复标签语法。
- **心跳**：心跳提示词和确认行为。
- **运行时**：主机、OS、node、模型、repo 根目录（检测到时）、思考级别（一行）。
- **推理**：当前可见性级别 + /reasoning 切换提示。

系统提示词中的安全护栏是建议性的。它们指导模型行为但不执行政策。使用工具策略、执行批准、沙箱化和通道允许列表进行强制执行；操作员可以根据设计禁用这些。

## 提示词模式

OpenClaw 可以为子代理渲染较小的系统提示词。运行时为每次运行设置一个
`promptMode`（非用户面向配置）：

- `full`（默认）：包含上述所有部分。
- `minimal`：用于子代理；省略 **技能**、**记忆回忆**、**OpenClaw
  自我更新**、**模型别名**、**用户身份**、**回复标签**、
  **消息传递**、**静默回复** 和 **心跳**。工具、**安全**、
  工作区、沙箱、当前日期和时间（已知时）、运行时和注入
  上下文保持可用。
- `none`：仅返回基本身份行。

当 `promptMode=minimal` 时，额外注入的提示词标记为 **子代理
上下文** 而不是 **群聊上下文**。

## 工作区引导注入

引导文件被修剪并附加在 **项目上下文** 下，以便模型看到身份和配置文件上下文而无需显式读取：

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（仅在全新工作区）
- `MEMORY.md` 和/或 `memory.md`（当存在于工作区时；可能注入其中一个或两个）

所有这些文件在每一轮都被 **注入到上下文窗口** 中，这
意味着它们消耗 token。保持它们简洁——尤其是 `MEMORY.md`，它可以
随时间增长并导致意外的高上下文使用和更频繁的
压缩。

> **注意：** `memory/*.md` 每日文件 **不** 自动注入。它们
> 通过 `memory_search` 和 `memory_get` 工具按需访问，因此它们
> 不计入上下文窗口，除非模型显式读取它们。

大文件会被标记截断。每个文件的最大大小由
`agents.defaults.bootstrapMaxChars` 控制（默认：20000）。跨文件的总注入引导
内容由 `agents.defaults.bootstrapTotalMaxChars`
上限（默认：150000）。缺失文件注入简短的缺失文件标记。当截断
发生时，OpenClaw 可以在项目上下文中注入警告块；通过
`agents.defaults.bootstrapPromptTruncationWarning` 控制此功能 (`off`, `once`, `always`;
默认：`once`)。

子代理会话仅注入 `AGENTS.md` 和 `TOOLS.md`（其他引导文件
被过滤掉以保持子代理上下文较小）。

内部钩子可以通过 `agent:bootstrap` 拦截此步骤以变异或替换
注入的引导文件（例如将 `SOUL.md` 交换为替代 persona）。

要检查每个注入文件的贡献量（原始 vs 注入，截断，加上工具 schema 开销），使用 `/context list` 或 `/context detail`。参见 [上下文](/concepts/context)。

## 时间处理

当用户时区已知时，系统提示词包含专用的 **当前日期和时间** 部分。为了
保持提示词缓存稳定，现在仅包含
**时区**（无动态时钟或时间格式）。

当代理需要当前时间时使用 `session_status`；状态卡
包含时间戳行。

配置方式：

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat` (`auto` | `12` | `24`)

参见 [日期和时间](/date-time) 获取完整行为详情。

## 技能

当存在符合条件的技能时，OpenClaw 注入紧凑的 **可用技能列表**
(`formatSkillsForPrompt`)，其中包括每个技能的 **文件路径**。该
提示词指示模型使用 `read` 加载列出的
位置的 SKILL.md（工作区、托管或打包）。如果没有符合条件的技能，则
技能部分被省略。

```
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
```

这保持了基础提示词较小，同时仍能启用定向技能使用。

## 文档

可用时，系统提示词包含 **文档** 部分，指向
本地 OpenClaw 文档目录（repo 工作区中的 `docs/` 或打包的 npm
包文档），并注明公共镜像、源 repo、社区 Discord 和
ClawHub ([https://clawhub.com](https://clawhub.com)) 用于技能发现。提示词指示模型首先查阅本地文档
以了解 OpenClaw 行为、命令、配置或架构，并在可能时自行运行
`openclaw status`（仅在缺乏访问权限时询问用户）。