---
summary: "Menu bar icon states and animations for OpenClaw on macOS"
read_when:
  - Changing menu bar icon behavior
title: "Menu Bar Icon"
---
# 菜单栏图标状态

作者：steipete · 更新时间：2025-12-06 · 范围：macOS 应用程序（`apps/macos`）

- **空闲：** 正常图标动画（闪烁，偶尔抖动）。
- **暂停：** 状态项使用 `appearsDisabled`；无运动。
- **语音触发（大耳朵）：** 语音唤醒检测器在听到唤醒词时调用 `AppState.triggerVoiceEars(ttl: nil)`，在捕获语音时保持 `earBoostActive=true`。耳朵放大（1.9倍），出现圆形耳孔以提高可读性，然后在1秒静默后通过 `stopVoiceEars()` 恢复。仅由应用内语音管道触发。
- **工作中（代理运行）：** `AppState.isWorking=true` 驱动“尾巴/腿快速移动”的微动画：工作进行时腿抖动更快且有轻微偏移。目前在 WebChat 代理运行时切换；在连接其他长时间任务时，也请在相应位置添加相同切换。

连接点

- **语音唤醒：** 运行时/测试者在触发时调用 `AppState.triggerVoiceEars(ttl: nil)`，并在1秒静默后调用 `stopVoiceEars()` 以匹配捕获窗口。
- **代理活动：** 在工作时间段内设置 `AppStateStore.shared.setWorking(true/false)`（WebChat 代理调用中已实现）。保持时间段短，并在 `defer` 块中重置以避免卡顿动画。

形状与尺寸

- **基础图标绘制在 `CritterIconRenderer.makeIcon(blink:legWiggle:earWiggle:earScale:earHoles:)`。**
- **耳朵缩放默认为 `1.0`；语音增强将 `earScale=1.9` 并切换 `earHoles=true`，不改变整体框架（18×18 pt 模板图像渲染至 36×36 px Retina 背板存储）。**
- **快速移动使用腿抖动至约 1.0，并带有轻微水平抖动；此动作叠加在任何现有空闲抖动上。**

行为说明

- **无外部 CLI/broker 切换耳朵/工作状态；保持在应用自身信号内部以避免意外切换。**
- **保持 TTL 短（<10 秒），以防任务卡顿时图标快速返回基准状态。**