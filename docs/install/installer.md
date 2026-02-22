---
summary: "How the installer scripts work (install.sh, install-cli.sh, install.ps1), flags, and automation"
read_when:
  - You want to understand `openclaw.ai/install.sh`
  - You want to automate installs (CI / headless)
  - You want to install from a GitHub checkout
title: "Installer Internals"
---
# 安装程序内部

OpenClaw 提供三个安装脚本，托管在 `openclaw.ai`。

| 脚本                             | 平台             | 功能                                                                                     |
| ---------------------------------- | -------------------- | -------------------------------------------------------------------------------------------- |
| [`install.sh`](#installsh)         | macOS / Linux / WSL  | 如需安装 Node，则安装 Node，通过 npm（默认）或 git 安装 OpenClaw，并可运行引导设置。 |
| [`install-cli.sh`](#install-clish) | macOS / Linux / WSL  | 将 Node + OpenClaw 安装到本地前缀 (`~/.openclaw`)。无需 root 权限。              |
| [`install.ps1`](#installps1)       | Windows (PowerShell) | 如需安装 Node，则安装 Node，通过 npm（默认）或 git 安装 OpenClaw，并可运行引导设置。 |

## 快速命令

<Tabs>
  <Tab title="install.sh">
    __CODE_BLOCK_5__

    __CODE_BLOCK_6__

  </Tab>
  <Tab title="install-cli.sh">
    __CODE_BLOCK_7__

    __CODE_BLOCK_8__

  </Tab>
  <Tab title="install.ps1">
    __CODE_BLOCK_9__

    __CODE_BLOCK_10__

  </Tab>
</Tabs>

<Note>
If install succeeds but __CODE_BLOCK_11__ is not found in a new terminal, see [Node.js troubleshooting](/install/node#troubleshooting).
</Note>

---

## install.sh

<Tip>
Recommended for most interactive installs on macOS/Linux/WSL.
</Tip>

### 流程 (install.sh)

<Steps>
  <Step title="Detect OS">
    Supports macOS and Linux (including WSL). If macOS is detected, installs Homebrew if missing.
  </Step>
  <Step title="Ensure Node.js 22+">
    Checks Node version and installs Node 22 if needed (Homebrew on macOS, NodeSource setup scripts on Linux apt/dnf/yum).
  </Step>
  <Step title="Ensure Git">
    Installs Git if missing.
  </Step>
  <Step title="Install OpenClaw">
    - __CODE_BLOCK_12__ method (default): global npm install
    - __CODE_BLOCK_13__ method: clone/update repo, install deps with pnpm, build, then install wrapper at __CODE_BLOCK_14__
  </Step>
  <Step title="Post-install tasks">
    - Runs __CODE_BLOCK_15__ on upgrades and git installs (best effort)
    - Attempts onboarding when appropriate (TTY available, onboarding not disabled, and bootstrap/config checks pass)
    - Defaults __CODE_BLOCK_16__
  </Step>
</Steps>

### 源代码检出检测

如果在 OpenClaw 检出目录中运行 (`package.json` + `pnpm-workspace.yaml`)，该脚本会提供：

- 使用 checkout (`git`)，或
- 使用全局安装 (`npm`)

如果没有可用的TTY且未设置安装方法，则默认使用 `npm` 并发出警告。

脚本在无效的方法选择或无效的 `--install-method` 值时以代码 `2` 退出。

### 示例 (install.sh)

<Tabs>
  <Tab title="Default">
    __CODE_BLOCK_5__
  </Tab>
  <Tab title="Skip onboarding">
    __CODE_BLOCK_6__
  </Tab>
  <Tab title="Git install">
    __CODE_BLOCK_7__
  </Tab>
  <Tab title="Dry run">
    __CODE_BLOCK_8__
  </Tab>
</Tabs>

<AccordionGroup>
  <Accordion title="标志参考">

| 标志                            | 描述                                                |
| ------------------------------- | ---------------------------------------------------------- |
| `--install-method npm\|git`     | 选择安装方法（默认：`npm`）。别名：`--method`  |
| `--npm`                         | npm 方法的快捷方式                                    |
| `--git`                         | git 方法的快捷方式。别名：`--github`                 |
| `--version <version\|dist-tag>` | npm 版本或 dist-tag（默认：`latest`）                |
| `--beta`                        | 如果可用则使用 beta dist-tag，否则回退到 `latest`  |
| `--git-dir <path>`              | 检出目录（默认：`~/openclaw`）。别名：`--dir` |
| `--no-git-update`               | 对于现有的检出跳过 `git pull`                      |
| `--no-prompt`                   | 禁用提示                                            |
| `--no-onboard`                  | 跳过入门                                            |
| `--onboard`                     | 启用入门                                          |
| `--dry-run`                     | 打印操作而不应用更改                     |
| `--verbose`                     | 启用调试输出 (`set -x`，npm notice级别日志)      |
| `--help`                        | 显示用法 (`-h`)                                          |

  </Accordion>

  <Accordion title="环境变量参考">

| 变量                                    | 描述                                   |
| ------------------------------------------- | --------------------------------------------- |
| `OPENCLAW_INSTALL_METHOD=git\|npm`          | 安装方法                                |
| `OPENCLAW_VERSION=latest\|next\|<semver>`   | npm 版本或 dist-tag                       |
| `OPENCLAW_BETA=0\|1`                        | 如果可用则使用 beta                         |
| `OPENCLAW_GIT_DIR=<path>`                   | 检出目录                            |
| `OPENCLAW_GIT_UPDATE=0\|1`                  | 切换 git 更新                            |
| `OPENCLAW_NO_PROMPT=1`                      | 禁用提示                               |
| `OPENCLAW_NO_ONBOARD=1`                     | 跳过引导                               |
| `OPENCLAW_DRY_RUN=1`                        | 干运行模式                                  |
| `OPENCLAW_VERBOSE=1`                        | 调试模式                                    |
| `OPENCLAW_NPM_LOGLEVEL=error\|warn\|notice` | npm 日志级别                                 |
| `SHARP_IGNORE_GLOBAL_LIBVIPS=0\|1`          | 控制 sharp/libvips 行为 (默认: `1`) |

  </Accordion>
</AccordionGroup>

---

## install-cli.sh

<Info>
Designed for environments where you want everything under a local prefix (default __CODE_BLOCK_12__) and no system Node dependency.
</Info>

### 流程 (install-cli.sh)

<Steps>
  <Step title="Install local Node runtime">
    Downloads Node tarball (default __CODE_BLOCK_13__) to __CODE_BLOCK_14__ and verifies SHA-256.
  </Step>
  <Step title="Ensure Git">
    If Git is missing, attempts install via apt/dnf/yum on Linux or Homebrew on macOS.
  </Step>
  <Step title="Install OpenClaw under prefix">
    Installs with npm using __CODE_BLOCK_15__, then writes wrapper to __CODE_BLOCK_16__.
  </Step>
</Steps>

### 示例 (install-cli.sh)

<Tabs>
  <Tab title="Default">
    __CODE_BLOCK_17__
  </Tab>
  <Tab title="Custom prefix + version">
    __CODE_BLOCK_18__
  </Tab>
  <Tab title="Automation JSON output">
    __CODE_BLOCK_19__
  </Tab>
  <Tab title="Run onboarding">
    __CODE_BLOCK_20__
  </Tab>
</Tabs>

<AccordionGroup>
  <Accordion title="标志参考">

| 标志                   | 描述                                                                     |
| ---------------------- | ------------------------------------------------------------------------------- |
| `--prefix <path>`      | 安装前缀（默认：`~/.openclaw`）                                         |
| `--version <ver>`      | OpenClaw 版本或 dist-tag（默认：`latest`）                                |
| `--node-version <ver>` | Node 版本（默认：`22.22.0`）                                               |
| `--json`               | 发射 NDJSON 事件                                                              |
| `--onboard`            | 安装后运行 `openclaw onboard`                                            |
| `--no-onboard`         | 跳过引导（默认）                                                       |
| `--set-npm-prefix`     | 在 Linux 上，如果当前前缀不可写，则强制 npm 前缀为 `~/.npm-global` |
| `--help`               | 显示用法 (`-h`)                                                               |

  </Accordion>

  <Accordion title="环境变量参考">

| 变量                                    | 描述                                                                       |
| ------------------------------------------- | --------------------------------------------------------------------------------- |
| `OPENCLAW_PREFIX=<path>`                    | 安装前缀                                                                    |
| `OPENCLAW_VERSION=<ver>`                    | OpenClaw 版本或 dist-tag                                                      |
| `OPENCLAW_NODE_VERSION=<ver>`               | Node 版本                                                                      |
| `OPENCLAW_NO_ONBOARD=1`                     | 跳过引导                                                                   |
| `OPENCLAW_NPM_LOGLEVEL=error\|warn\|notice` | npm 日志级别                                                                     |
| `OPENCLAW_GIT_DIR=<path>`                   | 旧版清理查找路径（在删除旧 `Peekaboo` 子模块检出时使用） |
| `SHARP_IGNORE_GLOBAL_LIBVIPS=0\|1`          | 控制 sharp/libvips 行为（默认：`1`）                                     |

  </Accordion>
</AccordionGroup>

---

## install.ps1

### 流程 (install.ps1)

<Steps>
  <Step title="Ensure PowerShell + Windows environment">
    Requires PowerShell 5+.
  </Step>
  <Step title="Ensure Node.js 22+">
    If missing, attempts install via winget, then Chocolatey, then Scoop.
  </Step>
  <Step title="Install OpenClaw">
    - __CODE_BLOCK_0__ method (default): global npm install using selected __CODE_BLOCK_1__
    - __CODE_BLOCK_2__ method: clone/update repo, install/build with pnpm, and install wrapper at __CODE_BLOCK_3__
  </Step>
  <Step title="Post-install tasks">
    Adds needed bin directory to user PATH when possible, then runs __CODE_BLOCK_4__ on upgrades and git installs (best effort).
  </Step>
</Steps>

### 示例 (install.ps1)

<Tabs>
  <Tab title="Default">
    __CODE_BLOCK_5__
  </Tab>
  <Tab title="Git install">
    __CODE_BLOCK_6__
  </Tab>
  <Tab title="Custom git directory">
    __CODE_BLOCK_7__
  </Tab>
  <Tab title="Dry run">
    __CODE_BLOCK_8__
  </Tab>
  <Tab title="Debug trace">
    __CODE_BLOCK_9__
  </Tab>
</Tabs>

<AccordionGroup>
  <Accordion title="Flags reference">

| Flag                      | Description                                            |
| ------------------------- | ------------------------------------------------------ |
| __CODE_BLOCK_10__ | Install method (default: __CODE_BLOCK_11__)                        |
| __CODE_BLOCK_12__              | npm dist-tag (default: __CODE_BLOCK_13__)                       |
| __CODE_BLOCK_14__          | Checkout directory (default: __CODE_BLOCK_15__) |
| __CODE_BLOCK_16__              | Skip onboarding                                        |
| __CODE_BLOCK_17__            | Skip __CODE_BLOCK_18__                                        |
| __CODE_BLOCK_19__                 | Print actions only                                     |

  </Accordion>

  <Accordion title="Environment variables reference">

| Variable                           | Description        |
| ---------------------------------- | ------------------ |
| __CODE_BLOCK_20__ | Install method     |
| __CODE_BLOCK_21__          | Checkout directory |
| __CODE_BLOCK_22__            | Skip onboarding    |
| __CODE_BLOCK_23__            | Disable git pull   |
| __CODE_BLOCK_24__               | Dry run mode       |

  </Accordion>
</AccordionGroup>

<Note>
If __CODE_BLOCK_25__ is used and Git is missing, the script exits and prints the Git for Windows link.
</Note>

---

## 持续集成和自动化

使用非交互式标志/环境变量以获得可预测的运行。

<Tabs>
  <Tab title="install.sh (non-interactive npm)">
    __CODE_BLOCK_0__
  </Tab>
  <Tab title="install.sh (non-interactive git)">
    __CODE_BLOCK_1__
  </Tab>
  <Tab title="install-cli.sh (JSON)">
    __CODE_BLOCK_2__
  </Tab>
  <Tab title="install.ps1 (skip onboarding)">
    __CODE_BLOCK_3__
  </Tab>
</Tabs>

---

## 故障排除

<AccordionGroup>
  <Accordion title="Why is Git required?">
    Git is required for __CODE_BLOCK_4__ install method. For __CODE_BLOCK_5__ installs, Git is still checked/installed to avoid __CODE_BLOCK_6__ failures when dependencies use git URLs.
  </Accordion>

  <Accordion title="Why does npm hit EACCES on Linux?">
    Some Linux setups point npm global prefix to root-owned paths. __CODE_BLOCK_7__ can switch prefix to __CODE_BLOCK_8__ and append PATH exports to shell rc files (when those files exist).
  </Accordion>

  <Accordion title="sharp/libvips issues">
    The scripts default __CODE_BLOCK_9__ to avoid sharp building against system libvips. To override:

    __CODE_BLOCK_10__

  </Accordion>

  <Accordion title='Windows: "npm error spawn git / ENOENT"'>
    Install Git for Windows, reopen PowerShell, rerun installer.
  </Accordion>

  <Accordion title='Windows: "openclaw is not recognized"'>
    Run __CODE_BLOCK_11__, append __CODE_BLOCK_12__, add that directory to user PATH, then reopen PowerShell.
  </Accordion>

  <Accordion title="Windows: how to get verbose installer output">
    __CODE_BLOCK_13__ does not currently expose a __CODE_BLOCK_14__ switch.
    Use PowerShell tracing for script-level diagnostics:

    __CODE_BLOCK_15__

  </Accordion>

  <Accordion title="openclaw not found after install">
    Usually a PATH issue. See [Node.js troubleshooting](/install/node#troubleshooting).
  </Accordion>
</AccordionGroup>