---
summary: "Testing kit: unit/e2e/live suites, Docker runners, and what each test covers"
read_when:
  - Running tests locally or in CI
  - Adding regressions for model/provider bugs
  - Debugging gateway + agent behavior
title: "Testing"
---
# 测试

OpenClaw 有三个 Vitest 套件（单元/集成、端到端、实时）和一个小的 Docker 运行器集合。

本文档是一个“我们如何测试”的指南：

- 每个套件覆盖的内容（以及它故意不覆盖的内容）
- 常见工作流（本地、预推送、调试）要运行的命令
- 实时测试如何发现凭证并选择模型/提供者
- 如何为现实世界中的模型/提供者问题添加回归测试

## 快速入门

大多数日子：

- 完整门禁（推送前预期）：`pnpm build && pnpm check && pnpm test`

当你修改测试或需要额外的信心时：

- 覆盖率门禁：`pnpm test:coverage`
- 端到端套件：`pnpm test:e2e`

当调试真实提供者/模型（需要真实凭证）时：

- 实时套件（模型 + 网关工具/镜像探测）：`pnpm test:live`

提示：当你只需要一个失败案例时，优先通过下面描述的白名单环境变量缩小实时测试范围。

## 测试套件（在哪里运行）

将套件视为“逐步增加的真实性”（以及增加的波动性/成本）：

### 单元 / 集成（默认）

- 命令：`pnpm test`
- 配置：`scripts/test-parallel.mjs`（运行 `vitest.unit.config.ts`，`vitest.extensions.config.ts`，`vitest.gateway.config.ts`）
- 文件：`src/**/*.test.ts`，`extensions/**/*.test.ts`
- 范围：
  - 纯单元测试
  - 进程内集成测试（网关认证、路由、工具、解析、配置）
  - 已知错误的确定性回归
- 期望：
  - 在 CI 中运行
  - 不需要真实密钥
  - 应该快速且稳定
- 池注意事项：
  - OpenClaw 使用 Vitest `vmForks` 在 Node 22/23 上进行更快的单元分片。
  - 在 Node 24+ 上，OpenClaw 自动回退到常规 `forks` 以避免 Node VM 链接错误 (`ERR_VM_MODULE_LINK_FAILURE` / `module is already linked`)。
  - 手动覆盖使用 `OPENCLAW_TEST_VM_FORKS=0`（强制 `forks`）或 `OPENCLAW_TEST_VM_FORKS=1`（强制 `vmForks`）。

### 端到端（网关冒烟）

- 命令：`pnpm test:e2e`
- 配置：`vitest.e2e.config.ts`
- 文件：`src/**/*.e2e.test.ts`
- 运行时默认值：
  - 使用 Vitest `vmForks` 以加快文件启动速度。
  - 使用自适应工作者（CI: 2-4，本地: 4-8）。
  - 默认以静默模式运行以减少控制台 I/O 开销。
- 有用的覆盖：
  - `OPENCLAW_E2E_WORKERS=<n>` 强制工作者数量（上限为 16）。
  - `OPENCLAW_E2E_VERBOSE=1` 重新启用详细控制台输出。
- 范围：
  - 多实例网关端到端行为
  - WebSocket/HTTP 表面、节点配对和更重的网络
- 期望：
  - 在 CI 中运行（当在管道中启用时）
  - 不需要真实密钥
  - 比单元测试有更多的活动部件（可能较慢）

### 实时（真实提供者 + 真实模型）

- 命令: `pnpm test:live`
- 配置: `vitest.live.config.ts`
- 文件: `src/**/*.live.test.ts`
- 默认: **enabled** by `pnpm test:live` (sets `OPENCLAW_LIVE_TEST=1`)
- 范围:
  - “这个提供商/模型今天是否真的可以用真实的凭证工作？”
  - 捕获提供商格式更改、工具调用的怪癖、认证问题以及速率限制行为
- 期望:
  - 有意设计为不是CI稳定的（真实网络、真实提供商策略、配额、停机）
  - 花费金钱/使用速率限制
  - 更倾向于运行缩小的子集而不是“一切”
  - 实际运行将从`~/.profile`获取以获取缺失的API密钥
- API密钥轮换（提供商特定）：使用逗号/分号格式设置`*_API_KEYS`，或`*_API_KEY_1`，`*_API_KEY_2`（例如`OPENAI_API_KEYS`，`ANTHROPIC_API_KEYS`，`GEMINI_API_KEYS`）或通过`OPENCLAW_LIVE_*_KEY`进行实时覆盖；测试在收到速率限制响应时重试。

## 我应该运行哪个套件？

使用此决策表：

- 编辑逻辑/测试：运行`pnpm test`（如果更改了很多，还应运行`pnpm test:coverage`）
- 触碰网关网络/WS协议/配对：添加`pnpm test:e2e`
- 调试“我的机器人宕机”/提供商特定故障/工具调用：运行一个缩小的`pnpm test:live`

## 实时：模型冒烟测试（配置文件密钥）

实时测试分为两层，以便我们可以隔离故障：

- “直接模型”告诉我们提供商/模型是否可以使用给定的密钥进行响应。
- “网关冒烟”告诉我们该模型的完整网关+代理管道是否正常工作（会话、历史记录、工具、沙盒策略等）。

### 层1：直接模型完成（无网关）

- 测试: `src/agents/models.profiles.live.test.ts`
- 目标:
  - 枚举发现的模型
  - 使用`getApiKeyForModel`选择您有凭证的模型
  - 每个模型运行一个小的完成测试（如有必要，运行针对性的回归）
- 如何启用:
  - `pnpm test:live`（或如果直接调用Vitest，则使用`OPENCLAW_LIVE_TEST=1`）
- 设置`OPENCLAW_LIVE_MODELS=modern`（或`all`，现代的别名）以实际运行此套件；否则跳过以使`pnpm test:live`专注于网关冒烟
- 如何选择模型:
  - `OPENCLAW_LIVE_MODELS=modern`以运行现代允许列表（Opus/Sonnet/Haiku 4.5, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.1, Grok 4）
  - `OPENCLAW_LIVE_MODELS=all`是现代允许列表的别名
  - 或`OPENCLAW_LIVE_MODELS="openai/gpt-5.2,anthropic/claude-opus-4-6,..."`（逗号允许列表）
- 如何选择提供商:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"`（逗号允许列表）
- 密钥来自何处:
  - 默认：配置文件存储和环境回退
  - 设置`OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`以强制仅使用**配置文件存储**
- 为什么存在:
  - 将“提供商API已损坏/密钥无效”与“网关代理管道已损坏”分开
  - 包含小型、隔离的回归（示例：OpenAI响应/Codex响应推理重放+工具调用流）

### 层2：网关 + 开发代理冒烟（“@openclaw”实际上所做的）

- 测试: `src/gateway/gateway-models.profiles.live.test.ts`
- 目标:
  - 启动一个进程内的网关
  - 创建/修补一个 `agent:dev:*` 会话（每次运行时覆盖模型）
  - 迭代带键的模型并断言：
    - “有意义”的响应（不使用工具）
    - 真实的工具调用有效（读取探测）
    - 可选的额外工具探测（执行+读取探测）
    - OpenAI 回归路径（仅工具调用 → 跟进）仍然有效
- 探测详情（以便快速解释失败）：
  - `read` 探测：测试在工作区写入一个随机数文件，并要求代理 `read` 它并回显随机数。
  - `exec+read` 探测：测试要求代理 `exec`-写一个随机数到临时文件，然后 `read` 它回来。
  - 图像探测：测试附加一个生成的PNG（猫+随机代码），并期望模型返回 `cat <CODE>`。
  - 实现参考：`src/gateway/gateway-models.profiles.live.test.ts` 和 `src/gateway/live-image-probe.ts`。
- 如何启用：
  - `pnpm test:live` （或 `OPENCLAW_LIVE_TEST=1` 如果直接调用 Vitest）
- 如何选择模型：
  - 默认：现代允许列表（Opus/Sonnet/Haiku 4.5, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.1, Grok 4）
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` 是现代允许列表的别名
  - 或设置 `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` （或逗号分隔列表）以缩小范围
- 如何选择提供商（避免“OpenRouter 所有”）：
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"` （逗号允许列表）
- 工具 + 图像探测在此实时测试中始终开启：
  - `read` 探测 + `exec+read` 探测（工具压力测试）
  - 图像探测在模型声明支持图像输入时运行
  - 流程（高层次）：
    - 测试生成一个带有“CAT”+随机代码的小型PNG (`src/gateway/live-image-probe.ts`)
    - 通过 `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]` 发送它
    - 网关将附件解析为 `images[]` (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - 内嵌代理将多模态用户消息转发给模型
    - 断言：回复包含 `cat` + 代码（OCR 容差：允许轻微错误）

提示：要查看您机器上可以测试的内容（以及确切的 `provider/model` ID），运行：

```bash
openclaw models list
openclaw models list --json
```

## 实时：Anthropic 设置令牌冒烟测试

- 测试: `src/agents/anthropic.setup-token.live.test.ts`
- 目标：验证 Claude Code CLI 设置令牌（或粘贴的设置令牌配置文件）能否完成一个 Anthropic 提示。
- 启用：
  - `pnpm test:live` （或 `OPENCLAW_LIVE_TEST=1` 如果直接调用 Vitest）
  - `OPENCLAW_LIVE_SETUP_TOKEN=1`
- 令牌来源（选择一个）：
  - 配置文件: `OPENCLAW_LIVE_SETUP_TOKEN_PROFILE=anthropic:setup-token-test`
  - 原始令牌: `OPENCLAW_LIVE_SETUP_TOKEN_VALUE=sk-ant-oat01-...`
- 模型覆盖（可选）：
  - `OPENCLAW_LIVE_SETUP_TOKEN_MODEL=anthropic/claude-opus-4-6`

设置示例：

```bash
openclaw models auth paste-token --provider anthropic --profile-id anthropic:setup-token-test
OPENCLAW_LIVE_SETUP_TOKEN=1 OPENCLAW_LIVE_SETUP_TOKEN_PROFILE=anthropic:setup-token-test pnpm test:live src/agents/anthropic.setup-token.live.test.ts
```

## 实时: CLI 后端冒烟测试 (Claude Code CLI 或其他本地 CLI)

- 测试: `src/gateway/gateway-cli-backend.live.test.ts`
- 目标: 使用本地 CLI 后端验证 Gateway + agent 管道，不修改默认配置。
- 启用:
  - `pnpm test:live` (或 `OPENCLAW_LIVE_TEST=1` 如果直接调用 Vitest)
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- 默认值:
  - 模型: `claude-cli/claude-sonnet-4-6`
  - 命令: `claude`
  - 参数: `["-p","--output-format","json","--dangerously-skip-permissions"]`
- 覆盖 (可选):
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="claude-cli/claude-opus-4-6"`
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.3-codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/claude"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["-p","--output-format","json","--permission-mode","bypassPermissions"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_CLEAR_ENV='["ANTHROPIC_API_KEY","ANTHROPIC_API_KEY_OLD"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1` 发送真实图像附件（路径注入到提示中）。
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"` 将图像文件路径作为 CLI 参数传递而不是提示注入。
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"` (或 `"list"`) 控制如何传递图像参数当 `IMAGE_ARG` 设置时。
  - `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1` 发送第二次交互并验证恢复流程。
- `OPENCLAW_LIVE_CLI_BACKEND_DISABLE_MCP_CONFIG=0` 保持 Claude Code CLI MCP 配置启用（默认使用临时空文件禁用 MCP 配置）。

示例:

```bash
OPENCLAW_LIVE_CLI_BACKEND=1 \
  OPENCLAW_LIVE_CLI_BACKEND_MODEL="claude-cli/claude-sonnet-4-6" \
  pnpm test:live src/gateway/gateway-cli-backend.live.test.ts
```

### 推荐实时食谱

狭窄且明确的允许列表最快且最稳定：

- 单一模型，直接（无网关）:
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.2" pnpm test:live src/agents/models.profiles.live.test.ts`

- 单一模型，网关冒烟测试:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.2" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- 跨多个提供商的工具调用:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.2,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/minimax-m2.1" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- 聚焦 Google (Gemini API 密钥 + Antigravity):
  - Gemini (API 密钥): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity (OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

注意事项：

- `google/...` 使用 Gemini API（API 密钥）。
- `google-antigravity/...` 使用 Antigravity OAuth 桥接（Cloud Code Assist 风格代理端点）。
- `google-gemini-cli/...` 使用您机器上的本地 Gemini CLI（单独的身份验证 + 工具特性）。
- Gemini API 与 Gemini CLI：
  - API：OpenClaw 通过 HTTP 调用 Google 托管的 Gemini API（API 密钥 / 配置文件身份验证）；这是大多数用户所说的“Gemini”。
  - CLI：OpenClaw 调用本地 `gemini` 二进制文件；它有自己的身份验证机制，并且行为可能不同（流式处理/工具支持/版本差异）。

## 实时：模型矩阵（我们涵盖的内容）

没有固定的“CI 模型列表”（实时是可选的），但这些是建议在带有密钥的开发机器上定期涵盖的**推荐**模型。

### 现代烟雾测试集（工具调用 + 图像）

这是我们期望持续运行的“通用模型”：

- OpenAI（非 Codex）：`openai/gpt-5.2`（可选：`openai/gpt-5.1`）
- OpenAI Codex：`openai-codex/gpt-5.3-codex`（可选：`openai-codex/gpt-5.3-codex-codex`）
- Anthropic：`anthropic/claude-opus-4-6`（或 `anthropic/claude-sonnet-4-5`）
- Google（Gemini API）：`google/gemini-3-pro-preview` 和 `google/gemini-3-flash-preview`（避免较旧的 Gemini 2.x 模型）
- Google（Antigravity）：`google-antigravity/claude-opus-4-6-thinking` 和 `google-antigravity/gemini-3-flash`
- Z.AI（GLM）：`zai/glm-4.7`
- MiniMax：`minimax/minimax-m2.1`

使用工具 + 图像运行网关烟雾测试：
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.2,openai-codex/gpt-5.3-codex,anthropic/claude-opus-4-6,google/gemini-3-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/minimax-m2.1" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### 基线：工具调用（读取 + 可选执行）

每个提供商家族至少选择一个：

- OpenAI：`openai/gpt-5.2`（或 `openai/gpt-5-mini`）
- Anthropic：`anthropic/claude-opus-4-6`（或 `anthropic/claude-sonnet-4-5`）
- Google：`google/gemini-3-flash-preview`（或 `google/gemini-3-pro-preview`）
- Z.AI（GLM）：`zai/glm-4.7`
- MiniMax：`minimax/minimax-m2.1`

可选的额外覆盖范围（很好拥有）：

- xAI：`xai/grok-4`（或最新可用版本）
- Mistral：`mistral/`…（选择一个您已启用的“工具”功能模型）
- Cerebras：`cerebras/`…（如果您有访问权限）
- LM Studio：`lmstudio/`…（本地；工具调用取决于 API 模式）

### 视觉：发送图像（附件 → 多模态消息）

在 `OPENCLAW_LIVE_GATEWAY_MODELS` 中包含至少一个支持图像的模型（Claude/Gemini/OpenAI 支持图像的变体等），以测试图像探测。

### 聚合器 / 替代网关

如果您启用了密钥，我们还支持通过以下方式进行测试：

- OpenRouter：`openrouter/...`（数百个模型；使用 `openclaw models scan` 查找支持工具+图像的候选模型）
- OpenCode Zen：`opencode/...`（通过 `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY` 进行身份验证）

您可以包含在实时矩阵中的更多提供商（如果您有凭据/配置）：

- 内置: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `google-gemini-cli`, `zai`, `openrouter`, `opencode`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- 通过 `models.providers` (自定义端点): `minimax` (云/API)，加上任何与OpenAI/Anthropic兼容的代理（LM Studio, vLLM, LiteLLM等）

提示：不要在文档中硬编码“所有模型”。权威列表是你的机器上`discoverModels(...)`返回的内容 + 可用的密钥。

## 凭证（从不提交）

实时测试发现凭证的方式与CLI相同。实际影响：

- 如果CLI正常工作，实时测试应该找到相同的密钥。
- 如果实时测试显示“没有凭证”，以调试`openclaw models list` / 模型选择相同的方式进行调试。

- 配置文件存储: `~/.openclaw/credentials/`（首选；测试中的“配置文件密钥”含义）
- 配置: `~/.openclaw/openclaw.json`（或 `OPENCLAW_CONFIG_PATH`）

如果你想依赖环境变量密钥（例如，在你的`~/.profile`中导出），在`source ~/.profile`之后运行本地测试，或使用下面的Docker运行器（它们可以将`~/.profile`挂载到容器中）。

## Deepgram实时（音频转录）

- 测试: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- 启用: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus编码计划实时

- 测试: `src/agents/byteplus.live.test.ts`
- 启用: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- 可选模型覆盖: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## Docker运行器（可选的“适用于Linux”的检查）

这些在仓库Docker镜像内部运行`pnpm test:live`，挂载你的本地配置目录和工作区（如果挂载则加载`~/.profile`）：

- 直接模型: `pnpm test:docker:live-models`（脚本: `scripts/test-live-models-docker.sh`）
- 网关 + 开发代理: `pnpm test:docker:live-gateway`（脚本: `scripts/test-live-gateway-models-docker.sh`）
- 入门向导（TTY，完整脚手架）: `pnpm test:docker:onboard`（脚本: `scripts/e2e/onboard-docker.sh`）
- 网关网络（两个容器，WS认证 + 健康检查）: `pnpm test:docker:gateway-network`（脚本: `scripts/e2e/gateway-network-docker.sh`）
- 插件（自定义扩展加载 + 注册表冒烟测试）: `pnpm test:docker:plugins`（脚本: `scripts/e2e/plugins-docker.sh`）

有用的环境变量：

- `OPENCLAW_CONFIG_DIR=...`（默认: `~/.openclaw`）挂载到 `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...`（默认: `~/.openclaw/workspace`）挂载到 `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...`（默认: `~/.profile`）挂载到 `/home/node/.profile` 并在运行测试前加载
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...` 以缩小运行范围
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` 确保凭证来自配置文件存储（而不是环境）

## 文档合理性检查

在文档编辑后运行文档检查：`pnpm docs:list`。

## 离线回归（CI安全）

这些是“真实管道”回归但没有真实提供商：

- 网关工具调用（模拟OpenAI，真实网关 + 代理循环）：`src/gateway/gateway.tool-calling.mock-openai.test.ts`
- 网关向导（WS `wizard.start`/`wizard.next`，写入配置 + 强制认证）：`src/gateway/gateway.wizard.e2e.test.ts`

## 代理可靠性评估（技能）

我们已经有一些类似“代理可靠性评估”的CI安全测试：

- 通过真实网关 + 代理循环进行模拟工具调用 (`src/gateway/gateway.tool-calling.mock-openai.test.ts`)。
- 验证会话连接和配置效果的端到端向导流程 (`src/gateway/gateway.wizard.e2e.test.ts`)。

技能方面仍然缺少的内容（参见 [Skills](/tools/skills)）：

- **决策：** 当技能在提示中列出时，代理是否选择了正确的技能（或避免了无关的技能）？
- **合规性：** 代理在使用前是否读取了 `SKILL.md` 并遵循了所需的步骤/参数？
- **工作流契约：** 断言工具顺序、会话历史延续性和沙盒边界的多回合场景。

未来的评估应首先保持确定性：

- 使用模拟提供商的场景运行器来断言工具调用 + 顺序、技能文件读取和会话连接。
- 一套小型的技能聚焦场景（使用与避免、门控、提示注入）。
- 仅在CI安全套件到位后才进行可选的实时评估（通过环境变量选择加入）。

## 添加回归（指导）

当您修复在实时环境中发现的提供商/模型问题时：

- 如果可能，添加一个CI安全回归（模拟/存根提供商，或捕获确切的请求形状转换）
- 如果本质上只能在实时环境中进行（速率限制、身份验证策略），则保持实时测试范围狭窄并通过环境变量选择加入
- 尽量针对捕获错误的最小层：
  - 提供商请求转换/重放错误 → 直接模型测试
  - 网关会话/历史/工具管道错误 → 网关实时冒烟测试或CI安全网关模拟测试