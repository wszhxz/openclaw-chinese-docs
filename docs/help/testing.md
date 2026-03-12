---
summary: "Testing kit: unit/e2e/live suites, Docker runners, and what each test covers"
read_when:
  - Running tests locally or in CI
  - Adding regressions for model/provider bugs
  - Debugging gateway + agent behavior
title: "Testing"
---
# 测试

OpenClaw 包含三个 Vitest 测试套件（单元/集成测试、端到端测试、实机测试）以及一组小型 Docker 运行器。

本文档是一份“我们如何测试”的指南：

- 每个套件覆盖的内容（以及它**刻意不覆盖**的内容）
- 常见工作流（本地开发、推送前检查、调试）所对应的执行命令
- 实机测试如何发现凭据并选择模型/提供商
- 如何为真实世界中的模型/提供商问题添加回归测试用例

## 快速开始

大多数日常开发中：

- 完整门禁检查（推送前预期执行）：`pnpm build && pnpm check && pnpm test`

当你修改了测试代码，或需要额外信心时：

- 覆盖率门禁检查：`pnpm test:coverage`
- 端到端测试套件：`pnpm test:e2e`

当调试真实提供商/模型（需使用真实凭据）时：

- 实机测试套件（涵盖模型 + 网关工具/镜像探针）：`pnpm test:live`

提示：若你仅需复现某一个失败用例，建议优先通过下方所述的白名单环境变量来缩小实机测试范围。

## 测试套件（各套件在何处运行）

可将这些套件理解为“真实性逐级提升”（同时不稳定性和开销也逐级增加）：

### 单元 / 集成测试（默认）

- 命令：`pnpm test`
- 配置：`scripts/test-parallel.mjs`（运行 `vitest.unit.config.ts`、`vitest.extensions.config.ts`、`vitest.gateway.config.ts`）
- 文件：`src/**/*.test.ts`、`extensions/**/*.test.ts`
- 范围：
  - 纯单元测试
  - 进程内集成测试（网关鉴权、路由、工具链、解析、配置）
  - 已知缺陷的确定性回归测试
- 期望行为：
  - 在 CI 中运行
  - 无需真实密钥
  - 应快速且稳定
- 池说明：
  - OpenClaw 在 Node 22/23 上使用 Vitest `vmForks` 以实现更快的单元测试分片。
  - 在 Node 24+ 上，OpenClaw 自动回退至常规 `forks`，以避免 Node VM 链接错误（`ERR_VM_MODULE_LINK_FAILURE` / `module is already linked`）。
  - 可手动覆写：使用 `OPENCLAW_TEST_VM_FORKS=0`（强制启用 `forks`）或 `OPENCLAW_TEST_VM_FORKS=1`（强制启用 `vmForks`）。

### 端到端测试（网关冒烟测试）

- 命令：`pnpm test:e2e`
- 配置：`vitest.e2e.config.ts`
- 文件：`src/**/*.e2e.test.ts`
- 运行时默认设置：
  - 使用 Vitest `vmForks` 以加快文件启动速度。
  - 使用自适应工作线程（CI：2–4 个，本地：4–8 个）。
  - 默认以静默模式运行，以降低控制台 I/O 开销。
- 有用的覆写选项：
  - 使用 `OPENCLAW_E2E_WORKERS=<n>` 强制指定工作线程数量（上限为 16）。
  - 使用 `OPENCLAW_E2E_VERBOSE=1` 重新启用详细控制台输出。
- 范围：
  - 多实例网关的端到端行为
  - WebSocket/HTTP 接口、节点配对及更重的网络交互
- 期望行为：
  - 在 CI 中运行（当流水线中启用时）
  - 无需真实密钥
  - 相比单元测试涉及更多组件（可能更慢）

### 实机测试（真实提供商 + 真实模型）

- 命令：`pnpm test:live`
- 配置：`vitest.live.config.ts`
- 文件：`src/**/*.live.test.ts`
- 默认状态：**启用**，由 `pnpm test:live` 控制（设置 `OPENCLAW_LIVE_TEST=1`）
- 范围：
  - “该提供商/模型在今天、使用真实凭据的情况下是否真的可用？”
  - 捕获提供商格式变更、工具调用异常、鉴权问题及速率限制行为
- 期望行为：
  - 设计上即不保证 CI 稳定性（真实网络、真实提供商策略、配额、服务中断）
  - 产生费用 / 消耗速率配额
  - 推荐运行缩小范围的子集，而非“全部运行”
  - 实机测试将读取 `~/.profile` 以补全缺失的 API 密钥
- API 密钥轮换（按提供商区分）：设置 `*_API_KEYS`（逗号/分号分隔格式）或 `*_API_KEY_1`、`*_API_KEY_2`（例如 `OPENAI_API_KEYS`、`ANTHROPIC_API_KEYS`、`GEMINI_API_KEYS`），或通过 `OPENCLAW_LIVE_*_KEY` 为单次实机测试单独覆写；测试会在收到速率限制响应时自动重试。

## 我该运行哪个套件？

请参考以下决策表：

- 修改逻辑/测试代码：运行 `pnpm test`（若改动较大，再加 `pnpm test:coverage`）
- 修改网关网络/WS 协议/配对逻辑：追加 `pnpm test:e2e`
- 调试“我的机器人宕机了”/特定提供商故障/工具调用问题：运行缩小范围的 `pnpm test:live`

## 实机测试：Android 节点能力扫描

- 测试：`src/gateway/android-node.capabilities.live.test.ts`
- 脚本：`pnpm android:test:integration`
- 目标：调用已连接 Android 节点当前**公开声明的所有命令**，并断言其命令契约行为。
- 范围：
  - 前置条件/手动设置（该套件不负责安装/运行/配对应用）。
  - 针对选定 Android 节点，逐条验证网关 `node.invoke` 行为。
- 必需前置准备：
  - Android 应用已连接并完成与网关的配对。
  - 应用保持在前台。
  - 已授予你期望通过的能力所需的权限和采集许可。
- 可选目标覆写项：
  - `OPENCLAW_ANDROID_NODE_ID` 或 `OPENCLAW_ANDROID_NODE_NAME`。
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`。
- 完整 Android 设置详情：[Android App](/platforms/android)

## 实机测试：模型冒烟测试（配置文件密钥）

实机测试分为两层，以便隔离故障根源：

- “直接模型调用”用于确认：给定密钥下，该提供商/模型能否正常响应。
- “网关冒烟测试”用于确认：该模型下的完整网关+智能体流水线是否正常工作（会话、历史、工具、沙箱策略等）。

### 第一层：直接模型补全（不经过网关）

- 测试：`src/agents/models.profiles.live.test.ts`
- 目标：
  - 枚举已发现的模型
  - 使用 `getApiKeyForModel` 选择你拥有凭据的模型
  - 对每个模型执行一次小型补全（必要时加入针对性回归测试）
- 启用方式：
  - `pnpm test:live`（或直接调用 Vitest 时使用 `OPENCLAW_LIVE_TEST=1`）
- 设置 `OPENCLAW_LIVE_MODELS=modern`（或 `all`，现代版别名）以实际运行此套件；否则跳过，使 `pnpm test:live` 专注于网关冒烟测试
- 如何选择模型：
  - `OPENCLAW_LIVE_MODELS=modern`：运行现代白名单（Opus/Sonnet/Haiku 4.5、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.5、Grok 4）
  - `OPENCLAW_LIVE_MODELS=all` 是现代白名单的别名
  - 或使用 `OPENCLAW_LIVE_MODELS="openai/gpt-5.2,anthropic/claude-opus-4-6,..."`（逗号分隔白名单）
- 如何选择提供商：
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"`（逗号分隔白名单）
- 密钥来源：
  - 默认：配置文件存储 + 环境变量回退
  - 设置 `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` 可强制仅使用**配置文件存储**
- 存在此层的原因：
  - 将“提供商 API 故障 / 密钥无效”与“网关智能体流水线故障”区分开
  - 包含小型、隔离的回归测试（例如：OpenAI Responses/Codex Responses 的推理回放 + 工具调用流程）

### 第二层：网关 + 开发智能体冒烟测试（即“@openclaw”实际执行的操作）

- 测试：`src/gateway/gateway-models.profiles.live.test.ts`
- 目标：
  - 启动一个进程内网关
  - 创建/更新一个 `agent:dev:*` 会话（每次运行可覆盖模型）
  - 遍历各“模型+密钥”组合，并断言：
    - 返回“有意义”的响应（无工具调用）
    - 实际工具调用成功（读取探针）
    - 可选附加工具探针（执行+读取探针）
    - OpenAI 回归路径（仅工具调用 → 后续跟进）仍能正常工作
- 探针细节（便于你快速解释失败原因）：
  - `read` 探针：测试在工作区中写入一个随机 nonce 文件，并要求智能体 `read` 该文件并回显 nonce。
  - `exec+read` 探针：测试要求智能体 `exec`-写入一个 nonce 到临时文件，然后 `read` 并返回。
  - 图像探针：测试附带一张生成的 PNG（猫图 + 随机代码），并期望模型返回 `cat <CODE>`。
  - 实现参考：`src/gateway/gateway-models.profiles.live.test.ts` 和 `src/gateway/live-image-probe.ts`。
- 启用方式：
  - `pnpm test:live`（或直接调用 Vitest 时使用 `OPENCLAW_LIVE_TEST=1`）
- 如何选择模型：
  - 默认：现代白名单（Opus/Sonnet/Haiku 4.5、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.5、Grok 4）
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` 是现代白名单的别名
  - 或设置 `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"`（或逗号分隔列表）进行缩小范围
- 如何选择提供商（避免“OpenRouter 全部启用”）：
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"`（逗号分隔白名单）
- 工具 + 图像探针在此实机测试中始终启用：
  - `read` 探针 + `exec+read` 探针（工具压力测试）
  - 图像探针仅在模型声明支持图像输入时运行
  - 流程（高层描述）：
    - 测试生成一张含“CAT”+随机代码的微型 PNG（`src/gateway/live-image-probe.ts`）
    - 通过 `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]` 发送
    - 网关将附件解析为 `images[]`（`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`）
    - 内嵌智能体将多模态用户消息转发给模型
    - 断言：回复中包含 `cat` + 该随机代码（OCR 容忍度：允许轻微误差）

提示：要查看你的机器上可测试的内容（以及确切的 `provider/model` ID），请运行：

```bash
openclaw models list
openclaw models list --json
```

## 实机测试：Anthropic setup-token 冒烟测试

- 测试：`src/agents/anthropic.setup-token.live.test.ts`
- 目标：验证 Claude Code CLI 的 setup-token（或粘贴的 setup-token 配置文件）能否成功完成 Anthropic 提示。
- 启用方式：
  - `pnpm test:live`（或直接调用 Vitest 时使用 `OPENCLAW_LIVE_TEST=1`）
  - `OPENCLAW_LIVE_SETUP_TOKEN=1`
- Token 来源（任选其一）：
  - 配置文件：`OPENCLAW_LIVE_SETUP_TOKEN_PROFILE=anthropic:setup-token-test`
  - 原始 token：`OPENCLAW_LIVE_SETUP_TOKEN_VALUE=sk-ant-oat01-...`
- 模型覆写（可选）：
  - `OPENCLAW_LIVE_SETUP_TOKEN_MODEL=anthropic/claude-opus-4-6`

设置示例：

```bash
openclaw models auth paste-token --provider anthropic --profile-id anthropic:setup-token-test
OPENCLAW_LIVE_SETUP_TOKEN=1 OPENCLAW_LIVE_SETUP_TOKEN_PROFILE=anthropic:setup-token-test pnpm test:live src/agents/anthropic.setup-token.live.test.ts
```

## 实机测试：CLI 后端冒烟测试（Claude Code CLI 或其他本地 CLI）

- 测试：`src/gateway/gateway-cli-backend.live.test.ts`  
- 目标：使用本地 CLI 后端验证 Gateway + agent 流水线，不修改您的默认配置。  
- 启用：  
  - `pnpm test:live`（或直接调用 Vitest 时使用 `OPENCLAW_LIVE_TEST=1`）  
  - `OPENCLAW_LIVE_CLI_BACKEND=1`  
- 默认值：  
  - 模型：`claude-cli/claude-sonnet-4-6`  
  - 命令：`claude`  
  - 参数：`["-p","--output-format","json","--permission-mode","bypassPermissions"]`  
- 覆盖项（可选）：  
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="claude-cli/claude-opus-4-6"`  
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`  
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/claude"`  
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["-p","--output-format","json","--permission-mode","bypassPermissions"]'`  
  - `OPENCLAW_LIVE_CLI_BACKEND_CLEAR_ENV='["ANTHROPIC_API_KEY","ANTHROPIC_API_KEY_OLD"]'`  
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1`：发送真实图像附件（路径将被注入到 prompt 中）。  
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"`：将图像文件路径作为 CLI 参数传入，而非通过 prompt 注入。  
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"`（或 `"list"`）：当设置 `IMAGE_ARG` 时，控制图像参数的传递方式。  
  - `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1`：发送第二轮请求，验证恢复流程（resume flow）。  
- `OPENCLAW_LIVE_CLI_BACKEND_DISABLE_MCP_CONFIG=0`：保持 Claude Code CLI MCP 配置启用（默认使用临时空文件禁用 MCP 配置）。  

示例：  

```bash
OPENCLAW_LIVE_CLI_BACKEND=1 \
  OPENCLAW_LIVE_CLI_BACKEND_MODEL="claude-cli/claude-sonnet-4-6" \
  pnpm test:live src/gateway/gateway-cli-backend.live.test.ts
```  

### 推荐的实时测试方案（live recipes）  

窄范围、显式白名单最快且最稳定：  

- 单一模型，直连（不经过 gateway）：  
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.2" pnpm test:live src/agents/models.profiles.live.test.ts`  

- 单一模型，gateway 烟雾测试（smoke test）：  
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.2" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`  

- 跨多个供应商的工具调用：  
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.2,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/minimax-m2.5" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`  

- Google 专项（Gemini API 密钥 + Antigravity）：  
  - Gemini（API 密钥）：`OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`  
  - Antigravity（OAuth）：`OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`  

说明：  

- `google/...` 使用 Gemini API（API 密钥）。  
- `google-antigravity/...` 使用 Antigravity OAuth 桥接器（类似 Cloud Code Assist 的 agent 端点）。  
- `google-gemini-cli/...` 使用您本地机器上的 Gemini CLI（独立认证 + 工具链行为差异）。  
- Gemini API 与 Gemini CLI 对比：  
  - API：OpenClaw 通过 HTTP 调用 Google 托管的 Gemini API（使用 API 密钥 / Profile 认证）；大多数用户所指的“Gemini”即为此种方式。  
  - CLI：OpenClaw 派生调用本地 `gemini` 二进制程序；其拥有独立认证机制，行为可能不同（如流式响应、工具支持、版本差异等）。  

## 实时测试：模型矩阵（覆盖范围）  

不存在固定的“CI 模型列表”（实时测试为按需启用），但以下为**推荐**在开发机上定期覆盖的模型（需已配置对应密钥）。  

### 现代烟雾测试集（支持工具调用 + 图像）  

这是我们认为应持续保持可用的“通用模型”测试集：  

- OpenAI（非 Codex）：`openai/gpt-5.2`（可选：`openai/gpt-5.1`）  
- OpenAI Codex：`openai-codex/gpt-5.4`  
- Anthropic：`anthropic/claude-opus-4-6`（或 `anthropic/claude-sonnet-4-5`）  
- Google（Gemini API）：`google/gemini-3.1-pro-preview` 和 `google/gemini-3-flash-preview`（避免使用较旧的 Gemini 2.x 系列模型）  
- Google（Antigravity）：`google-antigravity/claude-opus-4-6-thinking` 和 `google-antigravity/gemini-3-flash`  
- Z.AI（GLM）：`zai/glm-4.7`  
- MiniMax：`minimax/minimax-m2.5`  

运行带工具调用和图像能力的 gateway 烟雾测试：  
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.2,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/minimax-m2.5" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`  

### 基线测试：工具调用（Read + 可选 Exec）  

每个供应商家族至少选择一个：  

- OpenAI：`openai/gpt-5.2`（或 `openai/gpt-5-mini`）  
- Anthropic：`anthropic/claude-opus-4-6`（或 `anthropic/claude-sonnet-4-5`）  
- Google：`google/gemini-3-flash-preview`（或 `google/gemini-3.1-pro-preview`）  
- Z.AI（GLM）：`zai/glm-4.7`  
- MiniMax：`minimax/minimax-m2.5`  

可选补充覆盖（建议包含）：  

- xAI：`xai/grok-4`（或当前可用最新版本）  
- Mistral：`mistral/`…（任选一个您已启用的、支持工具调用的模型）  
- Cerebras：`cerebras/`…（若您有访问权限）  
- LM Studio：`lmstudio/`…（本地运行；工具调用能力取决于所选 API 模式）  

### 视觉能力测试：图像发送（附件 → 多模态消息）  

请在 `OPENCLAW_LIVE_GATEWAY_MODELS` 中至少包含一个支持图像输入的模型（如 Claude/Gemini/OpenAI 的视觉能力变体等），以验证图像探测流程。  

### 聚合器 / 替代网关  

若您已启用对应密钥，我们还支持通过以下方式测试：  

- OpenRouter：`openrouter/...`（涵盖数百个模型；使用 `openclaw models scan` 查找支持工具调用与图像能力的候选模型）  
- OpenCode Zen：`opencode/...`（通过 `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY` 进行认证）  

更多可在实时矩阵中加入的供应商（若您已配置凭据/配置）：  

- 内置支持：`openai`、`openai-codex`、`anthropic`、`google`、`google-vertex`、`google-antigravity`、`google-gemini-cli`、`zai`、`openrouter`、`opencode`、`xai`、`groq`、`cerebras`、`mistral`、`github-copilot`  
- 通过 `models.providers`（自定义端点）：`minimax`（云服务/API），以及任意兼容 OpenAI/Anthropic 的代理（如 LM Studio、vLLM、LiteLLM 等）  

提示：切勿在文档中硬编码“所有模型”。权威模型列表即为您的机器上 `discoverModels(...)` 返回的结果，加上当前可用的密钥集合。  

## 凭据（切勿提交）  

实时测试以与 CLI 完全相同的方式发现凭据。实际影响如下：  

- 若 CLI 可正常工作，则实时测试也应能发现相同的密钥。  
- 若某实时测试报错“no creds”，请以调试 `openclaw models list` / 模型选择问题的相同方式排查。  

- Profile 存储：`~/.openclaw/credentials/`（首选；测试中“profile keys”的含义即为此）  
- 配置文件：`~/.openclaw/openclaw.json`（或 `OPENCLAW_CONFIG_PATH`）  

若您希望依赖环境变量密钥（例如在您的 `~/.profile` 中导出），请在执行 ``source ~/.profile`` 后再运行本地测试，或使用下方 Docker 运行器（它们可将 `~/.profile` 挂载进容器）。  

## Deepgram 实时测试（音频转录）  

- 测试：`src/media-understanding/providers/deepgram/audio.live.test.ts`  
- 启用：`DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`  

## BytePlus 编码计划实时测试  

- 测试：`src/agents/byteplus.live.test.ts`  
- 启用：`BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`  
- 可选模型覆盖：`BYTEPLUS_CODING_MODEL=ark-code-latest`  

## Docker 运行器（可选，“在 Linux 上可用”验证）  

这些运行器在仓库 Docker 镜像内执行 `pnpm test:live`，挂载您的本地配置目录与工作区（若已挂载，则同时加载 `~/.profile`）：  

- 直连模型：`pnpm test:docker:live-models`（脚本：`scripts/test-live-models-docker.sh`）  
- Gateway + 开发者 agent：`pnpm test:docker:live-gateway`（脚本：`scripts/test-live-gateway-models-docker.sh`）  
- 入门向导（TTY，完整脚手架）：`pnpm test:docker:onboard`（脚本：`scripts/e2e/onboard-docker.sh`）  
- Gateway 网络（双容器，WS 认证 + 健康检查）：`pnpm test:docker:gateway-network`（脚本：`scripts/e2e/gateway-network-docker.sh`）  
- 插件（自定义扩展加载 + 注册中心烟雾测试）：`pnpm test:docker:plugins`（脚本：`scripts/e2e/plugins-docker.sh`）  

实时模型 Docker 运行器还会以只读方式挂载当前代码检出，并将其复制到容器内的临时工作目录中。此举既保证运行时镜像轻量，又能确保 Vitest 针对您精确的本地源码与配置执行。  

手动 ACP 平实语言线程烟雾测试（非 CI）：  

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`  
- 请保留该脚本用于回归测试/调试流程。未来可能再次需要它来验证 ACP 线程路由逻辑，因此请勿删除。  

常用环境变量：  

- `OPENCLAW_CONFIG_DIR=...`（默认：`~/.openclaw`）挂载至 `/home/node/.openclaw`  
- `OPENCLAW_WORKSPACE_DIR=...`（默认：`~/.openclaw/workspace`）挂载至 `/home/node/.openclaw/workspace`  
- `OPENCLAW_PROFILE_FILE=...`（默认：`~/.profile`）挂载至 `/home/node/.profile`，并在运行测试前加载  
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...`：缩小测试范围  
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`：确保凭据来自 profile 存储（而非环境变量）  

## 文档合理性检查  

在文档编辑后运行文档检查：`pnpm docs:list`。  

## 离线回归测试（CI 安全）  

这些是“真实流水线”回归测试，无需真实供应商参与：  

- Gateway 工具调用（模拟 OpenAI，真实 gateway + agent 循环）：`src/gateway/gateway.test.ts`（用例：“通过 gateway agent 循环端到端运行模拟 OpenAI 工具调用”）  
- Gateway 向导（WS `wizard.start`/`wizard.next`，写入配置 + 强制认证）：`src/gateway/gateway.test.ts`（用例：“通过 WS 运行向导并写入认证令牌配置”）  

## Agent 可靠性评估（技能）  

我们已具备若干 CI 安全的测试，其行为类似于“Agent 可靠性评估”：  

- 通过真实 gateway + agent 循环进行模拟工具调用（`src/gateway/gateway.test.ts`）。  
- 端到端向导流程，用于验证会话连接与配置效果（`src/gateway/gateway.test.ts`）。  

技能方面尚缺失的内容（参见 [Skills](/tools/skills)）：

- **决策能力**：当提示词中列出了技能时，智能体是否选择了正确的技能（或避免了不相关的技能）？  
- **合规性**：智能体在使用前是否读取了 `SKILL.md` 并遵循了必需的步骤/参数？  
- **工作流契约**：多轮交互场景，用于验证工具调用顺序、会话历史传递以及沙箱边界。

未来的评估应首先确保确定性：

- 使用模拟提供方（mock providers）的场景执行器，用于断言工具调用及其顺序、技能文件读取行为、以及会话连接逻辑。  
- 一套精简的、以技能为中心的测试场景（例如：该用时是否使用、该禁用时是否避免、条件控制、提示注入防护）。  
- 可选的线上评估（需显式启用，且受环境变量控制），仅在 CI 安全测试套件已就绪后才启用。

## 添加回归测试（指导说明）

当你在线上环境中发现并修复某个提供方/模型问题时：

- 若可行，请添加一个 CI 安全的回归测试（例如：使用模拟/打桩提供方，或捕获精确的请求结构转换过程）。  
- 若问题本质上只能在线上复现（如：速率限制、认证策略等），则保持线上测试范围尽可能窄，并通过环境变量显式启用。  
- 优先选择能覆盖该缺陷的最小层级进行测试：  
  - 若为提供方请求转换/重放类缺陷 → 直接在 models 层测试；  
  - 若为网关层的会话/历史/工具流水线缺陷 → 使用网关线上冒烟测试或 CI 安全的网关模拟测试。