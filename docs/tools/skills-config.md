---
summary: "Skills config schema and examples"
read_when:
  - Adding or modifying skills config
  - Adjusting bundled allowlist or install behavior
title: "Skills Config"
---
# 技能配置

所有与技能相关的配置都位于 `~/.openclaw/openclaw.json` 中的 `skills` 部分。

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
      nodeManager: "npm", // npm | pnpm | yarn | bun (网关运行时仍为 Node；bun 不推荐)
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

## 字段说明

- `allowBundled`: 仅允许**捆绑技能**的可选白名单。设置后，只有列表中的捆绑技能才符合条件（管理/工作区技能不受影响）。
- `load.extraDirs`: 额外扫描的技能目录（优先级最低）。
- `load.watch`: 监控技能文件夹并刷新技能快照（默认: true）。
- `load.watchDebounceMs`: 技能监视器事件的防抖时间（单位：毫秒，默认: 250）。
- `install.preferBrew`: 优先使用 brew 安装器（默认: true）。
- `install.nodeManager`: 节点安装器偏好（`npm` | `pnpm` | `yarn` | `bun`，默认: npm）。
  该设置仅影响**技能安装**；网关运行时仍应为 Node（Bun 不推荐用于 WhatsApp/Telegram）。
- `entries.<skillKey>`: 每个技能的覆盖配置。

每个技能的字段：

- `enabled`: 即使是捆绑或已安装的技能，设置为 `false` 也可禁用。
- `env`: 为代理运行注入的环境变量（仅在未设置时生效）。
- `apiKey`: 为声明主环境变量的技能提供便捷的可选字段。

## 注意事项

- 默认情况下，`entries` 下的键映射到技能名称。如果技能定义了 `metadata.openclaw.skillKey`，请使用该键。
- 当监视器启用时，技能更改将在下一次代理轮询时生效。

### 沙箱技能 + 环境变量

当会话被**沙箱化**时，技能进程将在 Docker 中运行。沙箱**不会**继承主机的 `process.env`。

可使用以下方式之一：

- `agents.defaults.sandbox.docker.env`（或每个代理 `agents.list[].sandbox.docker.env`）
- 将环境变量嵌入到自定义沙箱镜像中

全局 `env` 和 `skills.entries.<skill>.env/apiKey` 仅适用于**主机**运行。