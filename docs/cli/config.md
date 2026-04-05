---
summary: "CLI reference for `openclaw config` (get/set/unset/file/schema/validate)"
read_when:
  - You want to read or edit config non-interactively
title: "config"
---
# `openclaw config`

``openclaw.json`` 中用于非交互式编辑的配置辅助工具：按路径获取/设置/取消/文件/模式/验证值并打印当前配置文件。不带子命令运行以打开配置向导（与 ``openclaw configure`` 相同）。

根选项：

- ``--section <section>``：当你不带子命令运行 ``openclaw config`` 时的可重复引导式安装部分过滤器

支持的引导部分：

- ``workspace``
- ``model``
- ``web``
- ``gateway``
- ``daemon``
- ``channels``
- ``plugins``
- ``skills``
- ``health``

## 示例

````bash
openclaw config file
openclaw config --section model
openclaw config --section gateway --section daemon
openclaw config schema
openclaw config get browser.executablePath
openclaw config set browser.executablePath "/usr/bin/google-chrome"
openclaw config set agents.defaults.heartbeat.every "2h"
openclaw config set agents.list[0].tools.exec.node "node-id-or-name"
openclaw config set channels.discord.token --ref-provider default --ref-source env --ref-id DISCORD_BOT_TOKEN
openclaw config set secrets.providers.vaultfile --provider-source file --provider-path /etc/openclaw/secrets.json --provider-mode json
openclaw config unset plugins.entries.brave.config.webSearch.apiKey
openclaw config set channels.discord.token --ref-provider default --ref-source env --ref-id DISCORD_BOT_TOKEN --dry-run
openclaw config validate
openclaw config validate --json
````

### ``config schema``

将 ``openclaw.json`` 生成的 JSON 架构以 JSON 格式打印到标准输出。

包含内容：

- 当前根配置架构，以及一个用于编辑器工具的根 ``$schema`` 字符串字段
- 字段 ``title`` 和 ``description`` 文档元数据，由控制 UI 使用
- 当存在匹配的字段文档时，嵌套对象、通配符 (``*``) 和数组项 (``[]``) 节点继承相同的 ``title`` / ``description`` 元数据
- 当存在匹配的字段文档时，``anyOf`` / ``oneOf`` / ``allOf`` 分支也继承相同的文档元数据
- 当可以加载运行时清单时，尽力而为的实时插件 + 通道架构元数据
- 即使当前配置无效，也会提供一个干净的后备架构

相关运行时 RPC：

- ``config.schema.lookup`` 返回一个归一化的配置路径，带有浅层架构节点 (``title``, ``description``, ``type``, ``enum``, ``const``, 通用边界)，匹配的 UI 提示元数据和直接子摘要。在控制 UI 或自定义客户端中用于路径范围的钻取。

````bash
openclaw config schema
````

当您想使用其他工具检查或验证它时，将其管道传输到文件中：

````bash
openclaw config schema > openclaw.schema.json
````

### 路径

路径使用点号或括号表示法：

````bash
openclaw config get agents.defaults.workspace
openclaw config get agents.list[0].id
````

使用代理列表索引来定位特定代理：

````bash
openclaw config get agents.list
openclaw config set agents.list[1].tools.exec.node "node-id-or-name"
````

## 值

值尽可能解析为 JSON5；否则视为字符串。
使用 ``--strict-json`` 强制进行 JSON5 解析。``--json`` 仍作为遗留别名支持。

````bash
openclaw config set agents.defaults.heartbeat.every "0m"
openclaw config set gateway.port 19001 --strict-json
openclaw config set channels.whatsapp.groups '["*"]' --strict-json
````

``config get <path> --json`` 将原始值以 JSON 格式打印，而不是终端格式化文本。

## ``config set`` 模式

``openclaw config set`` 支持四种赋值样式：

1. 值模式：``openclaw config set <path> <value>``
2. SecretRef 构建器模式：

````bash
openclaw config set channels.discord.token \
  --ref-provider default \
  --ref-source env \
  --ref-id DISCORD_BOT_TOKEN
````

3. Provider 构建器模式（仅限 ``secrets.providers.<alias>`` 路径）：

````bash
openclaw config set secrets.providers.vault \
  --provider-source exec \
  --provider-command /usr/local/bin/openclaw-vault \
  --provider-arg read \
  --provider-arg openai/api-key \
  --provider-timeout-ms 5000
````

4. 批处理模式（``--batch-json`` 或 ``--batch-file``）：

````bash
openclaw config set --batch-json '[
  {
    "path": "secrets.providers.default",
    "provider": { "source": "env" }
  },
  {
    "path": "channels.discord.token",
    "ref": { "source": "env", "provider": "default", "id": "DISCORD_BOT_TOKEN" }
  }
]'
````

````bash
openclaw config set --batch-file ./config-set.batch.json --dry-run
````

策略说明：

- SecretRef 赋值在不支持的运行时可变表面上会被拒绝（例如 ``hooks.token``, ``commands.ownerDisplaySecret``, Discord 线程绑定 Webhook 令牌，以及 WhatsApp 凭据 JSON）。请参阅 [SecretRef 凭据表面](/reference/secretref-credential-surface)。

批处理解析始终使用批处理负载 (``--batch-json`/`--batch-file``) 作为事实来源。
``--strict-json`` / ``--json`` 不会更改批处理解析行为。

JSON 路径/值模式对 SecretRef 和 Provider 仍然支持：

````bash
openclaw config set channels.discord.token \
  '{"source":"env","provider":"default","id":"DISCORD_BOT_TOKEN"}' \
  --strict-json

openclaw config set secrets.providers.vaultfile \
  '{"source":"file","path":"/etc/openclaw/secrets.json","mode":"json"}' \
  --strict-json
````

## Provider 构建器标志

Provider 构建器目标必须使用 ``secrets.providers.<alias>`` 作为路径。

常见标志：

- ``--provider-source <env|file|exec>``
- ``--provider-timeout-ms <ms>`` (``file``, ``exec``)

环境 Provider (``--provider-source env``)：

- ``--provider-allowlist <ENV_VAR>`` (可重复)

文件 Provider (``--provider-source file``)：

- ``--provider-path <path>`` (必需)
- ``--provider-mode <singleValue|json>``
- ``--provider-max-bytes <bytes>``

执行 Provider (``--provider-source exec``)：

- ``--provider-command <path>`` (必需)
- ``--provider-arg <arg>`` (可重复)
- ``--provider-no-output-timeout-ms <ms>``
- ``--provider-max-output-bytes <bytes>``
- ``--provider-json-only``
- ``--provider-env <KEY=VALUE>`` (可重复)
- ``--provider-pass-env <ENV_VAR>`` (可重复)
- ``--provider-trusted-dir <path>`` (可重复)
- ``--provider-allow-insecure-path``
- ``--provider-allow-symlink-command``

强化执行 Provider 示例：

````bash
openclaw config set secrets.providers.vault \
  --provider-source exec \
  --provider-command /usr/local/bin/openclaw-vault \
  --provider-arg read \
  --provider-arg openai/api-key \
  --provider-json-only \
  --provider-pass-env VAULT_TOKEN \
  --provider-trusted-dir /usr/local/bin \
  --provider-timeout-ms 5000
````

## 试运行

使用 ``--dry-run`` 验证更改而不写入 ``openclaw.json``。

````bash
openclaw config set channels.discord.token \
  --ref-provider default \
  --ref-source env \
  --ref-id DISCORD_BOT_TOKEN \
  --dry-run

openclaw config set channels.discord.token \
  --ref-provider default \
  --ref-source env \
  --ref-id DISCORD_BOT_TOKEN \
  --dry-run \
  --json

openclaw config set channels.discord.token \
  --ref-provider vault \
  --ref-source exec \
  --ref-id discord/token \
  --dry-run \
  --allow-exec
````

试运行行为：

- 构建器模式：运行 SecretRef 可解析性检查以针对更改的 refs/providers。
- JSON 模式 (``--strict-json``, ``--json`` 或批处理模式)：运行架构验证加上 SecretRef 可解析性检查。
- 策略验证也会在已知的不支持的 SecretRef 目标表面上运行。
- 策略检查评估完整的变更后配置，因此父对象写入（例如将 ``hooks`` 设置为对象）无法绕过不支持的表面验证。
- 默认情况下，试运行期间跳过 Exec SecretRef 检查以避免命令副作用。
- 使用 ``--allow-exec`` 配合 ``--dry-run`` 选择加入 Exec SecretRef 检查（这可能会执行 Provider 命令）。
- ``--allow-exec`` 仅用于试运行，如果未使用 ``--dry-run`` 则报错。

``--dry-run --json`` 打印机器可读的报告：

- ``ok``: 试运行是否通过
- ``operations``: 评估的赋值数量
- ``checks``: 是否运行了架构/可解析性检查
- ``checks.resolvabilityComplete``: 可解析性检查是否运行完成（跳过 exec refs 时为 false）
- ``refsChecked``: 试运行期间实际解析的 refs 数量
- ``skippedExecRefs``: 因未设置 ``--allow-exec`` 而跳过的 exec refs 数量
- ``errors``: 当 ``ok=false`` 时的结构化架构/可解析性失败

### JSON 输出形状

````json5
{
  ok: boolean,
  operations: number,
  configPath: string,
  inputModes: ["value" | "json" | "builder", ...],
  checks: {
    schema: boolean,
    resolvability: boolean,
    resolvabilityComplete: boolean,
  },
  refsChecked: number,
  skippedExecRefs: number,
  errors?: [
    {
      kind: "schema" | "resolvability",
      message: string,
      ref?: string, // present for resolvability errors
    },
  ],
}
````

成功示例：

````json
{
  "ok": true,
  "operations": 1,
  "configPath": "~/.openclaw/openclaw.json",
  "inputModes": ["builder"],
  "checks": {
    "schema": false,
    "resolvability": true,
    "resolvabilityComplete": true
  },
  "refsChecked": 1,
  "skippedExecRefs": 0
}
````

失败示例：

````json
{
  "ok": false,
  "operations": 1,
  "configPath": "~/.openclaw/openclaw.json",
  "inputModes": ["builder"],
  "checks": {
    "schema": false,
    "resolvability": true,
    "resolvabilityComplete": true
  },
  "refsChecked": 1,
  "skippedExecRefs": 0,
  "errors": [
    {
      "kind": "resolvability",
      "message": "Error: Environment variable \"MISSING_TEST_SECRET\" is not set.",
      "ref": "env:default:MISSING_TEST_SECRET"
    }
  ]
}
````

如果试运行失败：

- `config schema validation failed`: 您的变更后 config 结构无效；请修复 path/value 或 provider/ref 对象结构。
- `Config policy validation failed: unsupported SecretRef usage`: 将该凭证移回 plaintext/string 输入，并仅保留 SecretRefs 在支持的 surfaces 上。
- `SecretRef assignment(s) could not be resolved`: 引用的 provider/ref 当前无法解析（缺少 env var、无效的 file pointer、exec provider 失败，或 provider/source 不匹配）。
- `Dry run note: skipped <n> exec SecretRef resolvability check(s)`: dry-run 跳过了 exec refs；如果您需要 exec 可解析性验证，请使用 `--allow-exec` 重新运行。
- 对于 batch mode，修复失败的 entries 并在 writing 前重新运行 `--dry-run`。

## 子命令

- `config file`: 打印活动的 config 文件路径（从 `OPENCLAW_CONFIG_PATH` 或默认 location 解析）。

编辑后重启 gateway。

## Validate

在不启动 gateway 的情况下，根据活动 schema 验证当前 config
gateway。

```bash
openclaw config validate
openclaw config validate --json
```