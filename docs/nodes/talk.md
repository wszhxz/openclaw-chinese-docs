---
summary: "Talk mode: continuous speech conversations with ElevenLabs TTS"
read_when:
  - Implementing Talk mode on macOS/iOS/Android
  - Changing voice/TTS/interrupt behavior
title: "Talk Mode"
---
# 对话模式

对话模式是一种持续语音对话循环：

1. 监听语音输入
2. 将文本记录发送给模型（主会话，chat.send）
3. 等待响应
4. 通过ElevenLabs进行语音播放（流式播放）

## 行为（macOS）

- **启用对话模式时始终显示覆盖层**。
- **监听 → 思考 → 播放**的阶段转换。
- 在**短暂停顿**（静默窗口）时发送当前文本记录。
- 回复内容**写入网页聊天**（与输入文本相同）。
- **语音中断**（默认开启）：如果用户在助手播放语音时开始说话，将停止播放并记录中断时间戳用于下一次提示。

## 回复中的语音指令

助手可能在回复前添加**一行JSON指令**以控制语音：

```json
{ "voice": "<voice-id>", "once": true }
```

规则：

- 仅第一行非空内容。
- 未知键值将被忽略。
- `once: true`仅适用于当前回复。
- 若无`once`，语音将成为Talk模式的新默认语音。
- JSON行在TTS播放前会被剥离。

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
    interruptOnSpeech: true,
  },
}
```

默认值：

- `interruptOnSpeech`: true
- `voiceId`: 回退到 `ELEVENLABS_VOICE_ID` / `SAG_VOICE_ID`（或在API密钥可用时使用第一个ElevenLabs语音）
- `modelId`: 未设置时默认为 `eleven_v3`
- `apiKey`: 回退到 `ELEVENLABS_API_KEY`（或可用网关shell配置文件）
- `outputFormat`: 默认在macOS/iOS上为 `pcm_44100`，在Android上为 `pcm_24000`（设置 `mp3_*` 强制MP3流式播放）

## macOS界面

- 菜单栏切换：**对话**
- 配置标签页：**对话模式**组（语音ID + 中断切换）
- 覆盖层：
  - **监听**：云图标随麦克风电平脉动
  - **思考**：下沉动画
  - **播放**：辐射环动画
  - 点击云图标：停止播放
  - 点击X：退出对话模式

## 说明

- 需要语音与麦克风权限。
- 使用 `chat.send` 对应会话密钥 `main`。
- TTS使用ElevenLabs流式API，配合 `ELEVENLABS_API_KEY`，在macOS/iOS/Android上使用增量播放以降低延迟。
- `eleven_v3` 的 `stability` 验证为 `0.0`、`0.5` 或 `1.0`；其他模型接受 `0..1`。
- `latency_tier` 设置时验证为 `0..4`。
- Android支持 `pcm_16000`、`pcm_22050`、`pcm_24000` 和 `pcm_44100` 输出格式以实现低延迟AudioTrack流式播放。