---
summary: "JSON-only LLM tasks for workflows (optional plugin tool)"
read_when:
  - You want a JSON-only LLM step inside workflows
  - You need schema-validated LLM output for automation
title: "LLM Task"
---
# LLM任务

`llm-task` 是一个 **可选插件工具**，用于运行仅支持JSON的LLM任务，并返回结构化输出（可选地根据JSON Schema进行验证）。

这对于像Lobster这样的工作流引擎非常理想：您可以添加单个LLM步骤，而无需为每个工作流编写自定义的OpenClaw代码。

## 启用插件

1. 启用插件：

```json
{
  "plugins": {
    "entries": {
      "llm-task": { "enabled": true }
    }
  }
}
```

2. 允许使用该工具（它已注册到 `optional: true`）：

```json
{
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

## 配置（可选）

```json
{
  "plugins": {
    "entries": {
      "llm-task": {
        "enabled": true,
        "config": {
          "defaultProvider": "openai-codex",
          "defaultModel": "gpt-5.2",
          "defaultAuthProfileId": "main",
          "allowedModels": ["openai-codex/gpt-5.2"],
          "maxTokens": 800,
          "timeoutMs": 30000
        }
      }
    }
  }
}
```

`allowedModels` 是 `provider/model` 字符串的允许列表。如果设置，则拒绝列表之外的任何请求。

## 工具参数

- `prompt` (字符串, 必需)
- `input` (任意, 可选)
- `schema` (对象, 可选JSON Schema)
- `provider` (字符串, 可选)
- `model` (字符串, 可选)
- `authProfileId` (字符串, 可选)
- `temperature` (数字, 可选)
- `maxTokens` (数字, 可选)
- `timeoutMs` (数字, 可选)

## 输出

返回 `details.json` 包含解析后的JSON（当提供时，根据 `schema` 进行验证）。

## 示例：Lobster工作流步骤

```lobster
openclaw.invoke --tool llm-task --action json --args-json '{
  "prompt": "Given the input email, return intent and draft.",
  "input": {
    "subject": "Hello",
    "body": "Can you help?"
  },
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

## 安全注意事项

- 该工具仅支持 **JSON**，并指示模型仅输出JSON（无代码块，无注释）。
- 对于此运行，不向模型暴露任何工具。
- 除非使用 `schema` 进行验证，否则不要信任输出。
- 在任何具有副作用的步骤（发送、发布、执行）之前放置审批。