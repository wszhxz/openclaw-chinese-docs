---
summary: "CLI reference for `openclaw hooks` (agent hooks)"
read_when:
  - You want to manage agent hooks
  - You want to install or update hooks
title: "hooks"
---
# `openclaw hooks`

管理代理钩子（面向事件的自动化，适用于 ``/new``、``/reset`` 和网关启动等命令）。

相关文档：

- 钩子：[钩子](/automation/hooks)  
- 插件钩子：[插件](/tools/plugin#plugin-hooks)

## 列出所有钩子

```bash
openclaw hooks list
```

列出工作区（workspace）、已托管（managed）和内置（bundled）目录中发现的所有钩子。

**选项：**

- `--eligible`：仅显示符合条件的钩子（满足全部依赖要求）  
- `--json`：以 JSON 格式输出  
- `-v, --verbose`：显示详细信息（包括缺失的依赖项）

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

显示不符合条件的钩子所缺失的依赖项。

**示例（JSON）：**

```bash
openclaw hooks list --json
```

返回结构化的 JSON，供程序化调用使用。

## 获取钩子信息

```bash
openclaw hooks info <name>
```

显示指定钩子的详细信息。

**参数：**

- `<name>`：钩子名称（例如 ``session-memory``）

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

## 检查钩子启用状态

```bash
openclaw hooks check
```

显示钩子启用状态汇总（已就绪与未就绪的数量对比）。

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

通过将钩子添加至配置文件（``~/.openclaw/config.json``）来启用特定钩子。

**注意：** 由插件管理的钩子在 ``openclaw hooks list`` 中显示为 ``plugin:<id>``，  
无法在此处启用或禁用。请改用插件自身的启用/禁用机制。

**参数：**

- `<name>`：钩子名称（例如 ``session-memory``）

**示例：**

```bash
openclaw hooks enable session-memory
```

**输出：**

```
✓ Enabled hook: 💾 session-memory
```

**执行操作：**

- 检查钩子是否存在且符合启用条件  
- 更新配置文件中的 ``hooks.internal.entries.<name>.enabled = true``  
- 将配置保存至磁盘  

**启用后：**  
- 重启网关，使钩子重新加载（macOS 上为菜单栏应用重启；开发环境中请重启网关进程）。

## 禁用钩子

```bash
openclaw hooks disable <name>
```

通过更新配置文件来禁用特定钩子。

**参数：**

- `<name>`：钩子名称（例如 ``command-logger``）

**示例：**

```bash
openclaw hooks disable command-logger
```

**输出：**

```
⏸ Disabled hook: 📝 command-logger
```

**禁用后：**  
- 重启网关，使钩子重新加载

## 安装钩子

```bash
openclaw hooks install <path-or-spec>
openclaw hooks install <npm-spec> --pin
```

从本地文件夹/归档包或 npm 安装钩子包。

npm 规范仅支持 **注册表源**（包名 + 可选的 **精确版本号** 或 **发布标签**）。  
Git/URL/文件路径规范及语义化版本范围均不被接受。依赖安装过程将使用 ``--ignore-scripts`` 以确保安全性。

裸规范（bare spec）和 ``@latest`` 默认保持稳定通道（stable track）。若 npm 将其中任一解析为预发布版本（prerelease），OpenClaw 将中止操作，并提示您显式选择预发布标签（如 ``@beta`` / ``@rc``）或指定精确的预发布版本号。

**执行操作：**

- 将钩子包复制到 ``~/.openclaw/hooks/<id>``  
- 在 ``hooks.internal.entries.*`` 中启用已安装的钩子  
- 在 ``hooks.internal.installs`` 下记录本次安装信息  

**选项：**

- `-l, --link`：链接本地目录而非复制（将其加入 ``hooks.internal.load.extraDirs``）  
- `--pin`：将 npm 安装记录为 ``name@version`` 的精确解析版本，并写入 ``hooks.internal.installs``

**支持的归档格式：** ``.zip``、``.tgz``、``.tar.gz``、``.tar``

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

更新已安装的钩子包（仅限 npm 安装方式）。

**选项：**

- `--all`：更新所有已跟踪的钩子包  
- `--dry-run`：预览变更内容，不实际写入  

当存在已存储的完整性哈希值（integrity hash），且获取到的新构件哈希值发生变化时，OpenClaw 将打印警告并请求确认，方可继续。可在 CI 或非交互式运行环境中使用全局 ``--yes`` 参数跳过提示。

## 内置钩子

### session-memory

在执行 ``/new`` 命令时，将会话上下文保存至内存。

**启用：**

```bash
openclaw hooks enable session-memory
```

**输出：** ``~/.openclaw/workspace/memory/YYYY-MM-DD-slug.md``

**参阅：** [session-memory 文档](/automation/hooks#session-memory)

### bootstrap-extra-files

在 ``agent:bootstrap`` 过程中注入额外的启动文件（例如单体仓库本地的 ``AGENTS.md`` / ``TOOLS.md``）。

**启用：**

```bash
openclaw hooks enable bootstrap-extra-files
```

**参阅：** [bootstrap-extra-files 文档](/automation/hooks#bootstrap-extra-files)

### command-logger

将所有命令事件记录至集中式审计日志文件。

**启用：**

```bash
openclaw hooks enable command-logger
```

**输出：** ``~/.openclaw/logs/commands.log``

**查看日志：**

```bash
# Recent commands
tail -n 20 ~/.openclaw/logs/commands.log

# Pretty-print
cat ~/.openclaw/logs/commands.log | jq .

# Filter by action
grep '"action":"new"' ~/.openclaw/logs/commands.log | jq .
```

**参阅：** [command-logger 文档](/automation/hooks#command-logger)

### boot-md

网关启动时（通道启动完成后）运行 ``BOOT.md``。

**触发事件：** ``gateway:startup``

**启用：**

```bash
openclaw hooks enable boot-md
```

**参阅：** [boot-md 文档](/automation/hooks#boot-md)