---
summary: "Text-to-speech (TTS) for outbound replies"
read_when:
  - Enabling text-to-speech for replies
  - Configuring TTS providers or limits
  - Using /tts commands
title: "Text-to-Speech"
---
# 文本转语音（TTS）

OpenClaw 可以使用 ElevenLabs、OpenAI 或 Edge TTS 将出站回复转换为音频。
它在 OpenClaw 可以发送音频的任何地方都能运行；Telegram 会收到一个圆形语音备忘录气泡。

## 支持的服务

- **ElevenLabs**（主要或备用提供者）
- **OpenAI**（主要或备用提供者；也用于摘要）
- **Edge TTS**（主要或备用提供者；使用 `node-edge-tts`，默认情况下在没有 API 密钥时使用）

### Edge TTS 注意事项

Edge TTS 通过 `node-edge-tts` 库使用 Microsoft Edge 的在线神经 TTS 服务。它是一个托管服务（非本地），使用 Microsoft 的端点，并且不需要 API 密钥。`node-edge-tts` 暴露了语音配置选项和输出格式，但并非所有选项都受 Edge 服务支持。 citeturn2search0

由于 Edge TTS 是一个没有发布 SLA 或配额的公共网络服务，应将其视为尽力而为。如果您需要保证的限制和支持，请使用 OpenAI 或 ElevenLabs。 citeturn2search0

## 可选密钥

- `ELEVENLABS_API_KEY`：ElevenLabs 的 API 密钥
- `OPENAI_API_KEY`：OpenAI 的 API 密钥
- `EDGE_TTS_API_KEY`：Edge TTS 的 API 密钥

## 服务链接

- [ElevenLabs 官方网站](https://elevenlabs.io/)
- [OpenAI 官方网站](https://openai.com/)
- [Edge TTS 官方网站](https://github.com/kevinsmiley/node-edge-tts)

## 使用示例

```json
{
  "tts": {
    "provider": "elevenlabs",
    "voice": "Rachel",
    "model": "eleven_multilingual_v2",
    "stability": 0.75,
    "similarityBoost": 0.75,
    "speed": 1.1,
    "applyTextNormalization": "auto",
    "languageCode": "en",
    "seed": 123456789
  }
}
```

## 每个用户的偏好

斜杠命令将本地覆盖写入 `prefsPath`（默认：`~/.openclaw/settings/tts.json`，可通过 `OPENCLAW_TTS_PREFS` 或 `messages.tts.prefsPath` 覆盖）。

存储的字段：

- `enabled`
- `provider`
- `maxLength`（摘要阈值；默认 1500 字符）
- `summarize`（默认 `true`）

这些覆盖 `messages.tts.*` 对于该主机。

## 输出格式（固定）

- **Telegram**：Opus 语音备忘录（来自 ElevenLabs 的 `opus_48000_64`，来自 OpenAI 的 `opus`）。
  - 48kHz / 64kbps 是语音备忘录的良好折中方案，且是圆形气泡所需的。
- **其他频道**：MP3（来自 ElevenLabs 的 `mp3_44100_128`，来自 OpenAI 的 `mp3`）。
  - 44.1kHz / 128kbps 是语音清晰度的默认平衡。
- **Edge TTS**：使用 `edge.outputFormat`（默认 `audio-24khz-48kbitrate-mono-mp3`）。
  - `node-edge-tts` 接受 `outputFormat`，但并非所有格式都来自 Edge 服务。 citeturn2search0
  - 输出格式值遵循 Microsoft Speech 输出格式（包括 Ogg/WebM Opus）。 citeturn1search0
  - Telegram `sendVoice` 接受 OGG/MP3/M4A；如果您需要保证 Opus 语音备忘录，请使用 OpenAI/ElevenLabs。 citeturn1search1
  - 如果配置的 Edge 输出格式失败，OpenClaw 将尝试使用 MP3。

OpenAI/ElevenLabs 格式是固定的；Telegram 期望 Opus 语音备忘录用户体验。

## 自动 TTS 行为

当启用时，OpenClaw：

- 如果回复已包含媒体或 `MEDIA:` 指令，则跳过 TTS。
- 跳过非常短的回复（< 10 字符）。
- 当启用时，使用 `agents.defaults.model.primary`（或 `summaryModel`）对长回复进行摘要。
- 将生成的音频附加到回复。

如果回复超过 `maxLength` 且摘要关闭（或没有摘要模型的 API 密钥），则跳过音频，发送正常的文本回复。

## 流程图

```
回复 -> TTS 启用？
  否 -> 发送文本
  是 -> 是否有媒体 / MEDIA: / 短？
          是 -> 发送文本
          否 -> 长度 > 限制？
                   否 -> TTS -> 附加音频
                   是 -> 摘要启用？
                            否 -> 发送文本
                            是 -> 摘要（summaryModel 或 agents.defaults.model.primary）
                                      -> TTS -> 附加音频
```

## 斜杠命令使用

有一个命令：`/tts`。
查看 [斜杠命令](/tools/slash-commands) 以获取启用详细信息。

Discord 注意：`/tts` 是内置的 Discord 命令，因此 OpenClaw 在那里注册 `/voice` 作为原生命令。文本 `/tts ...` 仍然有效。

```
/tts off
/tts always
/tts inbound
/tts tagged
/tts status
/tts provider openai
/tts limit 2000
/tts summary off
/tts audio Hello from OpenClaw
```

注意事项：

- 命令需要授权的发送者（允许列表/所有者规则仍然适用）。
- 必须启用 `commands.text` 或原生命令注册。
- `off|always|inbound|tagged` 是会话级切换（`/tts on` 是 `/tts always` 的别名）。
- `limit` 和 `summary` 存储在本地偏好中，而不是主配置中。
- `/tts audio`