---
summary: "macOS permission persistence (TCC) and signing requirements"
read_when:
  - Debugging missing or stuck macOS permission prompts
  - Packaging or signing the macOS app
  - Changing bundle IDs or app install paths
title: "macOS Permissions"
---
# macOS权限 (TCC)

macOS权限授予非常脆弱。TCC将权限授予与应用程序的代码签名、捆绑标识符和磁盘路径关联起来。如果其中任何一个发生变化，macOS会将该应用视为新应用，并可能删除或隐藏提示。

## 稳定权限的要求

- 相同路径：从固定位置运行应用程序（对于OpenClaw，`dist/OpenClaw.app`）。
- 相同捆绑标识符：更改捆绑ID会创建一个新的权限身份。
- 已签名的应用程序：未签名或临时签名的构建不会持久保存权限。
- 一致的签名：使用真实的Apple开发或开发者ID证书，以便在重新构建时签名保持稳定。

临时签名每次构建都会生成新的身份。macOS会忘记之前的授权，直到清除过期条目之前，提示可能会完全消失。

## 提示消失时的恢复检查清单

1. 退出应用程序。
2. 在系统设置 -> 隐私与安全中移除应用程序条目。
3. 从相同的路径重新启动应用程序并重新授予权限。
4. 如果提示仍然不出现，使用`tccutil`重置TCC条目后再次尝试。
5. 某些权限只有在完全重启macOS后才会重新出现。

示例重置（根据需要替换捆绑ID）：

```bash
sudo tccutil reset Accessibility ai.openclaw.mac
sudo tccutil reset ScreenCapture ai.openclaw.mac
sudo tccutil reset AppleEvents
```

## 文件和文件夹权限（桌面/文档/下载）

macOS也可能对终端/后台进程访问桌面、文档和下载进行限制。如果文件读取或目录列表挂起，请为执行文件操作的相同进程上下文授予访问权限（例如终端/iTerm、通过LaunchAgent启动的应用程序或SSH进程）。

解决方法：如果您想避免每个文件夹的授权，可以将文件移动到OpenClaw工作区(`~/.openclaw/workspace`)。

如果您正在测试权限，请始终使用真实证书签名。临时构建仅适用于不需要考虑权限的快速本地运行。