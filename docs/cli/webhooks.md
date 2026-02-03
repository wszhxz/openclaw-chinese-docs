---
summary: "CLI reference for `openclaw webhooks` (webhook helpers + Gmail Pub/Sub)"
read_when:
  - You want to wire Gmail Pub/Sub events into OpenClaw
  - You want webhook helper commands
title: "webhooks"
---
# `openclaw webhooks`

Webhook 工具和集成（Gmail Pub/Sub，webhook 工具）。

相关：

- Webhooks: [Webhook](/automation/webhook)
- Gmail Pub/Sub: [Gmail Pub/Sub](/automation/gmail-pubsub)

## Gmail

```bash
openclaw webhooks gmail setup --account you@example.com
openclaw webhooks gmail run
```

详见 [Gmail Pub/Sub 文档](/automation/gmail-pubsub)。