---
summary: "Configuration overview: common tasks, quick setup, and links to the full reference"
read_when:
  - Setting up OpenClaw for the first time
  - Looking for common configuration patterns
  - Navigating to specific config sections
title: "Configuration"
---
# 配置

OpenClaw 从 `~/.openclaw/openclaw.json` 读取可选的 <Tooltip tip="JSON5 支持注释和尾随逗号">**JSON5**</Tooltip> 配置。

如果文件缺失，OpenClaw 会使用安全的默认值。添加配置的常见原因：

- 连接渠道并控制谁可以向机器人发送消息
- 设置模型、工具、沙箱或自动化（cron、hooks）
- 调整会话、媒体、网络或 UI

请参阅 [完整参考](/gateway/configuration-reference) 了解所有可用字段。

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

## 严格验证

<Warning>
OpenClaw only accepts configurations that fully match the schema. Unknown keys, malformed types, or invalid values cause the Gateway to **refuse to start**. The only root-level exception is __CODE_BLOCK_6__ (string), so editors can attach JSON Schema metadata.
</Warning>

当验证失败时：

- Gateway 无法启动
- 仅诊断命令可用（`openclaw doctor`、`openclaw logs`、`openclaw health`、`openclaw status`）
- 运行 `openclaw doctor` 查看具体问题
- 运行 `openclaw doctor --fix`（或 `--yes`）应用修复

## 常见任务

<AccordionGroup>
  <Accordion title="设置渠道（WhatsApp、Telegram、Discord 等）">
    每个渠道在 `channels.<provider>` 下都有自己的配置部分。请参阅专用渠道页面了解设置步骤：

    - [WhatsApp](/channels/whatsapp) — `channels.whatsapp`
    - [Telegram](/channels/telegram) — `channels.telegram`
    - [Discord](/channels/discord) — `channels.discord`
    - [Slack](/channels/slack) — `channels.slack`
    - [Signal](/channels/signal) — `channels.signal`
    - [iMessage](/channels/imessage) — `channels.imessage`
    - [Google Chat](/channels/googlechat) — `channels.googlechat`
    - [Mattermost](/channels/mattermost) — `channels.mattermost`
    - [MS Teams](/channels/msteams) — `channels.msteams`

    所有渠道共享相同的 DM 策略模式：

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

  <Accordion title="选择和配置模型">
    设置主模型和可选备用模型：

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

    - `agents.defaults.models` 定义模型目录并充当 `/model` 的允许列表。
    - 模型引用使用 `provider/model` 格式（例如 `anthropic/claude-opus-4-6`）。
    - `agents.defaults.imageMaxDimensionPx` 控制转录/工具图像降采样（默认 `1200`）；较低的值通常在截图较多的运行中减少 vision-token 使用。
    - 请参阅 [模型 CLI](/concepts/models) 了解在聊天中切换模型，以及 [模型故障转移](/concepts/model-failover) 了解 auth rotation 和 fallback 行为。
    - 对于自定义/自托管提供商，请参阅参考中的 [自定义提供商](/gateway/configuration-reference#custom-providers-and-base-urls)。

  </Accordion>

  <Accordion title="控制谁可以向机器人发送消息">
    DM 访问权限通过 `dmPolicy` 按渠道控制：

    - `"pairing"`（默认）：未知发送者获得一次性配对代码以批准
    - `"allowlist"`：仅 `allowFrom` 中的发送者（或配对的允许存储）
    - `"open"`：允许所有入站 DM（需要 `allowFrom: ["*"]`）
    - `"disabled"`：忽略所有 DM

    对于群组，使用 `groupPolicy` + `groupAllowFrom` 或特定渠道的允许列表。

    请参阅 [完整参考](/gateway/configuration-reference#dm-and-group-access) 了解每个渠道的详细信息。

  </Accordion>

  <Accordion title="设置群聊提及门禁">
    群消息默认为 **需要提及**。按代理配置模式：

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

    - **Metadata mentions**：原生 @-mentions（WhatsApp tap-to-mention、Telegram @bot 等）
    - **Text patterns**：`mentionPatterns` 中的 regex 模式
    - 请参阅 [完整参考](/gateway/configuration-reference#group-chat-mention-gating) 了解每个渠道的覆盖和 self-chat 模式。

  </Accordion>

  <Accordion title="配置会话和重置">
    会话控制对话连续性和隔离性：

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

    - `dmScope`：`main`（共享）| `per-peer` | `per-channel-peer` | `per-account-channel-peer`
    - `threadBindings`：thread-bound 会话路由的全局默认值（Discord 支持 `/focus`、`/unfocus`、`/agents`、`/session idle` 和 `/session max-age`）。
    - 请参阅 [会话管理](/concepts/session) 了解 scoping、identity links 和 send policy。
    - 请参阅 [完整参考](/gateway/configuration-reference#session) 了解所有字段。

  </Accordion>

  <Accordion title="启用沙箱">
    在隔离的 Docker 容器中运行代理会话：

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

    请参阅 [沙箱](/gateway/sandboxing) 获取完整指南，以及 [完整参考](/gateway/configuration-reference#sandbox) 了解所有选项。

  </Accordion>

  <Accordion title="设置 heartbeat（定期检查）">
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

    - `every`：duration 字符串（`30m`、`2h`）。设置 `0m` 以禁用。
    - `target`：`last` | `whatsapp` | `telegram` | `discord` | `none`
    - `directPolicy`：`allow`（默认）或 `block` 用于 DM 风格的 heartbeat 目标
    - 请参阅 [Heartbeat](/gateway/heartbeat) 获取完整指南。

  </Accordion>

  <Accordion title="配置 cron jobs">
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

    - `sessionRetention`：从 `sessions.json` 修剪已完成的 isolated run 会话（默认 `24h`；设置 `false` 以禁用）。
    - `runLog`：按大小和保留行数修剪 `cron/runs/<jobId>.jsonl`。
    - 请参阅 [Cron jobs](/automation/cron-jobs) 了解功能概述和 CLI 示例。

  </Accordion>

  <Accordion title="设置 webhooks（hooks）">
    在 Gateway 上启用 HTTP webhook 端点：

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

    安全说明：
    - 将所有 hook/webhook payload 内容视为不可信输入。
    - 保持 unsafe-content bypass 标志禁用（`hooks.gmail.allowUnsafeExternalContent`、`hooks.mappings[].allowUnsafeExternalContent`），除非进行严格范围的调试。
    - 对于 hook-driven 代理，首选强大的现代 model tiers 和严格的 tool policy（例如仅限 messaging 加上沙箱，如果可能）。

    请参阅 [完整参考](/gateway/configuration-reference#hooks) 了解所有映射选项和 Gmail 集成。

  </Accordion>

  <Accordion title="配置多代理路由">
    运行多个具有独立工作区和会话的隔离代理：

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

    请参阅 [Multi-Agent](/concepts/multi-agent) 和 [完整参考](/gateway/configuration-reference#multi-agent-routing) 以了解绑定规则和每个代理的访问配置文件。

  </Accordion>

  <Accordion title="将配置拆分为多个文件 ($include)">
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

    - **单个文件**：替换包含的对象
    - **文件数组**：按顺序深度合并（后者胜出）
    - **同级键**：在 include 之后合并（覆盖包含的值）
    - **嵌套 include**：支持最深 10 层
    - **相对路径**：相对于包含文件解析
    - **错误处理**：针对缺失文件、解析错误和循环 include 提供清晰的错误信息

  </Accordion>
</AccordionGroup>

## 配置热重载

Gateway 监视 `~/.openclaw/openclaw.json` 并自动应用更改 — 大多数设置无需手动重启。

### 重载模式

| 模式                   | 行为                                                                                |
| ---------------------- | --------------------------------------------------------------------------------------- |
| **`hybrid`**（默认） | 即时热应用安全更改。自动重启关键更改。           |
| **`hot`**              | 仅热应用安全更改。当需要重启时记录警告 — 由您处理。 |
| **`restart`**          | 任何配置更改（无论是否安全）都重启 Gateway。                                 |
| **`off`**              | 禁用文件监视。更改在下次手动重启时生效。                 |

```json5
{
  gateway: {
    reload: { mode: "hybrid", debounceMs: 300 },
  },
}
```

### 哪些可热应用 vs 哪些需要重启

大多数字段可热应用而无需停机。在 `hybrid` 模式下，需要重启的更改会自动处理。

| 类别            | 字段                                                               | 需要重启？ |
| ------------------- | -------------------------------------------------------------------- | --------------- |
| 渠道            | `channels.*`, `web` (WhatsApp) — 所有内置和扩展渠道 | 否              |
| 代理与模型      | `agent`, `agents`, `models`, `routing`                               | 否              |
| 自动化          | `hooks`, `cron`, `agent.heartbeat`                                   | 否              |
| 会话与消息 | `session`, `messages`                                                | 否              |
| 工具与媒体       | `tools`, `browser`, `skills`, `audio`, `talk`                        | 否              |
| UI 与杂项           | `ui`, `logging`, `identity`, `bindings`                              | 否              |
| Gateway 服务器      | `gateway.*` (port, bind, auth, tailscale, TLS, HTTP)                 | **是**         |
| 基础设施      | `discovery`, `canvasHost`, `plugins`                                 | **是**         |

<Note>
__CODE_BLOCK_34__ and __CODE_BLOCK_35__ are exceptions — changing them does **not** trigger a restart.
</Note>

## 配置 RPC（编程更新）

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

OpenClaw 从父进程读取环境变量，外加：

- `.env` 来自当前工作目录（如果存在）
- `~/.openclaw/.env`（全局回退）

这两个文件都不会覆盖现有的环境变量。您也可以在配置中设置内联环境变量：

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: { GROQ_API_KEY: "gsk-..." },
  },
}
```

<Accordion title="Shell 环境变量导入（可选）">
  如果启用且预期的键未设置，OpenClaw 将运行您的登录 shell 并仅导入缺失的键：

```json5
{
  env: {
    shellEnv: { enabled: true, timeoutMs: 15000 },
  },
}
```

环境变量等效项：`OPENCLAW_LOAD_SHELL_ENV=1`
</Accordion>

<Accordion title="配置值中的环境变量替换">
  在任何配置字符串值中使用 `${VAR_NAME}` 引用环境变量：

```json5
{
  gateway: { auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" } },
  models: { providers: { custom: { apiKey: "${CUSTOM_API_KEY}" } } },
}
```

规则：

- 仅匹配大写名称：`[A-Z_][A-Z0-9_]*`
- 缺失/空变量在加载时抛出错误
- 使用 `$${VAR}` 转义以获得字面输出
- 在 `$include` 文件内有效
- 内联替换：`"${BASE}/v1"` → `"https://api.example.com/v1"`

</Accordion>

<Accordion title="Secret 引用（env, file, exec）">
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

SecretRef 详情（包括用于 `env`/`file`/`exec` 的 `secrets.providers`）见 [Secrets 管理](/gateway/secrets)。
支持的 credential 路径列在 [SecretRef Credential Surface](/reference/secretref-credential-surface) 中。
</Accordion>

请参阅 [环境](/help/environment) 了解完整的优先级和来源。

## 完整参考

完整的逐字段参考，请参阅 **[配置参考](/gateway/configuration-reference)**。

---

_相关：[配置示例](/gateway/configuration-examples) · [配置参考](/gateway/configuration-reference) · [诊断](/gateway/doctor)_