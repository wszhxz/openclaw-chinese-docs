---
summary: "Hooks: event-driven automation for commands and lifecycle events"
read_when:
  - You want event-driven automation for /new, /reset, /stop, and agent lifecycle events
  - You want to build, install, or debug hooks
title: "Hooks"
---
# 钩子

钩子提供了一个可扩展的事件驱动系统，用于根据代理命令和事件自动执行操作。钩子可以从目录中自动发现，并通过 CLI 命令进行管理，类似于 OpenClaw 中技能的工作方式。

## 了解概况

钩子是当某事发生时运行的小型脚本。有两种类型：

- **钩子**（本页面）：在网关内部运行，当代理事件触发时，如 `/new`, `/reset`, `/stop`, 或生命周期事件。
- **Webhook**：外部 HTTP Webhook，允许其他系统触发 OpenClaw 中的工作。参见 [Webhook Hooks](/automation/webhook) 或使用 `openclaw webhooks` 进行 Gmail 辅助命令。

钩子也可以打包在插件中；参见 [Plugins](/tools/plugin#plugin-hooks)。

常见用途：

- 重置会话时保存内存快照
- 保留命令的审计跟踪以用于故障排除或合规性
- 在会话开始或结束时触发后续自动化
- 当事件触发时写入文件到代理工作区或调用外部 API

如果你能编写小型 TypeScript 函数，你就能编写钩子。钩子会自动被发现，你可以通过 CLI 启用或禁用它们。

## 概述

钩子系统允许你：

- 当发出 `/new` 时将会话上下文保存到内存
- 记录所有命令以供审计
- 在代理生命周期事件上触发自定义自动化
- 扩展 OpenClaw 的行为而无需修改核心代码

## 入门

### 捆绑钩子

OpenClaw 附带四个自动发现的捆绑钩子：

- **💾 session-memory**：当你发出 `/new` 时，将会话上下文保存到你的代理工作区（默认 `~/.openclaw/workspace/memory/`）
- **📎 bootstrap-extra-files**：在 `agent:bootstrap` 期间从配置的 glob/路径模式注入额外的工作区引导文件
- **📝 command-logger**：将所有命令事件记录到 `~/.openclaw/logs/commands.log`
- **🚀 boot-md**：当网关启动时运行 `BOOT.md`（需要启用内部钩子）

列出可用钩子：

```bash
openclaw hooks list
```

启用钩子：

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

### 初始设置

在初始设置期间 (`openclaw onboard`)，你会被提示启用推荐的钩子。向导会自动发现符合条件的钩子并呈现供选择。

## 钩子发现

钩子从三个目录中自动发现（按优先级顺序）：

1. **工作区钩子**：`<workspace>/hooks/`（每个代理专用，最高优先级）
2. **托管钩子**：`~/.openclaw/hooks/`（用户安装，跨工作区共享）
3. **捆绑钩子**：`<openclaw>/dist/hooks/bundled/`（随 OpenClaw 一起提供）

托管钩子目录可以是 **单个钩子** 或 **钩子包**（软件包目录）。

每个钩子是一个包含以下内容的目录：

```
my-hook/
├── HOOK.md          # Metadata + documentation
└── handler.ts       # Handler implementation
```

## 钩子包 (npm/归档)

钩子包是标准的 npm 软件包，通过 `openclaw.hooks` 在 `package.json` 中导出一个或多个钩子。使用以下命令安装：

```bash
openclaw hooks install <path-or-spec>
```

Npm 规范仅限注册表（软件包名称 + 可选确切版本或 dist-tag）。Git/URL/file 规范和 semver 范围会被拒绝。

裸规范和 `@latest` 保持在稳定轨道上。如果 npm 解析其中任何一个为预发布版，OpenClaw 会停止并要求你明确选择加入，使用预发布标签如 `@beta`/`@rc` 或确切预发布版本。

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

每个条目指向一个包含 `HOOK.md` 和 `handler.ts`（或 `index.ts`）的钩子目录。钩子包可以附带依赖项；它们将安装在 `~/.openclaw/hooks/<id>` 下。每个 `openclaw.hooks` 条目必须在符号链接解析后保留在软件包目录内；逃逸的条目将被拒绝。

安全说明：`openclaw hooks install` 使用 `npm install --ignore-scripts` 安装依赖项（无生命周期脚本）。保持钩子包依赖树为“纯 JS/TS"，避免依赖 `postinstall` 构建的软件包。

## 钩子结构

### HOOK.md 格式

`HOOK.md` 文件包含 YAML frontmatter 加 Markdown 文档的元数据：

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

- **`emoji`**：CLI 显示的表情符号（例如 `"💾"`）
- **`events`**：要监听的事件数组（例如 `["command:new", "command:reset"]`）
- **`export`**：要使用的命名导出（默认为 `"default"`）
- **`homepage`**：文档 URL
- **`requires`**：可选要求
  - **`bins`**：PATH 上的必需二进制文件（例如 `["git", "node"]`）
  - **`anyBins`**：必须存在这些二进制文件中的至少一个
  - **`env`**：必需环境变量
  - **`config`**：必需配置路径（例如 `["workspace.dir"]`）
  - **`os`**：必需平台（例如 `["darwin", "linux"]`）
- **`always`**：绕过资格检查（布尔值）
- **`install`**：安装方法（对于捆绑钩子：`[{"id":"bundled","kind":"bundled"}]`）

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

每个事件包括：

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

当发出代理命令时触发：

- **`command`**：所有命令事件（通用监听器）
- **`command:new`**：当发出 `/new` 命令时
- **`command:reset`**：当发出 `/reset` 命令时
- **`command:stop`**：当发出 `/stop` 命令时

### 会话事件

- **`session:compact:before`**：在压缩总结历史记录之前
- **`session:compact:after`**：压缩完成且带有摘要元数据之后

内部钩子负载将这些作为 `type: "session"` 发出，带有 `action: "compact:before"` / `action: "compact:after"`；监听器使用上述组合键订阅。特定处理器注册使用字面量键格式 `${type}:${action}`。对于这些事件，注册 `session:compact:before` 和 `session:compact:after`。

### 代理事件

- **`agent:bootstrap`**：在工作区引导文件注入之前（钩子可以修改 `context.bootstrapFiles`）

### 网关事件

当网关启动时触发：

- **`gateway:startup`**：通道启动且钩子加载之后

### 消息事件

当接收或发送消息时触发：

- **`message`**：所有消息事件（通用监听器）
- **`message:received`**：当从任何通道接收传入消息时。在处理早期触发，早于媒体理解。内容可能包含原始占位符，如 `<media:audio>`，用于尚未处理的媒体附件。
- **`message:transcribed`**：当消息已完全处理，包括音频转录和链接理解时。此时，`transcript` 包含音频消息的完整转录文本。当你需要访问转录的音频内容时使用此钩子。
- **`message:preprocessed`**：在所有媒体 + 链接理解完成后为每条消息触发，使钩子在代理看到之前能够访问完全丰富的正文（转录、图像描述、链接摘要）。
- **`message:sent`**：当传出消息成功发送时

#### 消息事件上下文

消息事件包含有关消息的丰富上下文：

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

#### 示例：消息记录器钩子

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

这些钩子不是事件流监听器；它们允许插件在 OpenClaw 持久化之前同步调整工具结果。

- **`tool_result_persist`**：在写入会话记录之前转换工具结果。必须是同步的；返回更新后的工具结果负载或 `undefined` 以保持原样。参见 [Agent Loop](/concepts/agent-loop)。

### 插件钩子事件

通过插件钩子运行器暴露的压缩生命周期钩子：

- **`before_compaction`**：在压缩前运行，包含计数/令牌元数据
- **`after_compaction`**：在压缩后运行，包含压缩摘要元数据

### 未来事件

计划中的事件类型：

- **`session:start`**：当新会话开始时
- **`session:end`**：当会话结束时
- **`agent:error`**：当代理遇到错误时

## 创建自定义钩子

### 1. 选择位置

- **工作区钩子** (`<workspace>/hooks/`)：每个代理，优先级最高
- **托管钩子** (`~/.openclaw/hooks/`)：跨工作区共享

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

### 5. 启用和测试

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

### 每钩子配置

钩子可以拥有自定义配置：

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

从额外目录加载钩子：

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

### 旧配置格式（仍受支持）

旧配置格式仍然有效以向后兼容：

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

注意：`module` 必须是相对于工作区的路径。绝对路径和工作区外的遍历将被拒绝。

**迁移**：为新的钩子使用基于发现的新系统。旧处理器在基于目录的钩子之后加载。

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

## 捆绑钩子参考

### session-memory

当您发出 `/new` 时将会话上下文保存到内存。

**事件**：`command:new`

**要求**：必须配置 `workspace.dir`

**输出**：`<workspace>/memory/YYYY-MM-DD-slug.md`（默认为 `~/.openclaw/workspace`）

**功能**：

1. 使用重置前的会话条目定位正确的会话记录
2. 提取最后 15 行对话
3. 使用 LLM 生成描述性文件名标识符
4. 将会话元数据保存到带日期的内存文件

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
- `2026-01-16-1430.md`（如果标识符生成失败则回退时间戳）

**启用**：

```bash
openclaw hooks enable session-memory
```

### bootstrap-extra-files

在 `agent:bootstrap` 期间注入额外的引导文件（例如 monorepo-local `AGENTS.md` / `TOOLS.md`）。

**事件**：`agent:bootstrap`

**要求**：必须配置 `workspace.dir`

**输出**：不写入文件；引导上下文仅修改内存。

**配置**：

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

**注意**：

- 路径相对于工作区解析。
- 文件必须保留在工作区内（经过 realpath 检查）。
- 仅加载识别的引导基名。
- 子代理白名单得以保留（仅限 `AGENTS.md` 和 `TOOLS.md`）。

**启用**：

```bash
openclaw hooks enable bootstrap-extra-files
```

### command-logger

将所有命令事件记录到集中式审计文件中。

**事件**：`command`

**要求**：无

**输出**：`~/.openclaw/logs/commands.log`

**功能**：

1. 捕获事件详情（命令操作、时间戳、会话键、发送者 ID、来源）
2. 以 JSONL 格式追加到日志文件
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

**启用**：

```bash
openclaw hooks enable command-logger
```

### boot-md

当网关启动时（通道启动后）运行 `BOOT.md`。
必须启用内部钩子才能运行此功能。

**事件**：`gateway:startup`

**要求**：必须配置 `workspace.dir`

**功能**：

1. 从您的工作区读取 `BOOT.md`
2. 通过代理运行器运行指令
3. 通过消息工具发送任何请求的出站消息

**启用**：

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

始终包装风险操作：

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

在处理程序中，记录它被调用时的日志：

```typescript
const handler: HookHandler = async (event) => {
  console.log("[my-handler] Triggered:", event.type, event.action);
  // Your logic
};
```

### 验证资格

检查钩子不符合资格的原因：

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

隔离测试您的处理程序：

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

### 未发现钩子

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

### 钩子不符合资格

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

2. 重启您的网关进程以便重新加载钩子。

3. 检查网关日志是否有错误：

   ```bash
   ./scripts/clawlog.sh | grep hook
   ```

### 处理程序错误

检查 TypeScript/import 错误：

```bash
# Test import directly
node -e "import('./path/to/handler.ts').then(console.log)"
```

## 迁移指南

### 从旧版配置到发现

**之前**：

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

**之后**：

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

**迁移的好处**：

- 自动发现
- CLI 管理
- 资格检查
- 更好的文档
- 一致的结构

## 另请参阅

- [CLI 参考：hooks](/cli/hooks)
- [捆绑钩子 README](https://github.com/openclaw/openclaw/tree/main/src/hooks/bundled)
- [Webhook 钩子](/automation/webhook)
- [配置](/gateway/configuration#hooks)