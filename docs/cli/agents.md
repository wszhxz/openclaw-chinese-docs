---
summary: "CLI reference for `openclaw agents` (list/add/delete/bindings/bind/unbind/set identity)"
read_when:
  - You want multiple isolated agents (workspaces + routing + auth)
title: "agents"
---
# `openclaw agents`

管理隔离的代理（工作区 + 认证 + 路由）。

相关：

- 多代理路由：[Multi-Agent Routing](/concepts/multi-agent)
- 代理工作区：[Agent workspace](/concepts/agent-workspace)

## 示例

```bash
openclaw agents list
openclaw agents add work --workspace ~/.openclaw/workspace-work
openclaw agents bindings
openclaw agents bind --agent work --bind telegram:ops
openclaw agents unbind --agent work --bind telegram:ops
openclaw agents set-identity --workspace ~/.openclaw/workspace --from-identity
openclaw agents set-identity --agent main --avatar avatars/openclaw.png
openclaw agents delete work
```

## 路由绑定

使用路由绑定将入站通道流量固定到特定代理。

列出绑定：

```bash
openclaw agents bindings
openclaw agents bindings --agent work
openclaw agents bindings --json
```

添加绑定：

```bash
openclaw agents bind --agent work --bind telegram:ops --bind discord:guild-a
```

如果您省略 `accountId`（`--bind <channel>`），OpenClaw 将在可用时从通道默认值和插件设置钩子中解析它。

### 绑定范围行为

- 没有 `accountId` 的绑定仅匹配通道默认账户。
- `accountId: "*"` 是通道范围的后备（所有账户），且比显式账户绑定特异性更低。
- 如果同一代理已经有一个不带 `accountId` 的匹配通道绑定，并且您稍后使用显式或解析的 `accountId` 进行绑定，OpenClaw 将就地升级该现有绑定，而不是添加重复项。

示例：

```bash
# initial channel-only binding
openclaw agents bind --agent work --bind telegram

# later upgrade to account-scoped binding
openclaw agents bind --agent work --bind telegram:ops
```

升级后，该绑定的路由范围限定为 `telegram:ops`。如果您还需要默认账户路由，请显式添加它（例如 `--bind telegram:default`）。

移除绑定：

```bash
openclaw agents unbind --agent work --bind telegram:ops
openclaw agents unbind --agent work --all
```

## 身份文件

每个代理工作区可以在工作区根目录包含一个 `IDENTITY.md`：

- 示例路径：`~/.openclaw/workspace/IDENTITY.md`
- `set-identity --from-identity` 从工作区根目录读取（或显式的 `--identity-file`）

头像路径相对于工作区根目录解析。

## 设置身份

`set-identity` 将字段写入 `agents.list[].identity`：

- `name`
- `theme`
- `emoji`
- `avatar`（相对于工作区的路径、http(s) URL 或数据 URI）

从 `IDENTITY.md` 加载：

```bash
openclaw agents set-identity --workspace ~/.openclaw/workspace --from-identity
```

显式覆盖字段：

```bash
openclaw agents set-identity --agent main --name "OpenClaw" --emoji "🦞" --avatar avatars/openclaw.png
```

配置示例：

```json5
{
  agents: {
    list: [
      {
        id: "main",
        identity: {
          name: "OpenClaw",
          theme: "space lobster",
          emoji: "🦞",
          avatar: "avatars/openclaw.png",
        },
      },
    ],
  },
}
```