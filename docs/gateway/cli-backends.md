---
summary: "CLI backends: text-only fallback via local AI CLIs"
read_when:
  - You want a reliable fallback when API providers fail
  - You are running Claude Code CLI or other local AI CLIs and want to reuse them
  - You need a text-only, tool-free path that still supports sessions and images
title: "CLI Backends"
---
# CLI 后端（备用运行时）

当 API 服务不可用、遭遇速率限制或临时异常时，OpenClaw 可以将 **本地 AI CLI** 作为 **纯文本备用方案** 运行。该设计刻意保持保守：

- **禁用工具功能**（不执行任何工具调用）。
- **纯文本输入 → 纯文本输出**（可靠性高）。
- **支持会话**（确保后续对话轮次保持连贯性）。
- **若 CLI 支持图像路径，则可透传图像**。

此机制被设计为一种 **安全网**，而非主要运行路径。当你希望获得“始终可用”的纯文本响应、且不依赖外部 API 时，可启用它。

## 新手友好型快速入门

你可以直接使用 Claude Code CLI **无需任何配置**（OpenClaw 内置了默认配置）：

```bash
openclaw agent --message "hi" --model claude-cli/opus-4.6
```

Codex CLI 同样开箱即用：

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

如果你的网关在 launchd/systemd 下运行，且 PATH 环境变量极简，请仅添加命令路径：

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

仅此而已。除 CLI 自身外，无需密钥，也无需额外的身份验证配置。

## 将其用作备用方案

将 CLI 后端添加至你的备用列表中，使其仅在主模型失败时启用：

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["claude-cli/opus-4.6", "claude-cli/opus-4.5"],
      },
      models: {
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "claude-cli/opus-4.6": {},
        "claude-cli/opus-4.5": {},
      },
    },
  },
}
```

注意事项：

- 若你使用 `agents.defaults.models`（白名单），则必须包含 `claude-cli/...`。
- 若主服务提供商失败（身份验证错误、速率限制、超时等），OpenClaw 将尝试调用 CLI 后端。

## 配置概览

所有 CLI 后端均位于以下路径下：

```
agents.defaults.cliBackends
```

每个条目以 **提供商 ID**（例如 `claude-cli`、`my-cli`）为键。该提供商 ID 将成为你模型引用的左侧部分：

```
<provider>/<model>
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
            "claude-opus-4-6": "opus",
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

## 工作原理

1. **根据提供商前缀**（`claude-cli/...`）选择后端。
2. **构建系统提示词**：复用 OpenClaw 的标准提示词 + 工作区上下文。
3. **执行 CLI**：传入会话 ID（如 CLI 支持），以确保历史记录一致。
4. **解析输出**（JSON 或纯文本），并返回最终文本。
5. **按后端持久化会话 ID**，以便后续对话复用同一 CLI 会话。

## 会话

- 若 CLI 支持会话，请设置 `sessionArg`（例如 `--session-id`），或设置 `sessionArgs`（占位符为 `{sessionId}`），用于在多个参数中插入会话 ID。
- 若 CLI 使用带不同参数的 **恢复子命令（resume subcommand）**，请设置 `resumeArgs`（恢复时替换 `args`），并可选设置 `resumeOutput`（用于非 JSON 格式的恢复）。
- `sessionMode`：
  - `always`：始终发送会话 ID（若无已存储 ID，则生成新 UUID）。
  - `existing`：仅在已有已存储 ID 时才发送会话 ID。
  - `none`：从不发送会话 ID。

## 图像（透传）

若你的 CLI 支持图像路径，请设置 `imageArg`：

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClaw 会将 base64 图像写入临时文件。若设置了 `imageArg`，这些路径将以 CLI 参数形式传递；若未设置 `imageArg`，OpenClaw 将把文件路径追加至提示词中（路径注入），这对能自动从纯路径加载本地文件的 CLI（如 Claude Code CLI 行为）已足够。

## 输入 / 输出

- `output: "json"`（默认）：尝试解析 JSON，并提取文本内容与会话 ID。
- `output: "jsonl"`：解析 JSONL 流（Codex CLI 的 `--json`），并提取最后一条智能体消息，以及当存在时的 `thread_id`。
- `output: "text"`：将 stdout 视为最终响应。

输入模式：

- `input: "arg"`（默认）：将提示词作为最后一个 CLI 参数传入。
- `input: "stdin"`：通过 stdin 发送提示词。
- 若提示词过长且设置了 `maxPromptArgChars`，则使用 stdin。

## 默认配置（内置）

OpenClaw 为 `claude-cli` 提供了默认配置：

- `command: "claude"`
- `args: ["-p", "--output-format", "json", "--permission-mode", "bypassPermissions"]`
- `resumeArgs: ["-p", "--output-format", "json", "--permission-mode", "bypassPermissions", "--resume", "{sessionId}"]`
- `modelArg: "--model"`
- `systemPromptArg: "--append-system-prompt"`
- `sessionArg: "--session-id"`
- `systemPromptWhen: "first"`
- `sessionMode: "always"`

OpenClaw 同样为 `codex-cli` 提供了默认配置：

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","--color","never","--sandbox","read-only","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

仅在必要时覆盖（常见情形：指定绝对 `command` 路径）。

## 局限性

- **不支持 OpenClaw 工具**（CLI 后端永远不会接收到工具调用）。某些 CLI 仍可能自行运行其内部智能体工具链。
- **不支持流式响应**（CLI 输出将被完整收集后再返回）。
- **结构化输出** 依赖于 CLI 所采用的 JSON 格式。
- **Codex CLI 的会话恢复** 依赖文本输出（非 JSONL），其结构化程度低于初始的 `--json` 运行。但 OpenClaw 的会话机制仍可正常工作。

## 故障排查

- **找不到 CLI**：将 `command` 设置为完整路径。
- **模型名称错误**：使用 `modelAliases` 将 `provider/model` 映射至 CLI 模型。
- **会话无法延续**：确保已设置 `sessionArg`，且 `sessionMode` 不为 `none`（Codex CLI 当前尚不支持以 JSON 输出方式恢复会话）。
- **图像被忽略**：设置 `imageArg`（并确认 CLI 支持文件路径）。