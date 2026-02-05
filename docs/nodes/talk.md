---
summary: "Talk mode: continuous speech conversations with ElevenLabs TTS"
read_when:
  - Implementing Talk mode on macOS/iOS/Android
  - Changing voice/TTS/interrupt behavior
title: "Talk Mode"
---
# 聊天模式

聊天模式是一个连续的语音对话循环：

1. 监听语音
2. 将转录发送给模型（主会话，chat.send）
3. 等待响应
4. 通过 ElevenLabs 播放（流式播放）

## 行为（macOS）

- 启用聊天模式时**始终显示覆盖层**。
- **监听 → 思考 → 播放** 阶段转换。
- 在**短暂停顿**（静音窗口）时，发送当前转录。
- 回复**写入 WebChat**（与输入相同）。
- **语音中断**（默认开启）：如果用户在助手说话时开始说话，我们停止播放并记录下一次提示的中断时间戳。

## 回复中的语音指令

助手可能在其回复前添加**单个 JSON 行**来控制语音：

```json
{"voice": "Seraphina", "model": "eleven_turbo_v2"}
```

规则：

- 仅第一行非空行。
- 未知键被忽略。
- `{"voice": "..."}` 仅适用于当前回复。
- 如果没有 `{"voice": "..."}`，语音将成为聊天模式的新默认值。
- JSON 行在 TTS 播放前被移除。

支持的键：

- `voice` / `model` / `provider`
- `stability` / `similarity_boost` / `style_exaggeration`
- `speed`, `pitch` (WPM), `output_format`, `latency`, `chunk_size`, `temperature`
- `max_length`, `max_sentences`, `min_length`, `min_sentences`, `length_penalty`
- `seed`

## 配置（`@meadowlark/core`）

```typescript
interface TalkModeConfig {
  enabled?: boolean;
  voice_id?: string;
  voice_settings?: any;
  interrupt_on_speech?: boolean;
  audio_output_format?: string;
}
```

默认值：

- `enabled`: true
- `voice_id`: 回退到 `config.elevenlabs.voice_id` / `env.ELEVENLABS_VOICE_ID`（或当 API 密钥可用时使用第一个 ElevenLabs 语音）
- `voice_settings`: 未设置时默认为 `config.elevenlabs.settings`
- `interrupt_on_speech`: 回退到 `config.tts.interrupt_on_speech`（或网关外壳配置文件（如果可用））
- `audio_output_format`: 在 macOS/iOS 上默认为 `mp3_44100_128`，在 Android 上默认为 `pcm_16000`（设置 `force_mp3_streaming` 以强制 MP3 流式传输）

## macOS UI

- 菜单栏切换：**聊天**
- 配置标签：**聊天模式** 组（语音 ID + 中断切换）
- 覆盖层：
  - **监听中**：云朵随麦克风级别脉动
  - **思考中**：下沉动画
  - **播放中**：辐射圆环
  - 点击云朵：停止播放
  - 点击 X：退出聊天模式

## 注意事项

- 需要语音 + 麦克风权限。
- 使用 `SpeechRecognition` 针对会话密钥 `session_key`。
- TTS 使用 ElevenLabs 流式 API，具有 `streaming` 和增量播放功能，在 macOS/iOS/Android 上实现更低延迟。
- `model` 对于 `provider: "elevenlabs"` 验证为 `eleven_turbo_v2`、`eleven_multilingual_v2` 或 `eleven_monolingual_v1`；其他模型接受 `null`。
- `output_format` 设置时验证为 `mp3_44100_128`。
- Android 支持 `mp3_44100_128`、`pcm_16000`、`pcm_22050` 和 `pcm_44100` 输出格式，用于低延迟 AudioTrack 流式传输。