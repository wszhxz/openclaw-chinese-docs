---
summary: "Poll sending via gateway + CLI"
read_when:
  - Adding or modifying poll support
  - Debugging poll sends from the CLI or gateway
title: "Polls"
---
调度<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context. The content is about polling features across different channels like WhatsApp, Discord, and MS Teams, along with CLI commands and API details.

First, I'll translate the headers and section titles. "Polls" becomes "投票". "Supported channels" is "支持的渠道". For the list of channels, I'll make sure to use the correct terms for each platform. WhatsApp is "WhatsApp（网页渠道）", Discord remains "Discord", and MS Teams is "MS Teams（自适应卡片）".

Next, the CLI section. The code blocks need to be accurately translated, keeping the syntax the same but converting the commands and options. For example, "openclaw message poll" becomes "openclaw message poll", but the parameters like "--target" should stay as they are since they're command-line flags. I'll ensure that the examples are correctly formatted with proper indentation and code block markers.

Looking at the options section, I'll translate each key-value pair. Terms like "--channel" become "--channel", and the descriptions need to be in Chinese. For instance, "--poll-multi" is "允许选择多个选项".

Moving to the Gateway RPC section, the method and params need precise translation. "Method: poll" becomes "方法: poll". The parameters like "to" (string, required) should be translated to "to（字符串，必填）".

In the Channel differences section, I have to be careful with technical terms. For example, "Adaptive Card polls (OpenClaw-managed)" becomes "自适应卡片投票（由OpenClaw管理）". Also, note that MS Teams doesn't have a native poll API, so I'll translate that accurately.

The Agent tool (Message) section mentions using the "message" tool with "poll" action. I'll ensure that the parameters are correctly translated, like "pollQuestion" to "pollQuestion" and "pollOption" to "pollOption". The note about Discord not having a "pick exactly N" mode should be clear in Chinese, explaining that "pollMulti" maps to multi-select.

Finally, the note about Teams polls requiring the gateway to stay online to record votes in the specified JSON file needs to be accurately translated, making sure the file path is correctly represented.

Throughout the translation, I'll maintain the structure and formatting, ensuring that code blocks, lists, and sections are preserved. I'll also check for consistency in terminology and ensure that technical terms are correctly translated without losing their specific meanings. It's important to keep the instructions clear so that users can follow the steps without confusion. After translating, I'll review the text to catch any errors or inconsistencies, making sure the final translation is accurate and easy to understand.
</think>

# 投票

## 支持的渠道

- WhatsApp（网页渠道）
- Discord
- MS Teams（自适应卡片）

## CLI

```bash
# WhatsApp
openclaw message poll --target +15555550123 \
  --poll-question "今天午餐？" --poll-option "是" --poll-option "否" --poll-option "可能"
openclaw message poll --target 123456789@g.us \
  --poll-question "会议时间？" --poll-option "上午10点" --poll-option "下午2点" --poll-option "下午4点" --poll-multi

# Discord
openclaw message poll --channel discord --target channel:123456789 \
  --poll-question "零食？" --poll-option "披萨" --poll-option "寿司"
openclaw message poll --channel discord --target channel:123456789 \
  --poll-question "计划？" --poll-option "A" --poll-option "B" --poll-duration-hours 48

# MS Teams
openclaw message poll --channel msteams --target conversation:19:abc@thread.tacv2 \
  --poll-question "午餐？" --poll-option "披萨" --poll-option "寿司"
```

选项：

- `--channel`: `whatsapp`（默认值）、`discord` 或 `msteams`
- `--poll-multi`: 允许选择多个选项
- `--poll-duration-hours`: 仅适用于 Discord（省略时默认为 24 小时）

## 网关 RPC

方法：`poll`

参数：

- `to`（字符串，必填）
- `question`（字符串，必填）
- `options`（字符串数组，必填）
- `maxSelections`（数字，可选）
- `durationHours`（数字，可选）
- `channel`（字符串，可选，默认值：`whatsapp`）
- `idempotencyKey`（字符串，必填）

## 渠道差异

- WhatsApp：2-12 个选项，`maxSelections` 必须在选项数量范围内，忽略 `durationHours`。
- Discord：2-10 个选项，`duration
- MS Teams：自适应卡片投票（由 OpenClaw 管理）。无原生投票 API；`durationHours` 将被忽略。

## 代理工具（消息）

使用 `message` 工具并执行 `poll` 动作（`to`、`pollQuestion`、`pollOption`，可选 `pollMulti`、`pollDurationHours`、`channel`）。

注意：Discord 没有“精确选择 N 项”的模式；`pollMulti` 映射为多选。Teams 投票以自适应卡片形式呈现，需保持网关在线以在 `~/.openclaw/msteams-polls.json` 中记录投票。