---
summary: "Talk mode: continuous speech conversations with ElevenLabs TTS"
read_when:
  - Implementing Talk mode on macOS/iOS/Android
  - Changing voice/TTS/interrupt behavior
title: "Talk Mode"
---
# 语音对话模式

语音对话模式是一种持续的语音交流循环：

1. 监听语音输入  
2. 将语音转录文本发送至模型（主会话，`chat.send`）  
3. 等待模型响应  
4. 通过 ElevenLabs 合成语音并流式播放（streaming playback）

## 行为表现（macOS）

- 在启用语音对话模式期间，**始终显示悬浮覆盖层**。  
- 显示 **“监听 → 思考 → 发言”** 的阶段转换状态。  
- 遇到**短暂静音**（即静音窗口），当前转录文本将被立即发送。  
- 回复内容将**写入 WebChat**（与手动输入行为一致）。  
- **支持语音打断**（默认开启）：若用户在助手发言过程中开始说话，系统将停止语音播放，并记录打断时间戳，用于下一轮提示词生成。

## 回复中的语音指令

助手可在其回复开头添加**单行 JSON**，以控制语音合成行为：

```json
{ "voice": "<voice-id>", "once": true }
```

规则如下：

- 仅识别**首行非空行**。  
- 未知字段将被忽略。  
- `once: true` 仅对当前回复生效。  
- 若未指定 `once`，该语音设置将成为语音对话模式的新默认值。  
- 该 JSON 行将在 TTS 播放前被自动移除。

支持的字段：

- `voice` / `voice_id` / `voiceId`  
- `model` / `model_id` / `modelId`  
- `speed`、`rate`（单词每分钟数，WPM）、`stability`、`similarity`、`style`、`speakerBoost`  
- `seed`、`normalize`、`lang`、`output_format`、`latency_tier`  
- `once`

## 配置项（`~/.openclaw/openclaw.json`）

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

- `interruptOnSpeech`：`true`  
- `voiceId`：若未设置，则回退至 `ELEVENLABS_VOICE_ID` / `SAG_VOICE_ID`（或当 API 密钥可用时，使用首个 ElevenLabs 语音）  
- `modelId`：若未设置，默认为 `eleven_v3`  
- `apiKey`：若未设置，则回退至 `ELEVENLABS_API_KEY`（或使用可用的网关 Shell 配置文件）  
- `outputFormat`：在 macOS/iOS 上默认为 `pcm_44100`，在 Android 上默认为 `pcm_24000`（设置 `mp3_*` 可强制启用 MP3 流式传输）

## macOS 用户界面

- 菜单栏开关：**Talk**  
- 配置页签：**Talk Mode** 分组（含语音 ID 和打断开关）  
- 悬浮覆盖层状态指示：  
  - **Listening（监听中）**：云朵图标随麦克风输入电平脉动  
  - **Thinking（思考中）**：下沉动画效果  
  - **Speaking（发言中）**：向外扩散的环形动画  
  - 点击云朵图标：停止当前语音播放  
  - 点击 X：退出语音对话模式  

## 注意事项

- 需要授予“语音识别”和“麦克风”权限。  
- 使用 `chat.send` 对话能力，作用于会话密钥 `main`。  
- 文本转语音（TTS）采用 ElevenLabs 流式 API，并在 macOS/iOS/Android 平台上启用 `ELEVENLABS_API_KEY` 与增量式播放，以降低延迟。  
- 对于 `eleven_v3`，`stability` 已验证支持 `0.0`、`0.5` 或 `1.0`；其他模型仅接受 `0..1`。  
- 当设置 `latency_tier` 时，其值已验证为 `0..4`。  
- Android 支持 `pcm_16000`、`pcm_22050`、`pcm_24000` 和 `pcm_44100` 输出格式，以实现低延迟 AudioTrack 流式播放。