---
summary: "CLI reference for `openclaw agents` (list/add/delete/set identity)"
read_when:
  - You want multiple isolated agents (workspaces + routing + auth)
title: "agents"
---
# `openclaw 代理`

管理隔离的代理（工作区 + 认证 + 路由）。

相关：

- 多代理路由：[多代理路由](/concepts/multi-agent)
- 代理工作区：[代理工作区](/concepts/agent-workspace)

## 示例

```bash
openclaw 代理 列表
openclaw 代理 添加 工作 --工作区 ~/.openclaw/workspace-work
openclaw 代理 设置-身份 --工作区 ~/.openclaw/workspace --从身份
openclaw 代理 设置-身份 --代理 main --头像 avatars/openclaw.png
openclaw 代理 删除 工作
```

## 身份文件

每个代理工作区可以在工作区根目录包含一个 `IDENTITY.md` 文件：

- 示例路径：`~/.openclaw/workspace/IDENTITY.md`
- `设置-身份 --从身份` 从工作区根目录读取（或显式指定 `--identity-file`）

头像路径相对于工作区根目录解析。

## 设置身份

`设置-身份` 将字段写入 `agents.list[].identity`：

- `名称`
- `主题`
- `表情符号`
- `头像`（工作区相对路径、http(s) URL 或数据 URI）

从 `IDENTITY.md` 加载：

```bash
openclaw 代理 设置-身份 --工作区 ~/.openclaw/workspace --从身份
```

显式覆盖字段：

```bash
openclaw 代理 设置-身份 --代理 main --名称 "OpenClaw" --表情符号 "🦞" --头像 avatars/openclaw.png
```

配置示例：

```json5
{
  agents: {
    list: [
      {
        id: "main",
        identity: {
          名称: "OpenClaw",
          主题: "太空龙虾",
          表情符号: "🦞",
          头像: "avatars/openclaw.png",
        },
      },
    ],
  },
}
```