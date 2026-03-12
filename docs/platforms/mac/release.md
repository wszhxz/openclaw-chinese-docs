---
summary: "OpenClaw macOS release checklist (Sparkle feed, packaging, signing)"
read_when:
  - Cutting or validating a OpenClaw macOS release
  - Updating the Sparkle appcast or feed assets
title: "macOS Release"
---
# OpenClaw macOS 发布 (Sparkle)

此应用程序现在附带 Sparkle 自动更新。发布版本必须使用 Developer ID 签名、压缩，并通过签名的 appcast 条目发布。

## 前提条件

- 安装了 Developer ID Application 证书（例如：`Developer ID Application: <Developer Name> (<TEAMID>)`）。
- 在环境变量中设置 Sparkle 私钥路径为 `SPARKLE_PRIVATE_KEY_FILE`（指向你的 Sparkle ed25519 私钥；公钥嵌入 Info.plist 中）。如果缺失，请检查 `~/.profile`。
- 如果你希望分发 Gatekeeper 安全的 DMG/zip 文件，需要 Notary 凭据（keychain 配置文件或 API 密钥）`xcrun notarytool`。
  - 我们使用一个名为 `openclaw-notary` 的 Keychain 配置文件，该配置文件由 App Store Connect API 密钥环境变量在 shell 配置文件中创建：
    - `APP_STORE_CONNECT_API_KEY_P8`, `APP_STORE_CONNECT_KEY_ID`, `APP_STORE_CONNECT_ISSUER_ID`
    - `echo "$APP_STORE_CONNECT_API_KEY_P8" | sed 's/\\n/\n/g' > /tmp/openclaw-notary.p8`
    - `xcrun notarytool store-credentials "openclaw-notary" --key /tmp/openclaw-notary.p8 --key-id "$APP_STORE_CONNECT_KEY_ID" --issuer "$APP_STORE_CONNECT_ISSUER_ID"`
- 安装了 `pnpm` 依赖项 (`pnpm install --config.node-linker=hoisted`)。
- Sparkle 工具通过 SwiftPM 自动获取 `apps/macos/.build/artifacts/sparkle/Sparkle/bin/` (`sign_update`, `generate_appcast` 等)。

## 构建与打包

注意事项：

- `APP_BUILD` 映射到 `CFBundleVersion`/`sparkle:version`；请保持其为数字且单调递增（不要使用 `-beta`），否则 Sparkle 会将其视为相等。
- 如果省略了 `APP_BUILD`，则 `scripts/package-mac-app.sh` 会从 `APP_VERSION` 衍生出一个 Sparkle 安全的默认值 (`YYYYMMDDNN`: 稳定版默认为 `90`，预发布版本使用后缀派生的通道)，并使用该值和 git 提交计数中的较高者。
- 当发布工程需要特定的单调值时，仍然可以显式覆盖 `APP_BUILD`。
- 默认为当前架构 (`$(uname -m)`)。对于发布/通用构建，请设置 `BUILD_ARCHS="arm64 x86_64"`（或 `BUILD_ARCHS=all`）。
- 使用 `scripts/package-mac-dist.sh` 进行发布制品（zip + DMG + 公证）。使用 `scripts/package-mac-app.sh` 进行本地/开发打包。

```bash
# From repo root; set release IDs so Sparkle feed is enabled.
# APP_BUILD must be numeric + monotonic for Sparkle compare.
# Default is auto-derived from APP_VERSION when omitted.
BUNDLE_ID=ai.openclaw.mac \
APP_VERSION=2026.3.7 \
BUILD_CONFIG=release \
SIGN_IDENTITY="Developer ID Application: <Developer Name> (<TEAMID>)" \
scripts/package-mac-app.sh

# Zip for distribution (includes resource forks for Sparkle delta support)
ditto -c -k --sequesterRsrc --keepParent dist/OpenClaw.app dist/OpenClaw-2026.3.7.zip

# Optional: also build a styled DMG for humans (drag to /Applications)
scripts/create-dmg.sh dist/OpenClaw.app dist/OpenClaw-2026.3.7.dmg

# Recommended: build + notarize/staple zip + DMG
# First, create a keychain profile once:
#   xcrun notarytool store-credentials "openclaw-notary" \
#     --apple-id "<apple-id>" --team-id "<team-id>" --password "<app-specific-password>"
NOTARIZE=1 NOTARYTOOL_PROFILE=openclaw-notary \
BUNDLE_ID=ai.openclaw.mac \
APP_VERSION=2026.3.7 \
BUILD_CONFIG=release \
SIGN_IDENTITY="Developer ID Application: <Developer Name> (<TEAMID>)" \
scripts/package-mac-dist.sh

# Optional: ship dSYM alongside the release
ditto -c -k --keepParent apps/macos/.build/release/OpenClaw.app.dSYM dist/OpenClaw-2026.3.7.dSYM.zip
```

## Appcast 条目

使用发布说明生成器，以便 Sparkle 渲染格式化的 HTML 说明：

```bash
SPARKLE_PRIVATE_KEY_FILE=/path/to/ed25519-private-key scripts/make_appcast.sh dist/OpenClaw-2026.3.7.zip https://raw.githubusercontent.com/openclaw/openclaw/main/appcast.xml
```

从 `CHANGELOG.md` 生成 HTML 发布说明（通过 [`scripts/changelog-to-html.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/changelog-to-html.sh)）并将它们嵌入 appcast 条目中。
发布时，将更新后的 `appcast.xml` 与发布资源（zip + dSYM）一起提交。

## 发布与验证

- 将 `OpenClaw-2026.3.7.zip`（和 `OpenClaw-2026.3.7.dSYM.zip`）上传到 GitHub 发布标签 `v2026.3.7`。
- 确保原始 appcast URL 与嵌入的 feed 匹配：`https://raw.githubusercontent.com/openclaw/openclaw/main/appcast.xml`。
- 基本检查：
  - `curl -I https://raw.githubusercontent.com/openclaw/openclaw/main/appcast.xml` 返回 200。
  - 在上传资源后，`curl -I <enclosure url>` 返回 200。
  - 在之前的公开构建上，从“关于”选项卡运行“检查更新...”，并验证 Sparkle 能够干净地安装新构建。

完成定义：已发布签名的应用程序 + appcast，从旧版本开始的更新流程正常工作，并且发布资源已附加到 GitHub 发布。