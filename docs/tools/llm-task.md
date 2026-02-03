---
summary: "JSON-only LLM tasks for workflows (optional plugin tool)"
read_when:
  - You want a JSON-only LLM step inside workflows
  - You need schema-validated LLM output for automation
title: "LLM Task"
---
# LLM任务

`llm-task` 是一个**可选插件工具**，用于运行仅JSON格式的LLM任务，并返回结构化输出（可选地验证JSON模式）。

这对于工作流引擎（如Lobster）非常理想：您可以在不为每个工作流编写自定义OpenClaw代码的情况下，添加一个LLM步骤。

## 启用插件

1. 启用插件：

```json
{
  "plugins": {
    "entries": {
      "ll.任务": { "启用": true }
    }
  }
}
```

2. 允许该工具（它已注册为`optional: true`）：

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": { "允许": ["llm-task"] }
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
        "启用": true,
        "配置": {
          "默认提供者": "openai-codex",
          "默认模型": "gpt-5.2",
          "默认认证配置文件ID": "main",
          "允许的模型": ["openai-codex/gpt-5.2"],
          "最大令牌数": 800,
          "超时毫秒": 30000
        }
      }
    }
  }
}
```

`允许的模型` 是一个`提供者/模型`字符串的允许列表。如果设置，任何超出列表的请求都将被拒绝。

## 工具参数

- `提示`（字符串，必需）
- `输入`（任意类型，可选）
- `模式`（对象，可选JSON模式）
- `提供者`（字符串，可选）
- `模型`（字符串，可选）
- `认证配置文件ID`（字符串，可选）
- `温度`（数字，可选）
- `最大令牌数`（数字，可选）
- `超时毫秒`（数字，可选）

## 输出

返回包含解析后的JSON的`details.json`（当提供`模式`时，会验证其有效性）。

## 示例：Lobster工作流步骤

```lobster
openclaw.invoke --tool llm-task --action json --args-json '{
  "提示": "根据输入的电子邮件，返回意图和草稿。",
  "输入": {
    "主题": "你好",
    "正文": "你能帮忙吗？"
  },
  "模式": {
    "类型": "对象",
    "属性": {
      "意图": { "类型": "字符串" },
      "草稿": { "类型": "字符串" }
    },
    "必需": ["意图", "草稿"],
    "额外属性": false
  }
}'
```

## 安全注意事项

- 该工具是**仅JSON**格式，并指示模型仅输出JSON（无代码块，无注释）。
- 此次运行不会向模型暴露任何工具。
- 除非使用`模式`进行验证，否则将输出视为不可信。
- 在任何具有副作用的步骤（发送、发布、执行）之前进行审批。