---
summary: "RPC adapters for external CLIs (signal-cli, imsg) and gateway patterns"
read_when:
  - Adding or changing external CLI integrations
  - Debugging RPC adapters (signal-cli, imsg)
title: "RPC Adapters"
---
（<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context. The content is about RPC adapters in OpenClaw, specifically two patterns: Pattern A using signal-cli over HTTP and Pattern B using imsg via stdio. There are also guidelines for adapters.

First, I'll translate the headings. "RPC adapters" becomes "RPC适配器". The section about Pattern A mentions "signal-cli" as an HTTP daemon. I should make sure to keep the technical terms like JSON-RPC and SSE as they are, but maybe add Chinese explanations if needed. For example, "Event stream is SSE" could be "事件流为SSE" and note that SSE stands for Server-Sent Events, but maybe the original text doesn't need that expansion.

Next, the health probe URL: "/api/v1/check" should stay as is, but the description "Health probe" translates to "健康检查探针". The part about OpenClaw owning the lifecycle when channels.signal.autoStart is true needs to be clear. Maybe "当channels.signal.autoStart=true时，OpenClaw负责生命周期管理" would work.

For Pattern B, "stdio child process" is "标准输入输出子进程". The JSON-RPC line-delimited over stdin/stdout should be "通过标准输入/输出进行行分隔的JSON-RPC（每行一个JSON对象）". The note about no TCP port and no daemon required is straightforward: "无需TCP端口，无需守护进程".

The core methods listed: "watch.subscribe" → notifications, etc. I'll keep the method names as they are but translate the descriptions. For example, "watch.subscribe" → "通知" (method: "message") becomes "watch.subscribe → 通知（方法: 'message'）".

The guidelines section: "Gateway owns the process" translates to "网关拥有进程（启动/停止与提供者生命周期绑定）". Resilient RPC clients with timeouts and restarts on exit: "保持RPC客户端健壮性：超时处理，进程退出时重启". Stable IDs over display strings: "优先使用稳定ID（如chat_id）而非显示字符串".

I need to ensure that all technical terms are correctly translated and that the structure matches the original. Also, check for consistency in terms like "JSON-RPC" and URLs. Make sure that the links like [Signal](/channels/signal) are kept as is, but the text after the link is translated. For example, "See [Signal](/channels/signal) for setup and endpoints." becomes "参见 [Signal](/channels/signal) 了解设置和端点。".

I should also verify that the translation flows naturally in Chinese, maintaining the technical accuracy while ensuring readability. Let me go through each section again to catch any missed terms or formatting issues. Once done, review the entire translated text to ensure it's accurate and properly formatted.
</think>

# RPC适配器

OpenClaw通过JSON-RPC集成外部CLI。当前使用两种模式。

## 模式A：HTTP守护进程（signal-cli）

- `signal-cli`作为守护进程运行，通过HTTP实现JSON-RPC。
- 事件流为SSE（`/api/v1/events`）。
- 健康检查探针：`/api/v1/check`。
- 当`channels.signal.autoStart=true`时，OpenClaw负责生命周期管理。

参见 [Signal](/channels/signal) 了解设置和端点。

## 模式B：标准输入输出子进程（imsg）

- OpenClaw将`imsg rpc`作为子进程启动。
- JSON-RPC通过标准输入/输出进行行分隔（每行一个JSON对象）。
- 无需TCP端口，无需守护进程。

使用的内核方法：

- `watch.subscribe` → 通知（方法: "message"）
- `watch.unsubscribe`
- `send`
- `chats.list`（探针/诊断）

参见 [iMessage](/channels/imessage) 了解设置和寻址（推荐使用`chat_id`）。

## 适配器指南

- 网关拥有进程（启动/停止与提供者生命周期绑定）。
- 保持RPC客户端健壮性：超时处理，进程退出时重启。
- 优先使用稳定ID（如`chat_id`）而非显示字符串。