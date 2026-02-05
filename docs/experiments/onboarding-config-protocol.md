---
summary: "RPC protocol notes for onboarding wizard and config schema"
read_when: "Changing onboarding wizard steps or config schema endpoints"
title: "Onboarding and Config Protocol"
---
# 入门 + 配置协议

目的：在CLI、macOS应用程序和Web UI之间共享入门 + 配置界面。

## 组件

- 向导引擎（共享会话 + 提示 + 入门状态）。
- CLI入门使用与UI客户端相同的向导流程。
- 网关RPC暴露向导 + 配置模式端点。
- macOS入门使用向导步骤模型。
- Web UI从JSON模式 + UI提示渲染配置表单。

## 网关RPC

- `wizard.start` 参数：`{ mode?: "local"|"remote", workspace?: string }`
- `wizard.next` 参数：`{ sessionId, answer?: { stepId, value? } }`
- `wizard.cancel` 参数：`{ sessionId }`
- `wizard.status` 参数：`{ sessionId }`
- `config.schema` 参数：`{}`

响应（形状）

- 向导：`{ sessionId, done, step?, status?, error? }`
- 配置模式：`{ schema, uiHints, version, generatedAt }`

## UI提示

- `uiHints` 按路径键；可选元数据（标签/帮助/组/顺序/高级/敏感/占位符）。
- 敏感字段渲染为密码输入；无红action层。
- 不支持的模式节点回退到原始JSON编辑器。

## 注意事项

- 本文档是跟踪入门/配置协议重构的唯一位置。