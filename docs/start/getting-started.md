---
summary: "Get OpenClaw installed and run your first chat in minutes."
read_when:
  - First time setup from zero
  - You want the fastest path to a working chat
title: "Getting Started"
---
# 入门指南

目标：从零开始，通过最少的设置实现第一个工作的聊天。

<Info>
Fastest chat: open the Control UI (no channel setup needed). Run __CODE_BLOCK_0__
and chat in the browser, or open __CODE_BLOCK_1__ on the
<Tooltip headline="Gateway host" tip="The machine running the OpenClaw gateway service.">gateway host</Tooltip>.
Docs: [Dashboard](/web/dashboard) and [Control UI](/web/control-ui).
</Info>

## 前提条件

- Node 22 或更新版本

<Tip>
Check your Node version with __CODE_BLOCK_2__ if you are unsure.
</Tip>

## 快速设置 (CLI)

<Steps>
  <Step title="Install OpenClaw (recommended)">
    <Tabs>
      <Tab title="macOS/Linux">
        __CODE_BLOCK_3__
        <img
  src="/assets/install-script.svg"
  alt="Install Script Process"
  className="rounded-lg"
/>
      </Tab>
      <Tab title="Windows (PowerShell)">
        __CODE_BLOCK_4__
      </Tab>
    </Tabs>

    <Note>
    Other install methods and requirements: [Install](/install).
    </Note>

  </Step>
  <Step title="Run the onboarding wizard">
    __CODE_BLOCK_5__

    The wizard configures auth, gateway settings, and optional channels.
    See [Onboarding Wizard](/start/wizard) for details.

  </Step>
  <Step title="Check the Gateway">
    If you installed the service, it should already be running:

    __CODE_BLOCK_6__

  </Step>
  <Step title="Open the Control UI">
    __CODE_BLOCK_7__
  </Step>
</Steps>

<Check>
If the Control UI loads, your Gateway is ready for use.
</Check>

## 可选检查和额外功能

<AccordionGroup>
  <Accordion title="Run the Gateway in the foreground">
    Useful for quick tests or troubleshooting.

    __CODE_BLOCK_8__

  </Accordion>
  <Accordion title="Send a test message">
    Requires a configured channel.

    __CODE_BLOCK_9__

  </Accordion>
</AccordionGroup>

## 有用的环境变量

如果您以服务账户运行 OpenClaw 或希望自定义配置/状态位置：

- `OPENCLAW_HOME` 设置用于内部路径解析的主目录。
- `OPENCLAW_STATE_DIR` 覆盖状态目录。
- `OPENCLAW_CONFIG_PATH` 覆盖配置文件路径。

完整环境变量参考：[环境变量](/help/environment)。

## 深入了解

<Columns>
  <Card title="Onboarding Wizard (details)" href="/start/wizard">
    Full CLI wizard reference and advanced options.
  </Card>
  <Card title="macOS app onboarding" href="/start/onboarding">
    First run flow for the macOS app.
  </Card>
</Columns>

## 您将拥有

- 运行中的网关
- 配置好的认证
- 控制界面访问或连接的频道

## 下一步

- 直接消息安全性和批准：[配对](/channels/pairing)
- 连接更多频道：[频道](/channels)
- 高级工作流和从源代码设置：[设置](/start/setup)