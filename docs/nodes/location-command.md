---
summary: "Location command for nodes (location.get), permission modes, and Android foreground behavior"
read_when:
  - Adding location node support or permissions UI
  - Designing Android location permissions or foreground behavior
title: "Location Command"
---
# 位置命令（节点）

## 简而言之

- `location.get` 是一个节点命令（通过 `node.invoke`）。
- 默认关闭。
- Android 应用设置使用选择器：关闭 / 使用时允许。
- 独立开关：精确位置。

## 为什么使用选择器（而非单纯开关）

操作系统权限是多层级的。我们可以在应用内暴露一个选择器，但操作系统仍决定实际的授予情况。

- iOS/macOS 可能在系统提示/设置中暴露 **使用时允许** 或 **始终允许**。
- Android 应用目前仅支持前台定位。
- 精确位置是单独的授权（iOS 14+“精确”，Android“精细”与“粗略”）。

UI 中的选择器驱动我们的请求模式；实际授权存在于系统设置中。

## 设置模型

每个节点设备：

- `location.enabledMode`: `off | whileUsing`
- `location.preciseEnabled`: bool

UI 行为：

- 选择 `whileUsing` 请求前台权限。
- 如果操作系统拒绝请求的级别，则回退到最高已授予级别并显示状态。

## 权限映射（node.permissions）

可选。macOS 节点通过权限地图报告 `location`；iOS/Android 可能会省略它。

## 命令：`location.get`

通过 `node.invoke` 调用。

参数（建议）：

```json
{
  "timeoutMs": 10000,
  "maxAgeMs": 15000,
  "desiredAccuracy": "coarse|balanced|precise"
}
```

响应负载：

```json
{
  "lat": 48.20849,
  "lon": 16.37208,
  "accuracyMeters": 12.5,
  "altitudeMeters": 182.0,
  "speedMps": 0.0,
  "headingDeg": 270.0,
  "timestamp": "2026-01-03T12:34:56.000Z",
  "isPrecise": true,
  "source": "gps|wifi|cell|unknown"
}
```

错误（稳定代码）：

- `LOCATION_DISABLED`: 选择器已关闭。
- `LOCATION_PERMISSION_REQUIRED`: 缺少请求模式的权限。
- `LOCATION_BACKGROUND_UNAVAILABLE`: 应用处于后台，但仅允许“使用时允许”。
- `LOCATION_TIMEOUT`: 未能及时获取定位。
- `LOCATION_UNAVAILABLE`: 系统故障 / 无提供者。

## 后台行为

- Android 应用在后台时拒绝 `location.get`。
- 在 Android 上请求位置时，请保持 OpenClaw 打开。
- 其他节点平台可能有所不同。

## 模型/工具集成

- 工具界面：`nodes` 工具添加 `location_get` 操作（需要节点）。
- CLI: `openclaw nodes location get --node <id>`。
- 智能体指南：仅在用户启用位置且了解范围时调用。

## UX 文案（建议）

- 关闭：“位置共享已禁用。”
- 使用时允许：“仅在 OpenClaw 打开时。”
- 精确：“使用精确 GPS 位置。关闭以共享近似位置。”