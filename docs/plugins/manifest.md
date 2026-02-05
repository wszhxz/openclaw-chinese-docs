---
summary: "Plugin manifest + JSON schema requirements (strict config validation)"
read_when:
  - You are building a OpenClaw plugin
  - You need to ship a plugin config schema or debug plugin validation errors
title: "Plugin Manifest"
---
# 插件清单 (openclaw.plugin.json)

每个插件 **必须** 在 **插件根目录** 中包含一个 `openclaw.plugin.json` 文件。
OpenClaw 使用此清单在 **不执行插件代码** 的情况下验证配置。缺少或无效的清单被视为插件错误，并阻止配置验证。

查看完整的插件系统指南：[Plugins](/plugin)。

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

必需键：

- `id` (string): 插件的标准 ID。
- `configSchema` (object): 插件配置的 JSON Schema（内联）。

可选键：

- `kind` (string): 插件类型（示例：`"memory"`）。
- `channels` (array): 由该插件注册的频道 ID（示例：`["matrix"]`）。
- `providers` (array): 由该插件注册的提供者 ID。
- `skills` (array): 要加载的技能目录（相对于插件根目录）。
- `name` (string): 插件的显示名称。
- `description` (string): 插件的简短摘要。
- `uiHints` (object): 用于 UI 渲染的配置字段标签/占位符/敏感标志。
- `version` (string): 插件版本（信息性）。

## JSON Schema 要求

- **每个插件必须包含一个 JSON Schema**，即使它不接受任何配置。
- 空的 Schema 是可以接受的（例如，`{ "type": "object", "additionalProperties": false }`）。
- Schema 在读取/写入配置时进行验证，而不是在运行时。

## 验证行为

- 未知的 `channels.*` 键是 **错误**，除非该频道 ID 由插件清单声明。
- `plugins.entries.<id>`、`plugins.allow`、`plugins.deny` 和 `plugins.slots.*`
  必须引用 **可发现** 的插件 ID。未知的 ID 是 **错误**。
- 如果安装了插件但其清单或 Schema 损坏或丢失，验证将失败，并且 Doctor 会报告插件错误。
- 如果插件配置存在但插件被 **禁用**，则保留配置，并在 Doctor + 日志中显示 **警告**。

## 注意事项

- 清单对 **所有插件** 都是必需的，包括本地文件系统加载的插件。
- 运行时仍然会单独加载插件模块；清单仅用于发现 + 验证。
- 如果您的插件依赖于原生模块，请记录构建步骤以及任何包管理器白名单要求（例如，pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`）。