---
title: "Auth Credential Semantics"
summary: "Canonical credential eligibility and resolution semantics for auth profiles"
read_when:
  - Working on auth profile resolution or credential routing
  - Debugging model auth failures or profile order
---
# 认证凭证语义

本文档定义了跨以下系统使用的标准凭证资格和解析语义：

- `resolveAuthProfileOrder`
- `resolveApiKeyForProfile`
- `models status --probe`
- `doctor-auth`

目标是保持选择时和运行时行为一致。

## 稳定的探测原因代码

- `ok`
- `excluded_by_auth_order`
- `missing_credential`
- `invalid_expires`
- `expired`
- `unresolved_ref`
- `no_model`

## 令牌凭证

令牌凭证 (`type: "token"`) 支持内联 `token` 和/或 `tokenRef`。

### 资格规则

1. 当 `token` 和 `tokenRef` 均缺失时，令牌配置档案不合格。
2. `expires` 是可选的。
3. 如果 `expires` 存在，它必须是一个大于 `0` 的有限数字。
4. 如果 `expires` 无效（`NaN`、`0`、负数、非有限值或类型错误），则该配置档案不合格，并带有 `invalid_expires`。
5. 如果 `expires` 在过去，则该配置档案不合格，并带有 `expired`。
6. `tokenRef` 不会绕过 `expires` 验证。

### 解析规则

1. 解析器语义与 `expires` 的资格语义匹配。
2. 对于合格的配置档案，令牌数据可从内联值或 `tokenRef` 解析。
3. 无法解析的引用会在 `models status --probe` 输出中产生 `unresolved_ref`。

## 显式认证顺序过滤

- 当 `auth.order.<provider>` 或为某提供者的 auth-store 顺序覆盖被设置时，`models status --probe` 仅探测该提供者已解析认证顺序中剩余的 profile ids。
- 对于该提供者，若存储的配置档案未包含在显式顺序中，则不会随后静默尝试。探测输出会以 `reasonCode: excluded_by_auth_order` 报告它，并附带详情 `Excluded by auth.order for this provider.`。

## 探测目标解析

- 探测目标可以来自认证配置档案、环境变量凭证或 `models.json`。
- 如果某提供者有凭证但 OpenClaw 无法为其解析可探测的模型候选项，`models status --probe` 将报告 `status: no_model`，并附带 `reasonCode: no_model`。

## OAuth SecretRef 策略守卫

- SecretRef 输入仅用于静态凭证。
- 如果某配置档案凭证是 `type: "oauth"`，则不支持该配置档案凭证数据的 SecretRef 对象。
- 如果 `auth.profiles.<id>.mode` 是 `"oauth"`，则该配置档案的 SecretRef 支持的 `keyRef`/`tokenRef` 输入将被拒绝。
- 违规情况在启动/重载认证解析路径中会导致硬性失败。

## 向后兼容的消息传递

为了脚本兼容性，探测错误保留此第一行不变：

`Auth profile credentials are missing or expired.`

后续行可添加用户友好的详情和稳定的原因代码。