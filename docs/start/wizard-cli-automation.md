---
summary: "Scripted onboarding and agent setup for the OpenClaw CLI"
read_when:
  - You are automating onboarding in scripts or CI
  - You need non-interactive examples for specific providers
title: "CLI Automation"
sidebarTitle: "CLI automation"
---
# CLI 自动化

使用 `--non-interactive` 来自动化 `openclaw onboard`。

<Note>
__CODE_BLOCK_2__ does not imply non-interactive mode. Use __CODE_BLOCK_3__ (and __CODE_BLOCK_4__) for scripts.
</Note>

## 基线非交互式示例

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

添加 `--json` 以获得机器可读的摘要。

## 提供商特定示例

<AccordionGroup>
  <Accordion title="Gemini example">
    __CODE_BLOCK_7__
  </Accordion>
  <Accordion title="Z.AI example">
    __CODE_BLOCK_8__
  </Accordion>
  <Accordion title="Vercel AI Gateway example">
    __CODE_BLOCK_9__
  </Accordion>
  <Accordion title="Cloudflare AI Gateway example">
    __CODE_BLOCK_10__
  </Accordion>
  <Accordion title="Moonshot example">
    __CODE_BLOCK_11__
  </Accordion>
  <Accordion title="Synthetic example">
    __CODE_BLOCK_12__
  </Accordion>
  <Accordion title="OpenCode Zen example">
    __CODE_BLOCK_13__
  </Accordion>
  <Accordion title="Custom provider example">
    __CODE_BLOCK_14__

    __CODE_BLOCK_15__ is optional. If omitted, onboarding checks __CODE_BLOCK_16__.

  </Accordion>
</AccordionGroup>

## 添加另一个代理

使用 `openclaw agents add <name>` 创建一个具有自己工作区、会话和身份验证配置文件的单独代理。不带 `--workspace` 运行将启动向导。

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.2 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

它设置的内容：

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

注意事项：

- 默认工作区遵循 `~/.openclaw/workspace-<agentId>`。
- 添加 `bindings` 以路由传入消息（向导可以完成此操作）。
- 非交互式标志：`--model`，`--agent-dir`，`--bind`，`--non-interactive`。

## 相关文档

- 入门中心：[入门向导 (CLI)](/start/wizard)
- 完整参考：[CLI 入门参考](/start/wizard-cli-reference)
- 命令参考：[`openclaw onboard`](/cli/onboard)