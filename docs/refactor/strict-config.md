---
summary: "Strict config validation + doctor-only migrations"
read_when:
  - Designing or implementing config validation behavior
  - Working on config migrations or doctor workflows
  - Handling plugin config schemas or plugin load gating
title: "Strict Config Validation"
---
# 严格的配置验证（仅医生迁移）

## 目标

- **在所有位置拒绝未知的配置键**（根 + 嵌套），除了根 `$schema` 元数据。
- **拒绝没有模式的插件配置**；不要加载该插件。
- **移除加载时的遗留自动迁移**；迁移仅通过医生运行。
- **启动时自动运行医生（干运行）**；如果无效，阻止非诊断命令。

## 非目标

- 加载时的向后兼容性（遗留键不会自动迁移）。
- 对未识别键的静默丢弃。

## 严格的验证规则

- 配置必须在每个级别完全匹配模式。
- 未知键是验证错误（根或嵌套中不允许透传），除非根 `$schema` 是字符串。
- `plugins.entries.<id>.config` 必须由插件的模式进行验证。
  - 如果插件缺少模式，**拒绝插件加载**并显示清晰的错误。
- 除非插件清单声明了通道ID，否则未知的 `channels.<id>` 键是错误。
- 所有插件都需要插件清单 (`openclaw.plugin.json`)。

## 插件模式强制执行

- 每个插件为其配置提供一个严格的JSON模式（清单中内联）。
- 插件加载流程：
  1. 解析插件清单 + 模式 (`openclaw.plugin.json`)。
  2. 将配置与模式进行验证。
  3. 如果缺少模式或配置无效：阻止插件加载，记录错误。
- 错误消息包括：
  - 插件ID
  - 原因（缺少模式 / 配置无效）
  - 验证失败的路径
- 禁用的插件保留其配置，但医生 + 日志会显示警告。

## 医生流程

- 医生每次加载配置时都会运行（默认为干运行）。
- 如果配置无效：
  - 打印摘要 + 可操作的错误。
  - 指令：`openclaw doctor --fix`。
- `openclaw doctor --fix`：
  - 应用迁移。
  - 移除未知键。
  - 写入更新后的配置。

## 命令门控（当配置无效时）

允许（仅诊断）：

- `openclaw doctor`
- `openclaw logs`
- `openclaw health`
- `openclaw help`
- `openclaw status`
- `openclaw gateway status`

其他所有内容必须硬失败并显示：“配置无效。运行 `openclaw doctor --fix`。”

## 错误用户体验格式

- 单个摘要标题。
- 分组部分：
  - 未知键（完整路径）
  - 遗留键 / 需要迁移
  - 插件加载失败（插件ID + 原因 + 路径）

## 实现触点

- `src/config/zod-schema.ts`：移除根透传；所有地方使用严格的对象。
- `src/config/zod-schema.providers.ts`：确保严格的通道模式。
- `src/config/validation.ts`：对未知键失败；不应用遗留迁移。
- `src/config/io.ts`：移除遗留自动迁移；始终运行医生干运行。
- `src/config/legacy*.ts`：将使用移动到仅医生。
- `src/plugins/*`：添加模式注册表 + 门控。
- `src/cli` 中的CLI命令门控。

## 测试

- 拒绝未知键（根 + 嵌套）。
- 插件缺少模式 → 插件加载被阻止并显示清晰的错误。
- 配置无效 → 网关启动被阻止，除非是诊断命令。
- 医生干运行自动；`doctor --fix` 写入修正后的配置。