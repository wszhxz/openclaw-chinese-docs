---
title: "Creating Skills"
---
# 创建自定义技能 🛠

OpenClaw 设计为易于扩展。"技能"是向您的助手添加新功能的主要方式。

## 什么是技能？

技能是一个包含 SKILL.md 文件（为 LLM 提供说明和工具定义）的目录，可选地包含一些脚本或资源。

## 步骤说明：您的第一个技能

### 1. 创建目录

技能存放在您的工作区，通常为 `~/.openclaw/workspace/skills/`。创建一个新文件夹用于您的技能：

```bash
mkdir -p ~/.openclaw/workspace/skills/hello-world
```

### 2. 定义 SKILL.md

在该目录中创建一个 SKILL.md 文件。此文件使用 YAML 前置信息块用于元数据，并使用 Markdown 用于说明。

```markdown
---
name: hello_world
description: 一个简单的技能，用于问候。
---

# 你好世界技能

当用户请求问候时，使用 `echo` 工具说出 "来自您的自定义技能的问候！"。
```

### 3. 添加工具（可选）

您可以在前置信息块中定义自定义工具，或指示代理使用现有的系统工具（如 `bash` 或 `browser`）。

### 4. 刷新 OpenClaw

请您的代理执行 "刷新技能" 或重启网关。OpenClaw 将发现新目录并索引 SKILL.md。

## 最佳实践

- **简洁明了**：指导模型执行什么操作，而不是如何成为 AI。
- **安全第一**：如果您的技能使用 `bash`，请确保提示不会从不可信用户输入中注入任意命令。
- **本地测试**：使用 `openclaw agent --message "使用我的新技能"` 进行测试。

## 共享技能

您还可以浏览并贡献技能到 [ClawHub](https://clawhub.com)。