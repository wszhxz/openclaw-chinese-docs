---
title: "Pi Development Workflow"
---
# Pi 开发工作流程

本指南总结了在 OpenClaw 中进行 pi 集成工作的合理工作流程。

## 类型检查和代码规范检查

- 类型检查和构建: `pnpm build`
- 代码规范检查: `pnpm lint`
- 格式检查: `pnpm format`
- 提交前进行全面检查: `pnpm lint && pnpm build && pnpm test`

## 运行 Pi 测试

使用专用脚本运行 pi 集成测试集：

```bash
scripts/pi/run-tests.sh
```

要包含测试实时提供者行为的实时测试：

```bash
scripts/pi/run-tests.sh --live
```

该脚本通过这些通配符运行所有 pi 相关的单元测试：

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

对于工具调用行为，提示执行 `read` 或 `exec` 操作，以便您可以查看工具流和负载处理。

## 清空重置

状态存储在 OpenClaw 状态目录下。默认是 `~/.openclaw`。如果设置了 `OPENCLAW_STATE_DIR`，则使用该目录。

要重置所有内容：

- `openclaw.json` 用于配置
- `credentials/` 用于身份验证配置文件和令牌
- `agents/<agentId>/sessions/` 用于代理会话历史
- `agents/<agentId>/sessions.json` 用于会话索引
- `sessions/` 如果存在旧路径
- `workspace/` 如果您想要一个空白工作区

如果您只想重置会话，请删除该代理的 `agents/<agentId>/sessions/` 和 `agents/<agentId>/sessions.json`。如果不想重新认证，请保留 `credentials/`。

## 参考资料

- https://docs.openclaw.ai/testing
- https://docs.openclaw.ai/start/getting-started