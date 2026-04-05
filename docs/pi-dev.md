---
title: "Pi Development Workflow"
summary: "Developer workflow for Pi integration: build, test, and live validation"
read_when:
  - Working on Pi integration code or tests
  - Running Pi-specific lint, typecheck, and live test flows
---
# Pi 开发工作流

本指南总结了在 OpenClaw 中进行 Pi 集成的合理工作流程。

## 类型检查与代码规范检查

- 默认本地门禁：`pnpm check`
- 构建门禁：当更改可能影响构建输出、打包或懒加载/模块边界时，使用 `pnpm build`
- 针对重度 Pi 更改的完整落地门禁：`pnpm check && pnpm test`

## 运行 Pi 测试

直接使用 Vitest 运行专注于 Pi 的测试集：

```bash
pnpm test \
  "src/agents/pi-*.test.ts" \
  "src/agents/pi-embedded-*.test.ts" \
  "src/agents/pi-tools*.test.ts" \
  "src/agents/pi-settings.test.ts" \
  "src/agents/pi-tool-definition-adapter*.test.ts" \
  "src/agents/pi-hooks/**/*.test.ts"
```

若要包含实时提供者练习：

```bash
OPENCLAW_LIVE_TEST=1 pnpm test src/agents/pi-embedded-runner-extraparams.live.test.ts
```

这涵盖了主要的 Pi 单元测试套件：

- `src/agents/pi-*.test.ts`
- `src/agents/pi-embedded-*.test.ts`
- `src/agents/pi-tools*.test.ts`
- `src/agents/pi-settings.test.ts`
- `src/agents/pi-tool-definition-adapter.test.ts`
- `src/agents/pi-hooks/*.test.ts`

## 手动测试

推荐流程：

- 以开发模式运行网关：
  - `pnpm gateway:dev`
- 直接触发代理：
  - `pnpm openclaw agent --message "Hello" --thinking low`
- 使用 TUI 进行交互式调试：
  - `pnpm tui`

为了查看工具调用行为，请提示执行 `read` 或 `exec` 操作，以便观察工具流式传输和负载处理。

## 彻底重置

状态保存在 OpenClaw 状态目录下。默认为 `~/.openclaw`。如果设置了 `OPENCLAW_STATE_DIR`，则使用该目录。

要重置所有内容：

- `openclaw.json` 用于配置
- `agents/<agentId>/agent/auth-profiles.json` 用于模型认证配置文件（API 密钥 + OAuth）
- `credentials/` 用于仍存储在认证配置文件之外的提供者/通道状态
- `agents/<agentId>/sessions/` 用于代理会话历史
- `agents/<agentId>/sessions/sessions.json` 用于会话索引
- 如果存在旧路径，使用 `sessions/`
- 如果需要空白工作区，使用 `workspace/`

如果您只想重置会话，请删除该代理的 `agents/<agentId>/sessions/`。如果您想保留认证信息，请保留 `agents/<agentId>/agent/auth-profiles.json` 以及位于 `credentials/` 下的任何提供者状态。

## 参考资料

- [测试](/help/testing)
- [入门指南](/start/getting-started)