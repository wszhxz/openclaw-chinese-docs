---
title: "Node.js + npm (PATH sanity)"
summary: "Node.js + npm install sanity: versions, PATH, and global installs"
read_when:
  - "You installed OpenClaw but `openclaw` is “command not found”"
  - "You’re setting up Node.js/npm on a new machine"
  - "npm install -g ... fails with permissions or PATH issues"
---
# Node.js + npm (PATH 问题排查)

OpenClaw 的运行时基线是 **Node 22+**。

如果你可以运行 `npm install -g openclaw@latest` 但后来看到 `openclaw: command not found`，这通常是 **PATH** 问题：npm 放置全局二进制文件的目录不在你的 shell 的 PATH 中。

## 快速诊断

运行：

```bash
node -v
npm -v
npm prefix -g
echo "$PATH"
```

如果 `$(npm prefix -g)/bin`（macOS/Linux）或 `$(npm prefix -g)`（Windows）不在 `echo "$PATH"` 内，你的 shell 找不到全局 npm 二进制文件（包括 `openclaw`）。

## 解决方案：将 npm 的全局 bin 目录添加到 PATH

1. 找到你的全局 npm 前缀：

```bash
npm prefix -g
```

2. 将全局 npm bin 目录添加到你的 shell 启动文件中：

- zsh: `~/.zshrc`
- bash: `~/.bashrc`

示例（将路径替换为你的 `npm prefix -g` 输出）：

```bash
# macOS / Linux
export PATH="/path/from/npm/prefix/bin:$PATH"
```

然后打开一个 **新终端**（或在 zsh 中运行 `rehash` / 在 bash 中运行 `hash -r`）。

在 Windows 上，将 `npm prefix -g` 的输出添加到你的 PATH。

## 解决方案：避免 `sudo npm install -g` / 权限错误（Linux）

如果 `npm install -g ...` 失败并显示 `EACCES`，将 npm 的全局前缀切换到一个用户可写的目录：

```bash
mkdir -p "$HOME/.npm-global"
npm config set prefix "$HOME/.npm-global"
export PATH="$HOME/.npm-global/bin:$PATH"
```

在你的 shell 启动文件中持久化 `export PATH=...` 行。

## 推荐的 Node 安装选项

如果你以一种方式安装 Node/npm，将会遇到最少的问题：

- 保持 Node 更新（22+）
- 使全局 npm bin 目录在新 shell 中稳定且位于 PATH

常见选择：

- macOS: Homebrew (`brew install node`) 或版本管理器
- Linux: 你偏好的版本管理器，或提供 Node 22+ 的发行版支持安装
- Windows: 官方 Node 安装程序，`winget`，或 Windows Node 版本管理器

如果你使用版本管理器（nvm/fnm/asdf 等），确保它在你日常使用的 shell 中初始化（zsh vs bash），以便在运行安装程序时设置的 PATH 存在。