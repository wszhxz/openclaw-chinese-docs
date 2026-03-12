---
title: "Pi Development Workflow"
summary: "Developer workflow for Pi integration: build, test, and live validation"
read_when:
  - Working on Pi integration code or tests
  - Running Pi-specific lint, typecheck, and live test flows
---
# Pi 开发工作流

本指南总结了在 OpenClaw 中开发 pi 集成时一种合理的工作流程。

## 类型检查与代码规范检查

- 类型检查并构建：`pnpm build`  
- 代码规范检查（Lint）：`pnpm lint`  
- 格式检查：`pnpm format`  
- 推送前完整门禁检查：`pnpm lint && pnpm build && pnpm test`  

## 运行 Pi 测试

直接使用 Vitest 运行面向 Pi 的测试集：

```bash
pnpm test -- \
  "src/agents/pi-*.test.ts" \
  "src/agents/pi-embedded-*.test.ts" \
  "src/agents/pi-tools*.test.ts" \
  "src/agents/pi-settings.test.ts" \
  "src/agents/pi-tool-definition-adapter*.test.ts" \
  "src/agents/pi-extensions/**/*.test.ts"
```

如需包含实时 provider 演练，请执行：

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

推荐的操作流程如下：

- 以开发模式运行网关：  
  - `pnpm gateway:dev`  
- 直接触发 agent：  
  - `pnpm openclaw agent --message "Hello" --thinking low`  
- 使用 TUI 进行交互式调试：  
  - `pnpm tui`  

针对工具调用行为，可提示执行一个 `read` 或 `exec` 操作，以便观察工具流式输出及有效载荷处理过程。

## 清空状态重置

状态数据存放在 OpenClaw 状态目录下，默认路径为 `~/.openclaw`。若设置了环境变量 `OPENCLAW_STATE_DIR`，则改用该目录。

要彻底重置所有状态，请执行以下操作：

- `openclaw.json`：重置配置  
- `credentials/`：重置认证配置文件和令牌  
- `agents/<agentId>/sessions/`：重置 agent 会话历史  
- `agents/<agentId>/sessions.json`：重置会话索引  
- `sessions/`：清理遗留路径（如存在）  
- `workspace/`：创建空白工作区  

若仅需重置会话，可删除对应 agent 的 `agents/<agentId>/sessions/` 和 `agents/<agentId>/sessions.json`；如不希望重新认证，请保留 `credentials/`。

## 参考资料

- [https://docs.openclaw.ai/testing](https://docs.openclaw.ai/testing)  
- [https://docs.openclaw.ai/start/getting-started](https://docs.openclaw.ai/start/getting-started)