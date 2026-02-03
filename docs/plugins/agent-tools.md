---
summary: "Write agent tools in a plugin (schemas, optional tools, allowlists)"
read_when:
  - You want to add a new agent tool in a plugin
  - You need to make a tool opt-in via allowlists
title: "Plugin Agent Tools"
---
# 插件代理工具

OpenClaw 插件可以注册 **代理工具**（JSON‑schema 函数），这些工具在代理运行期间暴露给大语言模型（LLM）。工具可以是 **必需**（始终可用）或 **可选**（手动启用）。

代理工具的配置位于主配置的 `tools` 下，或每个代理的 `agents.list[].tools` 下。允许列表/拒绝列表策略控制代理可以调用的工具。

## 基础工具

```ts
import { Type } from "@sinclair/typebox";

export default function (api) {
  api.registerTool({
    name: "my_tool",
    description: "执行某个操作",
    parameters: Type.Object({
      input: Type.String(),
    }),
    async execute(_id, params) {
      return { content: [{ type: "text", text: params.input }] };
    },
  });
}
```

## 可选工具（手动启用）

可选工具 **永远不会** 自动启用。用户必须将其添加到代理的允许列表中。

```ts
export default function (api) {
  api.registerTool(
    {
      name: "workflow_tool",
      description: "运行本地工作流",
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

在 `agents.list[].tools.allow`（或全局 `tools.allow`）中启用可选工具：

```json5
{
  agents: {
    list: [
      {
        id: "main",
        tools: {
          allow: [
            "workflow_tool", // 具体工具名称
            "workflow", // 插件 ID（启用该插件下的所有工具）
            "group:plugins", // 所有插件工具
          ],
        },
      },
    ],
  },
}
```

其他影响工具可用性的配置项：

- 仅命名插件工具的允许列表被视为插件手动启用；核心工具除非也在允许列表中包含核心工具或组，否则保持启用。
- `tools.profile` / `agents.list[].tools.profile`（基础允许列表）
- `tools.byProvider` / `agents.list[].tools.byProvider`（特定提供者的允许/拒绝）
- `tools.sandbox.tools.*`（在沙箱环境中时的沙箱工具策略）

## 规则 + 提示

- 工具名称 **不得** 与核心工具名称冲突；冲突的工具将被跳过。
- 允许列表中使用的插件 ID 不得与核心工具名称冲突。
- 对于会触发副作用或需要额外二进制文件/凭证的工具，建议使用 `optional: true`。