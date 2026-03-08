---
summary: "Secrets management: SecretRef contract, runtime snapshot behavior, and safe one-way scrubbing"
read_when:
  - Configuring SecretRefs for provider credentials and `auth-profiles.json` refs
  - Operating secrets reload, audit, configure, and apply safely in production
  - Understanding startup fail-fast, inactive-surface filtering, and last-known-good behavior
title: "Secrets Management"
---
# 密钥管理

OpenClaw 支持组合式 SecretRef，因此受支持的凭证无需以明文形式存储在配置中。

明文仍然有效。每个凭证的 SecretRef 是可选启用的。

## 目标和运行时模型

密钥被解析为内存中的运行时快照。

- 解析在激活期间是立即执行的，而不是在请求路径上按需延迟。
- 当实际上有效的 SecretRef 无法解析时，启动会快速失败。
- 重载使用原子交换：完全成功，或保留最后一个已知良好的快照。
- 运行时请求仅从活动的内存快照中读取。

这确保了密钥提供程序的中断不会影响热点请求路径。

## 活动表面过滤

SecretRef 仅在实际上有效的表面上进行验证。

- 已启用的表面：未解析的引用会阻止启动/重载。
- 非活动表面：未解析的引用不会阻止启动/重载。
- 非活动的引用发出非致命诊断，代码为 `SECRETS_REF_IGNORED_INACTIVE_SURFACE`。

非活动表面的示例：

- 禁用的通道/账户条目。
- 没有启用账户继承的顶级通道凭证。
- 禁用的工具/功能表面。
- 未被 `tools.web.search.provider` 选定的 Web 搜索提供程序特定密钥。
  在自动模式（提供程序未设置）下，提供程序特定密钥也用于提供程序自动检测。
- 如果以下任一条件为真，则 `gateway.remote.token` / `gateway.remote.password` SecretRef 处于活动状态（当 `gateway.remote.enabled` 不是 `false` 时）：
  - `gateway.mode=remote`
  - `gateway.remote.url` 已配置
  - `gateway.tailscale.mode` 是 `serve` 或 `funnel`
    在没有这些远程表面的本地模式下：
  - 当令牌认证可以胜出且未配置 env/auth 令牌时，`gateway.remote.token` 处于活动状态。
  - 仅当密码认证可以胜出且未配置 env/auth 密码时，`gateway.remote.password` 才处于活动状态。
- 当设置 `OPENCLAW_GATEWAY_TOKEN`（或 `CLAWDBOT_GATEWAY_TOKEN`）时，`gateway.auth.token` SecretRef 对于启动身份验证解析是不活动的，因为该运行时 env 令牌输入胜出。

## 网关身份验证表面诊断

当在 `gateway.auth.token`, `gateway.auth.password`,
`gateway.remote.token`, 或 `gateway.remote.password` 上配置了 SecretRef 时，网关启动/重载记录
表面状态明确：

- `active`: SecretRef 是有效身份验证表面的一部分，必须解析。
- `inactive`: 此运行时忽略 SecretRef，因为另一个身份验证表面胜出，或者
  因为远程身份验证已禁用/不活动。

这些条目使用 `SECRETS_GATEWAY_AUTH_SURFACE` 记录，并包含由
活动表面策略使用的理由，因此您可以看到为何凭证被视为活动或非活动。

## 初始化参考预检

当初始化运行于交互模式且您选择 SecretRef 存储时，OpenClaw 在保存前运行预检验证：

- Env 引用：验证环境变量名称，并确认初始化期间可见非空值。
- 提供程序引用 (`file` 或 `exec`)：验证提供程序选择，解析 `id`，并检查解析值的类型。
- 快速启动重用路径：当 `gateway.auth.token` 已经是 SecretRef 时，初始化会在探测/仪表板引导之前解析它（针对 `env`, `file`, 和 `exec` 引用），使用相同的快速失败门控。

如果验证失败，初始化将显示错误并允许您重试。

## SecretRef 契约

在所有地方使用一种对象形状：

```json5
{ source: "env" | "file" | "exec", provider: "default", id: "..." }
```

### `source: "env"`

```json5
{ source: "env", provider: "default", id: "OPENAI_API_KEY" }
```

验证：

- `provider` 必须匹配 `^[a-z][a-z0-9_-]{0,63}$`
- `id` 必须匹配 `^[A-Z][A-Z0-9_]{0,127}$`

### `source: "file"`

```json5
{ source: "file", provider: "filemain", id: "/providers/openai/apiKey" }
```

验证：

- `provider` 必须匹配 `^[a-z][a-z0-9_-]{0,63}$`
- `id` 必须是绝对 JSON 指针 (`/...`)
- 段中的 RFC6901 转义：`~` => `~0`, `/` => `~1`

### `source: "exec"`

```json5
{ source: "exec", provider: "vault", id: "providers/openai/apiKey" }
```

验证：

- `provider` 必须匹配 `^[a-z][a-z0-9_-]{0,63}$`
- `id` 必须匹配 `^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$`

## 提供程序配置

在 `secrets.providers` 下定义提供程序：

```json5
{
  secrets: {
    providers: {
      default: { source: "env" },
      filemain: {
        source: "file",
        path: "~/.openclaw/secrets.json",
        mode: "json", // or "singleValue"
      },
      vault: {
        source: "exec",
        command: "/usr/local/bin/openclaw-vault-resolver",
        args: ["--profile", "prod"],
        passEnv: ["PATH", "VAULT_ADDR"],
        jsonOnly: true,
      },
    },
    defaults: {
      env: "default",
      file: "filemain",
      exec: "vault",
    },
    resolution: {
      maxProviderConcurrency: 4,
      maxRefsPerProvider: 512,
      maxBatchBytes: 262144,
    },
  },
}
```

### 环境提供程序

- 通过 `allowlist` 的可选白名单。
- 缺失/空的环境值会导致解析失败。

### 文件提供程序

- 从 `path` 读取本地文件。
- `mode: "json"` 期望 JSON 对象负载，并将 `id` 解析为指针。
- `mode: "singleValue"` 期望引用 ID `"value"` 并返回文件内容。
- 路径必须通过所有权/权限检查。
- Windows 故障关闭注意：如果路径不可用 ACL 验证，解析将失败。仅限可信路径，在该提供程序上设置 `allowInsecurePath: true` 以绕过路径安全检查。

### 执行提供程序

- 运行配置的绝对二进制路径，不使用 Shell。
- 默认情况下，`command` 必须指向常规文件（不是符号链接）。
- 设置 `allowSymlinkCommand: true` 以允许符号链接命令路径（例如 Homebrew shims）。OpenClaw 验证解析的目标路径。
- 将 `allowSymlinkCommand` 与 `trustedDirs` 配对用于包管理器路径（例如 `["/opt/homebrew"]`）。
- 支持超时、无输出超时、输出字节限制、env 白名单和可信目录。
- Windows 故障关闭注意：如果命令路径不可用 ACL 验证，解析将失败。仅限可信路径，在该提供程序上设置 `allowInsecurePath: true` 以绕过路径安全检查。

请求负载 (stdin):

```json
{ "protocolVersion": 1, "provider": "vault", "ids": ["providers/openai/apiKey"] }
```

响应负载 (stdout):

```jsonc
{ "protocolVersion": 1, "values": { "providers/openai/apiKey": "<openai-api-key>" } } // pragma: allowlist secret
```

可选的按 ID 错误：

```json
{
  "protocolVersion": 1,
  "values": {},
  "errors": { "providers/openai/apiKey": { "message": "not found" } }
}
```

## 执行集成示例

### 1Password CLI

```json5
{
  secrets: {
    providers: {
      onepassword_openai: {
        source: "exec",
        command: "/opt/homebrew/bin/op",
        allowSymlinkCommand: true, // required for Homebrew symlinked binaries
        trustedDirs: ["/opt/homebrew"],
        args: ["read", "op://Personal/OpenClaw QA API Key/password"],
        passEnv: ["HOME"],
        jsonOnly: false,
      },
    },
  },
  models: {
    providers: {
      openai: {
        baseUrl: "https://api.openai.com/v1",
        models: [{ id: "gpt-5", name: "gpt-5" }],
        apiKey: { source: "exec", provider: "onepassword_openai", id: "value" },
      },
    },
  },
}
```

### HashiCorp Vault CLI

```json5
{
  secrets: {
    providers: {
      vault_openai: {
        source: "exec",
        command: "/opt/homebrew/bin/vault",
        allowSymlinkCommand: true, // required for Homebrew symlinked binaries
        trustedDirs: ["/opt/homebrew"],
        args: ["kv", "get", "-field=OPENAI_API_KEY", "secret/openclaw"],
        passEnv: ["VAULT_ADDR", "VAULT_TOKEN"],
        jsonOnly: false,
      },
    },
  },
  models: {
    providers: {
      openai: {
        baseUrl: "https://api.openai.com/v1",
        models: [{ id: "gpt-5", name: "gpt-5" }],
        apiKey: { source: "exec", provider: "vault_openai", id: "value" },
      },
    },
  },
}
```

### `sops`

```json5
{
  secrets: {
    providers: {
      sops_openai: {
        source: "exec",
        command: "/opt/homebrew/bin/sops",
        allowSymlinkCommand: true, // required for Homebrew symlinked binaries
        trustedDirs: ["/opt/homebrew"],
        args: ["-d", "--extract", '["providers"]["openai"]["apiKey"]', "/path/to/secrets.enc.json"],
        passEnv: ["SOPS_AGE_KEY_FILE"],
        jsonOnly: false,
      },
    },
  },
  models: {
    providers: {
      openai: {
        baseUrl: "https://api.openai.com/v1",
        models: [{ id: "gpt-5", name: "gpt-5" }],
        apiKey: { source: "exec", provider: "sops_openai", id: "value" },
      },
    },
  },
}
```

## 受支持的凭证表面

标准受支持和不受支持的凭证列在：

- [SecretRef Credential Surface](/reference/secretref-credential-surface)

运行时生成或轮换的凭证以及 OAuth 刷新材料有意排除在只读 SecretRef 解析之外。

## 所需行为和优先级

- 没有引用的字段：保持不变。
- 有引用的字段：在激活期间的活动表面上是必需的。
- 如果同时存在明文和引用，则在支持的优先级路径上引用优先。

警告和审计信号：

- `SECRETS_REF_OVERRIDES_PLAINTEXT` (运行时警告)
- `REF_SHADOWED` (当 `auth-profiles.json` 凭证优先于 `openclaw.json` 引用时的审计发现)

Google Chat 兼容性行为：

- `serviceAccountRef` 优先于明文 `serviceAccount`。
- 当设置兄弟引用时，明文值将被忽略。

## 激活触发器

Secret 激活运行于：

- 启动（预检加最终激活）
- 配置重载热应用路径
- 配置重载重启检查路径
- 通过 `secrets.reload` 的手动重载

激活契约：

- 成功原子地交换快照。
- 启动失败中止网关启动。
- 运行时重载失败保留最后一个已知良好的快照。

## 降级和恢复信号

当健康状态后的重载时间激活失败时，OpenClaw 进入降级密钥状态。

一次性系统事件和日志代码：

- `SECRETS_RELOADER_DEGRADED`
- `SECRETS_RELOADER_RECOVERED`

行为：

- 降级：运行时保留最后一个已知良好的快照。
- 恢复：在下一次成功激活后发出一次。
- 已在降级状态下重复失败时记录警告，但不会大量产生事件。
- 启动快速失败不会发出降级事件，因为运行时从未变为活动状态。

## 命令路径解析

命令路径可以选择通过网关快照 RPC 支持 SecretRef 解析。

有两种广泛的行为：

- 严格命令路径（例如 `openclaw memory` 远程内存路径和 `openclaw qr --remote`）从活动快照读取，并在所需的 SecretRef 不可用时快速失败。
- 只读命令路径（例如 `openclaw status`、`openclaw status --all`、`openclaw channels status`、`openclaw channels resolve` 以及只读 Doctor/Config 修复流程）也首选活动快照，但当该命令路径中 targeted SecretRef 不可用时，会降级而不是中止。

只读行为：

- 当网关运行时，这些命令首先从活动快照读取。
- 如果网关解析不完整或网关不可用，它们会尝试针对特定命令表面进行 targeted 本地回退。
- 如果 targeted SecretRef 仍然不可用，命令将继续输出降级的只读内容以及明确的诊断信息，例如"configured but unavailable in this command path"。
- 这种降级行为仅限于命令本地。它不会削弱运行时启动、重载或 Send/Auth 路径。

其他说明：

- 后端 Secret 轮换后的快照刷新由 `openclaw secrets reload` 处理。
- 这些命令路径使用的网关 RPC 方法：`secrets.resolve`。

## 审计和配置工作流

默认操作员流程：

```bash
openclaw secrets audit --check
openclaw secrets configure
openclaw secrets audit --check
```

### `secrets audit`

发现包括：

- 静止状态的明文值（`openclaw.json`、`auth-profiles.json`、`.env` 和生成的 `agents/*/agent/models.json`）
- 生成的 `models.json` 条目中的明文敏感 Provider Header 残留
- 未解析的 Refs
- 优先级遮蔽（`auth-profiles.json` 优先于 `openclaw.json` Refs）
- 遗留残留（`auth.json`、OAuth 提醒）

Header 残留说明：

- 敏感 Provider Header 检测基于名称启发式（常见 Auth/Credential Header 名称和片段，如 `authorization`、`x-api-key`、`token`、`secret`、`password` 和 `credential`）。

### `secrets configure`

交互式助手，用于：

- 首先配置 `secrets.providers`（`env`/`file`/`exec`，添加/编辑/删除）
- 允许您在 `openclaw.json` 中选择支持的携带 Secret 的字段，加上 `auth-profiles.json` 用于一个 Agent 范围
- 可以直接在 Target Picker 中创建新的 `auth-profiles.json` 映射
- 捕获 SecretRef 详细信息（`source`、`provider`、`id`）
- 运行预检解析
- 可以立即应用

有帮助的模式：

- `openclaw secrets configure --providers-only`
- `openclaw secrets configure --skip-provider-setup`
- `openclaw secrets configure --agent <id>`

`configure` 应用默认值：

- 从 `auth-profiles.json` 中清除 targeted Providers 的匹配静态凭证
- 从 `auth.json` 中清除遗留静态 `api_key` 条目
- 从 `<config-dir>/.env` 中清除匹配的已知 Secret 行

### `secrets apply`

应用已保存的计划：

```bash
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run
```

有关严格的 Target/Path 合同详细信息和确切拒绝规则，请参阅：

- [Secrets 应用计划合同](/gateway/secrets-plan-contract)

## 单向安全策略

OpenClaw 故意不写入包含历史明文 Secret 值的回滚备份。

安全模型：

- 预检必须在写入模式之前成功
- 运行时激活在提交前进行验证
- 应用使用原子文件替换更新文件，并在失败时尽力恢复

## 遗留 Auth 兼容性说明

对于静态凭证，运行时不再依赖明文遗留 Auth 存储。

- 运行时凭证源是解析后的内存快照。
- 遗留静态 `api_key` 条目在发现时被清除。
- OAuth 相关的兼容性行为保持独立。

## Web UI 说明

某些 SecretInput 联合在原始编辑器模式下比在表单模式下更容易配置。

## 相关文档

- CLI 命令：[secrets](/cli/secrets)
- 计划合同详细信息：[Secrets 应用计划合同](/gateway/secrets-plan-contract)
- 凭证表面：[SecretRef 凭证表面](/reference/secretref-credential-surface)
- Auth 设置：[认证](/gateway/authentication)
- 安全态势：[安全](/gateway/security)
- 环境优先级：[环境变量](/help/environment)