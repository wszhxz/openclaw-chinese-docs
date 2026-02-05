---
summary: "Plan: one clean plugin SDK + runtime for all messaging connectors"
read_when:
  - Defining or refactoring the plugin architecture
  - Migrating channel connectors to the plugin SDK/runtime
title: "Plugin SDK Refactor"
---
# 插件 SDK + 运行时重构计划

目标：每个消息连接器都是一个插件（捆绑或外部），使用一个稳定的 API。
没有插件直接从 `src/**` 导入。所有依赖都通过 SDK 或运行时进行。

## 为什么现在开始

- 当前连接器混合了多种模式：直接核心导入、仅分发桥接和自定义助手。
- 这使得升级变得脆弱，并阻碍了清晰的外部插件界面。

## 目标架构（两层）

### 1) 插件 SDK（编译时、稳定、可发布）

范围：类型、助手和配置工具。无运行时状态，无副作用。

内容（示例）：

- 类型：`ChannelPlugin`、适配器、`ChannelMeta`、`ChannelCapabilities`、`ChannelDirectoryEntry`。
- 配置助手：`buildChannelConfigSchema`、`setAccountEnabledInConfigSection`、`deleteAccountFromConfigSection`、
  `applyAccountNameToChannelSection`。
- 配对助手：`PAIRING_APPROVED_MESSAGE`、`formatPairingApproveHint`。
- 入门助手：`promptChannelAccessConfig`、`addWildcardAllowFrom`、入门类型。
- 工具参数助手：`createActionGate`、`readStringParam`、`readNumberParam`、`readReactionParams`、`jsonResult`。
- 文档链接助手：`formatDocsLink`。

交付：

- 发布为 `openclaw/plugin-sdk`（或从核心导出到 `openclaw/plugin-sdk` 下）。
- 语义化版本控制并提供明确的稳定性保证。

### 2) 插件运行时（执行界面、注入式）

范围：所有涉及核心运行时行为的内容。
通过 `OpenClawPluginApi.runtime` 访问，因此插件永远不会导入 `src/**`。

建议界面（最小但完整）：

```ts
export type PluginRuntime = {
  channel: {
    text: {
      chunkMarkdownText(text: string, limit: number): string[];
      resolveTextChunkLimit(cfg: OpenClawConfig, channel: string, accountId?: string): number;
      hasControlCommand(text: string, cfg: OpenClawConfig): boolean;
    };
    reply: {
      dispatchReplyWithBufferedBlockDispatcher(params: {
        ctx: unknown;
        cfg: unknown;
        dispatcherOptions: {
          deliver: (payload: {
            text?: string;
            mediaUrls?: string[];
            mediaUrl?: string;
          }) => void | Promise<void>;
          onError?: (err: unknown, info: { kind: string }) => void;
        };
      }): Promise<void>;
      createReplyDispatcherWithTyping?: unknown; // adapter for Teams-style flows
    };
    routing: {
      resolveAgentRoute(params: {
        cfg: unknown;
        channel: string;
        accountId: string;
        peer: { kind: "dm" | "group" | "channel"; id: string };
      }): { sessionKey: string; accountId: string };
    };
    pairing: {
      buildPairingReply(params: { channel: string; idLine: string; code: string }): string;
      readAllowFromStore(channel: string): Promise<string[]>;
      upsertPairingRequest(params: {
        channel: string;
        id: string;
        meta?: { name?: string };
      }): Promise<{ code: string; created: boolean }>;
    };
    media: {
      fetchRemoteMedia(params: { url: string }): Promise<{ buffer: Buffer; contentType?: string }>;
      saveMediaBuffer(
        buffer: Uint8Array,
        contentType: string | undefined,
        direction: "inbound" | "outbound",
        maxBytes: number,
      ): Promise<{ path: string; contentType?: string }>;
    };
    mentions: {
      buildMentionRegexes(cfg: OpenClawConfig, agentId?: string): RegExp[];
      matchesMentionPatterns(text: string, regexes: RegExp[]): boolean;
    };
    groups: {
      resolveGroupPolicy(
        cfg: OpenClawConfig,
        channel: string,
        accountId: string,
        groupId: string,
      ): {
        allowlistEnabled: boolean;
        allowed: boolean;
        groupConfig?: unknown;
        defaultConfig?: unknown;
      };
      resolveRequireMention(
        cfg: OpenClawConfig,
        channel: string,
        accountId: string,
        groupId: string,
        override?: boolean,
      ): boolean;
    };
    debounce: {
      createInboundDebouncer<T>(opts: {
        debounceMs: number;
        buildKey: (v: T) => string | null;
        shouldDebounce: (v: T) => boolean;
        onFlush: (entries: T[]) => Promise<void>;
        onError?: (err: unknown) => void;
      }): { push: (v: T) => void; flush: () => Promise<void> };
      resolveInboundDebounceMs(cfg: OpenClawConfig, channel: string): number;
    };
    commands: {
      resolveCommandAuthorizedFromAuthorizers(params: {
        useAccessGroups: boolean;
        authorizers: Array<{ configured: boolean; allowed: boolean }>;
      }): boolean;
    };
  };
  logging: {
    shouldLogVerbose(): boolean;
    getChildLogger(name: string): PluginLogger;
  };
  state: {
    resolveStateDir(cfg: OpenClawConfig): string;
  };
};
```

注意事项：

- 运行时是访问核心行为的唯一方式。
- SDK 故意设计得小而稳定。
- 每个运行时方法映射到现有的核心实现（无重复）。

## 迁移计划（分阶段、安全）

### 第 0 阶段：脚手架

- 引入 `openclaw/plugin-sdk`。
- 将 `api.runtime` 添加到 `OpenClawPluginApi` 中，包含上述界面。
- 在过渡期间保持现有导入（弃用警告）。

### 第 1 阶段：桥接清理（低风险）

- 将每个扩展的 `core-bridge.ts` 替换为 `api.runtime`。
- 首先迁移 BlueBubbles、Zalo、Zalo Personal（已经接近完成）。
- 移除重复的桥接代码。

### 第 2 阶段：轻量级直接导入插件

- 将 Matrix 迁移到 SDK + 运行时。
- 验证入门、目录、群组提及逻辑。

### 第 3 阶段：重量级直接导入插件

- 迁移 MS Teams（最多运行时助手集）。
- 确保回复/输入语义与当前行为匹配。

### 第 4 阶段：iMessage 插件化

- 将 iMessage 移动到 `extensions/imessage` 中。
- 将直接核心调用替换为 `api.runtime`。
- 保持配置键、CLI 行为和文档不变。

### 第 5 阶段：强制执行

- 添加 lint 规则 / CI 检查：不允许从 `src/**` 导入 `extensions/**`。
- 添加插件 SDK/版本兼容性检查（运行时 + SDK 语义化版本）。

## 兼容性和版本控制

- SDK：语义化版本控制，已发布，有文档变更。
- 运行时：按核心版本发布。添加 `api.runtime.version`。
- 插件声明所需的运行时范围（例如 `openclawRuntime: ">=2026.2.0"`）。

## 测试策略

- 适配器级别的单元测试（使用真实核心实现执行运行时函数）。
- 每个插件的黄金测试：确保无行为漂移（路由、配对、白名单、提及网关）。
- CI 中使用的单个端到端插件示例（安装 + 运行 + 冒烟测试）。

## 待解决问题

- SDK 类型托管位置：独立包还是核心导出？
- 运行时类型分发：在 SDK 中（仅类型）还是在核心中？
- 如何为捆绑插件和外部插件暴露文档链接？
- 过渡期间是否允许仓库内插件有限的直接核心导入？

## 成功标准

- 所有频道连接器都是使用 SDK + 运行时的插件。
- 不再从 `src/**` 导入 `extensions/**`。
- 新连接器模板仅依赖于 SDK + 运行时。
- 外部插件可以在无需核心源码访问的情况下开发和更新。

相关文档：[插件](/plugin)、[频道](/channels/index)、[配置](/gateway/configuration)。