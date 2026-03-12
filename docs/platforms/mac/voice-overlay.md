---
summary: "Voice overlay lifecycle when wake-word and push-to-talk overlap"
read_when:
  - Adjusting voice overlay behavior
title: "Voice Overlay"
---
# 语音叠加层生命周期 (macOS)

受众：macOS 应用贡献者。目标：在唤醒词和按住说话重叠时保持语音叠加层的可预测性。

## 当前意图

- 如果叠加层已经因唤醒词而可见，用户按下热键时，热键会话将“采用”现有的文本而不是重置它。当热键被按住时，叠加层保持显示状态。当用户释放热键时：如果有修剪过的文本则发送，否则关闭。
- 单独使用唤醒词仍然会在静音时自动发送；按住说话在释放时立即发送。

## 已实现（2025年12月9日）

- 叠加层会话现在为每次捕获（唤醒词或按住说话）携带一个令牌。当令牌不匹配时，部分/最终/发送/关闭/级别更新将被丢弃，从而避免陈旧的回调。
- 按住说话采用任何可见的叠加层文本作为前缀（因此在唤醒叠加层显示时按下热键会保留文本并追加新的语音）。它最多等待1.5秒以获取最终转录，如果未获取到则回退到当前文本。
- 提示音/叠加层日志在`info`中发出，在类别`voicewake.overlay`、`voicewake.ptt`和`voicewake.chime`中（会话开始、部分、最终、发送、关闭、提示音原因）。

## 下一步

1. **VoiceSessionCoordinator (actor)**
   - 同一时间拥有恰好一个`VoiceSession`。
   - API（基于令牌）：`beginWakeCapture`, `beginPushToTalk`, `updatePartial`, `endCapture`, `cancel`, `applyCooldown`。
   - 丢弃携带陈旧令牌的回调（防止旧的识别器重新打开叠加层）。
2. **VoiceSession (模型)**
   - 字段：`token`, `source` (wakeWord|pushToTalk), committed/volatile text, chime flags, timers (auto-send, idle), `overlayMode` (display|editing|sending), cooldown deadline。
3. **叠加层绑定**
   - `VoiceSessionPublisher` (`ObservableObject`) 将活动会话镜像到SwiftUI。
   - `VoiceWakeOverlayView` 仅通过发布者渲染；它从不直接修改全局单例。
   - 叠加层用户操作(`sendNow`, `dismiss`, `edit`) 使用会话令牌回调协调器。
4. **统一发送路径**
   - 在`endCapture`: 如果修剪后的文本为空 → 关闭；否则`performSend(session:)`（播放一次发送提示音，转发，关闭）。
   - 按住说话：无延迟；唤醒词：可选延迟用于自动发送。
   - 在按住说话结束后对唤醒运行时应用短暂冷却期，以防止唤醒词立即重新触发。
5. **日志记录**
   - 协调器在子系统`ai.openclaw`中发出`.info`日志，类别为`voicewake.overlay`和`voicewake.chime`。
   - 关键事件：`session_started`, `adopted_by_push_to_talk`, `partial`, `finalized`, `send`, `dismiss`, `cancel`, `cooldown`。

## 调试检查清单

- 在重现粘滞叠加层时流式传输日志：

  ```bash
  sudo log stream --predicate 'subsystem == "ai.openclaw" AND category CONTAINS "voicewake"' --level info --style compact
  ```

- 确认只有一个活动会话令牌；陈旧的回调应由协调器丢弃。
- 确保按住说话释放总是使用活动令牌调用`endCapture`；如果文本为空，则期望`dismiss`而不带提示音或发送。

## 迁移步骤（建议）

1. 添加`VoiceSessionCoordinator`, `VoiceSession`, 和 `VoiceSessionPublisher`。
2. 重构`VoiceWakeRuntime` 以创建/更新/结束会话，而不是直接修改`VoiceWakeOverlayController`。
3. 重构`VoicePushToTalk` 以采用现有会话并在释放时调用`endCapture`；应用运行时冷却。
4. 将`VoiceWakeOverlayController` 连接到发布者；从运行时/PTT 中移除直接调用。
5. 为会话采用、冷却和空文本关闭添加集成测试。