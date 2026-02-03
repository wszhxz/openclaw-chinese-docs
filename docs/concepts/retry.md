---
summary: "Retry policy for outbound provider calls"
read_when:
  - Updating provider retry behavior or defaults
  - Debugging provider send errors or rate limits
title: "Retry Policy"
---
# 重试策略

## 目标

- 按 HTTP 请求重试，而非多步骤流程。
- 通过仅重试当前步骤来保持顺序。
- 避免重复非幂等操作。

## 默认值

- 尝试次数: 3
- 最大延迟上限: 30000 毫秒
- 抖动: 0.1 (10%)
- 提供商默认值：
  - Telegram 最小延迟: 400 毫秒
  - Discord 最小延迟: 500 毫秒

## 行为

### Discord

- 仅在速率限制错误（HTTP 429）时重试。
- 在可用时使用 Discord 的 `retry_after`，否则使用指数退避。

### Telegram

- 在瞬时错误（429、超时、连接/重置/关闭、暂时不可用）时重试。
- 在可用时使用 `retry_after`，否则使用指数退避。
- Markdown 解析错误不会重试，将回退为纯文本。

## 配置

在 `~/.openclaw/openclaw.json` 中为每个提供者设置重试策略：

```json5
{
  channels: {
    telegram: {
      retry: {
        attempts: 3,
        minDelayMs: 400,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
    },
    discord: {
      retry: {
        attempts: 3,
        minDelayMs: 500,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
    },
  },
}
```

## 说明

- 重试按请求（消息发送、媒体上传、反应、投票、贴纸）进行。
- 复合流程不会重试已完成的步骤。