---
summary: "CLI reference for `openclaw hooks` (agent hooks)"
read_when:
  - You want to manage agent hooks
  - You want to install or update hooks
title: "hooks"
---
# `openclaw hooks`

管理代理钩子（针对像 `/new`、`/reset` 和网关启动这样的命令的事件驱动自动化）。

相关：

- 钩子：[Hooks](/automation/hooks)
- 插件钩子：[Plugins](/tools/plugin#plugin-hooks)

## 列出所有钩子

```bash
openclaw hooks list
```

列出从工作区、管理目录和捆绑包目录发现的所有钩子。

**选项：**

- `--eligible`: 仅显示符合条件的钩子（满足要求）
- `--json`: 以 JSON 输出
- `-v, --verbose`: 显示包括缺失要求在内的详细信息

**示例输出：**

```
Hooks (4/4 ready)

Ready:
  🚀 boot-md ✓ - Run BOOT.md on gateway startup
  📎 bootstrap-extra-files ✓ - Inject extra workspace bootstrap files during agent bootstrap
  📝 command-logger ✓ - Log all command events to a centralized audit file
  💾 session-memory ✓ - Save session context to memory when /new command is issued
```

**详细示例：**

```bash
openclaw hooks list --verbose
```

显示不符合条件钩子的缺失要求。

**JSON 示例：**

```bash
openclaw hooks list --json
```

返回结构化的 JSON 用于程序化使用。

## 获取钩子信息

```bash
openclaw hooks info <name>
```

显示特定钩子的详细信息。

**参数：**

- `<name>`: 钩子名称（例如 `session-memory`）

**选项：**

- `--json`: 以 JSON 输出

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

显示钩子资格状态摘要（有多少准备就绪与未准备就绪）。

**选项：**

- `--json`: 以 JSON 输出

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

通过将其添加到您的配置中来启用特定钩子 (`~/.openclaw/config.json`)。

**注意：** 由插件管理的钩子在 `openclaw hooks list` 中显示 `plugin:<id>`，不能在此处启用/禁用。请启用/禁用插件。

**参数：**

- `<name>`: 钩子名称（例如 `session-memory`）

**示例：**

```bash
openclaw hooks enable session-memory
```

**输出：**

```
✓ Enabled hook: 💾 session-memory
```

**执行的操作：**

- 检查钩子是否存在且符合条件
- 更新您的配置中的 `hooks.internal.entries.<name>.enabled = true`
- 将配置保存到磁盘

**启用后：**

- 重启网关以便重新加载钩子（macOS 上的菜单栏应用程序重启，或在开发环境中重启网关进程）。

## 禁用钩子

```bash
openclaw hooks disable <name>
```

通过更新您的配置来禁用特定钩子。

**参数：**

- `<name>`: 钩子名称（例如 `command-logger`）

**示例：**

```bash
openclaw hooks disable command-logger
```

**输出：**

```
⏸ Disabled hook: 📝 command-logger
```

**禁用后：**

- 重启网关以便重新加载钩子

## 安装钩子

```bash
openclaw hooks install <path-or-spec>
openclaw hooks install <npm-spec> --pin
```

从本地文件夹/归档或 npm 安装钩子包。

npm 规范是仅限**注册表**（包名称 + 可选版本/标签）。Git/URL/文件规范被拒绝。依赖安装使用 `--ignore-scripts` 以确保安全。

**执行的操作：**

- 将钩子包复制到 `~/.openclaw/hooks/<id>`
- 在 `hooks.internal.entries.*` 中启用已安装的钩子
- 在 `hooks.internal.installs` 下记录安装

**选项：**

- `-l, --link`: 链接本地目录而不是复制（将其添加到 `hooks.internal.load.extraDirs`)
- `--pin`: 记录 npm 安装为确切解析的 `name@version` 在 `hooks.internal.installs`

**支持的归档文件：** `.zip`, `.tgz`, `.tar.gz`, `.tar`

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

- `--all`: 更新所有跟踪的钩子包
- `--dry-run`: 显示更改内容而不写入

当存储的完整性哈希存在且获取的工件哈希发生变化时，OpenClaw 打印警告并要求确认后继续进行。使用全局 `--yes` 在 CI/非交互式运行中绕过提示。

## 捆绑包钩子

### session-memory

在您发出 `/new` 时将会话上下文保存到内存中。

**启用：**

```bash
openclaw hooks enable session-memory
```

**输出：** `~/.openclaw/workspace/memory/YYYY-MM-DD-slug.md`

**参见：** [session-memory 文档](/automation/hooks#session-memory)

### bootstrap-extra-files

在 `agent:bootstrap` 期间注入额外的引导文件（例如 monorepo-local `AGENTS.md` / `TOOLS.md`）。

**启用：**

```bash
openclaw hooks enable bootstrap-extra-files
```

**参见：** [bootstrap-extra-files 文档](/automation/hooks#bootstrap-extra-files)

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

**参见：** [command-logger 文档](/automation/hooks#command-logger)

### boot-md

在网关启动时（通道启动后）运行 `BOOT.md`。

**事件：** `gateway:startup`

**启用：**

```bash
openclaw hooks enable boot-md
```

**参见：** [boot-md 文档](/automation/hooks#boot-md)