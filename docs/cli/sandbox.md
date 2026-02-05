---
title: Sandbox CLI
summary: "Manage sandbox containers and inspect effective sandbox policy"
read_when: "You are managing sandbox containers or debugging sandbox/tool-policy behavior."
status: active
---
# Sandbox CLI

管理基于Docker的沙箱容器以实现隔离代理执行。

## 概述

OpenClaw可以在隔离的Docker容器中运行代理以确保安全。`sandbox` 命令可以帮助您管理这些容器，特别是在更新或配置更改之后。

## 命令

### `openclaw sandbox explain`

检查**有效**的沙箱模式/范围/工作区访问、沙箱工具策略以及提升门（带有修复配置键路径）。

```bash
openclaw sandbox explain
openclaw sandbox explain --session agent:main:main
openclaw sandbox explain --agent work
openclaw sandbox explain --json
```

### `openclaw sandbox list`

列出所有沙箱容器及其状态和配置。

```bash
openclaw sandbox list
openclaw sandbox list --browser  # List only browser containers
openclaw sandbox list --json     # JSON output
```

**输出包括：**

- 容器名称和状态（正在运行/已停止）
- Docker镜像及其是否与配置匹配
- 年龄（自创建以来的时间）
- 空闲时间（自上次使用以来的时间）
- 关联的会话/代理

### `openclaw sandbox recreate`

删除沙箱容器以强制使用更新的镜像/配置重新创建。

```bash
openclaw sandbox recreate --all                # Recreate all containers
openclaw sandbox recreate --session main       # Specific session
openclaw sandbox recreate --agent mybot        # Specific agent
openclaw sandbox recreate --browser            # Only browser containers
openclaw sandbox recreate --all --force        # Skip confirmation
```

**选项：**

- `--all`: 重新创建所有沙箱容器
- `--session <key>`: 重新创建特定会话的容器
- `--agent <id>`: 重新创建特定代理的容器
- `--browser`: 仅重新创建浏览器容器
- `--force`: 跳过确认提示

**重要：** 当代理下次使用时，容器会自动重新创建。

## 使用场景

### 更新Docker镜像后

```bash
# Pull new image
docker pull openclaw-sandbox:latest
docker tag openclaw-sandbox:latest openclaw-sandbox:bookworm-slim

# Update config to use new image
# Edit config: agents.defaults.sandbox.docker.image (or agents.list[].sandbox.docker.image)

# Recreate containers
openclaw sandbox recreate --all
```

### 更改沙箱配置后

```bash
# Edit config: agents.defaults.sandbox.* (or agents.list[].sandbox.*)

# Recreate to apply new config
openclaw sandbox recreate --all
```

### 更改setupCommand后

```bash
openclaw sandbox recreate --all
# or just one agent:
openclaw sandbox recreate --agent family
```

### 仅针对特定代理

```bash
# Update only one agent's containers
openclaw sandbox recreate --agent alfred
```

## 为什么需要这个？

**问题：** 当您更新沙箱Docker镜像或配置时：

- 现有容器继续使用旧设置运行
- 容器仅在24小时不活动后被清理
- 经常使用的代理会无限期地保留旧容器

**解决方案：** 使用 `openclaw sandbox recreate` 强制删除旧容器。当下次需要时，它们将自动使用当前设置重新创建。

提示：优先使用 `openclaw sandbox recreate` 而不是手动 `docker rm`。它使用网关的容器命名，并避免在范围/会话键更改时出现不匹配。

## 配置

沙箱设置位于 `~/.openclaw/openclaw.json` 下的 `agents.defaults.sandbox` 中（每个代理的覆盖设置位于 `agents.list[].sandbox` 中）：

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

## 参见

- [沙箱文档](/gateway/sandboxing)
- [代理配置](/concepts/agent-workspace)
- [Doctor命令](/gateway/doctor) - 检查沙箱设置