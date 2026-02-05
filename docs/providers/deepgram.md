---
summary: "Deepgram transcription for inbound voice notes"
read_when:
  - You want Deepgram speech-to-text for audio attachments
  - You need a quick Deepgram config example
title: "Deepgram"
---
# Deepgram (音频转录)

Deepgram 是一个语音转文字 API。在 OpenClaw 中，它用于 **入站音频/语音笔记转录** 通过 `tools.media.audio`。

启用后，OpenClaw 将音频文件上传到 Deepgram，并将转录内容注入回复管道 (`{{Transcript}}` + `[Audio]` 块)。这不是 **流式传输**；它使用预录制转录端点。

网站: https://deepgram.com  
文档: https://developers.deepgram.com

## 快速开始

1. 设置您的 API 密钥：

```
DEEPGRAM_API_KEY=dg_...
```

2. 启用提供者：

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

## 选项

- `model`: Deepgram 模型 ID（默认: `nova-3`）
- `language`: 语言提示（可选）
- `tools.media.audio.providerOptions.deepgram.detect_language`: 启用语言检测（可选）
- `tools.media.audio.providerOptions.deepgram.punctuate`: 启用标点符号（可选）
- `tools.media.audio.providerOptions.deepgram.smart_format`: 启用智能格式化（可选）

带有语言的示例：

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "deepgram", model: "nova-3", language: "en" }],
      },
    },
  },
}
```

带有 Deepgram 选项的示例：

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        providerOptions: {
          deepgram: {
            detect_language: true,
            punctuate: true,
            smart_format: true,
          },
        },
        models: [{ provider: "deepgram", model: "nova-3" }],
      },
    },
  },
}
```

## 注意事项

- 认证遵循标准提供者认证顺序；`DEEPGRAM_API_KEY` 是最简单的路径。
- 使用代理时，使用 `tools.media.audio.baseUrl` 和 `tools.media.audio.headers` 覆盖端点或标题。
- 输出遵循与其他提供者相同的音频规则（大小限制、超时、转录注入）。