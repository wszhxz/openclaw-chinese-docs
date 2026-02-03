---
summary: "OpenClaw plugins/extensions: discovery, config, and safety"
read_when:
  - Adding or modifying plugins/extensions
  - Documenting plugin install or load rules
title: "Plugins"
---
以下是该技术文档的中文翻译：

---

# 插件翻译指南

## 翻译方法
翻译可通过以下方式实现：
- 使用 `plugins.entries` 配置项
- 或其他配置门控（config gates）

## 注册命令
插件可通过以下方式注册命令：
```ts
export default function (api) {
  api.registerCommand({
    name: "mystatus",
    description: "显示插件状态",
    handler: (ctx) => ({
      text: `插件正在运行！通道: ${ctx.channel}`,
    }),
  });
}
```

### 命令处理上下文
- `senderId`: 发送者的ID（如果可用）
- `channel`: 命令发送的通道
- `isAuthorizedSender`: 发送者是否为授权用户
- `args`: 命令后的参数（如果 `acceptsArgs: true`）
- `commandBody`: 完整的命令文本
- `config`: 当前的OpenClaw配置

### 命令选项
- `name`: 命令名称（不带前缀 `/`）
- `description`: 命令列表中的帮助文本
- `acceptsArgs`: 命令是否接受参数（默认为false）。若为false且提供参数，命令将不匹配，消息将传递给其他处理程序
- `requireAuth`: 是否需要授权发送者（默认为true）
- `handler`: 返回 `{ text: string }` 的函数（可异步）

### 示例（带授权和参数）
```ts
api.registerCommand({
  name: "setmode",
  description: "设置插件模式",
  acceptsArgs: true,
  requireAuth: true,
  handler: async (ctx) => {
    const mode = ctx.args?.trim() || "default";
    await saveMode(mode);
    return { text: `模式设置为: ${mode}` };
  },
});
```

### 注意事项
- 插件命令在内置命令和AI代理之前处理
- 命令全局注册，适用于所有通道
- 命令名称不区分大小写（`/MyStatus` 匹配 `/mystatus`）
- 命令名称必须以字母开头，仅包含字母、数字、连字符和下划线
- 保留命令名称（如 `help`、`status`、`reset` 等）不能被插件覆盖
- 跨插件的重复命令注册将导致诊断错误

## 注册后台服务
```ts
export default function (api) {
  api.registerService({
    id: "my-service",
    start: () => api.logger.info("准备就绪"),
    stop: () => api.logger.info("再见"),
  });
}
```

## 命名规范
- 网关方法：`插件ID.动作`（示例：`voicecall.status`）
- 工具：`snake_case`（示例：`voice_call`）
- 命令行命令：kebab或camel，但避免与核心命令冲突

## 技能
插件可将技能存放在仓库中（`skills/<name>/SKILL.md`）。通过 `plugins.entries.<id>.enabled`（或其他配置门控）启用，并确保其存在于您的工作区/管理技能位置。

## 分发（npm）
推荐打包：
- 主包：`openclaw`（本仓库）
- 插件：单独的npm包（`@openclaw/*`）（示例：`@openclaw/voice-call`）

发布协议：
- 插件 `package.json` 必须包含 `openclaw.extensions`，其中包含一个或多个入口文件。
- 入口文件可以是 `.js` 或 `.ts`（jiti在运行时加载TS）。
- `openclaw plugins install <npm-spec>` 使用 `npm pack`，提取到 `~/.openclaw/extensions/<id>/`，并在配置中启用。
- 配置键稳定性：作用域包会规范化为 **无作用域** ID 用于 `plugins.entries.*`。

## 示例插件：语音通话
本仓库包含一个语音通话插件（Twilio或日志回退）：
- 源代码：`extensions/voice-call`
- 技能：`skills/voice-call`
- 命令行：`openclaw voicecall start|status`
- 工具：`voice_call`
- RPC：`voicecall.start`、`voicecall.status`
- 配置（Twilio）：`provider: "twilio"` + `twilio.accountSid/authToken/from`（可选 `statusCallbackUrl`、`twimlUrl`）
- 配置（开发）：`provider: "log"`（无网络）

查看 [语音通话](/plugins/voice-call) 和 `extensions/voice-call/README.md` 获取设置和使用说明。

## 安全注意事项
插件与网关同进程运行。请将它们视为受信任的代码：
- 仅安装您信任的插件。
- 优先使用 `plugins.allow` 允许列表。
- 在更改后重启网关。

## 测试插件
插件应（且应）附带测试：
- 仓库内插件可将Vitest测试保留在 `src/**`（示例：`src/plugins/voice-call.plugin.test.ts`）。
- 独立发布的插件应运行自己的CI（lint/build/test），并验证 `openclaw.extensions` 指向构建后的入口点（`dist/index.js`）。