---
summary: "CLI reference for `openclaw plugins` (list, install, marketplace, uninstall, enable/disable, doctor)"
read_when:
  - You want to install or manage Gateway plugins or compatible bundles
  - You want to debug plugin load failures
title: "plugins"
---
# `openclaw plugins`

管理网关插件/扩展、钩子包和兼容捆绑包。

相关：

- 插件系统：[Plugins](/tools/plugin)
- 捆绑包兼容性：[Plugin bundles](/plugins/bundles)
- 插件清单 + 模式：[Plugin manifest](/plugins/manifest)
- 安全加固：[Security](/gateway/security)

## 命令

```bash
openclaw plugins list
openclaw plugins list --enabled
openclaw plugins list --verbose
openclaw plugins list --json
openclaw plugins install <path-or-spec>
openclaw plugins inspect <id>
openclaw plugins inspect <id> --json
openclaw plugins inspect --all
openclaw plugins info <id>
openclaw plugins enable <id>
openclaw plugins disable <id>
openclaw plugins uninstall <id>
openclaw plugins doctor
openclaw plugins update <id>
openclaw plugins update --all
openclaw plugins marketplace list <marketplace>
openclaw plugins marketplace list <marketplace> --json
```

捆绑插件随 OpenClaw 一起发布。部分默认启用（例如捆绑模型提供者、捆绑语音提供者和捆绑浏览器插件）；其他则需要 `plugins enable`。

原生 OpenClaw 插件必须附带 `openclaw.plugin.json` 以及内联 JSON Schema（`configSchema`，即使为空）。兼容捆绑包使用它们自己的捆绑包清单。

`plugins list` 显示 `Format: openclaw` 或 `Format: bundle`。详细列表/信息输出还会显示捆绑包子类型（`codex`、`claude` 或 `cursor`）以及检测到的捆绑包功能。

### 安装

```bash
openclaw plugins install <package>                      # ClawHub first, then npm
openclaw plugins install clawhub:<package>              # ClawHub only
openclaw plugins install <package> --force              # overwrite existing install
openclaw plugins install <package> --pin                # pin version
openclaw plugins install <package> --dangerously-force-unsafe-install
openclaw plugins install <path>                         # local path
openclaw plugins install <plugin>@<marketplace>         # marketplace
openclaw plugins install <plugin> --marketplace <name>  # marketplace (explicit)
openclaw plugins install <plugin> --marketplace https://github.com/<owner>/<repo>
```

裸包名首先与 ClawHub 进行比对，然后是 npm。安全提示：将插件安装视为运行代码。优先使用固定版本。

如果配置无效，`plugins install` 通常会失败关闭并提示你先运行 `openclaw doctor --fix`。唯一的文档记录例外是针对明确选择加入 `openclaw.install.allowInvalidConfigRecovery` 的插件的狭窄捆绑插件恢复路径。

`--force` 重用现有的安装目标并在原地覆盖已安装的插件或钩子包。当你有意从新的本地路径、归档文件、ClawHub 包或 npm 制品重新安装相同的 id 时使用它。

`--pin` 仅适用于 npm 安装。它与 `--marketplace` 不兼容，因为市场安装保留市场源元数据而不是 npm 规范。

`--dangerously-force-unsafe-install` 是内置危险代码扫描器误报的紧急选项。即使内置扫描器报告 `critical` 发现，它也允许安装继续，但它**不**绕过插件 `before_install` 钩子策略阻止，也**不**绕过扫描失败。

此 CLI 标志适用于插件安装/更新流程。由网关支持的技能依赖安装使用匹配的 `dangerouslyForceUnsafeInstall` 请求覆盖，而 `openclaw skills install` 仍然是单独的 ClawHub 技能下载/安装流程。

`plugins install` 也是暴露 `openclaw.hooks` 在 `package.json` 中的钩子包的安装界面。使用 `openclaw hooks` 进行过滤钩子可见性和每钩子启用，而不是包安装。

Npm 规范是**仅限注册表**（包名 + 可选的**确切版本**或**分发标签**）。Git/URL/文件规范和语义化版本范围被拒绝。依赖安装以 `--ignore-scripts` 运行以确保安全。

裸规范和 `@latest` 保持在稳定轨道上。如果 npm 将其中任何一个解析为预发布版，OpenClaw 会停止并要求你通过预发布标签（如 `@beta`/`@rc`）或确切预发布版本（如 `@1.2.3-beta.4`）显式选择加入。

如果裸安装规范匹配捆绑插件 id（例如 `diffs`），OpenClaw 直接安装捆绑插件。要安装同名 npm 包，请使用明确的限定符规范（例如 `@scope/diffs`）。

支持的归档：`.zip`、`.tgz`、`.tar.gz`、`.tar`。

也支持 Claude 市场安装。

ClawHub 安装使用明确的 `clawhub:<package>` 定位器：

```bash
openclaw plugins install clawhub:openclaw-codex-app-server
openclaw plugins install clawhub:openclaw-codex-app-server@1.2.3
```

OpenClaw 现在也偏好对裸 npm 安全插件规范使用 ClawHub。仅当 ClawHub 没有该包或版本时，它才回退到 npm：

```bash
openclaw plugins install openclaw-codex-app-server
```

OpenClaw 从 ClawHub 下载包归档，检查宣传的插件 API / 最小网关兼容性，然后通过正常归档路径安装它。记录的安装保留其 ClawHub 源元数据以供以后更新。

当市场名称存在于 `~/.claude/plugins/known_marketplaces.json` 处 Claude 的本地注册表缓存中时，使用 `plugin@marketplace` 简写：

```bash
openclaw plugins marketplace list <marketplace-name>
openclaw plugins install <plugin-name>@<marketplace-name>
```

当你想显式传递市场源时，使用 `--marketplace`：

```bash
openclaw plugins install <plugin-name> --marketplace <marketplace-name>
openclaw plugins install <plugin-name> --marketplace <owner/repo>
openclaw plugins install <plugin-name> --marketplace https://github.com/<owner>/<repo>
openclaw plugins install <plugin-name> --marketplace ./my-marketplace
```

市场源可以是：

- 来自 `~/.claude/plugins/known_marketplaces.json` 的 Claude 已知市场名称
- 本地市场根目录或 `marketplace.json` 路径
- 如 `owner/repo` 的 GitHub 仓库简写
- 如 `https://github.com/owner/repo` 的 GitHub 仓库 URL
- git URL

对于从 GitHub 或 git 加载的远程市场，插件条目必须保留在克隆的市场仓库内。OpenClaw 接受来自该仓库的相对路径源，并拒绝来自远程清单的 HTTP(S)、绝对路径、git、GitHub 和其他非路径插件源。

对于本地路径和归档，OpenClaw 自动检测：

- 原生 OpenClaw 插件 (`openclaw.plugin.json`)
- Codex 兼容捆绑包 (`.codex-plugin/plugin.json`)
- Claude 兼容捆绑包 (`.claude-plugin/plugin.json` 或默认 Claude 组件布局)
- Cursor 兼容捆绑包 (`.cursor-plugin/plugin.json`)

兼容捆绑包安装到正常的扩展根目录，并参与相同的列表/信息/启用/禁用流程。今天，支持捆绑技能、Claude 命令技能、Claude `settings.json` 默认值、Claude `.lsp.json` / 清单声明的 `lspServers` 默认值、Cursor 命令技能和兼容的 Codex 钩子目录；其他检测到的捆绑包功能在诊断/信息中显示，但尚未连接到运行时执行。

### 列表

```bash
openclaw plugins list
openclaw plugins list --enabled
openclaw plugins list --verbose
openclaw plugins list --json
```

使用 `--enabled` 仅显示已加载的插件。使用 `--verbose` 从表格视图切换到带有源/来源/版本/激活元数据的每个插件详细信息行。使用 `--json` 获取机器可读清单加上注册表诊断。

使用 `--link` 避免复制本地目录（添加到 `plugins.load.paths`）：

```bash
openclaw plugins install -l ./my-plugin
```

`--force` 不支持与 `--link` 一起使用，因为链接安装重用源路径而不是复制到受管理的安装目标。

在 npm 安装上使用 `--pin` 保存解析的确切规范 (`name@version`) 在 `plugins.installs` 中，同时保持默认行为未固定。

### 卸载

```bash
openclaw plugins uninstall <id>
openclaw plugins uninstall <id> --dry-run
openclaw plugins uninstall <id> --keep-files
```

`uninstall` 从 `plugins.entries`、`plugins.installs`、插件白名单和链接的 `plugins.load.paths` 条目中移除插件记录（如适用）。对于活动内存插件，内存槽重置为 `memory-core`。

默认情况下，卸载还会移除活动状态目录插件根下的插件安装目录。使用 `--keep-files` 保留磁盘上的文件。

`--keep-config` 作为 `--keep-files` 的弃用别名得到支持。

### 更新

```bash
openclaw plugins update <id-or-npm-spec>
openclaw plugins update --all
openclaw plugins update <id-or-npm-spec> --dry-run
openclaw plugins update @openclaw/voice-call@beta
openclaw plugins update openclaw-codex-app-server --dangerously-force-unsafe-install
```

更新适用于 `plugins.installs` 中的跟踪安装和 `hooks.internal.installs` 中的跟踪钩子包安装。

当你传递插件 id 时，OpenClaw 重用该插件的记录安装规范。这意味着之前存储的分发标签（如 `@beta`）和确切固定版本在以后的 `update <id>` 运行中继续使用。

对于 npm 安装，你也可以传递带有分发标签或确切版本的明确 npm 包规范。OpenClaw 将该包名解析回跟踪的插件记录，更新该已安装的插件，并记录新的 npm 规范以供未来的基于 id 的更新。

当存在存储的完整性哈希且获取的工件哈希更改时，OpenClaw 打印警告并在继续前要求确认。使用全局 `--yes` 在 CI/非交互式运行中绕过提示。

`--dangerously-force-unsafe-install` 也可在 `plugins update` 上作为插件更新期间内置的危险代码扫描误报的紧急覆盖方案。它仍然不会绕过插件 `before_install` 策略阻止或扫描失败阻止，且仅适用于插件更新，不适用于 hook-pack 更新。

### 检查

```bash
openclaw plugins inspect <id>
openclaw plugins inspect <id> --json
```

对单个插件进行深入检查。显示身份、加载状态、来源、注册的能力、钩子、工具、命令、服务、网关方法、HTTP 路由、策略标志、诊断信息、安装元数据、捆绑包能力以及任何检测到的 MCP 或 LSP 服务器支持。

每个插件根据其运行时实际注册的内容进行分类：

- **plain-capability** — 一种能力类型（例如仅提供服务的插件）
- **hybrid-capability** — 多种能力类型（例如文本 + 语音 + 图像）
- **hook-only** — 仅包含钩子，无能力或表面
- **non-capability** — 有工具/命令/服务但无能力

有关能力模型的更多信息，请参阅 [插件形状](/plugins/architecture#plugin-shapes)。

``--json`` 标志输出适合脚本编写和审计的机器可读报告。

``inspect --all`` 渲染一个涵盖整个集群的表格，包含形状、能力种类、兼容性通知、捆绑包能力和钩子摘要列。

``info`` 是 ``inspect`` 的别名。

### 诊断

```bash
openclaw plugins doctor
```

``doctor`` 报告插件加载错误、清单/发现诊断和兼容性通知。当一切正常时，它会打印 ``No plugin issues
detected.``

### 市场

```bash
openclaw plugins marketplace list <source>
openclaw plugins marketplace list <source> --json
```

市场列表接受本地市场路径、``marketplace.json`` 路径、类似 ``owner/repo`` 的 GitHub 简写、GitHub 仓库 URL 或 git URL。``--json`` 打印解析后的源标签以及解析的市场清单和插件条目。