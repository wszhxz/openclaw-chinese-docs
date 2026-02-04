---
summary: "Menu bar icon states and animations for OpenClaw on macOS"
read_when:
  - Changing menu bar icon behavior
title: "Menu Bar Icon"
---
# 菜单栏图标状态

作者: steipete · 更新日期: 2025-12-06 · 适用范围: macOS 应用 (`apps/macos`)

- **空闲:** 正常图标动画（闪烁，偶尔抖动）。
- **暂停:** 状态项使用 `appearsDisabled`；无动作。
- **语音触发（大耳朵）:** 语音唤醒检测器在听到唤醒词时调用 `AppState.triggerVoiceEars(ttl: nil)`，并在捕获到话语时保持 `earBoostActive=true`。耳朵放大（1.9倍），获得圆形耳洞以提高可读性，然后在1秒的静默后通过 `stopVoiceEars()` 下降。仅从应用内的语音流水线触发。
- **工作（代理运行中）:** `AppState.isWorking=true` 驱动“尾巴/腿快速移动”微动作：工作进行时腿部抖动加快并略有偏移。目前在WebChat代理运行时切换；在连接其他长时间任务时添加相同的切换。

连接点

- 语音唤醒: 运行时/测试器在触发时调用 `AppState.triggerVoiceEars(ttl: nil)`，并在1秒的静默后调用 `stopVoiceEars()` 以匹配捕获窗口。
- 代理活动: 在工作时段设置 `AppStateStore.shared.setWorking(true/false)`（WebChat代理调用中已完成）。保持时段较短，并在 `defer` 块中重置以避免动画卡住。

形状与大小

- 基础图标在 `CritterIconRenderer.makeIcon(blink:legWiggle:earWiggle:earScale:earHoles:)` 中绘制。
- 耳朵缩放默认为 `1.0`；语音增强设置 `earScale=1.9` 并切换 `earHoles=true` 而不改变整体框架（18×18 pt 模板图像渲染为36×36 px Retina 后备存储）。
- 快速移动使用腿部抖动最多达~1.0，并带有轻微水平抖动；它是对任何现有空闲抖动的叠加。

行为说明

- 耳朵/工作没有外部CLI/代理切换；保持内部信号以避免意外波动。
- 保持TTL短暂（<10秒），以便如果作业挂起图标能快速恢复到基线。