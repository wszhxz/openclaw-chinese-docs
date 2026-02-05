---
title: Lobster
summary: "Typed workflow runtime for OpenClaw with resumable approval gates."
description: Typed workflow runtime for OpenClaw — composable pipelines with approval gates.
read_when:
  - You want deterministic multi-step workflows with explicit approvals
  - You need to resume a workflow without re-running earlier steps
---
# Lobster

Lobster 是一个工作流 shell，允许 OpenClaw 将多步骤工具序列作为单个确定性操作运行，并具有显式的审批检查点。

## Hook

您的助手可以构建管理自身的工具。请求一个工作流，30 分钟后您将获得一个 CLI 加上作为一次调用运行的管道。Lobster 是缺失的部分：确定性管道、显式审批和可恢复状态。

## 为什么

今天，复杂的流程需要许多来回的工具调用。每次调用都会消耗代币，并且 LLM 必须协调每一步。Lobster 将这种协调移到了类型化运行时：

- **一次调用而不是多次**：OpenClaw 运行一个 Lobster 工具调用并获得一个结构化结果。
- **内置审批**：副作用（发送邮件、发布评论）会暂停工作流，直到显式批准。
- **可恢复**：暂停的工作流会返回一个代币；批准并恢复而无需重新运行所有内容。

## 为什么使用 DSL 而不是普通的程序？

Lobster 故意保持小巧。目标不是“一种新语言”，而是一个可预测的、AI 友好的管道规范，具有内置的审批和恢复代币。

- **内置审批/恢复**：一个普通的程序可以提示人类，但不能在没有自己发明该运行时的情况下使用持久代币进行_暂停和恢复_。
- **确定性 + 可审计性**：管道是数据，因此很容易记录、比较、重播和审查。
- **AI 的受限表面**：一个小语法+JSON 管道减少了“创造性”的代码路径，并使验证变得现实。
- **内置安全策略**：超时、输出限制、沙箱检查和白名单由运行时强制执行，而不是每个脚本。
- **仍然可编程**：每个步骤可以调用任何 CLI 或脚本。如果您想要 JS/TS，从代码生成 `.lobster` 文件。

## 它是如何工作的

OpenClaw 启动本地 `lobster` CLI 处于 **工具模式** 并解析 stdout 中的 JSON 包装。
如果管道暂停以等待审批，工具会返回一个 `resumeToken` 以便稍后继续。

## 模式：小型 CLI + JSON 管道 + 审批

构建小型命令以使用 JSON 通信，然后将它们链接到单个 Lobster 调用。（下面示例命令名称 — 替换为您自己的。）

```bash
inbox list --json
inbox categorize --json
inbox apply --json
```

```json
{
  "action": "run",
  "pipeline": "exec --json --shell 'inbox list --json' | exec --stdin json --shell 'inbox categorize --json' | exec --stdin json --shell 'inbox apply --json' | approve --preview-from-stdin --limit 5 --prompt 'Apply changes?'",
  "timeoutMs": 30000
}
```

如果管道请求审批，请使用代币恢复：

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

AI 触发工作流；Lobster 执行步骤。审批门将副作用保持显式和可审计。

示例：将输入项映射到工具调用：

```bash
gog.gmail.search --query 'newer_than:1d' \
  | openclaw.invoke --tool message --action send --each --item-key message --args-json '{"provider":"telegram","to":"..."}'
```

## 仅JSON的LLM步骤 (llm-task)

对于需要**结构化LLM步骤**的工作流，请启用可选的`llm-task`插件工具，并从Lobster调用它。这可以保持工作流的确定性，同时仍然允许您使用模型进行分类/总结/草拟。

启用工具：

```json
{
  "plugins": {
    "entries": {
      "llm-task": { "enabled": true }
    }
  },
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": { "allow": ["llm-task"] }
      }
    ]
  }
}
```

在管道中使用：

```lobster
openclaw.invoke --tool llm-task --action json --args-json '{
  "prompt": "Given the input email, return intent and draft.",
  "input": { "subject": "Hello", "body": "Can you help?" },
  "schema": {
    "type": "object",
    "properties": {
      "intent": { "type": "string" },
      "draft": { "type": "string" }
    },
    "required": ["intent", "draft"],
    "additionalProperties": false
  }
}'
```

详情和配置选项请参见[LLM Task](/tools/llm-task)。

## 工作流文件 (.lobster)

Lobster可以使用包含`name`，`args`，`steps`，`env`，`condition`和`approval`字段的YAML/JSON工作流文件。在OpenClaw工具调用中，将`pipeline`设置为文件路径。

```yaml
name: inbox-triage
args:
  tag:
    default: "family"
steps:
  - id: collect
    command: inbox list --json
  - id: categorize
    command: inbox categorize --json
    stdin: $collect.stdout
  - id: approve
    command: inbox apply --approve
    stdin: $categorize.stdout
    approval: required
  - id: execute
    command: inbox apply --execute
    stdin: $categorize.stdout
    condition: $approve.approved
```

注意：

- `stdin: $step.stdout`和`stdin: $step.json`传递前一步的输出。
- `condition`（或`when`）可以根据`$step.approved`来控制步骤的执行。

## 安装Lobster

在运行OpenClaw网关的**同一主机**上安装Lobster CLI（请参见[Lobster仓库](https://github.com/openclaw/lobster)），并确保`lobster`位于`PATH`。
如果您想使用自定义二进制位置，请在工具调用中传递一个**绝对**的`lobsterPath`。

## 启用工具

Lobster是一个**可选**的插件工具（默认不启用）。

推荐（附加，安全）：

```json
{
  "tools": {
    "alsoAllow": ["lobster"]
  }
}
```

或者按代理：

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": {
          "alsoAllow": ["lobster"]
        }
      }
    ]
  }
}
```

除非您打算以限制性的白名单模式运行，否则避免使用`tools.allow: ["lobster"]`。

注意：白名单是可选插件的可选功能。如果您的白名单仅命名了插件工具（如`lobster`），OpenClaw会保持核心工具启用。要限制核心工具，请在白名单中也包括您想要的核心工具或组。

## 示例：电子邮件分拣

不使用Lobster：

```
User: "Check my email and draft replies"
→ openclaw calls gmail.list
→ LLM summarizes
→ User: "draft replies to #2 and #5"
→ LLM drafts
→ User: "send #2"
→ openclaw calls gmail.send
(repeat daily, no memory of what was triaged)
```

使用 Lobster:

```json
{
  "action": "run",
  "pipeline": "email.triage --limit 20",
  "timeoutMs": 30000
}
```

返回一个 JSON 封装（截断）:

```json
{
  "ok": true,
  "status": "needs_approval",
  "output": [{ "summary": "5 need replies, 2 need action" }],
  "requiresApproval": {
    "type": "approval_request",
    "prompt": "Send 2 draft replies?",
    "items": [],
    "resumeToken": "..."
  }
}
```

用户批准 → 恢复:

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

一个工作流。确定性。安全。

## 工具参数

### `run`

以工具模式运行管道。

```json
{
  "action": "run",
  "pipeline": "gog.gmail.search --query 'newer_than:1d' | email.triage",
  "cwd": "/path/to/workspace",
  "timeoutMs": 30000,
  "maxStdoutBytes": 512000
}
```

使用参数运行工作流文件:

```json
{
  "action": "run",
  "pipeline": "/path/to/inbox-triage.lobster",
  "argsJson": "{\"tag\":\"family\"}"
}
```

### `resume`

在批准后继续中断的工作流。

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

### 可选输入

- `lobsterPath`: Lobster 二进制文件的绝对路径（省略以使用 `PATH`）。
- `cwd`: 管道的工作目录（默认为当前进程的工作目录）。
- `timeoutMs`: 如果子进程超出此持续时间则终止（默认：20000）。
- `maxStdoutBytes`: 如果 stdout 超出此大小则终止子进程（默认：512000）。
- `argsJson`: 传递给 `lobster run --args-json` 的 JSON 字符串（仅限工作流文件）。

## 输出封装

Lobster 返回一个包含三种状态之一的 JSON 封装：

- `ok` → 成功完成
- `needs_approval` → 暂停；需要 `requiresApproval.resumeToken` 来恢复
- `cancelled` → 显式拒绝或取消

工具在 `content`（美化后的 JSON）和 `details`（原始对象）中呈现封装。

## 批准

如果存在 `requiresApproval`，检查提示并决定：

- `approve: true` → 恢复并继续副作用
- `approve: false` → 取消并最终化工作流

使用 `approve --preview-from-stdin --limit N` 将 JSON 预览附加到审批请求，而无需自定义 jq/heredoc 胶水。恢复令牌现在更紧凑：Lobster 在其状态目录下存储工作流恢复状态，并返回一个小的令牌密钥。

## OpenProse

OpenProse 与 Lobster 配合良好：使用 `/prose` 编排多代理准备，然后运行 Lobster 管道以进行确定性审批。如果 Prose 程序需要 Lobster，请通过 `tools.subagents.tools` 允许子代理使用 `lobster` 工具。参见 [OpenProse](/prose)。

## 安全性

- **仅本地子进程** — 插件本身不进行网络调用。
- **无密钥** — Lobster 不管理 OAuth；它调用执行此操作的 OpenClaw 工具。
- **沙盒感知** — 当工具上下文被沙盒化时禁用。
- **加固** — 如果指定了，`lobsterPath` 必须是绝对路径；强制执行超时和输出限制。

## 故障排除

- **`lobster subprocess timed out`** → 增加 `timeoutMs`，或将长管道拆分。
- **`lobster output exceeded maxStdoutBytes`** → 提高 `maxStdoutBytes` 或减少输出大小。
- **`lobster returned invalid JSON`** → 确保管道以工具模式运行并仅打印 JSON。
- **`lobster failed (code …)`** → 在终端中运行相同的管道以检查 stderr。

## 了解更多

- [插件](/plugin)
- [插件工具编写](/plugins/agent-tools)

## 案例研究：社区工作流

一个公共示例：一个“第二大脑”CLI + Lobster 管道，管理三个 Markdown 保险库（个人、合作伙伴、共享）。CLI 发出用于统计信息、收件箱列表和过时扫描的 JSON；Lobster 将这些命令链接成工作流，如 `weekly-review`，`inbox-triage`，`memory-consolidation` 和 `shared-task-sync`，每个工作流都有审批门。AI 在可用时处理判断（分类），并在不可用时回退到确定性规则。

- 线程: https://x.com/plattenschieber/status/2014508656335770033
- 仓库: https://github.com/bloomedai/brain-cli