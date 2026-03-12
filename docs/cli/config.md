---
summary: "CLI reference for `openclaw config` (get/set/unset/file/validate)"
read_when:
  - You want to read or edit config non-interactively
title: "config"
---
# `openclaw config`

配置辅助工具：通过路径获取/设置/取消设置/验证值，并打印当前生效的配置文件。不带子命令运行时将启动配置向导（等同于 `openclaw configure`）。

## 示例

```bash
openclaw config file
openclaw config get browser.executablePath
openclaw config set browser.executablePath "/usr/bin/google-chrome"
openclaw config set agents.defaults.heartbeat.every "2h"
openclaw config set agents.list[0].tools.exec.node "node-id-or-name"
openclaw config unset tools.web.search.apiKey
openclaw config validate
openclaw config validate --json
```

## 路径

路径支持点号（dot）或方括号（bracket）表示法：

```bash
openclaw config get agents.defaults.workspace
openclaw config get agents.list[0].id
```

使用代理列表索引定位特定代理：

```bash
openclaw config get agents.list
openclaw config set agents.list[1].tools.exec.node "node-id-or-name"
```

## 值

值在可能的情况下按 JSON5 解析；否则作为字符串处理。  
使用 `--strict-json` 可强制要求以 JSON5 方式解析。`--json` 仍作为遗留别名予以支持。

```bash
openclaw config set agents.defaults.heartbeat.every "0m"
openclaw config set gateway.port 19001 --strict-json
openclaw config set channels.whatsapp.groups '["*"]' --strict-json
```

## 子命令

- `config file`：打印当前生效的配置文件路径（从 `OPENCLAW_CONFIG_PATH` 或默认位置解析得出）。

编辑后需重启网关。

## 验证

在不启动网关的前提下，依据当前生效的模式（schema）验证现有配置。

```bash
openclaw config validate
openclaw config validate --json
```