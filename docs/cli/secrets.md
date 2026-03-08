---
summary: "CLI reference for `openclaw secrets` (reload, audit, configure, apply)"
read_when:
  - Re-resolving secret refs at runtime
  - Auditing plaintext residues and unresolved refs
  - Configuring SecretRefs and applying one-way scrub changes
title: "secrets"
---
# `openclaw secrets`

使用 `openclaw secrets` 管理 SecretRefs，并维持活跃运行时快照的健康状态。

命令角色：

- `reload`：网关 RPC（`secrets.reload`），重新解析引用并在完全成功时原子化切换运行时快照（不执行任何配置写入）。
- `audit`：对配置/认证/生成模型存储以及遗留残留物进行只读扫描，检测明文凭据、未解析的引用及优先级偏移。
- `configure`：用于提供方设置、目标映射和预检的交互式规划器（需 TTY）。
- `apply`：执行已保存的计划（仅用 `--dry-run` 进行验证），随后清理指定的明文残留项。

推荐的运维循环：

```bash
openclaw secrets audit --check
openclaw secrets configure
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json
openclaw secrets audit --check
openclaw secrets reload
```

CI/门禁场景下的退出码说明：

- `audit --check` 在发现异常时返回 `1`。
- 未解析的引用返回 `2`。

相关文档：

- 密钥指南：[密钥管理](/gateway/secrets)  
- 凭据表面：[SecretRef 凭据表面](/reference/secretref-credential-surface)  
- 安全指南：[安全](/gateway/security)

## 重载运行时快照

重新解析密钥引用，并原子化地切换运行时快照。

```bash
openclaw secrets reload
openclaw secrets reload --json
```

注意事项：

- 使用网关 RPC 方法 `secrets.reload`。
- 若解析失败，网关将保留上一个已知可用的快照并返回错误（不支持部分激活）。
- JSON 响应中包含 `warningCount`。

## 审计

扫描 OpenClaw 状态，检查以下内容：

- 明文密钥存储  
- 未解析的引用  
- 优先级偏移（`auth-profiles.json` 凭据覆盖 `openclaw.json` 引用）  
- 生成的 `agents/*/agent/models.json` 残留项（提供方的 `apiKey` 值及敏感提供方请求头）  
- 遗留残留项（旧版认证存储条目、OAuth 提醒）

请求头残留说明：

- 敏感提供方请求头检测基于名称启发式（常见认证/凭据请求头名称及片段，例如 `authorization`、`x-api-key`、`token`、`secret`、`password` 和 `credential`）。

```bash
openclaw secrets audit
openclaw secrets audit --check
openclaw secrets audit --json
```

退出行为：

- `--check` 在发现异常时以非零退出码退出。  
- 未解析的引用将以更高优先级的非零退出码退出。

报告结构重点：

- `status`：`clean | findings | unresolved`  
- `summary`：`plaintextCount`、`unresolvedRefCount`、`shadowedRefCount`、`legacyResidueCount`  
- 发现代码：  
  - `PLAINTEXT_FOUND`  
  - `REF_UNRESOLVED`  
  - `REF_SHADOWED`  
  - `LEGACY_RESIDUE`  

## 配置（交互式辅助工具）

以交互方式构建提供方与 SecretRef 的变更，运行预检，并可选执行应用：

```bash
openclaw secrets configure
openclaw secrets configure --plan-out /tmp/openclaw-secrets-plan.json
openclaw secrets configure --apply --yes
openclaw secrets configure --providers-only
openclaw secrets configure --skip-provider-setup
openclaw secrets configure --agent ops
openclaw secrets configure --json
```

流程：

- 首先进行提供方设置（`add/edit/remove` 支持 `secrets.providers` 别名）。  
- 其次进行凭据映射（选择字段并分配 `{source, provider, id}` 引用）。  
- 最后执行预检及可选的应用操作。

标志参数：

- `--providers-only`：仅配置 `secrets.providers`，跳过凭据映射。  
- `--skip-provider-setup`：跳过提供方设置，直接将凭据映射至现有提供方。  
- `--agent <id>`：将 `auth-profiles.json` 目标发现与写入范围限定于单个代理存储。

注意事项：

- 需要交互式 TTY。  
- 不可同时使用 `--providers-only` 与 `--skip-provider-setup`。  
- `configure` 支持在选择器流程中直接创建新的 `auth-profiles.json` 映射。  
- `configure` 针对所选代理作用域内的 `openclaw.json` 中承载密钥的字段，以及 `auth-profiles.json`。  
- 规范支持的表面：[SecretRef 凭据表面](/reference/secretref-credential-surface)。  
- 应用前会执行预检解析。  
- 生成的计划默认启用清理选项（`scrubEnv`、`scrubAuthProfilesForProviderTargets`、`scrubLegacyAuthJson` 均启用）。  
- 对已清理的明文值，应用路径为单向不可逆。  
- 若未指定 `--apply`，CLI 仍会在预检后提示 `Apply this plan now?`。  
- 若指定 `--apply`（且未指定 `--yes`），CLI 将额外提示一次不可逆确认。

执行提供方安全说明：

- Homebrew 安装通常会在 `/opt/homebrew/bin/*` 下暴露符号链接的二进制文件。  
- 仅当确需信任包管理器路径时才设置 `allowSymlinkCommand: true`，并务必配合 `trustedDirs`（例如 `["/opt/homebrew"]`）。  
- 在 Windows 上，若某提供方路径无法执行 ACL 验证，OpenClaw 将采取“拒绝即关闭”策略；仅对可信路径，可在该提供方上设置 `allowInsecurePath: true` 以绕过路径安全检查。

## 应用已保存的计划

应用或预检先前生成的计划：

```bash
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --json
```

计划契约详情（允许的目标路径、验证规则及失败语义）：

- [密钥应用计划契约](/gateway/secrets-plan-contract)

`apply` 可能更新的内容：

- `openclaw.json`（SecretRef 目标 + 提供方增删）  
- `auth-profiles.json`（提供方-目标清理）  
- 遗留的 `auth.json` 残留项  
- `~/.openclaw/.env` 中已迁移值的已知密钥  

## 为何不提供回滚备份

`secrets apply` 故意不写入包含旧明文值的回滚备份。

安全性来源于严格的预检 + 类原子性应用，以及失败时尽最大努力在内存中恢复。

## 示例

```bash
openclaw secrets audit --check
openclaw secrets configure
openclaw secrets audit --check
```

若 `audit --check` 仍报告明文问题，请更新剩余报告的目标路径并重新运行审计。