---
summary: "How OpenClaw sandboxing works: modes, scopes, workspace access, and images"
title: Sandboxing
read_when: "You want a dedicated explanation of sandboxing or need to tune agents.defaults.sandbox."
status: active
---
# 沙箱

OpenClaw 可以在 **Docker 容器中运行工具** 以降低影响范围。
这是 **可选** 的，由配置控制 (`agents.defaults.sandbox` 或
`agents.list[].sandbox`)。如果禁用沙箱，工具将在主机上运行。
网关始终在主机上运行；当启用沙箱时，工具执行将在隔离的沙箱中运行。

这不是一个完美的安全边界，但它在模型执行低效操作时，实质限制了文件系统和进程的访问。

## 什么会被沙箱化

- 工具执行 (`exec`, `read`, `write`, `edit`, `apply_patch`, `process` 等)。
- 可选沙箱化浏览器 (`agents.defaults.sandbox.browser`)。
  - 默认情况下，当浏览器工具需要时，沙箱浏览器会自动启动（确保 CDP 可达）。
    通过 `agents.defaults.sandbox.browser.autoStart` 和 `agents.defaults.sandbox.browser.auto
    .autoStartTimeoutMs` 配置。
  - `agents.defaults.sandbox.browser.allowHostControl` 允许沙箱会话显式指向主机浏览器。
  - 可选允许列表 `target: "custom"`：`allowedControlUrls`, `allowedControlHosts`, `allowedControlPorts`。

不被沙箱化：

- 网关进程本身。
- 任何明确允许在主机上运行的工具（例如 `tools.elevated`）。
  - **提升的 exec 在主机上运行并绕过沙箱。**
  - 如果禁用沙箱，`tools.elevated` 不会改变执行（已经位于主机）。请参阅 [提升模式](/tools/elevated)。

## 模式

`agents.defaults.sandbox.mode` 控制 **何时** 使用沙箱：

- `"off"`：不使用沙箱。
- `"non-main"`：仅沙箱 **非主** 会话（如果您希望在主机上进行普通聊天，默认模式）。
- `"all"`：每个会话都在沙箱中运行。
  注意：`"non-main"` 基于 `session.mainKey`（默认 `"main"`），而不是代理 ID。
  组/频道会话使用自己的密钥，因此它们被视为非主会话并会被沙箱化。

## 范围

`agents.defaults.sandbox.scope` 控制 **创建多少个容器**：

- `"session"`（默认）：每个会话一个容器。
- `"agent"`：每个代理一个容器。
- `"shared"`：所有沙箱化会话共享一个容器。

## 工作区访问

`agents.defaults.sandbox.workspaceAccess` 控制 **沙箱可以看到什么**：

- `"none"`（默认）：工具看到一个位于 `~/.openclaw/sandboxes` 的沙箱工作区。
- `"ro"`：以只读方式将代理工作区挂载到 `/agent`（禁用 `write`/`edit`/`apply_patch`）。
- `"rw"`：以读写方式将代理工作区挂载到 `/workspace`。

入站媒体会被复制到活动沙箱工作区 (`media/inbound/*`)。
技能提示：`read` 工具以沙箱根目录为起点。当 `workspaceAccess: "none"` 时，
OpenClaw 会将符合条件的技能镜像到沙箱工作区 (`.../skills`)，以便可以读取。
当 `"rw"` 时，工作区技能可以从 `/workspace/skills` 读取。

## 自定义绑定挂载

`agents.defaults.sandbox.docker.binds` 将额外的主机目录挂载到容器中。
格式：`host:container:mode`（例如，`"/home/user/source:/source:ro"`）。

全局和每个代理的绑定 **合并**（不替换）。在 `scope: "shared"` 下，每个代理的绑定会被忽略。

示例（只读源 + Docker 套接字）：

```json5
{
  agents: {
    defaults: {
      sandbox: {
        docker: {
          binds: ["/home/user/source:/source:ro", "/var/run/docker.sock:/var/run/docker.sock"],
        },
      },
    },
    list: [
      {
        id: "build",
        sandbox: {
          docker: {
            binds: ["/mnt/cache:/cache:rw"],
          },
        },
      },
    ],
  },
}
```

安全提示：

- 绑定绕过沙箱文件系统：它们暴露主机路径，无论您设置的模式如何（`:ro` 或 `:rw`）。
- 敏感挂载（例如 `docker.sock`、秘密、SSH 密钥）除非绝对必要，应使用 `:ro`。
- 如果您只需要工作区的只读访问，结合使用 `workspaceAccess: "ro"`；绑定模式保持独立。
- 请参阅 [沙箱 vs 工具策略 vs 提升](/gateway/sandbox-vs-tool-policy-vs-elevated) 了解绑定如何与工具策略和提升执行交互。

## 镜像 + 设置

默认镜像：`openclaw-sandbox:bookworm-slim`

构建一次：

```bash
scripts/sandbox-setup.sh
```

注意：默认镜像 **不** 包含 Node。如果某个技能需要 Node（或其他运行时），要么构建自定义镜像，要么通过
`sandbox.docker.setupCommand` 安装（需要网络出站 + 可写根 + root 用户）。

沙箱化浏览器镜像：

```bash
scripts/sandbox