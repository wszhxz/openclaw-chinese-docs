---
title: "Node.js"
summary: "Install and configure Node.js for OpenClaw — version requirements, install options, and PATH troubleshooting"
read_when:
  - "You need to install Node.js before installing OpenClaw"
  - "You installed OpenClaw but `openclaw` is command not found"
  - "npm install -g fails with permissions or PATH issues"
---
# Node.js

OpenClaw 需要 **Node 22 或更高版本**。[安装脚本](/install#install-methods) 将自动检测并安装 Node —— 本页面适用于您希望自行设置 Node 并确保所有配置正确（版本、PATH、全局安装等）的情况。

## 检查您的版本

```bash
node -v
```

如果输出为 `v22.x.x` 或更高版本，则一切正常。如果尚未安装 Node，或版本过低，请在下方选择一种安装方式。

## 安装 Node

<Tabs>
  <Tab title="macOS">
    **Homebrew** (recommended):

    __CODE_BLOCK_2__

    Or download the macOS installer from [nodejs.org](https://nodejs.org/).

  </Tab>
  <Tab title="Linux">
    **Ubuntu / Debian:**

    __CODE_BLOCK_3__

    **Fedora / RHEL:**

    __CODE_BLOCK_4__

    Or use a version manager (see below).

  </Tab>
  <Tab title="Windows">
    **winget** (recommended):

    __CODE_BLOCK_5__

    **Chocolatey:**

    __CODE_BLOCK_6__

    Or download the Windows installer from [nodejs.org](https://nodejs.org/).

  </Tab>
</Tabs>

<Accordion title="使用版本管理器（nvm、fnm、mise、asdf）">
  版本管理器可让您轻松切换 Node 版本。常用选项包括：

- [**fnm**](https://github.com/Schniz/fnm) — 快速、跨平台
- [**nvm**](https://github.com/nvm-sh/nvm) — 在 macOS/Linux 上广泛使用
- [**mise**](https://mise.jdx.dev/) — 多语言支持（Node、Python、Ruby 等）

使用 fnm 的示例：

```bash
fnm install 22
fnm use 22
```

  <Warning>
  Make sure your version manager is initialized in your shell startup file (__CODE_BLOCK_8__ or __CODE_BLOCK_9__). If it isn't, __CODE_BLOCK_10__ may not be found in new terminal sessions because the PATH won't include Node's bin directory.
  </Warning>
</Accordion>

## 故障排除

### `openclaw: command not found`

这几乎总是意味着 npm 的全局 bin 目录未添加到您的 PATH 中。

<Steps>
  <Step title="Find your global npm prefix">
    __CODE_BLOCK_12__
  </Step>
  <Step title="Check if it's on your PATH">
    __CODE_BLOCK_13__

    Look for __CODE_BLOCK_14__ (macOS/Linux) or __CODE_BLOCK_15__ (Windows) in the output.

  </Step>
  <Step title="Add it to your shell startup file">
    <Tabs>
      <Tab title="macOS / Linux">
        Add to __CODE_BLOCK_16__ or __CODE_BLOCK_17__:

        __CODE_BLOCK_18__

        Then open a new terminal (or run __CODE_BLOCK_19__ in zsh / __CODE_BLOCK_20__ in bash).
      </Tab>
      <Tab title="Windows">
        Add the output of __CODE_BLOCK_21__ to your system PATH via Settings → System → Environment Variables.
      </Tab>
    </Tabs>

  </Step>
</Steps>

### 在 `npm install -g` 上出现权限错误（Linux）

如果您看到 `EACCES` 错误，请将 npm 的全局前缀更改为用户可写目录：

```bash
mkdir -p "$HOME/.npm-global"
npm config set prefix "$HOME/.npm-global"
export PATH="$HOME/.npm-global/bin:$PATH"
```

将 `export PATH=...` 行添加到您的 `~/.bashrc` 或 `~/.zshrc` 文件中，以使其永久生效。