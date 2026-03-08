---
title: "Pi Integration Architecture"
summary: "Architecture of OpenClaw's embedded Pi agent integration and session lifecycle"
read_when:
  - Understanding Pi SDK integration design in OpenClaw
  - Modifying agent session lifecycle, tooling, or provider wiring for Pi
---
# Pi 集成架构

本文档描述了 OpenClaw 如何与 [pi-coding-agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) 及其相关包（`pi-ai`, `pi-agent-core`, `pi-tui`）集成，以支持其 AI 代理功能。

## 概述

OpenClaw 使用 pi SDK 将 AI 编码代理嵌入到其消息网关架构中。与其将 pi 作为子进程启动或使用 RPC 模式不同，OpenClaw 直接通过 `createAgentSession()` 导入并实例化 pi 的 `AgentSession`。这种嵌入式方法提供了：

- 完全控制会话生命周期和事件处理
- 自定义工具注入（消息、沙箱、特定于通道的操作）
- 按通道/上下文定制系统提示
- 支持分支/压缩的会话持久化
- 多账户认证配置文件轮换及故障转移
- 与提供商无关的模型切换

## 包依赖

```json
{
  "@mariozechner/pi-agent-core": "0.49.3",
  "@mariozechner/pi-ai": "0.49.3",
  "@mariozechner/pi-coding-agent": "0.49.3",
  "@mariozechner/pi-tui": "0.49.3"
}
```

| 包 | 用途 |
| ----------------- | ------------------------------------------------------------------------------------------------------ |
| `pi-ai` | 核心 LLM 抽象：`Model`, `streamSimple`, 消息类型、提供程序 API |
| `pi-agent-core` | 代理循环、工具执行、`AgentMessage` 类型 |
| `pi-coding-agent` | 高级 SDK：`createAgentSession`, `SessionManager`, `AuthStorage`, `ModelRegistry`, 内置工具 |
| `pi-tui` | 终端 UI 组件（用于 OpenClaw 的本地 TUI 模式） |

## 文件结构

``
src/agents/
├── pi-embedded-runner.ts          # 从 pi-embedded-runner/ 重新导出
├── pi-embedded-runner/
│   ├── run.ts                     # 主入口：runEmbeddedPiAgent()
│   ├── run/
│   │   ├── attempt.ts             # 带会话设置的单次尝试逻辑
│   │   ├── params.ts              # RunEmbeddedPiAgentParams 类型
│   │   ├── payloads.ts            # 从运行结果构建响应负载
│   │   ├── images.ts              # 视觉模型图像注入
│   │   └── types.ts               # EmbeddedRunAttemptResult
│   ├── abort.ts                   # 中止错误检测
│   ├── cache-ttl.ts               # 用于上下文修剪的缓存 TTL 跟踪
│   ├── compact.ts                 # 手动/自动压缩逻辑
│   ├── extensions.ts              # 为嵌入式运行加载 pi 扩展
│   ├── extra-params.ts            # 特定提供者的流参数
│   ├── google.ts                  # Google/Gemini 回合顺序修复
│   ├── history.ts                 # 历史记录限制（DM vs 群组）
│   ├── lanes.ts                   # 会话/全局命令通道
│   ├── logger.ts                  # 子系统日志记录器
│   ├── model.ts                   # 通过 ModelRegistry 解析模型
│   ├── runs.ts                    # 活动运行跟踪、中止、队列
│   ├── sandbox-info.ts            # 系统提示的沙盒信息
│   ├── session-manager-cache.ts   # SessionManager 实例缓存
│   ├── session-manager-init.ts    # 会话文件初始化
│   ├── system-prompt.ts           # 系统提示生成器
│   ├── tool-split.ts              # 将工具拆分为 builtIn vs custom
│   ├── types.ts                   # EmbeddedPiAgentMeta, EmbeddedPiRunResult
│   └── utils.ts                   # ThinkLevel 映射、错误描述
├── pi-embedded-subscribe.ts       # 会话事件订阅/分发
├── pi-embedded-subscribe.types.ts # SubscribeEmbeddedPiSessionParams
├── pi-embedded-subscribe.handlers.ts # 事件处理程序工厂
├── pi-embedded-subscribe.handlers.lifecycle.ts
├── pi-embedded-subscribe.handlers.types.ts
├── pi-embedded-block-chunker.ts   # 流式块回复分块
├── pi-embedded-messaging.ts       # 消息工具发送跟踪
├── pi-embedded-helpers.ts         # 错误分类、回合验证
├── pi-embedded-helpers/           # 辅助模块
├── pi-embedded-utils.ts           # 格式化实用工具
├── pi-tools.ts                    # createOpenClawCodingTools()
├── pi-tools.abort.ts              # 工具的 AbortSignal 包装
├── pi-tools.policy.ts             # 工具允许/拒绝列表策略
├── pi-tools.read.ts               # 读取工具自定义
├── pi-tools.schema.ts             # 工具模式规范化
├── pi-tools.types.ts              # AnyAgentTool 类型别名
├── pi-tool-definition-adapter.ts  # AgentTool -> ToolDefinition 适配器
├── pi-settings.ts                 # 设置覆盖
├── pi-extensions/                 # 自定义 pi 扩展
│   ├── compaction-safeguard.ts    # 保护扩展
│   ├── compaction-safeguard-runtime.ts
│   ├── context-pruning.ts         # Cache-TTL 上下文修剪扩展
│   └── context-pruning/
├── model-auth.ts                  # 身份配置文件解析
├── auth-profiles.ts               # 配置文件存储、冷却、故障转移
├── model-selection.ts             # 默认模型解析
├── models-config.ts               # models.json 生成
├── model-catalog.ts               # 模型目录缓存
├── context-window-guard.ts        # 上下文窗口验证
├── failover-error.ts              # FailoverError 类
├── defaults.ts                    # DEFAULT_PROVIDER, DEFAULT_MODEL
├── system-prompt.ts               # buildAgentSystemPrompt()
├── system-prompt-params.ts        # 系统提示参数解析
├── system-prompt-report.ts        # 调试报告生成
├── tool-summaries.ts              # 工具描述摘要
├── tool-policy.ts                 # 工具策略解析
├── transcript-policy.ts           # 转录验证策略
├── skills.ts                      # 技能快照/提示构建
├── skills/                        # 技能子系统
├── sandbox.ts                     # 沙盒上下文解析
├── sandbox/                       # 沙盒子系统
├── channel-tools.ts               # 特定频道工具注入
├── openclaw-tools.ts              # OpenClaw 特定工具
├── bash-tools.ts                  # exec/process 工具
├── apply-patch.ts                 # apply_patch 工具（OpenAI）
├── tools/                         # 单个工具实现
│   ├── browser-tool.ts
│   ├── canvas-tool.ts
│   ├── cron-tool.ts
│   ├── discord-actions*.ts
│   ├── gateway-tool.ts
│   ├── image-tool.ts
│   ├── message-tool.ts
│   ├── nodes-tool.ts
│   ├── session*.ts
│   ├── slack-actions.ts
│   ├── telegram-actions.ts
│   ├── web-*.ts
│   └── whatsapp-actions.ts
└── ...

``

## 核心集成流程

### 1. 运行嵌入式代理

主要入口点是 `runEmbeddedPiAgent()`，位于 `pi-embedded-runner/run.ts` 中：

```typescript
import { runEmbeddedPiAgent } from "./agents/pi-embedded-runner.js";

const result = await runEmbeddedPiAgent({
  sessionId: "user-123",
  sessionKey: "main:whatsapp:+1234567890",
  sessionFile: "/path/to/session.jsonl",
  workspaceDir: "/path/to/workspace",
  config: openclawConfig,
  prompt: "Hello, how are you?",
  provider: "anthropic",
  model: "claude-sonnet-4-20250514",
  timeoutMs: 120_000,
  runId: "run-abc",
  onBlockReply: async (payload) => {
    await sendToChannel(payload.text, payload.mediaUrls);
  },
});
```

### 2. 会话创建

在 `runEmbeddedAttempt()` 内部（由 `runEmbeddedPiAgent()` 调用），使用了 pi SDK：

```typescript
import {
  createAgentSession,
  DefaultResourceLoader,
  SessionManager,
  SettingsManager,
} from "@mariozechner/pi-coding-agent";

const resourceLoader = new DefaultResourceLoader({
  cwd: resolvedWorkspace,
  agentDir,
  settingsManager,
  additionalExtensionPaths,
});
await resourceLoader.reload();

const { session } = await createAgentSession({
  cwd: resolvedWorkspace,
  agentDir,
  authStorage: params.authStorage,
  modelRegistry: params.modelRegistry,
  model: params.model,
  thinkingLevel: mapThinkingLevel(params.thinkLevel),
  tools: builtInTools,
  customTools: allCustomTools,
  sessionManager,
  settingsManager,
  resourceLoader,
});

applySystemPromptOverrideToSession(session, systemPromptOverride);
```

### 3. 事件订阅

`subscribeEmbeddedPiSession()` 订阅了 pi 的 `AgentSession` 事件：

```typescript
const subscription = subscribeEmbeddedPiSession({
  session: activeSession,
  runId: params.runId,
  verboseLevel: params.verboseLevel,
  reasoningMode: params.reasoningLevel,
  toolResultFormat: params.toolResultFormat,
  onToolResult: params.onToolResult,
  onReasoningStream: params.onReasoningStream,
  onBlockReply: params.onBlockReply,
  onPartialReply: params.onPartialReply,
  onAgentEvent: params.onAgentEvent,
});
```

处理的事件包括：

- `message_start` / `message_end` / `message_update`（流式文本/思考）
- `tool_execution_start` / `tool_execution_update` / `tool_execution_end`
- `turn_start` / `turn_end`
- `agent_start` / `agent_end`
- `auto_compaction_start` / `auto_compaction_end`

### 4. 提示

设置完成后，对会话进行提示：

```typescript
await session.prompt(effectivePrompt, { images: imageResult.images });
```

SDK 处理完整的代理循环：发送到 LLM、执行工具调用、流式响应。

图像注入是提示局部的：OpenClaw 从当前提示加载图像引用，并通过 `images` 仅针对该轮次传递它们。它不会重新扫描旧的历史轮次以重新注入图像负载。

## 工具架构

### 工具管道

1. **基础工具**：pi 的 ``codingTools``（read, bash, edit, write）
2. **自定义替换**：OpenClaw 将 bash 替换为 ``exec`/`process``，并为 sandbox 定制 read/edit/write
3. **OpenClaw 工具**：messaging, browser, canvas, sessions, cron, gateway 等。
4. **渠道工具**：针对 Discord/Telegram/Slack/WhatsApp 的操作工具
5. **策略过滤**：根据 profile、provider、agent、group、sandbox 策略过滤工具
6. **Schema 规范化**：清理 Schemas 以适应 Gemini/OpenAI 的特性
7. **AbortSignal 包装**：包装工具以尊重 abort signals

### 工具定义适配器

pi-agent-core 的 ``AgentTool`` 具有与 pi-coding-agent 的 ``ToolDefinition`` 不同的 ``execute`` 签名。``pi-tool-definition-adapter.ts`` 中的适配器桥接了这一点：

````typescript
export function toToolDefinitions(tools: AnyAgentTool[]): ToolDefinition[] {
  return tools.map((tool) => ({
    name: tool.name,
    label: tool.label ?? name,
    description: tool.description ?? "",
    parameters: tool.parameters,
    execute: async (toolCallId, params, onUpdate, _ctx, signal) => {
      // pi-coding-agent signature differs from pi-agent-core
      return await tool.execute(toolCallId, params, signal, onUpdate);
    },
  }));
}
````

### 工具拆分策略

``splitSdkTools()`` 通过 ``customTools`` 传递所有工具：

````typescript
export function splitSdkTools(options: { tools: AnyAgentTool[]; sandboxEnabled: boolean }) {
  return {
    builtInTools: [], // Empty. We override everything
    customTools: toToolDefinitions(options.tools),
  };
}
````

这确保了 OpenClaw 的策略过滤、sandbox 集成和扩展工具集在跨提供商时保持一致。

## 系统提示词构建

系统提示词在 ``buildAgentSystemPrompt()`` (``system-prompt.ts``) 中构建。它组装了一个完整的提示词，包含 Tooling、Tool Call Style、Safety guardrails、OpenClaw CLI 参考、Skills、Docs、Workspace、Sandbox、Messaging、Reply Tags、Voice、Silent Replies、Heartbeats、Runtime metadata 部分，以及启用时的 Memory 和 Reactions，还有可选的上下文文件和额外的系统提示词内容。子代理使用的最小化提示词模式会修剪这些部分。

该提示词在会话创建后通过 ``applySystemPromptOverrideToSession()`` 应用：

````typescript
const systemPromptOverride = createSystemPromptOverride(appendPrompt);
applySystemPromptOverrideToSession(session, systemPromptOverride);
````

## 会话管理

### 会话文件

会话是带有树形结构（id/parentId 链接）的 JSONL 文件。Pi 的 ``SessionManager`` 负责持久化：

````typescript
const sessionManager = SessionManager.open(params.sessionFile);
````

OpenClaw 使用 ``guardSessionManager()`` 对此进行包装以确保工具结果安全。

### 会话缓存

``session-manager-cache.ts`` 缓存 SessionManager 实例以避免重复的文件解析：

```typescript
await prewarmSessionFile(params.sessionFile);
sessionManager = SessionManager.open(params.sessionFile);
trackSessionManagerAccess(params.sessionFile);
```

### 历史限制

`limitHistoryTurns()` 根据频道类型（DM 与群组）修剪对话历史。

### 压缩

自动压缩在上下文溢出时触发。`compactEmbeddedPiSessionDirect()` 处理手动压缩：

```typescript
const compactResult = await compactEmbeddedPiSessionDirect({
  sessionId, sessionFile, provider, model, ...
});
```

## 认证与模型解析

### 认证配置文件

OpenClaw 维护一个认证配置文件存储库，每个提供商拥有多个 API 密钥：

```typescript
const authStore = ensureAuthProfileStore(agentDir, { allowKeychainPrompt: false });
const profileOrder = resolveAuthProfileOrder({ cfg, store: authStore, provider, preferredProfile });
```

配置文件在失败时轮换，并带有冷却期跟踪：

```typescript
await markAuthProfileFailure({ store, profileId, reason, cfg, agentDir });
const rotated = await advanceAuthProfile();
```

### 模型解析

```typescript
import { resolveModel } from "./pi-embedded-runner/model.js";

const { model, error, authStorage, modelRegistry } = resolveModel(
  provider,
  modelId,
  agentDir,
  config,
);

// Uses pi's ModelRegistry and AuthStorage
authStorage.setRuntimeApiKey(model.provider, apiKeyInfo.apiKey);
```

### 故障转移

`FailoverError` 在配置时触发模型回退：

```typescript
if (fallbackConfigured && isFailoverErrorMessage(errorText)) {
  throw new FailoverError(errorText, {
    reason: promptFailoverReason ?? "unknown",
    provider,
    model: modelId,
    profileId,
    status: resolveFailoverStatus(promptFailoverReason),
  });
}
```

## Pi 扩展

OpenClaw 加载自定义的 pi 扩展以实现特定行为：

### 压缩保护

`src/agents/pi-extensions/compaction-safeguard.ts` 为压缩添加护栏，包括自适应令牌预算以及工具失败和文件操作摘要：

```typescript
if (resolveCompactionMode(params.cfg) === "safeguard") {
  setCompactionSafeguardRuntime(params.sessionManager, { maxHistoryShare });
  paths.push(resolvePiExtensionPath("compaction-safeguard"));
}
```

### 上下文修剪

`src/agents/pi-extensions/context-pruning.ts` 实现基于缓存 TTL 的上下文修剪：

```typescript
if (cfg?.agents?.defaults?.contextPruning?.mode === "cache-ttl") {
  setContextPruningRuntime(params.sessionManager, {
    settings,
    contextWindowTokens,
    isToolPrunable,
    lastCacheTouchAt,
  });
  paths.push(resolvePiExtensionPath("context-pruning"));
}
```

## 流式传输与块回复

### 块分块

`EmbeddedBlockChunker` 将流式文本管理为独立的回复块：

```typescript
const blockChunker = blockChunking ? new EmbeddedBlockChunker(blockChunking) : null;
```

### 思考/最终标签剥离

流式输出经过处理以剥离 `<think>`/`<thinking>` 块并提取 `<final>` 内容：

```typescript
const stripBlockTags = (text: string, state: { thinking: boolean; final: boolean }) => {
  // Strip <think>...</think> content
  // If enforceFinalTag, only return <final>...</final> content
};
```

### 回复指令

回复指令如 `[[media:url]]`, `[[voice]]`, `[[reply:id]]` 会被解析并提取：

```typescript
const { text: cleanedText, mediaUrls, audioAsVoice, replyToId } = consumeReplyDirectives(chunk);
```

## 错误处理

### 错误分类

`pi-embedded-helpers.ts` 对错误进行分类以便适当处理：

```typescript
isContextOverflowError(errorText)     // Context too large
isCompactionFailureError(errorText)   // Compaction failed
isAuthAssistantError(lastAssistant)   // Auth failure
isRateLimitAssistantError(...)        // Rate limited
isFailoverAssistantError(...)         // Should failover
classifyFailoverReason(errorText)     // "auth" | "rate_limit" | "quota" | "timeout" | ...
```

### 思考层级回退

如果某个思考层级不受支持，它将回退：

```typescript
const fallbackThinking = pickFallbackThinkingLevel({
  message: errorText,
  attempted: attemptedThinking,
});
if (fallbackThinking) {
  thinkLevel = fallbackThinking;
  continue;
}
```

## 沙盒集成

当启用沙盒模式时，工具和路径将受到限制：

```typescript
const sandbox = await resolveSandboxContext({
  config: params.config,
  sessionKey: sandboxSessionKey,
  workspaceDir: resolvedWorkspace,
});

if (sandboxRoot) {
  // Use sandboxed read/edit/write tools
  // Exec runs in container
  // Browser uses bridge URL
}
```

## 特定提供商处理

### Anthropic

- 拒绝魔法字符串清理
- 连续角色的回合验证
- Claude Code 参数兼容性

### Google/Gemini

- 回合顺序修复 (`applyGoogleTurnOrderingFix`)
- 工具架构清理 (`sanitizeToolsForGoogle`)
- 会话历史清理 (`sanitizeSessionHistory`)

### OpenAI

- 用于 Codex 模型的 `apply_patch` 工具
- 思考层级降级处理

## TUI 集成

OpenClaw 还具有一个本地 TUI 模式，直接使用 pi-tui 组件：

```typescript
// src/tui/tui.ts
import { ... } from "@mariozechner/pi-tui";
```

这提供了与 pi 原生模式类似的交互式终端体验。

## 与 Pi CLI 的主要区别

| 方面          | Pi CLI                  | OpenClaw Embedded                                                                              |
| ------------- | ----------------------- | ---------------------------------------------------------------------------------------------- |
| 调用方式      | `pi` command / RPC      | 通过 SDK 经由 `createAgentSession()`                                                                 |
| 工具          | 默认编码工具            | 自定义 OpenClaw 工具套件                                                                     |
| 系统提示词    | AGENTS.md + prompts     | 按通道/上下文动态生成                                                                        |
| 会话存储      | `~/.pi/agent/sessions/` | `~/.openclaw/agents/<agentId>/sessions/` (或 `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`) |
| 认证          | 单一凭证                | 多配置文件并支持轮换                                                                         |
| 扩展          | 从磁盘加载              | 编程式 + 磁盘路径                                                                              |
| 事件处理      | TUI 渲染           | 基于回调（onBlockReply 等）                                                                    |

## 未来考量

可能需要进行重构的领域：

1. **工具签名对齐**：目前需要在 pi-agent-core 和 pi-coding-agent 签名之间进行适配
2. **会话管理器封装**：`guardSessionManager` 增加了安全性但提高了复杂性
3. **扩展加载**：可以更直接地使用 pi 的 `ResourceLoader`
4. **流处理器复杂性**：`subscribeEmbeddedPiSession` 变得庞大
5. **提供商特有行为**：许多特定于提供商的代码路径，pi 理论上可以处理

## 测试

Pi 集成覆盖以下套件：

- `src/agents/pi-*.test.ts`
- `src/agents/pi-auth-json.test.ts`
- `src/agents/pi-embedded-*.test.ts`
- `src/agents/pi-embedded-helpers*.test.ts`
- `src/agents/pi-embedded-runner*.test.ts`
- `src/agents/pi-embedded-runner/**/*.test.ts`
- `src/agents/pi-embedded-subscribe*.test.ts`
- `src/agents/pi-tools*.test.ts`
- `src/agents/pi-tool-definition-adapter*.test.ts`
- `src/agents/pi-settings.test.ts`
- `src/agents/pi-extensions/**/*.test.ts`

实时/可选启用：

- `src/agents/pi-embedded-runner-extraparams.live.test.ts` (启用 `OPENCLAW_LIVE_TEST=1`)

有关当前运行命令，请参阅 [Pi 开发工作流](/pi-dev)。