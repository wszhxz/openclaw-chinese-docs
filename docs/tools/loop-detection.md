---
title: "Tool-loop detection"
description: "Configure optional guardrails for preventing repetitive or stalled tool-call loops"
read_when:
  - A user reports agents getting stuck repeating tool calls
  - You need to tune repetitive-call protection
  - You are editing agent tool/runtime policies
---
# 工具循环检测

OpenClaw 可以防止代理陷入重复的工具调用模式。
该保护机制默认是**禁用**的。

仅在需要时启用它，因为严格的设置可能会阻止合法的重复调用。

## 为什么存在这个功能

- 检测没有进展的重复序列。
- 检测高频无结果循环（相同的工具，相同的输入，重复的错误）。
- 检测已知轮询工具的特定重复调用模式。

## 配置块

全局默认值：

```json5
{
  tools: {
    loopDetection: {
      enabled: false,
      historySize: 20,
      detectorCooldownMs: 12000,
      repeatThreshold: 3,
      criticalThreshold: 6,
      detectors: {
        repeatedFailure: true,
        knownPollLoop: true,
        repeatingNoProgress: true,
      },
    },
  },
}
```

每个代理的覆盖配置（可选）：

```json5
{
  agents: {
    list: [
      {
        id: "safe-runner",
        tools: {
          loopDetection: {
            enabled: true,
            repeatThreshold: 2,
            criticalThreshold: 5,
          },
        },
      },
    ],
  },
}
```

### 字段行为

- `enabled`: 主开关。`false` 表示不进行循环检测。
- `historySize`: 用于分析的最近工具调用数量。
- `detectorCooldownMs`: 无进展检测器使用的时间窗口。
- `repeatThreshold`: 开始警告/阻止之前的最小重复次数。
- `criticalThreshold`: 可触发更严格处理的更强阈值。
- `detectors.repeatedFailure`: 检测同一调用路径上的重复失败尝试。
- `detectors.knownPollLoop`: 检测已知的类似轮询的循环。
- `detectors.repeatingNoProgress`: 检测状态未变化的高频重复调用。

## 推荐设置

- 从 `enabled: true` 开始，保持默认值不变。
- 如果出现误报：
  - 提高 `repeatThreshold` 和/或 `criticalThreshold`
  - 仅禁用导致问题的检测器
  - 减少 `historySize` 以减少历史上下文的严格性

## 日志和预期行为

当检测到循环时，OpenClaw 报告一个循环事件，并根据严重程度阻止或抑制下一个工具周期。
这可以保护用户免受失控的令牌消耗和锁定，同时保留正常的工具访问。

- 首先优先警告和临时抑制。
- 仅在积累多次证据时升级。

## 注意事项

- `tools.loopDetection` 与代理级别的覆盖配置合并。
- 每个代理的配置完全覆盖或扩展全局值。
- 如果没有配置，防护措施保持关闭。