---
summary: "Voice Call plugin: outbound + inbound calls via Twilio/Telnyx/Plivo (plugin install + config + CLI)"
read_when:
  - You want to place an outbound voice call from OpenClaw
  - You are configuring or developing the voice-call plugin
title: "Voice Call Plugin"
---
# 语音通话 (插件)

通过插件为 OpenClaw 提供语音通话功能。支持外呼通知和带有入站策略的多轮对话。

当前提供商：

- `twilio` (可编程语音 + 媒体流)
- `telnyx` (呼叫控制 v2)
- `plivo` (语音 API + XML 转移 + GetInput 语音)
- `mock` (dev/无网络)

快速思维模型：

- 安装插件
- 重启网关
- 在 `plugins.entries.voice-call.config` 下进行配置
- 使用 `openclaw voicecall ...` 或 `voice_call` 工具

## 运行位置（本地 vs 远程）

语音通话插件在 **网关进程内部** 运行。

如果您使用远程网关，请在 **运行网关的机器** 上安装/配置插件，然后重启网关以加载它。

## 安装

### 选项 A：从 npm 安装（推荐）

```bash
openclaw plugins install @openclaw/voice-call
```

之后重启网关。

### 选项 B：从本地文件夹安装（开发，不复制）

```bash
openclaw plugins install ./extensions/voice-call
cd ./extensions/voice-call && pnpm install
```

之后重启网关。

## 配置

在 `plugins.entries.voice-call.config` 下设置配置：

```json5
{
  plugins: {
    entries: {
      "voice-call": {
        enabled: true,
        config: {
          provider: "twilio", // or "telnyx" | "plivo" | "mock"
          fromNumber: "+15550001234",
          toNumber: "+15550005678",

          twilio: {
            accountSid: "ACxxxxxxxx",
            authToken: "...",
          },

          telnyx: {
            apiKey: "...",
            connectionId: "...",
            // Telnyx webhook public key from the Telnyx Mission Control Portal
            // (Base64 string; can also be set via TELNYX_PUBLIC_KEY).
            publicKey: "...",
          },

          plivo: {
            authId: "MAxxxxxxxxxxxxxxxxxxxx",
            authToken: "...",
          },

          // Webhook server
          serve: {
            port: 3334,
            path: "/voice/webhook",
          },

          // Webhook security (recommended for tunnels/proxies)
          webhookSecurity: {
            allowedHosts: ["voice.example.com"],
            trustedProxyIPs: ["100.64.0.1"],
          },

          // Public exposure (pick one)
          // publicUrl: "https://example.ngrok.app/voice/webhook",
          // tunnel: { provider: "ngrok" },
          // tailscale: { mode: "funnel", path: "/voice/webhook" }

          outbound: {
            defaultMode: "notify", // notify | conversation
          },

          streaming: {
            enabled: true,
            streamPath: "/voice/stream",
          },
        },
      },
    },
  },
}
```

注意事项：

- Twilio/Telnyx 需要一个 **公开可访问** 的 webhook URL。
- Plivo 需要一个 **公开可访问** 的 webhook URL。
- `mock` 是本地开发提供商（无网络调用）。
- Telnyx 除非 `skipSignatureVerification` 为真，否则需要 `telnyx.publicKey` (或 `TELNYX_PUBLIC_KEY`)。
- `skipSignatureVerification` 仅用于本地测试。
- 如果您使用 ngrok 免费层，请将 `publicUrl` 设置为确切的 ngrok URL；签名验证始终强制执行。
- `tunnel.allowNgrokFreeTierLoopbackBypass: true` 仅当 `tunnel.provider="ngrok"` 和 `serve.bind` 为回环（ngrok 本地代理）时允许 Twilio 具有无效签名的 webhook。仅用于本地开发。
- Ngrok 免费层 URL 可能会更改或添加中间行为；如果 `publicUrl` 发生漂移，Twilio 签名将失败。对于生产环境，建议使用稳定域名或 Tailscale 漏斗。

## 过期通话清理器

使用 `staleCallReaperSeconds` 结束从未收到终端 webhook 的通话（例如，从未完成的通知模式通话）。默认值为 `0`（禁用）。

推荐范围：

- **生产环境：** 通知样式的流程使用 `120`–`300` 秒。
- 将此值设置为 **高于 `maxDurationSeconds`** 以便正常通话可以完成。一个好的起点是 `maxDurationSeconds + 30–60` 秒。

示例：

```json5
{
  plugins: {
    entries: {
      "voice-call": {
        config: {
          maxDurationSeconds: 300,
          staleCallReaperSeconds: 360,
        },
      },
    },
  },
}
```

## Webhook 安全性

当代理或隧道位于网关前面时，插件会重建用于签名验证的公共 URL。这些选项控制哪些转发头被信任。

`webhookSecurity.allowedHosts` 允许从转发头中列出的主机。

`webhookSecurity.trustForwardingHeaders` 信任没有白名单的转发头。

`webhookSecurity.trustedProxyIPs` 仅当请求远程 IP 匹配列表时才信任转发头。

具有稳定公共主机的示例：

```json5
{
  plugins: {
    entries: {
      "voice-call": {
        config: {
          publicUrl: "https://voice.example.com/voice/webhook",
          webhookSecurity: {
            allowedHosts: ["voice.example.com"],
          },
        },
      },
    },
  },
}
```

## 通话中的 TTS

语音通话使用核心 `messages.tts` 配置（OpenAI 或 ElevenLabs）进行通话中的流式语音。您可以在插件配置下使用 **相同的结构** 进行覆盖 — 它与 `messages.tts` 深度合并。

```json5
{
  tts: {
    provider: "elevenlabs",
    elevenlabs: {
      voiceId: "pMsXgVXv3BLzUgSXRplE",
      modelId: "eleven_multilingual_v2",
    },
  },
}
```

注意事项：

- **边缘 TTS 在语音通话中被忽略**（电话音频需要 PCM；边缘输出不可靠）。
- 当启用 Twilio 媒体流时使用核心 TTS；否则通话将回退到提供商的原生语音。

### 更多示例

仅使用核心 TTS（不覆盖）：

```json5
{
  messages: {
    tts: {
      provider: "openai",
      openai: { voice: "alloy" },
    },
  },
}
```

仅将通话覆盖为 ElevenLabs（其他地方保持核心默认）：

```json5
{
  plugins: {
    entries: {
      "voice-call": {
        config: {
          tts: {
            provider: "elevenlabs",
            elevenlabs: {
              apiKey: "elevenlabs_key",
              voiceId: "pMsXgVXv3BLzUgSXRplE",
              modelId: "eleven_multilingual_v2",
            },
          },
        },
      },
    },
  },
}
```

仅覆盖通话的 OpenAI 模型（深度合并示例）：

```json5
{
  plugins: {
    entries: {
      "voice-call": {
        config: {
          tts: {
            openai: {
              model: "gpt-4o-mini-tts",
              voice: "marin",
            },
          },
        },
      },
    },
  },
}
```

## 入站通话

入站策略默认为 `disabled`。要启用入站通话，请设置：

```json5
{
  inboundPolicy: "allowlist",
  allowFrom: ["+15550001234"],
  inboundGreeting: "Hello! How can I help?",
}
```

自动响应使用代理系统。调整：

- `responseModel`
- `responseSystemPrompt`
- `responseTimeoutMs`

## CLI

```bash
openclaw voicecall call --to "+15555550123" --message "Hello from OpenClaw"
openclaw voicecall continue --call-id <id> --message "Any questions?"
openclaw voicecall speak --call-id <id> --message "One moment"
openclaw voicecall end --call-id <id>
openclaw voicecall status --call-id <id>
openclaw voicecall tail
openclaw voicecall expose --mode funnel
```

## 代理工具

工具名称：`voice_call`

操作：

- `initiate_call` (message, to?, mode?)
- `continue_call` (callId, message)
- `speak_to_user` (callId, message)
- `end_call` (callId)
- `get_status` (callId)

此存储库附带匹配的技能文档 `skills/voice-call/SKILL.md`。

## 网关 RPC

- `voicecall.initiate` (`to?`, `message`, `mode?`)
- `voicecall.continue` (`callId`, `message`)
- `voicecall.speak` (`callId`, `message`)
- `voicecall.end` (`callId`)
- `voicecall.status` (`callId`)