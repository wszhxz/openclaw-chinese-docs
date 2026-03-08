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

## 基础非交互式示例

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

添加 `--json` 以获取机器可读的摘要。

使用 `--secret-input-mode ref` 在 auth profiles 中存储基于 env 的 refs，而不是明文值。
在 onboarding wizard 流程中，可以在 env refs 和配置好的 provider refs（`file` 或 `exec`）之间进行交互式选择。

在非交互式 `ref` 模式下，provider 环境变量必须在进程环境中设置。
传递内联 key flags 而没有匹配的环境变量现在会快速失败。

示例：

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice openai-api-key \
  --secret-input-mode ref \
  --accept-risk
```

## Provider 特定示例

<AccordionGroup>
  <Accordion title="Gemini example">
    __CODE_BLOCK_12__
  </Accordion>
  <Accordion title="Z.AI example">
    __CODE_BLOCK_13__
  </Accordion>
  <Accordion title="Vercel AI Gateway example">
    __CODE_BLOCK_14__
  </Accordion>
  <Accordion title="Cloudflare AI Gateway example">
    __CODE_BLOCK_15__
  </Accordion>
  <Accordion title="Moonshot example">
    __CODE_BLOCK_16__
  </Accordion>
  <Accordion title="Mistral example">
    __CODE_BLOCK_17__
  </Accordion>
  <Accordion title="Synthetic example">
    __CODE_BLOCK_18__
  </Accordion>
  <Accordion title="OpenCode Zen example">
    __CODE_BLOCK_19__
  </Accordion>
  <Accordion title="Custom provider example">
    __CODE_BLOCK_20__

    __CODE_BLOCK_21__ is optional. If omitted, onboarding checks __CODE_BLOCK_22__.

    Ref-mode variant:

    __CODE_BLOCK_23__

    In this mode, onboarding stores __CODE_BLOCK_24__ as __CODE_BLOCK_25__.

  </Accordion>
</AccordionGroup>

## 添加另一个 agent

使用 `openclaw agents add <name>` 创建一个独立的 agent，拥有其自己的 workspace、sessions 和 auth profiles。在不使用 `--workspace` 的情况下运行会启动 wizard。

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

注意：

- 默认 workspaces 遵循 `~/.openclaw/workspace-<agentId>`。
- 添加 `bindings` 以路由 inbound messages（wizard 可以完成此操作）。
- 非交互式 flags：`--model`、`--agent-dir`、`--bind`、`--non-interactive`。

## 相关文档

- 入门中心：[Onboarding Wizard (CLI)](/start/wizard)
- 完整参考：[CLI Onboarding Reference](/start/wizard-cli-reference)
- 命令参考：[`openclaw onboard`](/cli/onboard)