---
summary: "Hooks: event-driven automation for commands and lifecycle events"
read_when:
  - You want event-driven automation for /new, /reset, /stop, and agent lifecycle events
  - You want to build, install, or debug hooks
title: "Hooks"
---
# 钩子（Hooks）

钩子提供了一套可扩展的事件驱动系统，用于在响应代理（agent）命令和事件时自动执行操作。钩子会自动从目录中发现，并可通过 CLI 命令进行管理，其方式与 OpenClaw 中技能（skills）的工作方式类似。

## 快速入门

钩子是小型脚本，在某些事件发生时运行。共分为两类：

- **钩子**（本页内容）：在网关（Gateway）内部运行，当代理事件触发时执行，例如 `/new`、`/reset`、`/stop` 或生命周期事件。
- **Webhook（网络钩子）**：外部 HTTP Webhook，允许其他系统触发 OpenClaw 中的任务。参见 [Webhook 钩子](/automation/webhook)，或使用 `openclaw webhooks` 获取 Gmail 辅助命令。

钩子也可打包在插件中；详见 [插件](/tools/plugin#plugin-hooks)。

常见用途包括：

- 在重置会话时保存内存快照
- 为排查问题或满足合规要求而保留命令审计日志
- 在会话启动或结束时触发后续自动化流程
- 在事件触发时向代理工作区写入文件或调用外部 API

只要你会编写一个小型 TypeScript 函数，就能编写一个钩子。钩子会被自动发现，你可通过 CLI 启用或禁用它们。

## 概览

钩子系统支持你实现以下功能：

- 当发出 `/new` 命令时，将当前会话上下文保存至内存
- 记录所有命令以供审计
- 在代理生命周期事件上触发自定义自动化流程
- 在不修改核心代码的前提下扩展 OpenClaw 的行为

## 入门指南

### 预装钩子

OpenClaw 自带四个预装钩子，会自动被发现：

- **💾 session-memory**：在发出 `/new` 命令时，将当前会话上下文保存至你的代理工作区（默认路径为 `~/.openclaw/workspace/memory/`）
- **📎 bootstrap-extra-files**：在 `agent:bootstrap` 过程中，根据配置的 glob 模式或路径模式，向工作区注入额外的初始化文件
- **📝 command-logger**：将所有命令事件记录到 `~/.openclaw/logs/commands.log`
- **🚀 boot-md**：网关启动时运行 `BOOT.md`（需启用内部钩子）

列出可用钩子：

```bash
openclaw hooks list
```

启用某个钩子：

```bash
openclaw hooks enable session-memory
```

检查钩子状态：

```bash
openclaw hooks check
```

获取详细信息：

```bash
openclaw hooks info session-memory
```

### 初始设置（Onboarding）

在初始设置流程（`openclaw onboard`）中，系统会提示你启用推荐的钩子。向导将自动发现符合条件的钩子并提供选择界面。

## 钩子发现机制

钩子会按优先级顺序从以下三个目录中自动发现：

1. **工作区钩子**：`<workspace>/hooks/`（每个代理专属，优先级最高）
2. **托管钩子**：`~/.openclaw/hooks/`（用户安装，跨工作区共享）
3. **预装钩子**：`<openclaw>/dist/hooks/bundled/`（随 OpenClaw 一同发布）

托管钩子目录可以是单个钩子，也可以是钩子包（即一个包目录）。

每个钩子均为一个包含如下结构的目录：

```
my-hook/
├── HOOK.md          # Metadata + documentation
└── handler.ts       # Handler implementation
```

## 钩子包（npm / 归档包）

钩子包是标准的 npm 包，通过 `openclaw.hooks` 在 `package.json` 中导出一个或多个钩子。安装方式如下：

```bash
openclaw hooks install <path-or-spec>
```

npm 规范仅支持注册表（registry）形式（即包名 + 可选的精确版本号或 dist-tag）。Git / URL / 文件规范及 semver 范围均不被接受。

裸规范（bare spec）和 `@latest` 默认保持稳定通道（stable track）。若 npm 将其中任一解析为预发布版本（prerelease），OpenClaw 将中止安装，并要求你显式选择加入，例如指定预发布标签 `@beta`/`@rc`，或指定精确的预发布版本号。

示例 `package.json`：

```json
{
  "name": "@acme/my-hooks",
  "version": "0.1.0",
  "openclaw": {
    "hooks": ["./hooks/my-hook", "./hooks/other-hook"]
  }
}
```

每个条目指向一个包含 `HOOK.md` 和 `handler.ts`（或 `index.ts`）的钩子目录。钩子包可自带依赖项，这些依赖将安装在 `~/.openclaw/hooks/<id>` 下。每个 `openclaw.hooks` 条目在符号链接解析后，必须仍位于包目录内；任何试图跳出包目录的条目都将被拒绝。

安全说明：`openclaw hooks install` 使用 `npm install --ignore-scripts`（不执行生命周期脚本）安装依赖。请确保钩子包的依赖树“纯为 JS/TS”，避免使用依赖于 `postinstall` 构建的包。

## 钩子结构

### HOOK.md 格式

`HOOK.md` 文件包含 YAML 前置元数据（frontmatter）及 Markdown 文档：

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

`metadata.openclaw` 对象支持以下字段：

- **`emoji`**：CLI 中显示的 Emoji（例如 `"💾"`）
- **`events`**：监听的事件数组（例如 `["command:new", "command:reset"]`）
- **`export`**：要使用的具名导出（默认为 `"default"`）
- **`homepage`**：文档 URL
- **`requires`**：可选的前置要求
  - **`bins`**：PATH 中必需的二进制程序（例如 `["git", "node"]`）
  - **`anyBins`**：至少需存在其中一种二进制程序
  - **`env`**：必需的环境变量
  - **`config`**：必需的配置路径（例如 `["workspace.dir"]`）
  - **`os`**：必需的平台（例如 `["darwin", "linux"]`）
- **`always`**：跳过兼容性检查（布尔值）
- **`install`**：安装方式（对预装钩子而言为 `[{"id":"bundled","kind":"bundled"}]`）

### 处理器实现

`handler.ts` 文件导出一个 `HookHandler` 函数：

```typescript
const myHandler = async (event) => {
  // Only trigger on 'new' command
  if (event.type !== "command" || event.action !== "new") {
    return;
  }

  console.log(`[my-hook] New command triggered`);
  console.log(`  Session: ${event.sessionKey}`);
  console.log(`  Timestamp: ${event.timestamp.toISOString()}`);

  // Your custom logic here

  // Optionally send message to user
  event.messages.push("✨ My hook executed!");
};

export default myHandler;
```

#### 事件上下文

每个事件均包含以下内容：

```typescript
{
  type: 'command' | 'session' | 'agent' | 'gateway' | 'message',
  action: string,              // e.g., 'new', 'reset', 'stop', 'received', 'sent'
  sessionKey: string,          // Session identifier
  timestamp: Date,             // When the event occurred
  messages: string[],          // Push messages here to send to user
  context: {
    // Command events:
    sessionEntry?: SessionEntry,
    sessionId?: string,
    sessionFile?: string,
    commandSource?: string,    // e.g., 'whatsapp', 'telegram'
    senderId?: string,
    workspaceDir?: string,
    bootstrapFiles?: WorkspaceBootstrapFile[],
    cfg?: OpenClawConfig,
    // Message events (see Message Events section for full details):
    from?: string,             // message:received
    to?: string,               // message:sent
    content?: string,
    channelId?: string,
    success?: boolean,         // message:sent
  }
}
```

## 事件类型

### 命令事件

在代理发出命令时触发：

- **`command`**：所有命令事件（通用监听器）
- **`command:new`**：当发出 `/new` 命令时
- **`command:reset`**：当发出 `/reset` 命令时
- **`command:stop`**：当发出 `/stop` 命令时

### 会话事件

- **`session:compact:before`**：压缩（compaction）汇总历史记录前一刻
- **`session:compact:after`**：压缩完成并附带摘要元数据之后

内部钩子载荷将这些事件作为 `type: "session"` 发出，其键为 `action: "compact:before"` / `action: "compact:after"`；监听器则使用上方组合后的键进行订阅。具体处理器注册使用字面量键格式 `${type}:${action}`。对于这些事件，请注册 `session:compact:before` 和 `session:compact:after`。

### 代理事件

- **`agent:bootstrap`**：在向工作区注入初始化文件之前（钩子可修改 `context.bootstrapFiles`）

### 网关事件

在网关启动时触发：

- **`gateway:startup`**：通道启动且钩子加载完毕之后

### 消息事件

在接收或发送消息时触发：

- **`message`**：所有消息事件（通用监听器）
- **`message:received`**：从任意通道接收到入站消息时触发。该事件在媒体理解（media understanding）之前较早阶段触发。内容可能包含尚未处理的媒体附件原始占位符，例如 `<media:audio>`。
- **`message:transcribed`**：消息已完全处理完毕（含音频转录与链接理解）后触发。此时，`transcript` 包含音频消息的完整转录文本。当你需要访问已转录的音频内容时，请使用此钩子。
- **`message:preprocessed`**：在所有媒体及链接理解完成后，为每条消息触发一次，使钩子可在代理看到消息前，访问完全增强的消息体（含转录文本、图像描述、链接摘要等）。
- **`message:sent`**：出站消息成功发送后触发

#### 消息事件上下文

消息事件包含关于该消息的丰富上下文信息：

```typescript
// message:received context
{
  from: string,           // Sender identifier (phone number, user ID, etc.)
  content: string,        // Message content
  timestamp?: number,     // Unix timestamp when received
  channelId: string,      // Channel (e.g., "whatsapp", "telegram", "discord")
  accountId?: string,     // Provider account ID for multi-account setups
  conversationId?: string, // Chat/conversation ID
  messageId?: string,     // Message ID from the provider
  metadata?: {            // Additional provider-specific data
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

// message:sent context
{
  to: string,             // Recipient identifier
  content: string,        // Message content that was sent
  success: boolean,       // Whether the send succeeded
  error?: string,         // Error message if sending failed
  channelId: string,      // Channel (e.g., "whatsapp", "telegram", "discord")
  accountId?: string,     // Provider account ID
  conversationId?: string, // Chat/conversation ID
  messageId?: string,     // Message ID returned by the provider
  isGroup?: boolean,      // Whether this outbound message belongs to a group/channel context
  groupId?: string,       // Group/channel identifier for correlation with message:received
}

// message:transcribed context
{
  body?: string,          // Raw inbound body before enrichment
  bodyForAgent?: string,  // Enriched body visible to the agent
  transcript: string,     // Audio transcript text
  channelId: string,      // Channel (e.g., "telegram", "whatsapp")
  conversationId?: string,
  messageId?: string,
}

// message:preprocessed context
{
  body?: string,          // Raw inbound body
  bodyForAgent?: string,  // Final enriched body after media/link understanding
  transcript?: string,    // Transcript when audio was present
  channelId: string,      // Channel (e.g., "telegram", "whatsapp")
  conversationId?: string,
  messageId?: string,
  isGroup?: boolean,
  groupId?: string,
}
```

#### 示例：消息记录器钩子（Message Logger Hook）

```typescript
const isMessageReceivedEvent = (event: { type: string; action: string }) =>
  event.type === "message" && event.action === "received";
const isMessageSentEvent = (event: { type: string; action: string }) =>
  event.type === "message" && event.action === "sent";

const handler = async (event) => {
  if (isMessageReceivedEvent(event as { type: string; action: string })) {
    console.log(`[message-logger] Received from ${event.context.from}: ${event.context.content}`);
  } else if (isMessageSentEvent(event as { type: string; action: string })) {
    console.log(`[message-logger] Sent to ${event.context.to}: ${event.context.content}`);
  }
};

export default handler;
```

### 工具结果钩子（插件 API）

这些钩子并非事件流监听器；它们允许插件在 OpenClaw 持久化工具结果之前，以同步方式调整工具结果。

- **`tool_result_persist`**：在工具结果写入会话转录（session transcript）前对其进行转换。必须为同步操作；返回更新后的工具结果载荷，或返回 `undefined` 以保持原样不变。参见 [Agent Loop](/concepts/agent-loop)。

### 插件钩子事件

通过插件钩子运行器公开的压缩（compaction）生命周期钩子：

- **`before_compaction`**：在压缩开始前执行，附带计数/Token 元数据
- **`after_compaction`**：在压缩完成后执行，附带压缩摘要元数据

### 未来计划支持的事件类型

- **`session:start`**：当新会话启动时触发
- **`session:end`**：当会话结束时触发
- **`agent:error`**：当 Agent 遇到错误时触发

## 创建自定义钩子

### 1. 选择位置

- **工作区钩子**（`<workspace>/hooks/`）：按 Agent 级别配置，优先级最高
- **托管钩子**（`~/.openclaw/hooks/`）：跨多个工作区共享

### 2. 创建目录结构

```bash
mkdir -p ~/.openclaw/hooks/my-hook
cd ~/.openclaw/hooks/my-hook
```

### 3. 创建 HOOK.md

```markdown
---
name: my-hook
description: "Does something useful"
metadata: { "openclaw": { "emoji": "🎯", "events": ["command:new"] } }
---

# My Custom Hook

This hook does something useful when you issue `/new`.
```

### 4. 创建 handler.ts

```typescript
const handler = async (event) => {
  if (event.type !== "command" || event.action !== "new") {
    return;
  }

  console.log("[my-hook] Running!");
  // Your logic here
};

export default handler;
```

### 5. 启用并测试

```bash
# Verify hook is discovered
openclaw hooks list

# Enable it
openclaw hooks enable my-hook

# Restart your gateway process (menu bar app restart on macOS, or restart your dev process)

# Trigger the event
# Send /new via your messaging channel
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

### 按钩子配置

钩子可拥有自定义配置：

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

为向后兼容，旧配置格式仍可使用：

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

注意：`module` 必须为相对于工作区的路径。绝对路径及超出工作区范围的路径遍历均被拒绝。

**迁移建议**：对新钩子请使用基于发现（discovery-based）的新系统；旧版处理器将在基于目录的钩子之后加载。

## CLI 命令

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

### 查看钩子信息

```bash
# Show detailed info about a hook
openclaw hooks info session-memory

# JSON output
openclaw hooks info session-memory --json
```

### 检查启用资格

```bash
# Show eligibility summary
openclaw hooks check

# JSON output
openclaw hooks check --json
```

### 启用 / 禁用钩子

```bash
# Enable a hook
openclaw hooks enable session-memory

# Disable a hook
openclaw hooks disable command-logger
```

## 内置钩子参考

### session-memory

当你发出 `/new` 命令时，将当前会话上下文保存至内存。

**触发事件**：`command:new`

**前提条件**：必须已配置 `workspace.dir`

**输出**：`<workspace>/memory/YYYY-MM-DD-slug.md`（默认为 `~/.openclaw/workspace`）

**功能说明**：

1. 利用重置前的会话条目定位正确的转录文件
2. 提取最近 15 行对话内容
3. 调用大语言模型（LLM）生成描述性文件名 slug
4. 将会话元数据保存至按日期命名的内存文件中

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
- `2026-01-16-1430.md`（若 slug 生成失败，则回退为时间戳）

**启用方式**：

```bash
openclaw hooks enable session-memory
```

### bootstrap-extra-files

在 `agent:bootstrap` 过程中注入额外的引导文件（例如单体仓库本地的 `AGENTS.md` / `TOOLS.md`）。

**触发事件**：`agent:bootstrap`

**前提条件**：必须已配置 `workspace.dir`

**输出**：不写入任何文件；仅在内存中修改引导上下文。

**配置项**：

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

**注意事项**：

- 路径相对于工作区解析。
- 文件必须位于工作区内（经 realpath 校验）。
- 仅加载已识别的引导文件基础名（basename）。
- 子 Agent 白名单保持不变（仅限 `AGENTS.md` 和 `TOOLS.md`）。

**启用方式**：

```bash
openclaw hooks enable bootstrap-extra-files
```

### command-logger

将所有命令事件记录到集中式审计日志文件中。

**触发事件**：`command`

**前提条件**：无

**输出**：`~/.openclaw/logs/commands.log`

**功能说明**：

1. 捕获事件详情（命令动作、时间戳、会话密钥、发送方 ID、来源）
2. 以 JSONL 格式追加至日志文件
3. 在后台静默运行

**示例日志条目**：

```jsonl
{"timestamp":"2026-01-16T14:30:00.000Z","action":"new","sessionKey":"agent:main:main","senderId":"+1234567890","source":"telegram"}
{"timestamp":"2026-01-16T15:45:22.000Z","action":"stop","sessionKey":"agent:main:main","senderId":"user@example.com","source":"whatsapp"}
```

**查看日志**：

```bash
# View recent commands
tail -n 20 ~/.openclaw/logs/commands.log

# Pretty-print with jq
cat ~/.openclaw/logs/commands.log | jq .

# Filter by action
grep '"action":"new"' ~/.openclaw/logs/commands.log | jq .
```

**启用方式**：

```bash
openclaw hooks enable command-logger
```

### boot-md

网关启动时（通道启动后）运行 `BOOT.md`。  
此钩子需启用内部钩子（internal hooks）方可执行。

**触发事件**：`gateway:startup`

**前提条件**：必须已配置 `workspace.dir`

**功能说明**：

1. 从工作区读取 `BOOT.md`
2. 通过 Agent 运行器执行其中指令
3. 使用消息工具发送任何请求的出站消息

**启用方式**：

```bash
openclaw hooks enable boot-md
```

## 最佳实践

### 保持处理器快速响应

钩子在命令处理期间运行。请保持其轻量级：

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

始终将存在风险的操作包裹起来：

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

### 尽早过滤事件

如果事件不相关，请尽早返回：

```typescript
const handler: HookHandler = async (event) => {
  // Only handle 'new' commands
  if (event.type !== "command" || event.action !== "new") {
    return;
  }

  // Your logic here
};
```

### 使用特定的事件键

在元数据中尽可能指定确切的事件：

```yaml
metadata: { "openclaw": { "events": ["command:new"] } } # Specific
```

而不是：

```yaml
metadata: { "openclaw": { "events": ["command"] } } # General - more overhead
```

## 调试

### 启用钩子日志记录

网关在启动时会记录钩子加载情况：

```
Registered hook: session-memory -> command:new
Registered hook: bootstrap-extra-files -> agent:bootstrap
Registered hook: command-logger -> command
Registered hook: boot-md -> gateway:startup
```

### 检查发现过程

列出所有已发现的钩子：

```bash
openclaw hooks list --verbose
```

### 检查注册情况

在您的处理器中，记录其被调用的时间：

```typescript
const handler: HookHandler = async (event) => {
  console.log("[my-handler] Triggered:", event.type, event.action);
  // Your logic
};
```

### 验证适用性

检查钩子为何不满足适用条件：

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

在隔离环境中测试您的处理器：

```typescript
import { test } from "vitest";
import myHandler from "./hooks/my-hook/handler.js";

test("my handler works", async () => {
  const event = {
    type: "command",
    action: "new",
    sessionKey: "test-session",
    timestamp: new Date(),
    messages: [],
    context: { foo: "bar" },
  };

  await myHandler(event);

  // Assert side effects
});
```

## 架构

### 核心组件

- **`src/hooks/types.ts`**: 类型定义  
- **`src/hooks/workspace.ts`**: 目录扫描与加载  
- **`src/hooks/frontmatter.ts`**: HOOK.md 元数据解析  
- **`src/hooks/config.ts`**: 适用性检查  
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

2. 验证 HOOK.md 格式：

   ```bash
   cat ~/.openclaw/hooks/my-hook/HOOK.md
   # Should have YAML frontmatter with name and metadata
   ```

3. 列出所有已发现的钩子：

   ```bash
   openclaw hooks list
   ```

### 钩子不满足适用条件

检查要求：

```bash
openclaw hooks info my-hook
```

查找缺失项：

- 二进制文件（检查 PATH）  
- 环境变量  
- 配置值  
- 操作系统兼容性  

### 钩子未执行

1. 验证钩子是否已启用：

   ```bash
   openclaw hooks list
   # Should show ✓ next to enabled hooks
   ```

2. 重启您的网关进程，以便重新加载钩子。

3. 检查网关日志中是否存在错误：

   ```bash
   ./scripts/clawlog.sh | grep hook
   ```

### 处理器错误

检查 TypeScript / 导入错误：

```bash
# Test import directly
node -e "import('./path/to/handler.ts').then(console.log)"
```

## 迁移指南

### 从传统配置迁移到自动发现

**迁移前**：

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

**迁移后**：

1. 创建钩子目录：

   ```bash
   mkdir -p ~/.openclaw/hooks/my-hook
   mv ./hooks/handlers/my-handler.ts ~/.openclaw/hooks/my-hook/handler.ts
   ```

2. 创建 HOOK.md：

   ```markdown
   ---
   name: my-hook
   description: "My custom hook"
   metadata: { "openclaw": { "emoji": "🎯", "events": ["command:new"] } }
   ---

   # My Hook

   Does something useful.
   ```

3. 更新配置：

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

4. 验证并重启您的网关进程：

   ```bash
   openclaw hooks list
   # Should show: 🎯 my-hook ✓
   ```

**迁移优势**：

- 自动发现  
- CLI 管理  
- 适用性检查  
- 更完善的文档  
- 统一的结构  

## 参见

- [CLI 参考：hooks](/cli/hooks)  
- [内置钩子 README](https://github.com/openclaw/openclaw/tree/main/src/hooks/bundled)  
- [Webhook 钩子](/automation/webhook)  
- [配置](/gateway/configuration#hooks)