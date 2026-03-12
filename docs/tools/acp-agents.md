---
summary: "Use ACP runtime sessions for Pi, Claude Code, Codex, OpenCode, Gemini CLI, and other harness agents"
read_when:
  - Running coding harnesses through ACP
  - Setting up thread-bound ACP sessions on thread-capable channels
  - Binding Discord channels or Telegram forum topics to persistent ACP sessions
  - Troubleshooting ACP backend and plugin wiring
  - Operating /acp commands from chat
title: "ACP Agents"
---
# ACP 代理

[Agent Client Protocol (ACP)](https://agentclientprotocol.com/) 会话允许 OpenClaw 通过 ACP 后端插件运行外部编码框架（例如 Pi、Claude Code、Codex、OpenCode 和 Gemini CLI）。

如果您用自然语言要求 OpenClaw “在 Codex 中运行这个” 或 “在一个线程中启动 Claude Code”，OpenClaw 应该将该请求路由到 ACP 运行时（而不是原生子代理运行时）。

## 快速操作流程

当您需要一个实用的 `/acp` 运行手册时，请使用以下步骤：

1. 创建一个会话：
   - `/acp spawn codex --mode persistent --thread auto`
2. 在绑定的线程中工作（或显式地针对该会话密钥）。
3. 检查运行时状态：
   - `/acp status`
4. 根据需要调整运行时选项：
   - `/acp model <provider/model>`
   - `/acp permissions <profile>`
   - `/acp timeout <seconds>`
5. 在不替换上下文的情况下推动活动会话：
   - `/acp steer tighten logging and continue`
6. 停止工作：
   - `/acp cancel`（停止当前轮次），或
   - `/acp close`（关闭会话并移除绑定）

## 人类快速入门

自然请求示例：

- “在这里的一个线程中启动一个持久的 Codex 会话，并保持其专注。”
- “作为一次性 Claude Code ACP 会话运行此内容并总结结果。”
- “在这个任务中使用 Gemini CLI，在一个线程中，然后在同一线程中继续跟进。”

OpenClaw 应该执行的操作：

1. 选择 `runtime: "acp"`。
2. 解析请求的框架目标（例如 `agentId`，如 `codex`）。
3. 如果请求了线程绑定且当前通道支持，则将 ACP 会话绑定到该线程。
4. 将后续线程消息路由到同一个 ACP 会话，直到取消关注/关闭/过期。

## ACP 与子代理

当您需要外部框架运行时，请使用 ACP。当您需要 OpenClaw 原生委托运行时，请使用子代理。

| 区域          | ACP 会话                           | 子代理运行                      |
| ------------- | ------------------------------------- | ---------------------------------- |
| 运行时       | ACP 后端插件（例如 acpx） | OpenClaw 原生子代理运行  |
| 会话密钥   | `agent:<agentId>:acp:<uuid>`          | `agent:<agentId>:subagent:<uuid>`  |
| 主要命令 | `/acp ...`                            | `/subagents ...`                   |
| 创建工具    | `sessions_spawn` with `runtime:"acp"` | `sessions_spawn`（默认运行时） |

另见 [子代理](/tools/subagents)。

## 线程绑定会话（通道无关）

当为通道适配器启用线程绑定时，ACP 会话可以绑定到线程：

- OpenClaw 将线程绑定到目标 ACP 会话。
- 该线程中的后续消息路由到绑定的 ACP 会话。
- ACP 输出返回到同一线程。
- 取消关注/关闭/归档/空闲超时或最大年龄到期会移除绑定。

线程绑定支持是特定于适配器的。如果活动的通道适配器不支持线程绑定，OpenClaw 会返回一个明确的不支持/不可用消息。

线程绑定 ACP 所需的功能标志：

- `acp.enabled=true`
- `acp.dispatch.enabled` 默认开启（设置 `false` 暂停 ACP 分发）
- 通道适配器 ACP 线程创建标志已启用（特定于适配器）
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`

### 支持线程的通道

- 任何暴露会话/线程绑定能力的通道适配器。
- 当前内置支持：
  - Discord 线程/频道
  - Telegram 论坛主题（群组/超级群组中的论坛主题和私聊主题）
- 插件通道可以通过相同的绑定接口添加支持。

## 通道特定设置

对于非临时工作流，在顶级 `bindings[]` 条目中配置持久的 ACP 绑定。

### 绑定模型

- `bindings[].type="acp"` 标记一个持久的 ACP 对话绑定。
- `bindings[].match` 识别目标对话：
  - Discord 频道或线程: `match.channel="discord"` + `match.peer.id="<channelOrThreadId>"`
  - Telegram 论坛主题: `match.channel="telegram"` + `match.peer.id="<chatId>:topic:<topicId>"`
- `bindings[].agentId` 是拥有 OpenClaw 代理 ID。
- 可选的 ACP 覆盖位于 `bindings[].acp` 下：
  - `mode` (`persistent` 或 `oneshot`)
  - `label`
  - `cwd`
  - `backend`

### 每个代理的运行时默认值

使用 `agents.list[].runtime` 为每个代理定义一次 ACP 默认值：

- `agents.list[].runtime.type="acp"`
- `agents.list[].runtime.acp.agent`（框架 ID，例如 `codex` 或 `claude`）
- `agents.list[].runtime.acp.backend`
- `agents.list[].runtime.acp.mode`
- `agents.list[].runtime.acp.cwd`

ACP 绑定会话的覆盖优先级：

1. `bindings[].acp.*`
2. `agents.list[].runtime.acp.*`
3. 全局 ACP 默认值（例如 `acp.backend`）

示例：

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
      {
        id: "claude",
        runtime: {
          type: "acp",
          acp: { agent: "claude", backend: "acpx", mode: "persistent" },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "discord",
        accountId: "default",
        peer: { kind: "channel", id: "222222222222222222" },
      },
      acp: { label: "codex-main" },
    },
    {
      type: "acp",
      agentId: "claude",
      match: {
        channel: "telegram",
        accountId: "default",
        peer: { kind: "group", id: "-1001234567890:topic:42" },
      },
      acp: { cwd: "/workspace/repo-b" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "discord", accountId: "default" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "telegram", accountId: "default" },
    },
  ],
  channels: {
    discord: {
      guilds: {
        "111111111111111111": {
          channels: {
            "222222222222222222": { requireMention: false },
          },
        },
      },
    },
    telegram: {
      groups: {
        "-1001234567890": {
          topics: { "42": { requireMention: false } },
        },
      },
    },
  },
}
```

行为：

- OpenClaw 在使用之前确保配置的 ACP 会话存在。
- 该频道或主题中的消息路由到配置的 ACP 会话。
- 在绑定的对话中，`/new` 和 `/reset` 在原地重置相同的 ACP 会话密钥。
- 临时运行时绑定（例如由线程焦点流创建）仍然适用。

## 启动 ACP 会话（接口）

### 从 `sessions_spawn`

使用 `runtime: "acp"` 从代理轮次或工具调用开始 ACP 会话。

```json
{
  "task": "Open the repo and summarize failing tests",
  "runtime": "acp",
  "agentId": "codex",
  "thread": true,
  "mode": "session"
}
```

注意事项：

- `runtime` 默认为 `subagent`，因此请为 ACP 会话显式设置 `runtime: "acp"`。
- 如果省略了 `agentId`，OpenClaw 会在配置时使用 `acp.defaultAgent`。
- `mode: "session"` 需要 `thread: true` 以保持持久的绑定对话。

接口详情：

- `task`（必需）：发送到 ACP 会话的初始提示。
- `runtime`（ACP 必需）：必须是 `"acp"`。
- `agentId`（可选）：ACP 目标框架 ID。如果设置了则回退到 `acp.defaultAgent`。
- `thread`（可选，默认 `false`）：请求支持的线程绑定流。
- `mode`（可选）：`run`（一次性）或 `session`（持久）。
  - 默认是 `run`
  - 如果省略了 `thread: true` 和模式，OpenClaw 可能会根据运行时路径默认为持久行为
  - `mode: "session"` 需要 `thread: true`
- `cwd`（可选）：请求的运行时工作目录（由后端/运行时策略验证）。
- `label`（可选）：用于会话/横幅文本的操作员面向标签。
- `streamTo`（可选）：`"parent"` 将初始 ACP 运行进度摘要作为系统事件流回请求者会话。
  - 当可用时，接受的响应包括指向会话范围 JSONL 日志（`<sessionId>.acp-stream.jsonl`）的 `streamLogPath`，您可以对其进行尾随以获取完整的中继历史记录。

## 沙箱兼容性

ACP 会话目前在主机运行时上运行，而不是在 OpenClaw 沙箱内运行。

当前限制：

- 如果请求者会话被沙箱化，ACP 创建将同时阻止 `sessions_spawn({ runtime: "acp" })` 和 `/acp spawn`。
  - 错误：`Sandboxed sessions cannot spawn ACP sessions because runtime="acp" runs on the host. Use runtime="subagent" from sandboxed sessions.`
- `sessions_spawn` 与 `runtime: "acp"` 不支持 `sandbox: "require"`。
  - 错误：`sessions_spawn sandbox="require" is unsupported for runtime="acp" because ACP sessions run outside the sandbox. Use runtime="subagent" or sandbox="inherit".`

当需要沙箱强制执行时，请使用 `runtime: "subagent"`。

### 从 `/acp` 命令

在需要时，使用 `/acp spawn` 进行显式的操作员控制。

```text
/acp spawn codex --mode persistent --thread auto
/acp spawn codex --mode oneshot --thread off
/acp spawn codex --thread here
```

关键标志：

- `--mode persistent|oneshot`
- `--thread auto|here|off`
- `--cwd <absolute-path>`
- `--label <name>`

参见 [斜杠命令](/tools/slash-commands)。

## 会话目标解析

大多数 `/acp` 操作接受一个可选的会话目标（`session-key`、`session-id` 或 `session-label`）。

解析顺序：

1. 显式目标参数（或 `--session` 对于 `/acp steer`）
   - 尝试密钥
   - 然后尝试 UUID 形状的会话 ID
   - 然后尝试标签
2. 当前线程绑定（如果此对话/线程绑定到 ACP 会话）
3. 当前请求者会话回退

如果没有解析出目标，OpenClaw 会返回一个明确的错误（`Unable to resolve session target: ...`）。

## 创建线程模式

`/acp spawn` 支持 `--thread auto|here|off`。

| 模式   | 行为                                                                                            |
| ------ | --------------------------------------------------------------------------------------------------- |
| `auto` | 在活动线程中：绑定该线程。在非线程外部：当支持时创建/绑定子线程。 |
| `here` | 需要当前活动线程；如果不在其中则失败。                                                  |
| `off`  | 无绑定。会话以未绑定状态开始。                                                                 |

注意事项：

- 在非线程绑定表面上，默认行为实际上是 `off`。
- 线程绑定的生成需要通道策略支持：
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`

## ACP 控制

可用命令族：

- `/acp spawn`
- `/acp cancel`
- `/acp steer`
- `/acp close`
- `/acp status`
- `/acp set-mode`
- `/acp set`
- `/acp cwd`
- `/acp permissions`
- `/acp timeout`
- `/acp model`
- `/acp reset-options`
- `/acp sessions`
- `/acp doctor`
- `/acp install`

`/acp status` 显示有效的运行时选项，并且在可用时显示运行时级别和后端级别的会话标识符。

某些控制依赖于后端功能。如果后端不支持某个控制，OpenClaw 将返回一个明确的不支持控制错误。

## ACP 命令手册

| 命令              | 功能                                              | 示例                                                        |
| -------------------- | --------------------------------------------------------- | -------------------------------------------------------------- |
| `/acp spawn`         | 创建ACP会话；可选线程绑定。                 | `/acp spawn codex --mode persistent --thread auto --cwd /repo` |
| `/acp cancel`        | 取消目标会话中的飞行回合。                 | `/acp cancel agent:codex:acp:<uuid>`                           |
| `/acp steer`         | 向运行中的会话发送转向指令。                | `/acp steer --session support inbox prioritize failing tests`  |
| `/acp close`         | 关闭会话并解除线程目标绑定。                  | `/acp close`                                                   |
| `/acp status`        | 显示后端、模式、状态、运行时选项、功能。 | `/acp status`                                                  |
| `/acp set-mode`      | 设置目标会话的运行时模式。                      | `/acp set-mode plan`                                           |
| `/acp set`           | 通用运行时配置选项写入。                      | `/acp set model openai/gpt-5.2`                                |
| `/acp cwd`           | 设置运行时工作目录覆盖。                   | `/acp cwd /Users/user/Projects/repo`                           |
| `/acp permissions`   | 设置审批策略配置文件。                              | `/acp permissions strict`                                      |
| `/acp timeout`       | 设置运行时超时（秒）。                            | `/acp timeout 120`                                             |
| `/acp model`         | 设置运行时模型覆盖。                               | `/acp model anthropic/claude-opus-4-5`                         |
| `/acp reset-options` | 移除会话运行时选项覆盖。                  | `/acp reset-options`                                           |
| `/acp sessions`      | 列出存储中的最近ACP会话。                      | `/acp sessions`                                                |
| `/acp doctor`        | 后端健康状况、功能、可操作修复。           | `/acp doctor`                                                  |
| `/acp install`       | 打印确定性的安装和启用步骤。             | `/acp install`                                                 |

## 运行时选项映射

`/acp` 提供了方便的命令和一个通用设置器。

等效操作：

- `/acp model <id>` 映射到运行时配置键 `model`。
- `/acp permissions <profile>` 映射到运行时配置键 `approval_policy`。
- `/acp timeout <seconds>` 映射到运行时配置键 `timeout`。
- `/acp cwd <path>` 直接更新运行时cwd覆盖。
- `/acp set <key> <value>` 是通用路径。
  - 特殊情况：`key=cwd` 使用cwd覆盖路径。
- `/acp reset-options` 清除目标会话的所有运行时覆盖。

## acpx 套件支持（当前）

当前acpx内置套件别名：

- `pi`
- `claude`
- `codex`
- `opencode`
- `gemini`
- `kimi`

当OpenClaw使用acpx后端时，除非您的acpx配置定义了自定义代理别名，否则请优先使用这些值作为 `agentId`。

直接使用acpx CLI也可以通过 `--agent <command>` 针对任意适配器，但这是一种原始逃生舱口，是acpx CLI的功能（不是正常的OpenClaw `agentId` 路径）。

## 必需的配置

核心ACP基线：

```json5
{
  acp: {
    enabled: true,
    // Optional. Default is true; set false to pause ACP dispatch while keeping /acp controls.
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "codex",
    allowedAgents: ["pi", "claude", "codex", "opencode", "gemini", "kimi"],
    maxConcurrentSessions: 8,
    stream: {
      coalesceIdleMs: 300,
      maxChunkChars: 1200,
    },
    runtime: {
      ttlMinutes: 120,
    },
  },
}
```

线程绑定配置是特定于通道适配器的。Discord示例：

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        spawnAcpSessions: true,
      },
    },
  },
}
```

如果线程绑定的ACP生成不起作用，请首先验证适配器功能标志：
- Discord: `channels.discord.threadBindings.spawnAcpSessions=true`

参见[配置参考](/gateway/configuration-reference)。

## acpx后端的插件设置

安装并启用插件：

```bash
openclaw plugins install acpx
openclaw config set plugins.entries.acpx.enabled true
```

开发期间本地工作区安装：

```bash
openclaw plugins install ./extensions/acpx
```

然后验证后端健康状况：

```text
/acp doctor
```

### acpx 命令和版本配置

默认情况下，acpx 插件（发布为 `@openclaw/acpx`）使用插件本地固定的二进制文件：

1. 命令默认为 `extensions/acpx/node_modules/.bin/acpx`。
2. 预期版本默认为扩展固定版本。
3. 启动时立即注册ACP后端为未就绪状态。
4. 后台确保任务验证 `acpx --version`。
5. 如果插件本地二进制文件缺失或不匹配，它将运行：
   `npm install --omit=dev --no-save acpx@<pinned>` 并重新验证。

您可以在插件配置中覆盖命令/版本：

```json
{
  "plugins": {
    "entries": {
      "acpx": {
        "enabled": true,
        "config": {
          "command": "../acpx/dist/cli.js",
          "expectedVersion": "any"
        }
      }
    }
  }
}
```

注意事项：

- `command` 接受绝对路径、相对路径或命令名称 (`acpx`)。
- 相对路径从OpenClaw工作区目录解析。
- `expectedVersion: "any"` 禁用严格的版本匹配。
- 当 `command` 指向自定义二进制文件/路径时，禁用插件本地自动安装。
- OpenClaw启动在后台健康检查运行时保持非阻塞状态。

参见[插件](/tools/plugin)。

## 权限配置

ACP会话以非交互方式运行——没有TTY来批准或拒绝文件写入和shell执行权限提示。acpx插件提供了两个配置键来控制如何处理权限：

### `permissionMode`

控制套件代理在不提示的情况下可以执行哪些操作。

| 值           | 行为                                                  |
| --------------- | --------------------------------------------------------- |
| `approve-all`   | 自动批准所有文件写入和shell命令。          |
| `approve-reads` | 仅自动批准读取；写入和执行需要提示。 |
| `deny-all`      | 拒绝所有权限提示。                              |

### `nonInteractivePermissions`

控制在没有交互式TTY可用时（对于ACP会话总是这种情况）显示权限提示时会发生什么。

| 值  | 行为                                                          |
| ------ | ----------------------------------------------------------------- |
| `fail` | 中止会话并显示 `AcpRuntimeError`。 **(默认)**           |
| `deny` | 静默拒绝权限并继续（优雅降级）。 |

### 配置

通过插件配置设置：

```bash
openclaw config set plugins.entries.acpx.config.permissionMode approve-all
openclaw config set plugins.entries.acpx.config.nonInteractivePermissions fail
```

更改这些值后重启网关。

> **重要提示：** OpenClaw目前默认为 `permissionMode=approve-reads` 和 `nonInteractivePermissions=fail`。在非交互式ACP会话中，任何触发权限提示的写入或执行都可能因 `AcpRuntimeError: Permission prompt unavailable in non-interactive mode` 而失败。
>
> 如果您需要限制权限，请将 `nonInteractivePermissions` 设置为 `deny`，以便会话优雅降级而不是崩溃。

## 故障排除

| 症状                                                                  | 可能的原因                                                                    | 解决方法                                                                                                                                                               |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ACP runtime backend is not configured`                                  | 后端插件缺失或被禁用。                                             | 安装并启用后端插件，然后运行 `/acp doctor`。                                                                                                        |
| `ACP is disabled by policy (acp.enabled=false)`                          | ACP 全局禁用。                                                          | 设置 `acp.enabled=true`。                                                                                                                                           |
| `ACP dispatch is disabled by policy (acp.dispatch.enabled=false)`        | 从普通线程发送消息被禁用。                                  | 设置 `acp.dispatch.enabled=true`。                                                                                                                                  |
| `ACP agent "<id>" is not allowed by policy`                              | 代理不在允许列表中。                                                         | 使用允许的 `agentId` 或更新 `acp.allowedAgents`。                                                                                                              |
| `Unable to resolve session target: ...`                                  | 错误的密钥/ID/标签令牌。                                                         | 运行 `/acp sessions`，复制确切的密钥/标签，重试。                                                                                                                 |
| `--thread here requires running /acp spawn inside an active ... thread`  | `--thread here` 在线程上下文之外使用。                                  | 移动到目标线程或使用 `--thread auto`/`off`。                                                                                                               |
| `Only <user-id> can rebind this thread.`                                 | 另一个用户拥有线程绑定。                                               | 重新绑定为所有者或使用不同的线程。                                                                                                                        |
| `Thread bindings are unavailable for <channel>.`                         | 适配器缺乏线程绑定能力。                                        | 使用 `--thread off` 或移动到支持的适配器/通道。                                                                                                          |
| `Sandboxed sessions cannot spawn ACP sessions ...`                       | ACP 运行时在主机侧；请求会话在沙箱中。                       | 从沙箱会话中使用 `runtime="subagent"`，或从非沙箱会话中运行 ACP 孵化。                                                                  |
| `sessions_spawn sandbox="require" is unsupported for runtime="acp" ...`  | `sandbox="require"` 请求 ACP 运行时。                                  | 使用 `runtime="subagent"` 进行所需的沙箱处理，或使用 ACP 从非沙箱会话中运行 `sandbox="inherit"`。                                               |
| 绑定会话缺少 ACP 元数据                                   | 陈旧/已删除的 ACP 会话元数据。                                             | 使用 `/acp spawn` 重新创建，然后重新绑定/聚焦线程。                                                                                                             |
| `AcpRuntimeError: Permission prompt unavailable in non-interactive mode` | `permissionMode` 阻止在非交互式 ACP 会话中写入/执行。             | 将 `plugins.entries.acpx.config.permissionMode` 设置为 `approve-all` 并重启网关。参见 [权限配置](#permission-configuration)。                 |
| ACP 会话早期失败且输出很少                               | 权限提示被 `permissionMode`/`nonInteractivePermissions` 阻止。 | 检查网关日志中的 `AcpRuntimeError`。对于完整权限，设置 `permissionMode=approve-all`；对于优雅降级，设置 `nonInteractivePermissions=deny`。 |
| ACP 会话在完成工作后无限期停滞                    | 套件进程已完成但 ACP 会话未报告完成。             | 使用 `ps aux \| grep acpx` 监控；手动终止陈旧进程。                                                                                                |