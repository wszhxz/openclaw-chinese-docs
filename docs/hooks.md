---
summary: "Hooks: event-driven automation for commands and lifecycle events"
read_when:
  - You want event-driven automation for /new, /reset, /stop, and agent lifecycle events
  - You want to build, install, or debug hooks
title: "Hooks"
---
以下是您提供的英文内容的中文翻译：

---

**钩子使用指南**

**翻译说明**  
本指南详细介绍了如何在应用程序中使用钩子（hook）功能，包括设置、最佳实践、调试、测试、架构、故障排除、迁移指南等内容。

---

### **钩子概述**  
钩子是一种在特定事件发生时触发的机制，允许开发者在应用程序流程中插入自定义逻辑。例如，当用户发送 `/new` 命令时，钩子可以执行额外的处理操作。

---

### **设置钩子**  
1. **创建钩子目录**  
   在 `~/.openclaw/hooks/` 目录下创建一个子目录，例如 `my-hook`。  
   ```bash
   mkdir -p ~/.openclaw/hooks/my-hook
   ```

2. **编写钩子文件**  
   - **HOOK.md**：定义钩子的元数据（如名称、描述、事件类型等）。  
     ```markdown
     ---
     name: my-hook
     description: "我的自定义钩子"
     metadata: { "openclaw": { "emoji": "🎯", "events": ["command:new"] } }
     ---
     ```
   - **handler.ts**：实现钩子的逻辑处理函数。  
     ```typescript
     const handler: HookHandler = async (event) => {
       console.log("[my-handler] 触发事件:", event.type, event.action);
       // 你的逻辑代码
     };
     ```

3. **启用钩子**  
   在配置文件中启用钩子：  
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

---

### **最佳实践**  
1. **保持处理程序轻量**  
   钩子在命令处理期间运行，应避免阻塞操作：  
   ```typescript
   // ✅ 好 - 异步处理，立即返回
   const handler: HookHandler = async (event) => {
     void processInBackground(event); // 火箭发射，忘记
   };

   // ❌ 差 - 阻塞命令处理
   const handler: HookHandler = async (event) => {
     await slowDatabaseQuery(event);
     await evenSlowerAPICall(event);
   };
   ```

2. **优雅处理错误**  
   包裹可能出错的操作：  
   ```typescript
   const handler: HookHandler = async (event) => {
     try {
       await riskyOperation(event);
     } catch (err) {
       console.error("[my-handler] 失败:", err instanceof Error ? err.message : String(err));
       // 不抛出错误，让其他处理程序继续运行
     }
   };
   ```

3. **早期过滤事件**  
   如果事件不相关，立即返回：  
   ```typescript
   const handler: HookHandler = async (event) => {
     if (event.type !== "command" || event.action !== "new") {
       return;
     }
     // 你的逻辑
   };
   ```

---

### **调试钩子**  
1. **启用钩子日志**  
   网关启动时会记录钩子加载信息：  
   ```
   注册钩子: session-memory -> command:new
   注册钩子: command-logger -> command
   注册钩子: boot-md -> gateway:startup
   ```

2. **检查发现**  
   列出所有已发现的钩子：  
   ```bash
   openclaw hooks list --verbose
   ```

3. **验证资格**  
   检查钩子是否符合资格要求：  
   ```bash
   openclaw hooks info my-hook
   ```
   查看输出中的缺失依赖项（如二进制文件、环境变量等）。

---

### **测试钩子**  
1. **监控网关日志**  
   查看钩子执行情况：  
   ```bash
   # macOS
   ./scripts/clawlog.sh -f

   # 其他平台
   tail -f ~/.openclaw/gateway.log
   ```

2. **直接测试处理程序**  
   在隔离环境中测试处理程序：  
   ```typescript
   import { test } from "vitest";
   import { createHookEvent } from "./src/hooks/hooks.js";
   import myHandler from "./hooks/my-hook/handler.js";

   test("my handler works", async () => {
     const event = createHookEvent("command", "new", "test-session", {
       foo: "bar",
     });

     await myHandler(event);

     // 断言副作用
   });
   ```

---

### **架构设计**  
1. **核心组件**  
   - `src/hooks/types.ts`：类型定义  
   - `src/hooks/workspace.ts`：目录扫描与加载  
   - `src/hooks/frontmatter.ts`：解析 HOOK.md 元数据  
   - `src/hooks/config.ts`：资格检查  
   - `src/hooks/hooks-status.ts`：状态报告  
   - `src/hooks/loader.ts`：动态模块加载器  
   - `src/cli/hooks-cli.ts`：CLI 命令  
   - `src/gateway/server-startup.ts`：网关启动时加载钩子  
   - `src/auto-reply/reply/commands-core.ts`：触发命令事件  

2. **发现流程**  
   ```
   网关启动
       ↓
   扫描目录（工作区 → 管理 → 打包）
       ↓
   解析 HOOK.md 文件
       ↓
   检查资格（二进制、环境变量、配置、操作系统）
       ↓
   加载合格钩子的处理程序
       ↓
   注册事件处理程序
   ```

3. **事件流程**  
   ```
   用户发送 /new
       ↓
   命令验证
       ↓
   创建钩子事件
       ↓
   触发钩子（所有注册处理程序）
       ↓
   命令处理继续
       ↓
   会话重置
   ```

---

### **故障排除**  
1. **钩子未被发现**  
   - 检查目录结构：  
     ```bash
     ls -la ~/.openclaw/hooks/my-hook/
     # 应显示: HOOK.md, handler.ts
     ```
   - 验证 HOOK.md 格式：  
     ```bash
     cat ~/.openclaw/hooks/my-hook/HOOK.md
     # 应包含 YAML 前置元数据
     ```
   - 列出所有已发现的钩子：  
     ```bash
     openclaw hooks list
     ```

2. **钩子未符合资格**  
   检查要求：  
   ```