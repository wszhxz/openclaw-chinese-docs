---
title: Sandbox CLI
summary: "Manage sandbox runtimes and inspect effective sandbox policy"
read_when: "You are managing sandbox runtimes or debugging sandbox/tool-policy behavior."
status: active
---
# Sandbox CLI

管理用于隔离智能体执行的沙盒运行时。

## 概述

OpenClaw 可以在隔离的沙盒运行时中运行智能体以确保安全。``sandbox`` 命令可帮助您在更新或配置更改后检查并重建这些运行时。

目前通常指：

- Docker 沙盒容器
- 当 ``agents.defaults.sandbox.backend = "ssh"`` 时的 SSH 沙盒运行时
- 当 ``agents.defaults.sandbox.backend = "openshell"`` 时的 OpenShell 沙盒运行时

对于 ``ssh`` 和 OpenShell ``remote``，重建比 Docker 更重要：

- 初始种子后，远程工作区是标准的
- ``openclaw sandbox recreate`` 删除所选范围的标准远程工作区
- 下次使用时会从当前本地工作区再次初始化它

## 命令

### ``openclaw sandbox explain``

检查**有效**的沙盒模式/范围/工作区访问权限、沙盒工具策略以及提升的门控（含修复配置键路径）。

````bash
openclaw sandbox explain
openclaw sandbox explain --session agent:main:main
openclaw sandbox explain --agent work
openclaw sandbox explain --json
````

### ``openclaw sandbox list``

列出所有沙盒运行时及其状态和配置。

````bash
openclaw sandbox list
openclaw sandbox list --browser  # List only browser containers
openclaw sandbox list --json     # JSON output
````

**输出包含：**

- 运行时名称和状态
- 后端 (``docker``, ``openshell`` 等)
- 配置标签及其是否与当前配置匹配
- 存在时长（自创建以来的时间）
- 空闲时间（距上次使用的时间）
- 关联的会话/智能体

### ``openclaw sandbox recreate``

移除沙盒运行时以强制使用更新的配置进行重建。

````bash
openclaw sandbox recreate --all                # Recreate all containers
openclaw sandbox recreate --session main       # Specific session
openclaw sandbox recreate --agent mybot        # Specific agent
openclaw sandbox recreate --browser            # Only browser containers
openclaw sandbox recreate --all --force        # Skip confirmation
````

**选项：**

- ``--all``: 重建所有沙盒容器
- ``--session <key>``: 为特定会话重建容器
- ``--agent <id>``: 为特定智能体重建容器
- ``--browser``: 仅重建浏览器容器
- ``--force``: 跳过确认提示

**重要：** 当下次使用该智能体时，运行时会自动重建。

## 使用场景

### 更新 Docker 镜像后

````bash
# Pull new image
docker pull openclaw-sandbox:latest
docker tag openclaw-sandbox:latest openclaw-sandbox:bookworm-slim

# Update config to use new image
# Edit config: agents.defaults.sandbox.docker.image (or agents.list[].sandbox.docker.image)

# Recreate containers
openclaw sandbox recreate --all
````

### 更改沙盒配置后

````bash
# Edit config: agents.defaults.sandbox.* (or agents.list[].sandbox.*)

# Recreate to apply new config
openclaw sandbox recreate --all
````

### 更改 SSH 目标或 SSH 认证材料后

````bash
# Edit config:
# - agents.defaults.sandbox.backend
# - agents.defaults.sandbox.ssh.target
# - agents.defaults.sandbox.ssh.workspaceRoot
# - agents.defaults.sandbox.ssh.identityFile / certificateFile / knownHostsFile
# - agents.defaults.sandbox.ssh.identityData / certificateData / knownHostsData

openclaw sandbox recreate --all
````

对于核心 ``ssh`` 后端，重建会删除 SSH 目标上的每范围远程工作区根目录。下次运行时会从本地工作区再次初始化它。

### 更改 OpenShell 源、策略或模式后

````bash
# Edit config:
# - agents.defaults.sandbox.backend
# - plugins.entries.openshell.config.from
# - plugins.entries.openshell.config.mode
# - plugins.entries.openshell.config.policy

openclaw sandbox recreate --all
````

对于 OpenShell ``remote`` 模式，重建会删除该范围的标准远程工作区。下次运行时会从本地工作区再次初始化它。

### 更改 setupCommand 后

````bash
openclaw sandbox recreate --all
# or just one agent:
openclaw sandbox recreate --agent family
````

### 仅针对特定智能体

````bash
# Update only one agent's containers
openclaw sandbox recreate --agent alfred
````

## 为什么需要此功能？

**问题：** 当您更新沙盒配置时：

- 现有运行时继续使用旧设置运行
- 仅在 24 小时不活动后才会清理运行时
- 定期使用的智能体会无限期地保持旧运行时存活

**解决方案：** 使用 ``openclaw sandbox recreate`` 强制移除旧运行时。当下次需要时，它们将使用当前设置自动重建。

提示：优先使用 ``openclaw sandbox recreate`` 而非手动后端特定清理。它使用网关的运行时注册表，并在范围/会话密钥更改时避免不匹配。

## 配置

沙盒设置位于 ``~/.openclaw/openclaw.json`` 下的 ``agents.defaults.sandbox`` 中（每个智能体的覆盖项位于 ``agents.list[].sandbox`` 中）：

````jsonc
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "all", // off, non-main, all
        "backend": "docker", // docker, ssh, openshell
        "scope": "agent", // session, agent, shared
        "docker": {
          "image": "openclaw-sandbox:bookworm-slim",
          "containerPrefix": "openclaw-sbx-",
          // ... more Docker options
        },
        "prune": {
          "idleHours": 24, // Auto-prune after 24h idle
          "maxAgeDays": 7, // Auto-prune after 7 days
        },
      },
    },
  },
}
````

## 参见

- [沙盒文档](/gateway/sandboxing)
- [智能体配置](/concepts/agent-workspace)
- [诊断命令](/gateway/doctor) - 检查沙盒设置