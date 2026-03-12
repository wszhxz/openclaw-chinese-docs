---
summary: "Plugin manifest + JSON schema requirements (strict config validation)"
read_when:
  - You are building a OpenClaw plugin
  - You need to ship a plugin config schema or debug plugin validation errors
title: "Plugin Manifest"
---
# 插件清单 (openclaw.plugin.json)

每个插件**必须**在**插件根目录**中包含一个 `openclaw.plugin.json` 文件。
OpenClaw 使用此清单来验证配置，**无需执行插件代码**。缺少或无效的清单被视为插件错误，并阻止配置验证。

请参阅完整的插件系统指南：[插件](/tools/plugin)。

## 必需字段

```json
{
  "id": "voice-call",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

必需的键：

- `id` (string): 规范的插件ID。
- `configSchema` (object): 插件配置的JSON Schema（内联）。

可选的键：

- `kind` (string): 插件类型（例如：`"memory"`, `"context-engine"`）。
- `channels` (array): 由该插件注册的频道ID（例如：`["matrix"]`）。
- `providers` (array): 由该插件注册的提供者ID。
- `skills` (array): 要加载的技能目录（相对于插件根目录）。
- `name` (string): 插件的显示名称。
- `description` (string): 插件的简短摘要。
- `uiHints` (object): 用于UI渲染的配置字段标签/占位符/敏感标志。
- `version` (string): 插件版本（信息性）。

## JSON Schema要求

- **每个插件都必须附带一个JSON Schema**，即使它不接受任何配置。
- 空的Schema是可以接受的（例如，`{ "type": "object", "additionalProperties": false }`）。
- Schemas在配置读写时进行验证，而不是在运行时。

## 验证行为

- 未知的 `channels.*` 键是**错误**，除非频道ID由插件清单声明。
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny`, 和 `plugins.slots.*` 必须引用**可发现的**插件ID。未知的ID是**错误**。
- 如果安装了插件但其清单或Schema损坏或缺失，验证将失败，Doctor会报告插件错误。
- 如果插件配置存在但插件被**禁用**，配置将被保留，并且Doctor和日志中会显示**警告**。

## 注意事项

- 所有插件都需要清单，包括从本地文件系统加载的插件。
- 运行时仍然单独加载插件模块；清单仅用于发现+验证。
- 通过 `plugins.slots.*` 选择独占插件类型。
  - `kind: "memory"` 由 `plugins.slots.memory` 选择。
  - `kind: "context-engine"` 由 `plugins.slots.contextEngine` 选择
    （默认：内置 `legacy`）。
- 如果您的插件依赖于原生模块，请记录构建步骤和任何包管理器允许列表要求（例如，pnpm `allow-build-scripts` - `pnpm rebuild <package>`）。