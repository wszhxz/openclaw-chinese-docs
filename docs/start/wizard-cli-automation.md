---
summary: "Scripted onboarding and agent setup for the OpenClaw CLI"
read_when:
  - You are automating onboarding in scripts or CI
  - You need non-interactive examples for specific providers
title: "CLI Automation"
sidebarTitle: "CLI automation"
---
# CLI 自动化

使用 `--non-interactive` 自动化执行 `openclaw onboard`。

<Note>
__CODE_BLOCK_2__ does not imply non-interactive mode. Use __CODE_BLOCK_3__ (and __CODE_BLOCK_4__) for scripts.
</Note>

## 基线非交互式示例

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

添加 `--json` 以生成机器可读的摘要。

使用 `--secret-input-mode ref` 将环境变量支持的引用存储在认证配置文件中，而非明文值。  
在入门向导流程中，可在环境引用与已配置的提供程序引用（`file` 或 `exec`）之间进行交互式选择。

在非交互式 `ref` 模式下，提供程序环境变量必须在进程环境中设置。  
若未设置匹配的环境变量而直接传入内联密钥标志，则会立即失败。

示例：

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice openai-api-key \
  --secret-input-mode ref \
  --accept-risk
```

## 针对特定提供程序的示例

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

## 添加另一个代理

使用 `openclaw agents add <name>` 创建一个独立的代理，该代理拥有自己的工作区、会话和认证配置文件。  
不带 `--workspace` 运行时将启动向导。

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.2 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

它将设置以下内容：

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

注意事项：

- 默认工作区遵循 `~/.openclaw/workspace-<agentId>`。
- 添加 `bindings` 以路由入站消息（向导可自动完成此操作）。
- 非交互式标志：`--model`、`--agent-dir`、`--bind`、`--non-interactive`。

## 相关文档

- 入门中心：[入门向导（CLI）](/start/wizard)  
- 完整参考：[CLI 入门参考](/start/wizard-cli-reference)  
- 命令参考：[`openclaw onboard`](/cli/onboard)