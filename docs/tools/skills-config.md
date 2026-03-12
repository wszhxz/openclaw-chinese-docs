---
summary: "Skills config schema and examples"
read_when:
  - Adding or modifying skills config
  - Adjusting bundled allowlist or install behavior
title: "Skills Config"
---
# 技能配置

所有与技能相关的配置都位于 `skills` 下的 `~/.openclaw/openclaw.json` 中。

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
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // or plaintext string
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

- `allowBundled`: 仅用于**捆绑**技能的可选允许列表。设置后，只有列表中的捆绑技能才有资格（管理/工作区技能不受影响）。
- `load.extraDirs`: 额外的技能目录扫描（最低优先级）。
- `load.watch`: 监视技能文件夹并刷新技能快照（默认：true）。
- `load.watchDebounceMs`: 技能监视器事件的防抖时间（以毫秒为单位，默认：250）。
- `install.preferBrew`: 当可用时，优先使用brew安装程序（默认：true）。
- `install.nodeManager`: 节点安装程序偏好 (`npm` | `pnpm` | `yarn` | `bun`, 默认：npm)。这仅影响**技能安装**；网关运行时仍应为Node（不推荐Bun用于WhatsApp/Telegram）。
- `entries.<skillKey>`: 每个技能的覆盖项。

每个技能的字段：

- `enabled`: 设置 `false` 以禁用某个技能，即使它已捆绑/安装。
- `env`: 注入代理运行的环境变量（仅在未设置时注入）。
- `apiKey`: 对于声明了主要环境变量的技能，这是一个可选的便捷选项。支持纯文本字符串或SecretRef对象 (`{ source, provider, id }`)。

## 注意事项

- `entries` 下的键默认映射到技能名称。如果技能定义了 `metadata.openclaw.skillKey`，则使用该键。
- 当启用监视器时，对技能的更改将在下一个代理轮次中被拾取。

### 沙盒技能 + 环境变量

当会话被**沙盒化**时，技能进程在Docker内部运行。沙盒**不会**继承主机的 `process.env`。

请使用以下之一：

- `agents.defaults.sandbox.docker.env`（或每个代理的 `agents.list[].sandbox.docker.env`）
- 将环境变量烘焙到自定义沙盒镜像中

全局 `env` 和 `skills.entries.<skill>.env/apiKey` 仅适用于**主机**运行。