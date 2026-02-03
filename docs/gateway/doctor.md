---
summary: "Doctor command: health checks, config migrations, and repair steps"
read_when:
  - Adding or modifying doctor migrations
  - Introducing breaking config changes
title: "Doctor"
---
# 医生

`openclaw doctor` 是 OpenClaw 的修复 + 迁移工具。它修复过期的配置/状态，检查健康状况，并提供可操作的修复步骤。

## 快速入门

```bash
openclaw doctor
```

### 无头 / 自动化

```bash
openclaw doctor --yes
```

接受默认值而不进行提示（包括在适用时接受重启/服务/沙箱修复步骤）。

```bash
openclaw doctor --repair
```

应用推荐的修复操作而不进行提示（在安全的情况下进行修复和重启）。

```bash
openclaw doctor --repair --force
```

应用激进的修复操作（覆盖自定义的监督配置）。

```bash
openclaw doctor --non-interactive
```

不进行提示，仅应用安全的迁移（配置规范化 + 磁盘状态迁移）。跳过需要人工确认的重启/服务/沙箱操作。检测到旧状态迁移时会自动运行。

```bash
openclaw doctor --deep
```

扫描系统服务以查找额外的网关安装（launchd/systemd/schtasks）。

如果你想在写入前审查更改，请先打开配置文件：

```bash
cat ~/.openclaw/openclaw.json
```

## 功能概述

- 可选的预飞行更新（仅适用于 Git 安装，交互式）。
- UI 协议新鲜度检查（当协议模式更新时重建控制 UI）。
- 健康检查 + 重启提示。
- 技能状态摘要（合格/缺失/被阻止）。
- 旧配置值的规范化。
- OpenCode Zen 提供者覆盖警告（`models.providers.opencode`）。
- 旧磁盘状态迁移（会话/代理目录/WhatsApp 认证）。
- 状态完整性及权限检查（会话、转录、状态目录）。
- 本地运行时配置文件权限检查（chmod 600）。
- 模型认证健康检查：检查 OAuth 过期、可刷新过期令牌，并报告认证配置文件冷却/禁用状态。
- 额外的工作区目录检测（`~/openclaw`）。
- 启用沙箱时的沙箱镜像修复。
- 旧服务迁移和额外网关检测。
- 网关运行时检查（服务已安装但未运行；缓存的 launchd 标签）。
- 渠道状态警告（从运行中的网关探测）。
- 监督配置审计（launchd/systemd/schtasks）并可选修复。
- 网关运行时最佳实践检查（Node vs Bun、版本管理器路径）。
- 网关端口冲突诊断（默认 `18789`）。
- 开放 DM 策略的安全警告。
- 当未设置 `gateway.auth.token` 时的网关认证警告（本地模式；提供令牌生成）。
- Linux 上的 systemd linger 检查。
- 源安装检查（pnpm 工作区不匹配、缺少 UI 资产、缺少 tsx 二进制文件）。
- 写入更新的配置 + 向导元数据。

## 详细行为和理由

### 0) 可选更新（Git 安装）

如果这是 Git 检出且 doctor 以交互方式运行，它会提供更新（获取/变基/构建）后再运行 doctor。

### 1) 配置规范化

如果配置包含旧值格式（例如 `messages.ackReaction` 没有特定通道覆盖），doctor 会将其规范化为当前模式。

### 2) 旧配置键迁移

当配置包含已弃用的键时，其他命令将拒绝运行并提示你运行 `openclaw doctor`。

Doctor 会：

- 解释找到哪些旧键。
- 显示应用的迁移。
- 用更新后的模式重写 `~/.openclaw/openclaw.json`。

网关在启动时检测到旧配置格式时也会自动运行 doctor 迁移，因此过期配置会自动修复，无需手动干预。

当前迁移：

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → 顶层 `bindings`
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- `routing.agentToAgent` → `tools.agentToAgent`
- `routing.transcribeAudio` → `tools.transcribeAudio`
- `routing.defaultAgentId` → `agents.list[].default`

### 3) 旧状态迁移

当检测到旧状态迁移时，会自动运行。

### 4) 配置写入 + 向导元数据

Doctor 持久化任何配置更改，并标记向导元数据以记录 doctor 运行。

### 5) 工作区提示（备份 + 内存系统）

Doctor 在缺失时建议工作区内存系统，并在工作区未在 Git 下时打印备份提示。

查看 [/concepts/agent-workspace](/concepts/agent-workspace) 以获取完整的工作区结构和 Git 备份指南（推荐私有 GitHub 或 GitLab）。