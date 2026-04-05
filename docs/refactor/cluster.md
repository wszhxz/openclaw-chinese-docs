---
summary: "Refactor clusters with highest LOC reduction potential"
read_when:
  - You want to reduce total LOC without changing behavior
  - You are choosing the next dedupe or extraction pass
title: "Refactor Cluster Backlog"
---
# 重构集群积压任务

按可能的 LOC 减少量、安全性和广度排序。

## 1. 频道插件配置与安全脚手架

最高价值集群。

许多频道插件中重复的模式：

- `config.listAccountIds`
- `config.resolveAccount`
- `config.defaultAccountId`
- `config.setAccountEnabled`
- `config.deleteAccount`
- `config.describeAccount`
- `security.resolveDmPolicy`

典型示例：

- `extensions/telegram/src/channel.ts`
- `extensions/googlechat/src/channel.ts`
- `extensions/slack/src/channel.ts`
- `extensions/discord/src/channel.ts`
- `extensions/matrix/src/channel.ts`
- `extensions/irc/src/channel.ts`
- `extensions/signal/src/channel.ts`
- `extensions/mattermost/src/channel.ts`

可能的提取形态：

- `buildChannelConfigAdapter(...)`
- `buildMultiAccountConfigAdapter(...)`
- `buildDmSecurityAdapter(...)`

预期节省：

- ~250-450 LOC

风险：

- 中等。每个频道有略微不同的 `isConfigured`、警告和规范化。

## 2. 扩展运行时单例样板代码

非常安全。

几乎每个扩展都有相同的运行时持有者：

- `let runtime: PluginRuntime | null = null`
- `setXRuntime`
- `getXRuntime`

典型示例：

- `extensions/telegram/src/runtime.ts`
- `extensions/matrix/src/runtime.ts`
- `extensions/slack/src/runtime.ts`
- `extensions/discord/src/runtime.ts`
- `extensions/whatsapp/src/runtime.ts`
- `extensions/imessage/src/runtime.ts`
- `extensions/twitch/src/runtime.ts`

特殊情况变体：

- `extensions/bluebubbles/src/runtime.ts`
- `extensions/line/src/runtime.ts`
- `extensions/synology-chat/src/runtime.ts`

可能的提取形态：

- `createPluginRuntimeStore<T>(errorMessage)`

预期节省：

- ~180-260 LOC

风险：

- 低

## 3. 入职提示与配置补丁步骤

影响面较大。

许多入职文件重复：

- 解析账户 ID
- 提示白名单条目
- 合并 allowFrom
- 设置 DM 策略
- 提示密钥
- 修补顶层与账户范围配置

典型示例：

- `extensions/bluebubbles/src/onboarding.ts`
- `extensions/googlechat/src/onboarding.ts`
- `extensions/msteams/src/onboarding.ts`
- `extensions/zalo/src/onboarding.ts`
- `extensions/zalouser/src/onboarding.ts`
- `extensions/nextcloud-talk/src/onboarding.ts`
- `extensions/matrix/src/onboarding.ts`
- `extensions/irc/src/onboarding.ts`

现有辅助接口：

- `src/channels/plugins/onboarding/helpers.ts`

可能的提取形态：

- `promptAllowFromList(...)`
- `buildDmPolicyAdapter(...)`
- `applyScopedAccountPatch(...)`
- `promptSecretFields(...)`

预期节省：

- ~300-600 LOC

风险：

- 中等。容易过度泛化；保持辅助函数狭窄且可组合。

## 4. 多账户配置模式片段

扩展间重复的模式片段。

常见模式：

- `const allowFromEntry = z.union([z.string(), z.number()])`
- 账户模式加上：
  - `accounts: z.object({}).catchall(accountSchema).optional()`
  - `defaultAccount: z.string().optional()`
- 重复的 DM/组字段
- 重复的 Markdown/工具策略字段

典型示例：

- `extensions/bluebubbles/src/config-schema.ts`
- `extensions/zalo/src/config-schema.ts`
- `extensions/zalouser/src/config-schema.ts`
- `extensions/matrix/src/config-schema.ts`
- `extensions/nostr/src/config-schema.ts`

可能的提取形态：

- `AllowFromEntrySchema`
- `buildMultiAccountChannelSchema(accountSchema)`
- `buildCommonDmGroupFields(...)`

预期节省：

- ~120-220 LOC

风险：

- 低至中等。有些模式简单，有些特殊。

## 5. Webhook 与监控生命周期启动

良好的中等价值集群。

重复的 `startAccount` / 监控设置模式：

- 解析账户
- 计算 Webhook 路径
- 记录启动
- 启动监控
- 等待中止
- 清理
- 状态接收器更新

典型示例：

- `extensions/googlechat/src/channel.ts`
- `extensions/bluebubbles/src/channel.ts`
- `extensions/zalo/src/channel.ts`
- `extensions/telegram/src/channel.ts`
- `extensions/nextcloud-talk/src/channel.ts`

现有辅助接口：

- `src/plugin-sdk/channel-lifecycle.ts`

可能的提取形态：

- 账户监控生命周期辅助函数
- 基于 Webhook 的账户启动辅助函数

预期节省：

- ~150-300 LOC

风险：

- 中等至高。传输细节迅速分化。

## 6. 小型精确克隆清理

低风险清理类别。

示例：

- 重复的网关 argv 检测：
  - `src/infra/gateway-lock.ts`
  - `src/cli/daemon-cli/lifecycle.ts`
- 重复的端口诊断渲染：
  - `src/cli/daemon-cli/restart-health.ts`
- 重复的 session-key 构建：
  - `src/web/auto-reply/monitor/broadcast.ts`

预期节省：

- ~30-60 LOC

风险：

- 低

## 测试集群

### LINE Webhook 事件夹具

典型示例：

- `src/line/bot-handlers.test.ts`

可能提取：

- `makeLineEvent(...)`
- `runLineEvent(...)`
- `makeLineAccount(...)`

预期节省：

- ~120-180 LOC

### Telegram 原生命令授权矩阵

典型示例：

- `src/telegram/bot-native-commands.group-auth.test.ts`
- `src/telegram/bot-native-commands.plugin-auth.test.ts`

可能提取：

- 论坛上下文构建器
- 拒绝消息断言辅助函数
- 表驱动授权用例

预期节省：

- ~80-140 LOC

### Zalo 生命周期设置

典型示例：

- `extensions/zalo/src/monitor.lifecycle.test.ts`

可能提取：

- 共享监控设置框架

预期节省：

- ~50-90 LOC

### Brave LLM 上下文不支持选项测试

典型示例：

- `src/agents/tools/web-tools.enabled-defaults.test.ts`

可能提取：

- `it.each(...)` 矩阵

预期节省：

- ~30-50 LOC

## 建议顺序

1. 运行时单例样板代码
2. 小型精确克隆清理
3. 配置与安全构建器提取
4. 测试辅助函数提取
5. 入职步骤提取
6. 监控生命周期辅助函数提取