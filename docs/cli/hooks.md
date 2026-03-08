---
summary: "CLI reference for `openclaw hooks` (agent hooks)"
read_when:
  - You want to manage agent hooks
  - You want to install or update hooks
title: "hooks"
---
# `openclaw hooks`

管理代理钩子（用于命令的事件驱动自动化，例如 `/new`、`/reset` 以及网关启动）。

相关：

- 钩子：[钩子](/automation/hooks)
- 插件钩子：[插件](/tools/plugin#plugin-hooks)

## 列出所有钩子

```bash
openclaw hooks list
```

列出从工作区、已管理和捆绑目录中发现的所有钩子。

**选项：**

- `--eligible`：仅显示符合条件的钩子（满足要求）
- `--json`：以 JSON 格式输出
- `-v, --verbose`：显示详细信息，包括缺失的要求

**示例输出：**

```
Hooks (4/4 ready)

Ready:
  🚀 boot-md ✓ - Run BOOT.md on gateway startup
  📎 bootstrap-extra-files ✓ - Inject extra workspace bootstrap files during agent bootstrap
  📝 command-logger ✓ - Log all command events to a centralized audit file
  💾 session-memory ✓ - Save session context to memory when /new command is issued
```

**示例（详细模式）：**

```bash
openclaw hooks list --verbose
```

显示不符合条件的钩子的缺失要求。

**示例（JSON）：**

```bash
openclaw hooks list --json
```

返回结构化 JSON 以供编程使用。

## 获取钩子信息

```bash
openclaw hooks info <name>
```

显示特定钩子的详细信息。

**参数：**

- `<name>`：钩子名称（例如 `session-memory`）

**选项：**

- `--json`：以 JSON 格式输出

**示例：**

```bash
openclaw hooks info session-memory
```

**输出：**

```
💾 session-memory ✓ Ready

Save session context to memory when /new command is issued

Details:
  Source: openclaw-bundled
  Path: /path/to/openclaw/hooks/bundled/session-memory/HOOK.md
  Handler: /path/to/openclaw/hooks/bundled/session-memory/handler.ts
  Homepage: https://docs.openclaw.ai/automation/hooks#session-memory
  Events: command:new

Requirements:
  Config: ✓ workspace.dir
```

## 检查钩子资格

```bash
openclaw hooks check
```

显示钩子资格状态的摘要（多少就绪与未就绪）。

**选项：**

- `--json`：以 JSON 格式输出

**示例输出：**

```
Hooks Status

Total hooks: 4
Ready: 4
Not ready: 0
```

## 启用钩子

```bash
openclaw hooks enable <name>
```

通过将特定钩子添加到您的配置中（`~/.openclaw/config.json`）来启用它。

**注意：** 由插件管理的钩子在 `openclaw hooks list` 中显示 `plugin:<id>`，无法在此处启用/禁用。请改为启用/禁用该插件。

**参数：**

- `<name>`：钩子名称（例如 `session-memory`）

**示例：**

```bash
openclaw hooks enable session-memory
```

**输出：**

```
✓ Enabled hook: 💾 session-memory
```

**功能说明：**

- 检查钩子是否存在且符合条件
- 更新您配置中的 `hooks.internal.entries.<name>.enabled = true`
- 将配置保存到磁盘

**启用后：**

- 重启网关以重新加载钩子（macOS 上重启菜单栏应用，或在开发环境中重启网关进程）。

## 禁用钩子

```bash
openclaw hooks disable <name>
```

通过更新您的配置来禁用特定钩子。

**参数：**

- `<name>`：钩子名称（例如 `command-logger`）

**示例：**

```bash
openclaw hooks disable command-logger
```

**输出：**

```
⏸ Disabled hook: 📝 command-logger
```

**禁用后：**

- 重启网关以重新加载钩子

## 安装钩子

```bash
openclaw hooks install <path-or-spec>
openclaw hooks install <npm-spec> --pin
```

从本地文件夹/归档或 npm 安装钩子包。

NPM 规范是**仅注册表**（包名 + 可选的**确切版本**或**分发标签**）。Git/URL/文件规范和语义化版本范围将被拒绝。依赖安装使用 `--ignore-scripts` 以确保安全。

裸规范和 `@latest` 保持在稳定轨道上。如果 npm 将其中任何一个解析为预发布版，OpenClaw 会停止并提示您明确选择加入，使用预发布标签如 `@beta`/`@rc` 或确切的预发布版本。

**功能说明：**

- 将钩子包复制到 `~/.openclaw/hooks/<id>`
- 在 `hooks.internal.entries.*` 中启用已安装的钩子
- 在 `hooks.internal.installs` 下记录安装

**选项：**

- `-l, --link`：链接本地目录而不是复制（将其添加到 `hooks.internal.load.extraDirs`）
- `--pin`：在 `hooks.internal.installs` 中将 npm 安装记录为确切解析的 `name@version`

**支持的归档：** `.zip`、`.tgz`、`.tar.gz`、`.tar`

**示例：**

```bash
# Local directory
openclaw hooks install ./my-hook-pack

# Local archive
openclaw hooks install ./my-hook-pack.zip

# NPM package
openclaw hooks install @openclaw/my-hook-pack

# Link a local directory without copying
openclaw hooks install -l ./my-hook-pack
```

## 更新钩子

```bash
openclaw hooks update <id>
openclaw hooks update --all
```

更新已安装的钩子包（仅限 npm 安装）。

**选项：**

- `--all`：更新所有跟踪的钩子包
- `--dry-run`：显示更改内容而不写入

当存储的完整性哈希存在且获取的工件哈希发生变化时，OpenClaw 会打印警告并在继续之前请求确认。在全局 `--yes` 中使用以在 CI/非交互式运行中绕过提示。

### session-memory

当您发出 `/new` 时将会话上下文保存到内存。

**启用：**

```bash
openclaw hooks enable session-memory
```

**输出：** `~/.openclaw/workspace/memory/YYYY-MM-DD-slug.md`

**查看：** [session-memory 文档](/automation/hooks#session-memory)

### bootstrap-extra-files

在 `agent:bootstrap` 期间注入额外的引导文件（例如 monorepo-local `AGENTS.md` / `TOOLS.md`）。

**启用：**

```bash
openclaw hooks enable bootstrap-extra-files
```

**查看：** [bootstrap-extra-files 文档](/automation/hooks#bootstrap-extra-files)

### command-logger

将所有命令事件记录到集中式审计文件中。

**启用：**

```bash
openclaw hooks enable command-logger
```

**输出：** `~/.openclaw/logs/commands.log`

**查看日志：**

```bash
# Recent commands
tail -n 20 ~/.openclaw/logs/commands.log

# Pretty-print
cat ~/.openclaw/logs/commands.log | jq .

# Filter by action
grep '"action":"new"' ~/.openclaw/logs/commands.log | jq .
```

**查看：** [command-logger 文档](/automation/hooks#command-logger)

### boot-md

当网关启动时（通道启动后）运行 `BOOT.md`。

**事件**：`gateway:startup`

**启用**：

```bash
openclaw hooks enable boot-md
```

**查看：** [boot-md 文档](/automation/hooks#boot-md)