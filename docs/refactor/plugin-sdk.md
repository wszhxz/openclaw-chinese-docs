---
summary: "Plan: one clean plugin SDK + runtime for all messaging connectors"
read_when:
  - Defining or refactoring the plugin architecture
  - Migrating channel connectors to the plugin SDK/runtime
title: "Plugin SDK Refactor"
---
# 插件SDK + 运行时重构计划

目标：每个消息连接器都是一个插件（捆绑或外部）使用一个稳定的API。
没有插件直接从`src/**`导入。所有依赖项均通过SDK或运行时进行。

## 为何现在

- 当前连接器混合了多种模式：直接核心导入、仅分发桥接和自定义辅助工具。
- 这使得升级变得脆弱，并阻碍了干净的外部插件接口。

## 目标架构（两层）

### 1) 插件SDK（编译时、稳定、可发布）

范围：类型、辅助工具和配置实用工具。无运行时状态，无副作用。

内容（示例）：

- 类型：`ChannelPlugin`、适配器、`ChannelMeta`、`ChannelCapabilities`、`ChannelDirectoryEntry`。
- 配置辅助工具：`buildChannelConfigSchema`、`setAccountEnabledInConfigSection`、`deleteAccountFromConfigSection`、`applyAccountNameToChannelSection`。
- 配对辅助工具：`PAIRING_APPROVED_MESSAGE`、`formatPairingApproveHint`。
- 入门辅助工具：`promptChannelAccessConfig`、`addWildcardAllowFrom`、入门类型。
- 工具参数辅助工具：`createActionGate`、`readStringParam`、`readNumberParam`、`readReactionParams`、`jsonResult`。
- 文档链接辅助工具：`formatDocsLink`。

交付：

- 作为`openclaw/plugin-sdk`发布（或从核心导出`openclaw/plugin-sdk`）。
- 使用语义化版本控制（Semver）并明确稳定性保证。

### 2) 插件运行时（执行表面，注入）

范围：所有涉及核心运行时行为的内容。
通过`OpenClawPluginApi.runtime`访问，因此插件永远不会导入`src/**`。

建议的表面（最小但完整）：

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
      createReplyDispatcherWithTyping?: unknown; // 用于Teams风格流程的适配器
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
``
```

注意事项：

- 运行时是访问核心行为的唯一途径。
- SDK有意保持小巧且稳定。
- 每个运行时方法都映射到现有的核心实现（无重复）。

## 迁移计划（分阶段、安全）

### 阶段0：搭建框架

- 引入`openclaw/plugin-sdk`。
- 向`OpenClawPluginApi`添加`api.runtime`，使用上述表面。
- 在过渡窗口内维护现有导入（弃用警告）。

### 阶段1：桥接清理（低风险）