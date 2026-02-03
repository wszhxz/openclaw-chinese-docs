---
summary: "Step-by-step release checklist for npm + macOS app"
read_when:
  - Cutting a new npm release
  - Cutting a new macOS app release
  - Verifying metadata before publishing
---
# 发布检查清单（npm + macOS）

从仓库根目录使用 `pnpm`（Node 22+）。在标记/发布前保持工作树干净。

## 操作员触发

当操作员说“release”时，立即执行以下预检查（除非被阻塞，否则不询问额外问题）：

- 阅读此文档和 `docs/platforms/mac/release.md`。
- 从 `~/.profile` 加载环境变量，并确认 `SPARKLE_PRIVATE_KEY_FILE` + App Store Connect 变量已设置（`SPARKLE_PRIVATE_KEY_FILE` 应该位于 `~/.profile`）。
- 如需使用，从 `~/Library/CloudStorage/Dropbox/Backup/Sparkle` 加载 Sparkle 密钥。

1. **版本与元数据**

- [ ] 提升 `package.json` 版本（例如 `2026.1.29`）。
- [ ] 运行 `pnpm plugins:sync` 以对齐扩展包版本 + 变更日志。
- [ ] 更新 CLI/版本字符串：[`src/cli/program.ts`](https://github.com/openclaw/openclaw/blob/main/src/cli/program.ts) 和 [`src/provider-web.ts`](https://github.com/openclaw/openclaw/blob/main/src/provider-web.ts) 中的 Baileys 用户代理。
- [ ] 确认包元数据（名称、描述、仓库、关键词、许可证）和 `bin` 映射指向 [`openclaw.mjs`](https://github.com/openclaw/openclaw/blob/main/openclaw.mjs) 用于 `openclaw`。
- [ ] 如果依赖项已更改，运行 `pnpm install` 以确保 `pnpm-lock.yaml` 是最新的。

2. **构建与工件**

- [ ] 如果 A2UI 输入已更改，运行 `pnpm canvas:a2ui:bundle` 并提交任何更新的 [`src/canvas-host/a2ui/a2ui.bundle.js`](https://github.com/openclaw/openclaw/blob/main/src/canvas-host/a2ui/a2ui.bundle.js)。
- [ ] `pnpm run build`（重新生成 `dist/`）。
- [ ] 验证 npm 包 `files` 包含所有必要的 `dist/*` 文件夹（特别是 `dist/node-host/**` 和 `dist/acp/**` 用于无头节点 + ACP CLI）。
- [ ] 确认 `dist/build-info.json` 存在且包含预期的 `commit` 哈希（CLI 标题使用此哈希进行 npm 安装）。
- [ ] 可选：构建后运行 `npm pack --pack-destination /tmp`；检查 tarball 内容并保留以备 GitHub 发布（**不要**提交它）。

3. **变更日志与文档**

- [ ] 使用用户可见的亮点更新 `CHANGELOG.md`（如果缺失则创建文件）；保持条目按版本严格降序排列。
- [ ] 确保 README 示例/标志与当前 CLI 行为匹配（特别是新命令或选项）。

4. **验证**

- [ ] `pnpm build`
- [ ] `pnpm check`
- [ ] `pnpm test`（或 `pnpm test:coverage` 如果需要覆盖率输出）
- [ ] `pnpm release:check`（验证 npm pack 内容）
- [ ] `OPENCLAW_INSTALL_SMOKE_SKIP_NONROOT=1 pnpm test:install:smoke`（Docker 安装烟雾测试，快速路径；发布前必需）
  - 如果上一个 npm 发布已知损坏，设置 `OPENCLAW_INSTALL_SMOKE_PREVIOUS=<last-good-version>` 或 `OPENCLAW_INSTALL_SMOKE_SKIP_PREVIOUS=1` 用于预安装步骤。
- [ ]（可选）完整安装烟雾测试（添加非 root + CLI 覆盖）：`pnpm test:install:smoke`
- [ ]（可选）安装 E2E（Docker，运行 `curl -fsSL https://openclaw.ai/install.sh | bash`，进行 onboard，然后运行真实工具调用）：
  - `pnpm test:install:e2e:openai`（需要 `OPENAI_API_KEY`）
  - `pnpm test:install:e2e:anthropic`（需要 `ANTHROPIC_API_KEY`）
  - `pnpm test:install:e2e`（需要两个密钥；运行两个提供者）
- [ ]（可选）如果您的更改影响发送/接收路径，请抽查 Web 网关。

5. **macOS 应用（Sparkle）**

- [ ] 构建 + 签名 macOS 应用，然后压缩以供分发。
- [ ] 生成 Sparkle 应用程序更新说明（通过 [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh) 生成 HTML 说明）并更新 `appcast.xml`。
- [ ] 准备好应用压缩包（和可选的 dSYM 压缩包）以附加到 GitHub 发布。
- [ ] 遵循 [macOS 发布](/platforms/mac/release) 获取确切命令和所需环境变量。
  - `APP_BUILD` 必须是数字 + 单调递增（无 `-beta`），以便 Sparkle 正确比较版本。
  - 如果进行公证，使用从 App Store Connect API 环境变量创建的 `openclaw-notary` 密钥链配置文件（参见 [macOS 发布](/platforms/mac/release)）。

6. **发布