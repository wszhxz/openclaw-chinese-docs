---
summary: "CLI reference for `openclaw agent` (send one agent turn via the Gateway)"
read_when:
  - You want to run one agent turn from scripts (optionally deliver reply)
title: "agent"
---
# `openclaw agent`

通过网关执行智能体回合（嵌入式请使用 `--local`）。
使用 `--agent <id>` 直接指定已配置的智能体。

传入至少一个会话选择器：

- `--to <dest>`
- `--session-id <id>`
- `--agent <id>`

相关：

- Agent 发送工具：[Agent send](/tools/agent-send)

## 选项

- `-m, --message <text>`：必需的消息体
- `-t, --to <dest>`：用于派生会话密钥的接收方
- `--session-id <id>`：显式会话 ID
- `--agent <id>`：智能体 ID；覆盖路由绑定
- `--thinking <off|minimal|low|medium|high|xhigh>`：智能体思考级别
- `--verbose <on|off>`：持久化该会话的详细级别
- `--channel <channel>`：交付通道；省略则使用主会话通道
- `--reply-to <target>`：交付目标覆盖
- `--reply-channel <channel>`：交付通道覆盖
- `--reply-account <id>`：交付账户覆盖
- `--local`：直接运行嵌入式智能体（在插件注册表预加载后）
- `--deliver`：将回复发送回所选通道/目标
- `--timeout <seconds>`：覆盖智能体超时时间（默认 600 或配置值）
- `--json`：输出 JSON

## 示例

```bash
openclaw agent --to +15555550123 --message "status update" --deliver
openclaw agent --agent ops --message "Summarize logs"
openclaw agent --session-id 1234 --message "Summarize inbox" --thinking medium
openclaw agent --to +15555550123 --message "Trace logs" --verbose on --json
openclaw agent --agent ops --message "Generate report" --deliver --reply-channel slack --reply-to "#reports"
openclaw agent --agent ops --message "Run locally" --local
```

## 注意事项

- 当网关请求失败时，网关模式会回退到嵌入式智能体。使用 `--local` 强制立即执行嵌入式模式。
- `--local` 仍会首先预加载插件注册表，因此插件提供的提供者、工具和通道在嵌入式运行期间保持可用。
- `--channel`、`--reply-channel` 和 `--reply-account` 影响回复交付，不影响会话路由。
- 当此命令触发 `models.json` 重新生成时，由 SecretRef 管理的提供者凭据将作为非敏感标记进行持久化（例如环境变量名、`secretref-env:ENV_VAR_NAME` 或 `secretref-managed`），而非解析后的秘密明文。
- 标记写入以源为准：OpenClaw 从活动源配置快照中持久化标记，而非从解析后的运行时密钥值中。