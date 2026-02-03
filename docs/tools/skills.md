---
summary: "Skills: managed vs workspace, gating rules, and config/env wiring"
read_when:
  - Adding or modifying skills
  - Changing skill gating or load rules
title: "Skills"
---
# 技能（OpenClaw）

OpenClaw 使用 **[AgentSkills](https://agentskills.io)-兼容** 的技能文件夹来教代理如何使用工具。每个技能是一个包含 `SKILL.md` 的目录，其中包含 YAML 前置信息和说明。OpenClaw 会加载 **捆绑技能** 加上可选的本地覆盖，并在加载时根据环境、配置和二进制文件存在情况过滤这些技能。

## 位置和优先级

技能从 **三个** 地方加载：

1. **捆绑技能**：随安装一起提供（npm 包或 OpenClaw.app）
2. **管理/本地技能**：`~/.openclaw/skills`
3. **工作区技能**：`<workspace>/skills`

如果技能名称冲突，优先级为：

`<workspace>/skills`（最高）→ `~/.openclaw/skills` → 捆绑技能（最低）

此外，您可以通过 `skills.load.extraDirs` 在 `~/.openclaw/openclaw.json` 中配置额外的技能文件夹（最低优先级）。

## 每个代理 vs 共享技能

在 **多代理** 设置中，每个代理都有自己的工作区。这意味着：

- **每个代理的技能** 仅存在于该代理的 `<workspace>/skills` 中。
- **共享技能** 存在于 `~/.openclaw/skills`，在名称冲突时会覆盖工作区技能。

## 插件和技能

OpenClaw 的 `openclaw.plugin.json` 文件用于定义插件配置。`metadata.openclaw.requires.config` 是用于指定配置项的键。

## 安全注意事项

OpenClaw 支持 **沙箱化运行**，确保环境变量和配置的安全性。`primaryEnv` 和 `secondaryEnv` 分别表示主环境变量和次环境变量。

## 格式（AgentSkills + Pi 兼容）

技能格式需遵循特定的 YAML 前置信息规范。例如，`SKILL.md` 文件中的 YAML 前置信息应包含技能名称、描述和位置等信息。

## 加载时的过滤（load-time filters）

技能加载时，OpenClaw 会根据 `metadata.openclaw.requires.bins` 和 `metadata.openclaw.requires.env` 等配置项进行过滤，确保仅加载符合条件的技能。

## 配置覆盖

在 `~/.openclaw/openclaw.json` 中，您可以配置技能的启用状态、环境变量和自定义配置项。例如：

```json5
{
  skills: {
    entries: {
      "my-skill": { enabled: true },
      "another-skill": { enabled: false }
    }
  }
}
```

## 环境变量注入（每个代理运行）

当代理运行开始时，OpenClaw 会：

1. 读取技能元数据。
2. 将 `skills.entries.<key>.env` 或 `skills.entries.<key>.apiKey` 注入 `process.env`。
3. 使用 **符合条件** 的技能构建系统提示。
4. 在运行结束后恢复原始环境。

此过程 **仅限于代理运行**，不涉及全局 shell 环境。

## 会话快照（性能）

OpenClaw 在会话开始时快照符合条件的技能，并在后续会话中重用该列表。技能或配置的更改将在下一次新会话中生效。

## 远程 macOS 节点（Linux 网关）

如果网关在 Linux 上运行，但 **macOS 节点** 通过允许 `system.run` 连接（Exec 审批安全未设置为 `deny`），OpenClaw 可以将仅限 macOS 的技能视为符合条件，前提是该节点上存在所需的二进制文件。代理应通过 `nodes` 工具（通常为 `nodes.run`）执行这些技能。

## 技能监视器（自动刷新）

默认情况下，OpenClaw 会监视技能文件夹，并在 `SKILL.md` 文件更改时更新技能快照。配置此功能如下：

```json5
{
  skills: {
    load: {
      watch: true,
      watchDebounceMs: 250
    }
  }
}
```

## 令牌影响（技能列表）

当技能符合条件时，OpenClaw 会将可用技能的紧凑 XML 列表注入系统提示（通过 `pi-coding-agent` 中的 `formatSkillsForPrompt`）。成本是确定性的：

- **基础开销（仅当 ≥1 个技能时）**：195 个字符。
- **每个技能**：97 个字符 + XML 转义后的 `<name>`、`<description>` 和 `<location>` 值的长度。

公式（字符）：

```
total = 195 + Σ (97 + len(name_escaped) + len(description_escaped) + len(location_escaped))
```

## 管理技能生命周期

OpenClaw 作为安装的一部分（npm 包或 OpenClaw.app）提供一组基础技能作为 **捆绑技能**。`~/.openclaw/skills` 用于本地覆盖（例如，固定或修补技能而不更改捆绑副本）。工作区技能由用户拥有，并在名称冲突时覆盖两者。

## 配置参考

完整配置模式请参见 [技能配置](/tools/skills-config)。

## 寻找更多技能？

浏览 https://clawhub.com。