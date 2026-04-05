---
summary: "CLI reference for `openclaw tui` (terminal UI connected to the Gateway)"
read_when:
  - You want a terminal UI for the Gateway (remote-friendly)
  - You want to pass url/token/session from scripts
title: "tui"
---
# `openclaw tui`

打开连接到网关的终端 UI。

相关：

- TUI 指南：[TUI](/web/tui)

注意：

- `tui` 在可能时解析已配置的网关身份验证 SecretRefs 用于令牌/密码身份验证（`env`/`file`/`exec` 提供者）。
- 当从配置的代理工作区目录内部启动时，TUI 会自动选择该代理作为会话密钥默认值（除非 `--session` 显式设置为 `agent:<id>:...`）。

## 示例

```bash
openclaw tui
openclaw tui --url ws://127.0.0.1:18789 --token <token>
openclaw tui --session main --deliver
# when run inside an agent workspace, infers that agent automatically
openclaw tui --session bugfix
```