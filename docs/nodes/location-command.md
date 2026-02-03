---
summary: "Location command for nodes (location.get), permission modes, and background behavior"
read_when:
  - Adding location node support or permissions UI
  - Designing background location + push flows
title: "Location Command"
---
<<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context and the key terms. The document is about location commands in a node system, discussing permissions, settings, and API commands. 

First, I'll note the main sections: TL;DR, Why a selector, Settings model, Permissions mapping, Command: location.get, Background behavior, Model/tooling integration, and UX copy. Each section has specific terminology that needs accurate translation.

For the TL;DR section, terms like "node command" should be translated as "节点命令". The phrase "Off by default" becomes "默认关闭". The settings selector options need to be translated carefully, like "Off / While Using / Always" to "关闭 / 正在使用时 / 始终". The "Precise Location" toggle is "精确位置".

Moving to the "Why a selector" section, terms like "OS permissions" are "操作系统权限". The mention of iOS/macOS and Android specific permissions should be translated with their respective terms. For example, "While Using" becomes "正在使用时", and "Always" is "始终". The "Precise location" part should be "精确位置权限".

In the "Settings model" section, the parameters like "location.enabledMode" and "location.preciseEnabled" need to be translated as "location.enabledMode" and "location.preciseEnabled" since they are technical terms. The UI behavior descriptions should be translated to explain the actions clearly, such as "请求前台权限" for "requests foreground permission".

The "Permissions mapping" section mentions macOS and iOS/Android differences. I'll ensure that terms like "permissions map" are translated accurately, maybe as "权限映射". The note about optional reporting should be clear in Chinese.

For the "Command: location.get" section, the JSON parameters and response payload need to be translated but kept in JSON format. Terms like "timeoutMs" stay as is, but the descriptions should be in Chinese. The error codes like "LOCATION_DISABLED" should be translated with their meanings, such as "位置功能已关闭".

In the "Background behavior" section, terms like "background location" become "后台定位". The future flow steps should be translated step by step, ensuring the sequence is clear. Notes about iOS and Android requirements need precise translation, such as "Always permission + background location mode required" to "始终权限 + 后台定位模式".

The "Model/tooling integration" section has CLI commands and tool surface descriptions. The CLI command "openclaw nodes location get --node <id>" should be translated as "openclaw nodes location get --node <id>" since it's a command line instruction. The agent guidelines mention user consent, so "用户已启用位置并理解范围" is appropriate.

Finally, the "UX copy" section has user-facing text. Each label should be translated to match the intended message, like "Location sharing is disabled." becomes "位置共享已关闭。" and "Allow background location. Requires system permission." becomes "允许后台定位。需要系统权限。"

I need to ensure that technical terms are consistently translated and that the structure of the document is maintained. Also, special attention to JSON keys and error codes to keep them as they are, only translating the surrounding text. Avoiding any markdown formatting and keeping the translation accurate and natural in Chinese.
</think>

# 位置命令（节点）

## TL;DR

- `location.get` 是一个节点命令（通过 `node.invoke` 调用）。
- 默认关闭。
- 设置使用选择器：关闭 / 正在使用时 / 始终。
- 独立开关：精确位置。

## 为何使用选择器（而非仅开关）

操作系统权限是多级的。我们可以在应用内暴露选择器，但操作系统仍决定实际授权。

- iOS/macOS：用户可在系统提示/设置中选择 **正在使用时** 或 **始终**。应用可请求升级权限，但操作系统可能要求进入设置。
- Android：后台定位是独立权限；在 Android 10+ 中通常需要进入设置流程。
- 精确定位是独立授权（iOS 14+ “精确”，Android “精细” vs “粗略”）。

UI 中的选择器驱动我们的请求模式；实际授权存在于操作系统设置中。

## 设置模型

每个节点设备：

- `location.enabledMode`: `off | whileUsing | always`
- `location.preciseEnabled`: 布尔值

UI 行为：

- 选择 `whileUsing` 会请求前台权限。
- 选择 `always` 会首先确保 `while 使用`，然后请求后台（或在需要时引导用户进入设置）。
- 如果操作系统拒绝请求的权限级别，将回退到最高授予的权限并显示状态。

## 权限映射（node.permissions）

可选。macOS 节点通过权限映射报告 `location`；iOS/Android 可能省略该权限。

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

- `LOCATION_DISABLED`: 选择器关闭。
- `LOCATION_PERMISSION_REQUIRED`: 请求模式缺少权限。
- `LOCATION_BACKGROUND_UNAVAILABLE`: 应用在后台但仅允许正在使用时权限。
- `LOCATION_TIMEOUT`: 超时未获取定位。
- `LOCATION_UNAVAILABLE`: 系统故障 / 无定位提供者。

## 后台行为（未来）

目标：模型可在节点后台运行时请求定位，但仅当：

- 用户选择 **始终**。
- 操作系统授予后台定位权限。
- 应用允许在后台运行以获取定位（iOS 后台模式 / Android 前台服务或特殊许可）。

推送触发流程（未来）：

1. 网关向节点发送推送（静默推送或 FCM 数据）。
2. 节点短暂唤醒并从设备请求定位。
3. 节点将负载转发至网关。

注释：

- iOS：始终权限 + 后台定位模式必需。静默推送可能被限速；预期间歇性失败。
- Android：后台定位可能需要前台服务；否则预期被拒绝。

## 模型/工具集成

- 工具界面：`nodes` 工具添加 `location_get` 动作（需节点）。
- CLI：`openclaw nodes location get --node <id>`。
- 代理指南：仅在用户启用定位并理解范围时调用。

## UX 文本（建议）

- 关闭：位置共享已关闭。
- 正在使用时：仅当 OpenClaw 打开时。
- 始终：允许后台定位。需要系统权限。
- 精确：使用精确 GPS 定位。关闭以共享近似位置。