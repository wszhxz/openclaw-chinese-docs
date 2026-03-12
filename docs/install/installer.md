---
summary: "How the installer scripts work (install.sh, install-cli.sh, install.ps1), flags, and automation"
read_when:
  - You want to understand `openclaw.ai/install.sh`
  - You want to automate installs (CI / headless)
  - You want to install from a GitHub checkout
title: "Installer Internals"
---
# 安装程序内部机制

OpenClaw 提供三个安装脚本，托管于 `openclaw.ai`。

| 脚本                                 | 平台                 | 功能说明                                                                                     |
| ------------------------------------ | -------------------- | -------------------------------------------------------------------------------------------- |
| [`install.sh`](#installsh)           | macOS / Linux / WSL  | 如需则安装 Node，通过 npm（默认）或 git 安装 OpenClaw，并可运行入门引导流程。               |
| [`install-cli.sh`](#install-clish) | macOS / Linux / WSL  | 将 Node 和 OpenClaw 安装至本地前缀（`~/.openclaw`），无需 root 权限。                      |
| [`install.ps1`](#installps1)       | Windows（PowerShell）| 如需则安装 Node，通过 npm（默认）或 git 安装 OpenClaw，并可运行入门引导流程。               |

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

### 执行流程（install.sh）

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

### 源码检出检测

若在 OpenClaw 检出目录中运行（`package.json` + `pnpm-workspace.yaml`），脚本将提供以下选项：

- 使用当前检出（`git`），或  
- 使用全局安装（`npm`）

若不可用 TTY 且未指定安装方式，则默认采用 `npm` 并发出警告。

若安装方式选择无效，或 `--install-method` 值无效，脚本将以退出码 `2` 终止。

### 示例（install.sh）

<Tabs>
  <Tab title="Default">
    __CODE_BLOCK_24__
  </Tab>
  <Tab title="Skip onboarding">
    __CODE_BLOCK_25__
  </Tab>
  <Tab title="Git install">
    __CODE_BLOCK_26__
  </Tab>
  <Tab title="Dry run">
    __CODE_BLOCK_27__
  </Tab>
</Tabs>

<AccordionGroup>
  <Accordion title="Flags reference">

| Flag                            | Description                                                |
| ------------------------------- | ---------------------------------------------------------- |
| __CODE_BLOCK_28__     | Choose install method (default: __CODE_BLOCK_29__). Alias: __CODE_BLOCK_30__  |
| __CODE_BLOCK_31__                         | Shortcut for npm method                                    |
| __CODE_BLOCK_32__                         | Shortcut for git method. Alias: __CODE_BLOCK_33__                 |
| __CODE_BLOCK_34__ | npm version or dist-tag (default: __CODE_BLOCK_35__)                |
| __CODE_BLOCK_36__                        | Use beta dist-tag if available, else fallback to __CODE_BLOCK_37__  |
| __CODE_BLOCK_38__              | Checkout directory (default: __CODE_BLOCK_39__). Alias: __CODE_BLOCK_40__ |
| __CODE_BLOCK_41__               | Skip __CODE_BLOCK_42__ for existing checkout                      |
| __CODE_BLOCK_43__                   | Disable prompts                                            |
| __CODE_BLOCK_44__                  | Skip onboarding                                            |
| __CODE_BLOCK_45__                     | Enable onboarding                                          |
| __CODE_BLOCK_46__                     | Print actions without applying changes                     |
| __CODE_BLOCK_47__                     | Enable debug output (__CODE_BLOCK_48__, npm notice-level logs)      |
| __CODE_BLOCK_49__                        | Show usage (__CODE_BLOCK_50__)                                          |

  </Accordion>

  <Accordion title="Environment variables reference">

| Variable                                    | Description                                   |
| ------------------------------------------- | --------------------------------------------- |
| __CODE_BLOCK_51__          | Install method                                |
| __CODE_BLOCK_52__   | npm version or dist-tag                       |
| __CODE_BLOCK_53__                        | Use beta if available                         |
| __CODE_BLOCK_54__                   | Checkout directory                            |
| __CODE_BLOCK_55__                  | Toggle git updates                            |
| __CODE_BLOCK_56__                      | Disable prompts                               |
| __CODE_BLOCK_57__                     | Skip onboarding                               |
| __CODE_BLOCK_58__                        | Dry run mode                                  |
| __CODE_BLOCK_59__                        | Debug mode                                    |
| __CODE_BLOCK_60__ | npm log level                                 |
| __CODE_BLOCK_61__          | Control sharp/libvips behavior (default: __CODE_BLOCK_62__) |

  </Accordion>
</AccordionGroup>

---

## install-cli.sh

<Info>
Designed for environments where you want everything under a local prefix (default __CODE_BLOCK_63__) and no system Node dependency.
</Info>

### 执行流程（install-cli.sh）

<Steps>
  <Step title="Install local Node runtime">
    Downloads Node tarball (default __CODE_BLOCK_64__) to __CODE_BLOCK_65__ and verifies SHA-256.
  </Step>
  <Step title="Ensure Git">
    If Git is missing, attempts install via apt/dnf/yum on Linux or Homebrew on macOS.
  </Step>
  <Step title="Install OpenClaw under prefix">
    Installs with npm using __CODE_BLOCK_66__, then writes wrapper to __CODE_BLOCK_67__.
  </Step>
</Steps>

### 示例（install-cli.sh）

<Tabs>
  <Tab title="Default">
    __CODE_BLOCK_68__
  </Tab>
  <Tab title="Custom prefix + version">
    __CODE_BLOCK_69__
  </Tab>
  <Tab title="Automation JSON output">
    __CODE_BLOCK_70__
  </Tab>
  <Tab title="Run onboarding">
    __CODE_BLOCK_71__
  </Tab>
</Tabs>

<AccordionGroup>
  <Accordion title="参数参考">

| 参数                   | 描述                                                                             |
| ---------------------- | -------------------------------------------------------------------------------- |
| `--prefix <path>`      | 安装前缀（默认：`~/.openclaw`）                                                   |
| `--version <ver>`      | OpenClaw 版本或 dist-tag（默认：`latest`）                                      |
| `--node-version <ver>` | Node 版本（默认：`22.22.0`）                                                       |
| `--json`               | 输出 NDJSON 事件                                                                  |
| `--onboard`            | 安装后运行 `openclaw onboard`                                                        |
| `--no-onboard`         | 跳过入门引导流程（默认）                                                             |
| `--set-npm-prefix`     | 在 Linux 上，若当前前缀不可写，则强制将 npm 前缀设为 `~/.npm-global`                         |
| `--help`               | 显示用法（`-h`）                                                              |

  </Accordion>

  <Accordion title="环境变量参考">

| 变量                                        | 描述                                                                              |
| ------------------------------------------- | --------------------------------------------------------------------------------- |
| `OPENCLAW_PREFIX=<path>`                    | 安装前缀                                                                          |
| `OPENCLAW_VERSION=<ver>`                    | OpenClaw 版本或 dist-tag                                                          |
| `OPENCLAW_NODE_VERSION=<ver>`               | Node 版本                                                                         |
| `OPENCLAW_NO_ONBOARD=1`                     | 跳过入门引导                                                                      |
| `OPENCLAW_NPM_LOGLEVEL=error\|warn\|notice` | npm 日志级别                                                                      |
| `OPENCLAW_GIT_DIR=<path>`                   | 旧版清理查找路径（用于移除旧的 `Peekaboo` 子模块检出）                      |
| `SHARP_IGNORE_GLOBAL_LIBVIPS=0\|1`          | 控制 sharp/libvips 行为（默认值：`1`）                               |

  </Accordion>
</AccordionGroup>

---

## install.ps1

### 流程（install.ps1）

<Steps>
  <Step title="Ensure PowerShell + Windows environment">
    Requires PowerShell 5+.
  </Step>
  <Step title="Ensure Node.js 22+">
    If missing, attempts install via winget, then Chocolatey, then Scoop.
  </Step>
  <Step title="Install OpenClaw">
    - __CODE_BLOCK_9__ method (default): global npm install using selected __CODE_BLOCK_10__
    - __CODE_BLOCK_11__ method: clone/update repo, install/build with pnpm, and install wrapper at __CODE_BLOCK_12__
  </Step>
  <Step title="Post-install tasks">
    Adds needed bin directory to user PATH when possible, then runs __CODE_BLOCK_13__ on upgrades and git installs (best effort).
  </Step>
</Steps>

### 示例（install.ps1）

<Tabs>
  <Tab title="Default">
    __CODE_BLOCK_14__
  </Tab>
  <Tab title="Git install">
    __CODE_BLOCK_15__
  </Tab>
  <Tab title="Custom git directory">
    __CODE_BLOCK_16__
  </Tab>
  <Tab title="Dry run">
    __CODE_BLOCK_17__
  </Tab>
  <Tab title="Debug trace">
    __CODE_BLOCK_18__
  </Tab>
</Tabs>

<AccordionGroup>
  <Accordion title="Flags reference">

| Flag                      | Description                                            |
| ------------------------- | ------------------------------------------------------ |
| __CODE_BLOCK_19__ | Install method (default: __CODE_BLOCK_20__)                        |
| __CODE_BLOCK_21__              | npm dist-tag (default: __CODE_BLOCK_22__)                       |
| __CODE_BLOCK_23__          | Checkout directory (default: __CODE_BLOCK_24__) |
| __CODE_BLOCK_25__              | Skip onboarding                                        |
| __CODE_BLOCK_26__            | Skip __CODE_BLOCK_27__                                        |
| __CODE_BLOCK_28__                 | Print actions only                                     |

  </Accordion>

  <Accordion title="Environment variables reference">

| Variable                           | Description        |
| ---------------------------------- | ------------------ |
| __CODE_BLOCK_29__ | Install method     |
| __CODE_BLOCK_30__          | Checkout directory |
| __CODE_BLOCK_31__            | Skip onboarding    |
| __CODE_BLOCK_32__            | Disable git pull   |
| __CODE_BLOCK_33__               | Dry run mode       |

  </Accordion>
</AccordionGroup>

<Note>
If __CODE_BLOCK_34__ is used and Git is missing, the script exits and prints the Git for Windows link.
</Note>

---

## CI 和自动化

使用非交互式标志/环境变量以实现可预测的运行。

<Tabs>
  <Tab title="install.sh (non-interactive npm)">
    __CODE_BLOCK_35__
  </Tab>
  <Tab title="install.sh (non-interactive git)">
    __CODE_BLOCK_36__
  </Tab>
  <Tab title="install-cli.sh (JSON)">
    __CODE_BLOCK_37__
  </Tab>
  <Tab title="install.ps1 (skip onboarding)">
    __CODE_BLOCK_38__
  </Tab>
</Tabs>

---

## 故障排除

<AccordionGroup>
  <Accordion title="Why is Git required?">
    Git is required for __CODE_BLOCK_39__ install method. For __CODE_BLOCK_40__ installs, Git is still checked/installed to avoid __CODE_BLOCK_41__ failures when dependencies use git URLs.
  </Accordion>

  <Accordion title="Why does npm hit EACCES on Linux?">
    Some Linux setups point npm global prefix to root-owned paths. __CODE_BLOCK_42__ can switch prefix to __CODE_BLOCK_43__ and append PATH exports to shell rc files (when those files exist).
  </Accordion>

  <Accordion title="sharp/libvips issues">
    The scripts default __CODE_BLOCK_44__ to avoid sharp building against system libvips. To override:

    __CODE_BLOCK_45__

  </Accordion>

  <Accordion title='Windows: "npm error spawn git / ENOENT"'>
    Install Git for Windows, reopen PowerShell, rerun installer.
  </Accordion>

  <Accordion title='Windows: "openclaw is not recognized"'>
    Run __CODE_BLOCK_46__ and add that directory to your user PATH (no __CODE_BLOCK_47__ suffix needed on Windows), then reopen PowerShell.
  </Accordion>

  <Accordion title="Windows: how to get verbose installer output">
    __CODE_BLOCK_48__ does not currently expose a __CODE_BLOCK_49__ switch.
    Use PowerShell tracing for script-level diagnostics:

    __CODE_BLOCK_50__

  </Accordion>

  <Accordion title="openclaw not found after install">
    Usually a PATH issue. See [Node.js troubleshooting](/install/node#troubleshooting).
  </Accordion>
</AccordionGroup>