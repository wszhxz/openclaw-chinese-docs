---
summary: "Write agent tools in a plugin (schemas, optional tools, allowlists)"
read_when:
  - You want to add a new agent tool in a plugin
  - You need to make a tool opt-in via allowlists
title: "Plugin Agent Tools"
---
# 插件代理工具

OpenClaw 插件可以注册 **代理工具**（JSON-schema 函数），这些工具在代理运行期间向 LLM 暴露。工具可以是 **必需的**（始终可用）或 **可选的**（选择加入）。

代理工具在主配置中的 `tools` 下进行配置，或者每个代理在 `agents.list[].tools` 下进行配置。允许列表/拒绝列表策略控制代理可以调用哪些工具。

## 基本工具

```ts
import { Type } from "@sinclair/typebox";

export default function (api) {
  api.registerTool({
    name: "my_tool",
    description: "Do a thing",
    parameters: Type.Object({
      input: Type.String(),
    }),
    async execute(_id, params) {
      return { content: [{ type: "text", text: params.input }] };
    },
  });
}
```

## 可选工具（选择加入）

可选工具 **从不** 自动启用。用户必须将其添加到代理的允许列表中。

```ts
export default function (api) {
  api.registerTool(
    {
      name: "workflow_tool",
      description: "Run a local workflow",
      parameters: {
        type: "object",
        properties: {
          pipeline: { type: "string" },
        },
        required: ["pipeline"],
      },
      async execute(_id, params) {
        return { content: [{ type: "text", text: params.pipeline }] };
      },
    },
    { optional: true },
  );
}
```

在 `agents.list[].tools.allow` 中启用可选工具（或全局 `tools.allow`）：

```json5
{
  agents: {
    list: [
      {
        id: "main",
        tools: {
          allow: [
            "workflow_tool", // specific tool name
            "workflow", // plugin id (enables all tools from that plugin)
            "group:plugins", // all plugin tools
          ],
        },
      },
    ],
  },
}
```

影响工具可用性的其他配置选项：

- 仅命名插件工具的允许列表被视为插件选择加入；除非您还在允许列表中包含核心工具或组，否则核心工具将保持启用状态。
- `tools.profile` / `agents.list[].tools.profile`（基本允许列表）
- `tools.byProvider` / `agents.list[].tools.byProvider`（特定提供商的允许/拒绝）
- `tools.sandbox.tools.*`（沙盒化时的沙盒工具策略）

## 规则 + 提示

- 工具名称 **不得** 与核心工具名称冲突；冲突的工具将被跳过。
- 允许列表中使用的插件 ID 不得与核心工具名称冲突。
- 对于触发副作用或需要额外二进制文件/凭据的工具，请优先使用 `optional: true`。