---
summary: "Usage tracking surfaces and credential requirements"
read_when:
  - You are wiring provider usage/quota surfaces
  - You need to explain usage tracking behavior or auth requirements
title: "Usage Tracking"
---
# 使用情况跟踪

## 它是什么

- 直接从各提供商的用量端点拉取其用量/配额信息。
- 不提供预估费用；仅显示提供商报告的时间窗口内的实际用量。

## 在何处显示

- `/status` 在聊天界面中：富含表情符号的状态卡片，显示会话 Token 数量 + 预估费用（仅限 API 密钥）。当可用时，**当前模型提供商** 的用量信息将在此处显示。
- `/usage off|tokens|full` 在聊天界面中：每个响应下方的用量页脚（OAuth 方式仅显示 Token 数量）。
- `/usage cost` 在聊天界面中：基于 OpenClaw 会话日志聚合生成的本地费用汇总。
- CLI：`openclaw status --usage` 打印完整的、按提供商划分的用量明细。
- CLI：`openclaw channels list` 打印相同的用量快照，并附带提供商配置信息（可使用 `--no-usage` 跳过该配置信息）。
- macOS 菜单栏：“Context”（上下文）下的“Usage”（用量）部分（仅在可用时显示）。

## 提供商及凭证

- **Anthropic（Claude）**：认证配置文件中的 OAuth Token。
- **GitHub Copilot**：认证配置文件中的 OAuth Token。
- **Gemini CLI**：认证配置文件中的 OAuth Token。
- **Antigravity**：认证配置文件中的 OAuth Token。
- **OpenAI Codex**：认证配置文件中的 OAuth Token（如存在，则使用 `accountId`）。
- **MiniMax**：API 密钥（编程计划密钥；`MINIMAX_CODE_PLAN_KEY` 或 `MINIMAX_API_KEY`）；采用 5 小时编程计划时间窗口。
- **z.ai**：通过环境变量 / 配置 / 认证存储提供的 API 密钥。

若不存在匹配的 OAuth 或 API 凭证，则不显示用量信息。