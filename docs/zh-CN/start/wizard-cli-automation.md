---
read_when:
  - 你正在脚本或 CI 中自动化新手引导
  - 你需要特定提供商的非交互式示例
sidebarTitle: CLI automation
summary: 用于 OpenClaw CLI 的脚本化新手引导和智能体设置
title: CLI 自动化
x-i18n:
  generated_at: "2026-03-16T06:28:19Z"
  model: gpt-5.4
  provider: openai
  source_hash: 2a82c491616e8c1c2aa6ef5e19bde80b8cccd1e5f7684838b9ce704c33e41b0e
  source_path: start/wizard-cli-automation.md
  workflow: 15
---
# CLI 自动化

使用 `--non-interactive` 自动化 `openclaw onboard`。

<Note>
__CODE_BLOCK_2__ 并不意味着非交互模式。对于脚本，请使用 __CODE_BLOCK_3__（以及 __CODE_BLOCK_4__）。
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

添加 `--json` 可获得机器可读的摘要。

使用 `--secret-input-mode ref` 可在认证配置文件中存储基于环境变量的引用，而不是明文值。
在设置向导流程中，支持在环境变量引用与已配置的提供商引用（`file` 或 `exec`）之间进行交互式选择。

在非交互式 `ref` 模式下，必须在进程环境中设置提供商环境变量。
如果传入了内联密钥标志，但缺少匹配的环境变量，现在会快速失败。

示例：

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice openai-api-key \
  --secret-input-mode ref \
  --accept-risk
```

## 提供商专用示例

<AccordionGroup>
  <Accordion title="Gemini 示例">
    __CODE_BLOCK_12__
  </Accordion>
  <Accordion title="Z.AI 示例">
    __CODE_BLOCK_13__
  </Accordion>
  <Accordion title="Vercel AI Gateway 示例">
    __CODE_BLOCK_14__
  </Accordion>
  <Accordion title="Cloudflare AI Gateway 示例">
    __CODE_BLOCK_15__
  </Accordion>
  <Accordion title="Moonshot 示例">
    __CODE_BLOCK_16__
  </Accordion>
  <Accordion title="Mistral 示例">
    __CODE_BLOCK_17__
  </Accordion>
  <Accordion title="Synthetic 示例">
    __CODE_BLOCK_18__
  </Accordion>
  <Accordion title="OpenCode 示例">
    __CODE_BLOCK_19__
    对 Go 目录，可改用 __CODE_BLOCK_20__。
  </Accordion>
  <Accordion title="Ollama 示例">
    __CODE_BLOCK_21__
  </Accordion>
  <Accordion title="自定义提供商示例">
    __CODE_BLOCK_22__

    __CODE_BLOCK_23__ 是可选的。如果省略，新手引导会检查 __CODE_BLOCK_24__。

    __CODE_BLOCK_25__ 模式变体：

    __CODE_BLOCK_26__

    在此模式下，新手引导会将 __CODE_BLOCK_27__ 存储为 __CODE_BLOCK_28__。

  </Accordion>
</AccordionGroup>

## 添加另一个智能体

使用 `openclaw agents add <name>` 创建一个单独的智能体，它拥有自己的工作区、
会话和认证配置文件。不带 `--workspace` 运行会启动向导。

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

它会设置：

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

说明：

- 默认工作区遵循 `~/.openclaw/workspace-<agentId>`。
- 添加 `bindings` 以路由入站消息（向导可以完成这项操作）。
- 非交互式标志：`--model`、`--agent-dir`、`--bind`、`--non-interactive`。

## 相关文档

- 新手引导中心：[设置向导（CLI）](/start/wizard)
- 完整参考：[CLI 设置参考](/start/wizard-cli-reference)
- 命令参考：[`openclaw onboard`](/cli/onboard)