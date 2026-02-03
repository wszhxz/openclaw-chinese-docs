---
summary: "Voice overlay lifecycle when wake-word and push-to-talk overlap"
read_when:
  - Adjusting voice overlay behavior
title: "Voice Overlay"
---
# 语音覆盖生命周期（macOS）

受众：macOS 应用开发者。目标：在唤醒词和按住说话功能重叠时保持语音覆盖层的可预测性。

### 当前意图

- 如果覆盖层已由唤醒词显示，且用户按下热键，热键会话将**采用**现有的文本，而不是重置文本。在按住热键期间覆盖层保持显示。用户释放热键时：若存在修剪后的文本则发送，否则关闭覆盖层。
- 唤醒词单独使用时仍会在静默时自动发送；按住说话在释放时立即发送。

### 已实现（2025年12月9日）

- 覆盖层会话现在每个捕获（唤醒词或按住说话）携带一个令牌。当令牌不匹配时，部分/最终/发送/关闭/级别更新将被丢弃，避免过期回调。
- 按住说话将采用任何可见的覆盖层文本作为前缀（因此在唤醒覆盖层显示时按下热键会保持文本并追加新语音）。它最多等待1.5秒以获取最终转录文本，否则回退到当前文本。
- 提示音/覆盖层日志在 `voicewake.overlay`、`voicewake.ptt` 和 `voicewake.chime` 类别中以 `info` 级别输出（会话开始、部分、最终、发送、关闭、提示音原因）。

### 下一步计划

1. **VoiceSessionCoordinator（协程）**
   - 一次只拥有一个 `VoiceSession`。
   - 基于令牌的 API：`beginWakeCapture`、`beginPushToTalk`、`updatePartial`、`endCapture`、`cancel`、`applyCooldown`。
   - 丢弃携带过期令牌的回调（防止旧识别器重新打开覆盖层）。
2. **VoiceSession（模型）**
   - 字段：`token`、`source`（wakeWord|pushToTalk）、已提交/易变文本、提示音标志、计时器（自动发送、空闲）、`overlayMode`（显示|编辑|发送）、冷却截止时间。
3. **覆盖层绑定**
   - `VoiceSessionPublisher`（`ObservableObject`）将活动会话同步到 SwiftUI。
   - `VoiceWakeOverlayView` 仅通过发布者渲染；它从不直接修改全局单例。
   - 覆盖层用户操作（`sendNow`、`dismiss`、`edit`）通过会话令牌回调到协调器。
4. **统一发送路径**
   - 在 `endCapture` 时：若修剪后的文本为空 → 关闭；否则调用 `performSend(session:)`（播放发送提示音一次，转发，关闭）。
   - 按住说话：无延迟；唤醒词：可选延迟用于自动发送。
   - 在按住说话完成后对唤醒运行时应用短暂冷却期，以防止唤醒词立即重新触发。
5. **日志**
   - 协调器在子系统 `bot.molt` 的 `voicewake.overlay` 和 `voicewake.chime` 类别中发出 `.info` 日志。
   - 关键事件：`session_started`、`adopted_by_push_to_talk`、`partial`、`finalized`、`send`、`dismiss`、`cancel`、`cooldown`。

### 调试检查清单

- 在重现粘滞覆盖层时流式日志：

  ```bash
  sudo log stream --predicate 'subsystem == "bot.molt" AND category CONTAINS "voicewake"' --level info --style compact
  ```

- 验证仅有一个活动会话令牌；过期回调应由协调器丢弃。
- 确保按住说话释放时始终使用活动令牌调用 `endCapture`；若文本为空，预期关闭覆盖层且无提示音或发送。

### 迁移步骤（建议）

1. 添加 `VoiceSessionCoordinator`、`VoiceSession` 和 `VoiceSessionPublisher`。
2. 重构 `VoiceWakeRuntime` 以创建/更新/结束会话，而不是直接操作 `VoiceWakeOverlayController`。
3. 重构 `VoicePushToTalk` 以采用现有会话并在释放时调用 `endCapture`；应用运行时冷却期。
4. 将 `VoiceWakeOverlayController` 绑定到发布者；移除运行时/PTT 的直接调用。
5. 为会话采用、冷却期和空文本关闭添加集成测试。