---
summary: "Plugin manifest + JSON schema requirements (strict config validation)"
read_when:
  - You are building a OpenClaw plugin
  - You need to ship a plugin config schema or debug plugin validation errors
title: "Plugin Manifest"
---
# 插件清单（openclaw.plugin.json）

每个插件**必须**在**插件根目录**中包含一个`openclaw.plugin.json`文件。
OpenClaw 使用此清单来验证配置**而无需执行插件代码**。缺少或无效的清单会被视为插件错误并阻止配置验证。

查看完整的插件系统指南：[插件](/plugin)。

## 必填字段

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

必填键：

- `id`（字符串）：规范插件ID。
- `configSchema`（对象）：插件配置的JSON模式（内联）。

可选键：

- `kind`（字符串）：插件类型（示例：`"memory"`）。
- `channels`（数组）：此插件注册的通道ID（示例：`["matrix"]`）。
- `providers`（数组）：此插件注册的提供者ID。
- `skills`（数组）：要加载的技能目录（相对于插件根目录）。
- `name`（字符串）：插件的显示名称。
- `description`（字符串）：插件的简要说明。
- `uiHints`（对象）：用于UI渲染的配置字段标签/占位符/敏感标志。
- `version`（字符串）：插件版本（信息性）。

## JSON模式要求

- **每个插件都必须包含一个JSON模式**，即使它不接受任何配置。
- 空模式是可以接受的（例如，`{ "type": "object", "additionalProperties": false }`）。
- 模式在读取/写入配置时进行验证，而不是在运行时。

## 验证行为

- 未知的`channels.*`键是**错误**，除非该通道ID在插件清单中声明。
- `plugins.entries.<id>`、`plugins.allow`、`plugins.deny`和`plugins.slots.*`必须引用**可发现**的插件ID。未知的ID是**错误**。
- 如果插件已安装但清单或模式损坏或缺失，验证将失败，Doctor将报告插件错误。
- 如果插件配置存在但插件被**禁用**，配置将被保留，并在Doctor和日志中显示**警告**。

## 注意事项

- 清单是**所有插件**的必需项，包括本地文件系统加载。
- 运行时仍会单独加载插件模块；清单仅用于**发现 + 验证**。
- 如果您的插件依赖原生模块，请记录构建步骤以及任何包管理器允许列表要求（例如，pnpm `allow-build-scripts` - `pnpm rebuild <package>`）。