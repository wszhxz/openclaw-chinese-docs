---
summary: "Strict config validation + doctor-only migrations"
read_when:
  - Designing or implementing config validation behavior
  - Working on config migrations or doctor workflows
  - Handling plugin config schemas or plugin load gating
title: "Strict Config Validation"
---
# 严格配置验证（仅医生迁移）

## 目标

- **在所有位置拒绝未知配置键**（根级 + 嵌套）。
- **拒绝没有模式的插件配置**；不加载该插件。
- **在加载时移除遗留自动迁移**；迁移仅通过医生执行。
- **启动时自动运行医生（干运行）**；如果配置无效，阻止非诊断命令。

## 非目标

- 加载时的向后兼容性（遗留键不自动迁移）。
- 静默丢弃未识别的键。

## 严格验证规则

- 配置必须在每一层级完全匹配模式。
- 未知键是验证错误（根级或嵌套层级不透传）。
- `plugins.entries.<id>.config` 必须通过插件的模式进行验证。
  - 如果插件缺少模式，**拒绝加载插件**并显示明确错误。
- 未知的 `channels.<id>` 键是错误，除非插件清单声明了通道 ID。
- 所有插件均需提供插件清单（`openclaw.plugin.json`）。

## 插件模式强制执行

- 每个插件为其配置提供严格的 JSON 模式（内联在清单中）。
- 插件加载流程：
  1. 解析插件清单 + 模式（`openclaw.plugin.json`）。
  2. 将配置与模式进行验证。
  3. 如果缺少模式或配置无效：阻止插件加载，记录错误。
- 错误信息包括：
  - 插件 ID
  - 原因（缺少模式 / 配置无效）
  - 验证失败的路径
- 禁用插件保留其配置，但医生 + 日志会显示警告。

## 医生流程

- 医生在每次加载配置时运行（默认干运行）。
- 如果配置无效：
  - 打印摘要 + 可操作的错误。
  - 指示：`openclaw doctor --fix`。
- `openclaw doctor --fix`：
  - 应用迁移。
  - 移除未知键。
  - 写入更新后的配置。

## 命令限制（当配置无效时）

允许（仅诊断）：

- `openclaw doctor`
- `openclaw logs`
- `openclaw health`
- `openclaw help`
- `openclaw status`
- `openclaw gateway status`

其他所有命令必须硬失败并显示：“配置无效。运行 `openclaw doctor --fix`。”

## 错误用户体验格式

- 单一摘要标题。
- 分组部分：
  - 未知键（完整路径）
  - 遗留键 / 需要迁移
  - 插件加载失败（插件 ID + 原因 + 路径）

## 实现关键点

- `src/config/zod-schema.ts`：移除根级透传；所有层级严格对象。
- `src/config/zod-schema.providers.ts`：确保严格通道模式。
- `src/config/validation.ts`：对未知键失败；不应用遗留迁移。
- `src/config/io.ts`：移除遗留自动迁移；始终运行医生干运行。
- `src/config/legacy*.ts`：将使用移至医生仅执行。
- `src/plugins/*`：添加模式注册表 + 限制。
- CLI 命令限制在 `src/cli`。

## 测试

- 未知键拒绝（根级 + 嵌套）。
- 插件缺少模式 → 插件加载被阻止并显示明确错误。
- 配置无效 → 除诊断命令外阻止网关启动。
- 医生干运行自动；`doctor --fix` 写入修正后的配置。