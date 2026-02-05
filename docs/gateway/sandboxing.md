---
summary: "How OpenClaw sandboxing works: modes, scopes, workspace access, and images"
title: Sandboxing
read_when: "You want a dedicated explanation of sandboxing or need to tune agents.defaults.sandbox."
status: active
---
# 沙箱化

OpenClaw 可以在 **Docker 容器内运行工具** 以减少影响范围。
这是 **可选** 的，并通过配置 (`agents.defaults.sandbox` 或
`agents.list[].sandbox`) 进行控制。如果禁用沙箱化，工具将在主机上运行。
网关保留在主机上；启用时工具执行将在隔离的沙箱中运行。

这不是一个完美的安全边界，但在模型执行愚蠢操作时，它实质上限制了文件系统和进程访问。

## 什么会被沙箱化

- 工具执行 (`exec`, `read`, `write`, `edit`, `apply_patch`, `process` 等)。
- 可选的沙箱浏览器 (`agents.defaults.sandbox.browser`)。
  - 默认情况下，当浏览器工具需要时，沙箱浏览器会自动启动（确保 CDP 可达）。
    通过 `agents.defaults.sandbox.browser.autoStart` 和 `agents.defaults.sandbox.browser.autoStartTimeoutMs` 进行配置。
  - `agents.defaults.sandbox.browser.allowHostControl` 允许沙箱会话明确指向主机浏览器。
  - 可选的白名单门控 `target: "custom"`: `allowedControlUrls`, `allowedControlHosts`, `allowedControlPorts`。

未被沙箱化的：

- 网关进程本身。
- 任何明确允许在主机上运行的工具（例如 `tools.elevated`）。
  - **提升的 exec 在主机上运行并绕过沙箱化。**
  - 如果禁用沙箱化，`tools.elevated` 不会更改执行（已经在主机上）。参见 [提升模式](/tools/elevated)。

## 模式

`agents.defaults.sandbox.mode` 控制 **何时** 使用沙箱化：

- `"off"`: 不使用沙箱化。
- `"non-main"`: 仅对 **非主** 会话进行沙箱化（如果您希望正常聊天在主机上，默认设置）。
- `"all"`: 每个会话都在沙箱中运行。
  注意：`"non-main"` 基于 `session.mainKey`（默认 `"main"`），而不是代理 ID。
  组/频道会话使用自己的密钥，因此它们被视为非主会话并将被沙箱化。

## 范围

`agents.defaults.sandbox.scope` 控制 **创建多少容器**：

- `"session"`（默认）：每个会话一个容器。
- `"agent"`：每个代理一个容器。
- `"shared"`：所有沙箱化会话共享一个容器。

## 工作区访问

`agents.defaults.sandbox.workspaceAccess` 控制 **沙箱可以看到什么**：

- `"none"`（默认）：工具在 `~/.openclaw/sandboxes` 下看到一个沙箱工作区。
- `"ro"`：以只读方式挂载代理工作区到 `/agent`（禁用 `write`/`edit`/`apply_patch`）。
- `"rw"`：以读写方式挂载代理工作区到 `/workspace`。

传入的媒体被复制到活动的沙箱工作区 (`media/inbound/*`)。
技能说明：`read` 工具是基于沙箱根目录的。使用 `workspaceAccess: "none"`，
OpenClaw 将符合条件的技能镜像到沙箱工作区 (`.../skills`) 以便读取。使用 `"rw"`，工作区技能可以从 `/workspace/skills` 读取。

## 自定义绑定挂载

`agents.defaults.sandbox.docker.binds` 将附加的主机目录挂载到容器中。
格式：`host:container:mode`（例如 `"/home/user/source:/source:rw"`）。

全局和每个代理的绑定会 **合并**（不会被替换）。在 `scope: "shared"` 下，每个代理的绑定将被忽略。

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

安全注意事项：

- 绑定绕过了沙箱文件系统：它们以您设置的模式暴露主机路径 (`:ro` 或 `:rw`)。
- 敏感挂载（例如 `docker.sock`，机密信息，SSH 密钥）除非绝对必要，否则应 `:ro`。
- 结合 `workspaceAccess: "ro"` 如果您只需要对工作区的只读访问；绑定模式保持独立。
- 参见 [沙箱与工具策略与提升](/gateway/sandbox-vs-tool-policy-vs-elevated) 了解绑定如何与工具策略和提升执行交互。

## 镜像 + 设置

默认镜像：`openclaw-sandbox:bookworm-slim`

构建一次：

```bash
scripts/sandbox-setup.sh
```

注意：默认镜像 **不** 包含 Node。如果某个技能需要 Node（或其他运行时），可以制作自定义镜像或通过
`sandbox.docker.setupCommand` 安装（需要网络出口 + 可写的根目录 +
root 用户）。

沙箱浏览器镜像：

```bash
scripts/sandbox-browser-setup.sh
```

默认情况下，沙箱容器以 **无网络** 模式运行。
通过 `agents.defaults.sandbox.docker.network` 覆盖。

Docker 安装和容器化网关位于此处：
[Docker](/install/docker)

## setupCommand（一次性容器设置）

`setupCommand` 在创建沙箱容器后 **仅运行一次**（不是每次运行）。
它通过 `sh -lc` 在容器内执行。

路径：

- 全局：`agents.defaults.sandbox.docker.setupCommand`
- 每个代理：`agents.list[].sandbox.docker.setupCommand`

常见陷阱：

- 默认 `docker.network` 是 `"none"`（无出口），因此包安装将会失败。
- `readOnlyRoot: true` 阻止写入；设置 `readOnlyRoot: false` 或制作自定义镜像。
- `user` 必须是 root 才能进行包安装（省略 `user` 或设置 `user: "0:0"`）。
- 沙箱执行 **不** 继承主机 `process.env`。使用
  `agents.defaults.sandbox.docker.env`（或自定义镜像）用于技能 API 密钥。

## 工具策略 + 逃生舱

工具允许/拒绝策略仍然适用于沙箱规则之前。如果某个工具被全局或每个代理拒绝，沙箱化不会将其恢复。

`tools.elevated` 是一个显式的逃生舱，在主机上运行 `exec`。
`/exec` 指令仅适用于授权发送者并且每个会话持久化；要硬禁用
`exec`，使用工具策略拒绝（参见 [沙箱与工具策略与提升](/gateway/sandbox-vs-tool-policy-vs-elevated)）。

调试：

- 使用 `openclaw sandbox explain` 检查有效的沙箱模式、工具策略和修复配置键。
- 参见 [沙箱与工具策略与提升](/gateway/sandbox-vs-tool-policy-vs-elevated) 了解“为什么这被阻止？”的心理模型。
  保持其锁定状态。

## 多代理覆盖

每个代理可以覆盖沙箱 + 工具：
`agents.list[].sandbox` 和 `agents.list[].tools`（加上 `agents.list[].tools.sandbox.tools` 用于沙箱工具策略）。
参见 [多代理沙箱 & 工具](/multi-agent-sandbox-tools) 了解优先级。

## 最小启用示例

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none",
      },
    },
  },
}
```

## 相关文档

- [沙箱配置](/gateway/configuration#agentsdefaults-sandbox)
- [多代理沙箱 & 工具](/multi-agent-sandbox-tools)
- [安全性](/gateway/security)