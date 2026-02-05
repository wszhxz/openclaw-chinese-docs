---
summary: "OpenClaw plugins/extensions: discovery, config, and safety"
read_when:
  - Adding or modifying plugins/extensions
  - Documenting plugin install or load rules
title: "Plugins"
---
# 插件 (扩展)

## 快速入门 (新用户？)

插件只是一个**小型代码模块**，用于通过额外功能（命令、工具和网关RPC）扩展OpenClaw。

大多数时候，当你想要一个尚未内置到核心OpenClaw中的功能（或者你希望将可选功能保留在主要安装之外）时，会使用插件。

快速路径：

1. 查看已加载的内容：

```bash
openclaw plugins list
```

2. 安装官方插件（示例：语音通话）：

```bash
openclaw plugins install @openclaw/voice-call
```

3. 重启网关，然后在`plugins.entries.<id>.config`下进行配置。

参见[语音通话](/plugins/voice-call)获取具体示例插件。

## 可用插件（官方）

- 自2026.1.15起，Microsoft Teams仅作为插件提供；如果你使用Teams，请安装`@openclaw/msteams`。
- 内存 (核心) — 内置内存搜索插件（默认通过`plugins.slots.memory`启用）
- 内存 (LanceDB) — 内置长期记忆插件（自动回忆/捕获；设置`plugins.slots.memory = "memory-lancedb"`)
- [语音通话](/plugins/voice-call) — `@openclaw/voice-call`
- [Zalo个人](/plugins/zalouser) — `@openclaw/zalouser`
- [Matrix](/channels/matrix) — `@openclaw/matrix`
- [Nostr](/channels/nostr) — `@openclaw/nostr`
- [Zalo](/channels/zalo) — `@openclaw/zalo`
- [Microsoft Teams](/channels/msteams) — `@openclaw/msteams`
- Google Antigravity OAuth（提供商认证） — 内置为`google-antigravity-auth`（默认禁用）
- Gemini CLI OAuth（提供商认证） — 内置为`google-gemini-cli-auth`（默认禁用）
- Qwen OAuth（提供商认证） — 内置为`qwen-portal-auth`（默认禁用）
- Copilot Proxy（提供商认证） — 本地VS Code Copilot Proxy桥接；与内置的`github-copilot`设备登录不同（内置，默认禁用）

OpenClaw插件是通过jiti在运行时加载的**TypeScript模块**。**配置验证不会执行插件代码**；它使用插件清单和JSON Schema。参见[插件清单](/plugins/manifest)。

插件可以注册：

- 网关RPC方法
- 网关HTTP处理程序
- 代理工具
- CLI命令
- 后台服务
- 可选配置验证
- **技能**（在插件清单中列出`skills`目录）
- **自动回复命令**（无需调用AI代理即可执行）

插件与网关**在同一进程中**运行，因此请将其视为可信代码。
工具创作指南：[插件代理工具](/plugins/agent-tools)。

## 运行时辅助工具

插件可以通过`api.runtime`访问选定的核心辅助工具。对于电话TTS：

```ts
const result = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});
```

注意事项：

- 使用核心`messages.tts`配置（OpenAI或ElevenLabs）。
- 返回PCM音频缓冲区+采样率。插件必须对提供商进行重采样/编码。
- Edge TTS不支持电话。

## 发现与优先级

OpenClaw按顺序扫描：

1. 配置路径

- `plugins.load.paths`（文件或目录）

2. 工作区扩展

- `<workspace>/.openclaw/extensions/*.ts`
- `<workspace>/.openclaw/extensions/*/index.ts`

3. 全局扩展

- `~/.openclaw/extensions/*.ts`
- `~/.openclaw/extensions/*/index.ts`

4. 内置扩展（随 OpenClaw 发布，默认情况下**禁用**）

- `<openclaw>/extensions/*`

必须通过 `plugins.entries.<id>.enabled`
或 `openclaw plugins enable <id>` 显式启用内置插件。已安装的插件默认启用，
但可以通过相同的方式禁用。

每个插件必须在其根目录中包含一个 `openclaw.plugin.json` 文件。如果路径
指向一个文件，则插件根目录是该文件的目录，并且必须包含
清单文件。

如果有多个插件解析为相同的 id，则上述顺序中的第一个匹配项获胜，优先级较低的副本将被忽略。

### 包包

插件目录可以包含一个 `package.json`，其中包含 `openclaw.extensions`：

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"]
  }
}
```

每个条目都会成为一个插件。如果包列出了多个扩展，插件 id
变为 `name/<fileBase>`。

如果您的插件导入了 npm 依赖项，请在该目录中安装它们，以便
`node_modules` 可用 (`npm install` / `pnpm install`)。

### 频道目录元数据

频道插件可以通过 `openclaw.channel` 广告入门元数据，并通过 `openclaw.install` 提供安装提示。这使核心目录数据保持无污染。

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
注册表导出）。将 JSON 文件放置在以下位置之一：

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

或者将 `OPENCLAW_PLUGIN_CATALOG_PATHS`（或 `OPENCLAW_MPM_CATALOG_PATHS`）指向
一个或多个 JSON 文件（以逗号/分号/`PATH` 分隔）。每个文件应
包含 `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`。

## 插件 ID

默认插件 ID：

- 包包：`package.json` `name`
- 单独文件：文件基名 (`~/.../voice-call.ts` → `voice-call`)

如果插件导出了 `id`，OpenClaw 使用它但在不匹配配置的 ID 时会发出警告。

## 配置

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: ["untrusted-plugin"],
    load: { paths: ["~/Projects/oss/voice-call-extension"] },
    entries: {
      "voice-call": { enabled: true, config: { provider: "twilio" } },
    },
  },
}
```

字段:

- `enabled`: 主开关（默认: true）
- `allow`: 允许列表（可选）
- `deny`: 拒绝列表（可选；拒绝优先）
- `load.paths`: 额外插件文件/目录
- `entries.<id>`: 每个插件的开关 + 配置

配置更改 **需要网关重启**。

验证规则（严格）:

- `entries`、`allow`、`deny` 或 `slots` 中未知的插件ID是 **错误**。
- 除非插件清单声明了通道ID，否则未知的 `channels.<id>` 键是 **错误**。
- 使用嵌入在 `openclaw.plugin.json` (`configSchema`) 中的JSON Schema验证插件配置。
- 如果禁用了插件，其配置将被保留并发出 **警告**。

## 插件插槽（独占类别）

某些插件类别是 **独占** 的（一次只有一个活动）。使用 `plugins.slots` 选择哪个插件拥有该插槽：

```json5
{
  plugins: {
    slots: {
      memory: "memory-core", // or "none" to disable memory plugins
    },
  },
}
```

如果多个插件声明了 `kind: "memory"`，只有选定的一个会被加载。其他插件会被禁用并进行诊断。

## 控制UI（模式 + 标签）

控制UI使用 `config.schema`（JSON Schema + `uiHints`）来渲染更好的表单。

OpenClaw在运行时根据发现的插件增强 `uiHints`：

- 为每个插件添加 `plugins.entries.<id>` / `.enabled` / `.config` 的标签
- 合并可选的插件提供的配置字段提示到：
  `plugins.entries.<id>.config.<field>`

如果你想让你的插件配置字段显示良好的标签/占位符（并将密钥标记为敏感），请在插件清单中提供 `uiHints` 与你的JSON Schema一起。

示例：

```json
{
  "id": "my-plugin",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "apiKey": { "type": "string" },
      "region": { "type": "string" }
    }
  },
  "uiHints": {
    "apiKey": { "label": "API Key", "sensitive": true },
    "region": { "label": "Region", "placeholder": "us-east-1" }
  }
}
```

## 命令行界面

```bash
openclaw plugins list
openclaw plugins info <id>
openclaw plugins install <path>                 # copy a local file/dir into ~/.openclaw/extensions/<id>
openclaw plugins install ./extensions/voice-call # relative path ok
openclaw plugins install ./plugin.tgz           # install from a local tarball
openclaw plugins install ./plugin.zip           # install from a local zip
openclaw plugins install -l ./extensions/voice-call # link (no copy) for dev
openclaw plugins install @openclaw/voice-call # install from npm
openclaw plugins update <id>
openclaw plugins update --all
openclaw plugins enable <id>
openclaw plugins disable <id>
openclaw plugins doctor
```

`plugins update` 仅适用于在 `plugins.installs` 下跟踪的npm安装。

插件还可以注册自己的顶级命令（示例：`openclaw voicecall`）。

## 插件API（概述）

插件导出以下内容之一：

- 一个函数：`(api) => { ... }`
- 一个对象：`{ id, name, configSchema, register(api) { ... } }`

## 插件钩子

插件可以打包钩子并在运行时注册它们。这使得插件可以捆绑事件驱动的自动化，而无需单独安装钩子包。

### 示例

```
import { registerPluginHooksFromDir } from "openclaw/plugin-sdk";

export default function register(api) {
  registerPluginHooksFromDir(api, "./hooks");
}
```

注意事项：

- 钩子目录遵循正常的钩子结构 (`HOOK.md` + `handler.ts`)。
- 钩子资格规则仍然适用（操作系统/二进制文件/环境/配置要求）。
- 由插件管理的钩子会显示在 `openclaw hooks list` 中，带有 `plugin:<id>`。
- 不能通过 `openclaw hooks` 启用或禁用由插件管理的钩子；请启用或禁用插件本身。

## 提供者插件（模型认证）

插件可以注册 **模型提供者认证** 流程，以便用户可以在 OpenClaw 内部运行 OAuth 或 API 密钥设置（无需外部脚本）。

通过 `api.registerProvider(...)` 注册一个提供者。每个提供者公开一种或多种认证方法（OAuth、API 密钥、设备代码等）。这些方法支持：

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

- `run` 接收一个 `ProviderAuthContext`，其中包含 `prompter`、`runtime`、
  `openUrl` 和 `oauth.createVpsAwareHandlers` 辅助工具。
- 当需要添加默认模型或提供者配置时，返回 `configPatch`。
- 返回 `defaultModel` 以便 `--set-default` 可以更新代理默认设置。

### 注册消息通道

插件可以注册 **通道插件**，这些插件的行为类似于内置通道（WhatsApp、Telegram 等）。通道配置位于 `channels.<id>` 下，并由您的通道插件代码进行验证。

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

- 将配置放在 `channels.<id>` 下（而不是 `plugins.entries`）。
- `meta.label` 用于CLI/UI列表中的标签。
- `meta.aliases` 添加备用ID以进行规范化和CLI输入。
- `meta.preferOver` 列出在同时配置时要跳过自动启用的通道ID。
- `meta.detailLabel` 和 `meta.systemImage` 让UI显示更丰富的通道标签/图标。

### 编写新的消息通道（分步指南）

当您需要一个新的 **聊天界面**（“消息通道”），而不是模型提供商时使用此方法。
模型提供商文档位于 `/providers/*` 下。

1. 选择一个ID + 配置形状

- 所有通道配置都位于 `channels.<id>` 下。
- 对于多账户设置，请优先使用 `channels.<id>.accounts.<accountId>`。

2. 定义通道元数据

- `meta.label`，`meta.selectionLabel`，`meta.docsPath`，`meta.blurb` 控制CLI/UI列表。
- `meta.docsPath` 应该指向一个文档页面，如 `/channels/<id>`。
- `meta.preferOver` 允许插件替换另一个通道（自动启用时优先考虑它）。
- `meta.detailLabel` 和 `meta.systemImage` 由UI用于详细文本/图标。

3. 实现所需的适配器

- `config.listAccountIds` + `config.resolveAccount`
- `capabilities`（聊天类型、媒体、线程等）
- `outbound.deliveryMode` + `outbound.sendText`（用于基本发送）

4. 根据需要添加可选适配器

- `setup`（向导），`security`（DM策略），`status`（健康/诊断）
- `gateway`（启动/停止/登录），`mentions`，`threading`，`streaming`
- `actions`（消息操作），`commands`（本机命令行为）

5. 在您的插件中注册通道

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

仅限外发的最小通道插件：

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
然后在您的配置中配置 `channels.<id>`。

### 代理工具

参见专用指南：[Plugin agent tools](/plugins/agent-tools)。

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

插件可以注册自定义斜杠命令，这些命令**无需调用 AI 代理**即可执行。这对于开关命令、状态检查或不需要 LLM 处理的快速操作非常有用。

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

命令处理程序上下文：

- `senderId`: 发送者的 ID（如果可用）
- `channel`: 发送命令的频道
- `isAuthorizedSender`: 发送者是否为授权用户
- `args`: 命令后传递的参数（如果 `acceptsArgs: true`）
- `commandBody`: 完整的命令文本
- `config`: 当前的 OpenClaw 配置

命令选项：

- `name`: 命令名称（不包括前导 `/`）
- `description`: 在命令列表中显示的帮助文本
- `acceptsArgs`: 命令是否接受参数（默认：false）。如果为 false 且提供了参数，命令将不会匹配，消息将传递给其他处理程序
- `requireAuth`: 是否需要授权发送者（默认：true）
- `handler`: 返回 `{ text: string }` 的函数（可以是异步的）

带有授权和参数的示例：

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

注意：

- 插件命令在内置命令和AI代理**之前**处理
- 命令全局注册，并且在所有频道中工作
- 命令名称不区分大小写 (`/MyStatus` 匹配 `/mystatus`)
- 命令名称必须以字母开头，并且只包含字母、数字、连字符和下划线
- 预留的命令名称（如 `help`，`status`，`reset` 等）不能被插件覆盖
- 跨插件的重复命令注册将因诊断错误而失败

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

- 网关方法: `pluginId.action`（示例: `voicecall.status`）
- 工具: `snake_case`（示例: `voice_call`）
- CLI 命令: 使用连字符或驼峰命名法，但避免与核心命令冲突

## 技能

插件可以在仓库中提供一个技能 (`skills/<name>/SKILL.md`)。
使用 `plugins.entries.<id>.enabled`（或其他配置门）启用它，并确保
它存在于您的工作区/管理的技能位置。

## 分发 (npm)

推荐的打包方式：

- 主包: `openclaw`（此仓库）
- 插件: 单独的 npm 包在 `@openclaw/*` 下（示例: `@openclaw/voice-call`）

发布协议：

- 插件 `package.json` 必须包含 `openclaw.extensions`，其中包含一个或多个入口文件。
- 入口文件可以是 `.js` 或 `.ts`（jiti 在运行时加载 TS）。
- `openclaw plugins install <npm-spec>` 使用 `npm pack`，提取到 `~/.openclaw/extensions/<id>/`，并在配置中启用。
- 配置键稳定性：作用域包被规范化为 **非作用域** id 用于 `plugins.entries.*`。

## 示例插件: 语音通话

此仓库包含一个语音通话插件（Twilio 或日志回退）：

- 源码: `extensions/voice-call`
- 技能: `skills/voice-call`
- CLI: `openclaw voicecall start|status`
- 工具: `voice_call`
- RPC: `voicecall.start`，`voicecall.status`
- 配置 (twilio): `provider: "twilio"` + `twilio.accountSid/authToken/from`（可选 `statusCallbackUrl`，`twimlUrl`）
- 配置 (dev): `provider: "log"`（无网络）

参见 [语音通话](/plugins/voice-call) 和 `extensions/voice-call/README.md` 以获取设置和使用说明。

## 安全注意事项

插件与网关进程内运行。将它们视为受信任的代码：

- 仅安装您信任的插件。
- 偏好 `plugins.allow` 允许列表。
- 更改后重启网关。

## 测试插件

插件可以（并且应该）附带测试：

- 仓库内的插件可以将 Vitest 测试保留在 `src/**` 下（示例: `src/plugins/voice-call.plugin.test.ts`）。
- 单独发布的插件应运行自己的 CI（lint/build/test），并验证 `openclaw.extensions` 指向构建后的入口点 (`dist/index.js`)。