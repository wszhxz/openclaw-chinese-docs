---
title: "Pi Development Workflow"
summary: "Developer workflow for Pi integration: build, test, and live validation"
read_when:
  - Working on Pi integration code or tests
  - Running Pi-specific lint, typecheck, and live test flows
---
# Pi 开发工作流

本指南总结了在 OpenClaw 中进行 pi 集成的合理工作流程。

## 类型检查与代码检查

- 类型检查与构建：`pnpm build`
- 代码检查：`pnpm lint`
- 格式检查：`pnpm format`
- 推送前完整门禁：`pnpm lint && pnpm build && pnpm test`

## 运行 Pi 测试

直接使用 Vitest 运行专注于 Pi 的测试集：

```bash
pnpm test -- \
  "src/agents/pi-*.test.ts" \
  "src/agents/pi-embedded-*.test.ts" \
  "src/agents/pi-tools*.test.ts" \
  "src/agents/pi-settings.test.ts" \
  "src/agents/pi-tool-definition-adapter*.test.ts" \
  "src/agents/pi-extensions/**/*.test.ts"
```

若要包含实时提供者演练：

```bash
OPENCLAW_LIVE_TEST=1 pnpm test -- src/agents/pi-embedded-runner-extraparams.live.test.ts
```

这涵盖了主要的 Pi 单元测试套件：

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

对于工具调用行为，请提示执行 `read` 或 `exec` 操作，以便查看工具流式传输和负载处理。

## 完全重置

状态保存在 OpenClaw 状态目录下。默认值为 `~/.openclaw`。如果设置了 `OPENCLAW_STATE_DIR`，则使用该目录。

要重置所有内容：

- `openclaw.json` 用于配置
- `credentials/` 用于认证配置和令牌
- `agents/<agentId>/sessions/` 用于代理会话历史
- `agents/<agentId>/sessions.json` 用于会话索引
- `sessions/` 如果存在旧路径
- `workspace/` 如果您想要空白工作区

如果您只想重置会话，请删除该代理的 `agents/<agentId>/sessions/` 和 `agents/<agentId>/sessions.json`。如果您不想重新认证，请保留 `credentials/`。

## 参考资料

- [https://docs.openclaw.ai/testing](https://docs.openclaw.ai/testing)
- [https://docs.openclaw.ai/start/getting-started](https://docs.openclaw.ai/start/getting-started)