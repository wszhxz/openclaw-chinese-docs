---
summary: "CLI reference for `openclaw secrets` (reload, audit, configure, apply)"
read_when:
  - Re-resolving secret refs at runtime
  - Auditing plaintext residues and unresolved refs
  - Configuring SecretRefs and applying one-way scrub changes
title: "secrets"
---
# `openclaw secrets`

使用 `openclaw secrets` 来管理 SecretRefs 并保持活动运行时快照的健康。

命令角色：

- `reload`: 网关 RPC（`secrets.reload`），仅在完全成功时重新解析引用并交换运行时快照（不写入配置）。
- `audit`: 对配置/认证/生成模型存储及遗留残留进行只读扫描，查找明文、未解析引用和优先级漂移（除非设置 `--allow-exec`，否则跳过执行引用）。
- `configure`: 用于提供者设置、目标映射和预检的交互式规划器（需要 TTY）。
- `apply`: 执行保存的计划（`--dry-run` 仅用于验证；默认情况下 dry-run 跳过执行检查，且 write mode 拒绝包含执行的计划，除非设置 `--allow-exec`），然后清理目标明文残留。

推荐的操作循环：

```bash
openclaw secrets audit --check
openclaw secrets configure
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json
openclaw secrets audit --check
openclaw secrets reload
```

如果您的计划包含 `exec` SecretRefs/提供者，请在 dry-run 和 write apply 命令中都传递 `--allow-exec`。

CI/门禁的退出码说明：

- `audit --check` 在发现问题时返回 `1`。
- 未解析引用返回 `2`。

相关：

- 密钥指南：[密钥管理](/gateway/secrets)
- 凭证表面：[SecretRef 凭证表面](/reference/secretref-credential-surface)
- 安全指南：[安全](/gateway/security)

## 重载运行时快照

重新解析密钥引用并原子性地交换运行时快照。

```bash
openclaw secrets reload
openclaw secrets reload --json
openclaw secrets reload --url ws://127.0.0.1:18789 --token <token>
```

说明：

- 使用网关 RPC 方法 `secrets.reload`。
- 如果解析失败，网关保留最后一个已知良好的快照并返回错误（无部分激活）。
- JSON 响应包含 `warningCount`。

选项：

- `--url <url>`
- `--token <token>`
- `--timeout <ms>`
- `--json`

## 审计

扫描 OpenClaw 状态以查找：

- 明文密钥存储
- 未解析引用
- 优先级漂移（`auth-profiles.json` 凭证遮蔽 `openclaw.json` 引用）
- 生成的 `agents/*/agent/models.json` 残留（提供者 `apiKey` 值和敏感提供者头）
- 遗留残留（遗留认证存储条目、OAuth 提醒）

头残留说明：

- 敏感提供者头检测基于名称启发式（常见的认证/凭证头名称和片段，例如 `authorization`、`x-api-key`、`token`、`secret`、`password` 和 `credential`）。

```bash
openclaw secrets audit
openclaw secrets audit --check
openclaw secrets audit --json
openclaw secrets audit --allow-exec
```

退出行为：

- `--check` 在发现问题时非零退出。
- 未解析引用以更高优先级的非零代码退出。

报告结构重点：

- `status`: `clean | findings | unresolved`
- `resolution`: `refsChecked`、`skippedExecRefs`、`resolvabilityComplete`
- `summary`: `plaintextCount`、`unresolvedRefCount`、`shadowedRefCount`、`legacyResidueCount`
- 发现代码：
  - `PLAINTEXT_FOUND`
  - `REF_UNRESOLVED`
  - `REF_SHADOWED`
  - `LEGACY_RESIDUE`

## 配置（交互式助手）

交互式构建提供者和 SecretRef 更改，运行预检，并可选择应用：

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

- 首先设置提供者（`add/edit/remove` 用于 `secrets.providers` 别名）。
- 其次映射凭证（选择字段并分配 `{source, provider, id}` 引用）。
- 最后进行预检和可选的应用。

标志：

- `--providers-only`: 仅配置 `secrets.providers`，跳过凭证映射。
- `--skip-provider-setup`: 跳过提供者设置并将凭证映射到现有提供者。
- `--agent <id>`: 将 `auth-profiles.json` 目标发现和写入范围限定为一个代理存储。
- `--allow-exec`: 允许在预检/应用期间执行 SecretRef 检查（可能会执行提供者命令）。

说明：

- 需要交互式 TTY。
- 您不能将 `--providers-only` 与 `--skip-provider-setup` 结合使用。
- `configure` 针对 `openclaw.json` 中包含密钥的字段以及选定代理范围的 `auth-profiles.json`。
- `configure` 支持在选择器流程中直接创建新的 `auth-profiles.json` 映射。
- 标准支持表面：[SecretRef 凭证表面](/reference/secretref-credential-surface)。
- 它在应用前执行预检解析。
- 如果预检/应用包含执行引用，请为两个步骤都保持 `--allow-exec` 设置。
- 生成的计划默认为清理选项（`scrubEnv`、`scrubAuthProfilesForProviderTargets`、`scrubLegacyAuthJson` 全部启用）。
- 应用路径对于已清理的明文值是不可逆的。
- 没有 `--apply`，CLI 在预检后仍会提示 `Apply this plan now?`。
- 带有 `--apply`（且无 `--yes`），CLI 会提示额外的不可逆确认。
- `--json` 打印计划 + 预检报告，但命令仍然需要交互式 TTY。

执行提供者安全说明：

- Homebrew 安装通常会在 `/opt/homebrew/bin/*` 下暴露符号链接的二进制文件。
- 仅在可信包管理器路径需要时设置 `allowSymlinkCommand: true`，并将其与 `trustedDirs` 配对（例如 `["/opt/homebrew"]`）。
- 在 Windows 上，如果无法对提供者路径进行 ACL 验证，OpenClaw 将故障关闭。仅限可信路径，在该提供者上设置 `allowInsecurePath: true` 以绕过路径安全检查。

## 应用保存的计划

应用或预检先前生成的计划：

```bash
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --allow-exec
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run --allow-exec
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --json
```

执行行为：

- `--dry-run` 在不写入文件的情况下验证预检。
- 默认情况下，dry-run 跳过 exec SecretRef 检查。
- write mode 拒绝包含 exec SecretRefs/提供者的计划，除非设置 `--allow-exec`。
- 使用 `--allow-exec` 在任一模式下选择加入 exec 提供者检查/执行。

计划合约详情（允许的目标路径、验证规则和失败语义）：

- [密钥应用计划合约](/gateway/secrets-plan-contract)

`apply` 可能更新的内容：

- `openclaw.json`（SecretRef 目标 + 提供者 upserts/deletes）
- `auth-profiles.json`（提供者 - 目标清理）
- 遗留 `auth.json` 残留
- `~/.openclaw/.env` 已知密钥，其值已迁移

## 为何没有回滚备份

`secrets apply` 有意不写入包含旧明文值的回滚备份。

安全性来自严格的预检 + 类原子应用，并在失败时尽力进行内存恢复。

## 示例

```bash
openclaw secrets audit --check
openclaw secrets configure
openclaw secrets audit --check
```

如果 `audit --check` 仍报告明文发现，请更新剩余的报告目标路径并重新运行审计。