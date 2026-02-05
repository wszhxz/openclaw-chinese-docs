---
summary: "OpenClaw plugins/extensions: discovery, config, and safety"
read_when:
  - Adding or modifying plugins/extensions
  - Documenting plugin install or load rules
title: "Plugins"
---
# 插件（扩展）

## 快速开始（初次使用插件？）

插件只是一个**小型代码模块**，用于为 OpenClaw 扩展额外功能（命令、工具和网关 RPC）。

大多数情况下，当您需要核心 OpenClaw 中尚未内置的功能时（或者您希望将可选功能保留在主安装之外），您会使用插件。

快速路径：

1. 查看已加载的内容：

```
oc plugins list
```

2. 安装官方插件（示例：语音通话）：

```
npm install @openclaw/plugin-voice-call
```

3. 重启网关，然后在 `oc.plugins.voiceCall` 下进行配置。

有关具体示例插件，请参见 [Voice Call](/plugins/voice-call)。

## 可用插件（官方）

- Microsoft Teams 自 2026.1.15 起仅作为插件提供；如果您使用 Teams，请安装 `@openclaw/plugin-msteams`。
- Memory (Core) — 捆绑内存搜索插件（通过 `memory.core.enabled` 默认启用）
- Memory (LanceDB) — 捆绑长期记忆插件（自动回忆/捕获；设置 `memory.lancedb.autoRecall`）
- [Voice Call](/plugins/voice-call) — `@openclaw/plugin-voice-call`
- [Zalo Personal](/plugins/zalouser) — `@openclaw/plugin-zalouser`
- [Matrix](/channels/matrix) — `@openclaw/plugin-matrix`
- [Nostr](/channels/nostr) — `@openclaw/plugin-nostr`
- [Zalo](/channels/zalo) — `@openclaw/plugin-zalo`
- [Microsoft Teams](/channels/msteams) — `@openclaw/plugin-msteams`
- Google Antigravity OAuth (provider auth) — 捆绑为 `@openclaw/provider-google-auth`（默认禁用）
- Gemini CLI OAuth (provider auth) — 捆绑为 `@openclaw/provider-gemini-auth`（默认禁用）
- Qwen OAuth (provider auth) — 捆绑为 `@openclaw/provider-qwen-auth`（默认禁用）
- Copilot Proxy (provider auth) — 本地 VS Code Copilot 代理桥接；与内置的 `@openclaw/provider-copilot` 设备登录不同（捆绑，默认禁用）

OpenClaw 插件是通过 jiti 在运行时加载的**TypeScript 模块**。**配置验证不会执行插件代码**；而是使用插件清单和 JSON Schema。请参见 [Plugin manifest](/plugins/manifest)。

插件可以注册：

- 网关 RPC 方法
- 网关 HTTP 处理器
- 代理工具
- CLI 命令
- 后台服务
- 可选配置验证
- **技能**（通过在插件清单中列出 `skills` 目录）
- **自动回复命令**（无需调用 AI 代理即可执行）

插件与网关**进程内**运行，因此将它们视为受信任的代码。
工具编写指南：[Plugin agent tools](/plugins/agent-tools)。

## 运行时助手

插件可以通过 `core.helpers` 访问选定的核心助手。对于电话 TTS：

```ts
import { core } from '@hicommonwealth/core';
const { audio } = await core.helpers.telephonyTTS({
  text: 'Hello world',
  voice: 'alloy',
});
// audio: { buffer: ArrayBuffer, sampleRate: number }
```

注意事项：

- 使用核心 `tts` 配置（OpenAI 或 ElevenLabs）。
- 返回 PCM 音频缓冲区 + 采样率。插件必须为提供商重新采样/编码。
- 电话不支持 Edge TTS。

## 发现与优先级

OpenClaw 按顺序扫描：

1. 配置路径

- `configPath`（文件或目录）

2. 工作区扩展

- `<workspace>/.openclaw/extensions/*.ts`
- `<workspace>/.openclaw/extensions/*/index.ts`

3. 全局扩展

- `~/.openclaw/extensions/*.ts`
- `~/.openclaw/extensions/*/index.ts`

4. 捆绑扩展（随 OpenClaw 一起提供，**默认禁用**）

- `<openclaw>/extensions/*`

捆绑插件必须通过 `plugins.entries.<id>.enabled`
或 `openclaw plugins enable <id>` 明确启用。已安装的插件默认启用，
但可以通过相同方式禁用。

每个插件必须在其根目录包含一个 `openclaw.plugin.json` 文件。如果路径
指向文件，则插件根目录是该文件的目录，并且必须包含清单文件。

如果多个插件解析到相同的 id，则按上述顺序第一个匹配项获胜，
较低优先级的副本将被忽略。

### 包集合

插件目录可能包含一个带有 `openclaw.extensions` 的 `package.json`：

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"]
  }
}
```

每个条目成为一个插件。如果包列出多个扩展，则插件 id
变为 `name/<fileBase>`。

如果您的插件导入 npm 依赖项，请在该目录中安装它们以便
`node_modules` 可用（`npm install` / `pnpm install`）。

### 频道目录元数据

频道插件可以通过 `openclaw.channel` 广告入门元数据，
通过 `openclaw.install` 广告安装提示。这使核心目录保持无数据状态。

示例：

```json
{
  "name": "@openclaw/nextcloud-talk",
  "openclaw": {
    "extensions": ["./index.ts"],
    "channel": {
      "id": "nextcloud-talk",
      "label": "Nextcloud Talk",
      "selectionLabel": "Nextcloud Talk (self-hosted)",
      "docsPath": "/channels/nextcloud-talk",
      "docsLabel": "nextcloud-talk",
      "blurb": "Self-hosted chat via Nextcloud Talk webhook bots.",
      "order": 65,
      "aliases": ["nc-talk", "nc"]
    },
    "install": {
      "npmSpec": "@openclaw/nextcloud-talk",
      "localPath": "extensions/nextcloud-talk",
      "defaultChoice": "npm"
    }
  }
}
```

OpenClaw 还可以合并**外部频道目录**（例如，MPM
注册表导出）。在以下位置之一放置 JSON 文件：

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

或者将 `OPENCLAW_PLUGIN_CATALOG_PATHS`（或 `OPENCLAW_MPM_CATALOG_PATHS`）指向
一个或多个 JSON 文件（逗号/分号/`PATH` 分隔）。每个文件应
包含 `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`。

## 插件 ID

默认插件 id：

- 包集合：`package.json` `name`
- 独立文件：文件基本名称（`~/.../voice-call.ts` → `voice-call`）

如果插件导出 `id`，OpenClaw 使用它但在与
配置的 id 不匹配时发出警告。

## 配置

```yaml
plugins:
  enabled: true                    # master toggle (default: true)
  allow: [ "my-plugin" ]          # allowlist (optional)
  deny: [ "other-plugin" ]        # denylist (optional; deny wins)
  paths: [ "/path/to/my/plugin" ] # extra plugin files/dirs
  config:
    my-plugin:
      foo: bar                    # per‑plugin toggles + config
```

字段：

- `enabled`: 主开关（默认值：true）
- `allow`: 允许列表（可选）
- `deny`: 拒绝列表（可选；拒绝优先）
- `paths`: 额外的插件文件/目录
- `config`: 每个插件的开关+配置

配置更改**需要重启网关**。

验证规则（严格）：

- `allow`、`deny`、`paths` 或 `config` 中未知的插件ID是**错误**。
- 除非插件清单声明了通道ID，否则未知的`config`键是**错误**。
- 插件配置使用嵌入在`kong.yaml`（`_plugin_manifest`）中的JSON模式进行验证。
- 如果插件被禁用，其配置会被保留并发出**警告**。

## 插件槽位（独占类别）

某些插件类别是**独占的**（一次只能有一个处于活动状态）。使用`config`来选择哪个插件拥有该槽位：

```yaml
plugins:
  config:
    my-plugin:
      slot: "auth"
```

如果多个插件声明`slot`，只有选定的插件会加载。其他插件会被禁用并显示诊断信息。

## 控制UI（模式+标签）

控制UI使用`_gui_schema`（JSON模式+标签）来渲染更好的表单。

OpenClaw基于发现的插件在运行时增强`_gui_schema`：

- 为`allow` / `deny` / `paths` 添加每个插件的标签
- 合并插件提供的可选配置字段提示到以下位置：
  `_gui_hints`

如果您希望插件配置字段显示良好的标签/占位符（并将密钥标记为敏感），请在插件清单中与JSON模式一起提供`_gui_hints`。

示例：

```yaml
# kong.yaml
name: my-plugin
version: 1.0.0
priority: 100
_schema: 
  type: object
  properties:
    api_key:
      type: string
_gui_schema:
  labels:
    api_key: "API Key"
  placeholders:
    api_key: "Enter your API key"
  secrets:
    - "api_key"
```

## CLI

```bash
kong plugins list
```

`kong plugins list` 仅适用于跟踪在`$KONG_PREFIX/.rock_manifest`下的npm安装。

插件也可以注册自己的顶级命令（示例：`openclaw voicecall`）。

## 插件 API（概述）

插件导出以下任一内容：

- 一个函数：`(api) => { ... }`
- 一个对象：`{ id, name, configSchema, register(api) { ... } }`

## 插件钩子

插件可以打包钩子并在运行时注册它们。这使得插件包能够实现事件驱动的自动化，而无需单独安装钩子包。

### 示例

```
import { registerPluginHooksFromDir } from "openclaw/plugin-sdk";

export default function register(api) {
  registerPluginHooksFromDir(api, "./hooks");
}
```

注意事项：

- 钩子目录遵循正常的钩子结构（`HOOK.md` + `handler.ts`）。
- 钩子资格规则仍然适用（操作系统/二进制文件/环境/配置要求）。
- 插件管理的钩子会在 `openclaw hooks list` 中以 `plugin:<id>` 的形式出现。
- 您无法通过 `openclaw hooks` 启用/禁用插件管理的钩子；请启用/禁用插件本身。

## 提供者插件（模型认证）

插件可以注册**模型提供者认证**流程，使用户能够在 OpenClaw 内部运行 OAuth 或
API 密钥设置（无需外部脚本）。

通过 `api.registerProvider(...)` 注册提供者。每个提供者公开一个
或多个认证方法（OAuth、API 密钥、设备代码等）。这些方法支持：

- `openclaw models auth login --provider <id> [--method <id>]`

示例：

```ts
api.registerProvider({
  id: "acme",
  label: "AcmeAI",
  auth: [
    {
      id: "oauth",
      label: "OAuth",
      kind: "oauth",
      run: async (ctx) => {
        // Run OAuth flow and return auth profiles.
        return {
          profiles: [
            {
              profileId: "acme:default",
              credential: {
                type: "oauth",
                provider: "acme",
                access: "...",
                refresh: "...",
                expires: Date.now() + 3600 * 1000,
              },
            },
          ],
          defaultModel: "acme/opus-1",
        };
      },
    },
  ],
});
```

注意事项：

- `run` 接收一个带有 `ProviderAuthContext`、`prompter`、
  `runtime` 和 `openUrl` 辅助方法的 `oauth.createVpsAwareHandlers`。
- 当需要添加默认模型或提供者配置时，返回 `configPatch`。
- 返回 `defaultModel` 以便 `--set-default` 可以更新代理默认值。

### 注册消息通道

插件可以注册行为类似于内置通道的**通道插件**
（WhatsApp、Telegram 等）。通道配置位于 `channels.<id>` 下，并由
您的通道插件代码进行验证。

```ts
const myChannel = {
  id: "acmechat",
  meta: {
    id: "acmechat",
    label: "AcmeChat",
    selectionLabel: "AcmeChat (API)",
    docsPath: "/channels/acmechat",
    blurb: "demo channel plugin.",
    aliases: ["acme"],
  },
  capabilities: { chatTypes: ["direct"] },
  config: {
    listAccountIds: (cfg) => Object.keys(cfg.channels?.acmechat?.accounts ?? {}),
    resolveAccount: (cfg, accountId) =>
      cfg.channels?.acmechat?.accounts?.[accountId ?? "default"] ?? {
        accountId,
      },
  },
  outbound: {
    deliveryMode: "direct",
    sendText: async () => ({ ok: true }),
  },
};

export default function (api) {
  api.registerChannel({ plugin: myChannel });
}
```

注意事项：

- 将配置放在 `channels.<id>` 下（不是 `plugins.entries`）。
- `meta.label` 用于 CLI/UI 列表中的标签。
- `meta.aliases` 为标准化和 CLI 输入添加备用 ID。
- `meta.preferOver` 列出当两者都配置时跳过自动启用的频道 ID。
- `meta.detailLabel` 和 `meta.systemImage` 让 UI 显示更丰富的频道标签/图标。

### 编写新的消息频道（逐步指南）

当你需要一个**新的聊天界面**（"消息频道"）而不是模型提供商时，请使用此方法。
模型提供商文档位于 `/providers/*` 下。

1. 选择 ID + 配置形状

- 所有频道配置都位于 `channels.<id>` 下。
- 多账户设置优先使用 `channels.<id>.accounts.<accountId>`。

2. 定义频道元数据

- `meta.label`、`meta.selectionLabel`、`meta.docsPath`、`meta.blurb` 控制 CLI/UI 列表。
- `meta.docsPath` 应指向类似 `/channels/<id>` 的文档页面。
- `meta.preferOver` 让插件替换另一个频道（自动启用优先使用它）。
- `meta.detailLabel` 和 `meta.systemImage` 被 UI 用于详细文本/图标。

3. 实现必需的适配器

- `config.listAccountIds` + `config.resolveAccount`
- `capabilities`（聊天类型、媒体、线程等）
- `outbound.deliveryMode` + `outbound.sendText`（用于基本发送）

4. 根据需要添加可选适配器

- `setup`（向导）、`security`（私信策略）、`status`（健康/诊断）
- `gateway`（启动/停止/登录）、`mentions`、`threading`、`streaming`
- `actions`（消息操作）、`commands`（原生命令行为）

5. 在插件中注册频道

- `api.registerChannel({ plugin })`

最小配置示例：

```json5
{
  channels: {
    acmechat: {
      accounts: {
        default: { token: "ACME_TOKEN", enabled: true },
      },
    },
  },
}
```

最小频道插件（仅出站）：

```ts
const plugin = {
  id: "acmechat",
  meta: {
    id: "acmechat",
    label: "AcmeChat",
    selectionLabel: "AcmeChat (API)",
    docsPath: "/channels/acmechat",
    blurb: "AcmeChat messaging channel.",
    aliases: ["acme"],
  },
  capabilities: { chatTypes: ["direct"] },
  config: {
    listAccountIds: (cfg) => Object.keys(cfg.channels?.acmechat?.accounts ?? {}),
    resolveAccount: (cfg, accountId) =>
      cfg.channels?.acmechat?.accounts?.[accountId ?? "default"] ?? {
        accountId,
      },
  },
  outbound: {
    deliveryMode: "direct",
    sendText: async ({ text }) => {
      // deliver `text` to your channel here
      return { ok: true };
    },
  },
};

export default function (api) {
  api.registerChannel({ plugin });
}
```

加载插件（extensions 目录或 `plugins.load.paths`），重启网关，
然后在你的配置中配置 `channels.<id>`。

### 代理工具

参见专门指南：[插件代理工具](/plugins/agent-tools)。

### 注册网关 RPC 方法

```ts
export default function (api) {
  api.registerGatewayMethod("myplugin.status", ({ respond }) => {
    respond(true, { ok: true });
  });
}
```

### 注册 CLI 命令

```ts
export default function (api) {
  api.registerCli(
    ({ program }) => {
      program.command("mycmd").action(() => {
        console.log("Hello");
      });
    },
    { commands: ["mycmd"] },
  );
}
```

### 注册自动回复命令

插件可以注册自定义斜杠命令，这些命令**无需调用
AI 代理**即可执行。这对于切换命令、状态检查或不需要 LLM 处理的快速操作很有用。

```ts
export default function (api) {
  api.registerCommand({
    name: "mystatus",
    description: "Show plugin status",
    handler: (ctx) => ({
      text: `Plugin is running! Channel: ${ctx.channel}`,
    }),
  });
}
```

命令处理器上下文：

- `senderId`: 发送者的 ID（如果可用）
- `channel`: 命令发送到的频道
- `isAuthorizedSender`: 发送者是否为授权用户
- `args`: 命令后传递的参数（如果 `acceptsArgs: true`）
- `commandBody`: 完整的命令文本
- `config`: 当前的 OpenClaw 配置

命令选项：

- `name`: 命令名称（不包含前导的 `/`）
- `description`: 在命令列表中显示的帮助文本
- `acceptsArgs`: 命令是否接受参数（默认值：false）。如果为 false 且提供了参数，则命令不会匹配，消息会传递给其他处理器
- `requireAuth`: 是否需要授权发送者（默认值：true）
- `handler`: 返回 `{ text: string }` 的函数（可以是异步的）

带授权和参数的示例：

```ts
api.registerCommand({
  name: "setmode",
  description: "Set plugin mode",
  acceptsArgs: true,
  requireAuth: true,
  handler: async (ctx) => {
    const mode = ctx.args?.trim() || "default";
    await saveMode(mode);
    return { text: `Mode set to: ${mode}` };
  },
});
```

注意事项：

- 插件命令在内置命令和AI代理之前处理
- 命令是全局注册的，在所有频道中都有效
- 命令名称不区分大小写（`/MyStatus` 匹配 `/mystatus`）
- 命令名称必须以字母开头，只能包含字母、数字、连字符和下划线
- 预留的命令名称（如 `help`、`status`、`reset` 等）不能被插件覆盖
- 跨插件的重复命令注册将失败并显示诊断错误

### 注册后台服务

```ts
export default function (api) {
  api.registerService({
    id: "my-service",
    start: () => api.logger.info("ready"),
    stop: () => api.logger.info("bye"),
  });
}
```

## 命名约定

- 网关方法：`pluginId.action`（示例：`voicecall.status`）
- 工具：`snake_case`（示例：`voice_call`）
- CLI命令：kebab或camel，但避免与核心命令冲突

## 技能

插件可以在仓库中发布技能（`skills/<name>/SKILL.md`）。
使用 `plugins.entries.<id>.enabled`（或其他配置门）启用它，并确保
它存在于您的工作区/管理技能位置中。

## 分发（npm）

推荐打包方式：

- 主包：`openclaw`（此仓库）
- 插件：在 `@openclaw/*` 下的单独npm包（示例：`@openclaw/voice-call`）

发布合同：

- 插件 `package.json` 必须包含带有一个或多个入口文件的 `openclaw.extensions`。
- 入口文件可以是 `.js` 或 `.ts`（jiti在运行时加载TS）。
- `openclaw plugins install <npm-spec>` 使用 `npm pack`，提取到 `~/.openclaw/extensions/<id>/` 中，并在配置中启用它。
- 配置键稳定性：作用域包被规范化为用于 `plugins.entries.*` 的**无作用域**id。

## 示例插件：语音通话

此仓库包含一个语音通话插件（Twilio或日志回退）：

- 源码：`extensions/voice-call`
- 技能：`skills/voice-call`
- CLI：`openclaw voicecall start|status`
- 工具：`voice_call`
- RPC：`voicecall.start`、`voicecall.status`
- 配置（twilio）：`provider: "twilio"` + `twilio.accountSid/authToken/from`（可选 `statusCallbackUrl`、`twimlUrl`）
- 配置（开发）：`provider: "log"`（无网络）

查看 [语音通话](/plugins/voice-call) 和 `extensions/voice-call/README.md` 了解设置和使用方法。

## 安全注意事项

插件与网关在同一进程中运行。将其视为受信任的代码：

- 只安装您信任的插件。
- 优先使用 `plugins.allow` 白名单。
- 更改后重启网关。

## 测试插件

插件可以（并且应该）附带测试：

- 仓库内插件可以在 `src/**` 下保留Vitest测试（示例：`src/plugins/voice-call.plugin.test.ts`）。
- 单独发布的插件应运行自己的CI（lint/build/test）并验证 `openclaw.extensions` 指向构建后的入口点（`dist/index.js`）。