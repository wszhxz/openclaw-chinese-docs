---
summary: "Deepgram transcription for inbound voice notes"
read_when:
  - You want Deepgram speech-to-text for audio attachments
  - You need a quick Deepgram config example
title: "Deepgram"
---
# Deepgram（音频转录）

Deepgram 是一款语音转文本 API。在 OpenClaw 中，它用于通过 `tools.media.audio` 实现**入站音频/语音备忘录的转录**。

启用后，OpenClaw 将音频文件上传至 Deepgram，并将生成的转录文本注入回复处理流程（即 `{{Transcript}}` + `[Audio]` 模块）。该过程**并非流式传输**；而是使用预录制音频转录端点。

官网：[https://deepgram.com](https://deepgram.com)  
文档：[https://developers.deepgram.com](https://developers.deepgram.com)

## 快速开始

1. 设置您的 API 密钥：

```
DEEPGRAM_API_KEY=dg_...
```

2. 启用该服务提供商：

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

## 配置选项

- `model`：Deepgram 模型 ID（默认值：`nova-3`）
- `language`：语言提示（可选）
- `tools.media.audio.providerOptions.deepgram.detect_language`：启用语言检测（可选）
- `tools.media.audio.providerOptions.deepgram.punctuate`：启用标点符号识别（可选）
- `tools.media.audio.providerOptions.deepgram.smart_format`：启用智能格式化（可选）

指定语言的示例：

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

指定 Deepgram 选项的示例：

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

- 认证遵循标准的服务提供商认证顺序；`DEEPGRAM_API_KEY` 是最简路径。
- 在使用代理时，可通过 `tools.media.audio.baseUrl` 和 `tools.media.audio.headers` 覆盖端点或请求头。
- 输出遵循与其他服务提供商相同的音频处理规则（如文件大小限制、超时机制、转录文本注入等）。