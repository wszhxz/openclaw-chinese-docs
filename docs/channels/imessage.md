---
summary: "Legacy iMessage support via imsg (JSON-RPC over stdio). New setups should use BlueBubbles."
read_when:
  - Setting up iMessage support
  - Debugging iMessage send/receive
title: "iMessage"
---
# iMessage（旧版：imsg）

<Warning>
For new iMessage deployments, use <a href="/channels/bluebubbles">BlueBubbles</a>.

The __CODE_BLOCK_0__ integration is legacy and may be removed in a future release.
</Warning>

状态：已归档的外部 CLI 集成。网关启动 `imsg rpc`，并通过标准输入输出（stdio）上的 JSON-RPC 进行通信（无需单独的守护进程或端口）。

<CardGroup cols={3}>
  <Card title="BlueBubbles（推荐）" icon="message-circle" href="/channels/bluebubbles">
    新部署环境首选的 iMessage 通道路径。
  </Card>
  <Card title="配对" icon="link" href="/channels/pairing">
    iMessage 私信默认启用配对模式。
  </Card>
  <Card title="配置参考" icon="settings" href="/gateway/configuration-reference#imessage">
    完整的 iMessage 字段参考文档。
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

## 要求与权限（macOS）

- 运行 `imsg` 的 Mac 必须已使用 Apple ID 登录“信息”应用。
- 运行 OpenClaw/`imsg` 的进程上下文需获得“完全磁盘访问”权限（用于访问信息数据库）。
- 需授予“自动化”权限，以便通过 Messages.app 发送消息。

<Tip>
Permissions are granted per process context. If gateway runs headless (LaunchAgent/SSH), run a one-time interactive command in that same context to trigger prompts:

__CODE_BLOCK_20__

</Tip>

## 访问控制与路由

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

## 部署模式

<AccordionGroup>
  <Accordion title="Dedicated bot macOS user (separate iMessage identity)">
    Use a dedicated Apple ID and macOS user so bot traffic is isolated from your personal Messages profile.

    Typical flow:

    1. Create/sign in a dedicated macOS user.
    2. Sign into Messages with the bot Apple ID in that user.
    3. Install __CODE_BLOCK_49__ in that user.
    4. Create SSH wrapper so OpenClaw can run __CODE_BLOCK_50__ in that user context.
    5. Point __CODE_BLOCK_51__ and __CODE_BLOCK_52__ to that user profile.

    First run may require GUI approvals (Automation + Full Disk Access) in that bot user session.

  </Accordion>

  <Accordion title="Remote Mac over Tailscale (example)">
    Common topology:

    - gateway runs on Linux/VM
    - iMessage + __CODE_BLOCK_53__ runs on a Mac in your tailnet
    - __CODE_BLOCK_54__ wrapper uses SSH to run __CODE_BLOCK_55__
    - __CODE_BLOCK_56__ enables SCP attachment fetches

    Example:

__CODE_BLOCK_57__

__CODE_BLOCK_58__

    Use SSH keys so both SSH and SCP are non-interactive.
    Ensure the host key is trusted first (for example __CODE_BLOCK_59__) so __CODE_BLOCK_60__ is populated.

  </Accordion>

  <Accordion title="Multi-account pattern">
    iMessage supports per-account config under __CODE_BLOCK_61__.

    Each account can override fields such as __CODE_BLOCK_62__, __CODE_BLOCK_63__, __CODE_BLOCK_64__, __CODE_BLOCK_65__, __CODE_BLOCK_66__, history settings, and attachment root allowlists.

  </Accordion>
</AccordionGroup>

## 媒体、分块与投递目标

<AccordionGroup>
  <Accordion title="Attachments and media">
    - inbound attachment ingestion is optional: __CODE_BLOCK_67__
    - remote attachment paths can be fetched via SCP when __CODE_BLOCK_68__ is set
    - attachment paths must match allowed roots:
      - __CODE_BLOCK_69__ (local)
      - __CODE_BLOCK_70__ (remote SCP mode)
      - default root pattern: __CODE_BLOCK_71__
    - SCP uses strict host-key checking (__CODE_BLOCK_72__)
    - outbound media size uses __CODE_BLOCK_73__ (default 16 MB)
  </Accordion>

  <Accordion title="Outbound chunking">
    - text chunk limit: __CODE_BLOCK_74__ (default 4000)
    - chunk mode: __CODE_BLOCK_75__
      - __CODE_BLOCK_76__ (default)
      - __CODE_BLOCK_77__ (paragraph-first splitting)
  </Accordion>

  <Accordion title="Addressing formats">
    Preferred explicit targets:

    - __CODE_BLOCK_78__ (recommended for stable routing)
    - __CODE_BLOCK_79__
    - __CODE_BLOCK_80__

    Handle targets are also supported:

    - __CODE_BLOCK_81__
    - __CODE_BLOCK_82__
    - __CODE_BLOCK_83__

__CODE_BLOCK_84__

  </Accordion>
</AccordionGroup>

## 配置写入

iMessage 默认允许通道发起的配置写入（适用于 `/config set|unset`，当 `commands.config: true` 时）。

禁用方法：

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
  <Accordion title="未找到 imsg 或不支持 RPC">
    验证二进制文件及 RPC 支持情况：

```bash
imsg rpc --help
openclaw channels status --probe
```

    若 probe 报告不支持 RPC，请更新 `imsg`。

  </Accordion>

  <Accordion title="私信被忽略">
    检查以下项：

    - `channels.imessage.dmPolicy`
    - `channels.imessage.allowFrom`
    - 配对授权（`openclaw pairing list imessage`）

  </Accordion>

  <Accordion title="群组消息被忽略">
    检查以下项：

    - `channels.imessage.groupPolicy`
    - `channels.imessage.groupAllowFrom`
    - `channels.imessage.groups` 白名单行为
    - 提及模式配置（`agents.list[].groupChat.mentionPatterns`）

  </Accordion>

  <Accordion title="远程附件上传失败">
    检查以下项：

    - `channels.imessage.remoteHost`
    - `channels.imessage.remoteAttachmentRoots`
    - 网关主机上 SSH/SCP 的密钥认证
    - 网关主机的 `~/.ssh/known_hosts` 中是否存在对应主机密钥
    - 运行“信息”应用的 Mac 上远程路径是否可读

  </Accordion>

  <Accordion title="遗漏了 macOS 权限提示">
    在相同用户/会话上下文中，于交互式 GUI 终端中重新运行，并批准所有弹出提示：

```bash
imsg chats --limit 1
imsg send <handle> "test"
```

    确认已为运行 OpenClaw/`imsg` 的进程上下文授予“完全磁盘访问”和“自动化”权限。

</Accordion>
</AccordionGroup>

## 配置参考链接

- [配置参考 - iMessage](/gateway/configuration-reference#imessage)
- [网关配置](/gateway/configuration)
- [配对](/channels/pairing)
- [BlueBubbles](/channels/bluebubbles)