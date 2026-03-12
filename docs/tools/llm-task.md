---
summary: "JSON-only LLM tasks for workflows (optional plugin tool)"
read_when:
  - You want a JSON-only LLM step inside workflows
  - You need schema-validated LLM output for automation
title: "LLM Task"
---
# LLM 任务

`llm-task` 是一个**可选的插件工具**，它运行仅 JSON 的 LLM 任务并返回结构化的输出（可以选择性地针对 JSON Schema 进行验证）。

这对于像 Lobster 这样的工作流引擎来说是理想的：您可以添加单个 LLM 步骤，而无需为每个工作流编写自定义的 OpenClaw 代码。

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

2. 将工具列入白名单（它使用 `optional: true` 注册）：

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
          "defaultModel": "gpt-5.4",
          "defaultAuthProfileId": "main",
          "allowedModels": ["openai-codex/gpt-5.4"],
          "maxTokens": 800,
          "timeoutMs": 30000
        }
      }
    }
  }
}
```

`allowedModels` 是一个 `provider/model` 字符串的白名单。如果设置了此列表，则任何不在列表中的请求将被拒绝。

## 工具参数

- `prompt` (string, required)
- `input` (any, optional)
- `schema` (object, optional JSON Schema)
- `provider` (string, optional)
- `model` (string, optional)
- `authProfileId` (string, optional)
- `temperature` (number, optional)
- `maxTokens` (number, optional)
- `timeoutMs` (number, optional)

## 输出

返回包含解析后的 JSON 的 `details.json`（当提供 `schema` 时进行验证）。

## 示例：Lobster 工作流步骤

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

- 该工具是**仅 JSON**的，并指示模型只输出 JSON（无代码围栏，无注释）。
- 在此次运行中不向模型暴露任何工具。
- 除非您使用 `schema` 进行验证，否则请将输出视为不可信。
- 在任何具有副作用的步骤（发送、发布、执行）之前设置审批。