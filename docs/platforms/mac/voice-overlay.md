---
summary: "Voice overlay lifecycle when wake-word and push-to-talk overlap"
read_when:
  - Adjusting voice overlay behavior
title: "Voice Overlay"
---
# 语音叠加生命周期 (macOS)

受众：macOS 应用贡献者。目标：在唤醒词和按键说话重叠时保持语音叠加的可预测性。

### 当前意图

- 如果叠加已经因为唤醒词而可见，并且用户按下了热键，热键会话会_采用_现有文本而不是重置它。叠加会在热键被按住时保持显示。当用户释放热键时：如果有修剪后的文本则发送，否则关闭。
- 单独使用唤醒词仍然会在沉默时自动发送；按键说话在释放时立即发送。

### 已实现（2025年12月9日）

- 叠加会话现在每个捕获（唤醒词或按键说话）携带一个令牌。当令牌不匹配时，丢弃部分/最终/发送/关闭/级别更新，避免过时的回调。
- 按键说话会采用任何可见的叠加文本作为前缀（因此在唤醒叠加显示时按下热键会保留文本并附加新的语音）。它最多等待1.5秒以获取最终的转录，否则回退到当前文本。
- 铃声/叠加日志在`info`中以类别`voicewake.overlay`、`voicewake.ptt`和`voicewake.chime`（会话开始、部分、最终、发送、关闭、铃声原因）发出。

### 下一步计划

1. **VoiceSessionCoordinator (actor)**
   - 同时只拥有一个`VoiceSession`。
   - API（基于令牌）：`beginWakeCapture`、`beginPushToTalk`、`updatePartial`、`endCapture`、`cancel`、`applyCooldown`。
   - 丢弃携带过时令牌的回调（防止旧的识别器重新打开叠加）。
2. **VoiceSession (model)**
   - 字段：`token`、`source`（wakeWord|pushToTalk），已提交/易失性文本，铃声标志，计时器（自动发送、空闲），`overlayMode`（display|editing|sending），冷却截止时间。
3. **叠加绑定**
   - `VoiceSessionPublisher` (`ObservableObject`) 将活动会话镜像到 SwiftUI。
   - `VoiceWakeOverlayView` 仅通过发布者渲染；它从不直接修改全局单例。
   - 叠加用户操作 (`sendNow`、`dismiss`、`edit`) 调用协调器并传入会话令牌。
4. **统一发送路径**
   - 在`endCapture`：如果修剪后的文本为空 → 关闭；否则 `performSend(session:)`（播放发送铃声一次，转发，关闭）。
   - 按键说话：无延迟；唤醒词：可选延迟用于自动发送。
   - 在按键说话结束后对唤醒运行时应用短暂的冷却，以防止唤醒词立即重新触发。
5. **日志记录**
   - 协调器在子系统 `bot.molt` 中发出 `.info` 日志，类别 `voicewake.overlay` 和 `voicewake.chime`。
   - 关键事件：`session_started`、`adopted_by_push_to_talk`、`partial`、`finalized`、`send`、`dismiss`、`cancel`、`cooldown`。

### 调试检查清单

- 在重现粘滞叠加时流式传输日志：

  ```bash
  sudo log stream --predicate 'subsystem == "bot.molt" AND category CONTAINS "voicewake"' --level info --style compact
  ```

- 验证只有一个活动会话令牌；协调器应丢弃过时的回调。
- 确保按键说话释放总是使用活动令牌调用 `endCapture`；如果文本为空，预期 `dismiss` 不带铃声或发送。

### 迁移步骤（建议）

1. 添加 `VoiceSessionCoordinator`、`VoiceSession` 和 `VoiceSessionPublisher`。
2. 重构 `VoiceWakeRuntime` 以创建/更新/结束会话而不是直接接触 `VoiceWakeOverlayController`。
3. 重构 `VoicePushToTalk` 以采用现有会话并在释放时调用 `endCapture`；应用运行时冷却。
4. 将 `VoiceWakeOverlayController` 连接到发布者；从运行时/PTT 移除直接调用。
5. 为会话采用、冷却和空文本关闭添加集成测试。