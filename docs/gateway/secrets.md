---
summary: "Secrets management: SecretRef contract, runtime snapshot behavior, and safe one-way scrubbing"
read_when:
  - Configuring SecretRefs for provider credentials and `auth-profiles.json` refs
  - Operating secrets reload, audit, configure, and apply safely in production
  - Understanding startup fail-fast, inactive-surface filtering, and last-known-good behavior
title: "Secrets Management"
---
# 密钥管理

OpenClaw 支持叠加式 SecretRefs，因此受支持的凭据无需以明文形式存储在配置中。

明文方式仍然可用。SecretRefs 按凭据逐项启用（opt-in）。

## 目标与运行时模型

密钥被解析为内存中的运行时快照。

- 解析在激活期间立即执行（eager），而非在请求路径上延迟执行（lazy）。
- 当某个实际处于活动状态的 SecretRef 无法解析时，启动将快速失败。
- 重载采用原子交换机制：全部成功，或保留上一个已知有效的快照。
- 运行时请求仅从当前活动的内存快照中读取。

这可确保密钥提供方中断不会影响关键请求路径。

## 活动面过滤

SecretRefs 仅在实际处于活动状态的面上进行验证。

- 已启用的面：未解析的引用将阻塞启动/重载。
- 非活动面：未解析的引用不会阻塞启动/重载。
- 非活动引用会发出非致命诊断信息，其错误码为 `SECRETS_REF_IGNORED_INACTIVE_SURFACE`。

非活动面的示例包括：

- 已禁用的通道/账户条目。
- 没有任何已启用账户继承的顶层通道凭据。
- 已禁用的工具/功能面。
- 未被 `tools.web.search.provider` 选中的网络搜索提供商专用密钥。  
  在自动模式（provider 未设置）下，提供商专用密钥对提供商自动检测也属于活动状态。
- `gateway.remote.token` / `gateway.remote.password` SecretRefs 在 `gateway.remote.enabled` 不为 `false` 时属于活动状态（满足以下任一条件）：
  - `gateway.mode=remote`
  - `gateway.remote.url` 已配置
  - `gateway.tailscale.mode` 为 `serve` 或 `funnel`  
    在本地模式且无上述远程面的情况下：
  - 当令牌认证可能生效、且未配置环境变量/认证令牌时，`gateway.remote.token` 处于活动状态。
  - 当密码认证可能生效、且未配置环境变量/认证密码时，`gateway.remote.password` 仅处于活动状态。
- 当设置了 `OPENCLAW_GATEWAY_TOKEN`（或 `CLAWDBOT_GATEWAY_TOKEN`）时，`gateway.auth.token` SecretRef 在启动认证解析阶段为非活动状态，因为该运行时环境下环境变量令牌输入具有更高优先级。

## 网关认证面诊断

当 SecretRef 配置在 `gateway.auth.token`、`gateway.auth.password`、  
`gateway.remote.token` 或 `gateway.remote.password` 上时，网关启动/重载会显式记录该面的状态：

- `active`：该 SecretRef 属于实际生效的认证面，必须成功解析。
- `inactive`：该 SecretRef 在此运行时被忽略，原因可能是其他认证面胜出，或远程认证已被禁用/未激活。

这些日志条目使用 `SECRETS_GATEWAY_AUTH_SURFACE` 记录，并包含活动面策略所依据的原因，以便您了解某项凭据为何被视为活动或非活动状态。

## 入门参考预检

当入门流程以交互模式运行且您选择 SecretRef 存储方式时，OpenClaw 会在保存前执行预检验证：

- 环境变量引用（Env refs）：验证环境变量名称，并确认在入门过程中可见非空值。
- 提供方引用（Provider refs，`file` 或 `exec`）：验证提供方选择，解析 `id`，并检查解析结果的数据类型。
- 快速入门复用路径：当 `gateway.auth.token` 已是 SecretRef 时，入门流程将在探测/仪表板引导（针对 `env`、`file` 和 `exec` 引用）之前解析该引用，采用相同的快速失败机制（fail-fast gate）。

若验证失败，入门流程将显示错误并允许您重试。

## SecretRef 合约

所有位置均使用统一的对象结构：

```json5
{ source: "env" | "file" | "exec", provider: "default", id: "..." }
```

### `source: "env"`

```json5
{ source: "env", provider: "default", id: "OPENAI_API_KEY" }
```

验证规则：

- `provider` 必须匹配 `^[a-z][a-z0-9_-]{0,63}$`
- `id` 必须匹配 `^[A-Z][A-Z0-9_]{0,127}$`

### `source: "file"`

```json5
{ source: "file", provider: "filemain", id: "/providers/openai/apiKey" }
```

验证规则：

- `provider` 必须匹配 `^[a-z][a-z0-9_-]{0,63}$`
- `id` 必须为绝对 JSON 指针（`/...`）
- RFC6901 分段转义规则：`~` ⇒ `~0`，`/` ⇒ `~1`

### `source: "exec"`

```json5
{ source: "exec", provider: "vault", id: "providers/openai/apiKey" }
```

验证规则：

- `provider` 必须匹配 `^[a-z][a-z0-9_-]{0,63}$`
- `id` 必须匹配 `^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$`

## 提供方配置

在 `secrets.providers` 下定义提供方：

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

### 环境变量提供方（Env provider）

- 可选白名单，通过 `allowlist` 配置。
- 缺失或为空的环境变量值将导致解析失败。

### 文件提供方（File provider）

- 从 `path` 读取本地文件。
- `mode: "json"` 期望 JSON 对象载荷，并将 `id` 解析为指针。
- `mode: "singleValue"` 期望引用 ID `"value"`，并返回文件内容。
- 路径必须通过所有权/权限检查。
- Windows 平台“故障关闭”说明：若某路径无法执行 ACL 验证，则解析失败。仅对可信路径，可在该提供方上设置 `allowInsecurePath: true` 以绕过路径安全检查。

### 执行提供方（Exec provider）

- 运行所配置的绝对二进制路径，不经过 shell。
- 默认情况下，`command` 必须指向常规文件（非符号链接）。
- 设置 `allowSymlinkCommand: true` 可允许符号链接命令路径（例如 Homebrew shim）。OpenClaw 将验证解析后的目标路径。
- 将 `allowSymlinkCommand` 与 `trustedDirs` 配合使用，以支持包管理器路径（例如 `["/opt/homebrew"]`）。
- 支持超时、无输出超时、输出字节限制、环境变量白名单及可信目录。
- Windows 平台“故障关闭”说明：若命令路径无法执行 ACL 验证，则解析失败。仅对可信路径，可在该提供方上设置 `allowInsecurePath: true` 以绕过路径安全检查。

请求载荷（stdin）：

```json
{ "protocolVersion": 1, "provider": "vault", "ids": ["providers/openai/apiKey"] }
```

响应载荷（stdout）：

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

## Exec 集成示例

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

## 受支持的凭据面

标准的受支持与不受支持凭据列表见：

- [SecretRef 凭据面](/reference/secretref-credential-surface)

运行时生成或轮换的凭据，以及 OAuth 刷新材料，有意排除在只读 SecretRef 解析之外。

## 必需行为与优先级

- 字段无引用：保持不变。
- 字段含引用：在激活期间，于活动面上为必需项。
- 若明文与引用同时存在，在支持优先级路径上，引用优先于明文。

警告与审计信号：

- `SECRETS_REF_OVERRIDES_PLAINTEXT`（运行时警告）
- `REF_SHADOWED`（审计发现：当 `auth-profiles.json` 凭据优先于 `openclaw.json` 引用时）

Google Chat 兼容性行为：

- `serviceAccountRef` 优先于明文 `serviceAccount`。
- 当同级引用已设置时，明文值将被忽略。

## 激活触发器

密钥激活在以下时机运行：

- 启动（含预检及最终激活）
- 配置重载热应用路径
- 配置重载重启检查路径
- 通过 `secrets.reload` 手动重载

激活合约：

- 成功则原子交换快照。
- 启动失败则中止网关启动。
- 运行时重载失败则保留上一个已知有效的快照。

## 降级与恢复信号

当系统处于健康状态后，在重载期间激活失败时，OpenClaw 进入密钥降级状态。

一次性系统事件和日志代码：

- `SECRETS_RELOADER_DEGRADED`
- `SECRETS_RELOADER_RECOVERED`

行为：

- 降级（Degraded）：运行时保留最后已知良好的快照。
- 恢复（Recovered）：在下一次成功激活后仅触发一次。
- 在已处于降级状态时重复失败，仅记录警告日志，但不会刷屏式地发出事件。
- 启动阶段的快速失败（fail-fast）不会发出降级事件，因为运行时从未进入活跃状态。

## 命令路径解析

命令路径可通过网关快照 RPC 选择启用受支持的 `SecretRef` 解析功能。

存在两种主要行为：

- 严格型命令路径（例如 `openclaw memory` 远程内存路径和 `openclaw qr --remote`）从活跃快照中读取，并在所需 `SecretRef` 不可用时立即失败。
- 只读型命令路径（例如 `openclaw status`、`openclaw status --all`、`openclaw channels status`、`openclaw channels resolve`，以及只读的 doctor / config 修复流程）也优先使用活跃快照，但在该命令路径中目标 `SecretRef` 不可用时，转为降级模式而非中止执行。

只读型行为：

- 当网关正在运行时，这些命令首先从活跃快照中读取。
- 如果网关解析未完成或网关不可用，则尝试针对特定命令界面进行定向本地回退。
- 若目标 `SecretRef` 仍不可用，命令将继续以降级的只读输出方式执行，并提供明确的诊断信息，例如“已配置但在本命令路径中不可用”。
- 此类降级行为仅限于当前命令本地生效，不会削弱运行时启动、重载或发送/认证路径的功能。

其他说明：

- 后端密钥轮换后的快照刷新由 `openclaw secrets reload` 处理。
- 这些命令路径所使用的网关 RPC 方法为：`secrets.resolve`。

## 审计与配置工作流

默认操作员流程：

```bash
openclaw secrets audit --check
openclaw secrets configure
openclaw secrets audit --check
```

### `secrets audit`

发现项包括：

- 静态明文值（`openclaw.json`、`auth-profiles.json`、`.env` 和生成的 `agents/*/agent/models.json`）
- 生成的 `models.json` 条目中残留的明文敏感提供方请求头
- 未解析的引用（unresolved refs）
- 优先级遮蔽（precedence shadowing）（`auth-profiles.json` 优先级高于 `openclaw.json` 引用）
- 遗留残留项（`auth.json`、OAuth 提醒）

请求头残留说明：

- 敏感提供方请求头检测基于名称启发式（常见认证/凭证请求头名称及片段，例如 `authorization`、`x-api-key`、`token`、`secret`、`password` 和 `credential`）。

### `secrets configure`

交互式辅助工具，可：

- 首先配置 `secrets.providers`（`env`/`file`/`exec`，支持添加/编辑/删除）
- 允许您在 `openclaw.json` 中选择支持密钥承载的字段，并为单个代理作用域额外选择 `auth-profiles.json`
- 可直接在目标选择器中创建新的 `auth-profiles.json` 映射
- 捕获 `SecretRef` 详细信息（`source`、`provider`、`id`）
- 执行预检解析（preflight resolution）
- 可立即应用变更

实用模式：

- `openclaw secrets configure --providers-only`
- `openclaw secrets configure --skip-provider-setup`
- `openclaw secrets configure --agent <id>`

`configure` 应用默认策略：

- 从 `auth-profiles.json` 中清除面向目标提供方的匹配静态凭据
- 清除 `auth.json` 中遗留的静态 `api_key` 条目
- 清除 `<config-dir>/.env` 中匹配的已知密钥行

### `secrets apply`

应用已保存的计划：

```bash
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run
```

有关严格目标/路径契约细节及确切拒绝规则，请参阅：

- [密钥应用计划契约（Secrets Apply Plan Contract）](/gateway/secrets-plan-contract)

## 单向安全策略

OpenClaw 故意不写入包含历史明文密钥值的回滚备份。

安全模型：

- 必须通过预检（preflight）后才进入写入模式
- 提交前需验证运行时是否已激活
- 使用原子文件替换更新文件，并在失败时尽最大努力恢复

## 遗留认证兼容性说明

对于静态凭据，运行时不依赖明文形式的遗留认证存储。

- 运行时凭据来源为已解析的内存中快照。
- 发现遗留静态 `api_key` 条目时将自动清除。
- 与 OAuth 相关的兼容性行为保持独立。

## Web UI 说明

某些 `SecretInput` 联合类型在原始编辑器模式下比表单模式更易于配置。

## 相关文档

- CLI 命令：[密钥（secrets）](/cli/secrets)
- 计划契约详情：[密钥应用计划契约（Secrets Apply Plan Contract）](/gateway/secrets-plan-contract)
- 凭据界面：[SecretRef 凭据界面（SecretRef Credential Surface）](/reference/secretref-credential-surface)
- 认证设置：[认证（Authentication）](/gateway/authentication)
- 安全态势：[安全（Security）](/gateway/security)
- 环境优先级：[环境变量（Environment Variables）](/help/environment)