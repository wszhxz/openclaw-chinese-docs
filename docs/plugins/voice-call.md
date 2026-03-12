---
summary: "Voice Call plugin: outbound + inbound calls via Twilio/Telnyx/Plivo (plugin install + config + CLI)"
read_when:
  - You want to place an outbound voice call from OpenClaw
  - You are configuring or developing the voice-call plugin
title: "Voice Call Plugin"
---
# 语音通话（插件）

通过插件为OpenClaw提供语音通话功能。支持外拨通知和带有内拨策略的多轮对话。

当前提供商：

- `twilio` (可编程语音 + 媒体流)
- `telnyx` (呼叫控制v2)
- `plivo` (语音API + XML传输 + GetInput语音)
- `mock` (开发/无网络)

快速理解模型：

- 安装插件
- 重启网关
- 在`plugins.entries.voice-call.config`下配置
- 使用`openclaw voicecall ...`或`voice_call`工具

## 运行位置（本地与远程）

语音通话插件运行在**网关进程中**。

如果您使用的是远程网关，请在**运行网关的机器上**安装/配置插件，然后重启网关以加载它。

## 安装

### 选项A：从npm安装（推荐）

```bash
openclaw plugins install @openclaw/voice-call
```

之后重启网关。

### 选项B：从本地文件夹安装（开发，无需复制）

```bash
openclaw plugins install ./extensions/voice-call
cd ./extensions/voice-call && pnpm install
```

之后重启网关。

## 配置

在`plugins.entries.voice-call.config`下设置配置：

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
            preStartTimeoutMs: 5000,
            maxPendingConnections: 32,
            maxPendingConnectionsPerIp: 4,
            maxConnections: 128,
          },
        },
      },
    },
  },
}
```

注意事项：

- Twilio/Telnyx需要一个**公开可访问的**webhook URL。
- Plivo需要一个**公开可访问的**webhook URL。
- `mock`是本地开发提供商（无网络调用）。
- 除非`skipSignatureVerification`为真，否则Telnyx需要`telnyx.publicKey`（或`TELNYX_PUBLIC_KEY`）。
- `skipSignatureVerification`仅用于本地测试。
- 如果您使用ngrok免费版，请将`publicUrl`设置为确切的ngrok URL；始终强制执行签名验证。
- 当`tunnel.provider="ngrok"`和`serve.bind`为回环（ngrok本地代理）时，`tunnel.allowNgrokFreeTierLoopbackBypass: true`允许具有无效签名的Twilio webhooks。仅用于本地开发。
- ngrok免费版URL可能会更改或添加中间行为；如果`publicUrl`漂移，Twilio签名将失败。对于生产环境，建议使用稳定的域名或Tailscale隧道。
- 流媒体安全默认设置：
  - `streaming.preStartTimeoutMs`关闭从未发送有效`start`帧的套接字。
  - `streaming.maxPendingConnections`限制未经身份验证的预启动套接字总数。
  - `streaming.maxPendingConnectionsPerIp`限制每个源IP的未经身份验证的预启动套接字数量。
  - `streaming.maxConnections`限制总打开的媒体流套接字数（待处理+活动）。

## 陈旧呼叫收割器

使用`staleCallReaperSeconds`结束从未收到终端webhook的呼叫（例如，从未完成的通知模式呼叫）。默认值为`0`（禁用）。

推荐范围：

- **生产环境：** 对于通知样式流程，`120`–`300`秒。
- 保持此值**高于`maxDurationSeconds`**以便正常呼叫可以完成。一个好的起点是`maxDurationSeconds + 30–60`秒。

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

## Webhook安全性

当代理或隧道位于网关前面时，插件会重构公共URL以进行签名验证。这些选项控制哪些转发头被信任。

`webhookSecurity.allowedHosts`允许列表中的主机转发头。

`webhookSecurity.trustForwardingHeaders`信任转发头而无需允许列表。

`webhookSecurity.trustedProxyIPs`仅在请求远程IP与列表匹配时信任转发头。

已为Twilio和Plivo启用webhook重放保护。重放的有效webhook请求会被确认但跳过副作用。

Twilio对话回合在`<Gather>`回调中包含每回合令牌，因此陈旧/重放的语音回调无法满足更新的待处理转录回合。

使用稳定公共主机的示例：

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

## 呼叫的TTS

语音通话使用核心`messages.tts`配置（OpenAI或ElevenLabs）进行通话中的流式语音。您可以在插件配置中使用**相同结构**覆盖它——它会与`messages.tts`深度合并。

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

- **Edge TTS在语音通话中被忽略**（电话音频需要PCM；Edge输出不可靠）。
- 当启用Twilio媒体流时，使用核心TTS；否则，呼叫将回退到提供商的原生语音。

### 更多示例

仅使用核心TTS（无覆盖）：

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

仅为呼叫覆盖到ElevenLabs（其他地方保持核心默认设置）：

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

仅为呼叫覆盖OpenAI模型（深度合并示例）：

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

## 入站呼叫

入站策略默认为`disabled`。要启用入站呼叫，请设置：

```json5
{
  inboundPolicy: "allowlist",
  allowFrom: ["+15550001234"],
  inboundGreeting: "Hello! How can I help?",
}
```

自动响应使用代理系统。调整参数：

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

- `initiate_call` (消息, to?, 模式?)
- `continue_call` (callId, 消息)
- `speak_to_user` (callId, 消息)
- `end_call` (callId)
- `get_status` (callId)

此仓库在`skills/voice-call/SKILL.md`处附带了一个匹配的技能文档。

## 网关RPC

- `voicecall.initiate` (`to?`, `message`, `mode?`)
- `voicecall.continue` (`callId`, `message`)
- `voicecall.speak` (`callId`, `message`)
- `voicecall.end` (`callId`)
- `voicecall.status` (`callId`)