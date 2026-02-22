---
summary: "Legacy iMessage support via imsg (JSON-RPC over stdio). New setups should use BlueBubbles."
read_when:
  - Setting up iMessage support
  - Debugging iMessage send/receive
title: "iMessage"
---
# iMessage (legacy: imsg)

<Warning>
For new iMessage deployments, use <a href="/channels/bluebubbles">BlueBubbles</a>.

The __CODE_BLOCK_0__ integration is legacy and may be removed in a future release.
</Warning>

状态: 旧版外部CLI集成。网关生成 `imsg rpc` 并通过stdio上的JSON-RPC进行通信（没有单独的守护进程/端口）。

<CardGroup cols={3}>
  <Card title="BlueBubbles（推荐）" icon="message-circle" href="/channels/bluebubbles">
    新安装的首选iMessage路径。
  </Card>
  <Card title="配对" icon="link" href="/channels/pairing">
    iMessage私信默认为配对模式。
  </Card>
  <Card title="配置参考" icon="settings" href="/gateway/configuration-reference#imessage">
    完整的iMessage字段参考。
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

## 要求和权限（macOS）

- 消息必须在运行 `imsg` 的 Mac 上签名。
- 进程上下文运行 OpenClaw/`imsg`（消息数据库访问）需要完全磁盘访问权限。
- 自动化权限是通过 Messages.app 发送消息所必需的。

<Tip>
Permissions are granted per process context. If gateway runs headless (LaunchAgent/SSH), run a one-time interactive command in that same context to trigger prompts:

__CODE_BLOCK_2__

</Tip>

## 访问控制和路由

<Tabs>
  <Tab title="DM policy">
    __CODE_BLOCK_3__ controls direct messages:

    - __CODE_BLOCK_4__ (default)
    - __CODE_BLOCK_5__
    - __CODE_BLOCK_6__ (requires __CODE_BLOCK_7__ to include __CODE_BLOCK_8__)
    - __CODE_BLOCK_9__

    Allowlist field: __CODE_BLOCK_10__.

    Allowlist entries can be handles or chat targets (__CODE_BLOCK_11__, __CODE_BLOCK_12__, __CODE_BLOCK_13__).

  </Tab>

  <Tab title="Group policy + mentions">
    __CODE_BLOCK_14__ controls group handling:

    - __CODE_BLOCK_15__ (default when configured)
    - __CODE_BLOCK_16__
    - __CODE_BLOCK_17__

    Group sender allowlist: __CODE_BLOCK_18__.

    Runtime fallback: if __CODE_BLOCK_19__ is unset, iMessage group sender checks fall back to __CODE_BLOCK_20__ when available.

    Mention gating for groups:

    - iMessage has no native mention metadata
    - mention detection uses regex patterns (__CODE_BLOCK_21__, fallback __CODE_BLOCK_22__)
    - with no configured patterns, mention gating cannot be enforced

    Control commands from authorized senders can bypass mention gating in groups.

  </Tab>

  <Tab title="Sessions and deterministic replies">
    - DMs use direct routing; groups use group routing.
    - With default __CODE_BLOCK_23__, iMessage DMs collapse into the agent main session.
    - Group sessions are isolated (__CODE_BLOCK_24__).
    - Replies route back to iMessage using originating channel/target metadata.

    Group-ish thread behavior:

    Some multi-participant iMessage threads can arrive with __CODE_BLOCK_25__.
    If that __CODE_BLOCK_26__ is explicitly configured under __CODE_BLOCK_27__, OpenClaw treats it as group traffic (group gating + group session isolation).

  </Tab>
</Tabs>

## 部署模式

<AccordionGroup>
  <Accordion title="专用机器人 macOS 用户（单独的 iMessage 身份）">
    使用专用的 Apple ID 和 macOS 用户，使机器人的流量与您的个人消息配置文件隔离。

    典型流程：

    1. 创建/登录一个专用的 macOS 用户。
    2. 在该用户中使用机器人的 Apple ID 登录 Messages。
    3. 在该用户中安装 `imsg`。
    4. 创建 SSH 包装器，以便 OpenClaw 可以在该用户上下文中运行 `imsg`。
    5. 将 `channels.imessage.accounts.<id>.cliPath` 和 `.dbPath` 指向该用户配置文件。

    第一次运行可能需要在该机器人用户会话中进行 GUI 批准（自动化 + 完全磁盘访问）。

  </Accordion>

<Accordion title="通过Tailscale远程访问Mac（示例）">
    常见拓扑结构：

    - 网关运行在Linux/VM上
    - iMessage + `imsg` 运行在您tailnet中的Mac上
    - `cliPath` 包装器使用SSH来运行 `imsg`
    - `remoteHost` 启用SCP附件获取

    示例：

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "~/.openclaw/scripts/imsg-ssh",
      remoteHost: "bot@mac-mini.tailnet-1234.ts.net",
      includeAttachments: true,
      dbPath: "/Users/bot/Library/Messages/chat.db",
    },
  },
}
```

```bash
#!/usr/bin/env bash
exec ssh -T bot@mac-mini.tailnet-1234.ts.net imsg "$@"
```

    使用SSH密钥使SSH和SCP均为非交互式。
    首先确保主机密钥受信任（例如 `ssh bot@mac-mini.tailnet-1234.ts.net`），以便 `known_hosts` 被填充。

  </Accordion>

  <Accordion title="多账户模式">
    iMessage支持在 `channels.imessage.accounts` 下进行每个账户的配置。

    每个账户可以覆盖字段，例如 `cliPath`，`dbPath`，`allowFrom`，`groupPolicy`，`mediaMaxMb`，历史记录设置以及附件根允许列表。

  </Accordion>
</AccordionGroup>

## 媒体、分块和交付目标

<AccordionGroup>
  <Accordion title="Attachments and media">
    - inbound attachment ingestion is optional: __CODE_BLOCK_14__
    - remote attachment paths can be fetched via SCP when __CODE_BLOCK_15__ is set
    - attachment paths must match allowed roots:
      - __CODE_BLOCK_16__ (local)
      - __CODE_BLOCK_17__ (remote SCP mode)
      - default root pattern: __CODE_BLOCK_18__
    - SCP uses strict host-key checking (__CODE_BLOCK_19__)
    - outbound media size uses __CODE_BLOCK_20__ (default 16 MB)
  </Accordion>

  <Accordion title="Outbound chunking">
    - text chunk limit: __CODE_BLOCK_21__ (default 4000)
    - chunk mode: __CODE_BLOCK_22__
      - __CODE_BLOCK_23__ (default)
      - __CODE_BLOCK_24__ (paragraph-first splitting)
  </Accordion>

  <Accordion title="Addressing formats">
    Preferred explicit targets:

    - __CODE_BLOCK_25__ (recommended for stable routing)
    - __CODE_BLOCK_26__
    - __CODE_BLOCK_27__

    Handle targets are also supported:

    - __CODE_BLOCK_28__
    - __CODE_BLOCK_29__
    - __CODE_BLOCK_30__

__CODE_BLOCK_31__

  </Accordion>
</AccordionGroup>

## 配置写入

iMessage默认允许由通道发起的配置写入（对于 `/config set|unset` 当 `commands.config: true`）。

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

<AccordionGroup>
  <Accordion title="未找到imsg或RPC不受支持">
    验证二进制文件和RPC支持：

```bash
imsg rpc --help
openclaw channels status --probe
```

    如果探测报告RPC不受支持，请更新 `imsg`。

  </Accordion>

  <Accordion title="忽略DM">
    检查：

- `channels.imessage.dmPolicy`
- `channels.imessage.allowFrom`
- pairing approvals (`openclaw pairing list imessage`)

  </Accordion>

  <Accordion title="群组消息被忽略">
    检查：

    - `channels.imessage.groupPolicy`
    - `channels.imessage.groupAllowFrom`
    - `channels.imessage.groups` 允许列表行为
    - 提及模式配置 (`agents.list[].groupChat.mentionPatterns`)

  </Accordion>

  <Accordion title="远程附件失败">
    检查：

    - `channels.imessage.remoteHost`
    - `channels.imessage.remoteAttachmentRoots`
    - 网关主机上的SSH/SCP密钥认证
    - 网关主机上的 `~/.ssh/known_hosts` 中存在主机密钥
    - 运行Messages的Mac上的远程路径可读性

  </Accordion>

  <Accordion title="macOS权限提示被错过">
    在相同的用户/会话上下文中重新运行交互式GUI终端并批准提示：

```bash
imsg chats --limit 1
imsg send <handle> "test"
```

    确认OpenClaw/`imsg` 的进程上下文已授予完全磁盘访问和自动化权限。

  </Accordion>
</AccordionGroup>

## 配置参考指针

- [配置参考 - iMessage](/gateway/configuration-reference#imessage)
- [网关配置](/gateway/configuration)
- [配对](/channels/pairing)
- [BlueBubbles](/channels/bluebubbles)