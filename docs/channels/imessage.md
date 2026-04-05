---
summary: "Legacy iMessage support via imsg (JSON-RPC over stdio). New setups should use BlueBubbles."
read_when:
  - Setting up iMessage support
  - Debugging iMessage send/receive
title: "iMessage"
---
# iMessage (旧版：imsg)

<Warning>
For new iMessage deployments, use <a href="/channels/bluebubbles">BlueBubbles</a>.

The __CODE_BLOCK_0__ integration is legacy and may be removed in a future release.
</Warning>

状态：旧版外部 CLI 集成。Gateway 启动 `imsg rpc` 并通过 stdio 上的 JSON-RPC 进行通信（无独立守护进程/端口）。

<CardGroup cols={3}>
  <Card title="BlueBubbles (推荐)" icon="message-circle" href="/channels/bluebubbles">
    新部署的首选 iMessage 路径。
  </Card>
  <Card title="配对" icon="link" href="/channels/pairing">
    iMessage DMs 默认为配对模式。
  </Card>
  <Card title="配置参考" icon="settings" href="/gateway/configuration-reference#imessage">
    完整的 iMessage 字段参考。
  </Card>
</CardGroup>

## 快速设置

<Tabs>
  <Tab title="Local Mac (fast path)">
    <Steps>
      <Step title="Install and verify imsg">

__CODE_BLOCK_2__

      </Step>

      <Step title="Configure OpenClaw">

__CODE_BLOCK_3__

      </Step>

      <Step title="Start gateway">

__CODE_BLOCK_4__

      </Step>

      <Step title="Approve first DM pairing (default dmPolicy)">

__CODE_BLOCK_5__

        Pairing requests expire after 1 hour.
      </Step>
    </Steps>

  </Tab>

  <Tab title="Remote Mac over SSH">
    OpenClaw only requires a stdio-compatible __CODE_BLOCK_6__, so you can point __CODE_BLOCK_7__ at a wrapper script that SSHes to a remote Mac and runs __CODE_BLOCK_8__.

__CODE_BLOCK_9__

    Recommended config when attachments are enabled:

__CODE_BLOCK_10__

    If __CODE_BLOCK_11__ is not set, OpenClaw attempts to auto-detect it by parsing the SSH wrapper script.
    __CODE_BLOCK_12__ must be __CODE_BLOCK_13__ or __CODE_BLOCK_14__ (no spaces or SSH options).
    OpenClaw uses strict host-key checking for SCP, so the relay host key must already exist in __CODE_BLOCK_15__.
    Attachment paths are validated against allowed roots (__CODE_BLOCK_16__ / __CODE_BLOCK_17__).

  </Tab>
</Tabs>

## 要求和权限 (macOS)

- 必须在运行 `imsg` 的 Mac 上登录 Messages。
- 运行 OpenClaw/`imsg` 的进程上下文需要“完全磁盘访问”权限（用于访问 Messages 数据库）。
- 需要通过 Messages.app 发送消息的自动化权限。

<Tip>
Permissions are granted per process context. If gateway runs headless (LaunchAgent/SSH), run a one-time interactive command in that same context to trigger prompts:

__CODE_BLOCK_20__

</Tip>

## 访问控制和路由

<Tabs>
  <Tab title="DM policy">
    __CODE_BLOCK_21__ controls direct messages:

    - __CODE_BLOCK_22__ (default)
    - __CODE_BLOCK_23__
    - __CODE_BLOCK_24__ (requires __CODE_BLOCK_25__ to include __CODE_BLOCK_26__)
    - __CODE_BLOCK_27__

    Allowlist field: __CODE_BLOCK_28__.

    Allowlist entries can be handles or chat targets (__CODE_BLOCK_29__, __CODE_BLOCK_30__, __CODE_BLOCK_31__).

  </Tab>

  <Tab title="Group policy + mentions">
    __CODE_BLOCK_32__ controls group handling:

    - __CODE_BLOCK_33__ (default when configured)
    - __CODE_BLOCK_34__
    - __CODE_BLOCK_35__

    Group sender allowlist: __CODE_BLOCK_36__.

    Runtime fallback: if __CODE_BLOCK_37__ is unset, iMessage group sender checks fall back to __CODE_BLOCK_38__ when available.
    Runtime note: if __CODE_BLOCK_39__ is completely missing, runtime falls back to __CODE_BLOCK_40__ and logs a warning (even if __CODE_BLOCK_41__ is set).

    Mention gating for groups:

    - iMessage has no native mention metadata
    - mention detection uses regex patterns (__CODE_BLOCK_42__, fallback __CODE_BLOCK_43__)
    - with no configured patterns, mention gating cannot be enforced

    Control commands from authorized senders can bypass mention gating in groups.

  </Tab>

  <Tab title="Sessions and deterministic replies">
    - DMs use direct routing; groups use group routing.
    - With default __CODE_BLOCK_44__, iMessage DMs collapse into the agent main session.
    - Group sessions are isolated (__CODE_BLOCK_45__).
    - Replies route back to iMessage using originating channel/target metadata.

    Group-ish thread behavior:

    Some multi-participant iMessage threads can arrive with __CODE_BLOCK_46__.
    If that __CODE_BLOCK_47__ is explicitly configured under __CODE_BLOCK_48__, OpenClaw treats it as group traffic (group gating + group session isolation).

  </Tab>
</Tabs>

## ACP 会话绑定

旧版 iMessage 聊天也可以绑定到 ACP 会话。

快速操作流程：

- 在 DM 或允许的群聊中运行 `/acp spawn codex --bind here`。
- 该 iMessage 对话中的后续消息将路由到生成的 ACP 会话。
- `/new` 和 `/reset` 会就地重置相同的绑定 ACP 会话。
- `/acp close` 关闭 ACP 会话并移除绑定。

通过顶层 `bindings[]` 条目支持配置的持久化绑定，包含 `type: "acp"` 和 `match.channel: "imessage"`。

`match.peer.id` 可以使用：

- 标准化的 DM 句柄，例如 `+15555550123` 或 `user@example.com`
- `chat_id:<id>` （推荐用于稳定的群组绑定）
- `chat_guid:<guid>`
- `chat_identifier:<identifier>`

示例：

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: { agent: "codex", backend: "acpx", mode: "persistent" },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "imessage",
        accountId: "default",
        peer: { kind: "group", id: "chat_id:123" },
      },
      acp: { label: "codex-group" },
    },
  ],
}
```

有关共享 ACP 绑定行为，请参阅 [ACP Agents](/tools/acp-agents)。

## 部署模式

<AccordionGroup>
  <Accordion title="Dedicated bot macOS user (separate iMessage identity)">
    Use a dedicated Apple ID and macOS user so bot traffic is isolated from your personal Messages profile.

    Typical flow:

    1. Create/sign in a dedicated macOS user.
    2. Sign into Messages with the bot Apple ID in that user.
    3. Install __CODE_BLOCK_63__ in that user.
    4. Create SSH wrapper so OpenClaw can run __CODE_BLOCK_64__ in that user context.
    5. Point __CODE_BLOCK_65__ and __CODE_BLOCK_66__ to that user profile.

    First run may require GUI approvals (Automation + Full Disk Access) in that bot user session.

  </Accordion>

  <Accordion title="Remote Mac over Tailscale (example)">
    Common topology:

    - gateway runs on Linux/VM
    - iMessage + __CODE_BLOCK_67__ runs on a Mac in your tailnet
    - __CODE_BLOCK_68__ wrapper uses SSH to run __CODE_BLOCK_69__
    - __CODE_BLOCK_70__ enables SCP attachment fetches

    Example:

__CODE_BLOCK_71__

__CODE_BLOCK_72__

    Use SSH keys so both SSH and SCP are non-interactive.
    Ensure the host key is trusted first (for example __CODE_BLOCK_73__) so __CODE_BLOCK_74__ is populated.

  </Accordion>

  <Accordion title="Multi-account pattern">
    iMessage supports per-account config under __CODE_BLOCK_75__.

    Each account can override fields such as __CODE_BLOCK_76__, __CODE_BLOCK_77__, __CODE_BLOCK_78__, __CODE_BLOCK_79__, __CODE_BLOCK_80__, history settings, and attachment root allowlists.

  </Accordion>
</AccordionGroup>

## 媒体、分块和投递目标

<AccordionGroup>
  <Accordion title="Attachments and media">
    - inbound attachment ingestion is optional: __CODE_BLOCK_81__
    - remote attachment paths can be fetched via SCP when __CODE_BLOCK_82__ is set
    - attachment paths must match allowed roots:
      - __CODE_BLOCK_83__ (local)
      - __CODE_BLOCK_84__ (remote SCP mode)
      - default root pattern: __CODE_BLOCK_85__
    - SCP uses strict host-key checking (__CODE_BLOCK_86__)
    - outbound media size uses __CODE_BLOCK_87__ (default 16 MB)
  </Accordion>

  <Accordion title="Outbound chunking">
    - text chunk limit: __CODE_BLOCK_88__ (default 4000)
    - chunk mode: __CODE_BLOCK_89__
      - __CODE_BLOCK_90__ (default)
      - __CODE_BLOCK_91__ (paragraph-first splitting)
  </Accordion>

  <Accordion title="Addressing formats">
    Preferred explicit targets:

    - __CODE_BLOCK_92__ (recommended for stable routing)
    - __CODE_BLOCK_93__
    - __CODE_BLOCK_94__

    Handle targets are also supported:

    - __CODE_BLOCK_95__
    - __CODE_BLOCK_96__
    - __CODE_BLOCK_97__

__CODE_BLOCK_98__

  </Accordion>
</AccordionGroup>

## 配置写入

iMessage 默认允许通道发起的配置写入（当 `commands.config: true` 时针对 `/config set|unset`）。

禁用：

```json5
{
  channels: {
    imessage: {
      configWrites: false,
    },
  },
}
```

## 故障排除

<Accordion title="未找到 imsg 或 RPC 不支持">
    验证二进制文件和 RPC 支持：

```bash
imsg rpc --help
openclaw channels status --probe
```

    如果探针报告 RPC 不支持，请更新 `imsg`。

  </Accordion>

  <Accordion title="私聊消息被忽略">
    检查：

    - `channels.imessage.dmPolicy`
    - `channels.imessage.allowFrom`
    - 配对批准 (`openclaw pairing list imessage`)

  </Accordion>

  <Accordion title="群消息被忽略">
    检查：

    - `channels.imessage.groupPolicy`
    - `channels.imessage.groupAllowFrom`
    - `channels.imessage.groups` 白名单行为
    - 提及模式配置 (`agents.list[].groupChat.mentionPatterns`)

  </Accordion>

  <Accordion title="远程附件失败">
    检查：

    - `channels.imessage.remoteHost`
    - `channels.imessage.remoteAttachmentRoots`
    - 来自网关主机的 SSH/SCP 密钥认证
    - 主机密钥存在于网关主机上的 `~/.ssh/known_hosts` 中
    - 运行 Messages 的 Mac 上的远程路径可读性

  </Accordion>

  <Accordion title="错过了 macOS 权限提示">
    在相同的用户/会话上下文中，于交互式 GUI 终端重新运行并批准提示：

```bash
imsg chats --limit 1
imsg send <handle> "test"
```

    确认已为运行 OpenClaw/`imsg` 的进程上下文授予了全盘访问权限 + 自动化权限。

  </Accordion>
</AccordionGroup>

## 配置参考链接

- [配置参考 - iMessage](/gateway/configuration-reference#imessage)
- [网关配置](/gateway/configuration)
- [配对](/channels/pairing)
- [BlueBubbles](/channels/bluebubbles)

## 相关

- [频道概览](/channels) — 所有支持的频道
- [配对](/channels/pairing) — 私聊身份验证和配对流程
- [群组](/channels/groups) — 群聊行为和提及管控
- [频道路由](/channels/channel-routing) — 消息的会话路由
- [安全](/gateway/security) — 访问模型和加固