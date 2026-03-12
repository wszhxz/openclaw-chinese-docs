---
summary: "CLI reference for `openclaw completion` (generate/install shell completion scripts)"
read_when:
  - You want shell completions for zsh/bash/fish/PowerShell
  - You need to cache completion scripts under OpenClaw state
title: "completion"
---
# `openclaw completion`

生成 Shell 补全脚本，并可选择将其安装到您的 Shell 配置文件中。

## 用法

```bash
openclaw completion
openclaw completion --shell zsh
openclaw completion --install
openclaw completion --shell fish --install
openclaw completion --write-state
openclaw completion --shell bash --write-state
```

## 选项

- `-s, --shell <shell>`: Shell 目标（`zsh`、`bash`、`powershell`、`fish`；默认值：`zsh`）
- `-i, --install`: 通过向 Shell 配置文件中添加 `source` 行来安装补全功能
- `--write-state`: 将补全脚本写入 `$OPENCLAW_STATE_DIR/completions`，而不输出到标准输出（stdout）
- `-y, --yes`: 跳过安装确认提示

## 注意事项

- `--install` 会在您的 Shell 配置文件中写入一小段“OpenClaw Completion”代码块，并使其指向缓存的脚本。
- 若未指定 `--install` 或 `--write-state`，该命令会将脚本打印到标准输出（stdout）。
- 补全脚本生成过程会主动加载命令树，因此嵌套的子命令也会被包含在内。