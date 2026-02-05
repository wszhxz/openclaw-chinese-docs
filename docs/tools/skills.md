---
summary: "Skills: managed vs workspace, gating rules, and config/env wiring"
read_when:
  - Adding or modifying skills
  - Changing skill gating or load rules
title: "Skills"
---
# 技能 (OpenClaw)

OpenClaw 使用 **[AgentSkills](https://agentskills.io)-兼容** 的技能文件夹来教授代理如何使用工具。每个技能是一个包含 `SKILL.md` 和 YAML 前言及说明的目录。OpenClaw 加载 **内置技能** 以及可选的本地覆盖，并根据环境、配置和二进制文件的存在情况在加载时进行过滤。

## 位置和优先级

技能从 **三个** 地方加载：

1. **内置技能**：随安装一起提供（npm 包或 OpenClaw.app）
2. **管理/本地技能**：`~/.openclaw/skills`
3. **工作区技能**：`<workspace>/skills`

如果技能名称冲突，优先级为：

`<workspace>/skills`（最高）→ `~/.openclaw/skills` → 内置技能（最低）

此外，您可以通过 `skills.load.extraDirs` 在 `~/.openclaw/openclaw.json` 中配置额外的技能文件夹（最低优先级）。

## 每个代理的技能 vs 共享技能

在 **多代理** 设置中，每个代理都有自己的工作区。这意味着：

- **每个代理的技能** 仅存在于该代理的 `<workspace>/skills` 中。
- **共享技能** 存在于 `~/.openclaw/skills`（管理/本地），对同一机器上的 **所有代理** 可见。
- 如果需要多个代理使用通用技能包，还可以通过 `skills.load.extraDirs` 添加 **共享文件夹**（最低优先级）。

如果同一个技能名称存在于多个地方，则适用通常的优先级规则：工作区优先，然后是管理/本地，最后是内置。

## 插件 + 技能

插件可以通过在 `openclaw.plugin.json` 中列出 `skills` 目录（相对于插件根目录的路径）来提供自己的技能。当插件启用时，插件技能会加载并参与正常的技能优先级规则。您可以通过插件配置条目的 `metadata.openclaw.requires.config` 来控制它们。有关发现/配置，请参阅 [插件](/plugin)，有关这些技能所教授的工具界面，请参阅 [工具](/tools)。

## ClawHub（安装 + 同步）

ClawHub 是 OpenClaw 的公共技能注册表。浏览地址为 https://clawhub.com。使用它来发现、安装、更新和备份技能。完整指南：[ClawHub](/tools/clawhub)。

常见流程：

- 将技能安装到您的工作区：
  - `clawhub install <skill-slug>`
- 更新所有已安装的技能：
  - `clawhub update --all`
- 同步（扫描 + 发布更新）：
  - `clawhub sync --all`

默认情况下，`clawhub` 安装到当前工作目录下的 `./skills`（或回退到配置的 OpenClaw 工作区）。OpenClaw 在下一次会话中将其识别为 `<workspace>/skills`。

## 安全注意事项

- 将第三方技能视为 **不受信任的代码**。启用之前请阅读。
- 对于不受信任的输入和高风险工具，优先使用沙箱运行。参阅 [沙箱](/gateway/sandboxing)。
- `skills.entries.*.env` 和 `skills.entries.*.apiKey` 将机密信息注入该代理回合的 **主机** 进程（而不是沙箱）。请勿在提示和日志中包含机密信息。
- 有关更广泛的威胁模型和检查清单，请参阅 [安全](/gateway/security)。

## 格式 (AgentSkills + Pi兼容)

`SKILL.md` 必须包含至少：

```markdown
---
name: nano-banana-pro
description: Generate or edit images via Gemini 3 Pro Image
---
```

注意事项：

- 我们遵循 AgentSkills 规范进行布局/意图。
- 嵌入代理使用的解析器仅支持 **单行** 前言键。
- `metadata` 应该是一个 **单行 JSON 对象**。
- 在说明中使用 `{baseDir}` 引用技能文件夹路径。
- 可选的前言键：
  - `homepage` — 在 macOS 技能 UI 中显示为“网站”的 URL（也通过 `metadata.openclaw.homepage` 支持）。
  - `user-invocable` — `true|false`（默认：`true`）。当 `true` 时，技能作为用户斜杠命令暴露。
  - `disable-model-invocation` — `true|false`（默认：`false`）。当 `true` 时，技能从模型提示中排除（但仍可通过用户调用获得）。
  - `command-dispatch` — `tool`（可选）。设置为 `tool` 时，斜杠命令绕过模型并直接分派到工具。
  - `command-tool` — 当 `command-dispatch: tool` 设置时要调用的工具名称。
  - `command-arg-mode` — `raw`（默认）。对于工具分派，将原始参数字符串转发给工具（不进行核心解析）。

    工具调用的参数为：
    `{ command: "<raw args>", commandName: "<slash command>", skillName: "<skill name>" }`。

## 网关（加载时过滤器）

OpenClaw **在加载时使用 `metadata`（单行 JSON）过滤技能**：

```markdown
---
name: nano-banana-pro
description: Generate or edit images via Gemini 3 Pro Image
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"], "config": ["browser.enabled"] },
        "primaryEnv": "GEMINI_API_KEY",
      },
  }
---
```

`metadata.openclaw` 下的字段：

- `always: true` — 始终包含技能（跳过其他网关）。
- `emoji` — macOS 技能 UI 使用的可选表情符号。
- `homepage` — 在 macOS 技能 UI 中显示为“网站”的可选 URL。
- `os` — 可选的操作系统列表 (`darwin`, `linux`, `win32`)。如果设置，则该技能仅在这些操作系统上有效。
- `requires.bins` — 列表；每个必须存在于 `PATH` 上。
- `requires.anyBins` — 列表；至少有一个必须存在于 `PATH` 上。
- `requires.env` — 列表；环境变量必须存在 **或** 在配置中提供。
- `requires.config` — 必须为真值的 `openclaw.json` 路径列表。
- `primaryEnv` — 与 `skills.entries.<name>.apiKey` 关联的环境变量名称。
- `install` — macOS 技能 UI 使用的可选安装程序规范数组（brew/node/go/uv/download）。

关于沙盒的说明：

- `requires.bins` 在技能加载时在 **host** 上进行检查。
- 如果代理程序被沙盒化，则二进制文件也必须存在于 **容器内部**。
  通过 `agents.defaults.sandbox.docker.setupCommand` 安装它（或自定义镜像）。
  `setupCommand` 在容器创建后运行一次。
  包安装还需要网络出口、可写的根文件系统以及沙盒中的 root 用户。
  示例：`summarize` 技能 (`skills/summarize/SKILL.md`) 需要在沙盒容器中运行 `summarize` CLI。

安装程序示例：

```markdown
---
name: gemini
description: Use Gemini CLI for coding assistance and Google search lookups.
metadata:
  {
    "openclaw":
      {
        "emoji": "♊️",
        "requires": { "bins": ["gemini"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "gemini-cli",
              "bins": ["gemini"],
              "label": "Install Gemini CLI (brew)",
            },
          ],
      },
  }
---
```

注意：

- 如果列出了多个安装程序，网关会选择一个 **单一** 的首选选项（如果有 brew 则使用 brew，否则使用 node）。
- 如果所有安装程序都是 `download`，OpenClaw 会列出每个条目以便您可以查看可用的工件。
- 安装程序规范可以包含 `os: ["darwin"|"linux"|"win32"]` 以按平台过滤选项。
- Node 安装会遵守 `openclaw.json` 中的 `skills.install.nodeManager`（默认：npm；选项：npm/pnpm/yarn/bun）。
  这仅影响 **技能安装**；网关运行时应仍为 Node
  （不建议 Bun 用于 WhatsApp/Telegram）。
- Go 安装：如果缺少 `go` 而 `brew` 可用，网关将首先通过 Homebrew 安装 Go，并在可能的情况下将 `GOBIN` 设置为 Homebrew 的 `bin`。
- 下载安装：`url`（必需），`archive` (`tar.gz` | `tar.bz2` | `zip`)，`extract`（默认：检测到归档文件时为 auto），`stripComponents`，`targetDir`（默认：`~/.openclaw/tools/<skillKey>`）。

如果没有 `metadata.openclaw`，技能总是有资格的（除非在配置中禁用或被 `skills.allowBundled` 阻止捆绑技能）。

## 配置覆盖 (`~/.openclaw/openclaw.json`)

捆绑/管理的技能可以切换并提供环境变量：

```json5
{
  skills: {
    entries: {
      "nano-banana-pro": {
        enabled: true,
        apiKey: "GEMINI_KEY_HERE",
        env: {
          GEMINI_API_KEY: "GEMINI_KEY_HERE",
        },
        config: {
          endpoint: "https://example.invalid",
          model: "nano-pro",
        },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

注意：如果技能名称包含连字符，请引用键（JSON5 允许引用键）。

配置键默认与 **技能名称** 匹配。如果技能定义了
`metadata.openclaw.skillKey`，请在 `skills.entries` 下使用该键。

规则：

- `enabled: false` 即使技能被打包/安装了也会禁用该技能。
- `env`: 仅当变量在进程中尚未设置时才会注入。
- `apiKey`: 便于声明了 `metadata.openclaw.primaryEnv` 的技能。
- `config`: 自定义每个技能字段的可选存储袋；自定义键必须放在这里。
- `allowBundled`: 仅适用于 **打包** 技能的可选白名单。如果设置了，则只有列表中的打包技能有资格（管理/工作区技能不受影响）。

## 环境注入（每个代理运行）

当代理运行开始时，OpenClaw：

1. 读取技能元数据。
2. 将任何 `skills.entries.<key>.env` 或 `skills.entries.<key>.apiKey` 应用于
   `process.env`。
3. 使用 **有资格** 的技能构建系统提示。
4. 在运行结束后恢复原始环境。

这仅限于 **代理运行**，而不是全局 shell 环境。

## 会话快照（性能）

OpenClaw 在 **会话开始时** 对有资格的技能进行快照，并在同一个会话的后续回合中重用该列表。对技能或配置的更改将在下一个新会话中生效。

当启用技能监视器或出现新的有资格远程节点时（见下文），技能也可以在会话中间刷新。可以将其视为 **热重载**：刷新后的列表将在下一个代理回合中被采用。

## 远程 macOS 节点（Linux 网关）

如果网关在 Linux 上运行但连接了一个 **macOS 节点** 并且允许了 `system.run`（执行批准安全设置未设置为 `deny`），当该节点上存在所需的二进制文件时，OpenClaw 可以将仅限 macOS 的技能视为有资格。代理应通过 `nodes` 工具（通常是 `nodes.run`）执行这些技能。

这依赖于节点报告其命令支持并通过 `system.run` 进行二进制探测。如果 macOS 节点稍后离线，技能仍然可见；调用可能会失败，直到节点重新连接。

## 技能监视器（自动刷新）

默认情况下，OpenClaw 监视技能文件夹，并在 `SKILL.md` 文件更改时更新技能快照。在 `skills.load` 下进行配置：

```json5
{
  skills: {
    load: {
      watch: true,
      watchDebounceMs: 250,
    },
  },
}
```

## 令牌影响（技能列表）

当技能有资格时，OpenClaw 通过 `formatSkillsForPrompt` 在 `pi-coding-agent` 中将可用技能的紧凑 XML 列表注入系统提示。成本是确定性的：

- **基本开销（仅当 ≥1 技能时）：** 195 个字符。
- **每技能：** 97 个字符 + XML 转义的 `<name>`、`<description>` 和 `<location>` 值的长度。

公式（字符）：

```
total = 195 + Σ (97 + len(name_escaped) + len(description_escaped) + len(location_escaped))
```

说明：

- XML 转义将 `& < > " '` 展开为实体 (`&amp;`、`&lt;` 等)，增加长度。
- 令牌计数因模型分词器而异。一个粗略的 OpenAI 风格估计约为每 4 个字符 1 个令牌，因此 **97 个字符 ≈ 24 个令牌** 每技能加上实际字段长度。

## 管理技能生命周期

OpenClaw 随附一组基线技能作为 **bundled skills** 的一部分（npm 包或 OpenClaw.app）。`~/.openclaw/skills` 用于本地覆盖（例如，在不更改捆绑副本的情况下固定/修补技能）。工作区技能由用户拥有，并在名称冲突时进行覆盖。

## 配置参考

请参阅 [Skills config](/tools/skills-config) 获取完整的配置架构。

## 寻找更多技能？

浏览 https://clawhub.com。