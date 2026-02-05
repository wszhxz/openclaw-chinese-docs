---
summary: "OpenClaw macOS release checklist (Sparkle feed, packaging, signing)"
read_when:
  - Cutting or validating a OpenClaw macOS release
  - Updating the Sparkle appcast or feed assets
title: "macOS Release"
---
# OpenClaw macOS 版本发布 (Sparkle)

此应用现在包含 Sparkle 自动更新功能。发布版本必须使用 Developer ID 签名、压缩成 zip 格式，并通过签名的应用播客条目发布。

## 前提条件

- 已安装 Developer ID Application 证书 (示例: `Developer ID Application: <Developer Name> (<TEAMID>)`)。
- 在环境中设置 Sparkle 私钥路径为 `SPARKLE_PRIVATE_KEY_FILE` (您的 Sparkle ed25519 私钥路径；公钥嵌入到 Info.plist 中)。如果缺失，请检查 `~/.profile`。
- 如果您需要 Gatekeeper 安全的 DMG/zip 分发，需准备 `xcrun notarytool` 的公证凭证 (钥匙串配置文件或 API 密钥)。
  - 我们使用名为 `openclaw-notary` 的钥匙串配置文件，从 App Store Connect API 密钥环境变量在您的 shell 配置文件中创建：
    - `APP_STORE_CONNECT_API_KEY_P8`, `APP_STORE_CONNECT_KEY_ID`, `APP_STORE_CONNECT_ISSUER_ID`
    - `echo "$APP_STORE_CONNECT_API_KEY_P8" | sed 's/\\n/\n/g' > /tmp/openclaw-notary.p8`
    - `xcrun notarytool store-credentials "openclaw-notary" --key /tmp/openclaw-notary.p8 --key-id "$APP_STORE_CONNECT_KEY_ID" --issuer "$APP_STORE_CONNECT_ISSUER_ID"`
- 已安装 `pnpm` 依赖 (`pnpm install --config.node-linker=hoisted`)。
- Sparkle 工具通过 SwiftPM 在 `apps/macos/.build/artifacts/sparkle/Sparkle/bin/` 自动获取 (`sign_update`, `generate_appcast`, 等等)。

## 构建与打包

注意事项：

- `APP_BUILD` 映射到 `CFBundleVersion`/`sparkle:version`；保持其为数字且单调递增 (无 `-beta`)，否则 Sparkle 将其比较为相等。
- 默认为当前架构 (`$(uname -m)`)。对于发布/通用构建，请设置 `BUILD_ARCHS="arm64 x86_64"` (或 `BUILD_ARCHS=all`)。
- 对于发布产物 (zip + DMG + 公证)，使用 `scripts/package-mac-dist.sh`。对于本地/开发打包，使用 `scripts/package-mac-app.sh`。

```bash
# From repo root; set release IDs so Sparkle feed is enabled.
# APP_BUILD must be numeric + monotonic for Sparkle compare.
BUNDLE_ID=bot.molt.mac \
APP_VERSION=2026.2.3 \
APP_BUILD="$(git rev-list --count HEAD)" \
BUILD_CONFIG=release \
SIGN_IDENTITY="Developer ID Application: <Developer Name> (<TEAMID>)" \
scripts/package-mac-app.sh

# Zip for distribution (includes resource forks for Sparkle delta support)
ditto -c -k --sequesterRsrc --keepParent dist/OpenClaw.app dist/OpenClaw-2026.2.3.zip

# Optional: also build a styled DMG for humans (drag to /Applications)
scripts/create-dmg.sh dist/OpenClaw.app dist/OpenClaw-2026.2.3.dmg

# Recommended: build + notarize/staple zip + DMG
# First, create a keychain profile once:
#   xcrun notarytool store-credentials "openclaw-notary" \
#     --apple-id "<apple-id>" --team-id "<team-id>" --password "<app-specific-password>"
NOTARIZE=1 NOTARYTOOL_PROFILE=openclaw-notary \
BUNDLE_ID=bot.molt.mac \
APP_VERSION=2026.2.3 \
APP_BUILD="$(git rev-list --count HEAD)" \
BUILD_CONFIG=release \
SIGN_IDENTITY="Developer ID Application: <Developer Name> (<TEAMID>)" \
scripts/package-mac-dist.sh

# Optional: ship dSYM alongside the release
ditto -c -k --keepParent apps/macos/.build/release/OpenClaw.app.dSYM dist/OpenClaw-2026.2.3.dSYM.zip
```

## 应用播客条目

使用发布说明生成器以便 Sparkle 渲染格式化的 HTML 说明：

```bash
SPARKLE_PRIVATE_KEY_FILE=/path/to/ed25519-private-key scripts/make_appcast.sh dist/OpenClaw-2026.2.3.zip https://raw.githubusercontent.com/openclaw/openclaw/main/appcast.xml
```

从 `CHANGELOG.md` 生成 HTML 发布说明 (通过 [`scripts/changelog-to-html.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/changelog-to-html.sh)) 并将其嵌入到应用播客条目中。
发布时，将更新的 `appcast.xml` 与发布资源 (zip + dSYM) 一起提交。

## 发布与验证

- 上传 `OpenClaw-2026.2.3.zip` (和 `OpenClaw-2026.2.3.dSYM.zip`) 到标签为 `v2026.2.3` 的 GitHub 发布版本。
- 确保原始应用播客 URL 与内置的 feed 匹配: `https://raw.githubusercontent.com/openclaw/openclaw/main/appcast.xml`。
- 基本检查：
  - `curl -I https://raw.githubusercontent.com/openclaw/openclaw/main/appcast.xml` 返回 200。
  - 资源上传后，`curl -I <enclosure url>` 返回 200。
  - 在之前的公开版本上，从关于选项卡运行"检查更新..."并验证 Sparkle 能够干净地安装新版本。

完成定义：已发布签名的应用程序 + 应用播客，从较旧的已安装版本可以正常更新，并且发布资源已附加到 GitHub 发布版本。