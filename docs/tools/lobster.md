---
title: Lobster
summary: "Typed workflow runtime for OpenClaw with resumable approval gates."
description: Typed workflow runtime for OpenClaw — composable pipelines with approval gates.
read_when:
  - You want deterministic multi-step workflows with explicit approvals
  - You need to resume a workflow without re-running earlier steps
---
# 螃蟹（Lobster）

螃蟹是一个工作流外壳，它让OpenClaw能够将多步骤的工具序列作为单个、确定性的操作运行，并带有显式的审批检查点。

## 钩子（Hook）

您的助手可以构建管理自身的工具。请求一个工作流，30分钟后您将拥有一个命令行界面（CLI）和可以作为单次调用运行的流水线。螃蟹就是缺失的一环：确定性流水线、显式审批和可恢复状态。

## 为什么（Why）

今天，复杂的工作流需要许多来回的工具调用。每次调用都会消耗令牌，且大语言模型（LLM）必须协调每一步。螃蟹将这种协调转移到了类型化的运行时环境中：

- **一次调用代替多次调用**：OpenClaw运行一次螃蟹工具调用并获取结构化结果。
- **内置审批**：副作用（如发送邮件、发布评论）会暂停工作流，直到显式批准。
- **可恢复**：暂停的工作流返回一个令牌；批准并恢复而无需重新运行所有内容。

## 为什么使用DSL而不是普通程序？

螃蟹有意设计得小巧。目标不是“一种新的语言”，而是一个可预测、适合AI的流水线规范，带有第一类审批和恢复令牌。

- **内置批准/恢复**：普通程序可以提示人类，但无法在不自行发明运行时的情况下暂停和恢复。
- **确定性 + 可审计性**：流水线是数据，因此易于日志记录、差异比较、重放和审查。
- **对AI的受限接口**：一个极小的语法 + JSON管道减少了“创造性”代码路径，并使验证更加现实。
- **内置安全策略**：超时、输出限制、沙箱检查和允许列表由运行时强制执行，而非每个脚本。
- **仍然可编程**：每一步都可以调用任何CLI或脚本。如果您需要JS/TS，可以从代码生成`.lobster`文件。

## 工作原理（How it works）

OpenClaw以**工具模式**启动本地`lobster` CLI并解析从标准输出获取的JSON信封。
如果流水线需要审批，工具将返回一个`resumeToken`以便您稍后继续。

## 模式：小型CLI + JSON管道 + 审批

构建能够使用JSON的小型命令，然后将它们链接成一个螃蟹调用。（以下示例命令名称——请替换为您自己的。）

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

如果流水线请求审批，请使用令牌恢复：

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

AI触发工作流；螃蟹执行步骤。审批门控保持副作用的显式和可审计。

示例：将输入项映射为工具调用：

```bash
gog.gmail.search --query 'newer_than:1d' \
  | openclaw.invoke --tool message --action send --each --item-key message --args-json '{"provider":"telegram","to":"..."}'
```

## 仅JSON的LLM步骤（llm-task）

对于需要**结构化LLM步骤**的工作流，启用可选的`llm-task`插件工具并从螃蟹调用它。这保持工作流的确定性，同时仍允许您使用模型进行分类、摘要和草稿撰写。

启用该工具：

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

## 安全性（Safety）

- **仅本地子进程** —— 插件本身不进行网络调用。
- **无敏感信息** —— 螃蟹不管理OAuth；它调用执行OAuth的OpenClaw工具。
- **沙箱感知** —— 当工具上下文被沙箱禁用时。
- **强化** —— 如果指定`lobsterPath`必须为绝对路径；强制执行超时和输出限制。

## 故障排除（Troubleshooting）

- **`lobster subprocess timed out`** → 增加`timeoutMs`，或拆分长流水线。
- **`lobster output exceeded maxStdoutBytes`** → 提高`maxStdoutBytes`或减少输出大小。
- **`lobster returned invalid JSON`** → 确保流水线在工具模式下运行且仅输出JSON。
- **`lobster failed (code …)`** → 在终端中运行相同的流水线以检查标准错误输出。

## 学习更多（Learn more）

- [插件](/plugin)
- [插件工具开发](/plugins/agent-tools)

## 案例研究：社区工作流

一个公开示例：一个“第二大脑”CLI + 螃蟹流水线，管理三个Markdown vault（个人、合作伙伴、共享）。CLI输出JSON用于统计、收件箱列表和过期扫描；螃蟹将这些命令链接成工作流，如`weekly-review`、`inbox-triage`、`memory-consolidation`和`shared-task-sync`，每个工作流都有审批门控。AI在可用时处理判断（分类），在不可用时回退到确定性规则。

- 线程：https://x.com/plattenschieber/status/2014508656335770033
- 仓库：https://github.com/bloomedai/brain-cli