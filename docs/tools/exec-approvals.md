---
summary: "Exec approvals, allowlists, and sandbox escape prompts"
read_when:
  - Configuring exec approvals or allowlists
  - Implementing exec approval UX in the macOS app
  - Reviewing sandbox escape prompts and implications
title: "Exec Approvals"
---
# 执行审批

执行审批是让沙盒代理在真实主机（`gateway` 或 `node`）上运行命令的 **配套应用程序/节点主机防护栏**。可以将其视为安全联锁：只有当策略 + 允许列表 + （可选）用户审批都同意时，才允许执行命令。
执行审批 **附加于** 工具策略和提升门控（除非提升设置为 `full`，这将跳过审批）。
有效策略是 `tools.exec.*` 和审批默认值中 **更严格的**；如果省略了审批字段，则使用 `tools.exec` 值。

如果配套应用程序界面 **不可用**，任何需要提示的请求将由 **ask 回退**（默认：拒绝）解决。

## 应用场景

执行审批在执行主机上本地强制执行：

- **网关主机** → 网关机器上的 `openclaw` 进程
- **节点主机** → 节点运行器（macOS 配套应用程序或无头节点主机）

macOS 分割：

- **节点主机服务** 通过本地 IPC 将 `system.run` 转发到 **macOS 应用程序**。
- **macOS 应用程序** 强制执行审批并以 UI 上下文执行命令。

## 设置和存储

审批存储在执行主机上的本地 JSON 文件中：

`~/.openclaw/exec-approvals.json`

示例架构：

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

## 策略选项

### 安全性 (`exec.security`)

- **deny**: 阻止所有主机执行请求。
- **allowlist**: 仅允许白名单中的命令。
- **full**: 允许一切（等同于提升）。

### Ask (`exec.ask`)

- **off**: 从不提示。
- **on-miss**: 仅在白名单不匹配时提示。
- **always**: 对每个命令都提示。

### Ask 回退 (`askFallback`)

如果需要提示但无法访问 UI，回退决定：

- **deny**: 阻止。
- **allowlist**: 仅在白名单匹配时允许。
- **full**: 允许。

## 白名单（每个代理）

白名单是 **每个代理** 的。如果存在多个代理，请在 macOS 应用程序中切换正在编辑的代理。模式是 **不区分大小写的通配符匹配**。
模式应解析为 **二进制路径**（仅基于名称的条目将被忽略）。
旧版 `agents.default` 条目在加载时迁移到 `agents.main`。

示例：

- `~/Projects/**/bin/peekaboo`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

每个白名单条目跟踪：

- **id** 用于 UI 标识的稳定 UUID（可选）
- **最后使用时间戳**
- **最后使用的命令**
- **最后解析的路径**

## 自动允许技能 CLI

当启用 **自动允许技能 CLI** 时，由已知技能引用的可执行文件被视为节点上的白名单（macOS 节点或无头节点主机）。这使用 `skills.bins` 通过网关 RPC 获取技能二进制列表。如果您希望严格的手动白名单，请禁用此功能。

## 安全二进制（仅限 stdin）

`tools.exec.safeBins` 定义了一个小的 **仅限 stdin** 的二进制文件列表（例如 `jq`）
可以在白名单模式下 **无需** 显式白名单条目运行。安全二进制文件拒绝位置文件参数和路径样式的令牌，因此它们只能对传入流进行操作。
验证仅从 argv 形状确定（没有主机文件系统存在性检查），这防止了由于允许/拒绝差异导致的文件存在性预言行为。
默认安全二进制文件拒绝文件导向的选项（例如 `sort -o`，`sort --output`，
`sort --files0-from`，`sort --compress-program`，`wc --files0-from`，`jq -f/--from-file`，
`grep -f/--file`）。
安全二进制文件还强制对破坏仅限 stdin 行为的选项进行显式按二进制标志策略（例如 `sort -o/--output/--compress-program` 和 grep 递归标志）。
被安全二进制配置文件拒绝的标志：

<!-- SAFE_BIN_DENIED_FLAGS:START -->

- `grep`: `--dereference-recursive`，`--directories`，`--exclude-from`，`--file`，`--recursive`，`-R`，`-d`，`-f`，`-r`
- `jq`: `--argfile`，`--from-file`，`--library-path`，`--rawfile`，`--slurpfile`，`-L`，`-f`
- `sort`: `--compress-program`，`--files0-from`，`--output`，`-o`
- `wc`: `--files0-from`
<!-- SAFE_BIN_DENIED_FLAGS:END -->

安全二进制文件还会强制在执行时将 argv 令牌视为 **字面文本**（不进行通配符和 `$VARS` 展开）对于仅限 stdin 段落，因此像 `*` 或 `$HOME/...` 这样的模式不能用于走私文件读取。
安全二进制文件还必须从受信任的二进制目录解析（系统默认值加上网关进程 `PATH` 启动时）。这阻止了请求范围内的 PATH 劫持尝试。
在白名单模式下，不允许自动允许 shell 链接和重定向。

shell 链接 (`&&`，`||`，`;`) 在每个顶级段满足白名单时允许（包括安全二进制文件或技能自动允许）。重定向在白名单模式下仍然不受支持。
命令替换 (`$()` / 反引号) 在白名单解析期间被拒绝，包括在双引号内；如果需要字面 `$()` 文本，请使用单引号。
在 macOS 配套应用程序审批中，包含 shell 控制或扩展语法的原始 shell 文本（`&&`，`||`，`;`，`|`，`` ` ``, `$`, `<`, `>`, `(`, `)`) is treated as an allowlist miss unless
the shell binary itself is allowlisted.

Default safe bins: `jq`, `cut`, `uniq`, `head`, `tail`, `tr`, `wc`.

`grep` and `sort` are not in the default list. If you opt in, keep explicit allowlist entries for
their non-stdin workflows.
For `grep` in safe-bin mode, provide the pattern with `-e`/`--regexp`; positional pattern form is
rejected so file operands cannot be smuggled as ambiguous positionals.

## Control UI editing

Use the **Control UI → Nodes → Exec approvals** card to edit defaults, per‑agent
overrides, and allowlists. Pick a scope (Defaults or an agent), tweak the policy,
add/remove allowlist patterns, then **Save**. The UI shows **last used** metadata
per pattern so you can keep the list tidy.

The target selector chooses **Gateway** (local approvals) or a **Node**. Nodes
must advertise `system.execApprovals.get/set` (macOS app or headless node host).
If a node does not advertise exec approvals yet, edit its local
`~/.openclaw/exec-approvals.json` directly.

CLI: `openclaw approvals` supports gateway or node editing (see [Approvals CLI](/cli/approvals)).

## Approval flow

When a prompt is required, the gateway broadcasts `exec.approval.requested` to operator clients.
The Control UI and macOS app resolve it via `exec.approval.resolve`, then the gateway forwards the
approved request to the node host.

When approvals are required, the exec tool returns immediately with an approval id. Use that id to
correlate later system events (`Exec finished` / `Exec denied`). If no decision arrives before the
timeout, the request is treated as an approval timeout and surfaced as a denial reason.

The confirmation dialog includes:

- command + args
- cwd
- agent id
- resolved executable path
- host + policy metadata

Actions:

- **Allow once** → run now
- **Always allow** → add to allowlist + run
- **Deny** → block

## Approval forwarding to chat channels

You can forward exec approval prompts to any chat channel (including plugin channels) and approve
them with `/approve`. This uses the normal outbound delivery pipeline.

Config:

```json5
{
  approvals: {
    exec: {
      enabled: true,
      mode: "session", // "session" | "targets" | "both"
      agentFilter: ["main"],
      sessionFilter: ["discord"], // 子字符串或正则表达式
      targets: [
        { channel: "slack", to: "U12345678" },
        { channel: "telegram", to: "123456789" },
      ],
    },
  },
}
```

Reply in chat:

```
/approve <id> allow-once
/approve <id> allow-always
/approve <id> deny
```

### macOS IPC flow

```
网关 -> 节点服务 (WS)
                 |  IPC (UDS + token + HMAC + TTL)
                 v
             Mac 应用程序 (UI + 审批 + system.run)
```

Security notes:

- Unix socket mode `0600`, token stored in `exec-approvals.json`.
- Same-UID peer check.
- Challenge/response (nonce + HMAC token + request hash) + short TTL.

## System events

Exec lifecycle is surfaced as system messages:

- `Exec 正在运行` (only if the command exceeds the running notice threshold)
- `Exec 完成`
- `Exec 被拒绝`

These are posted to the agent’s session after the node reports the event.
Gateway-host exec approvals emit the same lifecycle events when the command finishes (and optionally when running longer than the threshold).
Approval-gated execs reuse the approval id as the `runId` in these messages for easy correlation.

## Implications

- **full** is powerful; prefer allowlists when possible.
- **ask** keeps you in the loop while still allowing fast approvals.
- Per-agent allowlists prevent one agent’s approvals from leaking into others.
- Approvals only apply to host exec requests from **authorized senders**. Unauthorized senders cannot issue `/exec`.
- `/exec security=full` is a session-level convenience for authorized operators and skips approvals by design.
  To hard-block host exec, set approvals security to `deny` or deny the `通过工具策略 `exec` 工具。

相关：

- [Exec 工具](/tools/exec)
- [提升模式](/tools/elevated)
- [技能](/tools/skills)