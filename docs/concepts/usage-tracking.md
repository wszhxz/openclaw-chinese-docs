---
summary: "Usage tracking surfaces and credential requirements"
read_when:
  - You are wiring provider usage/quota surfaces
  - You need to explain usage tracking behavior or auth requirements
title: "Usage Tracking"
---
# 使用情况跟踪

## 功能说明

- 直接从提供商的使用情况端点拉取提供商使用量/配额。
- 无估算成本；仅显示提供商报告的数据窗口。

## 显示位置

- 聊天中的 `/status`：表情丰富的状态卡片，显示会话令牌 + 预估成本（仅限API密钥）。提供商使用情况显示**当前模型提供商**的数据（如可用）。
- 聊天中的 `/usage off|tokens|full`：每个响应的使用情况页脚（OAuth仅显示令牌）。
- 聊天中的 `/usage cost`：从OpenClaw会话日志聚合的本地成本摘要。
- CLI：`openclaw status --usage` 打印每个提供商的完整分解。
- CLI：`openclaw channels list` 在提供商配置旁边打印相同的使用情况快照（使用 `--no-usage` 跳过）。
- macOS菜单栏：Context下的"Usage"部分（仅在可用时）。

## 提供商 + 凭据

- **Anthropic (Claude)**：认证配置文件中的OAuth令牌。
- **GitHub Copilot**：认证配置文件中的OAuth令牌。
- **Gemini CLI**：认证配置文件中的OAuth令牌。
- **Antigravity**：认证配置文件中的OAuth令牌。
- **OpenAI Codex**：认证配置文件中的OAuth令牌（存在时使用accountId）。
- **MiniMax**：API密钥（编码计划密钥；`MINIMAX_CODE_PLAN_KEY` 或 `MINIMAX_API_KEY`）；使用5小时编码计划窗口。
- **z.ai**：通过环境变量/配置/认证存储的API密钥。

如果没有匹配的OAuth/API凭据，使用情况将被隐藏。