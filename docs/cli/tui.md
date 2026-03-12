---
summary: "CLI reference for `openclaw tui` (terminal UI connected to the Gateway)"
read_when:
  - You want a terminal UI for the Gateway (remote-friendly)
  - You want to pass url/token/session from scripts
title: "tui"
---
# `openclaw tui`

打开连接到网关的终端用户界面（Terminal UI）。

相关文档：

- TUI 指南：[TUI](/web/tui)

注意事项：

- `tui` 在可能的情况下，解析已配置的网关身份验证 SecretRefs，以支持令牌/密码身份验证（适用于 `env`/`file`/`exec` 提供程序）。

## 示例

```bash
openclaw tui
openclaw tui --url ws://127.0.0.1:18789 --token <token>
openclaw tui --session main --deliver
```