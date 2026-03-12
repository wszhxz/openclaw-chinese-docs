---
summary: "CLI reference for `openclaw agents` (list/add/delete/bindings/bind/unbind/set identity)"
read_when:
  - You want multiple isolated agents (workspaces + routing + auth)
title: "agents"
---
# `openclaw agents`

管理隔离的智能体（工作区 + 认证 + 路由）。

相关文档：

- 多智能体路由：[Multi-Agent Routing](/concepts/multi-agent)  
- 智能体工作区：[Agent workspace](/concepts/agent-workspace)

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

使用路由绑定将入站通道流量固定到特定智能体。

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

如果省略 `accountId`（`--bind <channel>`），OpenClaw 将在可用时从通道默认配置及插件设置钩子中解析该值。

### 绑定作用域行为

- 不含 `accountId` 的绑定仅匹配通道默认账户。
- `accountId: "*"` 是通道级回退绑定（适用于所有账户），其特异性低于显式指定账户的绑定。
- 若同一智能体已存在不含 `accountId` 的匹配通道绑定，而您后续又以显式或解析所得的 `accountId` 创建新绑定，则 OpenClaw 将就地升级该现有绑定，而非新增重复绑定。

示例：

```bash
# initial channel-only binding
openclaw agents bind --agent work --bind telegram

# later upgrade to account-scoped binding
openclaw agents bind --agent work --bind telegram:ops
```

升级后，该绑定的路由作用域限定为 `telegram:ops`。若您同时需要默认账户路由，请显式添加（例如 `--bind telegram:default`）。

移除绑定：

```bash
openclaw agents unbind --agent work --bind telegram:ops
openclaw agents unbind --agent work --all
```

## 身份文件

每个智能体工作区可在工作区根目录包含一个 `IDENTITY.md` 文件：

- 示例路径：`~/.openclaw/workspace/IDENTITY.md`  
- `set-identity --from-identity` 从工作区根目录（或显式指定的 `--identity-file`）读取该文件  

头像路径相对于工作区根目录解析。

## 设置身份

`set-identity` 将字段写入 `agents.list[].identity`：

- `name`  
- `theme`  
- `emoji`  
- `avatar`（工作区相对路径、http(s) URL 或 data URI）

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