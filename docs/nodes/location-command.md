---
summary: "Location command for nodes (location.get), permission modes, and background behavior"
read_when:
  - Adding location node support or permissions UI
  - Designing background location + push flows
title: "Location Command"
---
# 位置命令（节点）

## 快速概览

- `location.get` 是一个节点命令（通过 `node.invoke` 调用）。
- 默认关闭。
- 设置项使用选择器：关闭 / 使用中 / 始终启用。
- 独立开关：精确位置。

## 为何采用选择器（而非简单开关）

操作系统权限具有多级结构。我们可在应用内暴露选择器，但实际授权仍由操作系统决定。

- iOS/macOS：用户可在系统提示或设置中选择 **使用中** 或 **始终启用**。应用可请求升级权限，但操作系统可能要求用户手动进入设置。
- Android：后台位置权限是独立的；在 Android 10 及更高版本中，通常需引导用户进入系统设置流程。
- 精确位置是单独授予的权限（iOS 14+ 的“精确”选项，Android 的“精细”与“粗略”定位）。

UI 中的选择器决定我们向系统请求的模式；而实际获得的权限则存在于操作系统设置中。

## 设置模型

每个节点设备：

- `location.enabledMode`: `off | whileUsing | always`
- `location.preciseEnabled`: bool

UI 行为：

- 选择 `whileUsing` 将请求前台权限。
- 选择 `always` 时，首先确保已启用 `whileUsing`，然后请求后台权限（若系统要求，则跳转至设置页面）。
- 若操作系统拒绝所请求的权限级别，则自动回退至当前已授予的最高级别，并显示状态提示。

## 权限映射（node.permissions）

可选。macOS 节点通过权限映射报告 `location`；iOS/Android 可能不提供该字段。

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

响应载荷：

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

错误（稳定错误码）：

- `LOCATION_DISABLED`：选择器处于关闭状态。
- `LOCATION_PERMISSION_REQUIRED`：所请求模式缺少必要权限。
- `LOCATION_BACKGROUND_UNAVAILABLE`：应用处于后台，但仅允许“使用中”模式。
- `LOCATION_TIMEOUT`：未能及时完成修复。
- `LOCATION_UNAVAILABLE`：系统故障 / 无可用定位服务提供者。

## 后台行为（未来规划）

目标：模型即使在节点处于后台时也能请求位置信息，但仅限于以下条件同时满足时：

- 用户已选择 **始终启用**。
- 操作系统已授予后台定位权限。
- 应用被允许在后台运行以获取位置（iOS 的后台模式 / Android 的前台服务或特殊许可）。

推送触发流程（未来规划）：

1. 网关向节点发送推送（静默推送或 FCM 数据消息）。
2. 节点短暂唤醒，并从设备请求位置信息。
3. 节点将获取到的载荷转发至网关。

注意事项：

- iOS：需同时具备“始终启用”权限及后台定位模式。静默推送可能受限；可能出现间歇性失败。
- Android：后台定位可能需要前台服务；否则将被拒绝。

## 模型/工具集成

- 工具界面：`nodes` 工具新增 `location_get` 动作（需指定节点）。
- CLI：`openclaw nodes location get --node <id>`。
- 智能体指南：仅当用户已启用位置功能并理解其作用范围时调用。

## 用户体验文案（建议）

- 关闭： “位置共享已禁用。”
- 使用中： “仅当 OpenClaw 处于打开状态时。”
- 始终启用： “允许后台定位。需系统授权。”
- 精确位置： “使用精确的 GPS 定位。关闭此选项后将仅共享大致位置。”