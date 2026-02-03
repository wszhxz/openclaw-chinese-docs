---
summary: "RPC protocol notes for onboarding wizard and config schema"
read_when: "Changing onboarding wizard steps or config schema endpoints"
title: "Onboarding and Config Protocol"
---
# 引导 + 配置协议

目的：在 CLI、macOS 应用和 Web 界面中共享引导 + 配置界面。

## 组件

- 引导引擎（共享会话 + 提示 + 引导状态）。
- CLI 引导使用与 UI 客户端相同的引导流程。
- 网关 RPC 暴露引导 + 配置模式的接口端点。
- macOS 引导使用引导步骤模型。
- Web 界面从 JSON Schema + UI 提示渲染配置表单。

## 网关 RPC

- `wizard.start` 参数：`{ mode?: "本地"|"远程", workspace?: string }`
- `wizard.next` 参数：`{ sessionId, answer?: { stepId, value? } }`
- `wizard.cancel` 参数：`{ sessionId }`
- `wizard.status` 参数：`{ sessionId }`
- `config.schema` 参数：`{}`

响应格式

- 引导：`{ sessionId, done, step?, status?, error? }`
- 配置模式：`{ schema, uiHints, version, generatedAt }`

## UI 提示

- `uiHints` 按路径键值；可选元数据（标签/帮助/分组/顺序/高级/敏感/占位符）。
- 敏感字段将渲染为密码输入框；无脱敏层。
- 不支持的模式节点将回退到原始 JSON 编辑器。

## 注意事项

- 此文档是跟踪引导/配置协议重构的唯一位置。