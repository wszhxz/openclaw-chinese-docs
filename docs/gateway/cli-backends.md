---
summary: "CLI backends: text-only fallback via local AI CLIs"
read_when:
  - You want a reliable fallback when API providers fail
  - You are running Claude Code CLI or other local AI CLIs and want to reuse them
  - You need a text-only, tool-free path that still supports sessions and images
title: "CLI Backends"
---
# CLI 后端（备用运行时）

OpenClaw 可以在 API 提供者宕机、限速或暂时出现问题时，作为**纯文本备用方案**运行 **本地 AI CLI**。这是有意保守的做法：

- **工具被禁用**（无工具调用）。
- **文本输入 → 文本输出**（可靠）。
- **支持会话**（因此后续回合保持连贯）。
- **如果 CLI 接受图像路径，则可以传递图像**。

这设计为一种**安全网**而不是主要路径。当你希望“始终有效”的文本响应而不依赖外部 API 时使用它。

## 初学者快速入门

你可以**无需任何配置**使用 Claude Code CLI（OpenClaw 内置了默认配置）：

```bash
openclaw agent --message "hi" --model claude-cli/opus-4.5
```

Codex CLI 也可以开箱即用：

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.2-codex
```

如果你的网关在 launchd/systemd 下运行且 PATH 最小化，只需添加命令路径：

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

就这样。除了 CLI 本身外，不需要密钥或额外的身份验证配置。

## 作为备用使用

将 CLI 后端添加到你的备用列表中，使其仅在主模型失败时运行：

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

- 如果你使用 `agents.defaults.models`（白名单），必须包含 `claude-cli/...`。
- 如果主提供者失败（身份验证、速率限制、超时），OpenClaw 将尝试下一个 CLI 后端。

## 配置概述

所有 CLI 后端位于：

```
agents.defaults.cliBackends
```

每个条目都由一个**提供者 ID**（例如 `claude-cli`，`my-cli`）键控。
提供者 ID 成为你模型引用的左侧部分：

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

1. **根据提供者前缀选择后端** (`claude-cli/...`)。
2. **使用相同的 OpenClaw 提示 + 工作区上下文构建系统提示**。
3. **执行 CLI**（如果支持）时带会话 ID 以保持历史记录一致。
4. **解析输出**（JSON 或纯文本）并返回最终文本。
5. **按后端持久化会话 ID**，以便后续重用相同的 CLI 会话。

## 会话

- 如果 CLI 支持会话，请设置 `sessionArg`（例如 `--session-id`）或
  `sessionArgs`（占位符 `{sessionId}`），当需要将 ID 插入多个标志时。
- 如果 CLI 使用具有不同标志的**恢复子命令**，请设置
  `resumeArgs`（恢复时替换 `args`）并可选设置 `resumeOutput`
  （用于非 JSON 恢复）。
- `sessionMode`:
  - `always`: 始终发送会话 ID（如果没有存储则为新 UUID）。
  - `existing`: 仅在之前存储过会话 ID 时发送。
  - `none`: 从不发送会话 ID。

## 图像（透传）

如果你的 CLI 接受图像路径，请设置 `imageArg`：

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClaw 将 base64 图像写入临时文件。如果设置了 `imageArg`，这些路径将作为 CLI 参数传递。如果缺少 `imageArg`，OpenClaw 将文件路径附加到提示中（路径注入），这对于自动从纯路径加载本地文件的 CLI（Claude Code CLI 行为）已经足够。

## 输入/输出

- `output: "json"`（默认）尝试解析 JSON 并提取文本 + 会话 ID。
- `output: "jsonl"` 解析 JSONL 流（Codex CLI `--json`）并提取最后一个代理消息加上 `thread_id`（如果存在）。
- `output: "text"` 将 stdout 视为最终响应。

输入模式：

- `input: "arg"`（默认）将提示作为最后一个 CLI 参数传递。
- `input: "stdin"` 通过 stdin 发送提示。
- 如果提示很长且设置了 `maxPromptArgChars`，则使用 stdin。

## 默认值（内置）

OpenClaw 内置了 `claude-cli` 的默认值：

- `command: "claude"`
- `args: ["-p", "--output-format", "json", "--dangerously-skip-permissions"]`
- `resumeArgs: ["-p", "--output-format", "json", "--dangerously-skip-permissions", "--resume", "{sessionId}"]`
- `modelArg: "--model"`
- `systemPromptArg: "--append-system-prompt"`
- `sessionArg: "--session-id"`
- `systemPromptWhen: "first"`
- `sessionMode: "always"`

OpenClaw 还内置了 `codex-cli` 的默认值：

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","--color","never","--sandbox","read-only","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

仅在需要时覆盖（常见：绝对 `command` 路径）。

## 限制

- **无 OpenClaw 工具**（CLI 后端永远不会接收工具调用）。某些 CLI 可能仍然运行自己的代理工具。
- **无流式传输**（CLI 输出会被收集然后返回）。
- **结构化输出** 依赖于 CLI 的 JSON 格式。
- **Codex CLI 会话** 通过文本输出恢复（无 JSONL），这比初始 `--json` 运行的结构更少。OpenClaw 会话仍正常工作。

## 故障排除

- **未找到 CLI**：将 `command` 设置为完整路径。
- **错误的模型名称**：使用 `modelAliases` 将 `provider/model` → CLI 模型映射。
- **无会话连续性**：确保 `sessionArg` 已设置且 `sessionMode` 不是
  `none`（Codex CLI 目前无法通过 JSON 输出恢复）。
- **忽略图像**：设置 `imageArg`（并验证 CLI 支持文件路径）。