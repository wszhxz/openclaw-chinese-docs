---
summary: "CLI reference for `openclaw plugins` (list, install, enable/disable, doctor)"
read_when:
  - You want to install or manage in-process Gateway plugins
  - You want to debug plugin load failures
title: "plugins"
---
# `openclaw 插件`

管理网关插件/扩展（在进程内加载）。

相关：

- 插件系统：[插件](/plugin)
- 插件清单 + 架构：[插件清单](/plugins/manifest)
- 安全加固：[安全](/gateway/security)

## 命令

```bash
openclaw plugins list
openclaw plugins info <id>
openclaw plugins enable <id>
openclaw plugins disable <id>
openclaw plugins doctor
openclaw plugins update <id>
openclaw plugins update --all
```

内置插件随 OpenClaw 一起提供但默认禁用。使用 `plugins enable` 命令激活它们。

所有插件必须包含一个 `openclaw.plugin.json` 文件，并包含内联 JSON 架构（`configSchema`，即使为空）。缺少/无效的清单或架构会导致插件无法加载并使配置验证失败。

### 安装

```bash
openclaw plugins install <路径或规范>
```

安全提示：将插件安装视为运行代码。建议使用固定版本。

支持的压缩包格式：`.zip`, `.tgz`, `.tar.gz`, `.tar`。

使用 `--link` 参数可避免复制本地目录（添加到 `plugins.load.paths`）：

```bash
openclaw plugins install -l ./my-plugin
```

### 更新

```bash
openclaw plugins update <id>
openclaw plugins update --all
openclaw plugins update <id> --dry-run
```

更新仅适用于从 npm 安装的插件（记录在 `plugins.installs` 中）。