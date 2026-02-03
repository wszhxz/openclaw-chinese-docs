---
summary: "CLI reference for `openclaw setup` (initialize config + workspace)"
read_when:
  - You’re doing first-run setup without the full onboarding wizard
  - You want to set the default workspace path
title: "setup"
---
# `openclaw setup`

初始化 `~/.openclaw/openclaw.json` 和 agent 工作区。

相关：

- 开始使用：[开始使用](/start/getting-started)
- 向导：[入门](/start/onboarding)

## 示例

```bash
openclaw setup
openclaw setup --workspace ~/.openclaw/workspace
```

通过 setup 运行向导：

```bash
openclaw setup --wizard
```