---
summary: "Move (migrate) a OpenClaw install from one machine to another"
read_when:
  - You are moving OpenClaw to a new laptop/server
  - You want to preserve sessions, auth, and channel logins (WhatsApp, etc.)
title: "Migration Guide"
---
# 将 OpenClaw 迁移到新机器

本指南介绍如何将 OpenClaw 网关从一台机器迁移到另一台机器，**无需重新完成初始配置（onboarding）**。

迁移在概念上很简单：

- 复制 **状态目录**（`$OPENCLAW_STATE_DIR`，默认值：`~/.openclaw/`）——其中包含配置、认证信息、会话及通道状态。
- 复制您的 **工作区**（默认为 `~/.openclaw/workspace/`）——其中包含您的智能体文件（记忆、提示词等）。

但实际操作中常因 **配置档案（profiles）**、**权限设置** 和 **不完整复制** 而出错。

## 开始前（您将迁移的内容）

### 1) 确认您的状态目录

大多数安装使用默认路径：

- **状态目录：** `~/.openclaw/`

但若您使用了以下方式，路径可能不同：

- `--profile <name>`（通常变为 `~/.openclaw-<profile>/`）
- `OPENCLAW_STATE_DIR=/some/path`

若不确定，请在 **旧** 机器上运行：

```bash
openclaw status
```

查看输出中是否提及 `OPENCLAW_STATE_DIR` / 配置档案。若您运行了多个网关，请对每个配置档案分别执行该命令。

### 2) 确认您的工作区

常见默认路径包括：

- `~/.openclaw/workspace/`（推荐的工作区路径）
- 您自行创建的自定义文件夹

您的工作区是存放如下文件的位置：`MEMORY.md`、`USER.md` 和 `memory/*.md`。

### 3) 明确您将保留的内容

若您同时复制 **状态目录** 和 **工作区**，则可保留：

- 网关配置（`openclaw.json`）
- 认证配置档案 / API 密钥 / OAuth 令牌
- 会话历史记录 + 智能体状态
- 通道状态（例如 WhatsApp 登录/会话）
- 您的工作区文件（记忆、技能笔记等）

若您仅复制 **工作区**（例如通过 Git），则 **不会** 保留：

- 会话
- 凭据
- 通道登录信息

这些内容均存放在 `$OPENCLAW_STATE_DIR` 下。

## 迁移步骤（推荐）

### 步骤 0 — 创建备份（旧机器）

在 **旧** 机器上，首先停止网关服务，避免复制过程中文件被修改：

```bash
openclaw gateway stop
```

（可选但强烈推荐）将状态目录和工作区打包归档：

```bash
# Adjust paths if you use a profile or custom locations
cd ~
tar -czf openclaw-state.tgz .openclaw

tar -czf openclaw-workspace.tgz .openclaw/workspace
```

若您有多个配置档案/状态目录（例如 `~/.openclaw-main`、`~/.openclaw-work`），请分别归档。

### 步骤 1 — 在新机器上安装 OpenClaw

在 **新** 机器上安装 CLI（如需，同时安装 Node）：

- 参见：[安装](/install)

此阶段，即使初始配置生成了新的 `~/.openclaw/` 也无妨——您将在下一步将其覆盖。

### 步骤 2 — 将状态目录和工作区复制到新机器

请同时复制以下两项：

- `$OPENCLAW_STATE_DIR`（默认为 `~/.openclaw/`）
- 您的工作区（默认为 `~/.openclaw/workspace/`）

常用方法包括：

- 使用 `scp` 解压归档包
- 通过 SSH 使用 `rsync -a` 复制
- 使用外部存储设备

复制完成后，请确认：

- 已包含隐藏目录（例如 `.openclaw/`）
- 文件所属用户与运行网关的用户一致

### 步骤 3 — 运行 Doctor 命令（执行迁移与服务修复）

在 **新** 机器上执行：

```bash
openclaw doctor
```

Doctor 是一个“安全且稳妥”的命令，用于修复服务、应用配置迁移，并对不匹配项发出警告。

随后执行：

```bash
openclaw gateway restart
openclaw status
```

## 常见陷阱（及规避方法）

### 陷阱：配置档案 / 状态目录不匹配

若您在旧网关中使用了配置档案（或 `OPENCLAW_STATE_DIR`），而新网关使用了不同的配置档案，则可能出现以下现象：

- 配置更改未生效
- 通道丢失 / 已退出登录
- 会话历史为空

解决方法：使用您所迁移的 **相同** 配置档案/状态目录启动网关/服务，然后重新运行：

```bash
openclaw doctor
```

### 陷阱：仅复制 `openclaw.json`

仅复制 `openclaw.json` 是不够的。许多服务商将状态数据存放在以下位置：

- `$OPENCLAW_STATE_DIR/credentials/`
- `$OPENCLAW_STATE_DIR/agents/<agentId>/...`

请务必迁移完整的 `$OPENCLAW_STATE_DIR` 文件夹。

### 陷阱：权限 / 所有者设置错误

若您以 root 用户复制，或更换了用户，网关可能无法读取凭据/会话。

解决方法：确保状态目录和工作区的所有者为运行网关的用户。

### 陷阱：在远程模式与本地模式之间迁移

- 若您的 UI（WebUI/TUI）指向一个 **远程** 网关，则会话存储与工作区由远程主机管理。
- 迁移您的笔记本电脑并不会迁移远程网关的状态。

若您处于远程模式，请迁移 **网关主机**。

### 陷阱：备份中包含敏感信息

`$OPENCLAW_STATE_DIR` 包含敏感信息（API 密钥、OAuth 令牌、WhatsApp 凭据）。请将备份视同生产环境密钥进行管理：

- 加密存储
- 避免通过不安全渠道共享
- 若怀疑已泄露，请轮换密钥

## 验证检查清单

在新机器上，请确认：

- `openclaw status` 显示网关正在运行
- 您的通道仍保持连接（例如 WhatsApp 无需重新配对）
- 仪表板可正常打开并显示现有会话
- 您的工作区文件（记忆、配置等）均已存在

## 相关文档

- [Doctor](/gateway/doctor)
- [网关故障排查](/gateway/troubleshooting)
- [OpenClaw 的数据存储位置？](/help/faq#where-does-openclaw-store-its-data)