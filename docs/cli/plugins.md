---
summary: "CLI reference for `openclaw plugins` (list, install, uninstall, enable/disable, doctor)"
read_when:
  - You want to install or manage in-process Gateway plugins
  - You want to debug plugin load failures
title: "plugins"
---
# `openclaw plugins`

管理 Gateway 插件/扩展（进程内加载）。

相关：

- 插件系统：[插件](/tools/plugin)
- 插件清单 + 架构：[插件清单](/plugins/manifest)
- 安全加固：[安全](/gateway/security)

## 命令

```bash
openclaw plugins list
openclaw plugins info <id>
openclaw plugins enable <id>
openclaw plugins disable <id>
openclaw plugins uninstall <id>
openclaw plugins doctor
openclaw plugins update <id>
openclaw plugins update --all
```

捆绑插件随 OpenClaw 提供，但初始处于禁用状态。使用 `plugins enable` 激活它们。

所有插件必须附带一个 `openclaw.plugin.json` 文件，其中包含内联 JSON Schema
（`configSchema`，即使为空）。缺失或无效的清单或架构将阻止插件加载并导致配置验证失败。

### 安装

```bash
openclaw plugins install <path-or-spec>
openclaw plugins install <npm-spec> --pin
```

安全说明：对待插件安装应如同运行代码。建议使用固定版本。

Npm 规格仅限 **registry-only**（包名 + 可选的 **exact version** 或 **dist-tag**）。Git/URL/file 规格和 semver 范围将被拒绝。依赖安装出于安全考虑会使用 `--ignore-scripts` 运行。

裸规格和 `@latest` 保持在稳定轨道上。如果 npm 将其中任何一个解析为预发布版本，OpenClaw 将停止并要求你显式选择加入预发布标签，例如 `@beta`/`@rc` 或精确预发布版本例如 `@1.2.3-beta.4`。

如果裸安装规格与捆绑插件 ID 匹配（例如 `diffs`），OpenClaw 将直接安装捆绑插件。要安装同名的 npm 包，请使用显式作用域规格（例如 `@scope/diffs`）。

支持的归档格式：`.zip`, `.tgz`, `.tar.gz`, `.tar`。

使用 `--link` 避免复制本地目录（添加到 `plugins.load.paths`）：

```bash
openclaw plugins install -l ./my-plugin
```

在 npm 安装时使用 `--pin` 将解析后的精确规格 (`name@version`) 保存到 `plugins.installs` 中，同时保持默认行为不固定版本。

### 卸载

```bash
openclaw plugins uninstall <id>
openclaw plugins uninstall <id> --dry-run
openclaw plugins uninstall <id> --keep-files
```

`uninstall` 从 `plugins.entries`、`plugins.installs`、插件允许列表以及链接的 `plugins.load.paths` 条目中移除插件记录（如适用）。对于活动内存插件，内存槽位重置为 `memory-core`。

默认情况下，卸载还会移除活动状态目录扩展根目录下的插件安装目录 (`$OPENCLAW_STATE_DIR/extensions/<id>`)。使用 `--keep-files` 保留磁盘上的文件。

`--keep-config` 作为 `--keep-files` 的已弃用别名受支持。

### 更新

```bash
openclaw plugins update <id>
openclaw plugins update --all
openclaw plugins update <id> --dry-run
```

更新仅适用于从 npm 安装的插件（在 `plugins.installs` 中跟踪）。

当存在存储的完整性哈希且获取的工件哈希发生变化时，OpenClaw 会打印警告并在继续之前请求确认。使用全局 `--yes` 在 CI/非交互式运行中绕过提示。