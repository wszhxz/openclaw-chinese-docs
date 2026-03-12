---
summary: "Install OpenClaw — installer script, npm/pnpm, from source, Docker, and more"
read_when:
  - You need an install method other than the Getting Started quickstart
  - You want to deploy to a cloud platform
  - You need to update, migrate, or uninstall
title: "Install"
---
# 安装

已经完成了[入门指南](/start/getting-started)？那您已准备就绪——本页介绍替代安装方式、特定平台的安装说明以及维护方法。

## 系统要求

- **[Node 22+](/install/node)**（若缺失，[安装脚本](#install-methods) 将自动安装）
- macOS、Linux 或 Windows
- `pnpm`（仅在从源码构建时需要）

<Note>
On Windows, we strongly recommend running OpenClaw under [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install).
</Note>

## 安装方式

<Tip>
The **installer script** is the recommended way to install OpenClaw. It handles Node detection, installation, and onboarding in one step.
</Tip>

<Warning>
For VPS/cloud hosts, avoid third-party "1-click" marketplace images when possible. Prefer a clean base OS image (for example Ubuntu LTS), then install OpenClaw yourself with the installer script.
</Warning>

<AccordionGroup>
  <Accordion title="Installer script" icon="rocket" defaultOpen>
    Downloads the CLI, installs it globally via npm, and launches the onboarding wizard.

    <Tabs>
      <Tab title="macOS / Linux / WSL2">
        __CODE_BLOCK_1__
      </Tab>
      <Tab title="Windows (PowerShell)">
        __CODE_BLOCK_2__
      </Tab>
    </Tabs>

    That's it — the script handles Node detection, installation, and onboarding.

    To skip onboarding and just install the binary:

    <Tabs>
      <Tab title="macOS / Linux / WSL2">
        __CODE_BLOCK_3__
      </Tab>
      <Tab title="Windows (PowerShell)">
        __CODE_BLOCK_4__
      </Tab>
    </Tabs>

    For all flags, env vars, and CI/automation options, see [Installer internals](/install/installer).

  </Accordion>

  <Accordion title="npm / pnpm" icon="package">
    If you already have Node 22+ and prefer to manage the install yourself:

    <Tabs>
      <Tab title="npm">
        __CODE_BLOCK_5__

        <Accordion title="sharp build errors?">
          If you have libvips installed globally (common on macOS via Homebrew) and __CODE_BLOCK_6__ fails, force prebuilt binaries:

          __CODE_BLOCK_7__

          If you see __CODE_BLOCK_8__, either install build tooling (macOS: Xcode CLT + __CODE_BLOCK_9__) or use the env var above.
        </Accordion>
      </Tab>
      <Tab title="pnpm">
        __CODE_BLOCK_10__

        <Note>
        pnpm requires explicit approval for packages with build scripts. After the first install shows the "Ignored build scripts" warning, run __CODE_BLOCK_11__ and select the listed packages.
        </Note>
      </Tab>
    </Tabs>

  </Accordion>

  <Accordion title="From source" icon="github">
    For contributors or anyone who wants to run from a local checkout.

    <Steps>
      <Step title="Clone and build">
        Clone the [OpenClaw repo](https://github.com/openclaw/openclaw) and build:

        __CODE_BLOCK_12__
      </Step>
      <Step title="Link the CLI">
        Make the __CODE_BLOCK_13__ command available globally:

        __CODE_BLOCK_14__

        Alternatively, skip the link and run commands via __CODE_BLOCK_15__ from inside the repo.
      </Step>
      <Step title="Run onboarding">
        __CODE_BLOCK_16__
      </Step>
    </Steps>

    For deeper development workflows, see [Setup](/start/setup).

  </Accordion>
</AccordionGroup>

## 其他安装方式

<CardGroup cols={2}>
  <Card title="Docker" href="/install/docker" icon="container">
    容器化或无界面部署。
  </Card>
  <Card title="Podman" href="/install/podman" icon="container">
    无 root 权限的容器：只需运行 `setup-podman.sh` 一次，然后运行启动脚本。
  </Card>
  <Card title="Nix" href="/install/nix" icon="snowflake">
    通过 Nix 进行声明式安装。
  </Card>
  <Card title="Ansible" href="/install/ansible" icon="server">
    自动化集群配置。
  </Card>
  <Card title="Bun" href="/install/bun" icon="zap">
    仅通过 Bun 运行时使用 CLI。
  </Card>
</CardGroup>

## 安装后操作

验证一切是否正常运行：

```bash
openclaw doctor         # check for config issues
openclaw status         # gateway status
openclaw dashboard      # open the browser UI
```

如需自定义运行时路径，请使用：

- `OPENCLAW_HOME` 指定基于用户主目录的内部路径  
- `OPENCLAW_STATE_DIR` 指定可变状态存储位置
- `OPENCLAW_CONFIG_PATH` 指定配置文件位置

详见 [环境变量](/help/environment)，了解优先级及完整说明。

## 故障排查：未找到 `openclaw`

<Accordion title="PATH 诊断与修复">
  快速诊断：

```bash
node -v
npm -v
npm prefix -g
echo "$PATH"
```

如果您的 `$PATH` 中**不包含** `$(npm prefix -g)/bin`（macOS/Linux）或 `$(npm prefix -g)`（Windows），则您的 Shell 将无法定位全局 npm 二进制文件（包括 `openclaw`）。

修复方法 —— 将其添加至 Shell 启动文件（`~/.zshrc` 或 `~/.bashrc`）中：

```bash
export PATH="$(npm prefix -g)/bin:$PATH"
```

在 Windows 上，请将 `npm prefix -g` 的输出添加到您的 PATH 中。

然后打开一个新的终端（或在 zsh 中执行 `rehash` / 在 bash 中执行 `hash -r`）。
</Accordion>

## 更新 / 卸载

<CardGroup cols={3}>
  <Card title="更新" href="/install/updating" icon="refresh-cw">
    保持 OpenClaw 为最新版本。
  </Card>
  <Card title="迁移" href="/install/migrating" icon="arrow-right">
    迁移到新设备。
  </Card>
  <Card title="卸载" href="/install/uninstall" icon="trash-2">
    彻底移除 OpenClaw。
  </Card>
</CardGroup>