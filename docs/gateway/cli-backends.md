---
summary: "CLI backends: text-only fallback via local AI CLIs"
read_when:
  - You want a reliable fallback when API providers fail
  - You are running Claude Code CLI or other local AI CLIs and want to reuse them
  - You need a text-only, tool-free path that still supports sessions and images
title: "CLI Backends"
---
# CLI后端（备用运行时）

当API提供方不可用、速率限制或暂时行为异常时，OpenClaw可以将**本地AI CLI**作为**纯文本备用方案**运行。这设计上是保守的：

- **工具被禁用**（无工具调用）。
- **文本入→文本出**（可靠）。
- **支持会话**（确保后续交互连贯）。
- **若CLI接受图像路径**，可传递图像。

该方案旨在作为**安全网**而非主要路径。当你希望“始终可用”的文本响应而不依赖外部API时使用。

## 新手友好快速入门

你可以**无需任何配置**使用Claude Code CLI（OpenClaw内置默认配置）：

```bash
openclaw agent --message "hi" --model claude-cli/opus-4.5
```

Codex CLI 也可以开箱即用：

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.2-codex
```

如果网关在launchd/systemd下运行且PATH极简，只需添加命令路径：

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "claude-cli": {
          command: "/opt/homebrew/bin/claude",
        },
      },
    },
  },
}
```

搞定。无需密钥，无需CLI之外的额外认证配置。

## 作为备用方案使用

将CLI后端添加到你的备用列表中，使其仅在主模型失败时运行：

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-5",
        fallbacks: ["claude-cli/opus-4.5"],
      },
      models: {
        "anthropic/claude-opus-4-5": { alias: "Opus" },
        "claude-cli/opus-4.5": {},
      },
    },
  },
}
```

注意事项：

- 如果你使用`agents.defaults.models`（白名单），必须包含`claude-cli/...`。
- 如果主提供方失败（认证、速率限制、超时），OpenClaw将尝试CLI后端。

## 配置概览

所有CLI后端位于：

```
agents.defaults.cliBackends
```

每个条目以**提供方ID**（例如`claude-cli`、`my-cli`）为键。
提供方ID成为你的模型引用的左侧部分：

```
<提供方>/<模型>
```

### 示例配置

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "claude-cli": {
          command: "/opt/homebrew/bin/claude",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          input: "arg",
          modelArg: "--model",
          modelAliases: {
            "claude-opus-4-5": "opus",
            "claude-sonnet-4-5": "sonnet",
          },
          sessionArg: "--session",
          sessionMode: "existing",
          sessionIdFields: ["session_id", "conversation_id"],
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
          serialize: true,
        },
      },
    },
  },
}
```

## 运行机制

1. **根据提供方前缀（如`claude-cli/...`）选择后端**。
2. **使用相同的OpenClaw提示+工作区上下文构建系统提示**。
3. **若支持，使用会话ID执行CLI**，以保持历史一致性。
4. **解析输出（JSON或纯文本）**，返回最终文本。
5. **按后端持久化会话ID**，以便后续交互复用同一CLI会话。

## 会话

- 若CLI支持会话，设置`sessionArg`（如`--session-id`）或`sessionArgs`（占位符`{sessionId}`）当需要将ID插入多个标志中。
- 若CLI使用**带有不同标志的恢复子命令**，设置`resumeArgs`（恢复时替换`args`）和可选的`resumeOutput`（非JSON恢复）。
- `sessionMode`：
  - `always`：始终发送会话ID（若无存储则生成新UUID）。
  - `existing`：仅在之前存储过会话ID时发送。
  - `none`：从不发送会话ID。

## 图像（透传）

若CLI接受图像路径，设置`imageArg`：

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClaw将把base64图像写入临时文件。若`imageArg`被设置，这些路径将作为CLI参数传递。若`imageArg`缺失，OpenClaw将把文件路径附加到提示（路径注入），这对能从纯路径自动加载本地文件的CLI（如Claude Code CLI）已足够。

## 输入/输出

- `output: "json"`（默认）尝试解析JSON并提取文本+会话ID。
- `output: "jsonl"`解析JSONL流（Codex CLI `--json`）并提取最后的代理消息及`thread_id`（若存在）。
- `output: "text"`将标准输出视为最终响应。

输入模式：

- `input: "arg"`（默认）将提示作为CLI的最后一个参数。
- `input: "stdin"`通过标准输入发送提示。
- 若提示非常长且设置了`maxPromptArgChars`，则使用标准输入。

## 默认值（内置）

OpenClaw为`claude-cli`提供默认配置：

- `command: "claude"`
- `args: ["-p", "--output-format", "json", "--dangerously-skip-permissions"]`
- `resumeArgs: ["-p", "--output-format", "json", "--dangerously-skip-permissions", "--resume", "{sessionId}"]`
- `modelArg: "--model"`
- `systemPromptArg: "--append-system-prompt"`
- `sessionArg: "--session-id"`
- `systemPromptWhen: "first"`
- `sessionMode: "always"`

OpenClaw也为`codex-cli`提供默认配置：

- `command: "codex"`
- `args: ["exec","