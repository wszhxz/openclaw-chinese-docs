---
summary: "OpenClaw plugins/extensions: discovery, config, and safety"
read_when:
  - Adding or modifying plugins/extensions
  - Documenting plugin install or load rules
title: "Plugins"
---
# 插件 (扩展)

## 快速入门（新接触插件？）

插件只是一个**小型代码模块**，它通过额外的功能（命令、工具和网关RPC）来扩展OpenClaw。

大多数情况下，当您需要一个尚未内置在核心OpenClaw中的功能时（或者希望将可选功能保留在主安装之外），就会使用插件。

快速路径：

1. 查看已加载的内容：

```bash
openclaw plugins list
```

2. 安装官方插件（示例：语音通话）：

```bash
openclaw plugins install @openclaw/voice-call
```

Npm规格是**仅限注册表**的（包名+可选的**确切版本**或**dist-tag**）。Git/URL/file规格和semver范围将被拒绝。

裸规格和`@latest`保持在稳定轨道上。如果npm解析这些为预发布版本，OpenClaw会停止并要求您明确选择带有预发布标签如`@beta`/`@rc`或确切预发布版本。

3. 重启网关，然后在`plugins.entries.<id>.config`下进行配置。

查看[语音通话](/plugins/voice-call)以获取具体的插件示例。
寻找第三方列表？请参阅[社区插件](/plugins/community)。

## 可用插件（官方）

- Microsoft Teams自2026.1.15起仅作为插件提供；如果您使用Teams，请安装`@openclaw/msteams`。
- 内存（核心）—捆绑的记忆搜索插件（默认通过`plugins.slots.memory`启用）
- 内存（LanceDB）—捆绑的长期记忆插件（自动回忆/捕获；设置`plugins.slots.memory = "memory-lancedb"`）
- [语音通话](/plugins/voice-call) — `@openclaw/voice-call`
- [Zalo个人版](/plugins/zalouser) — `@openclaw/zalouser`
- [Matrix](/channels/matrix) — `@openclaw/matrix`
- [Nostr](/channels/nostr) — `@openclaw/nostr`
- [Zalo](/channels/zalo) — `@openclaw/zalo`
- [Microsoft Teams](/channels/msteams) — `@openclaw/msteams`
- Google Antigravity OAuth（提供商认证）—捆绑为`google-antigravity-auth`（默认禁用）
- Gemini CLI OAuth（提供商认证）—捆绑为`google-gemini-cli-auth`（默认禁用）
- Qwen OAuth（提供商认证）—捆绑为`qwen-portal-auth`（默认禁用）
- Copilot代理（提供商认证）—本地VS Code Copilot代理桥接；与内置的`github-copilot`设备登录不同（捆绑，默认禁用）

OpenClaw插件是通过jiti在运行时加载的**TypeScript模块**。**配置验证不会执行插件代码**；而是使用插件清单和JSON Schema。请参阅[插件清单](/plugins/manifest)。

插件可以注册：

- 网关RPC方法
- 网关HTTP路由
- 代理工具
- CLI命令
- 后台服务
- 上下文引擎
- 可选配置验证
- **技能**（通过在插件清单中列出`skills`目录）
- **自动回复命令**（无需调用AI代理即可执行）

插件与网关**同进程**运行，因此应将其视为可信代码。
工具编写指南：[插件代理工具](/plugins/agent-tools)。

## 运行时辅助

插件可以通过`api.runtime`访问选定的核心辅助功能。对于电话TTS：

```ts
const result = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});
```

注意事项：

- 使用核心`messages.tts`配置（OpenAI或ElevenLabs）。
- 返回PCM音频缓冲区+采样率。插件必须重新采样/编码以适应提供商。
- Edge TTS不支持用于电话。

对于STT/转录，插件可以调用：

```ts
const { text } = await api.runtime.stt.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // Optional when MIME cannot be inferred reliably:
  mime: "audio/ogg",
});
```

注意事项：

- 使用核心媒体理解音频配置(`tools.media.audio`)和提供商回退顺序。
- 当没有产生转录输出时返回`{ text: undefined }`（例如跳过/不支持的输入）。

## 网关HTTP路由

插件可以使用`api.registerHttpRoute(...)`暴露HTTP端点。

```ts
api.registerHttpRoute({
  path: "/acme/webhook",
  auth: "plugin",
  match: "exact",
  handler: async (_req, res) => {
    res.statusCode = 200;
    res.end("ok");
    return true;
  },
});
```

路由字段：

- `path`: 在网关HTTP服务器下的路由路径。
- `auth`: 必需。使用`"gateway"`要求正常的网关认证，或使用`"plugin"`进行插件管理的认证/网络钩子验证。
- `match`: 可选。`"exact"`（默认）或`"prefix"`。
- `replaceExisting`: 可选。允许同一个插件替换其现有的路由注册。
- `handler`: 当路由处理请求时返回`true`。

注意事项：

- `api.registerHttpHandler(...)`已废弃。使用`api.registerHttpRoute(...)`。
- 插件路由必须显式声明`auth`。
- 除非`replaceExisting: true`，否则精确的`path + match`冲突将被拒绝，并且一个插件不能替换另一个插件的路由。
- 具有不同`auth`级别的重叠路由将被拒绝。仅在同一认证级别上保持`exact`/`prefix`穿透链。

## 插件SDK导入路径

在编写插件时，使用SDK子路径而不是单一的`openclaw/plugin-sdk`导入：

- `openclaw/plugin-sdk/core`用于通用插件API、提供商认证类型和共享辅助函数。
- `openclaw/plugin-sdk/compat`用于需要比`core`更广泛的共享运行时辅助函数的捆绑/内部插件代码。
- `openclaw/plugin-sdk/telegram`用于Telegram频道插件。
- `openclaw/plugin-sdk/discord`用于Discord频道插件。
- `openclaw/plugin-sdk/slack`用于Slack频道插件。
- `openclaw/plugin-sdk/signal`用于Signal频道插件。
- `openclaw/plugin-sdk/imessage`用于iMessage频道插件。
- `openclaw/plugin-sdk/whatsapp`用于WhatsApp频道插件。
- `openclaw/plugin-sdk/line`用于LINE频道插件。
- `openclaw/plugin-sdk/msteams`用于捆绑的Microsoft Teams插件表面。
- 捆绑的扩展特定子路径也可用：
  `openclaw/plugin-sdk/acpx`, `openclaw/plugin-sdk/bluebubbles`,
  `openclaw/plugin-sdk/copilot-proxy`, `openclaw/plugin-sdk/device-pair`,
  `openclaw/plugin-sdk/diagnostics-otel`, `openclaw/plugin-sdk/diffs`,
  `openclaw/plugin-sdk/feishu`,
  `openclaw/plugin-sdk/google-gemini-cli-auth`, `openclaw/plugin-sdk/googlechat`,
  `openclaw/plugin-sdk/irc`, `openclaw/plugin-sdk/llm-task`,
  `openclaw/plugin-sdk/lobster`, `openclaw/plugin-sdk/matrix`,
  `openclaw/plugin-sdk/mattermost`, `openclaw/plugin-sdk/memory-core`,
  `openclaw/plugin-sdk/memory-lancedb`,
  `openclaw/plugin-sdk/minimax-portal-auth`,
  `openclaw/plugin-sdk/nextcloud-talk`, `openclaw/plugin-sdk/nostr`,
  `openclaw/plugin-sdk/open-prose`, `openclaw/plugin-sdk/phone-control`,
  `openclaw/plugin-sdk/qwen-portal-auth`, `openclaw/plugin-sdk/synology-chat`,
  `openclaw/plugin-sdk/talk-voice`, `openclaw/plugin-sdk/test-utils`,
  `openclaw/plugin-sdk/thread-ownership`, `openclaw/plugin-sdk/tlon`,
  `openclaw/plugin-sdk/twitch`, `openclaw/plugin-sdk/voice-call`,
  `openclaw/plugin-sdk/zalo`, 和 `openclaw/plugin-sdk/zalouser`。

兼容性说明：

- `openclaw/plugin-sdk`仍支持现有外部插件。
- 新的和迁移的捆绑插件应使用频道或扩展特定子路径；对通用表面使用`core`，仅在需要更广泛的共享辅助函数时使用`compat`。

## 只读频道检查

如果您的插件注册了一个频道，建议同时实现`plugin.config.inspectAccount(cfg, accountId)`和`resolveAccount(...)`。

原因：

- `resolveAccount(...)`是运行时路径。它可以假设凭据已经完全实例化，并且在缺少必需密钥时可以快速失败。
- 只读命令路径如`openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve`和doctor/config修复流程不应为了描述配置而实例化运行时凭据。

推荐的`inspectAccount(...)`行为：

- 仅返回描述性的账户状态。
- 保留`enabled`和`configured`。
- 包括相关的凭据源/状态字段，例如：
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- 您不需要返回原始令牌值来报告只读可用性。返回`tokenStatus: "available"`（以及匹配的源字段）就足够用于状态样式命令了。
- 当凭据通过SecretRef配置但当前命令路径不可用时，使用`configured_unavailable`。

这使得只读命令能够报告“已配置但在该命令路径中不可用”，而不是崩溃或错误地报告账户未配置。

性能说明：

- 插件发现和清单元数据使用短的进程中缓存来减少突发启动/重新加载工作。
- 设置`OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1`或
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1`以禁用这些缓存。
- 使用`OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS`和
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS`调整缓存窗口。

## 发现与优先级

OpenClaw按以下顺序扫描：

1. 配置路径

- `plugins.load.paths`（文件或目录）

2. 工作区扩展

- `<workspace>/.openclaw/extensions/*.ts`
- `<workspace>/.openclaw/extensions/*/index.ts`

3. 全局扩展

- `~/.openclaw/extensions/*.ts`
- `~/.openclaw/extensions/*/index.ts`

4. 捆绑扩展（随OpenClaw一起提供，大部分默认禁用）

- `<openclaw>/extensions/*`

大多数捆绑插件必须通过`plugins.entries.<id>.enabled`或`openclaw plugins enable <id>`显式启用。

默认启用的捆绑插件例外情况：

- `device-pair`
- `phone-control`
- `talk-voice`
- 活动内存槽插件（默认槽：`memory-core`）

已安装的插件默认启用，但也可以以相同方式禁用。

加固说明：

- 如果 `plugins.allow` 为空且非捆绑插件可被发现，OpenClaw 会记录一个启动警告，其中包含插件 ID 和来源。
- 在发现之前，候选路径会进行安全检查。当以下情况发生时，OpenClaw 会阻止候选路径：
  - 扩展条目解析到插件根目录之外（包括符号链接/路径遍历逃逸），
  - 插件根目录/源路径是全局可写的，
  - 对于非捆绑插件，路径所有权可疑（POSIX 所有者既不是当前 uid 也不是 root）。
- 没有安装/加载路径来源的已加载非捆绑插件会发出警告，以便您可以固定信任 (`plugins.allow`) 或安装跟踪 (`plugins.installs`)。

每个插件必须在其根目录中包含一个 `openclaw.plugin.json` 文件。如果路径指向文件，则插件根目录为该文件的目录，并且必须包含清单。

如果有多个插件解析为相同的 ID，则以上述顺序中的第一个匹配为准，较低优先级的副本将被忽略。

### 包打包

插件目录可以包含带有 `openclaw.extensions` 的 `package.json`：

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"]
  }
}
```

每个条目成为一个插件。如果包列出了多个扩展，则插件 ID 变为 `name/<fileBase>`。

如果您的插件导入了 npm 依赖项，请在该目录中安装它们，以便 `node_modules` 可用 (`npm install` / `pnpm install`)。

安全护栏：每个 `openclaw.extensions` 条目在符号链接解析后必须留在插件目录内。逃离包目录的条目将被拒绝。

安全提示：`openclaw plugins install` 使用 `npm install --ignore-scripts` 安装插件依赖项（无生命周期脚本）。保持插件依赖树为“纯 JS/TS”，并避免需要 `postinstall` 构建的包。

### 渠道目录元数据

渠道插件可以通过 `openclaw.channel` 广告入门元数据，并通过 `openclaw.install` 提供安装提示。这使核心目录保持无数据。

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

OpenClaw 还可以合并 **外部渠道目录**（例如，MPM 注册表导出）。将 JSON 文件放置在以下位置之一：

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

或者指向 `OPENCLAW_PLUGIN_CATALOG_PATHS`（或 `OPENCLAW_MPM_CATALOG_PATHS`）的一个或多个 JSON 文件（逗号/分号/`PATH` 分隔）。每个文件应包含 `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`。

## 插件 ID

默认插件 ID：

- 包打包：`package.json` `name`
- 独立文件：文件基本名称 (`~/.../voice-call.ts` → `voice-call`)

如果插件导出 `id`，OpenClaw 会使用它，但会在其与配置的 ID 不匹配时发出警告。

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

字段：

- `enabled`：主开关（默认：true）
- `allow`：允许列表（可选）
- `deny`：拒绝列表（可选；拒绝优先）
- `load.paths`：额外的插件文件/目录
- `slots`：独占槽选择器，如 `memory` 和 `contextEngine`
- `entries.<id>`：每个插件的开关 + 配置

配置更改 **需要网关重启**。

验证规则（严格）：

- 在 `entries`、`allow`、`deny` 或 `slots` 中未知的插件 ID 是 **错误**。
- 除非插件清单声明了渠道 ID，否则未知的 `channels.<id>` 键是 **错误**。
- 使用嵌入在 `openclaw.plugin.json` 中的 JSON Schema 验证插件配置 (`configSchema`)。
- 如果禁用了插件，其配置将被保留，并发出 **警告**。

## 插件槽（独占类别）

某些插件类别是 **独占的**（一次只有一个处于活动状态）。使用 `plugins.slots` 选择哪个插件拥有该槽：

```json5
{
  plugins: {
    slots: {
      memory: "memory-core", // or "none" to disable memory plugins
      contextEngine: "legacy", // or a plugin id such as "lossless-claw"
    },
  },
}
```

支持的独占槽：

- `memory`：活动内存插件 (`"none"` 禁用内存插件)
- `contextEngine`：活动上下文引擎插件 (`"legacy"` 是内置默认值)

如果有多个插件声明 `kind: "memory"` 或 `kind: "context-engine"`，则只有选定的插件会为该槽加载。其他插件将被禁用并提供诊断信息。

### 上下文引擎插件

上下文引擎插件负责会话上下文的编排，包括摄取、组装和压缩。从您的插件注册它们使用 `api.registerContextEngine(id, factory)`，然后使用 `plugins.slots.contextEngine` 选择活动引擎。

当您的插件需要替换或扩展默认上下文管道而不是仅仅添加内存搜索或钩子时，请使用此功能。

## 控制 UI（模式 + 标签）

控制 UI 使用 `config.schema`（JSON Schema + `uiHints`）来渲染更好的表单。

OpenClaw 根据发现的插件在运行时增强 `uiHints`：

- 为 `plugins.entries.<id>` / `.enabled` / `.config` 添加每个插件的标签
- 合并在以下位置提供的可选插件配置字段提示：
  `plugins.entries.<id>.config.<field>`

如果您希望插件配置字段显示良好的标签/占位符（并将秘密标记为敏感），请在插件清单中提供 `uiHints` 以及 JSON Schema。

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

## CLI

```bash
openclaw plugins list
openclaw plugins info <id>
openclaw plugins install <path>                 # copy a local file/dir into ~/.openclaw/extensions/<id>
openclaw plugins install ./extensions/voice-call # relative path ok
openclaw plugins install ./plugin.tgz           # install from a local tarball
openclaw plugins install ./plugin.zip           # install from a local zip
openclaw plugins install -l ./extensions/voice-call # link (no copy) for dev
openclaw plugins install @openclaw/voice-call # install from npm
openclaw plugins install @openclaw/voice-call --pin # store exact resolved name@version
openclaw plugins update <id>
openclaw plugins update --all
openclaw plugins enable <id>
openclaw plugins disable <id>
openclaw plugins doctor
```

`plugins update` 仅适用于在 `plugins.installs` 下跟踪的 npm 安装。如果存储的完整性元数据在更新之间发生变化，OpenClaw 会发出警告并要求确认（使用全局 `--yes` 跳过提示）。

插件还可以注册自己的顶级命令（例如：`openclaw voicecall`）。

## 插件 API（概述）

插件导出以下之一：

- 函数：`(api) => { ... }`
- 对象：`{ id, name, configSchema, register(api) { ... } }`

上下文引擎插件还可以注册运行时拥有的上下文管理器：

```ts
export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages }) {
      return { messages, estimatedTokens: 0 };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

然后在配置中启用它：

```json5
{
  plugins: {
    slots: {
      contextEngine: "lossless-claw",
    },
  },
}
```

## 插件钩子

插件可以在运行时注册钩子。这允许插件捆绑事件驱动的自动化，而无需单独的钩子包安装。

### 示例

```ts
export default function register(api) {
  api.registerHook(
    "command:new",
    async () => {
      // Hook logic here.
    },
    {
      name: "my-plugin.command-new",
      description: "Runs when /new is invoked",
    },
  );
}
```

注意事项：

- 通过 `api.registerHook(...)` 显式注册钩子。
- 钩子资格规则仍然适用（OS/二进制文件/环境/配置要求）。
- 由插件管理的钩子在 `openclaw hooks list` 中显示为 `plugin:<id>`。
- 您不能通过 `openclaw hooks` 启用/禁用由插件管理的钩子；而是启用/禁用插件本身。

### 代理生命周期钩子 (`api.on`)

对于类型化的运行时生命周期钩子，使用 `api.on(...)`：

```ts
export default function register(api) {
  api.on(
    "before_prompt_build",
    (event, ctx) => {
      return {
        prependSystemContext: "Follow company style guide.",
      };
    },
    { priority: 10 },
  );
}
```

重要的提示构建钩子：

- `before_model_resolve`：在会话加载前运行（`messages` 不可用）。使用此钩子确定性地覆盖 `modelOverride` 或 `providerOverride`。
- `before_prompt_build`：在会话加载后运行（`messages` 可用）。使用此钩子塑造提示输入。
- `before_agent_start`：遗留兼容性钩子。优先使用上述两个显式钩子。

核心强制执行的钩子策略：

- 操作员可以通过 `plugins.entries.<id>.hooks.allowPromptInjection: false` 按插件禁用提示变异钩子。
- 当禁用时，OpenClaw 阻止 `before_prompt_build` 并忽略从遗留 `before_agent_start` 返回的提示变异字段，同时保留遗留 `modelOverride` 和 `providerOverride`。

`before_prompt_build` 结果字段：

- `prependContext`: 在本次运行的用户提示前添加文本。最适合特定回合或动态内容。
- `systemPrompt`: 完全覆盖系统提示。
- `prependSystemContext`: 在当前系统提示前添加文本。
- `appendSystemContext`: 在当前系统提示后添加文本。

嵌入式运行时中的提示构建顺序：

1. 将`prependContext`应用于用户提示。
2. 提供时应用`systemPrompt`覆盖。
3. 应用`prependSystemContext + current system prompt + appendSystemContext`。

合并和优先级说明：

- 钩子处理程序按优先级（较高者优先）运行。
- 对于合并的上下文字段，值按执行顺序连接。
- `before_prompt_build`值在旧版`before_agent_start`回退值之前应用。

迁移指南：

- 将静态指南从`prependContext`移动到`prependSystemContext`（或`appendSystemContext`），以便提供者可以缓存稳定的系统前缀内容。
- 保留`prependContext`用于应与用户消息绑定的每回合动态上下文。

## 提供者插件（模型认证）

插件可以注册**模型提供者认证**流程，以便用户可以在OpenClaw内运行OAuth或API密钥设置（无需外部脚本）。

通过`api.registerProvider(...)`注册提供者。每个提供者公开一个或多个认证方法（OAuth、API密钥、设备代码等）。这些方法支持：

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

- `run`接收带有`prompter`、`runtime`、`openUrl`和`oauth.createVpsAwareHandlers`辅助函数的`ProviderAuthContext`。
- 当需要添加默认模型或提供者配置时，返回`configPatch`。
- 返回`defaultModel`以便`--set-default`可以更新代理默认值。

### 注册消息通道

插件可以注册行为类似于内置通道（如WhatsApp、Telegram等）的**通道插件**。通道配置位于`channels.<id>`下，并由您的通道插件代码验证。

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

- 将配置放在`channels.<id>`下（而不是`plugins.entries`）。
- `meta.label`用于CLI/UI列表中的标签。
- `meta.aliases`为规范化和CLI输入添加备用ID。
- `meta.preferOver`列出当两者都配置时跳过自动启用的通道ID。
- `meta.detailLabel`和`meta.systemImage`允许UI显示更丰富的通道标签/图标。

### 通道引导钩子

通道插件可以在`plugin.onboarding`上定义可选的引导钩子：

- `configure(ctx)`是基准设置流程。
- `configureInteractive(ctx)`可以完全拥有已配置和未配置状态的交互式设置。
- `configureWhenConfigured(ctx)`仅对已配置的通道覆盖行为。

向导中的钩子优先级：

1. `configureInteractive`（如果存在）
2. `configureWhenConfigured`（仅当通道状态已配置时）
3. 回退到`configure`

上下文详情：

- `configureInteractive`和`configureWhenConfigured`接收：
  - `configured`（`true`或`false`）
  - `label`（提示中使用的面向用户的通道名称）
  - 加上共享的配置/运行时/提示器/选项字段
- 返回`"skip"`保持选择和账户跟踪不变。
- 返回`{ cfg, accountId? }`应用配置更新并记录账户选择。

### 编写新的消息通道（逐步指南）

当您想要一个新的聊天界面（“消息通道”）而不是模型提供者时，请使用此方法。模型提供者的文档位于`/providers/*`下。

1. 选择ID + 配置形状

- 所有通道配置都位于`channels.<id>`下。
- 对于多账户设置，首选`channels.<id>.accounts.<accountId>`。

2. 定义通道元数据

- `meta.label`、`meta.selectionLabel`、`meta.docsPath`、`meta.blurb`控制CLI/UI列表。
- `meta.docsPath`应指向类似`/channels/<id>`的文档页面。
- `meta.preferOver`允许插件替换另一个通道（自动启用优先选择它）。
- `meta.detailLabel`和`meta.systemImage`被UI用于详细文本/图标。

3. 实现所需的适配器

- `config.listAccountIds` + `config.resolveAccount`
- `capabilities`（聊天类型、媒体、线程等）
- `outbound.deliveryMode` + `outbound.sendText`（基本发送）

4. 根据需要添加可选适配器

- `setup`（向导）、`security`（DM策略）、`status`（健康/诊断）
- `gateway`（启动/停止/登录）、`mentions`、`threading`、`streaming`
- `actions`（消息操作）、`commands`（原生命令行为）

5. 在插件中注册通道

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

最小通道插件（仅出站）：

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

加载插件（扩展目录或`plugins.load.paths`），重启网关，然后在配置中设置`channels.<id>`。

### 代理工具

请参阅专用指南：[插件代理工具](/plugins/agent-tools)。

### 注册网关RPC方法

```ts
export default function (api) {
  api.registerGatewayMethod("myplugin.status", ({ respond }) => {
    respond(true, { ok: true });
  });
}
```

### 注册CLI命令

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

插件可以注册自定义斜杠命令，这些命令在**不调用AI代理**的情况下执行。这对于切换命令、状态检查或不需要LLM处理的快速操作非常有用。

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

- `senderId`：发送者的ID（如果可用）
- `channel`：发送命令的通道
- `isAuthorizedSender`：发送者是否为授权用户
- `args`：命令后的参数（如果`acceptsArgs: true`）
- `commandBody`：完整的命令文本
- `config`：当前的OpenClaw配置

命令选项：

- `name`：命令名称（不带前导`/`）
- `nativeNames`：可选的原生命令别名，用于斜杠/菜单界面。使用`default`适用于所有原生提供者，或使用像`discord`这样的特定提供者键
- `description`：命令列表中显示的帮助文本
- `acceptsArgs`：命令是否接受参数（默认：false）。如果为false且提供了参数，则命令不会匹配，消息将传递给其他处理程序
- `requireAuth`：是否要求授权的发送者（默认：true）
- `handler`：返回`{ text: string }`的函数（可以是异步的）

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

注意事项：

- 插件命令在内置命令和AI代理**之前**处理
- 命令全局注册并在所有通道中工作
- 命令名称不区分大小写（`/MyStatus`匹配`/mystatus`）
- 命令名称必须以字母开头，只能包含字母、数字、连字符和下划线
- 保留的命令名称（如`help`、`status`、`reset`等）不能被插件覆盖
- 跨插件重复注册命令将导致诊断错误

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

- 网关方法: `pluginId.action`（示例：`voicecall.status`）
- 工具: `snake_case`（示例：`voice_call`）
- CLI 命令: kebab 或 camel，但避免与核心命令冲突

## 技能

插件可以在仓库中包含一个技能 (`skills/<name>/SKILL.md`)。
使用 `plugins.entries.<id>.enabled`（或其他配置门）启用它，并确保
它存在于你的工作区/管理的技能位置。

## 分发 (npm)

推荐的打包方式：

- 主包: `openclaw`（此仓库）
- 插件: 在 `@openclaw/*` 下的单独 npm 包（示例：`@openclaw/voice-call`）

发布合约：

- 插件 `package.json` 必须包含带有一个或多个入口文件的 `openclaw.extensions`。
- 入口文件可以是 `.js` 或 `.ts`（jiti 在运行时加载 TS）。
- `openclaw plugins install <npm-spec>` 使用 `npm pack`，提取到 `~/.openclaw/extensions/<id>/` 并在配置中启用它。
- 配置键稳定性：作用域包被规范化为 **无作用域** ID 用于 `plugins.entries.*`。

## 示例插件：语音通话

此仓库包括一个语音通话插件（Twilio 或日志回退）：

- 源代码: `extensions/voice-call`
- 技能: `skills/voice-call`
- CLI: `openclaw voicecall start|status`
- 工具: `voice_call`
- RPC: `voicecall.start`, `voicecall.status`
- 配置 (twilio): `provider: "twilio"` + `twilio.accountSid/authToken/from`（可选 `statusCallbackUrl`, `twimlUrl`）
- 配置 (dev): `provider: "log"`（无网络）

请参阅 [语音通话](/plugins/voice-call) 和 `extensions/voice-call/README.md` 以获取设置和使用说明。

## 安全注意事项

插件与网关在同一进程中运行。将它们视为可信代码：

- 仅安装你信任的插件。
- 优先使用 `plugins.allow` 允许列表。
- 更改后重启网关。

## 测试插件

插件可以（并且应该）附带测试：

- 仓库中的插件可以将 Vitest 测试保留在 `src/**` 下（示例：`src/plugins/voice-call.plugin.test.ts`）。
- 单独发布的插件应运行自己的 CI（lint/build/test）并验证 `openclaw.extensions` 指向构建的入口点 (`dist/index.js`)。