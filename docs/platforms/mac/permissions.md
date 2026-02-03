---
summary: "macOS permission persistence (TCC) and signing requirements"
read_when:
  - Debugging missing or stuck macOS permission prompts
  - Packaging or signing the macOS app
  - Changing bundle IDs or app install paths
title: "macOS Permissions"
---
# macOS 权限（TCC）

macOS 权限授予是脆弱的。TCC 会将权限授予与应用程序的代码签名、捆绑标识符和磁盘上的路径相关联。如果其中任何一个发生变化，macOS 会将该应用程序视为新应用，可能会取消或隐藏提示。

## 稳定权限的要求

- 相同路径：从固定位置运行应用程序（对于 OpenClaw，路径为 `dist/OpenClaw.app`）。
- 相同捆绑标识符：更改捆绑标识符会创建新的权限身份。
- 签名的应用程序：未签名或临时签名的构建不会持久化权限。
- 一致的签名：使用真实的 Apple 开发者证书或开发者 ID 证书，以确保签名在重新构建时保持稳定。

临时签名会在每次构建时生成新的身份。macOS 会忘记之前的授权，提示可能会完全消失，直到清除过期条目。

## 提示消失时的恢复清单

1. 退出应用程序。
2. 在系统设置 -> 隐私与安全性中删除应用程序条目。
3. 从相同路径重新启动应用程序并重新授予权限。
4. 如果提示仍然未出现，请使用 `tccutil` 重置 TCC 条目并再次尝试。
5. 某些权限在完全重启 macOS 后才会重新出现。

示例重置（请根据需要替换捆绑标识符）：

```bash
sudo tccutil reset Accessibility bot.molt.mac
sudo tcc
```