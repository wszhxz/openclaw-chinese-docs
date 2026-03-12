---
title: Lobster
summary: "Typed workflow runtime for OpenClaw with resumable approval gates."
description: Typed workflow runtime for OpenClaw — composable pipelines with approval gates.
read_when:
  - You want deterministic multi-step workflows with explicit approvals
  - You need to resume a workflow without re-running earlier steps
---
# 龙虾

龙虾是一个工作流外壳，它允许OpenClaw将多步骤工具序列作为单个确定性操作运行，并带有明确的批准检查点。

## 钩子

您的助手可以构建管理自身的工具。请求一个工作流，30分钟后您将拥有一个CLI加上可以一次性调用的管道。龙虾是缺失的部分：确定性的管道、明确的批准和可恢复的状态。

## 为什么

如今，复杂的工作流需要许多来回的工具调用。每次调用都会消耗令牌，而LLM必须协调每个步骤。龙虾将这种协调移到了一个类型化的运行时中：

- **一次调用代替多次调用**：OpenClaw运行一次龙虾工具调用并获得结构化结果。
- **内置批准**：副作用（发送电子邮件、发布评论）会暂停工作流，直到明确批准。
- **可恢复**：暂停的工作流返回一个令牌；批准后无需重新运行所有内容即可恢复。

## 为什么使用DSL而不是普通程序？

龙虾有意保持小巧。目标不是“一种新语言”，而是一种具有头等批准和恢复令牌的可预测的、AI友好的管道规范。

- **内置批准/恢复**：普通程序可以提示人类，但不能在没有自己发明运行时的情况下_暂停和恢复_持久令牌。
- **确定性+可审计性**：管道是数据，因此它们易于记录、差异比较、重放和审查。
- **对AI的约束表面**：一个小语法+JSON管道减少了“创造性”代码路径，并使验证变得现实。
- **内置安全策略**：超时、输出上限、沙箱检查和白名单由运行时强制执行，而不是每个脚本。
- **仍然可编程**：每个步骤都可以调用任何CLI或脚本。如果您想要JS/TS，可以从代码生成`.lobster`文件。

## 工作原理

OpenClaw以**工具模式**启动本地`lobster` CLI，并从stdout解析JSON信封。
如果管道因批准而暂停，工具将返回一个`resumeToken`以便稍后继续。

## 模式：小CLI + JSON管道 + 批准

构建说JSON的小命令，然后将它们链接成一个单一的龙虾调用。（下面的示例命令名称——请替换为您自己的。）

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

如果管道请求批准，使用令牌恢复：

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

AI触发工作流；龙虾执行步骤。批准门确保副作用明确且可审计。

示例：将输入项映射到工具调用：

```bash
gog.gmail.search --query 'newer_than:1d' \
  | openclaw.invoke --tool message --action send --each --item-key message --args-json '{"provider":"telegram","to":"..."}'
```

## 仅JSON的LLM步骤 (llm-task)

对于需要**结构化LLM步骤**的工作流，启用可选的
`llm-task`插件工具并从龙虾中调用它。这使工作流保持确定性，同时仍允许您使用模型进行分类/总结/草稿。

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

在管道中使用它：

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

有关详细信息和配置选项，请参阅[LLM任务](/tools/llm-task)。

## 工作流文件 (.lobster)

龙虾可以运行包含`name`、`args`、`steps`、`env`、`condition`和`approval`字段的YAML/JSON工作流文件。在OpenClaw工具调用中，将`pipeline`设置为文件路径。

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

注意事项：

- `stdin: $step.stdout`和`stdin: $step.json`传递先前步骤的输出。
- `condition`（或`when`）可以根据`$step.approved`来控制步骤。

## 安装龙虾

在同一台主机上安装龙虾CLI，该主机运行OpenClaw网关（参见[Lobster仓库](https://github.com/openclaw/lobster)），并确保`lobster`位于`PATH`上。

## 启用工具

龙虾是一个**可选**的插件工具（默认未启用）。

推荐（附加的、安全的）：

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

除非您打算在限制性白名单模式下运行，否则避免使用`tools.allow: ["lobster"]`。

注意：白名单是可选插件的可选项。如果您的白名单只命名插件工具（如`lobster`），OpenClaw将保持核心工具启用。要限制核心工具，也请在白名单中包括您想要的核心工具或组。

## 示例：电子邮件分类

没有龙虾：

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

有龙虾：

```json
{
  "action": "run",
  "pipeline": "email.triage --limit 20",
  "timeoutMs": 30000
}
```

返回一个JSON信封（截断）：

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

用户批准→恢复：

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
  "cwd": "workspace",
  "timeoutMs": 30000,
  "maxStdoutBytes": 512000
}
```

带参数运行工作流文件：

```json
{
  "action": "run",
  "pipeline": "/path/to/inbox-triage.lobster",
  "argsJson": "{\"tag\":\"family\"}"
}
```

### `resume`

在批准后继续暂停的工作流。

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

### 可选输入

- `cwd`：管道的相对工作目录（必须保持在当前进程工作目录内）。
- `timeoutMs`：如果超过此持续时间则终止子进程（默认：20000）。
- `maxStdoutBytes`：如果stdout超过此大小则终止子进程（默认：512000）。
- `argsJson`：传递给`lobster run --args-json`的JSON字符串（仅限工作流文件）。

## 输出信封

龙虾返回一个带有三种状态之一的JSON信封：

- `ok` → 成功完成
- `needs_approval` → 暂停；需要`requiresApproval.resumeToken`才能恢复
- `cancelled` → 明确拒绝或取消

工具在`content`（漂亮的JSON）和`details`（原始对象）中显示信封。

## 批准

如果存在`requiresApproval`，请检查提示并决定：

- `approve: true` → 恢复并继续副作用
- `approve: false` → 取消并最终确定工作流

使用`approve --preview-from-stdin --limit N`将JSON预览附加到批准请求，而无需自定义jq/heredoc粘合。恢复令牌现在更紧凑：龙虾将其工作流恢复状态存储在其状态目录下，并返回一个小令牌键。

## OpenProse

OpenProse与龙虾配合得很好：使用`/prose`来协调多代理准备，然后运行一个龙虾管道以进行确定性批准。如果Prose程序需要龙虾，请通过`tools.subagents.tools`为子代理允许`lobster`工具。参见[OpenProse](/prose)。

## 安全性

- **仅本地子进程** — 插件本身不进行网络调用。
- **无秘密** — 龙虾不管理OAuth；它调用管理OAuth的OpenClaw工具。
- **沙箱感知** — 当工具上下文被沙箱化时禁用。
- **加固** — 在`PATH`上固定可执行文件名(`lobster`)；强制执行超时和输出上限。

## 故障排除

- **`lobster subprocess timed out`** → 增加`timeoutMs`，或将长管道拆分。
- **`lobster output exceeded maxStdoutBytes`** → 提高`maxStdoutBytes`或减少输出大小。
- **`lobster returned invalid JSON`** → 确保管道以工具模式运行并仅打印JSON。
- **`lobster failed (code …)`** → 在终端中运行相同的管道以检查stderr。

## 了解更多

- [插件](/tools/plugin)
- [插件工具编写](/plugins/agent-tools)

## 案例研究：社区工作流

一个公开的例子：“第二大脑”CLI + 龙虾管道，管理三个Markdown库（个人、合作伙伴、共享）。CLI发出用于统计、收件箱列表和过期扫描的JSON；龙虾将这些命令链接成像`weekly-review`、`inbox-triage`、`memory-consolidation`和`shared-task-sync`这样的工作流，每个都有批准门。当可用时，AI处理判断（分类），并在不可用时回退到确定性规则。

- 讨论串: [https://x.com/plattenschieber/status/2014508656335770033](https://x.com/plattenschieber/status/2014508656335770033)
- 仓库: [https://github.com/bloomedai/brain-cli](https://github.com/bloomedai/brain-cli)