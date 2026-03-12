---
summary: "Text-to-speech (TTS) for outbound replies"
read_when:
  - Enabling text-to-speech for replies
  - Configuring TTS providers or limits
  - Using /tts commands
title: "Text-to-Speech"
---
# 文本转语音（TTS）

OpenClaw 可使用 ElevenLabs、OpenAI 或 Edge TTS 将外发回复转换为音频。  
只要 OpenClaw 能发送音频的平台，该功能即可工作；在 Telegram 中会以圆形语音消息气泡形式呈现。

## 支持的服务

- **ElevenLabs**（主用或备用服务提供商）  
- **OpenAI**（主用或备用服务提供商；摘要生成也使用该服务）  
- **Edge TTS**（主用或备用服务提供商；使用 `node-edge-tts`，无 API 密钥时默认启用）

### Edge TTS 说明

Edge TTS 通过 `node-edge-tts` 库调用 Microsoft Edge 的在线神经网络文本转语音（TTS）服务。  
它是一项托管服务（非本地部署），使用 Microsoft 的服务端点，且**无需 API 密钥**。  
`node-edge-tts` 暴露了语音配置选项与输出格式，但 Edge 服务并不支持全部选项。citeturn2search0

由于 Edge TTS 是一项无公开服务等级协议（SLA）或配额限制的公共网络服务，应将其视为“尽力而为”（best-effort）服务。  
如需保障配额与技术支持，请改用 OpenAI 或 ElevenLabs。  
Microsoft Speech REST API 文档注明单次请求音频时长上限为 10 分钟；Edge TTS 未公布具体限制，因此请假设其限制与此相近或更低。citeturn0search3

## 可选密钥

如需启用 OpenAI 或 ElevenLabs：

- `ELEVENLABS_API_KEY`（或 `XI_API_KEY`）  
- `OPENAI_API_KEY`

Edge TTS **不需要** API 密钥。若未检测到任何 API 密钥，OpenClaw 将默认使用 Edge TTS（除非通过 `messages.tts.edge.enabled=false` 显式禁用）。

若配置了多个服务提供商，则优先使用指定的主用提供商，其余作为备用选项。  
自动摘要功能使用已配置的 `summaryModel`（或 `agents.defaults.model.primary`），因此若您启用了摘要功能，则该提供商也必须完成身份验证。

## 服务链接

- [OpenAI 文本转语音指南](https://platform.openai.com/docs/guides/text-to-speech)  
- [OpenAI 音频 API 参考文档](https://platform.openai.com/docs/api-reference/audio)  
- [ElevenLabs 文本转语音](https://elevenlabs.io/docs/api-reference/text-to-speech)  
- [ElevenLabs 身份验证](https://elevenlabs.io/docs/api-reference/authentication)  
- [node-edge-tts](https://github.com/SchneeHertz/node-edge-tts)  
- [Microsoft Speech 输出格式](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech#audio-outputs)

## 是否默认启用？

否。自动 TTS 功能**默认关闭**。您可通过配置项 `messages.tts.auto` 启用，或在会话中使用 `/tts always`（别名：`/tts on`）启用。

一旦启用 TTS，Edge TTS **默认启用**，并在未提供 OpenAI 或 ElevenLabs API 密钥时自动启用。

## 配置

TTS 配置位于 `messages.tts` 下的 `openclaw.json` 文件中。  
完整配置模式详见 [网关配置](/gateway/configuration)。

### 最小化配置（启用 + 指定提供商）

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

### OpenAI 主用 + ElevenLabs 备用

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
        baseUrl: "https://api.openai.com/v1",
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

### Edge TTS 主用（无需 API 密钥）

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

### 自定义限制 + 首选项路径

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

### 仅在收到入站语音消息后才以音频形式回复

```json5
{
  messages: {
    tts: {
      auto: "inbound",
    },
  },
}
```

### 为长回复禁用自动摘要

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

- `auto`：自动 TTS 模式（`off`、`always`、`inbound`、`tagged`）。  
  - `inbound` 仅在收到入站语音消息后才发送音频。  
  - `tagged` 仅在回复中包含 `[[tts]]` 标签时才发送音频。  
- `enabled`：旧版开关（doctor 会将此迁移至 `auto`）。  
- `mode`：`"final"`（默认）或 `"all"`（包含工具/区块回复）。  
- `provider`：`"elevenlabs"`、`"openai"` 或 `"edge"`（备用机制为自动切换）。  
- 若 `provider` **未设置**，OpenClaw 将优先选用 `openai`（如有密钥），其次为 `elevenlabs`（如有密钥），否则使用 `edge`。  
- `summaryModel`：用于自动摘要的低成本模型（可选）；默认为 `agents.defaults.model.primary`。  
  - 接受 `provider/model` 或已配置的模型别名。  
- `modelOverrides`：允许模型输出 TTS 指令（默认开启）。  
  - `allowProvider` 默认为 `false`（服务提供商切换需显式启用）。  
- `maxTextLength`：TTS 输入长度硬性上限（字符数）。超出则 `/tts audio` 失败。  
- `timeoutMs`：请求超时时间（毫秒）。  
- `prefsPath`：覆盖本地首选项 JSON 文件路径（含服务提供商/限制/摘要配置）。  
- `apiKey` 的值会回退至环境变量（`ELEVENLABS_API_KEY`/`XI_API_KEY`、`OPENAI_API_KEY`）。  
- `elevenlabs.baseUrl`：覆盖 ElevenLabs API 基础 URL。  
- `openai.baseUrl`：覆盖 OpenAI TTS 端点。  
  - 解析顺序：`messages.tts.openai.baseUrl` → `OPENAI_TTS_BASE_URL` → `https://api.openai.com/v1`  
  - 非默认值将被视为兼容 OpenAI 的 TTS 端点，因此支持自定义模型名与语音名。  
- `elevenlabs.voiceSettings`：  
  - `stability`、`similarityBoost`、`style`：`0..1`  
  - `useSpeakerBoost`：`true|false`  
  - `speed`：`0.5..2.0`（1.0 = 正常语速）  
- `elevenlabs.applyTextNormalization`：`auto|on|off`  
- `elevenlabs.languageCode`：两位字母 ISO 639-1 语言代码（例如 `en`、`de`）  
- `elevenlabs.seed`：整型 `0..4294967295`（尽力实现确定性）  
- `edge.enabled`：允许使用 Edge TTS（默认 `true`；无需 API 密钥）。  
- `edge.voice`：Edge 神经语音名称（例如 `en-US-MichelleNeural`）。  
- `edge.lang`：语言代码（例如 `en-US`）。  
- `edge.outputFormat`：Edge 输出格式（例如 `audio-24khz-48kbitrate-mono-mp3`）。  
  - 有效取值参见 Microsoft Speech 输出格式；并非所有格式均被 Edge 支持。  
- `edge.rate` / `edge.pitch` / `edge.volume`：百分比字符串（例如 `+10%`、`-5%`）。  
- `edge.saveSubtitles`：在生成音频文件的同时写入 JSON 字幕。  
- `edge.proxy`：Edge TTS 请求所用代理 URL。  
- `edge.timeoutMs`：请求超时时间覆盖值（毫秒）。

## 模型驱动的覆盖配置（默认启用）

默认情况下，模型**可以**为单条回复输出 TTS 指令。  
当 `messages.tts.auto` 设为 `tagged` 时，必须存在这些指令才能触发音频输出。

启用后，模型可输出 `[[tts:...]]` 指令，以覆盖单条回复所用语音；还可选择性地输出 `[[tts:text]]...[[/tts:text]]` 区块，提供仅用于音频的表达性标签（如笑声、歌唱提示等）。

除非启用 `modelOverrides.allowProvider: true`，否则 `provider=...` 指令将被忽略。

示例回复载荷：

```
Here you go.

[[tts:voiceId=pMsXgVXv3BLzUgSXRplE model=eleven_v3 speed=1.1]]
[[tts:text]](laughs) Read the song once more.[[/tts:text]]
```

启用时可用的指令键：

- `provider`（`openai` | `elevenlabs` | `edge`，需配合 `allowProvider: true`）  
- `voice`（OpenAI 语音）或 `voiceId`（ElevenLabs）  
- `model`（OpenAI TTS 模型或 ElevenLabs 模型 ID）  
- `stability`、`similarityBoost`、`style`、`speed`、`useSpeakerBoost`  
- `applyTextNormalization`（`auto|on|off`）  
- `languageCode`（ISO 639-1）  
- `seed`

禁用全部模型覆盖：

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

可选白名单（启用服务提供商切换，同时保留其他参数可配置）：

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: true,
        allowProvider: true,
        allowSeed: false,
      },
    },
  },
}
```

## 每用户偏好设置

斜杠命令将本地覆盖写入 `prefsPath`（默认为：`~/.openclaw/settings/tts.json`；可通过 `OPENCLAW_TTS_PREFS` 或 `messages.tts.prefsPath` 覆盖）。

存储字段包括：

- `enabled`  
- `provider`  
- `maxLength`（摘要阈值；默认 1500 字符）  
- `summarize`（默认 `true`）

这些字段将覆盖该主机的 `messages.tts.*` 配置。

## 输出格式（固定）

- **Telegram**：Opus 语音消息（ElevenLabs 输出为 `opus_48000_64`，OpenAI 输出为 `opus`）。  
  - 48kHz / 64kbps 是语音消息的良好折中方案，且为实现圆形气泡所必需。  
- **其他渠道**：MP3（ElevenLabs 输出为 `mp3_44100_128`，OpenAI 输出为 `mp3`）。  
  - 44.1kHz / 128kbps 是语音清晰度的默认平衡点。  
- **Edge TTS**：使用 `edge.outputFormat`（默认为 `audio-24khz-48kbitrate-mono-mp3`）。  
  - `node-edge-tts` 接受 `outputFormat`，但 Edge 服务并非支持全部格式。citeturn2search0  
  - 输出格式取值遵循 Microsoft Speech 输出格式规范（含 Ogg/WebM Opus）。citeturn1search0  
  - Telegram `sendVoice` 支持 OGG/MP3/M4A；如需确保获得 Opus 语音消息，请使用 OpenAI/ElevenLabs。citeturn1search1  
  - 若配置的 Edge 输出格式失败，OpenClaw 将自动重试 MP3 格式。

OpenAI/ElevenLabs 输出格式为固定值；Telegram 语音消息用户体验要求使用 Opus 格式。

## 自动 TTS 行为

启用后，OpenClaw：

- 如果回复中已包含媒体内容或 ``MEDIA:`` 指令，则跳过 TTS。
- 如果回复极短（< 10 个字符），则跳过 TTS。
- 在启用时，使用 ``agents.defaults.model.primary``（或 ``summaryModel``）对长回复进行摘要。
- 将生成的音频附加到回复中。

如果回复长度超过 ``maxLength``，且摘要功能未启用（或摘要模型无有效 API 密钥），则跳过音频生成，仅发送常规文本回复。

## 流程图

````
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
````

## 斜杠命令用法

仅有一个命令：``/tts``。  
启用详情请参阅 [斜杠命令](/tools/slash-commands)。

Discord 注意事项：``/tts`` 是 Discord 内置命令，因此 OpenClaw 在 Discord 中将 ``/voice`` 注册为原生命令。文本形式的 ``/tts ...`` 仍可正常使用。

````
/tts off
/tts always
/tts inbound
/tts tagged
/tts status
/tts provider openai
/tts limit 2000
/tts summary off
/tts audio Hello from OpenClaw
````

注意事项：

- 命令需由已授权的发送者触发（白名单/所有者规则仍然适用）。
- 必须启用 ``commands.text`` 或原生命令注册。
- ``off|always|inbound|tagged`` 是按会话启用/禁用的开关（``/tts on`` 是 ``/tts always`` 的别名）。
- ``limit`` 和 ``summary`` 存储在本地偏好设置中，而非主配置文件中。
- ``/tts audio`` 生成一次性语音回复（不会切换 TTS 状态）。

## Agent 工具

``tts`` 工具将文本转为语音，并返回一个 ``MEDIA:`` 路径。当结果与 Telegram 兼容时，该工具会包含 ``[[audio_as_voice]]``，以便 Telegram 发送语音气泡。

## 网关 RPC

网关方法：

- ``tts.status``
- ``tts.enable``
- ``tts.disable``
- ``tts.convert``
- ``tts.setProvider``
- ``tts.providers``