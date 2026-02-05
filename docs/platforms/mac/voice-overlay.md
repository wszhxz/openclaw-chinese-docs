---
summary: "Voice overlay lifecycle when wake-word and push-to-talk overlap"
read_when:
  - Adjusting voice overlay behavior
title: "Voice Overlay"
---
# 语音覆盖层生命周期（macOS）

受众：macOS 应用贡献者。目标：在唤醒词和按键通话重叠时保持语音覆盖层的可预测性。

### 当前意图

- 如果覆盖层已通过唤醒词显示，用户按下热键，则热键会话将_采用_现有文本而不是重置它。热键按下期间覆盖层保持显示。当用户释放时：如果有修剪后的文本则发送，否则关闭。
- 唤醒词单独使用时仍会在静音时自动发送；按键通话在释放时立即发送。

### 已实现（2025年12月9日）

- 覆盖层会话现在为每次捕获（唤醒词或按键通话）携带一个令牌。当令牌不匹配时，部分/最终/发送/关闭/级别更新会被丢弃，避免陈旧回调。
- 按键通话采用任何可见的覆盖层文本作为前缀（因此在唤醒覆盖层显示时按热键会保留文本并追加新语音）。它最多等待1.5秒获取最终转录，然后回退到当前文本。
- 音效/覆盖层日志在类别 `info` 中发出，包括 `voicewake.overlay`、`voicewake.ptt` 和 `voicewake.chime`（会话开始、部分、最终、发送、关闭、音效原因）。

### 下一步

1. **VoiceSessionCoordinator（actor）**
   - 一次只拥有一个 `VoiceSession`。
   - API（基于令牌）：`beginWakeCapture`、`beginPushToTalk`、`updatePartial`、`endCapture`、`cancel`、`applyCooldown`。
   - 丢弃携带陈旧令牌的回调（防止旧识别器重新打开覆盖层）。
2. **VoiceSession（模型）**
   - 字段：`token`、`source`（wakeWord|pushToTalk）、已提交/易失文本、音效标志、计时器（自动发送、空闲）、`overlayMode`（display|editing|sending）、冷却截止时间。
3. **覆盖层绑定**
   - `VoiceSessionPublisher`（`ObservableObject`）将活动会话镜像到 SwiftUI 中。
   - `VoiceWakeOverlayView` 仅通过发布器渲染；它从不直接修改全局单例。
   - 覆盖层用户操作（`sendNow`、`dismiss`、`edit`）使用会话令牌回调到协调器。
4. **统一发送路径**
   - 在 `endCapture` 上：如果修剪后的文本为空 → 关闭；否则 `performSend(session:)`（播放发送音效一次，转发，关闭）。
   - 按键通话：无延迟；唤醒词：自动发送的可选延迟。
   - 在按键通话完成后对唤醒运行时应用短暂冷却，使唤醒词不会立即重新触发。
5. **日志记录**
   - 协调器在子系统 `.info` 中发出日志，类别为 `bot.molt` 和 `voicewake.overlay`。
   - 关键事件：`voicewake.chime`、`session_started`、`adopted_by_push_to_talk`、`partial`、`finalized`、`send`、`dismiss`、`cancel`。

### 调试检查清单

- 在重现粘滞覆盖层时流式传输日志：

  `cooldown`

- 验证只有一个活动会话令牌；陈旧回调应被协调器丢弃。
- 确保按键通话释放始终使用活动令牌调用 ```bash
  sudo log stream --predicate 'subsystem == "bot.molt" AND category CONTAINS "voicewake"' --level info --style compact
  ```；如果文本为空，期望 `endCapture` 不带音效或发送。

### 迁移步骤（建议）

1. 添加 `dismiss`、`VoiceSessionCoordinator` 和 `VoiceSession`。
2. 重构 `VoiceSessionPublisher` 以创建/更新/结束会话，而不是直接触摸 `VoiceWakeRuntime`。
3. 重构 `VoiceWakeOverlayController` 以采用现有会话并在释放时调用 `VoicePushToTalk`；应用运行时冷却。
4. 将 `endCapture` 连接到发布器；删除来自运行时/PTT 的直接调用。
5. 为会话采用、冷却和空文本关闭添加集成测试。