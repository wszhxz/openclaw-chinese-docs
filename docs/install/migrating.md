---
summary: "Move (migrate) a OpenClaw install from one machine to another"
read_when:
  - You are moving OpenClaw to a new laptop/server
  - You want to preserve sessions, auth, and channel logins (WhatsApp, etc.)
title: "Migration Guide"
---
# 将 OpenClaw 迁移到新机器

本指南将 OpenClaw 网关从一台机器迁移到另一台机器，**无需重新进行首次接入**。

迁移在概念上很简单：

- 复制 **状态目录**（`$OPENCLAW_STATE_DIR`，默认：`~/.openclaw/`）—— 包括配置、认证、会话和频道状态。
- 复制您的 **工作区**（默认：`~/.openclaw/workspace/`）—— 包括您的代理文件（记忆、提示等）。

但存在一些常见的陷阱，涉及 **配置文件**、**权限** 和 **部分复制**。

## 开始前（您要迁移的内容）

### 1) 确认您的状态目录

大多数安装使用默认路径：

- **状态目录**：`~/.openclaw/`

但如果您使用了以下选项，路径可能不同：

- `--profile <name>`（通常变为 `~/.openclaw-<profile>/`）
- `OPENCLAW_STATE_DIR=/some/path`

如果您不确定，可以在 **旧机器** 上运行以下命令：

```bash
openclaw status
```

查找输出中提到的 `OPENCLAW_STATE_DIR` / 配置文件。如果您运行了多个网关，请为每个配置文件重复此步骤。

### 2) 确认您的工作区

常见默认路径：

- `~/.openclaw/workspace/`（推荐的工作区）
- 您自定义的文件夹

您的工作区是存放 `MEMORY.md`、`USER.md` 和 `memory/*.md` 等文件的位置。

### 3) 理解您将保留的内容

如果您复制了 **状态目录和工作区**，您将保留：

- 网关配置（`openclaw.json`）
- 认证配置文件 / API 密钥 / OAuth 令牌
- 会话历史 + 代理状态
- 频道状态（例如 WhatsApp 登录/会话）
- 您的工作区文件（记忆、技能笔记等）

如果您仅复制 **工作区**（例如通过 Git），您将 **不保留**：

- 会话
- 凭据
- 频道登录信息

这些信息存储在 `$OPENCLAW_STATE_DIR` 中。

## 迁移步骤（推荐）

### 步骤 0 — 备份（旧机器）

在 **旧机器** 上，首先停止网关以防止复制过程中文件发生变化：

```bash
openclaw gateway stop
```

（可选但推荐）归档状态目录和工作区：

```bash
# 如果您使用了配置文件或自定义路径，请调整路径
cd ~
tar -czf openclaw-state.tgz .openclaw

tar -czf openclaw-workspace.tgz .openclaw/workspace
```

如果您有多个配置文件/状态目录（例如 `~/.openclaw-main`、`~/.openclaw-work`），请分别归档。

### 步骤 1 — 在新机器上安装 OpenClaw

在 **新机器** 上安装 CLI（如需 Node.js 也一并安装）：

- 参见：[安装](/install)

此时，如果首次接入创建了新的 `~/.openclaw/` 是可以接受的，您将在下一步覆盖它。

### 步骤 2 — 将状态目录 + 工作区复制到新机器

复制 **两者**：

- `$OPENCLAW_STATE_DIR`（默认 `~/.openclaw/`）
- 您的工作区（默认 `~/.openclaw/workspace/`）

常见方法：

- 使用 `scp` 传输压缩包并解压
- 通过 SSH 使用 `rsync -a`
- 使用外部硬盘

复制完成后，请确保：

- 隐藏目录已被包含（例如 `.openclaw/`）
- 文件的所有权与运行网关的用户一致

### 步骤 3 — 运行 Doctor（迁移 + 服务修复）

在 **新机器** 上运行：

```bash
openclaw doctor
```

Doctor 是“安全且无趣”的命令。它会修复服务、应用配置迁移并警告不匹配项。

然后运行：

```bash
openclaw gateway restart
openclaw status
```

## 常见陷阱（及如何避免）

### 陷阱：配置文件 / 状态目录不匹配

如果您在旧网关上使用了配置文件（或 `OPENCLAW_STATE_DIR`），而新网关使用了不同的配置文件/状态目录，您将看到以下症状：

- 配置更改未生效
- 频道缺失 / 已登出
- 会话历史为空

解决方法：使用您迁移的 **相同配置文件/状态目录** 运行网关/服务，然后重新运行：

```bash
openclaw doctor
```

### 陷阱：仅复制 `openclaw.json`

`openclaw.json` 不足以保存所有数据。许多服务提供商将状态存储在：

- `$OPENCLAW_STATE_DIR/credentials/`
- `$OPENCLAW_STATE_DIR/agents/<agentId>/...`

始终迁移整个 `$OPENCLAW_STATE_DIR` 文件夹。

### 陷阱：权限 / 所有者问题

如果您以 root 用户或更改了用户身份进行复制，网关可能无法读取凭据/会话。

解决方法：确保状态目录和工作区由运行网关的用户拥有。

### 陷阱：在远程/本地模式之间迁移

- 如果您的 UI（WebUI/TUI）指向 **远程** 网关，远程主机拥有会话存储 + 工作区。
- 将您的笔记本电脑迁移到新机器不会移动远程网关的状态。

如果您处于远程模式，请迁移 **网关主机**。

### 陷阱：备份中的敏感信息

`$OPENCLAW_STATE_DIR` 包含敏感信息（API 密钥、OAuth 令牌、WhatsApp 凭据）。请像处理生产环境敏感信息一样处理备份：

- 加密存储
- 避免通过不安全渠道共享
- 如果怀疑泄露，请轮换密钥

## 验证检查清单

在新机器上确认以下内容：

- `openclaw status` 显示网关正在运行
- 您的频道仍连接（例如 WhatsApp 不需要重新配对）
- 仪表盘打开并显示现有会话
- 您的工作区文件（记忆、配置）存在

## 相关内容

- [Doctor](/gateway/doctor)
- [网关故障排除](/gateway/troubleshooting)
- [OpenClaw 存储数据的位置](/help/