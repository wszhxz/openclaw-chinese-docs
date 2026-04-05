---
summary: "Talk mode: continuous speech conversations with ElevenLabs TTS"
read_when:
  - Implementing Talk mode on macOS/iOS/Android
  - Changing voice/TTS/interrupt behavior
title: "Talk Mode"
---
# Talk 模式

Talk 模式是一个持续的语音对话循环：

1. 监听语音
2. 将转录发送给模型（主会话，chat.send）
3. 等待响应
4. 通过配置的 Talk 提供者 (`talk.speak`) 进行播报

## 行为 (macOS)

- **常驻叠加层**：启用 Talk 模式时。
- **监听 → 思考 → 播报** 阶段转换。
- 在**短暂停**（静默窗口）期间，发送当前转录文本。
- 回复会**写入 WebChat**（与输入相同）。
- **语音中断**（默认开启）：如果用户在助手说话时开始讲话，我们将停止播放并记录中断时间戳以供下一个提示使用。

## 回复中的语音指令

助手可以在其回复前添加一个**单行 JSON**来控制语音：

```json
{ "voice": "<voice-id>", "once": true }
```

规则：

- 仅第一行非空行。
- 未知键将被忽略。
- `once: true` 仅适用于当前回复。
- 如果没有 `once`，语音将成为 Talk 模式的新默认值。
- JSON 行在 TTS 播放前会被剥离。

支持的键：

- `voice` / `voice_id` / `voiceId`
- `model` / `model_id` / `modelId`
- `speed`, `rate` (WPM), `stability`, `similarity`, `style`, `speakerBoost`
- `seed`, `normalize`, `lang`, `output_format`, `latency_tier`
- `once`

## 配置 (`~/.openclaw/openclaw.json`)

```json5
{
  talk: {
    voiceId: "elevenlabs_voice_id",
    modelId: "eleven_v3",
    outputFormat: "mp3_44100_128",
    apiKey: "elevenlabs_api_key",
    silenceTimeoutMs: 1500,
    interruptOnSpeech: true,
  },
}
```

默认值：

- `interruptOnSpeech`: true
- `silenceTimeoutMs`: 未设置时，Talk 在发送转录前保持平台默认的暂停窗口 (`700 ms on macOS and Android, 900 ms on iOS`)
- `voiceId`: 回退到 `ELEVENLABS_VOICE_ID` / `SAG_VOICE_ID`（当有 API 密钥时使用第一个 ElevenLabs 语音）
- `modelId`: 未设置时默认为 `eleven_v3`
- `apiKey`: 回退到 `ELEVENLABS_API_KEY`（如果有可用的网关 shell 配置文件）
- `outputFormat`: 在 macOS/iOS 上默认为 `pcm_44100`，在 Android 上为 `pcm_24000`（设置 `mp3_*` 以强制 MP3 流式传输）

## macOS 界面

- 菜单栏切换：**Talk**
- 配置选项卡：**Talk 模式**组（语音 ID + 中断切换）
- 叠加层：
  - **监听中**：云朵随麦克风电平脉冲
  - **思考中**：下沉动画
  - **播报中**：辐射圆环
  - 点击云朵：停止播报
  - 点击 X：退出 Talk 模式

## 注意事项

- 需要语音 + 麦克风权限。
- 使用 `chat.send` 针对会话密钥 `main`。
- 网关通过 `talk.speak` 解析 Talk 播放，使用活动的 Talk 提供者。仅在 RPC 不可用时，Android 才会回退到本地系统 TTS。
- `stability` 对于 `eleven_v3` 被验证为 `0.0`、`0.5` 或 `1.0`；其他模型接受 `0..1`。
- 设置时，`latency_tier` 被验证为 `0..4`。
- Android 支持 `pcm_16000`、`pcm_22050`、`pcm_24000` 和 `pcm_44100` 输出格式，用于低延迟 AudioTrack 流式传输。