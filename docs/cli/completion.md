---
summary: "CLI reference for `openclaw completion` (generate/install shell completion scripts)"
read_when:
  - You want shell completions for zsh/bash/fish/PowerShell
  - You need to cache completion scripts under OpenClaw state
title: "completion"
---
# `openclaw completion`

生成 shell 补全脚本，并可选择将其安装到您的 shell 配置文件中。

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

- `-s, --shell <shell>`: shell 目标（`zsh`、`bash`、`powershell`、`fish`；默认：`zsh`）
- `-i, --install`: 通过向 shell 配置文件添加 source 行来安装补全
- `--write-state`: 将补全脚本写入 `$OPENCLAW_STATE_DIR/completions` 而不打印到 stdout
- `-y, --yes`: 跳过安装确认提示

## 注意事项

- `--install` 会在您的 shell 配置文件中写入一个小型"OpenClaw Completion"块，并将其指向缓存的脚本。
- 如果没有 `--install` 或 `--write-state`，命令会将脚本打印到 stdout。
- 补全生成会急切地加载命令树，以便包含嵌套子命令。