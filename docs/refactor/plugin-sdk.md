---
summary: "Plan: one clean plugin SDK + runtime for all messaging connectors"
read_when:
  - Defining or refactoring the plugin architecture
  - Migrating channel connectors to the plugin SDK/runtime
title: "Plugin SDK Refactor"
---
# 插件 SDK + 运行时重构计划

目标：每个消息通道连接器均为插件（内置或外部），且均使用同一套稳定 API。  
任何插件均不得直接导入 ``src/**``。所有依赖必须经由 SDK 或运行时提供。

## 为何现在启动

- 当前连接器混用多种模式：直接导入核心模块、仅分发版桥接层（dist-only bridges）、自定义辅助函数。  
- 这导致升级过程脆弱，并阻碍构建清晰、规范的外部插件接口。

## 目标架构（两层结构）

### 1) 插件 SDK（编译期、稳定、可发布）

作用域：类型定义、辅助函数与配置工具。不包含运行时状态，无副作用。

内容示例：

- 类型：``ChannelPlugin``、适配器、``ChannelMeta``、``ChannelCapabilities``、``ChannelDirectoryEntry``。  
- 配置辅助函数：``buildChannelConfigSchema``、``setAccountEnabledInConfigSection``、``deleteAccountFromConfigSection``、``applyAccountNameToChannelSection``。  
- 配对辅助函数：``PAIRING_APPROVED_MESSAGE``、``formatPairingApproveHint``。  
- 入门辅助函数：``promptChannelAccessConfig``、``addWildcardAllowFrom``、入门相关类型。  
- 工具参数辅助函数：``createActionGate``、``readStringParam``、``readNumberParam``、``readReactionParams``、``jsonResult``。  
- 文档链接辅助函数：``formatDocsLink``。

交付方式：

- 以 ``openclaw/plugin-sdk`` 形式发布（或从核心模块导出至 ``openclaw/plugin-sdk`` 下）。  
- 遵循语义化版本（Semver），并提供明确的稳定性保证。

### 2) 插件运行时（执行层面，注入式提供）

作用域：所有涉及核心运行时行为的部分。  
通过 ``OpenClawPluginApi.runtime`` 访问，确保插件永不直接导入 ``src/**``。

建议暴露的接口（最小但完整）：

```ts
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
        peer: { kind: RoutePeerKind; id: string };
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
```

说明：

- 运行时是访问核心行为的唯一途径。  
- SDK 设计为轻量且高度稳定。  
- 每个运行时方法均对应一个已有的核心实现（不引入重复逻辑）。

## 迁移计划（分阶段、安全推进）

### 第 0 阶段：基础搭建

- 引入 ``openclaw/plugin-sdk``。  
- 在 ``api.runtime`` 中向 ``OpenClawPluginApi`` 添加上述接口。  
- 过渡期内保留现有导入方式（辅以弃用警告）。

### 第 1 阶段：桥接层清理（低风险）

- 将各扩展中独立的 ``core-bridge.ts`` 替换为统一的 ``api.runtime``。  
- 优先迁移 BlueBubbles、Zalo、Zalo Personal（当前已较接近目标形态）。  
- 移除重复的桥接代码。

### 第 2 阶段：轻量级直连导入插件

- 将 Matrix 迁移至 SDK + 运行时架构。  
- 验证入门流程、目录服务、群组提及逻辑等功能。

### 第 3 阶段：重度直连导入插件

- 迁移 MS Teams（其运行时辅助函数数量最多）。  
- 确保回复与输入提示（typing）语义与当前行为一致。

### 第 4 阶段：iMessage 插件化

- 将 iMessage 移入 ``extensions/imessage``。  
- 以 ``api.runtime`` 替代所有对核心模块的直接调用。  
- 保持配置项键名、CLI 行为及文档内容不变。

### 第 5 阶段：强制执行

- 增加 lint 规则 / CI 检查：禁止 ``extensions/**`` 从 ``src/**`` 中导入。  
- 增加插件 SDK/运行时版本兼容性检查（基于运行时与 SDK 的语义化版本）。

## 兼容性与版本管理

- SDK：遵循语义化版本，独立发布，变更内容有明确文档记录。  
- 运行时：按核心版本号进行版本管理。增加 ``api.runtime.version``。  
- 插件需声明所需运行时版本范围（例如：``openclawRuntime: ">=2026.2.0"``）。

## 测试策略

- 适配器级别单元测试（使用真实核心实现来调用运行时函数）。  
- 每个插件的“黄金测试”（Golden tests）：确保行为无偏差（路由、配对、白名单、提及拦截等）。  
- CI 中使用单一端到端插件样例（安装 + 启动 + 冒烟测试）。

## 待解决问题

- SDK 类型应托管于独立包，还是由核心模块导出？  
- 运行时类型如何分发：置于 SDK（仅含类型定义），还是置于核心模块？  
- 如何为内置插件与外部插件分别暴露文档链接？  
- 过渡期间，是否允许仓库内插件有限度地直接导入核心模块？

## 成功标准

- 所有通道连接器均已改造为基于 SDK + 运行时的插件。  
- 完全杜绝 ``extensions/**`` 从 ``src/**`` 的导入。  
- 新建连接器模板仅依赖 SDK + 运行时。  
- 外部插件开发者无需访问核心源码即可完成开发与更新。

相关文档：[插件](/tools/plugin)、[通道](/channels/index)、[配置](/gateway/configuration)。