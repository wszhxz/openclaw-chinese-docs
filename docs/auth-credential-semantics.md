# 认证凭据语义

本文档定义了以下各项中使用的标准凭据资格判定与解析语义：

- `resolveAuthProfileOrder`
- `resolveApiKeyForProfile`
- `models status --probe`
- `doctor-auth`

目标是保持选择时（selection-time）与运行时（runtime）行为的一致性。

## 稳定的原因代码（Reason Codes）

- `ok`
- `missing_credential`
- `invalid_expires`
- `expired`
- `unresolved_ref`

## Token 凭据

Token 凭据（`type: "token"`）支持内联的 `token` 和/或 `tokenRef`。

### 资格判定规则

1. 当 `token` 和 `tokenRef` 均缺失时，该 Token 配置文件不具备资格。
2. `expires` 是可选的。
3. 若存在 `expires`，其值必须为大于 `0` 的有限数值。
4. 若 `expires` 无效（即为 `NaN`、`0`、负数、非有限值或类型错误），则该配置文件不具备资格，并返回原因码 `invalid_expires`。
5. 若 `expires` 已过期（即早于当前时间），则该配置文件不具备资格，并返回原因码 `expired`。
6. `tokenRef` 不会绕过 `expires` 的验证。

### 解析规则

1. 解析器语义与 `expires` 的资格判定语义一致。
2. 对于具备资格的配置文件，Token 内容可从内联值或 `tokenRef` 中解析获得。
3. 无法解析的引用将在 `models status --probe` 输出中生成 `unresolved_ref`。

## 向后兼容的消息格式

为保证脚本兼容性，探测错误需保持首行不变：

`Auth profile credentials are missing or expired.`

后续行中可添加面向用户的友好说明及稳定的原因代码。