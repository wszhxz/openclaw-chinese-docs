---
title: "Release Checklist"
summary: "Step-by-step release checklist for npm + macOS app"
read_when:
  - Cutting a new npm release
  - Cutting a new macOS app release
  - Verifying metadata before publishing
---
# 发布检查清单（npm + macOS）

从代码仓库根目录运行 `pnpm`（Node 22+）。在打标签/发布前，请确保工作树处于干净状态。

## 运算符触发

当运维人员说出“release”时，立即执行以下预检步骤（除非被阻塞，否则不额外提问）：

- 阅读本文档及 `docs/platforms/mac/release.md`。
- 从 `~/.profile` 加载环境变量，并确认已设置 `SPARKLE_PRIVATE_KEY_FILE` 和 App Store Connect 相关变量（`SPARKLE_PRIVATE_KEY_FILE` 应位于 `~/.profile`）。
- 如需，使用来自 `~/Library/CloudStorage/Dropbox/Backup/Sparkle` 的 Sparkle 密钥。

1. **版本与元数据**

- [ ] 更新 `package.json` 版本号（例如：`2026.1.29`）。
- [ ] 运行 `pnpm plugins:sync` 以同步扩展包版本与变更日志。
- [ ] 更新 [`src/version.ts`](https://github.com/openclaw/openclaw/blob/main/src/version.ts) 中的 CLI/版本字符串，以及 [`src/web/session.ts`](https://github.com/openclaw/openclaw/blob/main/src/web/session.ts) 中 Baileys 的用户代理字符串。
- [ ] 确认包元数据（名称、描述、仓库地址、关键词、许可证）及 `bin` 映射指向 [`openclaw.mjs`](https://github.com/openclaw/openclaw/blob/main/openclaw.mjs)，对应 `openclaw`。
- [ ] 若依赖项有变更，请运行 `pnpm install`，确保 `pnpm-lock.yaml` 为最新。

2. **构建与产物**

- [ ] 若 A2UI 输入文件发生变更，请运行 `pnpm canvas:a2ui:bundle`，并提交任何更新后的 [`src/canvas-host/a2ui/a2ui.bundle.js`](https://github.com/openclaw/openclaw/blob/main/src/canvas-host/a2ui/a2ui.bundle.js)。
- [ ] 运行 `pnpm run build`（重新生成 `dist/`）。
- [ ] 验证 npm 包 `files` 是否包含所有必需的 `dist/*` 文件夹（特别是用于无头 Node 和 ACP CLI 的 `dist/node-host/**` 与 `dist/acp/**`）。
- [ ] 确认 `dist/build-info.json` 存在且包含预期的 `commit` 哈希值（CLI 启动横幅在 npm 安装时使用该哈希）。
- [ ] （可选）构建完成后运行 `npm pack --pack-destination /tmp`；检查 tarball 内容，并将其保留备用以供 GitHub 发布使用（**切勿提交**）。

3. **变更日志与文档**

- [ ] 使用面向用户的重点内容更新 `CHANGELOG.md`（若文件不存在则新建）；条目须严格按版本号降序排列。
- [ ] 确保 README 中的示例和命令行参数与当前 CLI 行为一致（尤其是新增命令或选项）。

4. **验证**

- [ ] 执行 `pnpm build`
- [ ] 执行 `pnpm check`
- [ ] 执行 `pnpm test`（或执行 `pnpm test:coverage` 获取覆盖率输出）
- [ ] 执行 `pnpm release:check`（校验 `npm pack` 产物内容）
- [ ] 执行 `OPENCLAW_INSTALL_SMOKE_SKIP_NONROOT=1 pnpm test:install:smoke`（Docker 安装冒烟测试，快速路径；发布前必须通过）
  - 若已知上一个 npm 版本存在严重缺陷，请在预安装步骤中设置 `OPENCLAW_INSTALL_SMOKE_PREVIOUS=<last-good-version>` 或 `OPENCLAW_INSTALL_SMOKE_SKIP_PREVIOUS=1`。
- [ ] （可选）完整安装器冒烟测试（涵盖非 root 用户 + CLI 覆盖率）：`pnpm test:install:smoke`
- [ ] （可选）安装器端到端测试（Docker 环境，运行 `curl -fsSL https://openclaw.ai/install.sh | bash`，完成初始配置后调用真实工具）：
  - `pnpm test:install:e2e:openai`（需 `OPENAI_API_KEY`）
  - `pnpm test:install:e2e:anthropic`（需 `ANTHROPIC_API_KEY`）
  - `pnpm test:install:e2e`（需同时具备两个密钥；运行双提供商流程）
- [ ] （可选）若您的修改影响收发路径，请抽样检查 Web 网关。

5. **macOS 应用（Sparkle）**

- [ ] 构建并签名 macOS 应用，然后打包为 zip 以供分发。
- [ ] 生成 Sparkle appcast（HTML 格式说明文档，通过 [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh) 生成），并更新 `appcast.xml`。
- [ ] 将应用 zip 包（及可选的 dSYM zip 包）准备好，以便附加至 GitHub 发布页。
- [ ] 按照 [macOS 发布指南](/platforms/mac/release) 执行确切命令及所需环境变量。
  - `APP_BUILD` 必须为纯数字且单调递增（不可含 `-beta`），以确保 Sparkle 正确比较版本。
  - 若需公证（notarization），请使用基于 App Store Connect API 环境变量创建的 `openclaw-notary` 密钥链配置文件（参见 [macOS 发布指南](/platforms/mac/release)）。

6. **发布（npm）**

- [ ] 确认 Git 状态干净；按需提交并推送。
- [ ] 如需，请执行 `npm login`（验证双重认证）。
- [ ] 执行 `npm publish --access public`（预发布版本请使用 `--tag beta`）。
- [ ] 验证注册表：`npm view openclaw version`、`npm view openclaw dist-tags` 和 `npx -y openclaw@X.Y.Z --version`（或 `--help`）。

### 故障排查（源自 2.0.0-beta2 发布的经验记录）

- **`npm pack` / `npm publish` 卡住或生成超大 tarball**：``dist/OpenClaw.app``（及发布 zip 包）中的 macOS 应用程序包会被一并纳入发布包。修复方式是通过 `package.json` `files` 显式声明发布内容白名单（包含 `dist` 子目录、`docs`、`skills`；排除应用程序包）。使用 `npm pack --dry-run` 确认 `dist/OpenClaw.app` 未出现在列表中。
- **`dist-tags` 的 npm 认证陷入网页循环**：改用传统认证方式以获取一次性验证码（OTP）提示：
  - `NPM_CONFIG_AUTH_TYPE=legacy npm dist-tag add openclaw@X.Y.Z latest`
- **``npx`` 校验失败并报错 ``ECOMPROMISED: Lock compromised``**：尝试清空缓存后重试：
  - `NPM_CONFIG_CACHE=/tmp/npm-cache-$(date +%s) npx -y openclaw@X.Y.Z --version`
- **因后期修复需重置标签指向**：强制更新并推送标签，随后确保 GitHub 发布资产仍保持匹配：
  - `git tag -f vX.Y.Z && git push -f origin vX.Y.Z`

7. **GitHub 发布 + appcast**

- [ ] 打标签并推送：`git tag vX.Y.Z && git push origin vX.Y.Z`（或 `git push --tags`）。
- [ ] 为 `vX.Y.Z` 创建或刷新 GitHub 发布页，**标题必须为 `openclaw X.Y.Z`**（而不仅为标签名）；正文应内联包含该版本的**完整**变更日志章节（亮点 Highlights + 变更 Changes + 修复 Fixes），**不得仅放置裸链接，且正文中不得重复标题内容**。
- [ ] 附加产物：`npm pack` tarball（可选）、`OpenClaw-X.Y.Z.zip` 及 `OpenClaw-X.Y.Z.dSYM.zip`（如已生成）。
- [ ] 提交更新后的 `appcast.xml` 并推送（Sparkle 从 `main` 分支拉取）。
- [ ] 在一个干净的临时目录中（不含 `package.json`），运行 `npx -y openclaw@X.Y.Z send --help`，确认安装及 CLI 入口点正常工作。
- [ ] 发布并分享发行说明。

## 插件发布范围（npm）

我们仅发布已存在于 npm 上、归属 `@openclaw/*` 作用域下的**现有 npm 插件**。未发布至 npm 的捆绑插件将**仅保留在磁盘目录结构中**（但仍随 `extensions/**` 一同分发）。

推导插件列表的流程如下：

1. 运行 `npm search @openclaw --json` 并捕获包名。
2. 与 `extensions/*/package.json` 中的名称进行比对。
3. 仅发布两者的**交集部分**（即已在 npm 上发布的插件）。

当前 npm 插件列表（请按需更新）：

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

发行说明中还须特别指出**新加入的可选捆绑插件**（这些插件**默认不启用**），例如：`tlon`。