---
summary: "Text-to-speech (TTS) for outbound replies"
read_when:
  - Enabling text-to-speech for replies
  - Configuring TTS providers or limits
  - Using /tts commands
title: "Text-to-Speech"
---
# 文本转语音 (TTS)

OpenClaw 可以使用 ElevenLabs、OpenAI 或 Edge TTS 将外发回复转换为音频。
它可以在 OpenClaw 可以发送音频的任何地方工作；Telegram 会收到一个圆形的语音消息气泡。

## 支持的服务

- **ElevenLabs**（主要或备用提供商）
- **OpenAI**（主要或备用提供商；也用于摘要）
- **Edge TTS**（主要或备用提供商；使用 `node-edge-tts`，在没有 API 密钥时默认使用）

### Edge TTS 注意事项

Edge TTS 通过 `node-edge-tts` 库使用 Microsoft Edge 的在线神经 TTS 服务。
它是一个托管服务（不是本地的），使用 Microsoft 的端点，并且不需要 API 密钥。
`node-edge-tts` 暴露了语音配置选项和输出格式，但并非所有选项都由 Edge 服务支持。 citeturn2search0

由于 Edge TTS 是一个没有发布 SLA 或配额的公共 Web 服务，请将其视为尽力而为。
如果您需要保证的限制和支持，请使用 OpenAI 或 ElevenLabs。
Microsoft 的 Speech REST API 文档中提到每个请求的音频限制为 10 分钟；Edge TTS 没有发布限制，因此假设类似的或更低的限制。 citeturn0search3

## 可选密钥

如果您想使用 OpenAI 或 ElevenLabs：

- `ELEVENLABS_API_KEY`（或 `XI_API_KEY`）
- `OPENAI_API_KEY`

Edge TTS **不** 需要 API 密钥。如果没有找到 API 密钥，OpenClaw 默认使用 Edge TTS（除非通过 `messages.tts.edge.enabled=false` 禁用）。

如果配置了多个提供商，则首先使用选定的提供商，其他的是备用选项。
自动摘要使用配置的 `summaryModel`（或 `agents.defaults.model.primary`），
因此如果启用了摘要，该提供商也必须进行身份验证。

## 服务链接

- [OpenAI 文本转语音指南](https://platform.openai.com/docs/guides/text-to-speech)
- [OpenAI 音频 API 参考](https://platform.openai.com/docs/api-reference/audio)
- [ElevenLabs 文本转语音](https://elevenlabs.io/docs/api-reference/text-to-speech)
- [ElevenLabs 身份验证](https://elevenlabs.io/docs/api-reference/authentication)
- [node-edge-tts](https://github.com/SchneeHertz/node-edge-tts)
- [Microsoft 语音输出格式](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech#audio-outputs)

## 是否默认启用？

不，默认情况下自动 TTS 是 **关闭** 的。在配置中使用 `messages.tts.auto` 启用它，或者在会话中使用 `/tts always`（别名：`/tts on`）启用。

一旦 TTS 开启，Edge TTS **是** 默认启用的，并且在没有 OpenAI 或 ElevenLabs API 密钥时会自动使用。

## 配置

TTS 配置位于 `openclaw.json` 中的 `messages.tts` 下。
完整架构在 [网关配置](/gateway/configuration) 中。

### 最小配置（启用 + 提供商）

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "elevenlabs",
    },
  },
}
```

### OpenAI 主要，ElevenLabs 备用

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "openai",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: {
        enabled: true,
      },
      openai: {
        apiKey: "openai_api_key",
        model: "gpt-4o-mini-tts",
        voice: "alloy",
      },
      elevenlabs: {
        apiKey: "elevenlabs_api_key",
        baseUrl: "https://api.elevenlabs.io",
        voiceId: "voice_id",
        modelId: "eleven_multilingual_v2",
        seed: 42,
        applyTextNormalization: "auto",
        languageCode: "en",
        voiceSettings: {
          stability: 0.5,
          similarityBoost: 0.75,
          style: 0.0,
          useSpeakerBoost: true,
          speed: 1.0,
        },
      },
    },
  },
}
```

### Edge TTS 主要（无需API密钥）

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "edge",
      edge: {
        enabled: true,
        voice: "en-US-MichelleNeural",
        lang: "en-US",
        outputFormat: "audio-24khz-48kbitrate-mono-mp3",
        rate: "+10%",
        pitch: "-5%",
      },
    },
  },
}
```

### 禁用 Edge TTS

```json5
{
  messages: {
    tts: {
      edge: {
        enabled: false,
      },
    },
  },
}
```

### 自定义限制 + 配置路径

```json5
{
  messages: {
    tts: {
      auto: "always",
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
    },
  },
}
```

### 仅在收到语音消息后回复音频

```json5
{
  messages: {
    tts: {
      auto: "inbound",
    },
  },
}
```

### 禁用长回复的自动摘要

```json5
{
  messages: {
    tts: {
      auto: "always",
    },
  },
}
```

然后运行：

```
/tts summary off
```

### 字段说明

- `auto`: auto‑TTS 模式 (`off`, `always`, `inbound`, `tagged`).
  - `inbound` 仅在收到语音便签后发送音频。
  - `tagged` 仅在回复包含 `[[tts]]` 标签时发送音频。
- `enabled`: 旧版切换（医生将其迁移到 `auto`）。
- `mode`: `"final"`（默认）或 `"all"`（包括工具/块回复）。
- `provider`: `"elevenlabs"`, `"openai"`, 或 `"edge"`（回退为自动）。
- 如果 `provider` 未设置，OpenClaw 优先选择 `openai`（如果有密钥），然后是 `elevenlabs`（如果有密钥），
  否则选择 `edge`。
- `summaryModel`: 可选的廉价模型用于自动摘要；默认为 `agents.defaults.model.primary`。
  - 接受 `provider/model` 或配置的模型别名。
- `modelOverrides`: 允许模型发出 TTS 指令（默认开启）。
- `maxTextLength`: TTS 输入的硬限制（字符数）。如果超过 `/tts audio` 将失败。
- `timeoutMs`: 请求超时时间（毫秒）。
- `prefsPath`: 覆盖本地首选项 JSON 路径（提供者/限制/摘要）。
- `apiKey` 的值回退到环境变量 (`ELEVENLABS_API_KEY`/`XI_API_KEY`, `OPENAI_API_KEY`)。
- `elevenlabs.baseUrl`: 覆盖 ElevenLabs API 基础 URL。
- `elevenlabs.voiceSettings`:
  - `stability`, `similarityBoost`, `style`: `0..1`
  - `useSpeakerBoost`: `true|false`
  - `speed`: `0.5..2.0` (1.0 = 正常)
- `elevenlabs.applyTextNormalization`: `auto|on|off`
- `elevenlabs.languageCode`: 两位字母 ISO 639-1（例如 `en`, `de`）
- `elevenlabs.seed`: 整数 `0..4294967295`（尽力确定性）
- `edge.enabled`: 允许使用 Edge TTS（默认 `true`；无需 API 密钥）。
- `edge.voice`: Edge 神经声音名称（例如 `en-US-MichelleNeural`）。
- `edge.lang`: 语言代码（例如 `en-US`）。
- `edge.outputFormat`: Edge 输出格式（例如 `audio-24khz-48kbitrate-mono-mp3`）。
  - 请参阅 Microsoft Speech 输出格式以获取有效值；并非所有格式都由 Edge 支持。
- `edge.rate` / `edge.pitch` / `edge.volume`: 百分比字符串（例如 `+10%`, `-5%`）。
- `edge.saveSubtitles`: 在音频文件旁边写入 JSON 字幕。
- `edge.proxy`: Edge TTS 请求的代理 URL。
- `edge.timeoutMs`: 请求超时时间覆盖（毫秒）。

## 模型驱动的重写（默认开启）

默认情况下，模型 **可以** 为单个回复发出 TTS 指令。
当 `messages.tts.auto` 为 `tagged` 时，这些指令是触发音频所必需的。

启用后，模型可以发出 `[[tts:...]]` 指令来重写单个回复的声音，
加上一个可选的 `[[tts:text]]...[[/tts:text]]` 块来
提供仅应出现在音频中的表现标签（笑声、唱歌提示等）。

示例回复负载：

```
Here you go.

[[tts:provider=elevenlabs voiceId=pMsXgVXv3BLzUgSXRplE model=eleven_v3 speed=1.1]]
[[tts:text]](laughs) Read the song once more.[[/tts:text]]
```

可用指令键（当启用时）：

- `provider` (`openai` | `elevenlabs` | `edge`)
- `voice` (OpenAI voice) 或 `voiceId` (ElevenLabs)
- `model` (OpenAI TTS model 或 ElevenLabs model id)
- `stability`, `similarityBoost`, `style`, `speed`, `useSpeakerBoost`
- `applyTextNormalization` (`auto|on|off`)
- `languageCode` (ISO 639-1)
- `seed`

禁用所有模型覆盖：

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: false,
      },
    },
  },
}
```

可选白名单（在保持标签启用的同时禁用特定覆盖）：

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: true,
        allowProvider: false,
        allowSeed: false,
      },
    },
  },
}
```

## 每用户偏好设置

斜杠命令将本地覆盖写入 `prefsPath`（默认：
`~/.openclaw/settings/tts.json`，使用 `OPENCLAW_TTS_PREFS` 或
`messages.tts.prefsPath` 覆盖）。

存储字段：

- `enabled`
- `provider`
- `maxLength`（摘要阈值；默认 1500 字符）
- `summarize`（默认 `true`）

这些覆盖对该主机的 `messages.tts.*` 生效。

## 输出格式（固定）

- **Telegram**：Opus 语音消息 (`opus_48000_64` 来自 ElevenLabs, `opus` 来自 OpenAI)。
  - 48kHz / 64kbps 是一个良好的语音消息折衷方案，并且对于圆形气泡是必需的。
- **其他渠道**：MP3 (`mp3_44100_128` 来自 ElevenLabs, `mp3` 来自 OpenAI)。
  - 44.1kHz / 128kbps 是语音清晰度的默认平衡。
- **Edge TTS**：使用 `edge.outputFormat`（默认 `audio-24khz-48kbitrate-mono-mp3`）。
  - `node-edge-tts` 接受一个 `outputFormat`，但并非所有格式都可在 Edge 服务中使用。 citeturn2search0
  - 输出格式值遵循 Microsoft Speech 输出格式（包括 Ogg/WebM Opus）。 citeturn1search0
  - Telegram `sendVoice` 接受 OGG/MP3/M4A；如果需要保证 Opus 语音消息，请使用 OpenAI/ElevenLabs。 citeturn1search1
  - 如果配置的 Edge 输出格式失败，OpenClaw 将重试使用 MP3。

OpenAI/ElevenLabs 格式是固定的；Telegram 期望 Opus 用于语音消息体验。

## 自动 TTS 行为

启用时，OpenClaw：

- 如果回复中已经包含媒体或 `MEDIA:` 指令，则跳过 TTS。
- 跳过非常短的回复（< 10 字符）。
- 在启用 `agents.defaults.model.primary`（或 `summaryModel`）时对长回复进行总结。
- 将生成的音频附加到回复中。

如果回复超过 `maxLength` 且摘要关闭（或没有摘要模型的 API 密钥），则跳过音频并发送正常的文本回复。

## 流程图

```
Reply -> TTS enabled?
  no  -> send text
  yes -> has media / MEDIA: / short?
          yes -> send text
          no  -> length > limit?
                   no  -> TTS -> attach audio
                   yes -> summary enabled?
                            no  -> send text
                            yes -> summarize (summaryModel or agents.defaults.model.primary)
                                      -> TTS -> attach audio
```

## 斜杠命令用法

有一个单一的命令：`/tts`。
参见[Slash commands](/tools/slash-commands)以获取启用详细信息。

Discord 注意：`/tts` 是一个内置的 Discord 命令，因此 OpenClaw 在那里注册
`/voice` 作为原生命令。文本 `/tts ...` 仍然有效。

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

注意：

- 命令需要一个授权的发送者（允许列表/所有者规则仍然适用）。
- 必须启用 `commands.text` 或原生命令注册。
- `off|always|inbound|tagged` 是每个会话的开关（`/tts on` 是 `/tts always` 的别名）。
- `limit` 和 `summary` 存储在本地首选项中，而不是主配置中。
- `/tts audio` 生成一次性的音频回复（不会切换 TTS 开关）。

## 代理工具

`tts` 工具将文本转换为语音并返回一个 `MEDIA:` 路径。当
结果与 Telegram 兼容时，该工具包含 `[[audio_as_voice]]` 以便
Telegram 发送语音气泡。

## 网关 RPC

网关方法：

- `tts.status`
- `tts.enable`
- `tts.disable`
- `tts.convert`
- `tts.setProvider`
- `tts.providers`