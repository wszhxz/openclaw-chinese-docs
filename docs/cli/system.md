---
summary: "CLI reference for `openclaw system` (system events, heartbeat, presence)"
read_when:
  - You want to enqueue a system event without creating a cron job
  - You need to enable or disable heartbeats
  - You want to inspect system presence entries
title: "system"
---
启用<think>
Okay, I need to translate this English text into Chinese. Let me start by reading through the entire content to understand the context. The text is about a system called "openclaw" with commands related to events, heartbeats, and presence. 

First, the title is "openclaw system". I'll translate that as "openclaw 系统". Next, the system-level helpers for the Gateway: enqueue system events, control heartbeats, and view presence. The Gateway here is a specific term, so I'll keep it as "网关" since that's the standard translation. 

The common commands section has some bash commands. I need to make sure the command syntax is preserved but the descriptions are translated. For example, "openclaw system event --text "Check for urgent follow-ups" --mode now" becomes "openclaw system event --text "检查紧急跟进事项" --mode now". I'll keep the command structure the same but translate the text parts.

Moving to the "system event" section: Enqueue a system event on the main session. The next heartbeat will inject it as a "System:" line in the prompt. Use --mode now to trigger the heartbeat immediately; next-heartbeat waits for the next scheduled tick. I'll translate each part carefully, ensuring technical terms like "heartbeat" are correctly translated as "心跳" and "prompt" as "提示".

The flags section: --text is required, --mode has options, and --json for machine-readable output. I'll translate these flags and their descriptions accurately. 

For the "system heartbeat last|enable|disable" part, the commands are straightforward. "last" shows the last event, "enable" turns them back on, and "disable" pauses them. I'll make sure the translations reflect the actions correctly.

The "system presence" command lists current entries the Gateway knows about. I'll translate "presence" as "存在状态" and ensure the description is clear.

In the Notes section, "Requires a running Gateway reachable by your current config" becomes "需要一个可通过当前配置（本地或远程）访问的正在运行的网关". I'll check for any technical terms that might need specific translations.

I should also ensure that the structure remains the same, using headings and code blocks as in the original. Special characters like backticks and quotes should be preserved. Finally, I'll review the entire translation to make sure it's accurate and maintains the original meaning without any errors.
</think>

# `openclaw 系统`

网关的系统级辅助工具：入队系统事件、控制心跳、查看存在状态。

## 常用命令

```bash
openclaw system event --text "检查紧急跟进事项" --mode now
openclaw system heartbeat enable
openclaw system heartbeat last
openclaw system presence
```

## `system event`

在**主会话**中入队一个系统事件。下一个心跳将将其作为 `System:` 行注入提示中。使用 `--mode now` 立即触发心跳；`next-heartbeat` 会等待下一次计划的周期。

标志：

- `--text <text>`：必需的系统事件文本。
- `--mode <mode>`：`now` 或 `next-heartbeat`（默认）。
- `--json`：机器可读输出。

## `system heartbeat last|enable|disable`

心跳控制：

- `last`：显示最后一次心跳事件。
- `enable`：重新启用心跳（如果之前已禁用，请使用此命令）。
- `disable`：暂停心跳。

标志：

- `--json`：机器可读输出。

## `system presence`

列出网关已知的当前系统存在状态条目（节点、实例及其他类似状态行）。

标志：

- `--json`：机器可读输出。

## 说明

- 需要一个可通过当前配置（本地或远程）访问的正在运行的网关。
- 系统事件是临时的，不会在重启后保留。