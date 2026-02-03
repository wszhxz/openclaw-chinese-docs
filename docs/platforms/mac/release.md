---
summary: "OpenClaw macOS release checklist (Sparkle feed, packaging, signing)"
read_when:
  - Cutting or validating a OpenClaw macOS release
  - Updating the Sparkle appcast or feed assets
title: "macOS Release"
---
# OpenClaw macOS 发布版（Sparkle）

此应用现在支持 Sparkle 自动更新。发布构建必须使用 Developer ID 签名、压缩为 ZIP 文件，并通过带有已签名 appcast 条目进行发布。

## 前置条件

- 已安装开发者 ID 应用程序证书（示例：`Developer ID Application: <开发者名称> (<TEAMID>)`）。
- Sparkle 私钥路径需在环境变量中设置为 `SPARKLE_PRIVATE_KEY_FILE`（指向您的 Sparkle ed25519 私钥路径；公钥已嵌入 Info.plist）。
  - 若缺失，请检查 `~/.profile`。
- 若需 Gatekeeper 安全的 DMG/zip 分发，需设置 Notary 凭据（钥匙串配置文件或 API 密钥）用于 `xcrun notarytool`。
  - 我们使用名为 `openclaw-notary` 的钥匙串配置文件，该配置文件由 App Store Connect API 密钥环境变量在 shell 配置文件中创建：
    - `APP_STORE_CONNECT_API_KEY_P8`, `APP_STORE_CONNECT_KEY_ID`, `APP_STORE_CONNECT_ISSUER_ID`
    - `echo "$APP_STORE_CONNECT_API_KEY_P8" | sed 's/\\n/\n/g' > /tmp/openclaw-notary.p8`
    - `xcrun notarytool store-credentials "openclaw-notary" --key /tmp/openclaw-notary.p8 --key-id "$APP_STORE_CONNECT_KEY_ID" --issuer "$APP_STORE_CONNECT_ISSUER_ID"`
- 已安装 `pnpm` 依赖项（`pnpm install --config.node-linker=hoisted`）。
- Sparkle 工具会通过 SwiftPM 自动从 `apps/macos/.build/artifacts/sparkle/Sparkle/bin/` 获取（如 `sign_update`, `generate_appcast` 等）。

## 构建与打包

注意事项：

- `APP_BUILD` 映射到 `CFBundleVersion`/`sparkle:version`；保持为数字且单调递增（不带 `-beta`），否则 Sparkle 会将其视为相等。
- 默认为当前架构（`$(uname -m)`）。对于发布/通用构建，设置 `BUILD_ARCHS="arm64 x86_64"`（或 `BUILD_ARCHS=all`）。
- 使用 `scripts/package-mac-dist.sh` 生成发布制品（zip + DMG + 证书化）。使用 `scripts/package-mac-app.sh` 进行本地/开发打包。

```bash
# 从仓库根目录执行；设置发布 ID 以启用 Sparkle 饲养。
# APP_BUILD 必须为数字且单调递增，以便 Sparkle 比较。
BUNDLE_ID=bot.molt.mac \
APP_VERSION=2026.2.1 \
APP_BUILD="$(git rev-list --count HEAD)" \
BUILD_CONFIG=release \
SIGN_IDENTITY="Developer ID Application: <开发者名称> (<TEAMID>)" \
scripts/package-mac-app.sh

# 生成分发 zip（包含 Sparkle 差分支持的资源fork）
ditto -c -k --sequesterRsrc --keepParent dist/OpenClaw.app dist/OpenClaw-2026.2.1.zip

# 可选：也构建一个样式化的 DMG 供人类使用（拖到 /Applications）
scripts/create-dmg.sh dist/OpenClaw.app dist/OpenClaw-2026.2.1.dmg

# 推荐：构建 + 证书化/附加 zip + DMG
# 首先创建钥匙串配置文件一次：
#   xcrun notarytool store-credentials "openclaw-notary" \
#     --apple-id "<apple-id>" --team-id "<team-id>" --password "<app-specific-password>"
NOTARIZE=1 NOTARYTOOL_PROFILE=openclaw-notary \
BUNDLE_ID=bot.molt.mac \
APP_VERSION=2026.2.1 \
APP_BUILD="$(git rev-list --count HEAD)" \
BUILD_CONFIG=release \
SIGN_IDENTITY="Developer ID Application: <开发者名称> (<TEAMID>)" \
scripts/package-mac-dist.sh

# 可选：随发布一同分发 dSYM
ditto -c -k --keepParent apps/macos/.build/release/OpenClaw.app.dSYM dist/OpenClaw-2026.2.1.dSYM.zip
```

## appcast 条目

使用发布说明生成器，以便 Sparkle 渲染格式化的 HTML 说明：

```bash
SPARKLE_PRIVATE_KEY_FILE=/path/to/ed25519-private-key scripts/make_appcast.sh dist/OpenClaw-2026.2.1.zip https://raw.githubusercontent.com/openclaw/openclaw/main/appcast.xml
```

从 `CHANGELOG.md`（通过 [`scripts/changelog-to-html.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/changelog-to-html.sh)）生成 HTML 发布说明，并将其嵌入到 appcast 条目中。
在发布时，将更新的 `appcast.xml` 与发布资产（zip + dSYM）一同提交。

## 发布与验证

- 将 `OpenClaw-2026.2.1.zip`（和 `OpenClaw-2026.2.1.dSYM.zip`）上传到 GitHub 发布页面的 `v2026.2.1` 标签。
- 确保原始 appcast URL 与嵌入的 feed 匹配：`https://raw.githubusercontent.com/openclaw/openclaw/main/appcast.xml`。
- 简单验证：
  - `curl -I https://raw.githubusercontent.com/openclaw/openclaw/main/appcast.xml` 返回 200。
  - `curl -I <enclosure url>` 在上传资产后返回 200。
  - 在之前的公开构建中，从“关于”选项卡运行“检查更新…”并验证 Sparkle 是否能干净地安装新构建。

完成定义：签名应用 + appcast 已发布，更新流程可从旧版本安装中启动，且发布资产已附加到 GitHub 发布。