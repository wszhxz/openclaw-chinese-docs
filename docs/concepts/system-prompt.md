---
summary: "What the OpenClaw system prompt contains and how it is assembled"
read_when:
  - Editing system prompt text, tools list, or time/heartbeat sections
  - Changing workspace bootstrap or skills injection behavior
title: "System Prompt"
---
# 系统提示词（System Prompt）

OpenClaw 为每次智能体（agent）运行构建一个自定义的系统提示词。该提示词由 **OpenClaw 拥有**，不使用 `pi-coding-agent` 的默认提示词。

该提示词由 OpenClaw 组装，并注入到每次智能体运行中。

## 结构

该提示词有意设计得简洁紧凑，并采用固定分段结构：

- **工具（Tooling）**：当前可用工具列表及其简短说明。  
- **安全（Safety）**：简短的防护提醒，避免追求权力的行为或绕过监督机制。  
- **技能（Skills）**（如可用）：告知模型如何按需加载技能说明。  
- **OpenClaw 自更新（OpenClaw Self-Update）**：如何运行 ``config.apply`` 和 ``update.run``。  
- **工作区（Workspace）**：当前工作目录（``agents.defaults.workspace``）。  
- **文档（Documentation）**：OpenClaw 文档的本地路径（代码仓库或 npm 包），以及何时应查阅这些文档。  
- **工作区文件（已注入）（Workspace Files (injected)）**：表明引导文件将列于下方。  
- **沙箱（Sandbox）**（如启用）：表明运行环境为沙箱化、沙箱路径，以及是否支持提权执行（elevated exec）。  
- **当前日期与时间（Current Date & Time）**：用户本地时间、时区及时间格式。  
- **回复标签（Reply Tags）**：针对支持的提供商可选的回复标签语法。  
- **心跳机制（Heartbeats）**：心跳提示词及确认（ack）行为。  
- **运行时信息（Runtime）**：主机、操作系统、Node 版本、模型、代码仓库根目录（如可检测到）、思考层级（单行描述）。  
- **推理（Reasoning）**：当前可见性级别 + `/reasoning` 切换提示。

系统提示词中的安全防护栏仅为建议性内容。它们用于引导模型行为，但**不强制执行策略**。如需硬性策略控制，请使用工具策略（tool policy）、执行审批（exec approvals）、沙箱机制（sandboxing）以及通道白名单（channel allowlists）；操作员可按设计禁用这些机制。

## 提示词模式（Prompt modes）

OpenClaw 可为子智能体（sub-agents）生成更小的系统提示词。运行时为每次运行设置一个 ``promptMode``（非面向用户的配置）：

- ``full``（默认）：包含上述全部分段。  
- ``minimal``：用于子智能体；省略 **Skills**、**Memory Recall**、**OpenClaw Self-Update**、**Model Aliases**、**User Identity**、**Reply Tags**、**Messaging**、**Silent Replies** 和 **Heartbeats**。**Tooling**、**Safety**、**Workspace**、**Sandbox**、**Current Date & Time**（如已知）、**Runtime** 及已注入上下文仍保留可用。  
- ``none``：仅返回基础身份行（base identity line）。

当 ``promptMode=minimal`` 时，额外注入的提示词将被标记为 **Subagent Context**（子智能体上下文），而非 **Group Chat Context**（群组聊天上下文）。

## 工作区引导文件注入（Workspace bootstrap injection）

引导文件经裁剪后附加在 **Project Context**（项目上下文）下，使模型无需显式读取即可感知身份与档案上下文：

- ``AGENTS.md``  
- ``SOUL.md``  
- ``TOOLS.md``  
- ``IDENTITY.md``  
- ``USER.md``  
- ``HEARTBEAT.md``  
- ``BOOTSTRAP.md``（仅适用于全新工作区）  
- ``MEMORY.md`` 和/或 ``memory.md``（若存在于工作区中；二者之一或全部均可能被注入）

所有这些文件均在**每一轮对话中注入至上下文窗口**，即会占用 token。请保持其简洁——尤其是 ``MEMORY.md``，它可能随时间增长，导致上下文用量意外升高，并更频繁地触发压缩（compaction）。

> **注意：** ``memory/*.md`` 的每日文件**不会自动注入**。它们通过 ``memory_search`` 和 ``memory_get`` 工具按需访问，因此**除非模型显式读取，否则不计入上下文窗口**。

大文件会被截断并添加标记。单个文件最大大小由 ``agents.defaults.bootstrapMaxChars`` 控制（默认值：20000）。所有引导文件注入内容的总大小上限由 ``agents.defaults.bootstrapTotalMaxChars`` 控制（默认值：150000）。缺失的文件将注入一条简短的“文件缺失”标记。发生截断时，OpenClaw 可在 Project Context 中注入一条警告块；此行为由 ``agents.defaults.bootstrapPromptTruncationWarning`` 控制（可选值：``off``、``once``、``always``；默认值：``once``）。

子智能体会话**仅注入** ``AGENTS.md`` 和 ``TOOLS.md``（其余引导文件会被过滤掉，以保持子智能体上下文精简）。

内部钩子（internal hooks）可通过 ``agent:bootstrap`` 拦截此步骤，以修改或替换已注入的引导文件（例如，将 ``SOUL.md`` 替换为替代人格设定）。

如需检查每个注入文件的贡献量（原始 vs 注入后大小、是否截断、加上工具 schema 开销），可使用 ``/context list`` 或 ``/context detail``。参见 [Context（上下文）](/concepts/context)。

## 时间处理（Time handling）

当用户时区已知时，系统提示词中包含专用的 **Current Date & Time（当前日期与时间）** 分段。为确保提示词缓存稳定，现仅包含**时区信息**（不含动态时钟或时间格式）。

当智能体需要获取当前时间时，请使用 ``session_status``；状态卡片（status card）中包含时间戳行。

配置方式如下：

- ``agents.defaults.userTimezone``  
- ``agents.defaults.timeFormat``（可选值：``auto`` | ``12`` | ``24``）

完整行为细节请参见 [Date & Time（日期与时间）](/date-time)。

## 技能（Skills）

当存在符合条件的技能时，OpenClaw 将注入一份简洁的 **available skills list（可用技能列表）**（``formatSkillsForPrompt``），其中包含每个技能的**文件路径**。提示词指示模型使用 ``read`` 加载所列位置（工作区、托管或内置）下的 `SKILL.md` 文件。若无可适用技能，则完全省略 Skills 分段。

````
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
````

此举在保持基础提示词轻量的同时，仍支持有针对性地调用技能。

## 文档（Documentation）

当文档可用时，系统提示词中将包含一个 **Documentation（文档）** 分段，指向本地 OpenClaw 文档目录（即代码仓库工作区中的 ``docs/``，或打包的 npm 包文档），并同时注明公开镜像站、源代码仓库、社区 Discord 频道，以及技能发现平台 ClawHub（[https://clawhub.com](https://clawhub.com)）。提示词指示模型：  
- 首先查阅本地文档，以了解 OpenClaw 的行为、命令、配置或架构；  
- 在可行时，直接运行 ``openclaw status``（仅在缺乏访问权限时才向用户询问）。