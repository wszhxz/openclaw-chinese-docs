---
summary: "Direct `openclaw agent` CLI runs (with optional delivery)"
read_when:
  - Adding or modifying the agent CLI entrypoint
title: "Agent Send"
---
# `openclaw agent` (direct agent runs)

`openclaw agent` runs a single agent turn without needing an inbound chat message.
By default it goes **through the Gateway**; add `--local` to force the embedded
runtime on the current machine.

## 行为

- 必需: `--message <text>`
- 会话选择:
  - `--to <dest>` 派生会话密钥（群组/频道目标保持隔离；直接聊天合并到 `main`），**或者**
  - `--session-id <id>` 通过id重用现有会话，**或者**
  - `--agent <id>` 直接针对配置的代理（使用该代理的 `main` 会话密钥）
- 运行与正常入站回复相同的嵌入式代理运行时。
- 思考/详细标志持久化到会话存储中。
- 输出:
  - 默认: 打印回复文本（加上 `MEDIA:<url>` 行）
  - `--json`: 打印结构化负载 + 元数据
- 使用 `--deliver` + `--channel` 可选地将输出发送回频道（目标格式匹配 `openclaw message --target`）。
- 使用 `--reply-channel`/`--reply-to`/`--reply-account` 覆盖交付而不更改会话。

如果网关不可达，CLI **回退** 到本地嵌入式运行。

## 示例

```bash
openclaw agent --to +15555550123 --message "status update"
openclaw agent --agent ops --message "Summarize logs"
openclaw agent --session-id 1234 --message "Summarize inbox" --thinking medium
openclaw agent --to +15555550123 --message "Trace logs" --verbose on --json
openclaw agent --to +15555550123 --message "Summon reply" --deliver
openclaw agent --agent ops --message "Generate report" --deliver --reply-channel slack --reply-to "#reports"
```

## 标志

- `--local`: 本地运行（需要在shell中设置模型提供商API密钥）
- `--deliver`: 将回复发送到选定的频道
- `--channel`: 交付频道 (`whatsapp|telegram|discord|googlechat|slack|signal|imessage`, 默认: `whatsapp`)
- `--reply-to`: 交付目标覆盖
- `--reply-channel`: 交付频道覆盖
- `--reply-account`: 交付账户ID覆盖
- `--thinking <off|minimal|low|medium|high|xhigh>`: 持久化思考级别（仅适用于GPT-5.2 + Codex模型）
- `--verbose <on|full|off>`: 持久化详细级别
- `--timeout <seconds>`: 覆盖代理超时
- `--json`: 输出结构化JSON