---
summary: "How OpenClaw sandboxing works: modes, scopes, workspace access, and images"
title: Sandboxing
read_when: "You want a dedicated explanation of sandboxing or need to tune agents.defaults.sandbox."
status: active
---
# 沙箱机制

OpenClaw 可以在 Docker 容器内运行**工具**，以缩小潜在影响范围。  
此功能为**可选**，由配置项（`agents.defaults.sandbox` 或 `agents.list[].sandbox`）控制。若禁用沙箱，则工具直接在宿主机上运行。  
网关（Gateway）始终运行在宿主机上；启用沙箱后，工具执行将在隔离的沙箱环境中进行。

这并非完美的安全边界，但在模型做出不当操作时，能实质性地限制对文件系统和进程的访问。

## 被沙箱化的组件

- 工具执行（`exec`、`read`、`write`、`edit`、`apply_patch`、`process` 等）。
- 可选的沙箱化浏览器（`agents.defaults.sandbox.browser`）：
  - 默认情况下，当浏览器工具需要时，沙箱浏览器会自动启动（确保 CDP 可达）。可通过 `agents.defaults.sandbox.browser.autoStart` 和 `agents.defaults.sandbox.browser.autoStartTimeoutMs` 进行配置。
  - 默认情况下，沙箱浏览器容器使用专用 Docker 网络（`openclaw-sandbox-browser`），而非全局 `bridge` 网络。可通过 `agents.defaults.sandbox.browser.network` 配置。
  - 可选的 `agents.defaults.sandbox.browser.cdpSourceRange` 通过 CIDR 白名单限制容器边缘 CDP 的入站访问（例如 `172.21.0.1/32`）。
  - noVNC 观察者访问默认受密码保护；OpenClaw 生成一个短期有效的令牌 URL，该 URL 提供本地引导页面，并在 URL 片段（而非查询参数或请求头日志）中嵌入 noVNC 密码。
  - `agents.defaults.sandbox.browser.allowHostControl` 允许沙箱化会话显式地指向宿主机上的浏览器。
  - 可选白名单用于管控 `target: "custom"`：`allowedControlUrls`、`allowedControlHosts`、`allowedControlPorts`。

**未被沙箱化的组件**：

- 网关（Gateway）进程本身。
- 显式允许在宿主机上运行的任意工具（例如 `tools.elevated`）：
  - **提升权限的 exec 在宿主机上运行，并绕过沙箱机制。**
  - 若沙箱已关闭，`tools.elevated` 不会改变执行方式（本就已在宿主机上运行）。参见 [提升权限模式](/tools/elevated)。

## 模式

`agents.defaults.sandbox.mode` 控制沙箱机制**何时启用**：

- `"off"`：不启用沙箱。
- `"non-main"`：仅对**非主会话**启用沙箱（若希望常规聊天在宿主机上运行，则为默认选项）。
- `"all"`：所有会话均在沙箱中运行。  
  注意：`"non-main"` 基于 `session.mainKey`（默认为 `"main"`），而非代理 ID。  
  群组/频道会话使用其自身的密钥，因此被视为非主会话，将被沙箱化。

## 作用域

`agents.defaults.sandbox.scope` 控制**创建容器的数量**：

- `"session"`（默认）：每个会话对应一个容器。
- `"agent"`：每个代理对应一个容器。
- `"shared"`：所有沙箱化会话共享一个容器。

## 工作区访问

`agents.defaults.sandbox.workspaceAccess` 控制**沙箱可访问的内容**：

- `"none"`（默认）：工具可访问位于 `~/.openclaw/sandboxes` 下的沙箱工作区。
- `"ro"`：以只读方式挂载代理工作区至 `/agent`（禁用 `write` / `edit` / `apply_patch`）。
- `"rw"`：以读写方式挂载代理工作区至 `/workspace`。

传入的媒体文件将被复制到当前活跃的沙箱工作区（`media/inbound/*`）。  
技能说明：`read` 工具以沙箱根目录为基准。配合 `workspaceAccess: "none"`，OpenClaw 将符合条件的技能镜像至沙箱工作区（`.../skills`），以便读取。配合 `"rw"`，工作区中的技能可从 `/workspace/skills` 读取。

## 自定义绑定挂载（Custom bind mounts）

`agents.defaults.sandbox.docker.binds` 将额外的宿主机目录挂载进容器。  
格式为：`host:container:mode`（例如 `"/home/user/source:/source:rw"`）。

全局与按代理设置的挂载项将被**合并**（而非覆盖）。在 `scope: "shared"` 下，按代理设置的挂载项将被忽略。

`agents.defaults.sandbox.browser.binds` 仅将额外的宿主机目录挂载进**沙箱浏览器容器**。

- 当设置该值（包括 `[]`）时，它将替代浏览器容器中的 `agents.defaults.sandbox.docker.binds`。
- 若未设置，浏览器容器将回退至 `agents.defaults.sandbox.docker.binds`（向后兼容）。

示例（只读源目录 + 额外数据目录）：

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

- 绑定挂载会绕过沙箱文件系统：它们以您设定的权限模式（`:ro` 或 `:rw`）暴露宿主机路径。
- OpenClaw 会阻止危险的绑定挂载源（例如：`docker.sock`、`/etc`、`/proc`、`/sys`、`/dev`，以及可能暴露上述路径的父级挂载点）。
- 敏感挂载（如密钥、SSH 密钥、服务凭据）应**避免使用**（`:ro`），除非绝对必要。
- 若仅需对工作区的只读访问，可结合使用 `workspaceAccess: "ro"`；绑定挂载的权限模式保持独立。
- 关于挂载如何与工具策略及提升权限执行交互，请参阅 [沙箱 vs 工具策略 vs 提升权限](/gateway/sandbox-vs-tool-policy-vs-elevated)。

## 镜像与初始化设置

默认镜像：`openclaw-sandbox:bookworm-slim`

构建一次即可：

```bash
scripts/sandbox-setup.sh
```

注意：默认镜像**不包含 Node.js**。若某技能需要 Node.js（或其他运行时），请自行构建定制镜像，或通过 `sandbox.docker.setupCommand` 安装（需具备网络出口权限 + 可写根目录 + root 用户权限）。

若您希望获得功能更完备的沙箱镜像（含常用工具，例如 `curl`、`jq`、`nodejs`、`python3`、`git`），请构建：

```bash
scripts/sandbox-common-setup.sh
```

然后将 `agents.defaults.sandbox.docker.image` 设置为  
`openclaw-sandbox-common:bookworm-slim`。

沙箱浏览器镜像：

```bash
scripts/sandbox-browser-setup.sh
```

默认情况下，沙箱容器**无网络连接**。  
可通过 `agents.defaults.sandbox.docker.network` 覆盖该设置。

捆绑的沙箱浏览器镜像还为容器化工作负载应用了保守的 Chromium 启动默认值。当前容器默认值包括：

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
- 启用 `noSandbox` 时，启用 `--no-sandbox` 和 `--disable-setuid-sandbox`。
- 三项图形安全加固标志（`--disable-3d-apis`、`--disable-software-rasterizer`、`--disable-gpu`）为可选，适用于容器缺乏 GPU 支持的场景。若您的工作负载需要 WebGL 或其他 3D/浏览器特性，请设置 `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0`。
- `--disable-extensions` 默认启用，可通过 `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` 禁用，以支持依赖扩展的流程。
- `--renderer-process-limit=2` 由 `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>` 控制，其中 `0` 保留 Chromium 默认行为。

若您需要不同的运行时配置文件，请使用自定义浏览器镜像并提供自己的入口点（entrypoint）。对于本地（非容器化）Chromium 配置文件，请使用 `browser.extraArgs` 追加额外的启动参数。

安全默认设置：

- `network: "host"` 被阻止。
- `network: "container:<id>"` 默认被阻止（存在命名空间加入绕过风险）。
- 应急覆盖：`agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true`。

Docker 安装包及容器化网关部署位置：  
[Docker](/install/docker)

对于 Docker 网关部署，`docker-setup.sh` 可用于引导沙箱配置。  
设置 `OPENCLAW_SANDBOX=1`（或 `true` / `yes` / `on`）以启用该路径。您可通过 `OPENCLAW_DOCKER_SOCKET` 覆盖套接字位置。完整设置与环境变量参考：[Docker](/install/docker#enable-agent-sandbox-for-docker-gateway-opt-in)。

## setupCommand（一次性容器初始化命令）

`setupCommand` 在沙箱容器创建后**仅执行一次**（而非每次运行都执行）。  
它通过 `sh -lc` 在容器内部执行。

路径：

- 全局：`agents.defaults.sandbox.docker.setupCommand`
- 按代理：`agents.list[].sandbox.docker.setupCommand`

常见陷阱：

- 默认 `docker.network` 为 `"none"`（无网络出口），因此软件包安装将失败。
- `docker.network: "container:<id>"` 需要 `dangerouslyAllowContainerNamespaceJoin: true`，且仅为应急用途。
- `readOnlyRoot: true` 阻止写入；请设置 `readOnlyRoot: false` 或构建定制镜像。
- `user` 执行软件包安装时必须为 root 用户（省略 `user` 或设置 `user: "0:0"`）。
- 沙箱 exec **不会继承**宿主机的 `process.env`。请使用 `agents.defaults.sandbox.docker.env`（或定制镜像）管理技能 API 密钥。

## 工具策略与逃逸通道

在沙箱规则生效前，工具的允许/拒绝策略仍会首先应用。若某工具被全局或按代理拒绝，则沙箱机制无法使其恢复可用。

`tools.elevated` 是一个显式的逃逸通道，用于在宿主机上运行 `exec`。  
`/exec` 指令仅对已授权发送者生效，且按会话持久化；若需彻底禁用 `exec`，请使用工具策略拒绝（参见 [沙箱 vs 工具策略 vs 提升权限](/gateway/sandbox-vs-tool-policy-vs-elevated)）。

调试：

- 使用 `openclaw sandbox explain` 检查实际生效的沙箱模式、工具策略及修复配置键。
- 参见 [沙箱 vs 工具策略 vs 提升权限](/gateway/sandbox-vs-tool-policy-vs-elevated) 了解“为何被阻止？”的思维模型。  
  请始终保持严格的安全控制。

## 多代理覆盖配置

每个代理均可覆盖沙箱及工具配置：  
`agents.list[].sandbox` 和 `agents.list[].tools`（另含针对沙箱工具策略的 `agents.list[].tools.sandbox.tools`）。  
参见 [多代理沙箱与工具](/tools/multi-agent-sandbox-tools) 了解优先级规则。

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
- [安全性](/gateway/security)