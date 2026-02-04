---
summary: "Move (migrate) a OpenClaw install from one machine to another"
read_when:
  - You are moving OpenClaw to a new laptop/server
  - You want to preserve sessions, auth, and channel logins (WhatsApp, etc.)
title: "Migration Guide"
---
# 将 OpenClaw 迁移到新机器

本指南将 OpenClaw 网关从一台机器迁移到另一台 **而不重新进行入站设置**。

迁移的概念很简单：

- 复制 **状态目录** (`$OPENCLAW_STATE_DIR`，默认：`~/.openclaw/`) — 这包括配置、认证、会话和通道状态。
- 复制你的 **工作区** (`~/.openclaw/workspace/` 默认) — 这包括你的代理文件（内存、提示等）。

但在 **配置文件**、**权限** 和 **部分复制** 方面存在一些常见的陷阱。

## 开始之前（你要迁移的内容）

### 1) 确定你的状态目录

大多数安装使用默认值：

- **状态目录:** `~/.openclaw/`

但如果你使用了：

- `--profile <name>`（通常变为 `~/.openclaw-<profile>/`）
- `OPENCLAW_STATE_DIR=/some/path`

如果你不确定，在 **旧** 机器上运行：

```bash
openclaw status
```

查找输出中的 `OPENCLAW_STATE_DIR` / 配置文件提及。如果你运行多个网关，请对每个配置文件重复此操作。

### 2) 确定你的工作区

常见的默认值：

- `~/.openclaw/workspace/`（推荐的工作区）
- 你创建的自定义文件夹

你的工作区是 `MEMORY.md`、`USER.md` 和 `memory/*.md` 等文件所在的位置。

### 3) 理解你要保留的内容

如果你同时复制了 **状态目录** 和 **工作区**，你将保留：

- 网关配置 (`openclaw.json`)
- 认证配置文件 / API 密钥 / OAuth 令牌
- 会话历史 + 代理状态
- 通道状态（例如 WhatsApp 登录/会话）
- 你的工作区文件（内存、技能笔记等）

如果你只复制了 **工作区**（例如通过 Git），你将 **不** 保留：

- 会话
- 凭据
- 通道登录

这些位于 `$OPENCLAW_STATE_DIR` 下。

## 迁移步骤（推荐）

### 第0步 — 备份（旧机器）

在 **旧** 机器上，首先停止网关以防止文件在复制过程中更改：

```bash
openclaw gateway stop
```

（可选但推荐）归档状态目录和工作区：

```bash
# Adjust paths if you use a profile or custom locations
cd ~
tar -czf openclaw-state.tgz .openclaw

tar -czf openclaw-workspace.tgz .openclaw/workspace
```

如果你有多个配置文件/状态目录（例如 `~/.openclaw-main`，`~/.openclaw-work`），请分别归档每个。

### 第1步 — 在新机器上安装 OpenClaw

在 **新** 机器上，安装 CLI（如果需要 Node 也一并安装）：

- 参见：[安装](/install)

在这个阶段，如果入站设置创建了一个新的 `~/.openclaw/` 是可以的 — 你将在下一步覆盖它。

### 第2步 — 将状态目录 + 工作区复制到新机器

复制 **两者**：

- `$OPENCLAW_STATE_DIR`（默认 `~/.openclaw/`）
- 你的工作区（默认 `~/.openclaw/workspace/`）

常见的方法：

- 使用 `scp` 归档并提取
- 通过 SSH `rsync -a`
- 外部驱动器

复制后，请确保：

- 包含隐藏目录（例如 `.openclaw/`）
- 文件所有权正确，对应于运行网关的用户

### 第3步 — 运行 Doctor（迁移 + 服务修复）

在 **新** 机器上：

```bash
openclaw doctor
```

Doctor 是“安全无趣”的命令。它修复服务，应用配置迁移，并警告不匹配的情况。

然后：

```bash
openclaw gateway restart
openclaw status
```

## 常见陷阱（以及如何避免它们）

### 陷阱：配置文件 / 状态目录不匹配

如果你使用配置文件（或 `OPENCLAW_STATE_DIR`）运行旧网关，而新网关使用不同的配置文件，你会看到如下症状：

- 配置更改未生效
- 通道缺失 / 已注销
- 会话历史为空

解决方法：使用与迁移相同的 **配置文件/状态目录** 运行网关/服务，然后重新运行：

```bash
openclaw doctor
```

### 陷阱：仅复制 `openclaw.json`

仅复制 `openclaw.json` 是不够的。许多提供商的状态存储在：

- `$OPENCLAW_STATE_DIR/credentials/`
- `$OPENCLAW_STATE_DIR/agents/<agentId>/...`

始终迁移整个 `$OPENCLAW_STATE_DIR` 文件夹。

### 陷阱：权限 / 所有权

如果你以 root 用户复制或更改了用户，网关可能会无法读取凭据/会话。

解决方法：确保状态目录 + 工作区由运行网关的用户拥有。

### 陷阱：在远程/本地模式之间迁移

- 如果你的 UI（WebUI/TUI）指向一个 **远程** 网关，远程主机拥有会话存储 + 工作区。
- 迁移笔记本电脑不会移动远程网关的状态。

如果你处于远程模式，请迁移 **网关主机**。

### 陷阱：备份中的密钥

`$OPENCLAW_STATE_DIR` 包含密钥（API 密钥、OAuth 令牌、WhatsApp 凭据）。将备份视为生产密钥：

- 存储加密
- 避免通过不安全渠道共享
- 如果怀疑泄露，请轮换密钥

## 验证检查清单

在新机器上确认：

- `openclaw status` 显示网关正在运行
- 你的通道仍然连接（例如 WhatsApp 不需要重新配对）
- 仪表板打开并显示现有会话
- 你的工作区文件（内存、配置）存在

## 相关

- [Doctor](/gateway/doctor)
- [网关故障排除](/gateway/troubleshooting)
- [OpenClaw 存储数据的位置？](/help/faq#where-does-openclaw-store-its-data)