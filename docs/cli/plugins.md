---
summary: "CLI reference for `openclaw plugins` (list, install, uninstall, enable/disable, doctor)"
read_when:
  - You want to install or manage in-process Gateway plugins
  - You want to debug plugin load failures
title: "plugins"
---
# `openclaw plugins`

管理网关插件/扩展（进程内加载）。

相关：

- 插件系统：[Plugins](/tools/plugin)
- 插件清单 + 架构：[Plugin manifest](/plugins/manifest)
- 安全强化：[Security](/gateway/security)

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

捆绑插件随 OpenClaw 发货但默认处于禁用状态。使用 `plugins enable` 来
激活它们。

所有插件必须附带一个 `openclaw.plugin.json` 文件，其中包含内联 JSON 架构
(`configSchema`，即使为空）。缺失或无效的清单或架构会阻止插件加载并导致配置验证失败。

### 安装

```bash
openclaw plugins install <path-or-spec>
openclaw plugins install <npm-spec> --pin
```

安全注意事项：将插件安装视为运行代码。优先使用固定版本。

Npm 规范是仅限**注册表**（包名称 + 可选版本/标签）。Git/URL/文件规范被拒绝。依赖项安装使用 `--ignore-scripts` 以确保安全。

支持的归档格式：`.zip`，`.tgz`，`.tar.gz`，`.tar`。

使用 `--link` 避免复制本地目录（添加到 `plugins.load.paths`）：

```bash
openclaw plugins install -l ./my-plugin
```

在 npm 安装中使用 `--pin` 以保存解析后的精确规范 (`name@version`) 到
`plugins.installs`，同时保持默认行为不固定。

### 卸载

```bash
openclaw plugins uninstall <id>
openclaw plugins uninstall <id> --dry-run
openclaw plugins uninstall <id> --keep-files
```

`uninstall` 从 `plugins.entries`，`plugins.installs`，
插件白名单以及适用的链接 `plugins.load.paths` 条目中移除插件记录。
对于活动内存插件，内存槽重置为 `memory-core`。

默认情况下，卸载还会删除活动状态目录下的插件安装目录（位于扩展根目录下 `$OPENCLAW_STATE_DIR/extensions/<id>`）。使用
`--keep-files` 保留磁盘上的文件。

`--keep-config` 作为已弃用的别名支持 `--keep-files`。

### 更新

```bash
openclaw plugins update <id>
openclaw plugins update --all
openclaw plugins update <id> --dry-run
```

更新仅适用于从 npm 安装的插件（在 `plugins.installs` 中跟踪）。

当存储的完整性哈希存在且获取的工件哈希发生变化时，
OpenClaw 会打印警告并要求确认后继续。使用全局 `--yes` 在 CI/非交互式运行中绕过提示。