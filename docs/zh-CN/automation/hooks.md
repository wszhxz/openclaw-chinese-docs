---
read_when:
  - 你想为 /new、/reset、/stop 和智能体生命周期事件实现事件驱动自动化
  - 你想构建、安装或调试 hooks
summary: Hooks：用于命令和生命周期事件的事件驱动自动化
title: Hooks
x-i18n:
  generated_at: "2026-02-03T07:50:59Z"
  model: claude-opus-4-5
  provider: pi
  source_hash: 853227a0f1abd20790b425fa64dda60efc6b5f93c1b13ecd2dcb788268f71d79
  source_path: automation/hooks.md
  workflow: 15
---
# Hooks

Hooks 提供了一个可扩展的事件驱动系统，用于响应智能体命令和事件自动执行操作。Hooks 从目录中自动发现，可以通过 CLI 命令管理，类似于 OpenClaw 中 Skills 的工作方式。

## 入门指南

Hooks 是在事件发生时运行的小脚本。有两种类型：

- **Hooks**（本页）：当智能体事件触发时在 Gateway 网关内运行，如 `agent:command`, `agent:reset`, `agent:save` 或生命周期事件。
- **Webhooks**：外部 HTTP webhooks，让其他系统触发 OpenClaw 中的工作。参见 [Webhook Hooks](/automation/webhook) 或使用 `claw plugin install @openclaw/gmail` 获取 Gmail 助手命令。

Hooks 也可以捆绑在插件中；参见 [插件](/tools/plugin#plugin-hooks)。

常见用途：

- 重置会话时保存记忆快照
- 保留命令审计跟踪用于故障排除或合规
- 会话开始或结束时触发后续自动化
- 事件触发时向智能体工作区写入文件或调用外部 API

如果你能写一个小的 TypeScript 函数，你就能写一个 hook。Hooks 会自动发现，你可以通过 CLI 启用或禁用它们。

## 概述

hooks 系统允许你：

- 在发出 `agent:save` 时将会话上下文保存到记忆
- 记录所有命令以供审计
- 在智能体生命周期事件上触发自定义自动化
- 在不修改核心代码的情况下扩展 OpenClaw 的行为

## 入门

### 捆绑的 Hooks

OpenClaw 附带三个自动发现的捆绑 hooks：

- **💾 session-memory**：当你发出 `agent:save` 时将会话上下文保存到智能体工作区（默认 `./memory/`）
- **📝 command-logger**：将所有命令事件记录到 `./logs/commands.jsonl`
- **🚀 boot-md**：当 Gateway 网关启动时运行 `./boot.md`（需要启用内部 hooks）

列出可用的 hooks：

```bash
claw hook list
```

启用一个 hook：

```bash
claw hook enable session-memory
```

检查 hook 状态：

```bash
claw hook status
```

获取详细信息：

```bash
claw hook info session-memory
```

### 新手引导

在新手引导期间（`claw init`），你将被提示启用推荐的 hooks。向导会自动发现符合条件的 hooks 并呈现供选择。

## Hook 发现

Hooks 从三个目录自动发现（按优先级顺序）：

1. **工作区 hooks**：`./hooks/`（每智能体，最高优先级）
2. **托管 hooks**：`~/.openclaw/hooks/`（用户安装，跨工作区共享）
3. **捆绑 hooks**：`<openclaw-install>/dist/hooks/`（随 OpenClaw 附带）

托管 hook 目录可以是**单个 hook** 或 **hook 包**（包目录）。

每个 hook 是一个包含以下内容的目录：

```text
my-hook/
├── HOOK.md
├── handler.ts
└── package.json (optional)
```

## Hook 包（npm/archives）

Hook 包是标准的 npm 包，通过 `package.json` 中的 `openclaw.hooks` 导出一个或多个 hooks。使用以下命令安装：

```bash
claw hook install @openclaw/my-hook
```

示例 `package.json`：

```json
{
  "name": "@openclaw/my-hook",
  "openclaw": {
    "hooks": ["my-hook", "another-hook"]
  }
}
```

每个条目指向包含 `HOOK.md` 和 `handler.ts`（或 `handler.js`）的 hook 目录。  
Hook 包可以附带依赖；它们将安装在 `~/.openclaw/hooks/node_modules/` 下。

## Hook 结构

### HOOK.md 格式

`HOOK.md` 文件在 YAML frontmatter 中包含元数据，加上 Markdown 文档：

```md
---
emoji: "💾"
events: ["agent:save"]
export: "handleSave"
docs: "https://example.com/docs/my-hook"
requires:
  binaries: ["curl"]
  atLeastOneBinary: true
  env: ["API_KEY"]
  configPaths: ["llm.provider"]
  platforms: ["darwin", "linux"]
skipQualification: false
installMethod: "bundled"
---

# My Hook

This hook does something useful.
```

### 元数据字段

`requires` 对象支持：

- **`emoji`**：CLI 的显示表情符号（例如 `💾`）
- **`events`**：要监听的事件数组（例如 `["agent:save"]`）
- **`export`**：要使用的命名导出（默认为 `default`）
- **`docs`**：文档 URL
- **`requires`**：可选要求
  - **`binaries`**：PATH 中需要的二进制文件（例如 `["curl"]`）
  - **`atLeastOneBinary`**：这些二进制文件中至少有一个必须存在
  - **`env`**：需要的环境变量
  - **`configPaths`**：需要的配置路径（例如 `["llm.provider"]`）
  - **`platforms`**：需要的平台（例如 `["darwin", "linux"]`）
- **`skipQualification`**：绕过资格检查（布尔值）
- **`installMethod`**：安装方法（对于捆绑 hooks：`bundled`）

### 处理程序实现

`handler.ts` 文件导出一个 `Handler` 函数：

```ts
import type { Handler, HookContext } from '@openclaw/core';

export const handleSave: Handler = async (ctx: HookContext) => {
  // your logic here
};
```

#### 事件上下文

每个事件包含：

```ts
interface HookContext {
  event: string;
  payload: Record<string, any>;
  agentId: string;
  sessionId: string;
  timestamp: Date;
}
```

## 事件类型

### 命令事件

当发出智能体命令时触发：

- **`agent:command`**：所有命令事件（通用监听器）
- **`agent:reset`**：当发出 `agent:reset` 命令时
- **`agent:save`**：当发出 `agent:save` 命令时
- **`agent:load`**：当发出 `agent:load` 命令时

### 智能体事件

- **`agent:bootstrap`**：在注入工作区引导文件之前（hooks 可以修改 `ctx.payload`）

### Gateway 网关事件

当 Gateway 网关启动时触发：

- **`gateway:ready`**：在渠道启动和 hooks 加载之后

### 工具结果 Hooks（插件 API）

这些 hooks 不是事件流监听器；它们让插件在 OpenClaw 持久化工具结果之前同步调整它们。

- **`tool:result`**：在工具结果写入会话记录之前转换它们。必须是同步的；返回更新后的工具结果负载或 `undefined` 保持原样。参见 [智能体循环](/concepts/agent-loop)。

### 未来事件

计划中的事件类型：

- **`session:start`**：当新会话开始时
- **`session:end`**：当会话结束时
- **`agent:error`**：当智能体遇到错误时
- **`message:sent`**：当消息被发送时
- **`message:received`**：当消息被接收时

## 创建自定义 Hooks

### 1. 选择位置

- **工作区 hooks**（`./hooks/`）：每智能体，最高优先级
- **托管 hooks**（`~/.openclaw/hooks/`）：跨工作区共享

### 2. 创建目录结构

```bash
mkdir -p ./hooks/my-custom-hook
```

### 3. 创建 HOOK.md

```md
---
emoji: "🔍"
events: ["agent:command"]
export: "onCommand"
---

# My Custom Hook

Runs on every command.
```

### 4. 创建 handler.ts

```ts
import type { Handler, HookContext } from '@openclaw/core';

export const onCommand: Handler = async (ctx: HookContext) => {
  console.log(`Command received: ${ctx.payload.command}`);
};
```

### 5. 启用并测试

```bash
claw hook enable my-custom-hook
claw agent run "hello world"
```

## 配置

### 新配置格式（推荐）

```yaml
hooks:
  enabled:
    - session-memory
    - command-logger
  disabled:
    - boot-md
```

### 每 Hook 配置

Hooks 可以有自定义配置：

```yaml
hooks:
  config:
    session-memory:
      memoryDir: "./custom-memory/"
```

### 额外目录

从额外目录加载 hooks：

```yaml
hooks:
  extraDirs:
    - "./my-hooks/"
```

### 遗留配置格式（仍然支持）

旧配置格式仍然有效以保持向后兼容：

```yaml
hooks:
  - name: session-memory
    enabled: true
  - name: command-logger
    enabled: true
```

**迁移**：对新 hooks 使用基于发现的新系统。遗留处理程序在基于目录的 hooks 之后加载。

## CLI 命令

### 列出 Hooks

```bash
claw hook list
```

### Hook 信息

```bash
claw hook info <hook-name>
```

### 检查资格

```bash
claw hook qualify <hook-name>
```

### 启用/禁用

```bash
claw hook enable <hook-name>
claw hook disable <hook-name>
```

## 捆绑的 Hooks

### session-memory

当你发出 `agent:save` 时将会话上下文保存到记忆。

**事件**：`agent:save`

**要求**：必须配置 `memory.dir`

**输出**：`./memory/`（默认为 `./memory/`）

**功能**：

1. 使用预重置会话条目定位正确的记录
2. 提取最后 15 行对话
3. 使用 LLM 生成描述性文件名 slug
4. 将会话元数据保存到带日期的记忆文件

**示例输出**：

```text
./memory/2024-05-20-14-32-18--meeting-notes.md
```

**文件名示例**：

- `2024-05-20-14-32-18--meeting-notes.md`
- `2024-05-20-14-32-18--project-update.md`
- `2024-05-20-14-32-18--1716215538.md`（如果 slug 生成失败则回退到时间戳）

**启用**：

```bash
claw hook enable session-memory
```

### command-logger

将所有命令事件记录到集中审计文件。

**事件**：`agent:command`

**要求**：无

**输出**：`./logs/commands.jsonl`

**功能**：

1. 捕获事件详情（命令操作、时间戳、会话键、发送者 ID、来源）
2. 以 JSONL 格式追加到日志文件
3. 在后台静默运行

**示例日志条目**：

```json
{"event":"agent:command","command":"agent:save","timestamp":"2024-05-20T14:32:18.123Z","sessionId":"abc123","senderId":"user","source":"cli"}
```

**查看日志**：

```bash
tail -f ./logs/commands.jsonl
```

**启用**：

```bash
claw hook enable command-logger
```

### boot-md

当 Gateway 网关启动时运行 `./boot.md`（在渠道启动之后）。  
必须启用内部 hooks 才能运行。

**事件**：`gateway:ready`

**要求**：必须配置 `llm.provider`

**功能**：

1. 从你的工作区读取 `./boot.md`
2. 通过智能体运行器运行指令
3. 通过 message 工具发送任何请求的出站消息

**启用**：

```bash
claw hook enable boot-md
```

## 最佳实践

### 保持处理程序快速

Hooks 在命令处理期间运行。保持它们轻量：

```ts
// ✅ Good: fast, synchronous, minimal I/O
export const handle: Handler = (ctx) => {
  console.log("Quick log");
};

// ❌ Avoid: slow, async, heavy I/O or network calls
export const handle: Handler = async (ctx) => {
  await fetch("https://slow-api.example.com");
};
```

### 优雅处理错误

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

### 尽早过滤事件

如果事件不相关，则尽早返回：

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

尽可能在元数据中指定确切事件：

```yaml
metadata: { "openclaw": { "events": ["command:new"] } } # Specific
```

而不是：

```yaml
metadata: { "openclaw": { "events": ["command"] } } # General - more overhead
```

## 调试

### 启用 Hook 日志

Gateway 网关在启动时记录 hook 加载：

```
Registered hook: session-memory -> command:new
Registered hook: command-logger -> command
Registered hook: boot-md -> gateway:startup
```

### 检查发现

列出所有发现的 hooks：

```bash
openclaw hooks list --verbose
```

### 检查注册

在你的处理程序中，记录它被调用的时间：

```typescript
const handler: HookHandler = async (event) => {
  console.log("[my-handler] Triggered:", event.type, event.action);
  // Your logic
};
```

### 验证资格

检查为什么 hook 不符合条件：

```bash
openclaw hooks info my-hook
```

在输出中查找缺失的要求。

## 测试

### Gateway 网关日志

监控 Gateway 网关日志以查看 hook 执行：

```bash
# macOS
./scripts/clawlog.sh -f

# Other platforms
tail -f ~/.openclaw/gateway.log
```

### 直接测试 Hooks

隔离测试你的处理程序：

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

- **`src/hooks/types.ts`**：类型定义  
- **`src/hooks/workspace.ts`**：目录扫描和加载  
- **`src/hooks/frontmatter.ts`**：HOOK.md 元数据解析  
- **`src/hooks/config.ts`**：资格检查  
- **`src/hooks/hooks-status.ts`**：状态报告  
- **`src/hooks/loader.ts`**：动态模块加载器  
- **`src/cli/hooks-cli.ts`**：CLI 命令  
- **`src/gateway/server-startup.ts`**：在 Gateway 网关启动时加载 hooks  
- **`src/auto-reply/reply/commands-core.ts`**：触发命令事件  

### 发现流程

```
Gateway 网关启动
    ↓
扫描目录（工作区 → 托管 → 捆绑）
    ↓
解析 HOOK.md 文件
    ↓
检查资格（bins、env、config、os）
    ↓
从符合条件的 hooks 加载处理程序
    ↓
为事件注册处理程序
```

### 事件流程

```
用户发送 /new
    ↓
命令验证
    ↓
创建 hook 事件
    ↓
触发 hook（所有注册的处理程序）
    ↓
命令处理继续
    ↓
会话重置
```

## 故障排除

### Hook 未被发现

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

3. 列出所有发现的 hooks：  
   ```bash
   openclaw hooks list
   ```

### Hook 不符合条件

检查要求：

```bash
openclaw hooks info my-hook
```

查找缺失的：

- 二进制文件（检查 PATH）  
- 环境变量  
- 配置值  
- 操作系统兼容性  

### Hook 未执行

1. 验证 hook 已启用：

   ```bash
   openclaw hooks list
   # Should show ✓ next to enabled hooks
   ```

2. 重启你的 Gateway 网关进程以重新加载 hooks。

3. 检查 Gateway 网关日志中的错误：  
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

### 从遗留配置到发现

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

1. 创建 hook 目录：

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

4. 验证并重启你的 Gateway 网关进程：  
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
- [捆绑 Hooks README](https://github.com/openclaw/openclaw/tree/main/src/hooks/bundled)  
- [Webhook Hooks](/automation/webhook)  
- [配置](/gateway/configuration#hooks)