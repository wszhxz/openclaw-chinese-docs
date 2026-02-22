---
summary: "Hooks: event-driven automation for commands and lifecycle events"
read_when:
  - You want event-driven automation for /new, /reset, /stop, and agent lifecycle events
  - You want to build, install, or debug hooks
title: "Hooks"
---
# Hooks

Hooks 提供了一个可扩展的事件驱动系统，用于在响应代理命令和事件时自动化操作。Hooks 会自动从目录中发现，并且可以通过 CLI 命令进行管理，类似于 OpenClaw 中的技能。

## 入门指南

Hooks 是在某些事情发生时运行的小脚本。有两种类型：

- **Hooks**（本页）：在网关中运行，当代理事件触发时，例如 `/new`，`/reset`，`/stop` 或生命周期事件。
- **Webhooks**：外部 HTTP Webhooks，允许其他系统触发 OpenClaw 中的工作。参见 [Webhook Hooks](/automation/webhook) 或使用 `openclaw webhooks` 进行 Gmail 辅助命令。

Hooks 还可以打包在插件中；参见 [Plugins](/tools/plugin#plugin-hooks)。

常见用途：

- 在重置会话时保存内存快照
- 为故障排除或合规性维护命令审计跟踪
- 在会话开始或结束时触发后续自动化
- 在事件触发时将文件写入代理工作区或调用外部 API

如果您能编写一个小的 TypeScript 函数，您就可以编写一个 Hook。Hooks 会自动发现，您可以通过 CLI 启用或禁用它们。

## 概述

Hooks 系统允许您：

- 在发出 `/new` 时将会话上下文保存到内存中
- 记录所有命令以进行审计
- 在代理生命周期事件上触发自定义自动化
- 在不修改核心代码的情况下扩展 OpenClaw 的行为

## 开始使用

### 内置 Hooks

OpenClaw 随附了四个内置 Hooks，这些 Hooks 会自动发现：

- **💾 session-memory**：在发出 `/new` 时将会话上下文保存到您的代理工作区（默认 `~/.openclaw/workspace/memory/`）
- **📎 bootstrap-extra-files**：在 `agent:bootstrap` 期间从配置的 glob/path 模式注入额外的工作区引导文件
- **📝 command-logger**：将所有命令事件记录到 `~/.openclaw/logs/commands.log`
- **🚀 boot-md**：在网关启动时运行 `BOOT.md`（需要启用内部 Hooks）

列出可用 Hooks：

```bash
openclaw hooks list
```

启用一个 Hook：

```bash
openclaw hooks enable session-memory
```

检查 Hook 状态：

```bash
openclaw hooks check
```

获取详细信息：

```bash
openclaw hooks info session-memory
```

### 入职

在入职过程中 (`openclaw onboard`)，您将被提示启用推荐的 Hooks。向导会自动发现符合条件的 Hooks 并提供选择。

## Hook 发现

Hooks 会自动从三个目录中发现（按优先级顺序）：

1. **工作区 Hooks**：`<workspace>/hooks/`（每个代理，最高优先级）
2. **管理 Hooks**：`~/.openclaw/hooks/`（用户安装，跨工作区共享）
3. **内置 Hooks**：`<openclaw>/dist/hooks/bundled/`（随 OpenClaw 发货）

管理 Hook 目录可以是 **单个 Hook** 或 **Hook 包**（包目录）。

每个 Hook 是一个包含以下内容的目录：

```
my-hook/
├── HOOK.md          # Metadata + documentation
└── handler.ts       # Handler implementation
```

## Hook Packs (npm/archives)

Hook packs 是标准的 npm 包，通过 `openclaw.hooks` 在 `package.json` 中导出一个或多个 hooks。使用以下命令安装它们：

```bash
openclaw hooks install <path-or-spec>
```

Npm 规范仅限于注册表（包名称 + 可选版本/标签）。Git/URL/文件规范会被拒绝。

示例 `package.json`:

```json
{
  "name": "@acme/my-hooks",
  "version": "0.1.0",
  "openclaw": {
    "hooks": ["./hooks/my-hook", "./hooks/other-hook"]
  }
}
```

每个条目指向一个包含 `HOOK.md` 和 `handler.ts`（或 `index.ts`）的 hook 目录。
Hook packs 可以附带依赖项；它们将被安装在 `~/.openclaw/hooks/<id>` 下。
每个 `openclaw.hooks` 条目在符号链接解析后必须保留在包目录内；逃逸的条目将被拒绝。

安全说明：`openclaw hooks install` 使用 `npm install --ignore-scripts` 安装依赖项（不运行生命周期脚本）。保持 hook pack 依赖树为“纯 JS/TS”，避免依赖于 `postinstall` 构建的包。

## Hook 结构

### HOOK.md 格式

`HOOK.md` 文件包含 YAML 前置元数据加上 Markdown 文档：

```markdown
---
name: my-hook
description: "Short description of what this hook does"
homepage: https://docs.openclaw.ai/automation/hooks#my-hook
metadata:
  { "openclaw": { "emoji": "🔗", "events": ["command:new"], "requires": { "bins": ["node"] } } }
---

# My Hook

Detailed documentation goes here...

## What It Does

- Listens for `/new` commands
- Performs some action
- Logs the result

## Requirements

- Node.js must be installed

## Configuration

No configuration needed.
```

### 元数据字段

`metadata.openclaw` 对象支持：

- **`emoji`**: CLI 显示的 emoji（例如 `"💾"`）
- **`events`**: 要监听的事件数组（例如 `["command:new", "command:reset"]`）
- **`export`**: 要使用的命名导出（默认为 `"default"`）
- **`homepage`**: 文档 URL
- **`requires`**: 可选要求
  - **`bins`**: PATH 上所需的二进制文件（例如 `["git", "node"]`）
  - **`anyBins`**: 这些二进制文件中至少有一个必须存在
  - **`env`**: 所需的环境变量
  - **`config`**: 所需的配置路径（例如 `["workspace.dir"]`）
  - **`os`**: 所需的平台（例如 `["darwin", "linux"]`）
- **`always`**: 绕过资格检查（布尔值）
- **`install`**: 安装方法（对于捆绑的 hook：`[{"id":"bundled","kind":"bundled"}]`）

### 处理程序实现

`handler.ts` 文件导出一个 `HookHandler` 函数：

```typescript
import type { HookHandler } from "../../src/hooks/hooks.js";

const myHandler: HookHandler = async (event) => {
  // 仅在 'new' 命令时触发
  if (event.type !== "command" || event.action !== "new") {
    return;
  }

console.log(`[my-hook] New command triggered`);
console.log(`  Session: ${event.sessionKey}`);
console.log(`  Timestamp: ${event.timestamp.toISOString()}`);

// 您的自定义逻辑在此处

// 可选地向用户发送消息
event.messages.push("✨ My hook executed!");
};

export default myHandler;
```

#### Event Context

Each event includes:

```typescript
{
  type: 'command' | 'session' | 'agent' | 'gateway' | 'message',
  action: string,              // 例如，'new', 'reset', 'stop', 'received', 'sent'
  sessionKey: string,          // 会话标识符
  timestamp: Date,             // 事件发生的时间
  messages: string[],          // 将消息推送到此处以发送给用户
  context: {
    // 命令事件：
    sessionEntry?: SessionEntry,
    sessionId?: string,
    sessionFile?: string,
    commandSource?: string,    // 例如，'whatsapp', 'telegram'
    senderId?: string,
    workspaceDir?: string,
    bootstrapFiles?: WorkspaceBootstrapFile[],
    cfg?: OpenClawConfig,
    // 消息事件（有关完整详细信息，请参阅消息事件部分）：
    from?: string,             // message:received
    to?: string,               // message:sent
    content?: string,
    channelId?: string,
    success?: boolean,         // message:sent
  }
}
```

## Event Types

### Command Events

Triggered when agent commands are issued:

- **`command`**: All command events (general listener)
- **`command:new`**: When `/new` command is issued
- **`command:reset`**: When `/reset` command is issued
- **`command:stop`**: When `/stop` command is issued

### Agent Events

- **`agent:bootstrap`**: Before workspace bootstrap files are injected (hooks may mutate `context.bootstrapFiles`)

### Gateway Events

Triggered when the gateway starts:

- **`gateway:startup`**: After channels start and hooks are loaded

### Message Events

Triggered when messages are received or sent:

- **`message`**: All message events (general listener)
- **`message:received`**: When an inbound message is received from any channel
- **`message:sent`**: When an outbound message is successfully sent

#### Message Event Context

Message events include rich context about the message:

```typescript
// message:received 上下文
{
  from: string,           // 发送者标识符（电话号码、用户ID等）
  content: string,        // 消息内容
  timestamp?: number,     // 接收时的Unix时间戳
  channelId: string,      // 渠道（例如，"whatsapp", "telegram", "discord"）
  accountId?: string,     // 多账户设置中的提供商账户ID
  conversationId?: string, // 聊天/对话ID
  messageId?: string,     // 提供商的消息ID
  metadata?: {            // 其他提供商特定的数据
    to?: string,
    provider?: string,
    surface?: string,
    threadId?: string,
    senderId?: string,
    senderName?: string,
    senderUsername?: string,
    senderE164?: string,
  }
}

// message:sent 上下文
{
  to: string,             // 接收者标识符
  content: string,        // 发送的消息内容
  success: boolean,       // 发送是否成功
  error?: string,         // 如果发送失败，错误信息
  channelId: string,      // 通道（例如，"whatsapp", "telegram", "discord"）
  accountId?: string,     // 提供商账户ID
  conversationId?: string, // 聊天/对话ID
  messageId?: string,     // 提供商返回的消息ID
}
```

#### Example: Message Logger Hook

```typescript
import type { HookHandler } from "../../src/hooks/hooks.js";
import { isMessageReceivedEvent, isMessageSentEvent } from "../../src/hooks/internal-hooks.js";

const handler: HookHandler = async (event) => {
  if (isMessageReceivedEvent(event)) {
    console.log(`[message-logger] Received from ${event.context.from}: ${event.context.content}`);
  } else if (isMessageSentEvent(event)) {
    console.log(`[message-logger] Sent to ${event.context.to}: ${event.context.content}`);
  }
};

export default handler;
```

### Tool Result Hooks (Plugin API)

These hooks are not event-stream listeners; they let plugins synchronously adjust tool results before OpenClaw persists them.

- **`tool_result_persist`**: transform tool results before they are written to the session transcript. Must be synchronous; return the updated tool result payload or `undefined` to keep it as-is. See [Agent Loop](/concepts/agent-loop).

### Future Events

Planned event types:

- **`session:start`**: When a new session begins
- **`session:end`**: When a session ends
- **`agent:error`**: When an agent encounters an error

## Creating Custom Hooks

### 1. Choose Location

- **Workspace hooks** (`<workspace>/hooks/`): Per-agent, highest precedence
- **Managed hooks** (`~/.openclaw/hooks/`): Shared across workspaces

### 2. Create Directory Structure

```bash
mkdir -p ~/.openclaw/hooks/my-hook
cd ~/.openclaw/hooks/my-hook
```

### 3. Create HOOK.md

```markdown
---
name: my-hook
description: "执行一些有用的操作"
metadata: { "openclaw": { "emoji": "🎯", "events": ["command:new"] } }
---

# 我的自定义Hook

当你发出 `/new` 时，此Hook会执行一些有用的操作。
```

### 4. Create handler.ts

```typescript
import type { HookHandler } from "../../src/hooks/hooks.js";

const handler: HookHandler = async (event) => {
  if (event.type !== "command" || event.action !== "new") {
    return;
  }

  console.log("[my-hook] 正在运行！");
  // 你的逻辑代码
};

export default handler;
```

### 5. Enable and Test

```bash
# 验证hook已被发现
openclaw hooks list

# 启用它
openclaw hooks enable my-hook

# 重启你的网关进程（在macOS上重启菜单栏应用，或重启你的开发进程）

# 触发事件
# 通过消息渠道发送 /new
```

## 配置

### 新配置格式（推荐）

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "session-memory": { "enabled": true },
        "command-logger": { "enabled": false }
      }
    }
  }
}
```

### 每钩子配置

钩子可以有自定义配置：

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "my-hook": {
          "enabled": true,
          "env": {
            "MY_CUSTOM_VAR": "value"
          }
        }
      }
    }
  }
}
```

### 额外目录

从其他目录加载钩子：

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "load": {
        "extraDirs": ["/path/to/more/hooks"]
      }
    }
  }
}
```

### 旧版配置格式（仍受支持）

为了向后兼容，旧版配置格式仍然有效：

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "handlers": [
        {
          "event": "command:new",
          "module": "./hooks/handlers/my-handler.ts",
          "export": "default"
        }
      ]
    }
  }
}
```

注意：`module` 必须是相对于工作区的路径。绝对路径和超出工作区的遍历会被拒绝。

**迁移**：为新钩子使用新的基于发现的系统。旧的处理程序在基于目录的钩子之后加载。

## 命令行命令

### 列出钩子

```bash
# List all hooks
openclaw hooks list

# Show only eligible hooks
openclaw hooks list --eligible

# Verbose output (show missing requirements)
openclaw hooks list --verbose

# JSON output
openclaw hooks list --json
```

### 钩子信息

```bash
# Show detailed info about a hook
openclaw hooks info session-memory

# JSON output
openclaw hooks info session-memory --json
```

### 检查资格

```bash
# Show eligibility summary
openclaw hooks check

# JSON output
openclaw hooks check --json
```

### 启用/禁用

```bash
# Enable a hook
openclaw hooks enable session-memory

# Disable a hook
openclaw hooks disable command-logger
```

## 内置钩子参考

### session-memory

当你发出 `/new` 时，将会话上下文保存到内存中。

**事件**：`command:new`

**要求**：必须配置 `workspace.dir`

**输出**：`<workspace>/memory/YYYY-MM-DD-slug.md`（默认为 `~/.openclaw/workspace`）

**功能说明**：

1. 使用预重置会话条目来定位正确的对话记录
2. 提取最后15行对话
3. 使用LLM生成描述性文件名片段
4. 将会话元数据保存到日期标记的内存文件中

**示例输出**：

```markdown
# Session: 2026-01-16 14:30:00 UTC

- **Session Key**: agent:main:main
- **Session ID**: abc123def456
- **Source**: telegram
```

**文件名示例**：

- `2026-01-16-vendor-pitch.md`
- `2026-01-16-api-design.md`
- `2026-01-16-1430.md`（如果片段生成失败，则使用回退时间戳）

**启用**：

```bash
openclaw hooks enable session-memory
```

### bootstrap-extra-files

注入额外的引导文件（例如 monorepo-local `AGENTS.md` / `TOOLS.md`) 在 `agent:bootstrap` 期间。

**事件**: `agent:bootstrap`

**要求**: `workspace.dir` 必须已配置

**输出**: 不写入文件；仅在内存中修改引导上下文。

**配置**:

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "bootstrap-extra-files": {
          "enabled": true,
          "paths": ["packages/*/AGENTS.md", "packages/*/TOOLS.md"]
        }
      }
    }
  }
}
```

**注意**:

- 路径相对于工作区解析。
- 文件必须保留在工作区内（通过 realpath 检查）。
- 仅加载识别的引导基本名称。
- 子代理白名单保持不变（仅 `AGENTS.md` 和 `TOOLS.md`）。

**启用**:

```bash
openclaw hooks enable bootstrap-extra-files
```

### command-logger

将所有命令事件记录到中央审计文件。

**事件**: `command`

**要求**: 无

**输出**: `~/.openclaw/logs/commands.log`

**功能**:

1. 捕获事件详细信息（命令操作、时间戳、会话密钥、发送者ID、来源）
2. 以 JSONL 格式追加到日志文件
3. 在后台静默运行

**示例日志条目**:

```jsonl
{"timestamp":"2026-01-16T14:30:00.000Z","action":"new","sessionKey":"agent:main:main","senderId":"+1234567890","source":"telegram"}
{"timestamp":"2026-01-16T15:45:22.000Z","action":"stop","sessionKey":"agent:main:main","senderId":"user@example.com","source":"whatsapp"}
```

**查看日志**:

```bash
# View recent commands
tail -n 20 ~/.openclaw/logs/commands.log

# Pretty-print with jq
cat ~/.openclaw/logs/commands.log | jq .

# Filter by action
grep '"action":"new"' ~/.openclaw/logs/commands.log | jq .
```

**启用**:

```bash
openclaw hooks enable command-logger
```

### boot-md

当网关启动时（在通道启动之后）运行 `BOOT.md`。
必须启用内部钩子才能运行此操作。

**事件**: `gateway:startup`

**要求**: `workspace.dir` 必须已配置

**功能**:

1. 从工作区读取 `BOOT.md`
2. 通过代理运行器运行指令
3. 通过消息工具发送任何请求的出站消息

**启用**:

```bash
openclaw hooks enable boot-md
```

## 最佳实践

### 保持处理程序快速

钩子在命令处理期间运行。保持它们轻量级：

```typescript
// ✓ Good - async work, returns immediately
const handler: HookHandler = async (event) => {
  void processInBackground(event); // Fire and forget
};

// ✗ Bad - blocks command processing
const handler: HookHandler = async (event) => {
  await slowDatabaseQuery(event);
  await evenSlowerAPICall(event);
};
```

### 优雅地处理错误

始终包装有风险的操作：

```typescript
const handler: HookHandler = async (event) => {
  try {
    await riskyOperation(event);
  } catch (err) {
    console.error("[my-handler] Failed:", err instanceof Error ? err.message : String(err));
    // Don't throw - let other handlers run
  }
};
```

### 过滤事件

如果事件不相关，则提前返回：

```typescript
const handler: HookHandler = async (event) => {
  // Only handle 'new' commands
  if (event.type !== "command" || event.action !== "new") {
    return;
  }

  // Your logic here
};
```

### 使用特定事件键

尽可能在元数据中指定确切的事件：

```yaml
metadata: { "openclaw": { "events": ["command:new"] } } # Specific
```

而不是：

```yaml
metadata: { "openclaw": { "events": ["command"] } } # General - more overhead
```

## 调试

### 启用钩子日志记录

网关在启动时记录钩子加载情况：

```
Registered hook: session-memory -> command:new
Registered hook: bootstrap-extra-files -> agent:bootstrap
Registered hook: command-logger -> command
Registered hook: boot-md -> gateway:startup
```

### 检查发现

列出所有已发现的钩子：

```bash
openclaw hooks list --verbose
```

### 检查注册

在处理程序中记录调用时间：

```typescript
const handler: HookHandler = async (event) => {
  console.log("[my-handler] Triggered:", event.type, event.action);
  // Your logic
};
```

### 验证资格

检查钩子为何不符合资格：

```bash
openclaw hooks info my-hook
```

在输出中查找缺失的要求。

## 测试

### 网关日志

监控网关日志以查看钩子执行情况：

```bash
# macOS
./scripts/clawlog.sh -f

# Other platforms
tail -f ~/.openclaw/gateway.log
```

### 直接测试钩子

单独测试您的处理程序：

```typescript
import { test } from "vitest";
import { createHookEvent } from "./src/hooks/hooks.js";
import myHandler from "./hooks/my-hook/handler.js";

test("my handler works", async () => {
  const event = createHookEvent("command", "new", "test-session", {
    foo: "bar",
  });

  await myHandler(event);

  // Assert side effects
});
```

## 架构

### 核心组件

- **`src/hooks/types.ts`**: 类型定义
- **`src/hooks/workspace.ts`**: 目录扫描和加载
- **`src/hooks/frontmatter.ts`**: HOOK.md 元数据解析
- **`src/hooks/config.ts`**: 资格检查
- **`src/hooks/hooks-status.ts`**: 状态报告
- **`src/hooks/loader.ts`**: 动态模块加载器
- **`src/cli/hooks-cli.ts`**: CLI 命令
- **`src/gateway/server-startup.ts`**: 在网关启动时加载钩子
- **`src/auto-reply/reply/commands-core.ts`**: 触发命令事件

### 发现流程

```
Gateway startup
    ↓
Scan directories (workspace → managed → bundled)
    ↓
Parse HOOK.md files
    ↓
Check eligibility (bins, env, config, os)
    ↓
Load handlers from eligible hooks
    ↓
Register handlers for events
```

### 事件流程

```
User sends /new
    ↓
Command validation
    ↓
Create hook event
    ↓
Trigger hook (all registered handlers)
    ↓
Command processing continues
    ↓
Session reset
```

## 故障排除

### 钩子未被发现

1. 检查目录结构：

   ```bash
   ls -la ~/.openclaw/hooks/my-hook/
   # Should show: HOOK.md, handler.ts
   ```

2. 验证 HOOK.md 格式:

   ```bash
   cat ~/.openclaw/hooks/my-hook/HOOK.md
   # Should have YAML frontmatter with name and metadata
   ```

3. 列出所有发现的钩子:

   ```bash
   openclaw hooks list
   ```

### 钩子不符合条件

检查要求:

```bash
openclaw hooks info my-hook
```

查找缺失项:

- 二进制文件（检查 PATH）
- 环境变量
- 配置值
- 操作系统兼容性

### 钩子未执行

1. 验证钩子是否已启用:

   ```bash
   openclaw hooks list
   # Should show ✓ next to enabled hooks
   ```

2. 重启网关进程以重新加载钩子。

3. 检查网关日志中的错误:

   ```bash
   ./scripts/clawlog.sh | grep hook
   ```

### 处理程序错误

检查 TypeScript/import 错误:

```bash
# Test import directly
node -e "import('./path/to/handler.ts').then(console.log)"
```

## 迁移指南

### 从旧配置到发现

**之前**:

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "handlers": [
        {
          "event": "command:new",
          "module": "./hooks/handlers/my-handler.ts"
        }
      ]
    }
  }
}
```

**之后**:

1. 创建钩子目录:

   ```bash
   mkdir -p ~/.openclaw/hooks/my-hook
   mv ./hooks/handlers/my-handler.ts ~/.openclaw/hooks/my-hook/handler.ts
   ```

2. 创建 HOOK.md:

   ```markdown
   ---
   name: my-hook
   description: "My custom hook"
   metadata: { "openclaw": { "emoji": "🎯", "events": ["command:new"] } }
   ---

   # My Hook

   Does something useful.
   ```

3. 更新配置:

   ```json
   {
     "hooks": {
       "internal": {
         "enabled": true,
         "entries": {
           "my-hook": { "enabled": true }
         }
       }
     }
   }
   ```

4. 验证并重启网关进程:

   ```bash
   openclaw hooks list
   # Should show: 🎯 my-hook ✓
   ```

**迁移的好处**:

- 自动发现
- CLI 管理
- 合格性检查
- 更好的文档
- 一致的结构

## 参见

- [CLI 参考: hooks](/cli/hooks)
- [捆绑钩子 README](https://github.com/openclaw/openclaw/tree/main/src/hooks/bundled)
- [Webhook 钩子](/automation/webhook)
- [配置](/gateway/configuration#hooks)