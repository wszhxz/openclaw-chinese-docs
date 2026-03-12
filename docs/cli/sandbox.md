---
title: Sandbox CLI
summary: "Manage sandbox containers and inspect effective sandbox policy"
read_when: "You are managing sandbox containers or debugging sandbox/tool-policy behavior."
status: active
---
# 沙箱 CLI

管理基于 Docker 的沙箱容器，以实现代理（agent）的隔离执行。

## 概述

OpenClaw 可在隔离的 Docker 容器中运行代理，以提升安全性。`sandbox` 命令可帮助您管理这些容器，尤其是在更新或配置变更之后。

## 命令

### `openclaw sandbox explain`

检查**实际生效的**沙箱模式 / 作用域 / 工作区访问权限、沙箱工具策略以及提权闸门（含可修复配置项的键路径）。

```bash
openclaw sandbox explain
openclaw sandbox explain --session agent:main:main
openclaw sandbox explain --agent work
openclaw sandbox explain --json
```

### `openclaw sandbox list`

列出所有沙箱容器及其状态与配置。

```bash
openclaw sandbox list
openclaw sandbox list --browser  # List only browser containers
openclaw sandbox list --json     # JSON output
```

**输出包含：**

- 容器名称与状态（运行中 / 已停止）
- Docker 镜像及是否与当前配置匹配
- 容器年龄（自创建以来的时间）
- 空闲时间（距上次使用的时间）
- 关联的会话（session）/ 代理（agent）

### `openclaw sandbox recreate`

移除沙箱容器，强制使用更新后的镜像/配置重新创建。

```bash
openclaw sandbox recreate --all                # Recreate all containers
openclaw sandbox recreate --session main       # Specific session
openclaw sandbox recreate --agent mybot        # Specific agent
openclaw sandbox recreate --browser            # Only browser containers
openclaw sandbox recreate --all --force        # Skip confirmation
```

**选项：**

- `--all`：重新创建所有沙箱容器  
- `--session <key>`：为指定会话重新创建容器  
- `--agent <id>`：为指定代理重新创建容器  
- `--browser`：仅重新创建浏览器容器  
- `--force`：跳过确认提示  

**重要提示：** 当代理下次被调用时，容器将自动重新创建。

## 使用场景

### 更新 Docker 镜像后

```bash
# Pull new image
docker pull openclaw-sandbox:latest
docker tag openclaw-sandbox:latest openclaw-sandbox:bookworm-slim

# Update config to use new image
# Edit config: agents.defaults.sandbox.docker.image (or agents.list[].sandbox.docker.image)

# Recreate containers
openclaw sandbox recreate --all
```

### 修改沙箱配置后

```bash
# Edit config: agents.defaults.sandbox.* (or agents.list[].sandbox.*)

# Recreate to apply new config
openclaw sandbox recreate --all
```

### 修改 `setupCommand` 后

```bash
openclaw sandbox recreate --all
# or just one agent:
openclaw sandbox recreate --agent family
```

### 仅为特定代理执行

```bash
# Update only one agent's containers
openclaw sandbox recreate --agent alfred
```

## 为何需要此功能？

**问题：** 当您更新沙箱 Docker 镜像或配置时：

- 已存在的容器仍以旧设置持续运行  
- 容器仅在闲置满 24 小时后才会被清理  
- 频繁使用的代理会使旧容器无限期持续运行  

**解决方案：** 使用 `openclaw sandbox recreate` 强制移除旧容器。它们将在下次需要时，自动以当前配置重新创建。

提示：建议优先使用 `openclaw sandbox recreate`，而非手动执行 `docker rm`。前者利用网关（Gateway）的容器命名机制，可避免因作用域（scope）/会话（session）键变更导致的命名不一致问题。

## 配置

沙箱设置位于 `~/.openclaw/openclaw.json` 中的 `agents.defaults.sandbox` 下（按代理覆盖的配置置于 `agents.list[].sandbox` 中）：

```jsonc
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "all", // off, non-main, all
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
```

## 参阅

- [沙箱文档](/gateway/sandboxing)  
- [代理配置](/concepts/agent-workspace)  
- [Doctor 命令](/gateway/doctor) — 检查沙箱配置状态