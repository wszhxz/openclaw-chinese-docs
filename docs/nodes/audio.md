---
summary: "How inbound audio/voice notes are downloaded, transcribed, and injected into replies"
read_when:
  - Changing audio transcription or media handling
title: "Audio and Voice Notes"
---
# 音频/语音笔记 — 2026-01-17

## 工作原理

- **媒体理解（音频）**：如果启用了音频理解（或自动检测），OpenClaw：
  1. 定位第一个音频附件（本地路径或URL），如果需要则下载。
  2. 在发送到每个模型条目之前强制执行 `maxBytes`。
  3. 按顺序运行第一个符合条件的模型条目（提供者或CLI）。
  4. 如果失败或跳过（大小/超时），则尝试下一个条目。
  5. 成功后，它将 `Body` 替换为一个 `[Audio]` 块并设置 `{{Transcript}}`。
- **命令解析**：当转录成功时，将 `CommandBody`/`RawBody` 设置为转录内容，以便斜杠命令仍然有效。
- **详细日志记录**：在 `--verbose` 中，我们记录转录运行的时间以及替换正文的时间。

## 自动检测（默认）

如果您 **没有配置模型** 并且 `tools.media.audio.enabled` **不是** 设置为 `false`，
OpenClaw 按照以下顺序自动检测并在第一个可用选项处停止：

1. **本地 CLI**（如果已安装）
   - `sherpa-onnx-offline`（需要 `SHERPA_ONNX_MODEL_DIR` 包含编码器/解码器/连接器/标记）
   - `whisper-cli`（来自 `whisper-cpp`；使用 `WHISPER_CPP_MODEL` 或捆绑的小型模型）
   - `whisper`（Python CLI；自动下载模型）
2. **Gemini CLI** (`gemini`) 使用 `read_many_files`
3. **提供者密钥**（OpenAI → Groq → Deepgram → Google）

要禁用自动检测，请设置 `tools.media.audio.enabled: false`。
要自定义，请设置 `tools.media.audio.models`。
注意：二进制检测在 macOS/Linux/Windows 上是尽力而为；确保 CLI 在 `PATH`（我们扩展 `~`），或者使用完整命令路径显式设置 CLI 模型。

## 配置示例

### 提供者 + CLI 备用（OpenAI + Whisper CLI）

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

### 仅提供者带范围门控

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

### 仅提供者（Deepgram）

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

## 注意事项与限制

- 提供者认证遵循标准模型认证顺序（认证配置文件、环境变量、`models.providers.*.apiKey`）。
- Deepgram 在使用 `provider: "deepgram"` 时会拾取 `DEEPGRAM_API_KEY`。
- Deepgram 设置详情：[Deepgram (音频转录)](/providers/deepgram)。
- 音频提供者可以通过 `tools.media.audio` 覆盖 `baseUrl`，`headers` 和 `providerOptions`。
- 默认大小上限为 20MB (`tools.media.audio.maxBytes`)。超出大小的音频会被跳过该模型并尝试下一个条目。
- 默认音频的 `maxChars` 是 **未设置**（完整转录）。设置 `tools.media.audio.maxChars` 或每个条目的 `maxChars` 以修剪输出。
- OpenAI 的自动默认值是 `gpt-4o-mini-transcribe`；设置 `model: "gpt-4o-transcribe"` 以提高准确性。
- 使用 `tools.media.audio.attachments` 处理多个语音笔记 (`mode: "all"` + `maxAttachments`)。
- 转录内容对模板可用为 `{{Transcript}}`。
- CLI 标准输出被限制（5MB）；保持 CLI 输出简洁。

## 群组中的提及检测

当 `requireMention: true` 对于群聊设置时，OpenClaw 现在会在检查提及 **之前** 转录音频。这允许即使包含提及的语音笔记也能被处理。

**工作原理：**

1. 如果语音消息没有文本正文且群组需要提及，OpenClaw 执行“预检”转录。
2. 检查转录内容中的提及模式（例如，`@BotName`，表情符号触发器）。
3. 如果找到提及，则消息通过完整的回复管道进行处理。
4. 使用转录内容进行提及检测，使语音笔记能够通过提及门控。

**回退行为：**

- 如果预检期间转录失败（超时、API 错误等），则根据仅文本提及检测处理消息。
- 这确保了混合消息（文本 + 音频）永远不会被错误地丢弃。

**示例：** 用户在一个设置了 `requireMention: true` 的 Telegram 群组中发送了一条语音笔记，内容为“Hey @Claude, what's the weather?”。语音笔记被转录，检测到提及，并且代理回复。

## 注意事项

- 作用域规则使用首次匹配获胜。`chatType` 规范化为 `direct`，`group` 或 `room`。
- 确保您的 CLI 退出状态为 0 并打印纯文本；JSON 需要通过 `jq -r .text` 进行处理。
- 保持超时合理 (`timeoutSeconds`，默认 60 秒）以避免阻塞回复队列。
- 预检转录仅处理用于提及检测的 **第一个** 音频附件。其他音频在主要媒体理解阶段进行处理。