---
summary: "CLI reference for `openclaw setup` (initialize config + workspace)"
read_when:
  - You’re doing first-run setup without full CLI onboarding
  - You want to set the default workspace path
title: "setup"
---
# `openclaw setup`

初始化 `~/.openclaw/openclaw.json` 和代理工作区。

相关：

- 入门指南：[入门指南](/start/getting-started)
- CLI onboarding：[入门向导 (CLI)](/start/wizard)

## 示例

```bash
openclaw setup
openclaw setup --workspace ~/.openclaw/workspace
openclaw setup --wizard
openclaw setup --non-interactive --mode remote --remote-url wss://gateway-host:18789 --remote-token <token>
```

## 选项

- `--workspace <dir>`：代理工作区目录（存储为 `agents.defaults.workspace`）
- `--wizard`：运行 onboarding
- `--non-interactive`：无提示运行 onboarding
- `--mode <local|remote>`：onboarding 模式
- `--remote-url <url>`：远程 Gateway WebSocket URL
- `--remote-token <token>`：远程 Gateway token

通过 setup 运行 onboarding：

```bash
openclaw setup --wizard
```

注意：

- 直接 `openclaw setup` 初始化配置 + 工作区，不包含完整的 onboarding 流程。
- 当存在任何 onboarding 标志时，onboarding 将自动运行（`--wizard`，`--non-interactive`，`--mode`，`--remote-url`，`--remote-token`）。