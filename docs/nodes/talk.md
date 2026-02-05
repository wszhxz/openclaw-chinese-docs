---
summary: "Talk mode: continuous speech conversations with ElevenLabs TTS"
read_when:
  - Implementing Talk mode on macOS/iOS/Android
  - Changing voice/TTS/interrupt behavior
title: "Talk Mode"
---
# 对话模式

对话模式是一个连续的语音对话循环：

1. 监听语音
2. 将转录发送给模型（主会话，chat.send）
3. 等待响应
4. 通过ElevenLabs播放（流式播放）

## 行为 (macOS)

- 启用对话模式时，始终显示**叠加层**。
- **监听 → 思考 → 发言**阶段转换。
- 在**短暂暂停**（静音窗口）时，发送当前转录。
- 回复会**写入WebChat**（与输入相同）。
- **语音中断**（默认开启）：如果用户在助手发言时开始说话，我们将停止播放并记录中断时间戳以供下次提示使用。

## 回复中的语音指令

助手可能会在其回复前加上**单行JSON**来控制语音：

```json
{ "voice": "<voice-id>", "once": true }
```

规则：

- 仅第一行非空行有效。
- 未知键被忽略。
- `once: true`仅适用于当前回复。
- 没有`once`时，该语音将成为对话模式的新默认值。
- 在TTS播放前会移除JSON行。

支持的键：

- `voice` / `voice_id` / `voiceId`
- `model` / `model_id` / `modelId`
- `speed`, `rate`（WPM），`stability`, `similarity`, `style`, `speakerBoost`
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
    interruptOnSpeech: true,
  },
}
```

默认值：

- `interruptOnSpeech`: true
- `voiceId`: 回退到`ELEVENLABS_VOICE_ID` / `SAG_VOICE_ID`（或API密钥可用时的第一个ElevenLabs语音）
- `modelId`: 未设置时默认为`eleven_v3`
- `apiKey`: 回退到`ELEVENLABS_API_KEY`（或网关shell配置文件如果可用）
- `outputFormat`: 在macOS/iOS上默认为`pcm_44100`，在Android上默认为`pcm_24000`（设置`mp3_*`以强制MP3流式传输）

## macOS界面

- 菜单栏切换：**对话**
- 配置选项卡：**对话模式**组（语音ID + 中断切换）
- 叠加层：
  - **监听**：云脉冲随麦克风级别变化
  - **思考**：下沉动画
  - **发言**：辐射环
  - 点击云：停止发言
  - 点击X：退出对话模式

## 注意事项

- 需要语音和麦克风权限。
- 使用`chat.send`针对会话密钥`main`。
- TTS使用ElevenLabs流式API，结合`ELEVENLABS_API_KEY`并在macOS/iOS/Android上进行增量播放以降低延迟。
- `stability`对于`eleven_v3`验证为`0.0`，`0.5`，或`1.0`；其他模型接受`0..1`。
- 设置`latency_tier`时验证为`0..4`。
- Android支持`pcm_16000`，`pcm_22050`，`pcm_24000`，和`pcm_44100`输出格式以实现低延迟AudioTrack流式传输。