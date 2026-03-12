---
summary: "RPC protocol notes for onboarding wizard and config schema"
read_when: "Changing onboarding wizard steps or config schema endpoints"
title: "Onboarding and Config Protocol"
---
# 入门引导 + 配置协议

目的：在 CLI、macOS 应用和 Web UI 之间共享入门引导与配置界面。

## 组件

- 向导引擎（共享会话 + 提示 + 入门引导状态）。
- CLI 入门引导使用与 UI 客户端相同的向导流程。
- 网关 RPC 暴露向导与配置模式（schema）端点。
- macOS 入门引导采用向导步骤模型。
- Web UI 根据 JSON Schema + UI 提示渲染配置表单。

## 网关 RPC

- `wizard.start` 参数：`{ mode?: "local"|"remote", workspace?: string }`
- `wizard.next` 参数：`{ sessionId, answer?: { stepId, value? } }`
- `wizard.cancel` 参数：`{ sessionId }`
- `wizard.status` 参数：`{ sessionId }`
- `config.schema` 参数：`{}`
- `config.schema.lookup` 参数：`{ path }`
  - `path` 接受标准配置段，以及以斜杠分隔的插件 ID，例如 `plugins.entries.pack/one.config`。

响应结构（shape）

- 向导：`{ sessionId, done, step?, status?, error? }`
- 配置 schema：`{ schema, uiHints, version, generatedAt }`
- 配置 schema 查询：`{ path, schema, hint?, hintPath?, children[] }`

## UI 提示

- `uiHints` 按路径（path）索引；为可选元数据（label / help / group / order / advanced / sensitive / placeholder）。
- 敏感字段渲染为密码输入框；不添加脱敏（redaction）层。
- 不支持的 schema 节点将回退至原始 JSON 编辑器。

## 备注

- 本文档是跟踪入门引导/配置协议重构的唯一位置。