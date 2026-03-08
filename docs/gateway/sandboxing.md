---
summary: "How OpenClaw sandboxing works: modes, scopes, workspace access, and images"
title: Sandboxing
read_when: "You want a dedicated explanation of sandboxing or need to tune agents.defaults.sandbox."
status: active
---
# 沙箱隔离

OpenClaw 可以在 **Docker 容器内运行工具** 以减少爆炸半径。
这是 **可选的**，由配置控制 (`agents.defaults.sandbox` 或
`agents.list[].sandbox`)。如果沙箱关闭，工具将在主机上运行。
网关保持在主机上；启用时，工具执行在隔离的沙箱中运行。

这不是一个完美的安全边界，但当模型做出愚蠢行为时，它能实质性地限制文件系统和进程访问。

## 哪些内容会被沙箱化

- 工具执行 (`exec`, `read`, `write`, `edit`, `apply_patch`, `process`, 等)。
- 可选的沙箱浏览器 (`agents.defaults.sandbox.browser`)。
  - 默认情况下，当浏览器工具需要时，沙箱浏览器会自动启动（确保 CDP 可达）。
    通过 `agents.defaults.sandbox.browser.autoStart` 和 `agents.defaults.sandbox.browser.autoStartTimeoutMs` 进行配置。
  - 默认情况下，沙箱浏览器容器使用专用的 Docker 网络 (`openclaw-sandbox-browser`)，而不是全局 `bridge` 网络。
    使用 `agents.defaults.sandbox.browser.network` 进行配置。
  - 可选的 `agents.defaults.sandbox.browser.cdpSourceRange` 使用 CIDR 白名单限制容器边缘 CDP 入站（例如 `172.21.0.1/32`）。
  - noVNC 观察者访问默认受密码保护；OpenClaw 生成一个短期有效的令牌 URL，用于提供本地引导页面，并在 URL 片段中打开带有密码的 noVNC（不在查询/头日志中）。
  - `agents.defaults.sandbox.browser.allowHostControl` 允许沙箱会话明确指向主机浏览器。
  - 可选的白名单控制 `target: "custom"`：`allowedControlUrls`, `allowedControlHosts`, `allowedControlPorts`。

未沙箱化的内容：

- 网关进程本身。
- 任何明确允许在主机上运行的工具（例如 `tools.elevated`）。
  - **提升权限的执行在主机上运行并绕过沙箱。**
  - 如果沙箱关闭，`tools.elevated` 不会改变执行方式（已在主机上）。参见 [提升模式](/tools/elevated)。

## 模式

`agents.defaults.sandbox.mode` 控制沙箱使用的 **时机**：

- `"off"`：无沙箱。
- `"non-main"`：仅沙箱化 **非主** 会话（如果您希望在主机上进行正常聊天，则为默认值）。
- `"all"`：每个会话都在沙箱中运行。
  注意：`"non-main"` 基于 `session.mainKey`（默认 `"main"`），而非代理 ID。
  组/频道会话使用自己的密钥，因此它们被视为非主会话并将被沙箱化。

## 范围

`agents.defaults.sandbox.scope` 控制创建 **多少个容器**：

- `"session"`（默认）：每个会话一个容器。
- `"agent"`：每个代理一个容器。
- `"shared"`：所有沙箱会话共享一个容器。

## 工作区访问

`agents.defaults.sandbox.workspaceAccess` 控制 **沙箱能看到什么**：

- `"none"`（默认）：工具在 `~/.openclaw/sandboxes` 下看到一个沙箱工作区。
- `"ro"`：以只读方式挂载代理工作区到 `/agent`（禁用 `write`/`edit`/`apply_patch`）。
- `"rw"`：以读写方式挂载代理工作区到 `/workspace`。

传入媒体被复制到活动的沙箱工作区 (`media/inbound/*`)。
技能说明：`read` 工具位于沙箱根目录。
使用 `workspaceAccess: "none"`，OpenClaw 将符合条件的技能镜像到沙箱工作区 (`.../skills`) 以便读取。
使用 `"rw"`，工作区技能可从 `/workspace/skills` 读取。

## 自定义绑定挂载

`agents.defaults.sandbox.docker.binds` 将额外的主机目录挂载到容器中。
格式：`host:container:mode`（例如 `"/home/user/source:/source:rw"`）。

全局和按代理的绑定是 **合并** 的（不是替换）。在 `scope: "shared"` 下，按代理的绑定被忽略。

`agents.defaults.sandbox.browser.binds` 仅将额外的主机目录挂载到 **沙箱浏览器** 容器中。

- 当设置时（包括 `[]`），它替换浏览器容器的 `agents.defaults.sandbox.docker.binds`。
- 当省略时，浏览器容器回退到 `agents.defaults.sandbox.docker.binds`（向后兼容）。

示例（只读源 + 额外数据目录）：

```json5
{
  agents: {
    defaults: {
      sandbox: {
        docker: {
          binds: ["/home/user/source:/source:ro", "/var/data/myapp:/data:ro"],
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

- 绑定绕过沙箱文件系统：它们以您设置的任何模式暴露主机路径 (`:ro` 或 `:rw`)。
- OpenClaw 阻止危险的绑定源（例如：`docker.sock`, `/etc`, `/proc`, `/sys`, `/dev`，以及会暴露它们的父级挂载）。
- 敏感挂载（密钥、SSH 密钥、服务凭证）应为 `:ro`，除非绝对必要。
- 如果只需要对工作区的只读访问，请结合 `workspaceAccess: "ro"`；绑定模式保持独立。
- 参见 [沙箱与工具策略及提升模式](/gateway/sandbox-vs-tool-policy-vs-elevated) 了解绑定如何与工具策略和提升执行交互。

## 镜像 + 设置

默认镜像：`openclaw-sandbox:bookworm-slim`

构建一次：

```bash
scripts/sandbox-setup.sh
```

注意：默认镜像 **不** 包含 Node。如果技能需要 Node（或其他运行时），请烘焙自定义镜像或通过 `sandbox.docker.setupCommand` 安装（需要网络出口 + 可写根目录 + root 用户）。

如果您想要一个具有常用工具（例如 `curl`, `jq`, `nodejs`, `python3`, `git`）的功能更强大的沙箱镜像，请构建：

```bash
scripts/sandbox-common-setup.sh
```

然后将 `agents.defaults.sandbox.docker.image` 设置为 `openclaw-sandbox-common:bookworm-slim`。

沙箱浏览器镜像：

```bash
scripts/sandbox-browser-setup.sh
```

默认情况下，沙箱容器以 **无网络** 运行。使用 `agents.defaults.sandbox.docker.network` 覆盖。

捆绑的沙箱浏览器镜像也为容器化工作负载应用了保守的 Chromium 启动默认值。当前容器默认值包括：

- `--remote-debugging-address=127.0.0.1`
- `--remote-debugging-port=<derived from OPENCLAW_BROWSER_CDP_PORT>`
- `--user-data-dir=${HOME}/.chrome`
- `--no-first-run`
- `--no-default-browser-check`
- `--disable-3d-apis`
- `--disable-gpu`
- `--disable-dev-shm-usage`
- `--disable-background-networking`
- `--disable-extensions`
- `--disable-features=TranslateUI`
- `--disable-breakpad`
- `--disable-crash-reporter`
- `--disable-software-rasterizer`
- `--no-zygote`
- `--metrics-recording-only`
- `--renderer-process-limit=2`
- `--no-sandbox` 和 `--disable-setuid-sandbox` 当 `noSandbox` 启用时。
- 三个图形加固标志 (`--disable-3d-apis`,
  `--disable-software-rasterizer`, `--disable-gpu`) 是可选的，当容器缺乏 GPU 支持时很有用。如果您的工作负载需要 WebGL 或其他 3D/浏览器功能，请设置 `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0`。
- `--disable-extensions` 默认启用，可以通过 `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` 禁用以支持依赖扩展的流程。
- `--renderer-process-limit=2` 由 `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>` 控制，其中 `0` 保留 Chromium 的默认值。

如果您需要不同的运行时配置文件，请使用自定义浏览器镜像并提供自己的入口点。对于本地（非容器）Chromium 配置文件，使用 `browser.extraArgs` 附加额外的启动标志。

安全默认值：

- `network: "host"` 被阻止。
- `network: "container:<id>"` 默认被阻止（命名空间加入绕过风险）。
- 紧急覆盖：`agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true`。

Docker 安装和容器化网关位于此处：
[Docker](/install/docker)

对于 Docker 网关部署，`docker-setup.sh` 可以引导沙箱配置。
设置 `OPENCLAW_SANDBOX=1`（或 `true`/`yes`/`on`）以启用该路径。您可以
使用 `OPENCLAW_DOCKER_SOCKET` 覆盖套接字位置。完整设置和环境参考：[Docker](/install/docker#enable-agent-sandbox-for-docker-gateway-opt-in)。

## setupCommand（一次性容器设置）

`setupCommand` 在沙箱容器创建后运行 **一次**（不是在每次运行时）。
它通过 `sh -lc` 在容器内部执行。

路径：

- 全局：`agents.defaults.sandbox.docker.setupCommand`
- 按代理：`agents.list[].sandbox.docker.setupCommand`

常见陷阱：

- 默认 `docker.network` 为 `"none"`（无出口），因此包安装将失败。
- `docker.network: "container:<id>"` 需要 `dangerouslyAllowContainerNamespaceJoin: true`，且仅限紧急使用。
- `readOnlyRoot: true` 防止写入；设置 `readOnlyRoot: false` 或烘焙自定义镜像。
- `user` 必须为 root 才能安装包（省略 `user` 或设置 `user: "0:0"`）。
- 沙箱执行 **不** 继承主机 `process.env`。使用
  `agents.defaults.sandbox.docker.env`（或自定义镜像）处理技能 API 密钥。

## 工具策略 + 逃生舱口

工具允许/拒绝策略在沙箱规则之前仍然适用。如果工具在全局或按代理级别被拒绝，沙箱不会将其恢复。

`tools.elevated` 是一个明确的逃生舱口，它在主机上运行 `exec`。
`/exec` 指令仅适用于授权发送者并按会话持久化；要硬禁用
`exec`，请使用工具策略拒绝（参见 [沙箱与工具策略及提升模式](/gateway/sandbox-vs-tool-policy-vs-elevated)）。

调试：

- 使用 `openclaw sandbox explain` 检查有效的沙箱模式、工具策略和修复配置键。
- 参见 [沙箱与工具策略及提升模式](/gateway/sandbox-vs-tool-policy-vs-elevated) 了解“为什么被阻止？”的思维模型。
  保持锁定状态。

## 多代理覆盖

每个代理都可以覆盖沙箱 + 工具：
`agents.list[].sandbox` 和 `agents.list[].tools`（加上用于沙箱工具政策的 `agents.list[].tools.sandbox.tools`）。
有关优先级，请参见 [多代理沙箱与工具](/tools/multi-agent-sandbox-tools)。

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
- [多智能体沙箱与工具](/tools/multi-agent-sandbox-tools)
- [安全](/gateway/security)