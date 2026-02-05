---
summary: "Usage tracking surfaces and credential requirements"
read_when:
  - You are wiring provider usage/quota surfaces
  - You need to explain usage tracking behavior or auth requirements
title: "Usage Tracking"
---
# 使用跟踪

## 什么是使用跟踪

- 直接从提供商的使用端点拉取使用情况/配额。
- 没有估算成本；只有提供商报告的时间窗口。

## 显示位置

- `/status` 在聊天中：带有会话令牌+估算成本的表情符号丰富的状态卡片（仅限API密钥）。当可用时，显示**当前模型提供商**的使用情况。
- `/usage off|tokens|full` 在聊天中：每个响应的使用情况页脚（OAuth仅显示令牌）。
- `/usage cost` 在聊天中：从OpenClaw会话日志聚合的本地成本摘要。
- CLI: `openclaw status --usage` 打印每个提供商的完整细分。
- CLI: `openclaw channels list` 打印相同的使用情况快照以及提供商配置（使用 `--no-usage` 跳过）。
- macOS菜单栏：Context下的“使用”部分（仅在可用时显示）。

## 提供商 + 凭证

- **Anthropic (Claude)**: 认证配置文件中的OAuth令牌。
- **GitHub Copilot**: 认证配置文件中的OAuth令牌。
- **Gemini CLI**: 认证配置文件中的OAuth令牌。
- **Antigravity**: 认证配置文件中的OAuth令牌。
- **OpenAI Codex**: 认证配置文件中的OAuth令牌（如果存在则使用accountId）。
- **MiniMax**: API密钥（编码计划密钥；`MINIMAX_CODE_PLAN_KEY` 或 `MINIMAX_API_KEY`)；使用5小时编码计划窗口。
- **z.ai**: 通过env/config/auth存储的API密钥。

如果没有匹配的OAuth/API凭证，则隐藏使用情况。