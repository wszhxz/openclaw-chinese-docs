---
summary: "Security considerations and threat model for running an AI gateway with shell access"
read_when:
  - Adding features that widen access or automation
title: "Security"
---
# 安全性 🔒

> [!WARNING]
> **个人助理信任模型：** 本指南假设每个网关对应一个受信任的操作员边界（单用户/个人助理模型）。
> OpenClaw **并非** 为多个对抗性用户共享同一代理/网关而设计的恶意多租户安全边界。
> 如果您需要混合信任级别或对抗性用户的运行环境，请拆分信任边界（独立网关 + 凭据，理想情况下使用独立的操作系统用户/主机）。

## 首先明确范围：个人助理安全模型

OpenClaw 的安全指南基于 **个人助理** 部署模型：一个受信任的操作员边界，可能包含多个代理。

- 支持的安全态势：每个网关对应一个用户/信任边界（建议每个边界使用一个操作系统用户/主机/VPS）。
- 不支持的安全边界：由相互不信任或存在对抗关系的多个用户共享一个网关/代理。
- 若需实现对抗性用户隔离，请按信任边界进行拆分（独立网关 + 凭据，且理想情况下使用独立的操作系统用户/主机）。
- 若多个不受信任的用户均可向某个启用工具的代理发送消息，则应视其共享该代理所授予的相同工具权限。

本页说明如何在 **该模型内** 进行加固。它并不声称可在单一共享网关上实现对抗性多租户隔离。

## 快速检查：`openclaw security audit`

另请参阅：[形式化验证（安全模型）](/security/formal-verification/)

请定期运行此检查（尤其在更改配置或暴露网络面后）：

```bash
openclaw security audit
openclaw security audit --deep
openclaw security audit --fix
openclaw security audit --json
```

它会标记常见隐患（网关身份验证暴露、浏览器控制暴露、提升的白名单、文件系统权限）。

OpenClaw 既是一款产品，也是一项实验：您正在将前沿模型行为接入真实的通信界面与真实工具中。**不存在“绝对安全”的配置。** 目标是审慎决策以下事项：

- 谁可以与您的机器人通信
- 机器人被允许在哪些位置执行操作
- 机器人可访问哪些资源

请从最小可行权限起步，再随着信心增强逐步扩大权限范围。

## 部署前提（重要）

OpenClaw 假设主机与配置边界是受信任的：

- 若某人可修改网关主机状态/配置（`~/.openclaw`，包括 `openclaw.json`），则应将其视为受信任的操作员。
- 为多个相互不信任/对抗的操作员共用一个网关的部署方式 **不被推荐**。
- 对于混合信任团队，请通过独立网关（或至少独立操作系统用户/主机）拆分信任边界。
- OpenClaw 可在同一台机器上运行多个网关实例，但推荐做法更倾向于清晰划分信任边界。
- 推荐默认配置：每台机器/主机（或 VPS）对应一位用户，每位用户对应一个网关，该网关中可运行一个或多个代理。
- 若多位用户需要使用 OpenClaw，请为每位用户分配独立的 VPS/主机。

### 实际影响（操作员信任边界）

在一个网关实例内部，经身份验证的操作员访问属于受信任的控制平面角色，而非按用户划分的租户角色。

- 拥有读取/控制平面访问权限的操作员可按设计查看网关会话元数据/历史记录。
- 会话标识符（`sessionKey`、会话 ID、标签）是路由选择器，而非授权令牌。
- 示例：期望对 `sessions.list`、`sessions.preview` 或 `chat.history` 等方法实现每位操作员的隔离，超出了本模型范畴。
- 若需对抗性用户隔离，请为每个信任边界运行独立网关。
- 单台机器上运行多个网关在技术上可行，但并非多用户隔离的推荐基准方案。

## 个人助理模型（非多租户总线）

OpenClaw 设计为个人助理安全模型：一个受信任的操作员边界，可能包含多个代理。

- 若多人可向某个启用工具的代理发送消息，则每位用户均可驱动该相同的权限集。
- 按用户划分的会话/内存隔离有助于保护隐私，但无法将共享代理转换为按用户划分的主机授权。
- 若用户之间可能存在对抗关系，请为每个信任边界运行独立网关（或独立操作系统用户/主机）。

### 共享 Slack 工作区：真实风险

若“Slack 中的所有人均可向机器人发送消息”，核心风险在于委托的工具权限：

- 任何获准的发送者均可在代理策略范围内触发工具调用（`exec`、浏览器、网络/文件工具）；
- 来自某位发送者的提示词/内容注入可能导致影响共享状态、设备或输出的操作；
- 若某共享代理持有敏感凭据/文件，则任何获准的发送者均可能通过工具使用驱动数据泄露。

请为团队工作流使用具备最少工具集的独立代理/网关；将处理个人数据的代理保持私有。

### 公司共享代理：可接受模式

当所有使用该代理的人员均处于同一信任边界内（例如同一公司团队），且该代理严格限定于业务用途时，此模式可接受。

- 在专用机器/虚拟机/容器中运行；
- 为该运行时使用专用操作系统用户 + 专用浏览器/配置文件/账号；
- 切勿让该运行时登录个人 Apple/Google 账号或个人密码管理器/浏览器配置文件。

若您在同一运行时中混用个人与公司身份，则会破坏隔离性，并增加个人数据暴露风险。

## 网关与节点信任概念

请将网关与节点视为一个操作员信任域，但角色不同：

- **网关** 是控制平面与策略界面（`gateway.auth`、工具策略、路由）。
- **节点** 是与该网关配对的远程执行界面（命令、设备操作、主机本地能力）。
- 经网关身份验证的调用方在网关范围内被视为受信任；配对后，节点上的操作即为该节点上受信任操作员的操作。
- `sessionKey` 是用于上下文/会话选择的路由机制，而非按用户授权。
- 执行批准（白名单 + 询问）是保障操作员意图的防护措施，而非对抗性多租户隔离。

若需实现对抗性用户隔离，请按操作系统用户/主机拆分信任边界，并运行独立网关。

## 信任边界矩阵

在评估风险时，请使用此快速模型：

| 边界或控制项                         | 含义                                     | 常见误解                                                                |
| ------------------------------------------- | ------------------------------------------------- | ----------------------------------------------------------------------------- |
| `gateway.auth`（令牌/密码/设备身份验证） | 对调用方进行网关 API 身份验证             | “需对每帧消息添加逐条签名才能确保安全”                    |
| `sessionKey`                                | 上下文/会话选择的路由密钥         | “会话密钥是用户身份验证边界”                                         |
| 提示词/内容防护措施                   | 降低模型滥用风险                           | “仅提示词注入即证明身份验证被绕过”                                   |
| `canvas.eval` / 浏览器求值            | 启用时的有意操作员能力      | “任何 JS 求值原语在此信任模型中自动构成漏洞”           |
| 本地 TUI `!` shell                         | 显式由操作员触发的本地执行       | “本地 shell 便捷命令即远程注入”                         |
| 节点配对与节点命令              | 在已配对设备上执行的操作员级远程执行 | “远程设备控制默认应视为不受信任用户访问” |

## 设计上非漏洞项

以下模式常被报告，通常在未展示真实边界绕过的情况下被标记为“无需处理”：

- 仅含提示词注入的链路，且无策略/身份验证/沙箱绕过。
- 假设在单一共享主机/配置上进行对抗性多租户操作的主张。
- 将共享网关设置中正常的操作员读取路径访问（例如 `sessions.list`/`sessions.preview`/`chat.history`）归类为 IDOR 的主张。
- 仅限 localhost 的部署发现（例如仅在回环地址网关上启用 HSTS）。
- 针对本仓库中并不存在的入站路径（如 Discord 入站 Webhook 签名）的发现。
- 将 `sessionKey` 视为身份验证令牌的“缺少按用户授权”发现。

## 研究人员预检清单

在提交 GHSA 前，请确认以下全部条件：

1. 复现问题在最新 `main` 或最新发布版本中仍有效。
2. 报告包含确切代码路径（`file`、函数、行号范围）及测试版本/提交哈希。
3. 影响跨越已记录的信任边界（而不仅限于提示词注入）。
4. 主张未列于 [范围之外](https://github.com/openclaw/openclaw/blob/main/SECURITY.md#out-of-scope)。
5. 已核查现有公告是否存在重复（适用时复用标准 GHSA）。
6. 部署前提已明确说明（回环/本地 vs 已暴露，受信任 vs 不受信任操作员）。

## 60 秒加固基线

请首先采用此基线，再根据受信任代理的选择性重新启用工具：

```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    auth: { mode: "token", token: "replace-with-long-random-token" },
  },
  session: {
    dmScope: "per-channel-peer",
  },
  tools: {
    profile: "messaging",
    deny: ["group:automation", "group:runtime", "group:fs", "sessions_spawn", "sessions_send"],
    fs: { workspaceOnly: true },
    exec: { security: "deny", ask: "always" },
    elevated: { enabled: false },
  },
  channels: {
    whatsapp: { dmPolicy: "pairing", groups: { "*": { requireMention: true } } },
  },
}
```

此配置使网关仅限本地访问、隔离私信，并默认禁用控制平面/运行时工具。

## 共享收件箱快速规则

若超过一人可向您的机器人发送私信：

- 设置 `session.dmScope: "per-channel-peer"`（或多账户频道使用 `"per-account-channel-peer"`）。
- 保持 `dmPolicy: "pairing"` 或严格的白名单。
- 切勿将共享私信与广泛的工具访问权限结合使用。
- 此方案可强化协作型/共享收件箱，但并非针对用户共享主机/配置写入权限场景设计的对抗性共租户隔离方案。

### 审计检查内容（高层概述）

- **入站访问**（DM 策略、组策略、白名单）：陌生人能否触发机器人？
- **工具影响范围**（提权工具 + 公开房间）：提示词注入是否可能演变为 shell/文件/网络操作？
- **网络暴露面**（网关绑定/认证、Tailscale Serve/Funnel、弱效/过短的认证令牌）。
- **浏览器控制暴露面**（远程节点、中继端口、远程 CDP 端点）。
- **本地磁盘卫生状况**（权限、符号链接、配置包含项、“同步文件夹”路径）。
- **插件**（扩展存在但未显式列入白名单）。
- **策略漂移/配置错误**（沙箱 Docker 设置已配置但沙箱模式关闭；无效的 `gateway.nodes.denyCommands` 模式，因其仅精确匹配命令名称（例如 `system.run`），不检查 shell 文本；危险的 `gateway.nodes.allowCommands` 条目；全局 `tools.profile="minimal"` 被各代理配置文件覆盖；在宽松工具策略下可调用扩展插件工具）。
- **运行时预期漂移**（例如 `tools.exec.host="sandbox"`，而沙箱模式处于关闭状态，此时该操作将直接在网关主机上运行）。
- **模型卫生状况**（当配置的模型呈现老旧特征时发出警告；非强制性阻断）。

若运行 `--deep`，OpenClaw 还将尝试尽最大努力执行一次实时网关探测。

## 凭据存储映射表

审计访问权限或决定备份内容时，请参考此表：

- **WhatsApp**：`~/.openclaw/credentials/whatsapp/<accountId>/creds.json`
- **Telegram 机器人令牌**：配置/环境变量 或 `channels.telegram.tokenFile`
- **Discord 机器人令牌**：配置/环境变量 或 SecretRef（支持 env/file/exec 提供器）
- **Slack 令牌**：配置/环境变量（`channels.slack.*`）
- **配对白名单**：
  - `~/.openclaw/credentials/<channel>-allowFrom.json`（默认账户）
  - `~/.openclaw/credentials/<channel>-<accountId>-allowFrom.json`（非默认账户）
- **模型认证配置集**：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- **基于文件的密钥载荷（可选）**：`~/.openclaw/secrets.json`
- **遗留 OAuth 导入**：`~/.openclaw/credentials/oauth.json`

## 安全审计检查清单

当审计输出结果时，请按以下优先级顺序处理：

1. **任何“开放”状态 + 工具启用**：首先收紧 DM/群组策略（配对/白名单），再强化工具策略与沙箱机制。
2. **公网网络暴露**（局域网绑定、Funnel 开启、缺失认证）：须立即修复。
3. **浏览器控制远程暴露**：视同运维人员访问权限处理（仅限 Tailnet 内部、有意识地配对节点、避免公网暴露）。
4. **权限设置**：确保状态/配置/凭据/认证文件不具有组/全局可读权限。
5. **插件/扩展**：仅加载您明确信任的组件。
6. **模型选择**：对于任何启用工具的机器人，优先选用现代、具备指令加固能力的模型。

## 安全审计术语表

在实际部署中您极有可能遇到的高价值 `checkId` 取值（非穷举）：

| `checkId`                                          | 严重程度      | 为何重要                                                                                       | 主要修复项的键/路径                                                                              | 是否支持自动修复 |
| -------------------------------------------------- | ------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | -------- |
| `fs.state_dir.perms_world_writable`                | 致命          | 其他用户/进程可修改完整的 OpenClaw 状态                                                     | `~/.openclaw` 的文件系统权限                                                                 | 是       |
| `fs.config.perms_writable`                         | 致命          | 其他人可更改认证/工具策略/配置                                                                | `~/.openclaw/openclaw.json` 的文件系统权限                                                                | 是       |
| `fs.config.perms_world_readable`                   | 致命          | 配置可能泄露令牌/设置                                                                         | 配置文件的文件系统权限                                                                          | 是       |
| `gateway.bind_no_auth`                             | 致命          | 无共享密钥的远程绑定                                                                          | `gateway.bind`、`gateway.auth.*`                                                              | 否       |
| `gateway.loopback_no_auth`                         | 致命          | 反向代理的回环请求可能变为未经身份验证                                                        | `gateway.auth.*`、代理配置                                                                     | 否       |
| `gateway.http.no_auth`                             | 警告/致命     | 网关 HTTP API 在启用 `auth.mode="none"` 时可被访问                                            | `gateway.auth.mode`、`gateway.http.endpoints.*`                                                            | 否       |
| `gateway.tools_invoke_http.dangerous_allow`        | 警告/致命     | 通过 HTTP API 重新启用了危险工具                                                             | `gateway.tools.allow`                                                                               | 否       |
| `gateway.nodes.allow_commands_dangerous`           | 警告/致命     | 启用了高影响节点命令（摄像头/屏幕/联系人/日历/SMS）                                           | `gateway.nodes.allowCommands`                                                                               | 否       |
| `gateway.tailscale_funnel`                         | 致命          | 暴露于公共互联网                                                                              | `gateway.tailscale.mode`                                                                               | 否       |
| `gateway.control_ui.allowed_origins_required`      | 致命          | 非回环地址的控制 UI 未显式配置浏览器来源白名单                                               | `gateway.controlUi.allowedOrigins`                                                                               | 否       |
| `gateway.control_ui.host_header_origin_fallback`   | 警告/致命     | 启用了 Host-header 来源回退机制（DNS 重绑定防护降级）                                        | `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback`                                                                               | 否       |
| `gateway.control_ui.insecure_auth`                 | 警告          | 启用了不安全认证兼容性开关                                                                    | `gateway.controlUi.allowInsecureAuth`                                                                               | 否       |
| `gateway.control_ui.device_auth_disabled`          | 致命          | 禁用了设备身份校验                                                                            | `gateway.controlUi.dangerouslyDisableDeviceAuth`                                                                               | 否       |
| `gateway.real_ip_fallback_enabled`                 | 警告/致命     | 信任 `X-Real-IP` 回退机制可能因代理配置错误导致源 IP 伪造                              | `gateway.allowRealIpFallback`、`gateway.trustedProxies`                                                            | 否       |
| `discovery.mdns_full_mode`                         | 警告/致命     | mDNS 全模式会在本地网络中广播 `cliPath`/`sshPort` 元数据                    | `discovery.mdns.mode`、`gateway.bind`                                                            | 否       |
| `config.insecure_or_dangerous_flags`               | 警告          | 启用了任意不安全/危险的调试标志                                                               | 多个键（参见具体发现详情）                                                                      | 否       |
| `hooks.token_too_short`                            | 警告          | 钩子入口处更易遭受暴力破解攻击                                                                | `hooks.token`                                                                               | 否       |
| `hooks.request_session_key_enabled`                | 警告/致命     | 外部调用方可指定 sessionKey                                                                   | `hooks.allowRequestSessionKey`                                                                               | 否       |
| `hooks.request_session_key_prefixes_missing`       | 警告/致命     | 对外部 session key 的格式未加限制                                                            | `hooks.allowedSessionKeyPrefixes`                                                                               | 否       |
| `logging.redact_off`                               | 警告          | 敏感值泄露至日志/状态信息中                                                                   | `logging.redactSensitive`                                                                               | 是       |
| `sandbox.docker_config_mode_off`                   | 警告          | 存在沙箱 Docker 配置但未启用                                                                  | `agents.*.sandbox.mode`                                                                               | 否       |
| `sandbox.dangerous_network_mode`                   | 致命          | 沙箱 Docker 网络使用了 `host` 或 `container:*` 命名空间连接模式              | `agents.*.sandbox.docker.network`                                                                               | 否       |
| `tools.exec.host_sandbox_no_sandbox_defaults`      | 警告          | 当沙箱关闭时，`exec host=sandbox` 解析为主机执行                                              | `tools.exec.host`、`agents.defaults.sandbox.mode`                                                            | 否       |
| `tools.exec.host_sandbox_no_sandbox_agents`        | 警告          | 当沙箱关闭时，每个 Agent 的 `exec host=sandbox` 解析为主机执行                                | `agents.list[].tools.exec.host`、`agents.list[].sandbox.mode`                                                            | 否       |
| `tools.exec.safe_bins_interpreter_unprofiled`      | 警告          | `safeBins` 中的解释器/运行时二进制文件未配置显式配置文件，扩大了执行风险             | `tools.exec.safeBins`、`tools.exec.safeBinProfiles`、`agents.list[].tools.exec.*`                                       | 否       |
| `skills.workspace.symlink_escape`                  | 警告          | 工作区 `skills/**/SKILL.md` 解析超出工作区根目录（符号链接链偏移）                             | 工作区 `skills/**` 的文件系统状态                                                        | 否       |
| `security.exposure.open_groups_with_elevated`      | 致命          | 开放群组 + 提权工具构成高影响提示注入路径                                                    | `channels.*.groupPolicy`、`tools.elevated.*`                                                            | 否       |
| `security.exposure.open_groups_with_runtime_or_fs` | 致命/警告 | 开放群组可在无沙箱/工作区防护的情况下访问命令/文件工具                                      | `channels.*.groupPolicy`、`tools.profile/deny`、`tools.fs.workspaceOnly`、`agents.*.sandbox.mode`                    | 否       |
| `security.trust_model.multi_user_heuristic`        | 警告          | 配置看似面向多用户，而网关信任模型实为个人助理                                             | 分割信任边界，或采用共享用户强化措施（`sandbox.mode`、工具拒绝/工作区范围限定）            | 否       |
| `tools.profile_minimal_overridden`                 | 警告          | Agent 覆盖项绕过了全局最小化配置文件                                                        | `agents.list[].tools.profile`                                                                               | 否       |
| `plugins.tools_reachable_permissive_policy`        | 警告          | 扩展工具在宽松上下文中可被访问                                                              | `tools.profile` + 工具允许/拒绝列表                                                          | 否       |
| `models.small_params`                              | 致命/信息     | 小型模型 + 不安全工具接口提升了注入风险                                                     | 模型选择 + 沙箱/工具策略                                                                        | 否       |

## 通过 HTTP 访问控制 UI

控制 UI 需要一个**安全上下文**（HTTPS 或 localhost）来生成设备身份。  
`gateway.controlUi.allowInsecureAuth` **不会**绕过安全上下文、设备身份或设备配对检查。  
建议优先使用 HTTPS（Tailscale Serve）或在 `127.0.0.1` 上打开 UI。

仅限紧急故障排除场景，`gateway.controlUi.dangerouslyDisableDeviceAuth` 会完全禁用设备身份检查。这是一种严重的安全降级；除非您正在主动调试且能快速恢复，否则请保持该选项关闭。

当启用此设置时，`openclaw security audit` 将发出警告。

## 不安全或危险标志汇总

`openclaw security audit` 在已知的不安全/危险调试开关启用时包含 `config.insecure_or_dangerous_flags`。  
当前该检查聚合了以下内容：

- `gateway.controlUi.allowInsecureAuth=true`  
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true`  
- `gateway.controlUi.dangerouslyDisableDeviceAuth=true`  
- `hooks.gmail.allowUnsafeExternalContent=true`  
- `hooks.mappings[<index>].allowUnsafeExternalContent=true`  
- `tools.exec.applyPatch.workspaceOnly=false`  

完整填写 OpenClaw 配置架构中定义的 `dangerous*` / `dangerously*` 配置项：

- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback`  
- `gateway.controlUi.dangerouslyDisableDeviceAuth`  
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`  
- `channels.discord.dangerouslyAllowNameMatching`  
- `channels.discord.accounts.<accountId>.dangerouslyAllowNameMatching`  
- `channels.slack.dangerouslyAllowNameMatching`  
- `channels.slack.accounts.<accountId>.dangerouslyAllowNameMatching`  
- `channels.googlechat.dangerouslyAllowNameMatching`  
- `channels.googlechat.accounts.<accountId>.dangerouslyAllowNameMatching`  
- `channels.msteams.dangerouslyAllowNameMatching`  
- `channels.irc.dangerouslyAllowNameMatching`（扩展通道）  
- `channels.irc.accounts.<accountId>.dangerouslyAllowNameMatching`（扩展通道）  
- `channels.mattermost.dangerouslyAllowNameMatching`（扩展通道）  
- `channels.mattermost.accounts.<accountId>.dangerouslyAllowNameMatching`（扩展通道）  
- `agents.defaults.sandbox.docker.dangerouslyAllowReservedContainerTargets`  
- `agents.defaults.sandbox.docker.dangerouslyAllowExternalBindSources`  
- `agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin`  
- `agents.list[<index>].sandbox.docker.dangerouslyAllowReservedContainerTargets`  
- `agents.list[<index>].sandbox.docker.dangerouslyAllowExternalBindSources`  
- `agents.list[<index>].sandbox.docker.dangerouslyAllowContainerNamespaceJoin`  

## 反向代理配置

若将网关（Gateway）部署在反向代理（如 nginx、Caddy、Traefik 等）之后，应配置 `gateway.trustedProxies` 以实现正确的客户端 IP 识别。

当网关检测到来自 **未列入** `trustedProxies` 的地址的代理头时，将 **不** 将该连接视为本地客户端。若网关身份验证被禁用，则此类连接将被拒绝。此举可防止因代理连接被误判为来自 localhost 而自动获得信任，从而绕过身份验证。

```yaml
gateway:
  trustedProxies:
    - "127.0.0.1" # if your proxy runs on localhost
  # Optional. Default false.
  # Only enable if your proxy cannot provide X-Forwarded-For.
  allowRealIpFallback: false
  auth:
    mode: password
    password: ${OPENCLAW_GATEWAY_PASSWORD}
```

当配置了 `trustedProxies` 时，网关使用 `X-Forwarded-For` 来确定客户端 IP。默认情况下，`X-Real-IP` 被忽略，除非显式设置了 `gateway.allowRealIpFallback: true`。

良好的反向代理行为（覆写传入的转发头）：

```nginx
proxy_set_header X-Forwarded-For $remote_addr;
proxy_set_header X-Real-IP $remote_addr;
```

不良的反向代理行为（追加/保留不可信的转发头）：

```nginx
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

## HSTS 与源（origin）说明

- OpenClaw 网关默认优先面向本地/回环（loopback）场景。若在反向代理处终止 TLS，请在代理面向 HTTPS 的域名上设置 HSTS。  
- 若网关自身终止 HTTPS，可通过设置 `gateway.http.securityHeaders.strictTransportSecurity`，使 OpenClaw 响应中输出 HSTS 头。  
- 详细的部署指南参见 [可信代理身份验证](/gateway/trusted-proxy-auth#tls-termination-and-hsts)。  
- 对于非回环（non-loopback）的控制界面（Control UI）部署，默认要求配置 `gateway.controlUi.allowedOrigins`。  
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true` 启用 Host 头源（origin）回退模式；请将其视为一种危险的、由操作员自主选择的策略。  
- 请将 DNS 重绑定（DNS rebinding）和代理 Host 头行为视作部署加固问题；务必严格限制 `trustedProxies`，并避免将网关直接暴露于公共互联网。

## 本地会话日志存储于磁盘

OpenClaw 将会话转录内容（session transcripts）存储在磁盘路径 `~/.openclaw/agents/<agentId>/sessions/*.jsonl` 下。  
该机制是保障会话连续性以及（可选）会话记忆索引所必需的；但同时也意味着：  
**任何具有文件系统访问权限的进程或用户均可读取这些日志**。请将磁盘访问视为信任边界，并严格限制对 `~/.openclaw` 的权限（参见下方审计章节）。若需在智能体（agents）之间实现更强的隔离，请为其分别配置独立的操作系统用户或部署于独立主机。

## 节点执行（system.run）

若已配对 macOS 节点，网关可在该节点上调用 `system.run`。这属于针对 Mac 的 **远程代码执行**：

- 需要完成节点配对（需用户批准 + token）。  
- 在 Mac 上通过 **“设置 → 执行批准”** 进行管控（含安全策略、交互提示及白名单机制）。  
- 若不希望启用远程执行，请将安全策略设为 **拒绝（deny）**，并移除该 Mac 的节点配对。

## 动态技能（watcher / 远程节点）

OpenClaw 可在会话进行中动态刷新技能列表：

- **技能监视器（Skills watcher）**：对 `SKILL.md` 的修改可在下一轮智能体响应时更新当前技能快照。  
- **远程节点**：接入 macOS 节点后，可基于二进制探测（bin probing）使仅限 macOS 的技能变为可用。

请将技能目录（skill folders）视为 **可信代码**，并严格限制可修改其内容的人员权限。

## 威胁模型（Threat Model）

您的 AI 助理可以：

- 执行任意 shell 命令  
- 读取/写入文件  
- 访问网络服务  
- 向任何人发送消息（若您授予其 WhatsApp 接入权限）

向您发送消息的人员可以：

- 尝试诱骗您的 AI 执行恶意操作  
- 通过社交工程手段获取您数据的访问权限  
- 探测您的基础设施细节  

## 核心理念：先访问控制，后智能决策

此处大多数失败案例并非高阶漏洞利用——而是“有人给机器人发了一条消息，机器人照做了”。

OpenClaw 的立场如下：

- **身份优先（Identity first）**：首先决定谁可以与机器人对话（私信配对 / 白名单 / 显式“开放”）。  
- **范围其次（Scope next）**：再决定机器人被允许在哪些范围内执行操作（群组白名单 + 提及门控 / 工具权限 / 沙箱机制 / 设备权限）。  
- **模型最后（Model last）**：假定大语言模型可能被操控；设计系统时应确保此类操控的影响范围尽可能受限。

## 命令授权模型

斜杠命令（slash commands）与指令（directives）仅对 **已授权发送者** 生效。授权依据来源于频道白名单/配对机制，以及 `commands.useAccessGroups`（详见 [配置](/gateway/configuration) 和 [斜杠命令](/tools/slash-commands)）。若某频道白名单为空，或包含 `"*"`，则该频道的命令将实质上处于开放状态。

`/exec` 是仅为已授权操作员提供的、**仅限当前会话有效** 的便捷功能。它 **不会** 写入配置，也不会影响其他会话。

## 控制平面工具风险

以下两个内置工具可对控制平面做出持久性变更：

- `gateway` 可调用 `config.apply`、`config.patch` 和 `update.run`。  
- `cron` 可创建定时任务，使其在原始聊天/任务结束后仍持续运行。

对于处理不可信内容的任意智能体或界面（agent/surface），默认应禁止上述两项能力：

```json5
{
  tools: {
    deny: ["gateway", "cron", "sessions_spawn", "sessions_send"],
  },
}
```

`commands.restart=false` 仅阻止重启（restart）操作，**不会** 禁用 `gateway` 的配置/更新操作。

## 插件/扩展（Plugins/extensions）

插件与网关 **进程内运行**。请将其视为可信代码：

- 仅从您信任的来源安装插件。  
- 优先采用显式的 `plugins.allow` 白名单机制。  
- 启用前须审阅插件配置。  
- 插件变更后需重启网关。  
- 若您通过 npm（`openclaw plugins install <npm-spec>`）安装插件，请视其为运行不可信代码：
  - 安装路径为 `~/.openclaw/extensions/<pluginId>/`（或 `$OPENCLAW_STATE_DIR/extensions/<pluginId>/`）。  
  - OpenClaw 使用 `npm pack`，随后在该目录中运行 `npm install --omit=dev`（npm 生命周期脚本可在安装期间执行任意代码）。  
  - 推荐使用固定且精确的版本号（`@scope/pkg@1.2.3`），并在启用前检查磁盘上解压后的代码。

详情参见：[插件](/tools/plugin)

## 私信（DM）访问模型（配对 / 白名单 / 开放 / 禁用）

所有当前支持私信的频道均支持一种 DM 策略（`dmPolicy` 或 `*.dm.policy`），该策略在消息被处理 **之前** 即对入站私信实施管控：

- `pairing`（默认）：未知发送者将收到一个简短的配对码，机器人将在其请求获准前忽略其消息。配对码 1 小时后过期；重复发送私信不会重新发送配对码，除非创建新的请求。待处理请求默认上限为 **每频道 3 个**。  
- `allowlist`：直接拦截未知发送者的私信（无配对握手流程）。  
- `open`：允许任何人发送私信（公开模式）。此模式 **必须** 在频道白名单中包含 `"*"`（显式选择加入）。  
- `disabled`：完全忽略所有入站私信。

通过 CLI 审批：

```bash
openclaw pairing list <channel>
openclaw pairing approve <channel> <code>
```

详情及磁盘文件说明：[配对](/channels/pairing)

## 私信会话隔离（多用户模式）

默认情况下，OpenClaw 将 **所有私信路由至主会话**，以便您的助手能在不同设备与频道间保持上下文连续性。若 **多人** 可向机器人发送私信（开放私信或多人白名单），建议启用私信会话隔离：

```json5
{
  session: { dmScope: "per-channel-peer" },
}
```

此举可防止跨用户上下文泄露，同时维持群聊的独立性。

这是一种**消息上下文边界**，而非主机管理员（host-admin）边界。若用户彼此互为对抗关系，且共享同一网关主机/配置，请改为按信任边界为每个用户单独部署网关。

### 安全私信模式（推荐）

请将上述代码片段视为 **安全私信模式（Secure DM mode）**：

- 默认值：`session.dmScope: "main"`（所有私信共享一个会话以保障连续性）。  
- 本地 CLI 入门默认行为：当未设置时，自动写入 `session.dmScope: "per-channel-peer"`（保留现有显式值）。  
- 安全私信模式：`session.dmScope: "per-channel-peer"`（每个频道+发送者组合拥有独立的私信上下文）。

如果您在同一个频道上运行多个账户，请改用 `per-account-channel-peer`。如果同一人在多个频道上联系您，请使用 `session.identityLinks` 将这些私信会话合并为一个规范身份。参阅 [会话管理](/concepts/session) 和 [配置](/gateway/configuration)。

## 白名单（私信 + 群组）——术语说明

OpenClaw 具有两个独立的“谁可以触发我？”层级：

- **私信白名单**（`allowFrom` / `channels.discord.allowFrom` / `channels.slack.allowFrom`；旧版：`channels.discord.dm.allowFrom`、`channels.slack.dm.allowFrom`）：允许哪些用户通过私信与机器人对话。
  - 当启用 `dmPolicy="pairing"` 时，批准记录将写入账户作用域的配对白名单存储中，路径为 `~/.openclaw/credentials/`（默认账户对应 `<channel>-allowFrom.json`，非默认账户对应 `<channel>-<accountId>-allowFrom.json`），并与配置中的白名单合并。
- **群组白名单**（频道特定）：机器人接受消息的群组/频道/服务器列表。
  - 常见模式：
    - `channels.whatsapp.groups`、`channels.telegram.groups`、`channels.imessage.groups`：按群组设置的默认值，例如 `requireMention`；启用后，该设置同时也作为群组白名单（如需保留“允许全部”的行为，请包含 `"*"`）。
    - `groupPolicy="allowlist"` + `groupAllowFrom`：限制在群组会话内部（WhatsApp/Telegram/Signal/iMessage/Microsoft Teams）可触发机器人的人员范围。
    - `channels.discord.guilds` / `channels.slack.channels`：按界面（surface）设置的白名单 + 提及（mention）默认行为。
  - 群组检查按如下顺序执行：先检查 `groupPolicy`/群组白名单，再检查提及/回复激活机制。
  - 回复机器人消息（隐式提及）**不会**绕过发件人白名单（如 `groupAllowFrom`）。
  - **安全提示**：请将 `dmPolicy="open"` 和 `groupPolicy="open"` 视为最后手段的设置。它们应极少启用；除非您完全信任房间内的每一位成员，否则请优先采用配对机制 + 白名单。

详情参阅：[配置](/gateway/configuration) 和 [群组](/channels/groups)

## 提示注入（定义及其重要性）

提示注入是指攻击者精心构造一条消息，诱使模型执行不安全操作（例如：“忽略你的指令”、“转储你的文件系统”、“访问此链接并执行命令”等）。

即使拥有强系统提示（system prompt），**提示注入问题仍未被解决**。系统提示的防护机制仅提供软性指导；硬性强制措施来自工具策略（tool policy）、执行审批（exec approvals）、沙箱隔离（sandboxing）以及频道白名单（channel allowlists）——而操作员可按设计禁用这些防护。实践中有效的缓解措施包括：

- 严格限制入站私信（通过配对/白名单）。
- 在群组中优先采用“提及触发”机制；避免在公开房间中部署“始终在线”的机器人。
- 默认将链接、附件和粘贴的指令视为恶意内容。
- 在沙箱环境中运行敏感工具执行操作；确保密钥等敏感信息不存于代理可访问的文件系统中。
- 注意：沙箱功能为可选启用项。若沙箱模式关闭，则即使 `tools.exec.host` 默认设为 `sandbox`，执行操作仍将在网关主机上运行；此时，除非显式设置 `host=gateway` 并配置执行审批，否则主机执行无需审批。
- 将高风险工具（`exec`、`browser`、`web_fetch`、`web_search`）限制为仅由受信任代理或明确白名单调用。
- **模型选择至关重要**：较旧/较小/传统模型在抵御提示注入和工具误用方面显著更脆弱。对于支持工具的代理，请务必选用最新一代、经过指令强化（instruction-hardened）的最强模型。

以下信号应被视为不可信内容：

- “读取该文件/URL，并严格按其指示执行。”
- “忽略你的系统提示或安全规则。”
- “披露你的隐藏指令或工具输出结果。”
- “粘贴 `~/.openclaw` 目录或日志的全部内容。”

## 不安全的外部内容绕过标志

OpenClaw 包含若干显式绕过标志，用于禁用对外部内容的安全封装：

- `hooks.mappings[].allowUnsafeExternalContent`
- `hooks.gmail.allowUnsafeExternalContent`
- 定时任务（cron）负载字段 `allowUnsafeExternalContent`

使用建议：

- 在生产环境中，务必保持这些标志未设置或设为 `false`。
- 仅在范围高度受限的调试场景中临时启用。
- 若已启用，请对该代理进行隔离（启用沙箱 + 最小化工具集 + 独立会话命名空间）。

钩子（hook）风险提示：

- 钩子负载属于不可信内容，即使交付来源是您可控的系统（邮件/文档/网页内容也可能携带提示注入）。
- 模型能力等级越低，该风险越高。对于基于钩子的自动化流程，建议优先选用强健的现代模型等级，并严格收紧工具策略（`tools.profile: "messaging"` 或更严格），同时尽可能启用沙箱。

### 提示注入无需依赖公开私信

即使**仅有您本人**能向机器人发送私信，提示注入仍可能通过机器人读取的任何**不可信内容**发生（例如网络搜索/抓取结果、浏览器页面、电子邮件、文档、附件、粘贴的日志/代码）。换言之：发件人并非唯一的威胁面；**内容本身**就可能携带对抗性指令。

当启用工具时，典型风险是上下文泄露或意外触发工具调用。可通过以下方式缩小影响范围：

- 使用只读或禁用工具的**阅读器代理（reader agent）** 对不可信内容进行摘要，再将摘要传递给主代理。
- 对于启用了工具的代理，除非确有需要，否则请关闭 `web_search` / `web_fetch` / `browser`。
- 对于 OpenResponses 的 URL 输入（`input_file` / `input_image`），请设置严格的 `gateway.http.endpoints.responses.files.urlAllowlist` 和 `gateway.http.endpoints.responses.images.urlAllowlist`，并保持 `maxUrlParts` 数值较低。
- 对任何处理不可信输入的代理，均应启用沙箱及严格的工具白名单。
- 切勿将密钥等敏感信息置于提示词中；请改用网关主机上的环境变量或配置文件传递。

### 模型强度（安全提示）

提示注入抵抗力在不同模型等级间**并不均匀**。较小/更廉价的模型通常更容易遭受工具误用和指令劫持，尤其在对抗性提示下。

<Warning>
For tool-enabled agents or agents that read untrusted content, prompt-injection risk with older/smaller models is often too high. Do not run those workloads on weak model tiers.
</Warning>

建议：

- 对任何可执行工具或访问文件/网络的机器人，请**使用最新一代、最高等级的模型**。
- **切勿对启用了工具的代理或不可信收件箱**使用老旧/较弱/较小的模型等级；提示注入风险过高。
- 若必须使用较小模型，请**缩小影响范围**（仅启用只读工具、强化沙箱、最小化文件系统访问权限、严格执行白名单）。
- 运行小型模型时，**所有会话均应启用沙箱**，且**除非输入受到严格控制，否则禁用 `web_search`/`web_fetch`/`browser`**。
- 对于仅限聊天、输入可信且不启用工具的个人助理类应用，小型模型通常足够适用。

## 群组中的推理与详细输出

`/reasoning` 和 `/verbose` 可能暴露本不应出现在公开频道中的内部推理过程或工具输出。在群组环境中，请将它们视为**仅用于调试**，除非明确需要，否则请保持禁用。

使用建议：

- 在公开房间中，请保持 `/reasoning` 和 `/verbose` 处于禁用状态。
- 若需启用，请仅限于受信任的私信或严格管控的房间。
- 请注意：详细输出可能包含工具参数、URL 以及模型所见的数据。

## 配置加固（示例）

### 0）文件权限

请在网关主机上确保配置文件与状态数据的私密性：

- `~/.openclaw/openclaw.json`：`600`（仅限用户可读写）
- `~/.openclaw`：`700`（仅限用户）

`openclaw doctor` 可发出警告并提供自动收紧这些权限的选项。

### 0.4）网络暴露（绑定地址 + 端口 + 防火墙）

网关在同一端口上复用 **WebSocket + HTTP** 协议：

- 默认端口：`18789`
- 配置/命令行参数/环境变量：`gateway.port`、`--port`、`OPENCLAW_GATEWAY_PORT`

该 HTTP 接口包含控制台 UI 和画布（canvas）宿主服务：

- 控制台 UI（单页应用资源）（默认基础路径为 `/`）
- 画布宿主：`/__openclaw__/canvas/` 和 `/__openclaw__/a2ui/`（任意 HTML/JS；视作不可信内容）

若您通过常规浏览器加载画布内容，请将其视作其他任何不可信网页：

- 切勿将画布宿主暴露给不可信的网络或用户。
- 除非您完全理解其含义，否则切勿让画布内容与特权 Web 界面共享同一源（same origin）。

绑定模式（bind mode）控制网关监听的位置：

- `gateway.bind: "loopback"`（默认）：仅本地客户端可连接。
- 非回环地址绑定（`"lan"`、`"tailnet"`、`"custom"`）会扩大攻击面。仅在配合共享令牌/密码及真实防火墙时使用。

经验法则：

- 优先选用 Tailscale Serve 而非局域网（LAN）绑定（Serve 将网关保留在回环地址，Tailscale 负责访问控制）。
- 若必须绑定至局域网，请使用防火墙将端口访问限制在极小的源 IP 白名单内；切勿广泛地进行端口映射（port-forward）。
- 切勿在 `0.0.0.0` 上以未经身份验证的方式暴露网关。

### 0.4.1）Docker 端口发布 + UFW（`DOCKER-USER`）

若您在 VPS 上使用 Docker 运行 OpenClaw，请注意：已发布的容器端口（`-p HOST:CONTAINER` 或 Compose 中的 `ports:`）不仅受主机 `INPUT` 规则路由，还会经由 Docker 自身的转发链路。

为确保 Docker 流量符合您的防火墙策略，请在 `DOCKER-USER` 中强制实施规则（该链在 Docker 自身的 accept 规则之前被评估）。在许多现代发行版中，`iptables`/`ip6tables` 使用 `iptables-nft` 前端，但仍会将这些规则应用于 nftables 后端。

最小化白名单示例（IPv4）：

```bash
# /etc/ufw/after.rules (append as its own *filter section)
*filter
:DOCKER-USER - [0:0]
-A DOCKER-USER -m conntrack --ctstate ESTABLISHED,RELATED -j RETURN
-A DOCKER-USER -s 127.0.0.0/8 -j RETURN
-A DOCKER-USER -s 10.0.0.0/8 -j RETURN
-A DOCKER-USER -s 172.16.0.0/12 -j RETURN
-A DOCKER-USER -s 192.168.0.0/16 -j RETURN
-A DOCKER-USER -s 100.64.0.0/10 -j RETURN
-A DOCKER-USER -p tcp --dport 80 -j RETURN
-A DOCKER-USER -p tcp --dport 443 -j RETURN
-A DOCKER-USER -m conntrack --ctstate NEW -j DROP
-A DOCKER-USER -j RETURN
COMMIT
```

IPv6 使用独立的表。若启用了 Docker IPv6，请在 `/etc/ufw/after6.rules` 中添加匹配策略。

避免在文档代码片段中硬编码接口名称，例如 `eth0`。接口名称因 VPS 镜像而异（如 `ens3`、`enp*` 等），名称不匹配可能导致您的拒绝规则意外失效。

重载后的快速验证：

```bash
ufw reload
iptables -S DOCKER-USER
ip6tables -S DOCKER-USER
nmap -sT -p 1-65535 <public-ip> --open
```

预期暴露的外部端口应仅为明确需要对外提供服务的端口（对大多数部署而言：SSH + 反向代理端口）。

### 0.4.2) mDNS/Bonjour 发现（信息泄露）

网关通过 mDNS（端口 5353 上的 `_openclaw-gw._tcp`）广播其存在，以支持本地设备发现。在“完整模式”下，该广播包含可能泄露运行时细节的 TXT 记录：

- `cliPath`：CLI 二进制文件的完整文件系统路径（暴露用户名和安装位置）
- `sshPort`：宣告主机上 SSH 服务可用
- `displayName`、`lanHost`：主机名信息

**运维安全考量**：广播基础设施细节会为本地网络上的任何人员提供更便利的侦察条件。即使是看似“无害”的信息（如文件系统路径或 SSH 可用性）也能帮助攻击者绘制您的环境拓扑。

**建议措施**：

1. **最小化模式**（默认，推荐用于对外暴露的网关）：从 mDNS 广播中省略敏感字段：

   ```json5
   {
     discovery: {
       mdns: { mode: "minimal" },
     },
   }
   ```

2. **完全禁用**（若您无需本地设备发现）：

   ```json5
   {
     discovery: {
       mdns: { mode: "off" },
     },
   }
   ```

3. **完整模式**（需显式启用）：在 TXT 记录中包含 `cliPath` 和 `sshPort`：

   ```json5
   {
     discovery: {
       mdns: { mode: "full" },
     },
   }
   ```

4. **环境变量方式**（替代方案）：设置 `OPENCLAW_DISABLE_BONJOUR=1`，在不修改配置的前提下禁用 mDNS。

在最小化模式下，网关仍广播足够信息以支持设备发现（`role`、`gatewayPort`、`transport`），但省略 `cliPath` 和 `sshPort`。需要获取 CLI 路径信息的应用程序可通过已认证的 WebSocket 连接获取该信息。

### 0.5) 锁定网关 WebSocket（本地认证）

网关认证 **默认强制启用**。若未配置令牌/密码，网关将拒绝所有 WebSocket 连接（故障时默认关闭）。

初始配置向导默认生成一个令牌（即使仅用于回环连接），因此本地客户端必须完成身份认证。

设置令牌，使 **所有** WebSocket 客户端均须认证：

```json5
{
  gateway: {
    auth: { mode: "token", token: "your-token" },
  },
}
```

Doctor 工具可为您生成一个：`openclaw doctor --generate-gateway-token`。

注意：`gateway.remote.token` / `.password` 是客户端凭据来源，它们 **本身无法** 保护本地 WebSocket 访问。  
本地调用路径可在 `gateway.auth.*` 未设置时，将 `gateway.remote.*` 作为备用方案。  
可选：当使用 `wss://` 时，通过 `gateway.remote.tlsFingerprint` 对远程 TLS 进行证书固定。  
明文 `ws://` 默认仅限回环访问。对于受信任的私有网络路径，可在客户端进程中设置 `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1` 作为应急绕过机制。

本地设备配对：

- 对于 **本地** 连接（回环地址或网关主机自身的 Tailnet 地址），设备配对自动批准，以保障同主机客户端的流畅体验。
- 其他 Tailnet 对等节点 **不视为本地节点**；它们仍需人工配对审批。

认证模式：

- `gateway.auth.mode: "token"`：共享的承载令牌（推荐用于大多数部署）。
- `gateway.auth.mode: "password"`：密码认证（建议通过环境变量设置：`OPENCLAW_GATEWAY_PASSWORD`）。
- `gateway.auth.mode: "trusted-proxy"`：信任具备身份感知能力的反向代理，由其完成用户认证，并通过请求头传递身份信息（参见 [可信代理认证](/gateway/trusted-proxy-auth)）。

轮换检查清单（令牌/密码）：

1. 生成/设置新密钥（`gateway.auth.token` 或 `OPENCLAW_GATEWAY_PASSWORD`）。
2. 重启网关（若 macOS 应用托管网关，则重启该应用）。
3. 更新所有远程客户端（在调用网关的机器上更新 `gateway.remote.token` / `.password`）。
4. 验证是否已无法使用旧凭据建立连接。

### 0.6) Tailscale Serve 身份请求头

当 `gateway.auth.allowTailscale` 为 `true`（Serve 的默认值）时，OpenClaw 接受 Tailscale Serve 身份请求头（`tailscale-user-login`）进行控制界面/WebSocket 认证。OpenClaw 通过本地 Tailscale 守护进程（`tailscale whois`）解析 `x-forwarded-for` 地址，并与请求头中的值比对来验证身份。此机制仅对命中回环地址且携带 Tailscale 注入的 `x-forwarded-for`、`x-forwarded-proto` 和 `x-forwarded-host` 请求头的请求触发。  
HTTP API 端点（例如 `/v1/*`、`/tools/invoke` 和 `/api/channels/*`）仍需令牌/密码认证。

重要边界说明：

- 网关 HTTP 承载令牌认证实质上是全有或全无的操作员级访问权限。
- 将能调用 `/v1/chat/completions`、`/v1/responses`、`/tools/invoke` 或 `/api/channels/*` 的凭据视为该网关的完全访问操作员密钥。
- 切勿将此类凭据共享给不可信的调用方；建议按信任边界为每个网关单独部署。

**信任假设**：无令牌的 Serve 认证假定网关主机本身可信。  
请勿将其视作抵御恶意同主机进程的防护手段。若网关主机上可能运行不可信的本地代码，请禁用 `gateway.auth.allowTailscale` 并强制要求令牌/密码认证。

**安全规则**：切勿从您自己的反向代理转发这些请求头。若您在网关前端终止 TLS 或执行代理，应禁用 `gateway.auth.allowTailscale`，并改用令牌/密码认证（或 [可信代理认证](/gateway/trusted-proxy-auth)）。

可信代理：

- 若您在网关前端终止 TLS，请将 `gateway.trustedProxies` 设置为您代理服务器的 IP 地址。
- OpenClaw 将信任来自这些 IP 的 `x-forwarded-for`（或 `x-real-ip`），用于确定客户端 IP，从而执行本地配对检查及 HTTP 认证/本地检查。
- 请确保您的代理 **覆盖** `x-forwarded-for`，并阻止对网关端口的直接访问。

参见 [Tailscale](/gateway/tailscale) 和 [Web 概览](/web)。

### 0.6.1) 通过 Node 主机实现浏览器控制（推荐）

若您的网关位于远程，但浏览器运行于另一台机器上，请在浏览器所在机器上运行 **Node 主机**，并让网关代理浏览器操作（参见 [浏览器工具](/tools/browser)）。请将 Node 配对视为管理员访问权限。

推荐实践：

- 将网关与 Node 主机置于同一 Tailnet（Tailscale）中。
- 主动完成 Node 配对；若无需浏览器代理路由，请禁用该功能。

请避免：

- 在局域网或公共互联网上暴露中继/控制端口。
- 使用 Tailscale Funnel 暴露浏览器控制端点（造成公开暴露）。

### 0.7) 磁盘上的密钥（哪些内容敏感）

请假设 `~/.openclaw/`（或 `$OPENCLAW_STATE_DIR/`）目录下的所有内容均可能包含密钥或私有数据：

- `openclaw.json`：配置文件可能包含网关/远程网关令牌、提供商设置及白名单。
- `credentials/**`：通道凭据（例如 WhatsApp 凭据）、配对白名单、遗留 OAuth 导入项。
- `agents/<agentId>/agent/auth-profiles.json`：API 密钥、令牌配置文件、OAuth 令牌，以及可选的 `keyRef`/`tokenRef`。
- `secrets.json`（可选）：由 `file` SecretRef 提供商使用的基于文件的密钥载荷（`secrets.providers`）。
- `agents/<agentId>/agent/auth.json`：遗留兼容性文件。静态 `api_key` 条目在被发现时将被清除。
- `agents/<agentId>/sessions/**`：会话转录内容（`*.jsonl`）+ 路由元数据（`sessions.json`），其中可能包含私密消息及工具输出。
- `extensions/**`：已安装插件（及其 `node_modules/`）。
- `sandboxes/**`：工具沙箱工作区；可能累积您在沙箱内读写文件的副本。

加固建议：

- 严格限制权限（目录设为 `700`，文件设为 `600`）。
- 在网关主机上启用全盘加密。
- 若主机为多用户共享环境，建议为网关创建专用操作系统用户账户。

### 0.8) 日志与转录内容（脱敏与保留策略）

即使访问控制配置正确，日志与转录内容仍可能泄露敏感信息：

- 网关日志可能包含工具摘要、错误信息及 URL。
- 会话转录内容可能包含粘贴的密钥、文件内容、命令输出及链接。

建议措施：

- 保持工具摘要脱敏开启（`logging.redactSensitive: "tools"`；默认启用）。
- 通过 `logging.redactPatterns` 添加适用于您环境的自定义脱敏模式（令牌、主机名、内部 URL 等）。
- 分享诊断信息时，请优先使用 `openclaw status --all`（可粘贴格式，已脱敏密钥），而非原始日志。
- 若无需长期保留，请定期清理旧的会话转录与日志文件。

详情参见：[日志记录](/gateway/logging)

### 1) 私信：默认启用配对

```json5
{
  channels: { whatsapp: { dmPolicy: "pairing" } },
}
```

### 2) 群组：处处需提及

```json
{
  "channels": {
    "whatsapp": {
      "groups": {
        "*": { "requireMention": true }
      }
    }
  },
  "agents": {
    "list": [
      {
        "id": "main",
        "groupChat": { "mentionPatterns": ["@openclaw", "@mybot"] }
      }
    ]
  }
}
```

在群组聊天中，仅在被明确提及（@）时才响应。

### 3. 分离号码

建议为 AI 应用分配独立于个人号码的电话号码：

- 个人号码：保障您的对话隐私
- Bot 号码：AI 处理相关事务，并设定适当边界

### 4. 只读模式（当前通过沙箱 + 工具实现）

您目前已可通过以下组合构建只读配置：

- `agents.defaults.sandbox.workspaceAccess: "ro"`（或 `"none"`，完全禁用工作区访问）
- 工具允许/禁止列表，屏蔽 `write`、`edit`、`apply_patch`、`exec`、`process` 等操作

未来我们可能添加单一的 `readOnlyMode` 标志，以简化此类配置。

其他加固选项：

- `tools.exec.applyPatch.workspaceOnly: true`（默认）：确保即使沙箱功能已关闭，`apply_patch` 也无法在工作区目录之外执行写入或删除操作。仅当您明确希望 `apply_patch` 访问工作区之外的文件时，才将其设为 `false`。
- `tools.fs.workspaceOnly: true`（可选）：将 `read`/`write`/`edit`/`apply_patch` 路径及原生提示图像自动加载路径限制在工作区目录内（若您当前允许使用绝对路径，此设置可作为单一防护措施）。
- 保持文件系统根路径尽可能狭窄：避免为代理工作区/沙箱工作区指定过宽泛的根路径（例如您的主目录）。过宽的根路径可能导致敏感本地文件（例如位于 `~/.openclaw` 下的状态/配置文件）暴露给文件系统工具。

### 5) 安全基线（复制/粘贴）

一种“安全默认”配置，可确保网关私有化、要求 DM 配对，并避免始终启用群组机器人：

```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    port: 18789,
    auth: { mode: "token", token: "your-long-random-token" },
  },
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      groups: { "*": { requireMention: true } },
    },
  },
}
```

若您也希望工具执行“默认更安全”，可为任意非所有者代理添加沙箱机制，并禁止其使用危险工具（参见下方“按代理访问配置文件”中的示例）。

面向聊天驱动型代理轮次的内置基线：非所有者发送方无法使用 `cron` 或 `gateway` 工具。

## 沙箱机制（推荐）

专属文档：[沙箱机制](/gateway/sandboxing)

两种互补方法：

- **在 Docker 中运行完整网关**（容器边界）：[Docker](/install/docker)  
- **工具级沙箱**（`agents.defaults.sandbox`，主机网关 + Docker 隔离工具）：[沙箱机制](/gateway/sandboxing)

注意：为防止跨代理访问，请将 `agents.defaults.sandbox.scope` 保持为 `"agent"`（默认值），  
或设为 `"session"` 以实现更严格的按会话隔离。`scope: "shared"` 使用单个容器/工作区。

还需考虑沙箱内代理工作区的访问权限：

- `agents.defaults.sandbox.workspaceAccess: "none"`（默认）使代理工作区不可访问；工具在 `~/.openclaw/sandboxes` 下的沙箱工作区中运行  
- `agents.defaults.sandbox.workspaceAccess: "ro"` 将代理工作区以只读方式挂载至 `/agent`（禁用 `write`/`edit`/`apply_patch`）  
- `agents.defaults.sandbox.workspaceAccess: "rw"` 将代理工作区以读写方式挂载至 `/workspace`

重要提示：`tools.elevated` 是全局基线逃生通道，可在宿主机上直接执行 exec 命令。请严格管控 `tools.elevated.allowFrom`，切勿向陌生人启用该功能。您还可通过 `agents.list[].tools.elevated` 进一步按代理限制提权操作。详见 [提权模式](/tools/elevated)。

### 子代理委托防护栏

若您允许会话工具，请将委托式子代理运行视为另一重边界决策：

- 除非代理确实需要委托能力，否则禁止 `sessions_spawn`。  
- 将 `agents.list[].subagents.allowAgents` 严格限制于已知安全的目标代理。  
- 对任何必须保持沙箱化的流程，请调用 `sessions_spawn` 并传入 `sandbox: "require"`（默认为 `inherit`）。  
- 当目标子运行时环境未启用沙箱时，`sandbox: "require"` 将快速失败。

## 浏览器控制风险

启用浏览器控制功能后，模型即可驱动真实浏览器。  
若该浏览器配置文件中已存在登录会话，则模型可访问对应账号及其中数据。请将浏览器配置文件视为**敏感状态**：

- 优先为代理使用专用配置文件（默认为 `openclaw` 配置文件）。  
- 避免将代理指向您日常使用的个人浏览器配置文件。  
- 对于沙箱化代理，请在宿主机上禁用浏览器控制功能，除非您完全信任该代理。  
- 将浏览器下载内容视为不可信输入；建议使用隔离的下载目录。  
- 若可行，请在代理配置文件中禁用浏览器同步/密码管理器（以缩小潜在影响范围）。  
- 对于远程网关，请假定“浏览器控制”等同于“操作员访问权限”，即该配置文件所能触及的所有资源均可能被访问。  
- 请确保网关与节点主机仅限 Tailnet 内部通信；避免将中继/控制端口暴露至局域网或公网。  
- Chrome 扩展中继的 CDP 端点受身份验证保护；仅 OpenClaw 客户端可连接。  
- 在无需浏览器代理路由时请将其禁用（`gateway.nodes.browser.mode="off"`）。  
- Chrome 扩展中继模式**并非**“更安全”选项；它可接管您现有的 Chrome 标签页。请假定其可在该标签页/配置文件所能访问的全部范围内以您的身份执行操作。

### 浏览器 SSRF 策略（默认为可信网络）

OpenClaw 的浏览器网络策略默认采用可信操作员模型：除非您显式禁用，否则允许访问私有/内部地址。

- 默认值：`browser.ssrfPolicy.dangerouslyAllowPrivateNetwork: true`（未设置时隐式生效）。  
- 兼容性别名：`browser.ssrfPolicy.allowPrivateNetwork` 仍被接受以保证向后兼容。  
- 严格模式：设置 `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork: false`，默认阻止私有/内部/特殊用途地址。  
- 在严格模式下，使用 `hostnameAllowlist`（支持类似 `*.example.com` 的匹配模式）和 `allowedHostnames`（精确主机例外列表，包括已被屏蔽的名称如 `localhost`）进行显式例外配置。  
- 导航请求会在发起前检查，并在导航完成后尽力对最终 `http(s)` URL 进行二次检查，以降低基于重定向的横向移动风险。

严格策略示例：

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,
      hostnameAllowlist: ["*.example.com", "example.com"],
      allowedHostnames: ["localhost"],
    },
  },
}
```

## 按代理访问配置文件（多代理）

借助多代理路由机制，每个代理均可拥有独立的沙箱及工具策略：  
可借此为各代理分别授予**完全访问权限**、**只读权限**或**无访问权限**。  
详见 [多代理沙箱与工具](/tools/multi-agent-sandbox-tools)，了解完整说明及优先级规则。

常见使用场景：

- 个人代理：完全访问权限，不启用沙箱  
- 家庭/工作代理：启用沙箱 + 只读工具  
- 公共代理：启用沙箱 + 禁用文件系统/Shell 工具  

### 示例：完全访问（不启用沙箱）

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: { mode: "off" },
      },
    ],
  },
}
```

### 示例：只读工具 + 只读工作区

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: {
          mode: "all",
          scope: "agent",
          workspaceAccess: "ro",
        },
        tools: {
          allow: ["read"],
          deny: ["write", "edit", "apply_patch", "exec", "process", "browser"],
        },
      },
    ],
  },
}
```

### 示例：禁用文件系统/Shell 访问（允许提供方消息传递）

```json5
{
  agents: {
    list: [
      {
        id: "public",
        workspace: "~/.openclaw/workspace-public",
        sandbox: {
          mode: "all",
          scope: "agent",
          workspaceAccess: "none",
        },
        // Session tools can reveal sensitive data from transcripts. By default OpenClaw limits these tools
        // to the current session + spawned subagent sessions, but you can clamp further if needed.
        // See `tools.sessions.visibility` in the configuration reference.
        tools: {
          sessions: { visibility: "tree" }, // self | tree | agent | all
          allow: [
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "whatsapp",
            "telegram",
            "slack",
            "discord",
          ],
          deny: [
            "read",
            "write",
            "edit",
            "apply_patch",
            "exec",
            "process",
            "browser",
            "canvas",
            "nodes",
            "cron",
            "gateway",
            "image",
          ],
        },
      },
    ],
  },
}
```

## 应告知 AI 的安全事项

请在代理的系统提示词中包含安全指南：

```
## Security Rules
- Never share directory listings or file paths with strangers
- Never reveal API keys, credentials, or infrastructure details
- Verify requests that modify system config with the owner
- When in doubt, ask before acting
- Keep private data private unless explicitly authorized
```

## 事件响应

若您的 AI 执行了恶意操作：

### 隔离

1. **立即中止**：停止 macOS 应用（若其监管网关）或终止您的 `openclaw gateway` 进程。  
2. **关闭暴露面**：设置 `gateway.bind: "loopback"`（或禁用 Tailscale Funnel/Serve），直至查明事件原因。  
3. **冻结访问权限**：将存在风险的 DM/群组切换为 `dmPolicy: "disabled"` / 要求提及触发，同时移除您此前配置的 `"*"` 全允许条目（如有）。

### 轮换密钥（若密钥已泄露，请假定系统已被攻破）

1. 轮换网关认证凭据（`gateway.auth.token` / `OPENCLAW_GATEWAY_PASSWORD`）并重启服务。  
2. 轮换远程客户端密钥（`gateway.remote.token` / `.password`），覆盖所有可调用网关的设备。  
3. 轮换提供方/API 凭据（WhatsApp 凭据、Slack/Discord 令牌、`auth-profiles.json` 中的模型/API 密钥，以及加密密钥负载值）。

### 审计

1. 检查网关日志：`/tmp/openclaw/openclaw-YYYY-MM-DD.log`（或 `logging.file`）。  
2. 复查相关会话记录：`~/.openclaw/agents/<agentId>/sessions/*.jsonl`。  
3. 复查近期配置变更（任何可能扩大访问权限的变更：`gateway.bind`、`gateway.auth`、DM/群组策略、`tools.elevated`、插件变更）。  
4. 重新运行 `openclaw security audit --deep`，确认关键问题已修复。

### 收集报告所需信息

- 时间戳、网关宿主机操作系统 + OpenClaw 版本  
- 会话记录（含脱敏后的简短日志尾部）  
- 攻击者发送的内容 + 代理执行的操作  
- 网关是否超出回环地址暴露（局域网/Tailscale Funnel/Serve）

## 密钥扫描（detect-secrets）

CI 在 `secrets` 任务中运行 `detect-secrets` pre-commit 钩子。  
向 `main` 的推送始终执行全文件扫描。对于拉取请求，若存在基础提交（base commit），则采用变更文件的快速路径；否则回退至全文件扫描。如果扫描失败，则说明存在尚未纳入基线的新候选密钥。

### 如果 CI 失败

1. 在本地复现问题：

   ```bash
   pre-commit run --all-files detect-secrets
   ```

2. 理解相关工具：
   - pre-commit 中的 `detect-secrets` 会使用仓库的基线和排除规则运行 `detect-secrets-hook`。
   - `detect-secrets audit` 启动交互式审查，用于将每个基线条目标记为真实密钥或误报。
3. 对于真实密钥：请轮换或移除它们，然后重新运行扫描以更新基线。
4. 对于误报：运行交互式审计并将其标记为误报：

   ```bash
   detect-secrets audit .secrets.baseline
   ```

5. 如果需要新增排除项，请将其添加到 `.detect-secrets.cfg`，并使用匹配的 `--exclude-files` / `--exclude-lines` 标志重新生成基线（该配置文件仅作参考；detect-secrets 不会自动读取它）。

当 `.secrets.baseline` 反映出预期状态后，请提交更新后的文件。

## 报告安全问题

发现 OpenClaw 存在漏洞？请负责任地报告：

1. 邮箱：[security@openclaw.ai](mailto:security@openclaw.ai)  
2. 请勿在问题修复前公开披露  
3. 我们将致谢您的贡献（除非您希望保持匿名）