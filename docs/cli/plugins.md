---
summary: "CLI reference for `openclaw plugins` (list, install, uninstall, enable/disable, doctor)"
read_when:
  - You want to install or manage in-process Gateway plugins
  - You want to debug plugin load failures
title: "plugins"
---
# `openclaw plugins`

管理网关插件/扩展（在进程中加载）。

相关文档：

- 插件系统：[插件](/tools/plugin)  
- 插件清单 + 模式定义：[插件清单](/plugins/manifest)  
- 安全加固：[安全性](/gateway/security)

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

捆绑插件随 OpenClaw 一同发布，但默认处于禁用状态。请使用 `plugins enable` 启用它们。

所有插件都必须包含一个 `openclaw.plugin.json` 文件，并内嵌 JSON Schema（即 `configSchema`，即使为空）。缺失或无效的清单文件或 Schema 将导致插件无法加载，并使配置验证失败。

### 安装

```bash
openclaw plugins install <path-or-spec>
openclaw plugins install <npm-spec> --pin
```

安全提示：请将插件安装视为运行任意代码。建议优先使用固定版本（pinned version）。

Npm 规范仅支持**注册表形式**（包名 + 可选的**精确版本号**或**dist-tag**）。Git/URL/本地文件规范以及 semver 范围均被拒绝。依赖安装将在 `--ignore-scripts` 模式下执行，以确保安全性。

裸规范（bare spec）和 `@latest` 默认保持在稳定版本轨道上。若 npm 将其中任一解析为预发布版本（prerelease），OpenClaw 将中止操作，并要求您显式选择加入，例如通过指定预发布标签 `@beta`/`@rc`，或指定精确的预发布版本号（如 `@1.2.3-beta.4`）。

若裸安装规范与某个已捆绑插件 ID 匹配（例如 `diffs`），OpenClaw 将直接安装该捆绑插件。若要安装同名的 npm 包，请使用显式的带作用域规范（例如 `@scope/diffs`）。

支持的归档格式：`.zip`、`.tgz`、`.tar.gz`、`.tar`。

使用 `--link` 可避免复制本地目录（该操作会添加到 `plugins.load.paths`）：

```bash
openclaw plugins install -l ./my-plugin
```

在 npm 安装过程中使用 `--pin`，可将解析后的精确规范（即 `name@version`）保存至 `plugins.installs`，同时保留默认行为（即不锁定版本）。

### 卸载

```bash
openclaw plugins uninstall <id>
openclaw plugins uninstall <id> --dry-run
openclaw plugins uninstall <id> --keep-files
```

`uninstall` 会从 `plugins.entries`、`plugins.installs`、插件白名单以及适用的链接 `plugins.load.paths` 条目中移除插件记录。对于处于活动状态的内存插件，其内存槽将重置为 `memory-core`。

默认情况下，卸载操作还会删除活动状态目录下的插件扩展根目录（即 `$OPENCLAW_STATE_DIR/extensions/<id>`）中的插件安装目录。如需保留在磁盘上的文件，请使用 `--keep-files`。

`--keep-config` 作为 `--keep-files` 的已弃用别名，仍受支持。

### 更新

```bash
openclaw plugins update <id>
openclaw plugins update --all
openclaw plugins update <id> --dry-run
```

更新操作仅适用于从 npm 安装的插件（记录于 `plugins.installs` 中）。

当存在已存储的完整性哈希值（integrity hash），且所获取构件（artifact）的新哈希值发生变化时，OpenClaw 将打印警告，并在继续操作前请求确认。可在 CI 或非交互式运行环境中，使用全局选项 `--yes` 跳过此类提示。