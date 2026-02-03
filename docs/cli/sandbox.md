---
title: Sandbox CLI
summary: "Manage sandbox containers and inspect effective sandbox policy"
read_when: "You are managing sandbox containers or debugging sandbox/tool-policy behavior."
status: active
---
# 沙盒 CLI

管理基于 Docker 的沙盒容器，用于隔离代理执行。

## 概述

OpenClaw 可以在隔离的 Docker 容器中运行代理以确保安全性。`sandbox` 命令帮助您管理这些容器，尤其是在更新或配置更改后。

## 命令

### `openclaw sandbox explain`

检查 **生效的** 沙盒模式/作用域/工作区访问权限、沙盒工具策略以及提升的权限（包含 fix-it 配置键路径）。

```bash
openclaw sandbox explain
openclaw sandbox explain --session agent:main:main
openclaw sandbox explain --agent work
openclaw sandbox explain --json
```

### `open,claw sandbox list`

列出所有沙盒容器及其状态和配置。

```bash
openclaw sandbox list
openclaw sandbox list --browser  # 仅列出浏览器容器
openclaw sandbox list --json     # JSON 输出
```

**输出包括：**

- 容器名称和状态（运行中/已停止）
- Docker 镜像以及是否与配置匹配
- 创建时间（距创建时间的时长）
- 空闲时间（距上次使用的时间）
- 关联的会话/代理

### `openclaw sandbox recreate`

删除沙盒容器以强制使用更新的镜像/配置重新创建。

```bash
openclaw sandbox recreate --all                # 重新创建所有容器
openclaw sandbox recreate --session main       # 指定会话
openclaw sandbox recreate --agent mybot        # 指定代理
openclaw sandbox recreate --browser            # 仅重新创建浏览器容器
openclaw sandbox recreate --all --force        # 跳过确认提示
```

**选项：**

- `--all`: 重新创建所有沙盒容器
- `--session <key>`: 为特定会话重新创建容器
- `--agent <id>`: 为特定代理重新创建容器
- `--browser`: 仅重新创建浏览器容器
- `--force`: 跳过确认提示

**重要：** 当代理下次使用时，容器会自动重新创建。

## 使用场景

### 在更新 Docker 镜像后

```bash
# 拉取新镜像
docker pull openclaw-sandbox:latest
docker tag openclaw-sandbox:latest openclaw-sandbox:bookworm-slim

# 更新配置以使用新镜像
# 编辑配置：agents.defaults.sandbox.docker.image（或 agents.list[].sandbox.docker.image）

# 重新创建容器
openclaw sandbox recreate --all
```

### 在更改沙盒配置后

```bash
# 编辑配置：agents.defaults.sandbox.*（或 agents.list[].sandbox.*）

# 重新创建以应用新配置
openclaw sandbox recreate --all
```

### 在更改 setupCommand 后

```bash
openclaw sandbox recreate --all
# 或仅重新创建一个代理：
openclaw sandbox recreate --agent family
```

### 仅针对特定代理

```bash
# 仅更新特定代理的容器
openclaw sandbox recreate --agent alfred
```

## 为什么需要这个功能？

**问题：** 当您更新沙盒 Docker 镜像或配置时：

- 现有容器会继续使用旧设置运行
- 容器在 24 小时无活动后才会被清理
- 常用代理会无限期保留旧容器

**解决方案：** 使用 `openclaw sandbox recreate` 强制删除旧容器。它们将在下次需要时自动使用当前设置重新创建。

提示：优先使用 `openclaw sandbox recreate` 而不是手动 `docker rm`。它使用网关的容器命名规则，并在作用域/会话键更改时避免匹配错误。

## 配置

沙盒设置位于 `~/.openclaw/openclaw.json` 中的 `agents.defaults.sandbox`（每个代理的覆盖配置位于 `agents.list[].sandbox`）：

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
          // ... 更多 Docker 选项
        },
        "prune": {
          "idleHours": 24, // 空闲 24 小时后自动清理
          "maxAgeDays": 7, // 7 天后自动清理
        },
      },
    },
  },
}
```

## 参见

- [沙盒文档](/gateway/sandboxing)
- [代理配置](/concepts/agent-workspace)
- [Doctor 命令](/gateway/doctor) - 检查沙盒设置