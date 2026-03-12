---
summary: "Configuration overview: common tasks, quick setup, and links to the full reference"
read_when:
  - Setting up OpenClaw for the first time
  - Looking for common configuration patterns
  - Navigating to specific config sections
title: "Configuration"
---
# 配置

OpenClaw 会从 `~/.openclaw/openclaw.json` 中读取一个可选的 <Tooltip tip="JSON5 支持注释和末尾逗号">**JSON5**</Tooltip> 配置文件。

如果该文件缺失，OpenClaw 将使用安全的默认配置。常见需要添加配置的原因包括：

- 连接通道并控制谁可以向机器人发送消息  
- 设置模型、工具、沙箱环境或自动化任务（如 cron、钩子）  
- 调优会话、媒体、网络或用户界面  

有关所有可用字段，请参阅[完整参考文档](/gateway/configuration-reference)。

<Tip>
**New to configuration?** Start with __CODE_BLOCK_1__ for interactive setup, or check out the [Configuration Examples](/gateway/configuration-examples) guide for complete copy-paste configs.
</Tip>

## 最小化配置

```json5
// ~/.openclaw/openclaw.json
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
  channels: { whatsapp: { allowFrom: ["+15555550123"] } },
}
```

## 编辑配置

<Tabs>
  <Tab title="Interactive wizard">
    __CODE_BLOCK_3__
  </Tab>
  <Tab title="CLI (one-liners)">
    __CODE_BLOCK_4__
  </Tab>
  <Tab title="Control UI">
    Open [http://127.0.0.1:18789](http://127.0.0.1:18789) and use the **Config** tab.
    The Control UI renders a form from the config schema, with a **Raw JSON** editor as an escape hatch.
  </Tab>
  <Tab title="Direct edit">
    Edit __CODE_BLOCK_5__ directly. The Gateway watches the file and applies changes automatically (see [hot reload](#config-hot-reload)).
  </Tab>
</Tabs>

## 严格校验

<Warning>
OpenClaw only accepts configurations that fully match the schema. Unknown keys, malformed types, or invalid values cause the Gateway to **refuse to start**. The only root-level exception is __CODE_BLOCK_6__ (string), so editors can attach JSON Schema metadata.
</Warning>

当校验失败时：

- 网关将无法启动  
- 仅诊断命令可用（`openclaw doctor`、`openclaw logs`、`openclaw health`、`openclaw status`）  
- 运行 `openclaw doctor` 可查看具体错误信息  
- 运行 `openclaw doctor --fix`（或 `--yes`）可自动修复问题  

## 常见任务

<AccordionGroup>
  <Accordion title="配置通道（WhatsApp、Telegram、Discord 等）">
    每个通道在 `channels.<provider>` 下都有其独立的配置节。请参阅对应通道的专属页面以了解配置步骤：

    - [WhatsApp](/channels/whatsapp) — `channels.whatsapp`  
    - [Telegram](/channels/telegram) — `channels.telegram`  
    - [Discord](/channels/discord) — `channels.discord`  
    - [Slack](/channels/slack) — `channels.slack`  
    - [Signal](/channels/signal) — `channels.signal`  
    - [iMessage](/channels/imessage) — `channels.imessage`  
    - [Google Chat](/channels/googlechat) — `channels.googlechat`  
    - [Mattermost](/channels/mattermost) — `channels.mattermost`  
    - [MS Teams](/channels/msteams) — `channels.msteams`  

    所有通道均采用相同的私信（DM）访问策略模式：

    ```json5
    {
      channels: {
        telegram: {
          enabled: true,
          botToken: "123:abc",
          dmPolicy: "pairing",   // pairing | allowlist | open | disabled
          allowFrom: ["tg:123"], // only for allowlist/open
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="选择并配置模型">
    设置主模型及可选的备用模型：

    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "anthropic/claude-sonnet-4-5",
            fallbacks: ["openai/gpt-5.2"],
          },
          models: {
            "anthropic/claude-sonnet-4-5": { alias: "Sonnet" },
            "openai/gpt-5.2": { alias: "GPT" },
          },
        },
      },
    }
    ```

    - `agents.defaults.models` 定义模型目录，并作为 `/model` 的白名单。  
    - 模型引用采用 `provider/model` 格式（例如：`anthropic/claude-opus-4-6`）。  
    - `agents.defaults.imageMaxDimensionPx` 控制对话记录/工具图像的缩放比例（默认为 `1200`）；较低值通常可在截图密集型运行中减少视觉 token 的消耗。  
    - 有关在聊天中切换模型，请参阅 [模型 CLI](/concepts/models)；有关认证轮换与备用行为，请参阅 [模型故障转移](/concepts/model-failover)。  
    - 对于自定义/自托管提供商，请参阅参考文档中的 [自定义提供商](/gateway/configuration-reference#custom-providers-and-base-urls)。

  </Accordion>

  <Accordion title="控制谁可以向机器人发送消息">
    私信（DM）访问权限按通道通过 `dmPolicy` 控制：

    - `"pairing"`（默认）：未知发件人将收到一次性配对码以完成授权  
    - `"allowlist"`：仅允许出现在 `allowFrom`（或已配对的白名单存储）中的发件人  
    - `"open"`：允许所有入站私信（需启用 `allowFrom: ["*"]`）  
    - `"disabled"`：忽略所有私信  

    对于群组，请结合使用 `groupPolicy` + `groupAllowFrom` 或通道专属白名单。

    有关各通道详细说明，请参阅 [完整参考文档](/gateway/configuration-reference#dm-and-group-access)。

  </Accordion>

  <Accordion title="配置群组聊天提及门控（mention gating）">
    群组消息默认 **要求提及**。可按智能体分别配置匹配模式：

    ```json5
    {
      agents: {
        list: [
          {
            id: "main",
            groupChat: {
              mentionPatterns: ["@openclaw", "openclaw"],
            },
          },
        ],
      },
      channels: {
        whatsapp: {
          groups: { "*": { requireMention: true } },
        },
      },
    }
    ```

    - **元数据提及**：原生 @ 提及（如 WhatsApp 的点击提及、Telegram 的 @bot 等）  
    - **文本模式**：在 `mentionPatterns` 中定义的正则表达式模式  
    - 有关通道级覆盖和自聊模式，请参阅 [完整参考文档](/gateway/configuration-reference#group-chat-mention-gating)。

  </Accordion>

  <Accordion title="配置会话与重置">
    会话用于控制对话连续性与隔离性：

    ```json5
    {
      session: {
        dmScope: "per-channel-peer",  // recommended for multi-user
        threadBindings: {
          enabled: true,
          idleHours: 24,
          maxAgeHours: 0,
        },
        reset: {
          mode: "daily",
          atHour: 4,
          idleMinutes: 120,
        },
      },
    }
    ```

    - `dmScope`：`main`（共享）｜`per-peer`｜`per-channel-peer`｜`per-account-channel-peer`  
    - `threadBindings`：线程绑定会话路由的全局默认值（Discord 支持 `/focus`、`/unfocus`、`/agents`、`/session idle` 和 `/session max-age`）。  
    - 有关作用域、身份关联与发送策略，请参阅 [会话管理](/concepts/session)。  
    - 有关全部字段，请参阅 [完整参考文档](/gateway/configuration-reference#session)。

  </Accordion>

  <Accordion title="启用沙箱环境">
    在隔离的 Docker 容器中运行智能体会话：

    ```json5
    {
      agents: {
        defaults: {
          sandbox: {
            mode: "non-main",  // off | non-main | all
            scope: "agent",    // session | agent | shared
          },
        },
      },
    }
    ```

    首先构建镜像：`scripts/sandbox-setup.sh`

    请参阅 [沙箱环境](/gateway/sandboxing) 获取完整指南，并查阅 [完整参考文档](/gateway/configuration-reference#sandbox) 了解全部选项。

  </Accordion>

  <Accordion title="配置心跳机制（周期性签到）">
    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "30m",
            target: "last",
          },
        },
      },
    }
    ```

    - `every`：持续时间字符串（如 `30m`、`2h`）。设为 `0m` 可禁用心跳。  
    - `target`：`last`｜`whatsapp`｜`telegram`｜`discord`｜`none`  
    - `directPolicy`：`allow`（默认）或 `block`（适用于私信风格的心跳目标）  
    - 请参阅 [心跳机制](/gateway/heartbeat) 获取完整指南。

  </Accordion>

  <Accordion title="配置定时任务（cron jobs）">
    ```json5
    {
      cron: {
        enabled: true,
        maxConcurrentRuns: 2,
        sessionRetention: "24h",
        runLog: {
          maxBytes: "2mb",
          keepLines: 2000,
        },
      },
    }
    ```

    - `sessionRetention`：从 `sessions.json` 中清理已完成的独立运行会话（默认为 `24h`；设为 `false` 可禁用）。  
    - `runLog`：按大小与保留行数清理 `cron/runs/<jobId>.jsonl`。  
    - 请参阅 [定时任务](/automation/cron-jobs) 了解功能概览与 CLI 示例。

  </Accordion>

  <Accordion title="配置 Webhook（钩子）">
    在网关上启用 HTTP webhook 端点：

    ```json5
    {
      hooks: {
        enabled: true,
        token: "shared-secret",
        path: "/hooks",
        defaultSessionKey: "hook:ingress",
        allowRequestSessionKey: false,
        allowedSessionKeyPrefixes: ["hook:"],
        mappings: [
          {
            match: { path: "gmail" },
            action: "agent",
            agentId: "main",
            deliver: true,
          },
        ],
      },
    }
    ```

    安全提示：
    - 请将所有钩子/webhook 负载内容视为不可信输入。  
    - 除非进行范围极窄的调试，否则请保持不安全内容绕过标志禁用状态（`hooks.gmail.allowUnsafeExternalContent`、`hooks.mappings[].allowUnsafeExternalContent`）。  
    - 对于由钩子驱动的智能体，建议优先选用强健的现代模型层级，并实施严格的工具策略（例如仅限消息收发，且尽可能启用沙箱）。

    有关全部映射选项与 Gmail 集成，请参阅 [完整参考文档](/gateway/configuration-reference#hooks)。

  </Accordion>

  <Accordion title="配置多智能体路由">
    运行多个相互隔离的智能体，各自拥有独立的工作区与会话：

```json5
    {
      agents: {
        list: [
          { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
          { id: "work", workspace: "~/.openclaw/workspace-work" },
        ],
      },
      bindings: [
        { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
        { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
      ],
    }
    ```

    有关绑定规则及每个 Agent 的访问配置文件，请参阅 [多 Agent](/concepts/multi-agent) 和 [完整参考文档](/gateway/configuration-reference#multi-agent-routing)。

  </Accordion>

  <Accordion title="将配置拆分为多个文件（$include）">
    使用 `$include` 来组织大型配置：

    ```json5
    // ~/.openclaw/openclaw.json
    {
      gateway: { port: 18789 },
      agents: { $include: "./agents.json5" },
      broadcast: {
        $include: ["./clients/a.json5", "./clients/b.json5"],
      },
    }
    ```

    - **单个文件**：替换所包含的对象  
    - **文件数组**：按顺序深度合并（后出现的值优先）  
    - **同级键（Sibling keys）**：在 include 后合并（覆盖已引入的值）  
    - **嵌套 include**：最多支持 10 层嵌套  
    - **相对路径**：相对于当前引入该配置的文件进行解析  
    - **错误处理**：对缺失文件、解析错误和循环引用提供清晰的错误提示  

  </Accordion>
</AccordionGroup>

## 配置热重载

网关会监听 `~/.openclaw/openclaw.json` 并自动应用变更——大多数设置无需手动重启。

### 重载模式

| 模式                   | 行为                                                                                     |
| ---------------------- | ---------------------------------------------------------------------------------------- |
| **`hybrid`**（默认） | 立即热应用安全变更；对关键变更自动执行重启。                                              |
| **`hot`**              | 仅热应用安全变更；当需要重启时记录警告日志——由您手动处理。                                   |
| **`restart`**          | 对任意配置变更（无论是否安全）均重启网关。                                                  |
| **`off`**              | 禁用文件监听。变更将在下一次手动重启时生效。                                                 |

```json5
{
  gateway: {
    reload: { mode: "hybrid", debounceMs: 300 },
  },
}
```

### 哪些可热应用，哪些需重启

大多数字段均可热更新且不中断服务。在 `hybrid` 模式下，需重启的变更将被自动处理。

| 类别            | 字段                                                               | 是否需要重启？ |
| ------------------- | -------------------------------------------------------------------- | --------------- |
| 通道（Channels）            | `channels.*`、`web`（WhatsApp）——所有内置及扩展通道 | 否              |
| Agent 与模型      | `agent`、`agents`、`models`、`routing`                               | 否              |
| 自动化（Automation）          | `hooks`、`cron`、`agent.heartbeat`                                   | 否              |
| 会话与消息（Sessions & messages） | `session`、`messages`                                                | 否              |
| 工具与媒体（Tools & media）       | `tools`、`browser`、`skills`、`audio`、`talk`                        | 否              |
| UI 与杂项（UI & misc）           | `ui`、`logging`、`identity`、`bindings`                              | 否              |
| 网关服务器（Gateway server）      | `gateway.*`（端口、绑定地址、认证、Tailscale、TLS、HTTP）                 | **是**         |
| 基础设施（Infrastructure）      | `discovery`、`canvasHost`、`plugins`                                 | **是**         |

<Note>
__CODE_BLOCK_34__ and __CODE_BLOCK_35__ are exceptions — changing them does **not** trigger a restart.
</Note>

## 配置 RPC（程序化更新）

<Note>
Control-plane write RPCs (__CODE_BLOCK_36__, __CODE_BLOCK_37__, __CODE_BLOCK_38__) are rate-limited to **3 requests per 60 seconds** per __CODE_BLOCK_39__. When limited, the RPC returns __CODE_BLOCK_40__ with __CODE_BLOCK_41__.
</Note>

<AccordionGroup>
  <Accordion title="config.apply (full replace)">
    Validates + writes the full config and restarts the Gateway in one step.

    <Warning>
    __CODE_BLOCK_42__ replaces the **entire config**. Use __CODE_BLOCK_43__ for partial updates, or __CODE_BLOCK_44__ for single keys.
    </Warning>

    Params:

    - __CODE_BLOCK_45__ (string) — JSON5 payload for the entire config
    - __CODE_BLOCK_46__ (optional) — config hash from __CODE_BLOCK_47__ (required when config exists)
    - __CODE_BLOCK_48__ (optional) — session key for the post-restart wake-up ping
    - __CODE_BLOCK_49__ (optional) — note for the restart sentinel
    - __CODE_BLOCK_50__ (optional) — delay before restart (default 2000)

    Restart requests are coalesced while one is already pending/in-flight, and a 30-second cooldown applies between restart cycles.

    __CODE_BLOCK_51__

  </Accordion>

  <Accordion title="config.patch (partial update)">
    Merges a partial update into the existing config (JSON merge patch semantics):

    - Objects merge recursively
    - __CODE_BLOCK_52__ deletes a key
    - Arrays replace

    Params:

    - __CODE_BLOCK_53__ (string) — JSON5 with just the keys to change
    - __CODE_BLOCK_54__ (required) — config hash from __CODE_BLOCK_55__
    - __CODE_BLOCK_56__, __CODE_BLOCK_57__, __CODE_BLOCK_58__ — same as __CODE_BLOCK_59__

    Restart behavior matches __CODE_BLOCK_60__: coalesced pending restarts plus a 30-second cooldown between restart cycles.

    __CODE_BLOCK_61__

  </Accordion>
</AccordionGroup>

## 环境变量

OpenClaw 从父进程读取环境变量，并额外加载：

- 当前工作目录下的 `.env`（如存在）  
- 全局回退文件 `~/.openclaw/.env`  

这两个文件均不会覆盖已存在的环境变量。您也可以在配置中内联设置环境变量：

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: { GROQ_API_KEY: "gsk-..." },
  },
}
```

<Accordion title="Shell 环境变量导入（可选）">
  若启用此功能，且预期的环境变量未设置，OpenClaw 将运行您的登录 Shell，并仅导入缺失的变量：

```json5
{
  env: {
    shellEnv: { enabled: true, timeoutMs: 15000 },
  },
}
```

对应环境变量：`OPENCLAW_LOAD_SHELL_ENV=1`
</Accordion>

<Accordion title="配置值中的环境变量替换">
  在任意配置字符串值中，可通过 `${VAR_NAME}` 引用环境变量：

```json5
{
  gateway: { auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" } },
  models: { providers: { custom: { apiKey: "${CUSTOM_API_KEY}" } } },
}
```

规则如下：

- 仅匹配全大写名称：`[A-Z_][A-Z0-9_]*`  
- 缺失或为空的变量将在加载时抛出错误  
- 使用 `$${VAR}` 进行转义以输出字面量  
- 支持在 `$include` 文件内部使用  
- 内联替换示例：`"${BASE}/v1"` → `"https://api.example.com/v1"`  

</Accordion>

<Accordion title="密钥引用（env、file、exec）">
  对于支持 SecretRef 对象的字段，您可以使用：

```json5
{
  models: {
    providers: {
      openai: { apiKey: { source: "env", provider: "default", id: "OPENAI_API_KEY" } },
    },
  },
  skills: {
    entries: {
      "nano-banana-pro": {
        apiKey: {
          source: "file",
          provider: "filemain",
          id: "/skills/entries/nano-banana-pro/apiKey",
        },
      },
    },
  },
  channels: {
    googlechat: {
      serviceAccountRef: {
        source: "exec",
        provider: "vault",
        id: "channels/googlechat/serviceAccount",
      },
    },
  },
}
```

SecretRef 的详细说明（包括针对 `secrets.providers` 的 `env`/`file`/`exec`）请参阅 [密钥管理](/gateway/secrets)。  
支持的凭据路径列表见 [SecretRef 凭据接口](/reference/secretref-credential-surface)。
</Accordion>

有关完整优先级顺序与来源，请参阅 [环境](/help/environment)。

## 完整参考

如需完整的逐字段参考文档，请查阅 **[配置参考](/gateway/configuration-reference)**。

---

_相关文档：[配置示例](/gateway/configuration-examples) · [配置参考](/gateway/configuration-reference) · [Doctor](/gateway/doctor)_