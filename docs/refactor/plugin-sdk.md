---
summary: "Plan: one clean plugin SDK + runtime for all messaging connectors"
read_when:
  - Defining or refactoring the plugin architecture
  - Migrating channel connectors to the plugin SDK/runtime
title: "Plugin SDK Refactor"
---
# 插件SDK + 运行时重构计划

目标：每个消息连接器都是一个插件（内置或外部），使用一个稳定的API。
没有插件直接从`src/**`导入。所有依赖项通过SDK或运行时传递。

## 为什么现在

- 当前连接器混合了模式：直接核心导入、仅dist桥接和自定义辅助工具。
- 这使得升级变得脆弱，并阻止了一个干净的外部插件表面。

## 目标架构（两层）

### 1) 插件SDK（编译时，稳定，可发布）

范围：类型、辅助工具和配置实用程序。没有运行时状态，没有副作用。

内容（示例）：

- 类型：`ChannelPlugin`，适配器，`ChannelMeta`，`ChannelCapabilities`，`ChannelDirectoryEntry`。
- 配置辅助工具：`buildChannelConfigSchema`，`setAccountEnabledInConfigSection`，`deleteAccountFromConfigSection`，
  `applyAccountNameToChannelSection`。
- 配对辅助工具：`PAIRING_APPROVED_MESSAGE`，`formatPairingApproveHint`。
- 入门辅助工具：`promptChannelAccessConfig`，`addWildcardAllowFrom`，入门类型。
- 工具参数辅助工具：`createActionGate`，`readStringParam`，`readNumberParam`，`readReactionParams`，`jsonResult`。
- 文档链接辅助工具：`formatDocsLink`。

交付：

- 发布为`openclaw/plugin-sdk`（或从核心导出到`openclaw/plugin-sdk`）。
- 使用语义化版本控制，并提供明确的稳定性保证。

### 2) 插件运行时（执行表面，注入）

范围：所有触及核心运行时行为的内容。
通过`OpenClawPluginApi.runtime`访问，因此插件永远不会导入`src/**`。

提议的表面（最小但完整）：

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

注释：

- 运行时是访问核心行为的唯一方式。
- SDK故意保持小且稳定。
- 每个运行时方法映射到现有的核心实现（没有重复）。

## 迁移计划（分阶段，安全）

### 第0阶段：搭建

- 引入`openclaw/plugin-sdk`。
- 将`api.runtime`添加到`OpenClawPluginApi`，并包含上述表面。
- 在过渡窗口期间维护现有导入（弃用警告）。

### 第1阶段：桥接清理（低风险）

- 将每个扩展的`core-bridge.ts`替换为`api.runtime`。
- 首先迁移BlueBubbles、Zalo、Zalo Personal（已经接近完成）。
- 移除重复的桥接代码。

### 第2阶段：轻量级直接导入插件

- 将Matrix迁移到SDK + 运行时。
- 验证入门、目录、群组提及逻辑。

### 第3阶段：重量级直接导入插件

- 将MS Teams（最大的一组运行时辅助工具集）迁移到SDK + 运行时。
- 确保回复/正在输入语义与当前行为匹配。

### 第4阶段：iMessage插件化

- 将iMessage移动到`extensions/imessage`。
- 将直接核心调用替换为`api.runtime`。
- 保持配置键、CLI行为和文档不变。

### 第5阶段：强制执行

- 添加lint规则/CI检查：不允许从`src/**`导入`extensions/**`。
- 添加插件SDK/版本兼容性检查（运行时+SDK语义化版本控制）。

## 兼容性和版本控制

- SDK：语义化版本控制，已发布，记录更改。
- 运行时：按核心版本发布。添加`api.runtime.version`。
- 插件声明所需的运行时范围（例如，`openclawRuntime: ">=2026.2.0"`）。

## 测试策略

- 适配器级别的单元测试（使用真实的核心实现来练习运行时函数）。
- 每个插件的黄金测试：确保没有行为漂移（路由、配对、允许列表、提及门控）。
- 用于CI的单个端到端插件示例（安装 + 运行 + 烟雾测试）。

## 开放问题

- SDK类型的托管位置：单独的包还是核心导出？
- 运行时类型分发：在SDK（仅类型）还是在核心中？
- 如何为捆绑和外部插件公开文档链接？
- 在过渡期间是否允许仓库内插件有限的直接核心导入？

## 成功标准

- 所有通道连接器都是使用SDK + 运行时的插件。
- 没有从`src/**`导入`extensions/**`。
- 新连接器模板仅依赖于SDK + 运行时。
- 外部插件可以在没有核心源代码访问的情况下开发和更新。

相关文档：[插件](/plugin)，[通道](/channels/index)，[配置](/gateway/configuration)。