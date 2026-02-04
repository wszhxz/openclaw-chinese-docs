---
summary: "Skills config schema and examples"
read_when:
  - Adding or modifying skills config
  - Adjusting bundled allowlist or install behavior
title: "Skills Config"
---
# 技能配置

所有与技能相关的配置位于 `skills` 下的 `~/.openclaw/openclaw.json` 中。

```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    load: {
      extraDirs: ["~/Projects/agent-scripts/skills", "~/Projects/oss/some-skill-pack/skills"],
      watch: true,
      watchDebounceMs: 250,
    },
    install: {
      preferBrew: true,
      nodeManager: "npm", // npm | pnpm | yarn | bun (Gateway runtime still Node; bun not recommended)
    },
    entries: {
      "nano-banana-pro": {
        enabled: true,
        apiKey: "GEMINI_KEY_HERE",
        env: {
          GEMINI_API_KEY: "GEMINI_KEY_HERE",
        },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

## 字段

- `allowBundled`: 仅适用于 **捆绑** 技能的可选白名单。当设置时，只有列表中的捆绑技能有资格（管理/工作区技能不受影响）。
- `load.extraDirs`: 额外的技能目录以供扫描（优先级最低）。
- `load.watch`: 监视技能文件夹并刷新技能快照（默认：true）。
- `load.watchDebounceMs`: 技能监视器事件的防抖时间（以毫秒为单位，默认：250）。
- `install.preferBrew`: 当可用时优先使用 brew 安装程序（默认：true）。
- `install.nodeManager`: 节点安装程序首选项 (`npm` | `pnpm` | `yarn` | `bun`，默认：npm)。
  这仅影响 **技能安装**；网关运行时应仍为 Node（不建议 Bun 用于 WhatsApp/Telegram）。
- `entries.<skillKey>`: 每个技能的覆盖。

每个技能的字段：

- `enabled`: 将 `false` 设置为禁用技能，即使它是捆绑/已安装的。
- `env`: 为代理运行注入的环境变量（仅在未设置的情况下）。
- `apiKey`: 适用于声明了主要环境变量的技能的可选便利性。

## 注意事项

- `entries` 下的键默认映射到技能名称。如果技能定义了 `metadata.openclaw.skillKey`，则使用该键。
- 启用监视器时，技能更改将在下一个代理轮次中被拾取。

### 沙盒化技能 + 环境变量

当会话是 **沙盒化** 的，技能进程在 Docker 内运行。沙盒 **不** 继承主机的 `process.env`。

使用以下方法之一：

- `agents.defaults.sandbox.docker.env`（或每个代理的 `agents.list[].sandbox.docker.env`）
- 将 env 烘焙到自定义沙盒镜像中

全局 `env` 和 `skills.entries.<skill>.env/apiKey` 仅适用于 **主机** 运行。