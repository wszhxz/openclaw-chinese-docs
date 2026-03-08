---
summary: "CLI backends: text-only fallback via local AI CLIs"
read_when:
  - You want a reliable fallback when API providers fail
  - You are running Claude Code CLI or other local AI CLIs and want to reuse them
  - You need a text-only, tool-free path that still supports sessions and images
title: "CLI Backends"
---
# CLI 后端（回退运行时）

当 API 提供商宕机、达到速率限制或暂时行为异常时，OpenClaw 可以运行 **本地 AI CLI** 作为 **纯文本回退**。这是故意保守的：

- **工具已禁用**（无工具调用）。
- **文本输入 → 文本输出**（可靠）。
- **支持会话**（以便后续回合保持一致性）。
- 如果 CLI 接受图像路径，则 **可以透传图像**。

这设计为 **安全网** 而非主要路径。当您希望在不依赖外部 API 的情况下获得“始终可用”的文本响应时使用它。

## 适合初学者的快速开始

您可以使用 Claude Code CLI **无需任何配置**（OpenClaw 内置了默认值）：

```bash
openclaw agent --message "hi" --model claude-cli/opus-4.6
```

Codex CLI 也可以开箱即用：

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

如果您的网关在 launchd/systemd 下运行且 PATH 最小化，只需添加命令路径：

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

就是这样。不需要密钥，除了 CLI 本身外也不需要额外的身份验证配置。

## 将其用作回退

将 CLI 后端添加到您的回退列表中，这样它仅在主要模型失败时运行：

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

注意：

- 如果您使用 `agents.defaults.models`（白名单），您必须包含 `claude-cli/...`。
- 如果主要提供商失败（认证、速率限制、超时），OpenClaw 将尝试 CLI 后端。

## 配置概览

所有 CLI 后端位于：

```
agents.defaults.cliBackends
```

每个条目都由 **provider id** 键控（例如 `claude-cli`, `my-cli`）。
provider id 将成为您模型引用的左侧部分：

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

1. **选择后端** 基于 provider 前缀 (`claude-cli/...`)。
2. **构建系统提示词**，使用相同的 OpenClaw 提示词 + 工作区上下文。
3. **执行 CLI**，附带 session id（如果支持），以保持历史记录一致。
4. **解析输出**（JSON 或纯文本）并返回最终文本。
5. **持久化 session ids** 每个后端，以便后续操作重用相同的 CLI 会话。

## 会话

- 如果 CLI 支持会话，设置 `sessionArg`（例如 `--session-id`）或 `sessionArgs`（占位符 `{sessionId}`），当 ID 需要插入到多个标志中时。
- 如果 CLI 使用带有不同标志的 **恢复子命令**，设置 `resumeArgs`（恢复时替换 `args`）以及可选的 `resumeOutput`（用于非 JSON 恢复）。
- `sessionMode`:
  - `always`: 始终发送 session id（如果没有存储则为新 UUID）。
  - `existing`: 仅当之前存储过时才发送 session id。
  - `none`: 从不发送 session id。

## 图像（透传）

如果您的 CLI 接受图像路径，设置 `imageArg`：

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClaw 会将 base64 图像写入 temp files。如果设置了 `imageArg`，这些路径将作为 CLI args 传递。如果 `imageArg` 缺失，OpenClaw 将文件路径附加到提示词中（路径注入），这对于从普通路径自动加载本地文件的 CLI 来说已经足够（Claude Code CLI 行为）。

## 输入 / 输出

- `output: "json"`（默认）尝试解析 JSON 并提取文本 + session id。
- `output: "jsonl"` 解析 JSONL 流（Codex CLI `--json`）并提取最后一个代理消息加上 `thread_id`（如果存在）。
- `output: "text"` 将 stdout 视为最终响应。

输入模式：

- `input: "arg"`（默认）将提示词作为最后一个 CLI arg 传递。
- `input: "stdin"` 通过 stdin 发送提示词。
- 如果提示词非常长且设置了 `maxPromptArgChars`，则使用 stdin。

## 默认值（内置）

OpenClaw 为 `claude-cli` 提供了默认值：

- `command: "claude"`
- `args: ["-p", "--output-format", "json", "--permission-mode", "bypassPermissions"]`
- `resumeArgs: ["-p", "--output-format", "json", "--permission-mode", "bypassPermissions", "--resume", "{sessionId}"]`
- `modelArg: "--model"`
- `systemPromptArg: "--append-system-prompt"`
- `sessionArg: "--session-id"`
- `systemPromptWhen: "first"`
- `sessionMode: "always"`

OpenClaw 也为 `codex-cli` 提供了默认值：

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

- **没有 OpenClaw 工具**（CLI 后端永远不会接收工具调用）。某些 CLI 可能仍会运行其自己的 agent tooling。
- **无流式传输**（收集 CLI 输出然后返回）。
- **结构化输出** 取决于 CLI 的 JSON 格式。
- **Codex CLI 会话** 通过文本输出恢复（无 JSONL），这比初始 `--json` 运行结构化程度低。OpenClaw 会话仍然正常工作。

## 故障排除

- **未找到 CLI**：将 `command` 设置为完整路径。
- **错误的模型名称**：使用 `modelAliases` 将 `provider/model` 映射到 CLI 模型。
- **无会话连续性**：确保设置 `sessionArg` 且 `sessionMode` 不是 `none`（Codex CLI 目前无法使用 JSON 输出恢复）。
- **图像被忽略**：设置 `imageArg`（并验证 CLI 支持文件路径）。