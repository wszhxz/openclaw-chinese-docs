---
summary: "Configuration overview: common tasks, quick setup, and links to the full reference"
read_when:
  - Setting up OpenClaw for the first time
  - Looking for common configuration patterns
  - Navigating to specific config sections
title: "Configuration"
---
# 配置

OpenClaw 从 `~/.openclaw/openclaw.json` 读取一个可选的 <Tooltip tip="JSON5 支持注释和尾随逗号">**JSON5**</Tooltip> 配置文件。

如果文件缺失，OpenClaw 将使用安全的默认设置。添加配置文件的一些常见原因：

- 连接频道并控制谁可以向机器人发送消息
- 设置模型、工具、沙箱或自动化（cron、hooks）
- 调整会话、媒体、网络或用户界面

查看[完整参考](/gateway/configuration-reference)以获取每个可用字段的信息。

<Tip>
**New to configuration?** Start with __CODE_BLOCK_1__ for interactive setup, or check out the [Configuration Examples](/gateway/configuration-examples) guide for complete copy-paste configs.
</Tip>

## 最小配置

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

- 网关无法启动
- 仅诊断命令可用 (`openclaw doctor`, `openclaw logs`, `openclaw health`, `openclaw status`)
- 运行 `openclaw doctor` 查看具体问题
- 运行 `openclaw doctor --fix`（或 `--yes`）应用修复

## 常见任务

<AccordionGroup>
  <Accordion title="设置频道（WhatsApp、Telegram、Discord 等）">
    每个频道在其自身的配置部分下有 `channels.<provider>`。请参阅专用频道页面以获取设置步骤：

- [WhatsApp](/channels/whatsapp) — `channels.whatsapp`
- [Telegram](/channels/telegram) — `channels.telegram`
- [Discord](/channels/discord) — `channels.discord`
- [Slack](/channels/slack) — `channels.slack`
- [Signal](/channels/signal) — `channels.signal`
- [iMessage](/channels/imessage) — `channels.imessage`
- [Google Chat](/channels/googlechat) — `channels.googlechat`
- [Mattermost](/channels/mattermost) — `channels.mattermost`
- [MS Teams](/channels/msteams) — `channels.msteams`

所有渠道共享相同的DM策略模式：

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
设置主要模型和可选的备用模型：

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

- `agents.defaults.models` 定义模型目录并作为 `/model` 的白名单。
- 模型引用使用 `provider/model` 格式（例如 `anthropic/claude-opus-4-6`）。
- `agents.defaults.imageMaxDimensionPx` 控制转录/工具图像的下缩放（默认 `1200`）；较低的值通常会减少在以截图为主的运行中对视觉标记的使用。
- 有关在聊天中切换模型的信息，请参阅 [Models CLI](/concepts/models)，有关身份验证轮换和备用行为的信息，请参阅 [Model Failover](/concepts/model-failover)。
- 对于自定义/自托管提供商，请参阅参考中的 [Custom providers](/gateway/configuration-reference#custom-providers-and-base-urls)。

</Accordion>

<Accordion title="控制谁可以向机器人发送消息">
DM 访问权限通过每个渠道的 `dmPolicy` 进行控制：

- `"pairing"`（默认）：未知发件人会收到一个一次性配对代码以进行批准
- `"allowlist"`：仅允许在 `allowFrom` 中的发件人（或配对的允许存储）
- `"open"`：允许所有传入的DM（需要 `allowFrom: ["*"]`）
- `"disabled"`：忽略所有DM

对于群组，请使用 `groupPolicy` + `groupAllowFrom` 或特定于渠道的白名单。

有关每个渠道的详细信息，请参阅 [完整参考](/gateway/configuration-reference#dm-and-group-access)。

</Accordion>

<Accordion title="设置群聊提及门控">
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

    - **Metadata mentions**: native @-mentions (WhatsApp tap-to-mention, Telegram @bot, 等)
    - **Text patterns**: regex patterns in `mentionPatterns`
    - 请参阅[完整参考](/gateway/configuration-reference#group-chat-mention-gating)以获取每个频道的覆盖和自聊模式。

  </Accordion>

  <Accordion title="配置会话和重置">
    会话控制对话的连续性和隔离：

    ```json5
    {
      session: {
        dmScope: "per-channel-peer",  // recommended for multi-user
        threadBindings: {
          enabled: true,
          ttlHours: 24,
        },
        reset: {
          mode: "daily",
          atHour: 4,
          idleMinutes: 120,
        },
      },
    }
    ```

    - `dmScope`: `main` (共享) | `per-peer` | `per-channel-peer` | `per-account-channel-peer`
    - `threadBindings`: 线程绑定会话路由的全局默认值 (Discord 支持 `/focus`, `/unfocus`, `/agents`, 和 `/session ttl`)。
    - 请参阅[会话管理](/concepts/session)以获取范围、身份链接和发送策略。
    - 请参阅[完整参考](/gateway/configuration-reference#session)以获取所有字段。

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

    请参阅[沙箱](/gateway/sandboxing)以获取完整指南和[完整参考](/gateway/configuration-reference#sandbox)以获取所有选项。

  </Accordion>

  <Accordion title="设置心跳（定期检查）">
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

    - `every`: 持续时间字符串 (`30m`, `2h`)。设置 `0m` 以禁用。
    - `target`: `last` | `whatsapp` | `telegram` | `discord` | `none`
    - 请参阅[心跳](/gateway/heartbeat)以获取完整指南。

  </Accordion>

  <Accordion title="配置 cron 作业">
    ```json5
    {
      cron: {
        enabled: true,
        maxConcurrentRuns: 2,
        sessionRetention: "24h",
      },
    }
    ```

    请参阅[Cron 作业](/automation/cron-jobs)以获取功能概述和 CLI 示例。

  </Accordion>

  <Accordion title="设置 Webhook（钩子）">
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

请参阅[完整参考](/gateway/configuration-reference#hooks)以获取所有映射选项和Gmail集成信息。

  </Accordion>

  <Accordion title="配置多代理路由">
    运行多个隔离的代理，每个代理具有独立的工作区和会话：

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

    请参阅[多代理](/concepts/multi-agent)和[完整参考](/gateway/configuration-reference#multi-agent-routing)以获取绑定规则和每个代理的访问配置文件。

  </Accordion>

  <Accordion title="将配置拆分为多个文件 ($include)">
    使用`$include`来组织大型配置：

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
    - **文件数组**：按顺序深度合并（后面的覆盖前面的）
    - **同级键**：在包含后合并（覆盖包含的值）
    - **嵌套包含**：支持最多10层深度
    - **相对路径**：相对于包含文件进行解析
    - **错误处理**：缺失文件、解析错误和循环包含的清晰错误

  </Accordion>
</AccordionGroup>

## 配置热重载

网关监视`~/.openclaw/openclaw.json`并自动应用更改 — 大多数设置无需手动重启。

### 重载模式

| 模式                   | 行为                                                                                |
| ---------------------- | --------------------------------------------------------------------------------------- |
| **`hybrid`**（默认） | 立即热应用安全更改。对于关键更改会自动重启。           |
| **`hot`**              | 仅热应用安全更改。当需要重启时记录警告 — 您负责处理。 |
| **`restart`**          | 对于任何配置更改（安全或不安全），都会重启网关。                                 |
| **`off`**              | 禁用文件监视。更改将在下一次手动重启时生效。                 |

```json5
{
  gateway: {
    reload: { mode: "hybrid", debounceMs: 300 },
  },
}
```

### 热应用与需要重启的应用

大多数字段在不停机的情况下热应用。在 `hybrid` 模式下，需要重启的更改会自动处理。

| 类别            | 字段                                                               | 需要重启？ |
| ------------------- | -------------------------------------------------------------------- | --------------- |
| 渠道            | `channels.*`, `web` (WhatsApp) — 所有内置和扩展渠道 | 否              |
| 坐席与模型      | `agent`, `agents`, `models`, `routing`                               | 否              |
| 自动化          | `hooks`, `cron`, `agent.heartbeat`                                   | 否              |
| 会话与消息      | `session`, `messages`                                                | 否              |
| 工具与媒体      | `tools`, `browser`, `skills`, `audio`, `talk`                        | 否              |
| 用户界面与杂项  | `ui`, `logging`, `identity`, `bindings`                              | 否              |
| 网关服务器      | `gateway.*` (端口, 绑定, 认证, tailscale, TLS, HTTP)                 | **是**         |
| 基础设施        | `discovery`, `canvasHost`, `plugins`                                 | **是**         |

<Note>
__CODE_BLOCK_26__ and __CODE_BLOCK_27__ are exceptions — changing them does **not** trigger a restart.
</Note>

## 配置 RPC（编程更新）

<Note>
Control-plane write RPCs (__CODE_BLOCK_28__, __CODE_BLOCK_29__, __CODE_BLOCK_30__) are rate-limited to **3 requests per 60 seconds** per __CODE_BLOCK_31__. When limited, the RPC returns __CODE_BLOCK_32__ with __CODE_BLOCK_33__.
</Note>

<AccordionGroup>
  <Accordion title="config.apply (完整替换)">
    验证并写入完整配置，并在一步中重启网关。

    <Warning>
    __CODE_BLOCK_34__ replaces the **entire config**. Use __CODE_BLOCK_35__ for partial updates, or __CODE_BLOCK_36__ for single keys.
    </Warning>

    参数:

    - `raw` (string) — 整个配置的 JSON5 负载
    - `baseHash` (可选) — 来自 `config.get` 的配置哈希（当配置存在时必需）
    - `sessionKey` (可选) — 重启后唤醒 ping 的会话密钥
    - `note` (可选) — 重启哨兵的备注
    - `restartDelayMs` (可选) — 重启前的延迟（默认 2000）

    当一个重启请求已经待处理或正在飞行时，重启请求会被合并，并且在重启周期之间应用 30 秒的冷却时间。

    ```bash
    openclaw gateway call config.get --params '{}'  # capture payload.hash
    openclaw gateway call config.apply --params '{
      "raw": "{ agents: { defaults: { workspace: \"~/.openclaw/workspace\" } } }",
      "baseHash": "<hash>",
      "sessionKey": "agent:main:whatsapp:dm:+15555550123"
    }'
    ```

  </Accordion>

<Accordion title="config.patch (部分更新)">
    将部分更新合并到现有配置中（JSON合并补丁语义）：

    - 对象递归合并
    - `null` 删除键
    - 数组替换

    参数：

    - `raw` (string) — 仅包含要更改的键的JSON5
    - `baseHash` (必需) — 来自`config.get`的配置哈希
    - `sessionKey`, `note`, `restartDelayMs` — 与`config.apply`相同

    重启行为与`config.apply`匹配：合并待处理的重启加上每次重启周期之间的30秒冷却时间。

    ```bash
    openclaw gateway call config.patch --params '{
      "raw": "{ channels: { telegram: { groups: { \"*\": { requireMention: false } } } } }",
      "baseHash": "<hash>"
    }'
    ```

  </Accordion>
</AccordionGroup>

## 环境变量

OpenClaw 从父进程读取环境变量，再加上：

- 当前工作目录中的`.env`（如果存在）
- `~/.openclaw/.env`（全局回退）

这两个文件不会覆盖现有的环境变量。你还可以在配置中设置内联环境变量：

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: { GROQ_API_KEY: "gsk-..." },
  },
}
```

<Accordion title="Shell 环境导入（可选）">
  如果启用且预期的键未设置，OpenClaw 将运行你的登录 shell 并仅导入缺失的键：

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
  在任何配置字符串值中引用环境变量，使用`${VAR_NAME}`：

```json5
{
  gateway: { auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" } },
  models: { providers: { custom: { apiKey: "${CUSTOM_API_KEY}" } } },
}
```

规则：

- 仅匹配大写名称：`[A-Z_][A-Z0-9_]*`
- 缺少/空变量在加载时抛出错误
- 使用`$${VAR}`进行转义以输出字面值
- 支持在`$include`文件中使用
- 内联替换：`"${BASE}/v1"` → `"https://api.example.com/v1"`

</Accordion>

参见 [Environment](/help/environment) 获取完整的优先级和来源。

## 完整参考

有关完整的字段-by-字段参考，请参阅 **[Configuration Reference](/gateway/configuration-reference)**。

---

_相关：[Configuration Examples](/gateway/configuration-examples) · [Configuration Reference](/gateway/configuration-reference) · [Doctor](/gateway/doctor)_