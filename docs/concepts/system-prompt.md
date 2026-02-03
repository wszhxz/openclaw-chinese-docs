---
summary: "What the OpenClaw system prompt contains and how it is assembled"
read_when:
  - Editing system prompt text, tools list, or time/heartbeat sections
  - Changing workspace bootstrap or skills injection behavior
title: "System Prompt"
---
发送<think>
Okay, I need to translate this entire English text into Chinese. Let me start by reading through the content to understand the context and key terms. The text is about OpenClaw's system prompt structure, modes, workspace bootstrap injection, time handling, skills, and documentation. 

First, I'll go through each section carefully. The main sections are System Prompt, Structure, Prompt modes, Workspace bootstrap injection, Time handling, Skills, and Documentation. Each has sub-sections with specific terminology. 

I need to ensure that technical terms like "Tooling", "Safety", "Skills", "OpenClaw Self-Update", "Workspace", "Documentation", "Sandbox", "Heartbeats", "Runtime", "Reasoning" are accurately translated. Since these are specific to the system, I should check if there are standard translations for such terms in Chinese technical contexts. For example, "Sandbox" is often translated as "沙箱", and "Heartbeats" might be "心跳" in this context.

Next, I'll handle the structure of the document. The original uses markdown with headers and bullet points. I need to maintain the same structure in Chinese, using appropriate headers and list formatting. 

Some parts have code blocks or specific syntax, like the XML example for available skills. I need to ensure that these are preserved in the translation without altering their structure. For instance, the XML tags should remain as they are, but the content inside should be translated.

I also need to pay attention to the nuances in the text. For example, "advisory" in the Safety section should be translated to convey that these are guidelines, not enforced policies. Terms like "hard enforcement" might be translated as "强制执行" to maintain the intended meaning.

Another part to be careful with is the mention of specific files like "AGENTS.md", "SOUL.md", etc. These should remain in their original form as they are file names, but the descriptions around them need translation. 

The time handling section mentions user timezone and time formats. I need to ensure that terms like "time zone" are correctly translated as "时区", and the configuration options like "auto", "12", "24" should be translated appropriately, maybe as "自动", "12小时制", "24小时制".

In the Skills section, the XML structure for available skills needs to be accurately translated, keeping the tags and structure intact. The explanation about how the model uses `read` to load SKILL.md should be clear in Chinese.

For the Documentation section, the mention of public mirrors, source repos, Discord, and ClawHub should be translated, but the URLs like "https://clawhub.com" remain unchanged. The instruction to consult local docs first and run `openclaw status` should be translated to maintain the command structure.

I should also check for consistency in terminology throughout the translation. For example, "system prompt" is consistently translated as "系统提示" or "系统提示语". Ensuring that terms are used consistently will help in maintaining clarity.

Lastly, I'll review the entire translated text to ensure that the meaning is preserved, the structure is maintained, and the technical terms are accurately translated. This will help in delivering a precise and readable Chinese version of the original English text.
</think>

# 系统提示

OpenClaw 为每个代理运行构建自定义的系统提示。该提示由 **OpenClaw 所有**，不使用 p-coding-agent 的默认提示。

该提示由 OpenClaw 组装并注入到每个代理运行中。

## 结构

该提示有意保持紧凑，并使用固定部分：

- **工具**：当前工具列表 + 简要描述。
- **安全**：简短的护栏提醒，以避免寻求权力的行为或绕过监督。
- **技能**（当可用时）：告诉模型如何按需加载技能指令。
- **OpenClaw 自我更新**：如何运行 `config.apply` 和 `update.run`。
- **工作区**：工作目录 (`agents.defaults.workspace`)。
- **文档**：本地 OpenClaw 文档路径（仓库或 npm 包）以及何时阅读它们。
- **工作区文件（注入）**：表明以下包含引导文件。
- **沙箱**（当启用时）：表明沙箱运行时、沙箱路径以及是否可用提升执行。
- **当前日期和时间**：用户本地时间、时区和时间格式。
- **回复标签**：支持提供者的可选回复标签语法。
- **心跳**：心跳提示和确认行为。
- **运行时**：主机、操作系统、节点、模型、仓库根目录（当检测到时）、思考级别（一行）。
- **推理**：当前可见性级别 + /reasoning 切换提示。

系统提示中的安全护栏是建议性的。它们引导模型行为，但不强制执行策略。使用工具策略、执行批准、沙箱和通道白名单进行强制执行；操作员可以通过设计禁用这些功能。

## 提示模式

OpenClaw 可以为子代理渲染较小的系统提示。运行时为每个运行设置一个 `promptMode`（不是面向用户的配置）：

- `full`（默认）：包含以上所有部分。
- `minimal`：用于子代理；省略 **技能**、**记忆回溯**、**OpenClaw 自我更新**、**模型别名**、**用户身份**、**回复标签**、**消息**、**静默回复** 和 **心跳**。工具、**安全**、工作区、沙箱、当前日期和时间（当已知时）、运行时和注入上下文保持可用。
- `none`：仅返回基础身份行。

当 `promptMode=minimal` 时，额外注入的提示会被标记为 **子代理上下文** 而不是 **群聊上下文**。

## 工作区引导注入

引导文件在 **项目上下文** 下被修剪并附加，使模型在无需显式读取的情况下看到身份和配置文件上下文：

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（仅在全新工作区中）

大文件会用标记截断。每个文件的最大大小由 `agents.defaults.bootstrapMaxChars` 控制（默认：20000）。缺失的文件会注入一个简短的缺失文件标记。

内部钩子可以通过 `agent:bootstrap` 拦截此步骤，以修改或替换注入的引导文件（例如将 `SOUL.md` 替换为替代的人格）。

要检查每个注入文件的贡献（原始 vs 注入、截断、加上工具模式开销），使用 `/context list` 或 `/context detail`。参见 [上下文](/concepts/context)。

## 时间处理

系统提示在用户时区已知时包含一个专用的 **当前日期和时间** 部分。为了保持提示缓存稳定，现在仅包含 **时区**（不包含动态时钟或时间格式）。

当代理需要当前时间时，使用 `session_status`；状态卡包含时间戳行。

配置方式如下：

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat`（`auto` | `12` | `24`）

参见 [日期和时间](/date-time) 了解完整行为细节。

## 技能

当有资格的技能存在时，OpenClaw 会注入一个紧凑的 **可用技能列表**（`formatSkillsForPrompt`），其中包含每个技能的 **文件路径**。提示指导模型使用 `read` 读取位于列出位置（工作区、管理或捆绑）的 SKILL.md。如果没有资格的技能，技能部分将被省略。

```
<可用技能>
  <技能>
    <名称>...</名称>
    <描述>...</描述>
    <位置>...</位置>
  </技能>
</可用技能>
```

这在保持基础提示小巧的同时，仍能启用针对性的技能使用。

## 文档

当可用时，系统提示包含一个 **文档** 部分，指向本地 OpenClaw 文档目录（仓库工作区中的 `docs/` 或捆绑的 npm 包文档），并注明公共镜像、源仓库、社区 Discord 和 ClawHub（https://clawhub.com）用于技能发现。提示指导模型首先查阅本地文档以了解 OpenClaw 的行为、命令、配置或架构，并在可能时自行运行 `openclaw status`（仅在无法访问时询问用户）。