---
summary: "Bun workflow (experimental): installs and gotchas vs pnpm"
read_when:
  - You want the fastest local dev loop (bun + watch)
  - You hit Bun install/patch/lifecycle script issues
title: "Bun (Experimental)"
---
# Bun（实验性）

目标：使用 **Bun**（可选，不建议用于 WhatsApp/Telegram）运行此仓库，而无需偏离 pnpm 工作流。

⚠️ **不建议用于网关运行时**（WhatsApp/Telegram 存在 bug）。生产环境请使用 Node。

## 状态

- Bun 是一个可选的本地运行时，用于直接运行 TypeScript（`bun run …`，`bun --watch …`）。
- `pnpm` 是默认的构建工具，且完全支持（并被某些文档工具使用）。
- Bun 无法使用 `pnpm-lock.yaml`，并将忽略它。

## 安装

默认：

```sh
bun install
```

注意：`bnad.lock`/`bun.lockb` 被 git 忽略，因此无论哪种方式都不会产生仓库变更。如果你想实现**无锁文件写入**：

```sh
bun install --no-save
```

## 构建 / 测试（Bun）

```sh
bun run build
bun run vitest run
```

## Bun 生命周期脚本（默认被阻止）

除非明确信任，Bun 可能会阻止依赖项生命周期脚本（`bun pm untrusted` / `bun pm trust`）。
对于此仓库，通常被阻止的脚本并不需要：

- `@whiskeysockets/baileys` `preinstall`：检查 Node 主版本 >= 20（我们运行的是 Node 22+）。
- `protobufjs` `postinstall`：发出关于不兼容版本方案的警告（无构建产物）。

如果你遇到需要这些脚本的真实运行时问题，请显式信任它们：

```sh
bun pm trust @whiskeysockets/baileys protobufjs
```

## 注意事项

- 一些脚本仍硬编码了 pnpm（例如 `docs:build`，`ui:*`，`protocol:check`）。目前请通过 pnpm 运行这些脚本。