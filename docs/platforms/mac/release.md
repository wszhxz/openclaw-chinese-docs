---
summary: "OpenClaw macOS release checklist (Sparkle feed, packaging, signing)"
read_when:
  - Cutting or validating a OpenClaw macOS release
  - Updating the Sparkle appcast or feed assets
title: "macOS Release"
---
# OpenClaw macOS release (Sparkle)

此应用程序现在支持通过 Sparkle 自动更新。发布版本必须使用 Developer ID 签名、压缩并使用已签名的 appcast 条目发布。

## 前提条件

- 已安装 Developer ID Application 证书（示例：`Developer ID Application: <Developer Name> (<TEAMID>)`）。
- 在环境变量中设置 Sparkle 私钥路径作为 `SPARKLE_PRIVATE_KEY_FILE`（指向您的 Sparkle ed25519 私钥的路径；公钥已嵌入到 Info.plist 中）。如果缺失，请检查 `~/.profile`。
- 如果您希望进行 Gatekeeper 安全的 DMG/zip 分发，则需要 `xcrun notarytool` 的公证凭证（钥匙串配置文件或 API 密钥）。
  - 我们使用一个名为 `openclaw-notary` 的钥匙串配置文件，从您的 shell 配置文件中的 App Store Connect API 密钥环境变量创建：
    - `APP_STORE_CONNECT_API_KEY_P8`, `APP_STORE_CONNECT_KEY_ID`, `APP_STORE_CONNECT_ISSUER_ID`
    - `echo "$APP_STORE_CONNECT_API_KEY_P8" | sed 's/\\n/\n/g' > /tmp/openclaw-notary.p8`
    - `xcrun notarytool store-credentials "openclaw-notary" --key /tmp/openclaw-notary.p8 --key-id "$APP_STORE_CONNECT_KEY_ID" --issuer "$APP_STORE_CONNECT_ISSUER_ID"`
- 已安装 `pnpm` 依赖项 (`pnpm install --config.node-linker=hoisted`)。
- Sparkle 工具通过 SwiftPM 在 `apps/macos/.build/artifacts/sparkle/Sparkle/bin/` 自动获取 (`sign_update`, `generate_appcast` 等)。

## 构建与打包

注意事项：

- `APP_BUILD` 映射到 `CFBundleVersion`/`sparkle:version`；保持其为数字且单调递增（无 `-beta`），否则 Sparkle 会将其视为相等。
- 默认为当前架构 (`$(uname -m)`)。对于发布/通用构建，请设置 `BUILD_ARCHS="arm64 x86_64"`（或 `BUILD_ARCHS=all`）。
- 使用 `scripts/package-mac-dist.sh` 进行发布工件（zip + DMG + 公证）。使用 `scripts/package-mac-app.sh` 进行本地/开发打包。

```bash
# From repo root; set release IDs so Sparkle feed is enabled.
# APP_BUILD must be numeric + monotonic for Sparkle compare.
BUNDLE_ID=bot.molt.mac \
APP_VERSION=2026.2.21 \
APP_BUILD="$(git rev-list --count HEAD)" \
BUILD_CONFIG=release \
SIGN_IDENTITY="Developer ID Application: <Developer Name> (<TEAMID>)" \
scripts/package-mac-app.sh

# Zip for distribution (includes resource forks for Sparkle delta support)
ditto -c -k --sequesterRsrc --keepParent dist/OpenClaw.app dist/OpenClaw-2026.2.21.zip

# Optional: also build a styled DMG for humans (drag to /Applications)
scripts/create-dmg.sh dist/OpenClaw.app dist/OpenClaw-2026.2.21.dmg

# Recommended: build + notarize/staple zip + DMG
# First, create a keychain profile once:
#   xcrun notarytool store-credentials "openclaw-notary" \
#     --apple-id "<apple-id>" --team-id "<team-id>" --password "<app-specific-password>"
NOTARIZE=1 NOTARYTOOL_PROFILE=openclaw-notary \
BUNDLE_ID=bot.molt.mac \
APP_VERSION=2026.2.21 \
APP_BUILD="$(git rev-list --count HEAD)" \
BUILD_CONFIG=release \
SIGN_IDENTITY="Developer ID Application: <Developer Name> (<TEAMID>)" \
scripts/package-mac-dist.sh

# Optional: ship dSYM alongside the release
ditto -c -k --keepParent apps/macos/.build/release/OpenClaw.app.dSYM dist/OpenClaw-2026.2.21.dSYM.zip
```

## Appcast 条目

使用发布说明生成器，以便 Sparkle 渲染格式化的 HTML 说明：

```bash
SPARKLE_PRIVATE_KEY_FILE=/path/to/ed25519-private-key scripts/make_appcast.sh dist/OpenClaw-2026.2.21.zip https://raw.githubusercontent.com/openclaw/openclaw/main/appcast.xml
```

从 `CHANGELOG.md` 生成 HTML 发布说明（通过 [`scripts/changelog-to-html.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/changelog-to-html.sh)）并将它们嵌入到 appcast 条目中。
在发布时，与发布资产（zip + dSYM）一起提交更新后的 `appcast.xml`。

## 发布与验证

- 将 `OpenClaw-2026.2.21.zip`（和 `OpenClaw-2026.2.21.dSYM.zip`）上传到 GitHub 发布的标签 `v2026.2.21`。
- 确保原始 appcast URL 与嵌入的源匹配：`https://raw.githubusercontent.com/openclaw/openclaw/main/appcast.xml`。
- 基本检查：
  - `curl -I https://raw.githubusercontent.com/openclaw/openclaw/main/appcast.xml` 返回 200。
  - 资产上传后，`curl -I <enclosure url>` 返回 200。
  - 在之前的公共构建上，从“关于”选项卡运行“检查更新...”，并验证 Sparkle 是否干净地安装了新版本。

完成定义：已发布的签名应用程序 + appcast，更新流可以从较旧的已安装版本工作，并且发布资产已附加到 GitHub 发布。