---
summary: "CLI reference for `openclaw hooks` (agent hooks)"
read_when:
  - You want to manage agent hooks
  - You want to install or update hooks
title: "hooks"
---
# `openclaw 钩子`

管理代理钩子（针对命令如 `/new`、`/reset` 和网关启动的事件驱动自动化）。

相关：

- 钩子：[钩子](/hooks)
- 插件钩子：[插件](/plugin#plugin-hooks)

## 列出所有钩子

```bash
openclaw hooks list
```

列出从工作区、管理目录和捆绑目录中发现的所有钩子。

**选项：**

- `--eligible`：仅显示符合条件的钩子（需求已满足）
- `--json`：以 JSON 格式输出
- `-v, --verbose`：显示详细信息，包括缺失的需求

**示例输出：**

```
钩子 (4/4 已就绪)

已就绪：
  🚀 boot-md ✓ - 网关启动时运行 BOOT.md
  📝 command-logger ✓ - 将所有命令事件记录到集中式审计文件
  💾 session-memory ✓ - 在发出 `/new` 命令时将会话上下文保存到内存
  😈 soul-evil ✓ - 在清理窗口期间或随机机会下交换注入的 SOUL 内容
```

**示例（详细模式）：**

```bash
openclaw hooks list --verbose
```

显示不符合条件的钩子缺失的需求。

**示例（JSON 格式）：**

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

- `<name>`：钩子名称（例如 `session-memory`）

**选项：**

- `--json`：以 JSON 格式输出

**示例：**

```bash
openclaw hooks info session-memory
```

**输出：**

```
💾 session-memory ✓ 已就绪

在发出 `/new` 命令时将会话上下文保存到内存

详情：
  来源：openclaw-bundled
  路径：/path/to/openclaw/hooks/bundled/session-memory/HOOK.md
  处理程序：/path/to/openclaw/hooks/bundled/session-memory/handler.ts
  首页：https://docs.openclaw.ai/hooks#session-memory
  事件：command:new

需求：
  配置：✓ workspace.dir
```

## 检查钩子资格

```bash
openclaw hooks check
```

显示钩子资格状态摘要（已就绪与未就绪的钩子数量）。

**选项：**

- `--json`：以 JSON 格式输出

**示例输出：**

```
钩子状态

总钩子数：4
已就绪：4
未就绪：0
```

## 启用一个钩子

```bash
openclaw hooks enable <name>
```

通过将钩子添加到你的配置文件（`~/.openclaw/config.json`）来启用特定钩子。

**注意：** 由插件管理的钩子在 `openclaw hooks list` 中显示为 `plugin:<id>`，并且不能在此处启用/禁用。请启用/禁用插件本身。

**参数：**

- `<name>`：钩子名称（例如 `session-memory`）

**示例：**

```bash
openclaw hooks enable session-memory
```

**输出：**

```
✓ 已启用钩子：💾 session-memory
```

**作用：**

- 检查钩子是否存在且符合条件
- 更新你的配置文件中的 `hooks.internal.entries.<name>.enabled = true`
- 将配置保存到磁盘

**启用后：**

- 重启网关以重新加载钩子（在 macOS 上重启菜单栏应用，或在开发环境中重启网关进程）。

## 禁用一个钩子

```bash
openclaw hooks disable <name>
```

通过更新你的配置文件来禁用特定钩子。

**参数：**

- `<name>`：钩子名称（例如 `command-logger`）

**示例：**

```bash
openclaw hooks disable command-logger
```

**输出：**

```
⏸ 已禁用钩子：📝 command-logger
```

**禁用后：**

- 重启网关以重新加载钩子

## 安装钩子

```bash
openclaw hooks install <path-or-spec>
```

从本地文件夹/归档文件或 npm 安装钩子包。

**作用：**

- 将钩子包复制到 `~/.openclaw/hooks/<id>`
- 在 `hooks.internal.entries.*` 中启用已安装的钩子
- 在 `hooks.internal.installs` 中记录安装信息

**选项：**

- `-l, --link`：链接本地目录而非复制（将其添加到 `hooks.internal.load.extraDirs`）

**支持的归档文件：** `.zip`, `.tgz`, `.tar.gz`, `.tar`

**示例：**

```bash
# 本地目录
openclaw hooks install ./my-hook-pack

# 本地归档文件
openclaw hooks install ./my-hook-pack.zip

# NPM 包
openclaw hooks install @openclaw/my-hook-pack

# 链接本地目录而不复制
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
- `--dry-run`：显示更改内容而不实际写入

## 捆绑钩子

### session-memory

在发出 `/new` 命令时将会话上下文保存到内存。

**启用：**

```bash
openclaw hooks enable session-memory
```

**输出：** `~/.openclaw/workspace/memory/YYYY-MM-DD-slug.md`

**查看：** [session-memory 文档](/hooks#session-memory)

### command-logger

将所有命令事件记录到集中式审计文件。

**