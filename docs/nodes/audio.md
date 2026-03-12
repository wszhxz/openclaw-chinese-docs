---
summary: "How inbound audio/voice notes are downloaded, transcribed, and injected into replies"
read_when:
  - Changing audio transcription or media handling
title: "Audio and Voice Notes"
---
# 音频 / 语音笔记 — 2026-01-17

## 当前支持的功能

- **媒体理解（音频）**：若已启用音频理解功能（或自动检测到），OpenClaw 将：
  1. 定位首个音频附件（本地路径或 URL），并在需要时下载。
  2. 在发送至每个模型条目前强制执行 `maxBytes`。
  3. 按顺序运行首个符合条件的模型条目（提供商或 CLI）。
  4. 若失败或跳过（因尺寸/超时限制），则尝试下一个条目。
  5. 成功后，将 `Body` 替换为一个 `[Audio]` 块，并设置 `{{Transcript}}`。
- **命令解析**：当转录成功时，`CommandBody`/`RawBody` 将被设为转录文本，以确保斜杠命令仍可正常工作。
- **详细日志记录**：在 `--verbose` 中，我们会记录转录任务的启动时间及替换正文的时间。

## 自动检测（默认行为）

若您**未配置模型**，且 `tools.media.audio.enabled` **未** 设置为 `false`，  
OpenClaw 将按以下顺序进行自动检测，并在首个可用选项处停止：

1. **本地 CLI 工具**（如已安装）
   - `sherpa-onnx-offline`（需安装 `SHERPA_ONNX_MODEL_DIR`，含 encoder/decoder/joiner/tokens）
   - `whisper-cli`（来自 `whisper-cpp`；使用 `WHISPER_CPP_MODEL` 或内置的 tiny 模型）
   - `whisper`（Python CLI；自动下载模型）
2. **Gemini CLI**（`gemini`），使用 `read_many_files`
3. **提供商密钥**（OpenAI → Groq → Deepgram → Google）

如需禁用自动检测，请设置 `tools.media.audio.enabled: false`。  
如需自定义检测顺序，请设置 `tools.media.audio.models`。  
注意：二进制文件检测在 macOS/Linux/Windows 上均为尽力而为；请确保 CLI 已加入 `PATH`（我们会展开 `~`），或通过完整命令路径显式指定 CLI 模型。

## 配置示例

### 提供商 + CLI 回退（OpenAI + Whisper CLI）

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        maxBytes: 20971520,
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          {
            type: "cli",
            command: "whisper",
            args: ["--model", "base", "{{MediaPath}}"],
            timeoutSeconds: 45,
          },
        ],
      },
    },
  },
}
```

### 仅提供商模式（带作用域门控）

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        scope: {
          default: "allow",
          rules: [{ action: "deny", match: { chatType: "group" } }],
        },
        models: [{ provider: "openai", model: "gpt-4o-mini-transcribe" }],
      },
    },
  },
}
```

### 仅提供商模式（Deepgram）

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "deepgram", model: "nova-3" }],
      },
    },
  },
}
```

### 仅提供商模式（Mistral Voxtral）

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "mistral", model: "voxtral-mini-latest" }],
      },
    },
  },
}
```

### 将转录文本回显至聊天（选择启用）

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        echoTranscript: true, // default is false
        echoFormat: '📝 "{transcript}"', // optional, supports {transcript}
        models: [{ provider: "openai", model: "gpt-4o-mini-transcribe" }],
      },
    },
  },
}
```

## 注意事项与限制

- 提供商认证遵循标准模型认证顺序（认证配置文件、环境变量、`models.providers.*.apiKey`）。
- 当使用 `provider: "deepgram"` 时，Deepgram 将读取 `DEEPGRAM_API_KEY`。
- Deepgram 配置详情参见：[Deepgram（音频转录）](/providers/deepgram)。
- Mistral 配置详情参见：[Mistral](/providers/mistral)。
- 音频提供商可通过 `tools.media.audio` 覆盖 `baseUrl`、`headers` 和 `providerOptions`。
- 默认大小上限为 20MB（`tools.media.audio.maxBytes`）。超出此限制的音频将被当前模型跳过，并尝试下一选项。
- 小于 1024 字节的极小/空音频文件会在提供商/CLI 转录前被跳过。
- 音频的默认 `maxChars` 为**未设置**（即返回完整转录文本）。可设置 `tools.media.audio.maxChars` 或各条目的 `maxChars` 来裁剪输出。
- OpenAI 的自动默认值为 `gpt-4o-mini-transcribe`；如需更高准确率，请设置 `model: "gpt-4o-transcribe"`。
- 使用 `tools.media.audio.attachments` 可处理多个语音笔记（`mode: "all"` + `maxAttachments`）。
- 转录文本可在模板中通过 `{{Transcript}}` 访问。
- `tools.media.audio.echoTranscript` 默认关闭；启用后将在代理处理前，将转录确认消息发回原始聊天。
- `tools.media.audio.echoFormat` 用于自定义回显文本（占位符：`{transcript}`）。
- CLI 标准输出上限为 5MB；请保持 CLI 输出简洁。

### 代理环境支持

基于提供商的音频转录功能支持标准的出站代理环境变量：

- `HTTPS_PROXY`
- `HTTP_PROXY`
- `https_proxy`
- `http_proxy`

若未设置任何代理环境变量，则使用直连方式。若代理配置格式错误，OpenClaw 将记录警告并回退至直连获取。

## 群组中的提及检测

当群组聊天中设置了 `requireMention: true` 时，OpenClaw 现在会在检查提及**之前**对音频进行转录。这使得即使语音笔记中包含提及，也能被正常处理。

**工作原理如下：**

1. 若语音消息无文本正文，且该群组要求提及触发，则 OpenClaw 执行一次“预检”转录。
2. 对转录文本检查提及模式（例如 `@BotName`、emoji 触发器等）。
3. 若检测到提及，该消息将继续进入完整回复流程。
4. 转录文本用于提及检测，从而让语音笔记可通过提及门控。

**回退行为：**

- 若预检转录失败（超时、API 错误等），消息将依据纯文本提及检测逻辑进行处理。
- 此机制确保混合消息（文本 + 音频）绝不会被错误丢弃。

**每 Telegram 群组/主题的退出选项：**

- 设置 `channels.telegram.groups.<chatId>.disableAudioPreflight: true` 可跳过该群组的预检转录提及检查。
- 设置 `channels.telegram.groups.<chatId>.topics.<threadId>.disableAudioPreflight` 可按主题覆盖（`true` 表示跳过，`false` 表示强制启用）。
- 默认为 `false`（当满足提及门控条件时启用预检）。

**示例：** 用户在启用了 `requireMention: true` 的 Telegram 群组中发送一条语音笔记：“Hey @Claude, what's the weather?”。该语音被转录，提及被识别，随后代理作出回复。

## 常见陷阱

- 作用域规则采用“首匹配胜出”原则。`chatType` 将被规范化为 `direct`、`group` 或 `room`。
- 请确保您的 CLI 以退出码 0 结束并输出纯文本；JSON 输出需通过 `jq -r .text` 进行转换。
- 对于 `parakeet-mlx`，若您传入 `--output-dir`，OpenClaw 将在 `--output-format` 为 `txt`（或省略）时读取 `<output-dir>/<media-basename>.txt`；非 `txt` 输出格式将回退至标准输出解析。
- 请保持超时设置合理（`timeoutSeconds`，默认 60 秒），以免阻塞回复队列。
- 预检转录仅处理**首个**音频附件以进行提及检测；其余音频将在主媒体理解阶段处理。