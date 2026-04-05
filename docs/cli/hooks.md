---
summary: "CLI reference for `openclaw hooks` (agent hooks)"
read_when:
  - You want to manage agent hooks
  - You want to inspect hook availability or enable workspace hooks
title: "hooks"
---
# `openclaw hooks`

管理代理钩子（针对 ``/new``、``/reset`` 及网关启动等命令的事件驱动自动化）。

运行 ``openclaw hooks`` 且不带子命令等同于 ``openclaw hooks list``。

相关：

- 钩子：[钩子](/automation/hooks)
- 插件钩子：[插件钩子](/plugins/architecture#provider-runtime-hooks)

## 列出所有钩子

````bash
openclaw hooks list
````

列出工作区、托管、额外和捆绑目录中发现的所有钩子。

**选项：**

- ``--eligible``: 仅显示符合条件的钩子（满足要求）
- ``--json``: 以 JSON 格式输出
- ``-v, --verbose``: 显示详细信息，包括缺失的要求

**示例输出：**

````
Hooks (4/4 ready)

Ready:
  🚀 boot-md ✓ - Run BOOT.md on gateway startup
  📎 bootstrap-extra-files ✓ - Inject extra workspace bootstrap files during agent bootstrap
  📝 command-logger ✓ - Log all command events to a centralized audit file
  💾 session-memory ✓ - Save session context to memory when /new or /reset command is issued
````

**示例（详细模式）：**

````bash
openclaw hooks list --verbose
````

显示不符合条件钩子的缺失要求。

**示例（JSON）：**

````bash
openclaw hooks list --json
````

返回结构化 JSON 以供程序使用。

## 获取钩子信息

````bash
openclaw hooks info <name>
````

显示特定钩子的详细信息。

**参数：**

- ``<name>``: 钩子名称或钩子键（例如 ``session-memory``）

**选项：**

- ``--json``: 以 JSON 格式输出

**示例：**

````bash
openclaw hooks info session-memory
````

**输出：**

````
💾 session-memory ✓ Ready

Save session context to memory when /new or /reset command is issued

Details:
  Source: openclaw-bundled
  Path: /path/to/openclaw/hooks/bundled/session-memory/HOOK.md
  Handler: /path/to/openclaw/hooks/bundled/session-memory/handler.ts
  Homepage: https://docs.openclaw.ai/automation/hooks#session-memory
  Events: command:new, command:reset

Requirements:
  Config: ✓ workspace.dir
````

## 检查钩子资格

````bash
openclaw hooks check
````

显示钩子资格状态摘要（有多少已就绪与未就绪）。

**选项：**

- ``--json``: 以 JSON 格式输出

**示例输出：**

````
Hooks Status

Total hooks: 4
Ready: 4
Not ready: 0
````

## 启用钩子

````bash
openclaw hooks enable <name>
````

通过将钩子添加到配置来启用特定钩子（默认为 ``~/.openclaw/openclaw.json``）。

**注意：** 工作区钩子默认禁用，直到在此处或配置中启用。由插件管理的钩子在 ``openclaw hooks list`` 中显示 ``plugin:<id>``，无法在此处启用/禁用。请启用/禁用插件本身。

**参数：**

- ``<name>``: 钩子名称（例如 ``session-memory``）

**示例：**

````bash
openclaw hooks enable session-memory
````

**输出：**

````
✓ Enabled hook: 💾 session-memory
````

**功能说明：**

- 检查钩子是否存在且符合条件
- 更新配置中的 ``hooks.internal.entries.<name>.enabled = true``
- 将配置保存到磁盘

如果钩子来自 ``<workspace>/hooks/``，在网关加载它之前需要此可选步骤。

**启用后：**

- 重启网关以重新加载钩子（macOS 上重启菜单栏应用，或在开发环境中重启网关进程）。

## 禁用钩子

````bash
openclaw hooks disable <name>
````

通过更新配置来禁用特定钩子。

**参数：**

- ``<name>``: 钩子名称（例如 ``command-logger``）

**示例：**

````bash
openclaw hooks disable command-logger
````

**输出：**

````
⏸ Disabled hook: 📝 command-logger
````

**禁用后：**

- 重启网关以重新加载钩子

## 注意事项

- ``openclaw hooks list --json``、``info --json`` 和 ``check --json`` 直接将结构化 JSON 写入 stdout。
- 插件管理的钩子无法在此处启用或禁用；请启用或禁用所属插件。

## 安装钩子包

````bash
openclaw plugins install <package>        # ClawHub first, then npm
openclaw plugins install <package> --pin  # pin version
openclaw plugins install <path>           # local path
````

通过统一插件安装器安装钩子包。

``openclaw hooks install`` 仍作为兼容别名工作，但它会打印弃用警告并转发到 ``openclaw plugins install``。

NPM 规范是**仅限注册表**的（包名 + 可选的**精确版本**或**发行标签**）。Git/URL/文件规范和 semver 范围将被拒绝。依赖安装使用 ``--ignore-scripts`` 运行以确保安全。

裸规范和 ``@latest`` 保持在稳定轨道上。如果 npm 将其中任何一个解析为预发布版本，OpenClaw 将停止并要求您明确选择加入，使用预发布标签如 ``@beta``/``@rc`` 或确切的预发布版本。

**功能说明：**

- 将钩子包复制到 ``~/.openclaw/hooks/<id>``
- 在 ``hooks.internal.entries.*`` 中启用安装的钩子
- 在 ``hooks.internal.installs`` 下记录安装

**选项：**

- ``-l, --link``: 链接本地目录而不是复制（将其添加到 ``hooks.internal.load.extraDirs``）
- ``--pin``: 在 ``hooks.internal.installs`` 中将 npm 安装记录为确切解析的 ``name@version``

**支持的归档：** ``.zip``、``.tgz``、``.tar.gz``、``.tar``

**示例：**

````bash
# Local directory
openclaw plugins install ./my-hook-pack

# Local archive
openclaw plugins install ./my-hook-pack.zip

# NPM package
openclaw plugins install @openclaw/my-hook-pack

# Link a local directory without copying
openclaw plugins install -l ./my-hook-pack
````

链接的钩子包被视为来自操作员配置目录的托管钩子，而不是工作区钩子。

## 更新钩子包

````bash
openclaw plugins update <id>
openclaw plugins update --all
````

通过统一插件更新器更新跟踪的基于 npm 的钩子包。

``openclaw hooks update`` 仍作为兼容别名工作，但它会打印弃用警告并转发到 ``openclaw plugins update``。

**选项：**

- ``--all``: 更新所有跟踪的钩子包
- ``--dry-run``: 显示更改内容而不写入

当存储的完整性哈希存在且获取的工件哈希发生变化时，OpenClaw 会打印警告并在继续前请求确认。在全局 ``--yes`` 中使用以在 CI/非交互式运行中绕过提示。

## 捆绑钩子

### session-memory

当您发出 ``/new`` 或 ``/reset`` 时将会话上下文保存到内存。

**启用：**

````bash
openclaw hooks enable session-memory
````

**输出：** ``~/.openclaw/workspace/memory/YYYY-MM-DD-slug.md``

**查看：** [session-memory 文档](/automation/hooks#session-memory)

### bootstrap-extra-files

在 ``agent:bootstrap`` 期间注入额外的引导文件（例如 monorepo-local ``AGENTS.md`` / ``TOOLS.md``）。

**启用：**

````bash
openclaw hooks enable bootstrap-extra-files
````

**查看：** [bootstrap-extra-files 文档](/automation/hooks#bootstrap-extra-files)

### command-logger

将所有命令事件记录到集中式审计文件中。

**启用：**

````bash
openclaw hooks enable command-logger
````

**输出：** ``~/.openclaw/logs/commands.log``

**查看日志：**

````bash
# Recent commands
tail -n 20 ~/.openclaw/logs/commands.log

# Pretty-print
cat ~/.openclaw/logs/commands.log | jq .

# Filter by action
grep '"action":"new"' ~/.openclaw/logs/commands.log | jq .
````

**查看：** [command-logger 文档](/automation/hooks#command-logger)

### boot-md

网关启动时（通道启动后）运行 ``BOOT.md``。

**事件：** ``gateway:startup``

**启用：**

````bash
openclaw hooks enable boot-md
````

**查看：** [boot-md 文档](/automation/hooks#boot-md)