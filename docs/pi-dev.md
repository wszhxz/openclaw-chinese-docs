---
title: "Pi Development Workflow"
---
# Pi 开发工作流程

本指南总结了在 OpenClaw 中进行 pi 集成开发的合理工作流程。

## 类型检查和代码规范

- 类型检查和构建：`pnpm build`
- 代码规范检查：`pnpm lint`
- 格式检查：`pnpm format`
- 推送前的完整检查：`pnpm lint && pnpm build && pnpm test`

## 运行 Pi 测试

使用专用脚本运行 pi 集成测试集：

```bash
scripts/pi/run-tests.sh
```

若要包含实际提供者行为的实时测试：

```bash
scripts/pi/run-tests.sh --live
```

该脚本通过以下 glob 模式运行所有与 pi 相关的单元测试：

- `src/agents/pi-*.test.ts`
- `src/agents/pi-embedded-*.test.ts`
- `src/agents/pi-tools*.test.ts`
- `src/agents/pi-settings.test.ts`
- `src/agents/pi-tool-definition-adapter.test.ts`
- `src/agents/pi-extensions/*.test.ts`

## 手动测试

推荐流程：

- 以开发模式运行网关：
  - `pnpm gateway:dev`
- 直接触发代理：
  - `pnpm openclaw agent --message "Hello" --thinking low`
- 使用 TUI 进行交互式调试：
  - `pnpm tui`

对于工具调用行为，请提示选择 `read` 或 `exec` 操作，以便观察工具流式传输和负载处理。

## 清除状态重置

状态存储在 OpenClaw 的状态目录中。默认路径为 `~/.openclaw`。若设置了 `OPENCLAW_STATE_DIR` 环境变量，则使用该目录。

重置所有内容：

- `openclaw.json` 用于配置
- `credentials/` 用于认证配置文件和令牌
- `agents/<agentId>/sessions/` 用于代理会话历史记录
- `agents/<agentId>/sessions.json` 用于会话索引
- `sessions/` 若存在旧路径
- `workspace/` 若需要一个空白工作区

若您仅想重置会话，请删除 `agents/<agentId>/sessions/` 和 `agents/<agentId>/sessions.json`，若不需要重新认证，请保留 `credentials/`。

## 参考链接

- https://docs.openclaw.ai/testing
- https://docs.openclaw.ai/start/getting-started