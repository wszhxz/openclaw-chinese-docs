---
title: "Creating Skills"
summary: "Build and test custom workspace skills with SKILL.md"
read_when:
  - You are creating a new custom skill in your workspace
  - You need a quick starter workflow for SKILL.md-based skills
---
# 创建自定义技能 🛠

OpenClaw 设计为易于扩展。“技能”是向您的助手添加新功能的主要方式。

## 什么是技能？

技能是一个包含 `SKILL.md` 文件（该文件为LLM提供指令和工具定义）的目录，还可以选择性地包含一些脚本或资源。

## 分步指南：您的第一个技能

### 1. 创建目录

技能位于您的工作空间中，通常是 `~/.openclaw/workspace/skills/`。为您的技能创建一个新的文件夹：

```bash
mkdir -p ~/.openclaw/workspace/skills/hello-world
```

### 2. 定义 `SKILL.md`

在该目录中创建一个 `SKILL.md` 文件。此文件使用YAML前导内容作为元数据，并使用Markdown编写指令。

```markdown
---
name: hello_world
description: A simple skill that says hello.
---

# Hello World Skill

When the user asks for a greeting, use the `echo` tool to say "Hello from your custom skill!".
```

### 3. 添加工具（可选）

您可以在前导内容中定义自定义工具，或者指示代理使用现有的系统工具（如 `bash` 或 `browser`）。

### 4. 刷新 OpenClaw

要求您的代理“刷新技能”或重启网关。OpenClaw 将发现新的目录并索引 `SKILL.md`。

## 最佳实践

- **简洁明了**：指导模型做什么，而不是如何成为一个AI。
- **安全第一**：如果您的技能使用 `bash`，请确保提示不允许从不受信任的用户输入中注入任意命令。
- **本地测试**：使用 `openclaw agent --message "use my new skill"` 进行测试。

## 共享技能

您还可以浏览并向 [ClawHub](https://clawhub.com) 贡献技能。