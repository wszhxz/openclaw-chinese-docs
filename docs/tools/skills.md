---
summary: "Skills: managed vs workspace, gating rules, and config/env wiring"
read_when:
  - Adding or modifying skills
  - Changing skill gating or load rules
title: "Skills"
---
# 技能 (OpenClaw)

OpenClaw 使用 **[AgentSkills](https://agentskills.io)-兼容** 的技能文件夹来教代理如何使用工具。每个技能都是一个包含 `SKILL.md` 的目录，其中包含 YAML 前置元数据和指令。OpenClaw 加载 **捆绑的技能** 以及可选的本地覆盖，并在加载时根据环境、配置和二进制文件的存在情况进行过滤。

## 位置和优先级

技能从 **三个** 地方加载：

1. **捆绑的技能**：随安装包（npm 包或 OpenClaw.app）一起提供
2. **管理/本地技能**：`~/.openclaw/skills`
3. **工作区技能**：`<workspace>/skills`

如果技能名称冲突，优先级为：

`<workspace>/skills` (最高) → `~/.openclaw/skills` → 捆绑的技能 (最低)

此外，您还可以通过在 `~/.openclaw/openclaw.json` 中设置 `skills.load.extraDirs` 来配置额外的技能文件夹（最低优先级）。

## 每个代理与共享技能

在 **多代理** 设置中，每个代理都有自己的工作区。这意味着：

- **每个代理的技能** 存在于该代理的 `<workspace>/skills` 中。
- **共享技能** 存在于 `~/.openclaw/skills` (管理/本地) 并且对同一台机器上的 **所有代理** 可见。
- **共享文件夹** 也可以通过 `skills.load.extraDirs` (最低优先级) 添加，如果您希望多个代理使用通用的技能包。

如果同一个技能名称存在于多个地方，通常的优先级适用：工作区优先，然后是管理/本地，最后是捆绑的。

## 插件 + 技能

插件可以通过在 `openclaw.plugin.json` 中列出 `skills` 目录（相对于插件根目录的路径）来提供自己的技能。当插件启用时，插件技能会加载并参与正常的技能优先级规则。您可以通过插件配置条目中的 `metadata.openclaw.requires.config` 来控制它们。有关发现/配置，请参阅 [插件](/tools/plugin)，有关这些技能教授的工具表面，请参阅 [工具](/tools)。

## ClawHub (安装 + 同步)

ClawHub 是 OpenClaw 的公共技能注册表。浏览地址为 [https://clawhub.com](https://clawhub.com)。使用它来发现、安装、更新和备份技能。完整指南：[ClawHub](/tools/clawhub)。

常见流程：

- 将技能安装到您的工作区：
  - `clawhub install <skill-slug>`
- 更新所有已安装的技能：
  - `clawhub update --all`
- 同步（扫描 + 发布更新）：
  - `clawhub sync --all`

默认情况下，`clawhub` 安装到当前工作目录下的 `./skills`（或者回退到配置的 OpenClaw 工作区）。OpenClaw 在下一次会话中将其识别为 `<workspace>/skills`。

## 安全注意事项

- 将第三方技能视为 **不可信代码**。在启用前阅读它们。
- 对于不可信的输入和有风险的工具，建议使用沙箱运行。请参阅 [沙箱](/gateway/sandboxing)。
- 工作区和额外目录的技能发现仅接受技能根目录和 `SKILL.md` 文件，其解析后的实际路径必须保持在配置的根目录内。
- `skills.entries.*.env` 和 `skills.entries.*.apiKey` 将秘密注入到该代理回合的 **主机** 进程中（而不是沙箱）。将秘密信息排除在提示和日志之外。
- 更广泛的威胁模型和检查列表，请参阅 [安全](/gateway/security)。

## 格式 (AgentSkills + Pi 兼容)

`SKILL.md` 必须至少包括：

```markdown
---
name: nano-banana-pro
description: Generate or edit images via Gemini 3 Pro Image
---
```

注意：

- 我们遵循 AgentSkills 规范进行布局/意图。
- 嵌入式代理使用的解析器仅支持 **单行** 前置元数据键。
- `metadata` 应该是一个 **单行 JSON 对象**。
- 在指令中使用 `{baseDir}` 来引用技能文件夹路径。
- 可选的前置元数据键：
  - `homepage` —— 在 macOS 技能 UI 中显示为“网站”（也支持通过 `metadata.openclaw.homepage`）。
  - `user-invocable` —— `true|false` (默认: `true`)。当 `true` 时，技能作为用户斜杠命令暴露。
  - `disable-model-invocation` —— `true|false` (默认: `false`)。当 `true` 时，技能被排除在模型提示之外（仍然可以通过用户调用获得）。
  - `command-dispatch` —— `tool` (可选)。当设置为 `tool` 时，斜杠命令绕过模型直接调度到工具。
  - `command-tool` —— 当 `command-dispatch: tool` 设置时要调用的工具名称。
  - `command-arg-mode` —— `raw` (默认)。对于工具调度，将原始参数字符串转发给工具（不进行核心解析）。

    调用工具时的参数为：
    `{ command: "<raw args>", commandName: "<slash command>", skillName: "<skill name>" }`。

## 门控 (加载时过滤)

OpenClaw 使用 `metadata` (单行 JSON) **在加载时过滤技能**：

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

- `always: true` —— 总是包含该技能（跳过其他门控）。
- `emoji` —— macOS 技能 UI 使用的可选表情符号。
- `homepage` —— macOS 技能 UI 中显示为“网站”的可选 URL。
- `os` —— 可选的平台列表 (`darwin`, `linux`, `win32`)。如果设置，则该技能仅在这些操作系统上有效。
- `requires.bins` —— 列表；每个都必须存在于 `PATH` 上。
- `requires.anyBins` —— 列表；至少有一个必须存在于 `PATH` 上。
- `requires.env` —— 列表；环境变量必须存在 **或** 在配置中提供。
- `requires.config` —— `openclaw.json` 路径列表，必须为真值。
- `primaryEnv` —— 与 `skills.entries.<name>.apiKey` 关联的环境变量名。
- `install` —— macOS 技能 UI 使用的可选安装程序规格数组 (brew/node/go/uv/download)。

关于沙箱的注意事项：

- `requires.bins` 在技能加载时在 **主机** 上检查。
- 如果代理被沙箱化，二进制文件也必须存在于 **容器内**。
  通过 `agents.defaults.sandbox.docker.setupCommand` (或自定义镜像) 安装它。
  `setupCommand` 在创建容器后运行一次。
  包安装还需要网络出口、可写根文件系统和沙箱中的 root 用户。
  例如，`summarize` 技能 (`skills/summarize/SKILL.md`) 需要在沙箱容器中运行 `summarize` CLI。

安装示例：

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

- 如果列出了多个安装程序，网关会选择一个 **单一** 的首选选项（如果有 brew，则选择 brew，否则选择 node）。
- 如果所有安装程序都是 `download`，OpenClaw 会列出每个条目，以便您可以查看可用的工件。
- 安装程序规格可以包括 `os: ["darwin"|"linux"|"win32"]` 以按平台过滤选项。
- Node 安装尊重 `openclaw.json` 中的 `skills.install.nodeManager` (默认: npm; 选项: npm/pnpm/yarn/bun)。
  这仅影响 **技能安装**；网关运行时仍应为 Node (Bun 不推荐用于 WhatsApp/Telegram)。
- Go 安装：如果缺少 `go` 且 `brew` 可用，网关会先通过 Homebrew 安装 Go，并尽可能将 `GOBIN` 设置为 Homebrew 的 `bin`。
- 下载安装：`url` (必需), `archive` (`tar.gz` | `tar.bz2` | `zip`), `extract` (默认: 当检测到存档时自动), `stripComponents`, `targetDir` (默认: `~/.openclaw/tools/<skillKey>`)。

如果没有 `metadata.openclaw`，则该技能始终有效（除非在配置中禁用或被捆绑技能的 `skills.allowBundled` 阻止）。

## 配置覆盖 (`~/.openclaw/openclaw.json`)

捆绑/管理的技能可以切换并提供环境值：

```json5
{
  skills: {
    entries: {
      "nano-banana-pro": {
        enabled: true,
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // or plaintext string
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

配置键默认匹配 **技能名称**。如果技能定义了 `metadata.openclaw.skillKey`，请在 `skills.entries` 下使用该键。

规则：

- `enabled: false` 即使技能已捆绑/安装也会禁用它。
- `env`：**仅当** 进程中尚未设置该变量时才注入。
- `apiKey`：方便声明了 `metadata.openclaw.primaryEnv` 的技能。
  支持纯文本字符串或 SecretRef 对象 (`{ source, provider, id }`)。
- `config`：每个技能的自定义字段的可选包；自定义键必须位于此处。
- `allowBundled`：**仅限捆绑** 技能的可选允许列表。如果设置，只有列表中的捆绑技能才有效（管理/工作区技能不受影响）。

## 环境注入 (每次代理运行)

当代理运行开始时，OpenClaw：

1. 读取技能元数据。
2. 将任何 `skills.entries.<key>.env` 或 `skills.entries.<key>.apiKey` 应用于 `process.env`。
3. 使用 **符合条件** 的技能构建系统提示。
4. 运行结束后恢复原始环境。

这是 **针对代理运行的作用域**，而不是全局 shell 环境。

## 会话快照 (性能)

OpenClaw 在 **会话开始时** 对符合条件的技能进行快照，并在同一会话中的后续回合中重用该列表。对技能或配置的更改将在下一个新会话中生效。

技能也可以在会话中途刷新，当启用了技能监视器或出现新的符合条件的远程节点时（见下文）。可以将此视为**热重载**：刷新后的列表将在下一个代理回合中被采纳。

## 远程macOS节点（Linux网关）

如果网关运行在Linux上，但连接了一个**允许`system.run`的macOS节点**（执行审批安全未设置为`deny`），那么当该节点上存在所需的二进制文件时，OpenClaw可以将仅限macOS的技能视为符合条件。代理应通过`nodes`工具（通常是`nodes.run`）来执行这些技能。

这依赖于节点报告其命令支持情况以及通过`system.run`进行的二进制探测。如果macOS节点稍后离线，技能仍然可见；调用可能会失败，直到节点重新连接。

## 技能监视器（自动刷新）

默认情况下，当`SKILL.md`文件发生变化时，OpenClaw会监视技能文件夹并更新技能快照。可以在`skills.load`下配置此功能：

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

当技能符合条件时，OpenClaw会将可用技能的紧凑XML列表注入系统提示（通过`pi-coding-agent`中的`formatSkillsForPrompt`）。成本是确定性的：

- **基础开销（仅当≥1个技能时）：** 195个字符。
- **每个技能：** 97个字符加上XML转义后的`<name>`、`<description>`和`<location>`值的长度。

公式（字符数）：

```
total = 195 + Σ (97 + len(name_escaped) + len(description_escaped) + len(location_escaped))
```

注意事项：

- XML转义会将`& < > " '`扩展为实体（如`&amp;`、`&lt;`等），从而增加长度。
- 令牌数量因模型分词器而异。一个粗略的OpenAI风格估计是~4字符/令牌，因此**97字符 ≈ 24令牌**每项技能加上您的实际字段长度。

## 管理的技能生命周期

OpenClaw作为安装的一部分（npm包或OpenClaw.app）提供了一组基线技能作为**捆绑技能**。`~/.openclaw/skills`用于本地覆盖（例如，在不更改捆绑副本的情况下固定/修补技能）。工作区技能归用户所有，并且在名称冲突时优先级高于两者。

## 配置参考

请参阅[技能配置](/tools/skills-config)以获取完整的配置模式。

## 寻找更多技能？

浏览[https://clawhub.com](https://clawhub.com)。