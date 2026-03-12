---
summary: "Contract for `secrets apply` plans: target validation, path matching, and `auth-profiles.json` target scope"
read_when:
  - Generating or reviewing `openclaw secrets apply` plans
  - Debugging `Invalid plan target path` errors
  - Understanding target type and path validation behavior
title: "Secrets Apply Plan Contract"
---
# 密钥应用计划契约

本页面定义了 `openclaw secrets apply` 所强制执行的严格契约。

如果某个目标不满足这些规则，则在修改配置之前，应用操作即会失败。

## 计划文件结构

`openclaw secrets apply --from <plan.json>` 期望一个由计划目标组成的 `targets` 数组：

```json5
{
  version: 1,
  protocolVersion: 1,
  targets: [
    {
      type: "models.providers.apiKey",
      path: "models.providers.openai.apiKey",
      pathSegments: ["models", "providers", "openai", "apiKey"],
      providerId: "openai",
      ref: { source: "env", provider: "default", id: "OPENAI_API_KEY" },
    },
    {
      type: "auth-profiles.api_key.key",
      path: "profiles.openai:default.key",
      pathSegments: ["profiles", "openai:default", "key"],
      agentId: "main",
      ref: { source: "env", provider: "default", id: "OPENAI_API_KEY" },
    },
  ],
}
```

## 支持的目标作用域

计划目标仅接受以下支持的凭据路径：

- [SecretRef 凭据面](/reference/secretref-credential-surface)

## 目标类型行为

通用规则：

- `target.type` 必须被识别，且必须与标准化的 `target.path` 结构完全匹配。

为兼容现有计划，以下别名仍被接受：

- `models.providers.apiKey`
- `skills.entries.apiKey`
- `channels.googlechat.serviceAccount`

## 路径验证规则

每个目标均需通过以下全部验证：

- `type` 必须是已被识别的目标类型。
- `path` 必须是非空的点分路径（dot path）。
- `pathSegments` 可省略；若提供，则其标准化后路径必须与 `path` 完全一致。
- 禁止使用以下段：`__proto__`、`prototype`、`constructor`。
- 标准化后的路径必须与该目标类型的已注册路径结构相匹配。
- 若设置了 `providerId` 或 `accountId`，则其值必须与路径中编码的 ID 一致。
- `auth-profiles.json` 类型的目标要求提供 `agentId`。
- 创建新的 `auth-profiles.json` 映射时，须包含 `authProfileProvider`。

## 失败行为

若某个目标验证失败，应用操作将退出并报错，例如：

```text
Invalid plan target path for models.providers.apiKey: models.providers.openai.baseUrl
```

对于无效的计划，不会提交任何写入操作。

## 运行时与审计作用域说明

- 仅引用（ref-only）的 `auth-profiles.json` 条目（即 `keyRef`/`tokenRef`）将纳入运行时解析及审计覆盖范围。
- `secrets apply` 支持写入以下目标：已支持的 `openclaw.json` 目标、已支持的 `auth-profiles.json` 目标，以及可选的脱敏（scrub）目标。

## 运算符检查

```bash
# Validate plan without writes
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run

# Then apply for real
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json
```

若应用操作因目标路径无效而失败，请使用 `openclaw secrets configure` 重新生成计划，或按上述支持的结构修正目标路径。

## 相关文档

- [密钥管理](/gateway/secrets)
- [CLI `secrets`](/cli/secrets)
- [SecretRef 凭据面](/reference/secretref-credential-surface)
- [配置参考](/gateway/configuration-reference)