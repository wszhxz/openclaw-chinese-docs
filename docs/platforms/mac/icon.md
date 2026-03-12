---
summary: "Menu bar icon states and animations for OpenClaw on macOS"
read_when:
  - Changing menu bar icon behavior
title: "Menu Bar Icon"
---
# 菜单栏图标状态

作者: steipete · 更新日期: 2025-12-06 · 范围: macOS 应用 (`apps/macos`)

- **空闲:** 正常图标动画（闪烁，偶尔摆动）。
- **暂停:** 状态项使用 `appearsDisabled`; 无动作。
- **语音触发（大耳朵）:** 当听到唤醒词时，语音唤醒检测器调用 `AppState.triggerVoiceEars(ttl: nil)`，在捕捉到话语期间保持 `earBoostActive=true`。耳朵放大（1.9倍），获得圆形耳孔以提高可读性，然后在1秒静默后通过 `stopVoiceEars()` 下降。仅从应用内的语音管道触发。
- **工作（代理运行中）:** `AppState.isWorking=true` 驱动“尾巴/腿快速移动”微动：更快的腿部摆动和轻微偏移，同时工作正在进行。目前在WebChat代理运行时切换；在连接其他长时间任务时添加相同的切换。

连接点

- 语音唤醒: 运行时/测试器在触发时调用 `AppState.triggerVoiceEars(ttl: nil)`，并在1秒静默后调用 `stopVoiceEars()` 以匹配捕捉窗口。
- 代理活动: 在工作跨度周围设置 `AppStateStore.shared.setWorking(true/false)`（已在WebChat代理调用中完成）。保持跨度简短，并在 `defer` 块中重置，以避免动画卡住。

形状与尺寸

- 基础图标绘制在 `CritterIconRenderer.makeIcon(blink:legWiggle:earWiggle:earScale:earHoles:)` 中。
- 耳朵缩放默认为 `1.0`; 语音增强设置为 `earScale=1.9` 并切换 `earHoles=true`，而不改变整体框架（18×18 pt 模板图像渲染到36×36 px Retina 后备存储）。
- 快速移动使用腿部摆动至约1.0，并带有小幅度水平抖动；它会叠加到任何现有的空闲摆动上。

行为说明

- 没有外部CLI/代理切换耳朵/工作状态；保持其内部信号，以避免意外摆动。
- 保持TTL较短（<10s），以便在任务挂起时图标能迅速返回基线。