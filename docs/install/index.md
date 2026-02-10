---
summary: "Install OpenClaw — installer script, npm/pnpm, from source, Docker, and more"
read_when:
  - You need an install method other than the Getting Started quickstart
  - You want to deploy to a cloud platform
  - You need to update, migrate, or uninstall
title: "Install"
---
# 安装

已经按照 [Getting Started](/start/getting-started) 操作？您已经准备好了 —— 本页提供替代安装方法、特定平台的说明和维护信息。

## 系统要求

- **[Node 22+](/install/node)** (如果缺失，[安装脚本](#install-methods) 将会安装它)
- macOS, Linux 或 Windows
- `pnpm` 仅在从源代码构建时需要

<Note>
On Windows, we strongly recommend running OpenClaw under [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install).
</Note>

## 安装方法

<Tip>
The **installer script** is the recommended way to install OpenClaw. It handles Node detection, installation, and onboarding in one step.
</Tip>

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

## 其他安装方法

<CardGroup cols={2}>
  <Card title="Docker" href="/install/docker" icon="container">
    容器化或无头部署。
  </Card>
  <Card title="Nix" href="/install/nix" icon="snowflake">
    通过 Nix 进行声明式安装。
  </Card>
  <Card title="Ansible" href="/install/ansible" icon="server">
    自动化集群预配。
  </Card>
  <Card title="Bun" href="/install/bun" icon="zap">
    通过 Bun 运行时进行 CLI 仅使用。
  </Card>
</CardGroup>

## 安装后

验证一切正常：

```bash
openclaw doctor         # check for config issues
openclaw status         # gateway status
openclaw dashboard      # open the browser UI
```

如果您需要自定义运行时路径，请使用：

- `OPENCLAW_HOME` 用于基于主目录的内部路径
- `OPENCLAW_STATE_DIR` 用于可变状态位置
- `OPENCLAW_CONFIG_PATH` 用于配置文件位置

请参阅 [环境变量](/help/environment) 以了解优先级和详细信息。

## 故障排除：未找到 `openclaw`

<Accordion title="PATH 诊断和修复">
  快速诊断：

```bash
node -v
npm -v
npm prefix -g
echo "$PATH"
```

如果 `$(npm prefix -g)/bin` (macOS/Linux) 或 `$(npm prefix -g)` (Windows) 不在您的 `$PATH` 中，您的 shell 将无法找到全局 npm 二进制文件（包括 `openclaw`）。

修复 — 将其添加到您的 shell 启动文件 (`~/.zshrc` 或 `~/.bashrc`)：

```bash
export PATH="$(npm prefix -g)/bin:$PATH"
```

在 Windows 上，将 `npm prefix -g` 的输出添加到您的 PATH。

然后打开一个新的终端（或在 zsh 中使用 `rehash` / 在 bash 中使用 `hash -r`）。
</Accordion>

## 更新 / 卸载

<CardGroup cols={3}>
  <Card title="更新" href="/install/updating" icon="refresh-cw">
    保持 OpenClaw 最新。
  </Card>
  <Card title="迁移" href="/install/migrating" icon="arrow-right">
    迁移到新机器。
  </Card>
  <Card title="卸载" href="/install/uninstall" icon="trash-2">
    完全移除 OpenClaw。
  </Card>
</CardGroup>