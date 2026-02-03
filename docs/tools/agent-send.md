---
summary: "Direct `openclaw agent` CLI runs (with optional delivery)"
read_when:
  - Adding or modifying the agent CLI entrypoint
title: "Agent Send"
---
# `openclaw agent`（直接代理运行）

`openclaw agent` 可在无需入站聊天消息的情况下运行单个代理回合。
默认情况下，它会通过**网关**运行；添加 `--local` 可强制在当前机器上使用嵌入式运行时。

## 行为

- 必需参数：`--message <文本>`
- 会话选择：
  - `--to <目标>` 通过目标推导会话密钥（群组/频道目标保持隔离；直接聊天合并到 `main`），**或**
  - `--session-id <id>` 通过指定 ID 重用现有会话，**或**
  - `--agent <id>` 直接指向配置的代理（使用该代理的 `main` 会话密钥）
- 运行与常规入站回复相同的嵌入式代理运行时。
- 思考/详细模式标志会持久化到会话存储中。
- 输出：
  - 默认：打印回复文本（加上 `MEDIA:<url>` 行）
  - `--json`：打印结构化负载 + 元数据
- 可选地通过 `--deliver` + `--channel` 将回复发送回频道（目标格式与 `openclaw message --target` 一致）。
- 使用 `--reply-channel`/`--reply-to`/`--reply-account` 可覆盖发送目标，而不改变会话。

如果网关不可达，CLI **将回退**到本地嵌入式运行。

## 示例

```bash
openclaw agent --to +15555550123 --message "状态更新"
openclaw agent --agent ops --message "汇总日志"
openclaw agent --session-id 1234 --message "汇总收件箱" --thinking medium
openclaw agent --to +15555550123 --message "追踪日志" --verbose on --json
openclaw agent --to +15555550123 --message "召唤回复" --deliver
openclaw agent --agent ops --message "生成报告" --deliver --reply-channel slack --reply-to "#reports"
```

## 参数

- `--local`：本地运行（需在 shell 中配置模型提供商 API 密钥）
- `--deliver`：将回复发送到选定的频道
- `--channel`：发送频道（`whatsapp|telegram|discord|googlechat|slack|signal|imessage`，默认：`whatsapp`）
- `--reply-to`：发送目标覆盖
- `--reply-channel`：发送频道覆盖
- `--reply-account`：发送账户 ID 覆盖
- `--thinking <关|最小|低|中|高|极高>`：持久化思考级别（仅限 GPT-5.2 + Codex 模型）
- `--verbose <开|完整|关>`：持久化详细级别
- `--timeout <秒数>`：覆盖代理超时时间
- `--json`：输出结构化 JSON