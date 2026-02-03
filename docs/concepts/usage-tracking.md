---
summary: "Usage tracking surfaces and credential requirements"
read_when:
  - You are wiring provider usage/quota surfaces
  - You need to explain usage tracking behavior or auth requirements
title: "Usage Tracking"
---
# 使用跟踪

## 这是什么

- 从提供商的使用端点直接获取使用量/配额。
- 不包含预估费用；仅显示提供商报告的窗口。

## 显示位置

- 聊天中的 `/status`：包含表情符号的丰富状态卡片，显示会话令牌 + 预估费用（仅 API 密钥）。当可用时，显示当前模型提供商的使用量。
- 聊天中的 `/usage off|tokens|full`：每条回复的使用量页脚（OAuth 仅显示令牌）。
- 聊天中的 `/usage cost`：从 OpenClaw 会话日志汇总的本地费用摘要。
- CLI：`openclaw status --usage` 会打印每个提供商的完整使用量明细。
- CLI：`openclaw channels list` 会打印与提供商配置相同的使用量快照（使用 `--no-usage` 可跳过）。
- macOS 状态栏：在“上下文”下的“使用量”部分（仅在可用时显示）。

## 提供商 + 凭据

- **Anthropic (Claude)**：OAuth 令牌存储在授权配置文件中。
- **GitHub Copilot**：OAuth 令牌存储在授权配置文件中。
- **Gemini CLI**：OAuth 令牌存储在授权配置文件中。
- **Antigravity**：OAuth 令牌存储在授权配置文件中。
- **OpenAI Codex**：OAuth 令牌存储在授权配置文件中（若存在则使用 accountId）。
- **MiniMax**：API 密钥（编码计划密钥；`MINIMAX_CODE_PLAN_KEY` 或 `MINIMAX_API_KEY`）；使用 5 小时编码计划窗口。
- **z.ai**：通过环境/配置/授权存储获取 API 密钥。

如果不存在匹配的 OAuth/API 凭据，使用量将被隐藏。