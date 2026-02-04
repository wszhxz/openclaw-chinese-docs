---
title: Lobster
summary: "Typed workflow runtime for OpenClaw with resumable approval gates."
description: Typed workflow runtime for OpenClaw — composable pipelines with approval gates.
read_when:
  - You want deterministic multi-step workflows with explicit approvals
  - You need to resume a workflow without re-running earlier steps
---
# 龙虾

龙虾是一个工作流外壳，允许OpenClaw以单个确定性操作的方式运行多步骤工具序列，并具有显式的批准检查点。

## 钩子

您的助手可以构建管理自身的工具。请求一个工作流，30分钟后您将获得一个CLI加上作为一次调用运行的管道。龙虾是缺失的部分：确定性的管道、显式批准和可恢复的状态。

## 为什么

今天，复杂的流程需要许多来回的工具调用。每次调用都会消耗代币，并且LLM必须协调每一步骤。龙虾将这种协调移动到一个类型化运行时中：

- **一次调用而不是多次**：OpenClaw运行一次龙虾工具调用并获得一个结构化结果。
- **内置批准**：副作用（发送电子邮件、发布评论）会暂停工作流，直到显式批准。
- **可恢复**：暂停的工作流会返回一个令牌；批准并恢复而无需重新运行所有内容。

## 为什么使用DSL而不是普通程序？

龙虾故意保持小巧。目标不是“一种新语言”，而是一种可预测的、AI友好的管道规范，具有内置的批准和恢复令牌。

- **内置批准/恢复**：普通程序可以提示人类，但不能在没有自己发明该运行时的情况下使用持久令牌进行暂停和恢复。
- **确定性+可审计性**：管道是数据，因此易于记录、比较、重播和审查。
- **AI受限表面**：小型语法+JSON管道减少了“创造性”的代码路径，并使验证变得现实。
- **内置安全策略**：超时、输出上限、沙箱检查和白名单由运行时强制执行，而不是每个脚本。
- **仍然可编程**：每个步骤可以调用任何CLI或脚本。如果您想要JS/TS，从代码生成`.lobster`文件。

## 它是如何工作的

OpenClaw以**工具模式**启动本地的`lobster` CLI，并从标准输出解析一个JSON信封。
如果管道暂停以等待批准，工具将返回一个`resumeToken`，以便稍后继续。

## 模式：小型CLI + JSON管道 + 批准

构建小型命令以使用JSON通信，然后将它们链接成单个龙虾调用。（下面的示例命令名称——替换为您自己的。）

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

如果管道请求批准，请使用令牌继续：

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

AI触发工作流；龙虾执行步骤。批准门保持副作用明确且可审计。

示例：将输入项映射到工具调用：

```bash
gog.gmail.search --query 'newer_than:1d' \
  | openclaw.invoke --tool message --action send --each --item-key message --args-json '{"provider":"telegram","to":"..."}'
```

## 仅JSON的LLM步骤（llm-task）

对于需要**结构化LLM步骤**的工作流，启用可选的
`llm-task`插件工具并从龙虾调用它。这保持了工作流的确定性，同时仍允许您使用模型进行分类/摘要/草稿。

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

龙虾可以使用`name`、`args`、`steps`、`env`、`condition`和`approval`字段运行YAML/JSON工作流文件。在OpenClaw工具调用中，将`pipeline`设置为文件路径。

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
- `condition`（或`when`）可以根据`$step.approved`来控制步骤。

## 安装龙虾

在与OpenClaw网关运行在同一台主机上安装龙虾CLI（参阅[Lobster仓库](https://github.com/openclaw/lobster)），并确保`lobster`位于`PATH`。
如果您想使用自定义二进制位置，请在工具调用中传递一个**绝对**的`lobsterPath`。

## 启用工具

龙虾是一个**可选**的插件工具（默认不启用）。

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

除非打算在限制性白名单模式下运行，否则避免使用`tools.allow: ["lobster"]`。

注意：可选插件的白名单是选择加入的。如果您的白名单仅命名插件工具（如`lobster`），OpenClaw将保持核心工具启用。要限制核心工具，请在白名单中包括您想要的核心工具或组。

## 示例：电子邮件筛选

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

使用龙虾：

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

用户批准 → 继续：

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

以工具模式运行一个管道。

```json
{
  "action": "run",
  "pipeline": "gog.gmail.search --query 'newer_than:1d' | email.triage",
  "cwd": "/path/to/workspace",
  "timeoutMs": 30000,
  "maxStdoutBytes": 512000
}
```

使用参数运行一个工作流文件：

```json
{
  "action": "run",
  "pipeline": "/path/to/inbox-triage.lobster",
  "argsJson": "{\"tag\":\"family\"}"
}
```

### `resume`

在批准后继续一个暂停的工作流。

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

### 可选输入

- `lobsterPath`：龙虾二进制文件的绝对路径（省略以使用`PATH`）。
- `cwd`：管道的工作目录（默认为当前进程的工作目录）。
- `timeoutMs`：如果子进程超出此持续时间则终止（默认：20000）。
- `maxStdoutBytes`：如果标准输出超出此大小则终止（默认：512000）。
- `argsJson`：传递给`lobster run --args-json`的JSON字符串（仅限工作流文件）。

## 输出信封

龙虾返回一个包含三种状态之一的JSON信封：

- `ok` → 成功完成
- `needs_approval` → 暂停；需要`requiresApproval.resumeToken`才能继续
- `cancelled` → 明确拒绝或取消

工具在`content`（漂亮JSON）和`details`（原始对象）中呈现信封。

## 批准

如果存在`requiresApproval`，请检查提示并决定：

- `approve: true` → 继续并继续副作用
- `approve: false` → 取消并最终确定工作流

使用`approve --preview-from-stdin --limit N`将JSON预览附加到批准请求，而无需自定义jq/heredoc粘合代码。恢复令牌现在更紧凑：龙虾在其状态目录下存储工作流恢复状态，并返回一个小令牌键。

## OpenProse

OpenProse与龙虾配合良好：使用`/prose`编排多代理准备，然后运行一个龙虾管道以进行确定性批准。如果Prose程序需要龙虾，请通过`tools.subagents.tools`为子代理允许`lobster`工具。参阅[OpenProse](/prose)。

## 安全

- **仅本地子进程** — 插件本身不会进行网络调用。
- **无秘密** — 龙虾不管理OAuth；它调用执行此操作的OpenClaw工具。
- **沙盒感知** — 当工具上下文被沙盒化时禁用。
- **加固** — 如果指定了，`lobsterPath`必须是绝对路径；强制执行超时和输出上限。

## 故障排除

- **`lobster subprocess timed out`** → 增加`timeoutMs`，或将长管道拆分。
- **`lobster output exceeded maxStdoutBytes`** → 提高`maxStdoutBytes`或减少输出大小。
- **`lobster returned invalid JSON`** → 确保管道以工具模式运行并仅打印JSON。
- **`lobster failed (code …)`** → 在终端中运行相同的管道以检查stderr。

## 了解更多

- [插件](/plugin)
- [插件工具编写](/plugins/agent-tools)

## 案例研究：社区工作流

一个公共示例：一个“第二大脑”CLI + 龙虾管道，管理三个Markdown保险库（个人、合作伙伴、共享）。CLI发出JSON用于统计信息、收件箱列表和过时扫描；龙虾将这些命令链接成工作流，如`weekly-review`、`inbox-triage`、`memory-consolidation`和`shared-task-sync`，每个工作流都有批准门。AI在可用时处理判断（分类），并在不可用时回退到确定性规则。

- 线程：https://x.com/plattenschieber/status/2014508656335770033
- 仓库：https://github.com/bloomedai/brain-cli