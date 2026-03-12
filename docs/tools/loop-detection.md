---
title: "Tool-loop detection"
description: "Configure optional guardrails for preventing repetitive or stalled tool-call loops"
summary: "How to enable and tune guardrails that detect repetitive tool-call loops"
read_when:
  - A user reports agents getting stuck repeating tool calls
  - You need to tune repetitive-call protection
  - You are editing agent tool/runtime policies
---
# 工具循环检测

OpenClaw 可以防止代理陷入重复的工具调用模式。该保护默认是**禁用的**。

仅在需要时启用它，因为严格的设置可能会阻止合法的重复调用。

## 为什么存在这个功能

- 检测不产生进展的重复序列。
- 检测高频率无结果循环（相同的工具、相同的输入、重复的错误）。
- 检测已知轮询工具的特定重复调用模式。

## 配置块

全局默认值：

```json5
{
  tools: {
    loopDetection: {
      enabled: false,
      historySize: 30,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
      detectors: {
        genericRepeat: true,
        knownPollNoProgress: true,
        pingPong: true,
      },
    },
  },
}
```

每个代理的覆盖（可选）：

```json5
{
  agents: {
    list: [
      {
        id: "safe-runner",
        tools: {
          loopDetection: {
            enabled: true,
            warningThreshold: 8,
            criticalThreshold: 16,
          },
        },
      },
    ],
  },
}
```

### 字段行为

- `enabled`: 主开关。`false` 表示不执行循环检测。
- `historySize`: 用于分析的最近工具调用数量。
- `warningThreshold`: 在将模式分类为仅警告之前的阈值。
- `criticalThreshold`: 阻止重复循环模式的阈值。
- `globalCircuitBreakerThreshold`: 全局无进展中断器阈值。
- `detectors.genericRepeat`: 检测重复的相同工具+相同参数模式。
- `detectors.knownPollNoProgress`: 检测没有状态变化的已知类似轮询模式。
- `detectors.pingPong`: 检测交替的乒乓模式。

## 推荐设置

- 从`enabled: true`开始，保持默认值不变。
- 保持阈值顺序为`warningThreshold < criticalThreshold < globalCircuitBreakerThreshold`。
- 如果出现误报：
  - 提高`warningThreshold`和/或`criticalThreshold`
  - （可选）提高`globalCircuitBreakerThreshold`
  - 仅禁用引起问题的检测器
  - 减少`historySize`以降低历史上下文的严格性

## 日志和预期行为

当检测到循环时，OpenClaw 会报告一个循环事件，并根据严重程度阻塞或抑制下一个工具周期。这可以保护用户免受失控的令牌支出和锁定，同时保留正常的工具访问。

- 优先选择警告和临时抑制。
- 仅在累积了重复证据时才升级处理。

## 注意事项

- `tools.loopDetection` 与代理级别的覆盖合并。
- 每个代理的配置完全覆盖或扩展全局值。
- 如果不存在配置，则护栏保持关闭。