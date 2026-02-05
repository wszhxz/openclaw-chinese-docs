---
summary: "Menu bar icon states and animations for OpenClaw on macOS"
read_when:
  - Changing menu bar icon behavior
title: "Menu Bar Icon"
---
# 菜单栏图标状态

作者：steipete · 更新时间：2025-12-06 · 范围：macOS 应用 (`apps/macos`)

- **空闲：** 正常图标动画（眨眼，偶尔摇摆）。
- **暂停：** 状态项目使用 `appearsDisabled`；无运动。
- **语音触发（大耳朵）：** 语音唤醒检测器在听到唤醒词时调用 `AppState.triggerVoiceEars(ttl: nil)`，在捕获语音时保持 `earBoostActive=true`。耳朵放大（1.9倍），获得圆形耳洞以提高可读性，然后在静默1秒后通过 `stopVoiceEars()` 恢复。仅从应用内语音管道触发。
- **工作中（代理运行）：** `AppState.isWorking=true` 驱动"尾巴/腿部快速移动"微动作：工作进行时腿部摇摆更快并有轻微偏移。当前在WebChat代理运行期间切换；在连接其他长时间任务时添加相同的切换。

连接点

- 语音唤醒：运行时/测试器在触发时调用 `AppState.triggerVoiceEars(ttl: nil)`，在静默1秒后调用 `stopVoiceEars()` 以匹配捕获窗口。
- 代理活动：在工作时间段周围设置 `AppStateStore.shared.setWorking(true/false)`（已在WebChat代理调用中完成）。保持时间段短并在 `defer` 块中重置以避免动画卡住。

形状和大小

- 基础图标绘制在 `CritterIconRenderer.makeIcon(blink:legWiggle:earWiggle:earScale:earHoles:)` 中。
- 耳朵缩放默认为 `1.0`；语音增强设置 `earScale=1.9` 并切换 `earHoles=true` 而不改变整体框架（18×18 pt模板图像渲染到36×36 px视网膜后备存储中）。
- 快速移动使用腿部摇摆最多约1.0，并带有小水平抖动；它会叠加到任何现有的空闲摇摆上。

行为注意事项

- 没有外部CLI/代理器用于耳朵/工作的切换；将其保留在应用自己的信号内部以避免意外拍打。
- 保持TTL短（&lt;10秒），以便如果作业挂起，图标能快速返回基线。