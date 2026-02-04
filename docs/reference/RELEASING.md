---
summary: "Step-by-step release checklist for npm + macOS app"
read_when:
  - Cutting a new npm release
  - Cutting a new macOS app release
  - Verifying metadata before publishing
---
# 发布检查清单 (npm + macOS)

使用 `pnpm` (Node 22+) 从仓库根目录运行。在打标签/发布之前保持工作树干净。

## 操作员触发

当操作员说“release”时，立即执行以下预检（除非被阻塞，否则不要提问）：

- 阅读本文档和 `docs/platforms/mac/release.md`。
- 从 `~/.profile` 加载环境并确认 `SPARKLE_PRIVATE_KEY_FILE` + App Store Connect 变量已设置（SPARKLE_PRIVATE_KEY_FILE 应位于 `~/.profile`）。
- 如需，使用来自 `~/Library/CloudStorage/Dropbox/Backup/Sparkle` 的 Sparkle 密钥。

1. **版本与元数据**

- [ ] 升级 `package.json` 版本（例如，`2026.1.29`）。
- [ ] 运行 `pnpm plugins:sync` 以对齐扩展包版本 + 更新日志。
- [ ] 更新 CLI/版本字符串：[`src/cli/program.ts`](https://github.com/openclaw/openclaw/blob/main/src/cli/program.ts) 和 Baileys 用户代理在 [`src/provider-web.ts`](https://github.com/openclaw/openclaw/blob/main/src/provider-web.ts) 中。
- [ ] 确认包元数据（名称、描述、存储库、关键字、许可证）以及 `bin` 映射指向 [`openclaw.mjs`](https://github.com/openclaw/openclaw/blob/main/openclaw.mjs) 对于 `openclaw`。
- [ ] 如果依赖项已更改，运行 `pnpm install` 使 `pnpm-lock.yaml` 保持最新。

2. **构建与工件**

- [ ] 如果 A2UI 输入已更改，运行 `pnpm canvas:a2ui:bundle` 并提交任何更新的 [`src/canvas-host/a2ui/a2ui.bundle.js`](https://github.com/openclaw/openclaw/blob/main/src/canvas-host/a2ui/a2ui.bundle.js)。
- [ ] `pnpm run build`（重新生成 `dist/`）。
- [ ] 验证 npm 包 `files` 包含所有必需的 `dist/*` 文件夹（特别是 `dist/node-host/**` 和 `dist/acp/**` 用于无头节点 + ACP CLI）。
- [ ] 确认 `dist/build-info.json` 存在并包含预期的 `commit` 哈希（CLI横幅使用此哈希进行 npm 安装）。
- [ ] 可选：构建后运行 `npm pack --pack-destination /tmp`；检查 tarball 内容并保留以备 GitHub 发布（不要提交）。

3. **更新日志与文档**

- [ ] 使用用户可见的亮点更新 `CHANGELOG.md`（如果文件缺失则创建）；严格按版本降序排列条目。
- [ ] 确保 README 示例/标志与当前 CLI 行为匹配（特别是新命令或选项）。

4. **验证**

- [ ] `pnpm build`
- [ ] `pnpm check`
- [ ] `pnpm test`（或 `pnpm test:coverage` 如果需要覆盖率输出）
- [ ] `pnpm release:check`（验证 npm pack 内容）
- [ ] `OPENCLAW_INSTALL_SMOKE_SKIP_NONROOT=1 pnpm test:install:smoke`（Docker 安装冒烟测试，快速路径；发布前必需）
  - 如果最近一次 npm 发布已知有问题，请在预安装步骤中设置 `OPENCLAW_INSTALL_SMOKE_PREVIOUS=<last-good-version>` 或 `OPENCLAW_INSTALL_SMOKE_SKIP_PREVIOUS=1`。
- [ ] （可选）完整安装冒烟（添加非 root + CLI 覆盖）：`pnpm test:install:smoke`
- [ ] （可选）安装端到端测试（Docker，运行 `curl -fsSL https://openclaw.ai/install.sh | bash`，注册，然后运行实际工具调用）：
  - `pnpm test:install:e2e:openai`（需要 `OPENAI_API_KEY`）
  - `pnpm test:install:e2e:anthropic`（需要 `ANTHROPIC_API_KEY`）
  - `pnpm test:install:e2e`（需要两个密钥；运行两个提供者）
- [ ] （可选）如果更改影响发送/接收路径，则对 Web 网关进行点检。

5. **macOS 应用（Sparkle）**

- [ ] 构建并签名 macOS 应用，然后将其压缩以供分发。
- [ ] 生成 Sparkle 应用列表（通过 [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh) 生成 HTML 备注）并更新 `appcast.xml`。
- [ ] 保留应用压缩包（和可选的 dSYM 压缩包）以附加到 GitHub 发布。
- [ ] 遵循 [macOS 发布](/platforms/mac/release) 获取确切的命令和必需的环境变量。
  - `APP_BUILD` 必须是数字且单调递增（无 `-beta`）以便 Sparkle 正确比较版本。
  - 如果需要公证，请使用从 App Store Connect API 环境变量创建的 `openclaw-notary` 密钥串配置文件（参见 [macOS 发布](/platforms/mac/release)）。

6. **发布（npm）**

- [ ] 确认 git 状态干净；如有必要，提交并推送。
- [ ] 如需，运行 `npm login`（验证 2FA）。
- [ ] 运行 `npm publish --access public`（使用 `--tag beta` 进行预发布）。
- [ ] 验证注册表：`npm view openclaw version`，`npm view openclaw dist-tags`，和 `npx -y openclaw@X.Y.Z --version`（或 `--help`）。

### 故障排除（来自 2.0.0-beta2 发布的笔记）

- **npm pack/publish 悬挂或生成巨大的 tarball**：macOS 应用程序包在 `dist/OpenClaw.app`（和发布压缩包）中被扫入包中。通过 `package.json` `files` 白名单发布内容进行修复（包括 dist 子目录、docs、skills；排除应用程序包）。使用 `npm pack --dry-run` 确认 `dist/OpenClaw.app` 未列出。
- **npm auth web 循环用于 dist-tags**：使用旧版身份验证获取 OTP 提示：
  - `NPM_CONFIG_AUTH_TYPE=legacy npm dist-tag add openclaw@X.Y.Z latest`
- **`npx` 验证失败与 `ECOMPROMISED: Lock compromised`**：使用新鲜缓存重试：
  - `NPM_CONFIG_CACHE=/tmp/npm-cache-$(date +%s) npx -y openclaw@X.Y.Z --version`
- **标签需要在后期修复后重新指针**：强制更新并推送标签，然后确保 GitHub 发布资产仍然匹配：
  - `git tag -f vX.Y.Z && git push -f origin vX.Y.Z`

7. **GitHub 发布 + 应用列表**

- [ ] 打标签并推送：`git tag vX.Y.Z && git push origin vX.Y.Z`（或 `git push --tags`）。
- [ ] 为 `vX.Y.Z` 创建/刷新 GitHub 发布，标题为 **`openclaw X.Y.Z`**（不仅仅是标签）；正文应包括该版本的**完整**更新日志部分（亮点 + 更改 + 修复），内联（无裸链接），并且**正文内不得重复标题**。
- [ ] 附加工件：`npm pack` tarball（可选），`OpenClaw-X.Y.Z.zip`，和 `OpenClaw-X.Y.Z.dSYM.zip`（如果生成）。
- [ ] 提交更新后的 `appcast.xml` 并推送（Sparkle 从 main 提取）。
- [ ] 在干净的临时目录（无 `package.json`）中运行 `npx -y openclaw@X.Y.Z send --help` 以确认安装/CLI 入口点正常工作。
- [ ] 宣布/分享发布说明。

## 插件发布范围（npm）

我们仅在 `@openclaw/*` 范围下发布**现有 npm 插件**。未在 npm 上的捆绑插件保持**仅磁盘树**（仍在 `extensions/**` 中分发）。

派生列表的过程：

1. `npm search @openclaw --json` 并捕获包名称。
2. 与 `extensions/*/package.json` 名称进行比较。
3. 仅发布**交集**（已在 npm 上）。

当前 npm 插件列表（按需更新）：

- @openclaw/bluebubbles
- @openclaw/diagnostics-otel
- @openclaw/discord
- @openclaw/lobster
- @openclaw/matrix
- @openclaw/msteams
- @openclaw/nextcloud-talk
- @openclaw/nostr
- @openclaw/voice-call
- @openclaw/zalo
- @openclaw/zalouser

发布说明还必须指出**新的可选捆绑插件**，这些插件**默认不启用**（示例：`tlon`）。