---
summary: "Exec approvals, allowlists, and sandbox escape prompts"
read_when:
  - Configuring exec approvals or allowlists
  - Implementing exec approval UX in the macOS app
  - Reviewing sandbox escape prompts and implications
title: "Exec Approvals"
---
# 执行审批

执行审批是让沙盒代理在真实主机（`gateway` 或 `node`）上运行命令的**配套应用/节点主机护栏**。可以将其视为一种安全联锁：只有当策略 + 允许列表 + （可选的）用户批准都同意时，才允许执行命令。
执行审批是**除了**工具策略和提升门控之外的（除非提升设置为 `full`，这将跳过审批）。有效策略是 `tools.exec.*` 和审批默认值中**更严格**的那个；如果省略了审批字段，则使用 `tools.exec` 值。

如果配套应用程序UI**不可用**，任何需要提示的请求都将通过**询问回退**（默认：拒绝）解决。

## 适用范围

执行审批在执行主机上本地强制执行：

- **网关主机** → 网关机器上的 `openclaw` 进程
- **节点主机** → 节点运行器（macOS 配套应用或无头节点主机）

信任模型说明：

- 经网关认证的调用者被视为该网关的信任操作员。
- 配对节点将这种受信任的操作员能力扩展到节点主机。
- 执行审批减少了意外执行的风险，但不是每个用户的授权边界。
- 已批准的节点主机运行还绑定规范执行上下文：规范的工作目录、适用时固定的可执行文件路径以及解释器风格的脚本操作数。如果绑定的脚本在批准后但在执行前发生变化，则会拒绝运行而不是执行漂移的内容。

macOS 分割：

- **节点主机服务**通过本地IPC将 `system.run` 转发给**macOS 应用程序**。
- **macOS 应用程序**强制执行审批并在UI上下文中执行命令。

## 设置和存储

审批信息存储在执行主机上的本地JSON文件中：

`~/.openclaw/exec-approvals.json`

示例模式：

```json
{
  "version": 1,
  "socket": {
    "path": "~/.openclaw/exec-approvals.sock",
    "token": "base64url-token"
  },
  "defaults": {
    "security": "deny",
    "ask": "on-miss",
    "askFallback": "deny",
    "autoAllowSkills": false
  },
  "agents": {
    "main": {
      "security": "allowlist",
      "ask": "on-miss",
      "askFallback": "deny",
      "autoAllowSkills": true,
      "allowlist": [
        {
          "id": "B0C8C0B3-2C2D-4F8A-9A3C-5A4B3C2D1E0F",
          "pattern": "~/Projects/**/bin/rg",
          "lastUsedAt": 1737150000000,
          "lastUsedCommand": "rg -n TODO",
          "lastResolvedPath": "/Users/user/Projects/.../bin/rg"
        }
      ]
    }
  }
}
```

## 策略控制

### 安全性 (`exec.security`)

- **deny**：阻止所有主机执行请求。
- **allowlist**：仅允许允许列表中的命令。
- **full**：允许一切（等同于提升）。

### 询问 (`exec.ask`)

- **off**：从不提示。
- **on-miss**：仅当允许列表不匹配时提示。
- **always**：每次命令都提示。

### 询问回退 (`askFallback`)

如果需要提示但没有可达的UI，回退决定：

- **deny**：阻止。
- **allowlist**：仅当允许列表匹配时允许。
- **full**：允许。

## 允许列表（每个代理）

允许列表是**针对每个代理**的。如果有多个代理存在，请在macOS应用程序中切换要编辑的代理。模式是**不区分大小写的通配符匹配**。模式应解析为**二进制路径**（仅包含基本名称的条目将被忽略）。旧的 `agents.default` 条目在加载时迁移到 `agents.main`。

示例：

- `~/Projects/**/bin/peekaboo`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

每个允许列表条目跟踪：

- **id** 用于UI标识的稳定UUID（可选）
- **最后使用** 时间戳
- **最后使用的命令**
- **最后解析的路径**

## 自动允许技能CLI

当启用**自动允许技能CLI**时，由已知技能引用的可执行文件被视为在节点（macOS节点或无头节点主机）上允许列表中的。这使用通过网关RPC获取技能bin列表的 `skills.bins`。如果您希望严格的手动允许列表，请禁用此功能。

重要的信任注意事项：

- 这是一个**隐式的便利允许列表**，与手动路径允许列表条目分开。
- 它旨在用于网关和节点在同一信任边界内的受信任操作员环境。
- 如果您需要严格的显式信任，请保持 `autoAllowSkills: false` 并仅使用手动路径允许列表条目。

## 安全二进制文件（仅标准输入）

`tools.exec.safeBins` 定义了一个小的**仅标准输入**二进制文件列表（例如 `jq`），这些文件可以在允许列表模式下运行而无需显式的允许列表条目。安全二进制文件拒绝位置文件参数和类似路径的标记，因此它们只能处理传入流。将此视为流过滤器的狭窄快速路径，而不是通用信任列表。
**不要**将解释器或运行时二进制文件（例如 `python3`, `node`, `ruby`, `bash`, `sh`, `zsh`）添加到 `safeBins` 中。
如果一个命令设计上可以评估代码、执行子命令或读取文件，请优先使用显式的允许列表条目并保持审批提示启用。
自定义安全二进制文件必须在 `tools.exec.safeBinProfiles.<bin>` 中定义明确的配置文件。
验证仅从argv形状确定（不进行主机文件系统存在检查），从而防止从允许/拒绝差异导致的文件存在预言行为。
默认的安全二进制文件拒绝面向文件的选项（例如 `sort -o`, `sort --output`,
`sort --files0-from`, `sort --compress-program`, `sort --random-source`,
`sort --temporary-directory`/`-T`, `wc --files0-from`, `jq -f/--from-file`,
`grep -f/--file`）。
安全二进制文件还对破坏仅标准输入行为的选项实施显式的每二进制文件标志策略（例如 `sort -o/--output/--compress-program` 和grep递归标志）。
在安全二进制文件模式下，长选项验证失败关闭：未知标志和模糊缩写被拒绝。
按安全二进制文件配置文件拒绝的标志：

<!-- SAFE_BIN_DENIED_FLAGS:START -->

- `grep`: `--dereference-recursive`, `--directories`, `--exclude-from`, `--file`, `--recursive`, `-R`, `-d`, `-f`, `-r`
- `jq`: `--argfile`, `--from-file`, `--library-path`, `--rawfile`, `--slurpfile`, `-L`, `-f`
- `sort`: `--compress-program`, `--files0-from`, `--output`, `--random-source`, `--temporary-directory`, `-T`, `-o`
- `wc`: `--files0-from`
<!-- SAFE_BIN_DENIED_FLAGS:END -->

安全二进制文件还强制在执行时将argv令牌视为**字面文本**（对于仅标准输入段落，没有通配符展开和没有 `$VARS` 展开），因此像 `*` 或 `$HOME/...` 这样的模式不能用于走私文件读取。
安全二进制文件还必须从受信任的二进制目录（系统默认值加上可选的 `tools.exec.safeBinTrustedDirs`）解析。`PATH` 条目永远不会自动信任。
默认的受信任安全二进制文件目录有意最小化：`/bin`, `/usr/bin`。
如果您的安全二进制文件位于包管理器/用户路径（例如 `/opt/homebrew/bin`, `/usr/local/bin`, `/opt/local/bin`, `/snap/bin`）中，请将它们显式添加到 `tools.exec.safeBinTrustedDirs`。
在允许列表模式下，shell链和重定向不会自动允许。

当每个顶层段满足允许列表（包括安全二进制文件或技能自动允许）时，允许shell链（`&&`, `||`, `;`）。在允许列表模式下，重定向仍然不受支持。
在允许列表解析期间，包括双引号内，命令替换（`$()` / 反引号）被拒绝；如果需要字面 `$()` 文本，请使用单引号。
在macOS配套应用审批中，包含shell控制或扩展语法的原始shell文本（`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`) is treated as an allowlist miss unless
the shell binary itself is allowlisted.
For shell wrappers (`bash|sh|zsh ... -c/-lc`), request-scoped env overrides are reduced to a
small explicit allowlist (`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`).
For allow-always decisions in allowlist mode, known dispatch wrappers
(`env`, `nice`, `nohup`, `stdbuf`, `timeout`) persist inner executable paths instead of wrapper
paths. Shell multiplexers (`busybox`, `toybox`) are also unwrapped for shell applets (`sh`, `ash`,
etc.) so inner executables are persisted instead of multiplexer binaries. If a wrapper or
multiplexer cannot be safely unwrapped, no allowlist entry is persisted automatically.

Default safe bins: `jq`, `cut`, `uniq`, `head`, `tail`, `tr`, `wc`.

`grep` and `sort` are not in the default list. If you opt in, keep explicit allowlist entries for
their non-stdin workflows.
For `grep` in safe-bin mode, provide the pattern with `-e`/`--regexp`; positional pattern form is
rejected so file operands cannot be smuggled as ambiguous positionals.

### Safe bins versus allowlist

| Topic            | `tools.exec.safeBins`                                  | Allowlist (`exec-approvals.json`)                            |
| ---------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| Goal             | Auto-allow narrow stdin filters                        | Explicitly trust specific executables                        |
| Match type       | Executable name + safe-bin argv policy                 | Resolved executable path glob pattern                        |
| Argument scope   | Restricted by safe-bin profile and literal-token rules | Path match only; arguments are otherwise your responsibility |
| Typical examples | `jq`, `head`, `tail`, `wc`                             | `python3`, `node`, `ffmpeg`, 自定义CLI                     |
| 最佳用途         | 在管道中进行低风险文本转换                  | 任何具有更广泛行为或副作用的工具               |

配置位置：

- `safeBins` 来自配置（`tools.exec.safeBins` 或每个代理的 `agents.list[].tools.exec.safeBins`）。
- `safeBinTrustedDirs` 来自配置（`tools.exec.safeBinTrustedDirs` 或每个代理的 `agents.list[].tools.exec.safeBinTrustedDirs`）。
- `safeBinProfiles` 来自配置（`tools.exec.safeBinProfiles` 或每个代理的 `agents.list[].tools.exec.safeBinProfiles`）。每个代理的配置键会覆盖全局键。
- 允许列表条目位于主机本地的 `~/.openclaw/exec-approvals.json` 下的 `agents.<id>.allowlist` 中（或通过控制界面 / `openclaw approvals allowlist ...`）。
- 当解释器/运行时二进制文件出现在没有明确配置文件的 `safeBins` 时，`openclaw security audit` 会使用 `tools.exec.safe_bins_interpreter_unprofiled` 发出警告。
- `openclaw doctor --fix` 可以将缺失的自定义 `safeBinProfiles.<bin>` 条目作为 `{}` 构建（之后进行审查和收紧）。解释器/运行时二进制文件不会自动构建。

自定义配置文件示例：

```json5
{
  tools: {
    exec: {
      safeBins: ["jq", "myfilter"],
      safeBinProfiles: {
        myfilter: {
          minPositional: 0,
          maxPositional: 0,
          allowedValueFlags: ["-n", "--limit"],
          deniedFlags: ["-f", "--file", "-c", "--command"],
        },
      },
    },
  },
}
```

## 控制界面编辑

使用 **控制界面 → 节点 → 执行批准** 卡片来编辑默认值、每个代理的覆盖设置和允许列表。选择一个范围（默认值或某个代理），调整策略，添加/删除允许列表模式，然后 **保存**。界面会显示每个模式的 **最后使用** 元数据，以便您可以保持列表整洁。

目标选择器可以选择 **网关**（本地批准）或 **节点**。节点必须广播 `system.execApprovals.get/set`（macOS 应用程序或无头节点主机）。
如果某个节点尚未广播执行批准，则直接编辑其本地的 `~/.openclaw/exec-approvals.json`。

CLI: `openclaw approvals` 支持网关或节点编辑（参见 [批准 CLI](/cli/approvals)）。

## 批准流程

当需要提示时，网关会向操作员客户端广播 `exec.approval.requested`。控制界面和 macOS 应用程序通过 `exec.approval.resolve` 解决它，然后网关将批准的请求转发到节点主机。

对于 `host=node`，批准请求包括一个规范的 `systemRunPlan` 有效负载。网关在转发批准的 `system.run` 请求时，使用该计划作为权威的命令/cwd/会话上下文。

当需要批准时，执行工具会立即返回一个批准 ID。使用该 ID 来关联后续的系统事件（`Exec finished` / `Exec denied`）。如果没有在超时前做出决定，请求将被视为批准超时，并作为拒绝原因显示。

确认对话框包括：

- 命令 + 参数
- 当前工作目录
- 代理 ID
- 解析后的可执行路径
- 主机 + 策略元数据

操作：

- **允许一次** → 立即运行
- **始终允许** → 添加到允许列表并运行
- **拒绝** → 阻止

## 将批准转发到聊天频道

您可以将执行批准提示转发到任何聊天频道（包括插件频道），并通过 `/approve` 批准它们。这使用正常的外发交付管道。

配置：

```json5
{
  approvals: {
    exec: {
      enabled: true,
      mode: "session", // "session" | "targets" | "both"
      agentFilter: ["main"],
      sessionFilter: ["discord"], // substring or regex
      targets: [
        { channel: "slack", to: "U12345678" },
        { channel: "telegram", to: "123456789" },
      ],
    },
  },
}
```

在聊天中回复：

```
/approve <id> allow-once
/approve <id> allow-always
/approve <id> deny
```

### macOS IPC 流程

```
Gateway -> Node Service (WS)
                 |  IPC (UDS + token + HMAC + TTL)
                 v
             Mac App (UI + approvals + system.run)
```

安全注意事项：

- Unix 套接字模式 `0600`，令牌存储在 `exec-approvals.json` 中。
- 同 UID 对等检查。
- 挑战/响应（nonce + HMAC 令牌 + 请求哈希）+ 短 TTL。

## 系统事件

执行生命周期作为系统消息显示：

- `Exec running`（仅当命令超过运行通知阈值时）
- `Exec finished`
- `Exec denied`

这些消息会在节点报告事件后发布到代理的会话中。网关主机执行批准在命令完成时（以及可选地在运行时间超过阈值时）发出相同的生命周期事件。需要批准的执行在这些消息中重用批准 ID 作为 `runId`，以便于关联。

## 影响

- **full** 功能强大；尽可能使用允许列表。
- **ask** 让您保持在循环中，同时仍允许快速批准。
- 每个代理的允许列表防止一个代理的批准泄露给其他代理。
- 批准仅适用于来自 **授权发送者** 的主机执行请求。未经授权的发送者不能发出 `/exec`。
- `/exec security=full` 是为授权操作员提供的会话级便利，并且设计上跳过批准。要硬阻止主机执行，请将批准安全性设置为 `deny` 或通过工具策略拒绝 `exec` 工具。

相关：

- [执行工具](/tools/exec)
- [提升模式](/tools/elevated)
- [技能](/tools/skills)