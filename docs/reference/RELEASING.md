---
summary: "Step-by-step release checklist for npm + macOS app"
read_when:
  - Cutting a new npm release
  - Cutting a new macOS app release
  - Verifying metadata before publishing
---
# 发布检查清单 (npm + macOS)

从仓库根目录使用 `pnpm` (Node 22+)。在标记/发布之前保持工作树干净。

## 操作员触发

当操作员说"发布"时，立即执行此预检（除非受阻，否则无需额外询问）：

- 阅读本文档和 `docs/platforms/mac/release.md`。
- 从 `~/.profile` 加载环境变量并确认设置了 `SPARKLE_PRIVATE_KEY_FILE` + App Store Connect 变量（SPARKLE_PRIVATE_KEY_FILE 应位于 `~/.profile` 中）。
- 如需要，使用来自 `~/Library/CloudStorage/Dropbox/Backup/Sparkle` 的 Sparkle 密钥。

1. **版本和元数据**

- [ ] 提升 `package.json` 版本（例如，`2026.1.29`）。
- [ ] 运行 `pnpm plugins:sync` 以对齐扩展包版本 + 更新日志。
- [ ] 更新 CLI/版本字符串：[`src/cli/program.ts`](https://github.com/openclaw/openclaw/blob/main/src/cli/program.ts) 和 [`src/provider-web.ts`](https://github.com/openclaw/openclaw/blob/main/src/provider-web.ts) 中的 Baileys 用户代理。
- [ ] 确认包元数据（名称、描述、仓库、关键词、许可证）和 `bin` 映射点指向 [`openclaw.mjs`](https://github.com/openclaw/openclaw/blob/main/openclaw.mjs) 用于 `openclaw`。
- [ ] 如果依赖项发生变化，运行 `pnpm install` 以便 `pnpm-lock.yaml` 是最新的。

2. **构建和构件**

- [ ] 如果 A2UI 输入发生变化，运行 `pnpm canvas:a2ui:bundle` 并提交任何更新的 [`src/canvas-host/a2ui/a2ui.bundle.js`](https://github.com/openclaw/openclaw/blob/main/src/canvas-host/a2ui/a2ui.bundle.js)。
- [ ] `pnpm run build`（重新生成 `dist/`）。
- [ ] 验证 npm 包 `files` 包含所有必需的 `dist/*` 文件夹（特别是 `dist/node-host/**` 和 `dist/acp/**` 用于无头节点 + ACP CLI）。
- [ ] 确认 `dist/build-info.json` 存在并包含预期的 `commit` 哈希值（CLI 横幅在 npm 安装中使用此值）。
- [ ] 可选：构建后运行 `npm pack --pack-destination /tmp`；检查压缩包内容并将其保存以供 GitHub 发布使用（请勿提交）。

3. **更新日志和文档**

- [ ] 使用面向用户的亮点更新 `CHANGELOG.md`（如果文件不存在则创建）；保持条目按版本严格降序排列。
- [ ] 确保 README 示例/标志符与当前 CLI 行为匹配（特别是新命令或选项）。

4. **验证**

- [ ] `pnpm build`
- [ ] `pnpm check`
- [ ] `pnpm test`（或如果你需要覆盖率输出则使用 `pnpm test:coverage`）
- [ ] `pnpm release:check`（验证 npm 打包内容）
- [ ] `OPENCLAW_INSTALL_SMOKE_SKIP_NONROOT=1 pnpm test:install:smoke`（Docker 安装冒烟测试，快速路径；发布前必需）
  - 如果已知上一个 npm 发布版本有缺陷，请为预安装步骤设置 `OPENCLAW_INSTALL_SMOKE_PREVIOUS=<last-good-version>` 或 `OPENCLAW_INSTALL_SMOKE_SKIP_PREVIOUS=1`。
- [ ] （可选）完整安装程序冒烟测试（增加非 root + CLI 覆盖率）：`pnpm test:install:smoke`
- [ ] （可选）安装程序端到端测试（Docker，运行 `curl -fsSL https://openclaw.ai/install.sh | bash`，进行引导，然后运行真实工具调用）：
  - `pnpm test:install:e2e:openai`（需要 `OPENAI_API_KEY`）
  - `pnpm test:install:e2e:anthropic`（需要 `ANTHROPIC_API_KEY`）
  - `pnpm test:install:e2e`（需要两个密钥；运行两个提供者）
- [ ] （可选）如果你的更改影响发送/接收路径，请抽查 web 网关。

5. **macOS 应用程序 (Sparkle)**

- [ ] 构建并签名 macOS 应用程序，然后将其压缩以供分发。
- [ ] 生成 Sparkle appcast（HTML 注释通过 [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)）并更新 `appcast.xml`。
- [ ] 保留应用程序 zip（和可选的 dSYM zip）以准备附加到 GitHub 发布。
- [ ] 遵循 [macOS release](/platforms/mac/release) 获取确切的命令和必需的环境变量。
  - `APP_BUILD` 必须是数字且单调递增（不能有 `-beta`），以便 Sparkle 正确比较版本。
  - 如果需要公证，请使用从 App Store Connect API 环境变量创建的 `openclaw-notary` 密钥链配置文件（参见 [macOS release](/platforms/mac/release)）。

6. **发布 (npm)**

- [ ] 确认 git 状态干净；根据需要提交和推送。
- [ ] 如需要，运行 `npm login`（验证 2FA）。
- [ ] `npm publish --access public`（预发布使用 `--tag beta`）。
- [ ] 验证注册表：`npm view openclaw version`、`npm view openclaw dist-tags` 和 `npx -y openclaw@X.Y.Z --version`（或 `--help`）。

### 故障排除（来自 2.0.0-beta2 发布的注释）

- **npm 打包/发布挂起或产生巨大压缩包**：`dist/OpenClaw.app` 中的 macOS 应用程序包（和发布 zip）被卷入包中。通过白名单发布内容修复：`package.json` `files`（包括 dist 子目录、文档、技能；排除应用程序包）。通过 `npm pack --dry-run` 确认 `dist/OpenClaw.app` 未列出。
- **npm auth web 循环用于 dist-tags**：使用传统认证获取 OTP 提示：
  - `NPM_CONFIG_AUTH_TYPE=legacy npm dist-tag add openclaw@X.Y.Z latest`
- **`npx` 验证失败显示 `ECOMPROMISED: Lock compromised`**：使用新鲜缓存重试：
  - `NPM_CONFIG_CACHE=/tmp/npm-cache-$(date +%s) npx -y openclaw@X.Y.Z --version`
- **晚期修复后需要重新指向标签**：强制更新并推送标签，然后确保 GitHub 发布资产仍然匹配：
  - `git tag -f vX.Y.Z && git push -f origin vX.Y.Z`

7. **GitHub 发布 + appcast**

- [ ] 标记并推送：`git tag vX.Y.Z && git push origin vX.Y.Z`（或 `git push --tags`）。
- [ ] 为 `vX.Y.Z` 创建/刷新 GitHub 发布，**标题为 `openclaw X.Y.Z`**（不仅仅是标签）；正文应包含该版本的**完整**更新日志部分（亮点 + 更改 + 修复），内联显示（无纯链接），并且**不得在正文中重复标题**。
- [ ] 附加构件：`npm pack` 压缩包（可选）、`OpenClaw-X.Y.Z.zip` 和 `OpenClaw-X.Y.Z.dSYM.zip`（如已生成）。
- [ ] 提交更新的 `appcast.xml` 并推送它（Sparkle 从主分支获取）。
- [ ] 在干净的临时目录（没有 `package.json`）中，运行 `npx -y openclaw@X.Y.Z send --help` 以确认安装/CLI 入口点正常工作。
- [ ] 宣布/分享发布说明。

## 插件发布范围 (npm)

我们只在 `@openclaw/*` 范围下发布**现有的 npm 插件**。不在 npm 上的捆绑
插件保持**仅磁盘树**（仍包含在
`extensions/**` 中）。

派生列表的过程：

1. `npm search @openclaw --json` 并捕获包名。
2. 与 `extensions/*/package.json` 名称进行比较。
3. 仅发布**交集**（已在 npm 上）。

当前 npm 插件列表（根据需要更新）：

- @openclaw/bluebubbles
- @openclaw/diagnostics-otel
- @openclaw/discord
- @openclaw/feishu
- @openclaw/lobster
- @openclaw/matrix
- @openclaw/msteams
- @openclaw/nextcloud-talk
- @openclaw/nostr
- @openclaw/voice-call
- @openclaw/zalo
- @openclaw/zalouser

发布说明还必须指出**新的可选捆绑插件**，这些插件**默认不启用**（示例：`tlon`）。