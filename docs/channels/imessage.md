---
summary: "iMessage support via imsg (JSON-RPC over stdio), setup, and chat_id routing"
read_when:
  - Setting up iMessage support
  - Debugging iMessage send/receive
title: iMessage
---
Okay, I need to translate this technical document about iMessage integration into Chinese. Let me start by reading through the entire text to understand the context and the specific terms used. The document includes sections like setup instructions, configuration details, and various options for different scenarios. 

First, I'll go through each section and identify key terms that need accurate translation. For example, "CLI integration" should be "命令行界面集成". Technical terms like "JSON-RPC" are usually kept in English but might need a brief explanation. Terms like "Full Disk Access" should be translated as "完全磁盘访问权限".

I need to be careful with the structure, ensuring that headings and subheadings are correctly translated. For instance, "Quick setup (beginner)" becomes "快速设置（初学者）". Also, code blocks and JSON configurations should remain in their original format but with the comments and keys translated appropriately.

Some parts mention specific commands like `brew install` or `imsg rpc`, which are technical commands and should stay in English. However, the surrounding text explaining these commands needs to be in Chinese. For example, "Install `imsg`:" becomes "安装 `imsg`:".

I should also pay attention to the examples provided, such as the wrapper script and configuration files. Ensuring that the syntax and structure are preserved while translating the explanatory text is crucial. For instance, the example wrapper script's comments and the JSON configuration keys need to be translated without altering their format.

Another important aspect is handling the specific terminology related to macOS features, like "Remote Login" which translates to "远程登录", and "Automation permission" as "自动化权限". These terms are specific to the operating system and should be accurately translated to maintain the document's technical accuracy.

The document also includes notes about security and access control, such as "Ensure the Mac is signed in to Messages, and Remote Login is enabled." Here, "signed in" should be translated to "已登录" and "Remote Login" to "远程登录".

I need to make sure that all the configuration options and their descriptions are correctly translated. For example, "channels.imessage.dmPolicy" becomes "channels.imessage.dmPolicy" (keeping the key names in English) but the explanation in Chinese. Similarly, "groupPolicy" should be translated as "群组策略".

There are also mentions of specific features like "Pairing" which is a term used in iMessage for establishing a connection, so it's best to keep it as "配对" or use the term that's commonly understood in Chinese technical contexts.

I'll also check for consistency in terminology throughout the document. For instance, if "Full Disk Access" is translated once, it should be used consistently in all instances. Additionally, ensuring that the translation of technical terms like "attachment" is correctly rendered as "附件" and "media" as "媒体".

Finally, I'll review the entire translated text to ensure that the flow and structure are maintained, and that all technical details are accurately conveyed in Chinese without any grammatical errors or mistranslations. This includes verifying that code examples and JSON configurations are correctly formatted and that the explanations are clear and precise.
</think>

# iMessage（imsg）

状态：外部命令行界面（CLI）集成。网关会启动 `imsg rpc`（通过标准输入输出的 JSON-RPC）。

## 快速设置（初学者）

1. 确保此 Mac 上的 Messages 已登录。
2. 安装 `imsg`：
   - `brew install steipete/tap/imsg`
3. 使用 `channels.imessage.cliPath` 和 `channels.imessage.dbPath` 配置 OpenClaw。
4. 启动网关并批准任何 macOS 提示（自动化 + 完全磁盘访问权限）。

最小配置：

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "/usr/local/bin/imsg",
      dbPath: "/Users/<you>/Library/Messages/chat.db",
    },
  },
}
```

## 它是什么

- 由 `imsg` 支持的 macOS iMessage 通道。
- 确定性路由：回复始终返回到 iMessage。
- 单聊共享代理的主会话；群组是隔离的（`agent:<agentId>:imessage:group:<chat_id>`）。
- 如果多参与者线程到达且 `is_group=false`，您仍可通过 `channels.imessage.groups` 使用 `chat_id` 隔离它（见下方“类似群组的线程”部分）。

## 配置写入

默认情况下，iMessage 允许通过 `/config set|unset` 触发的配置更新（需要 `commands.config: true`）。

禁用：

```json5
{
  channels: { imessage: { configWrites: false } },
}
```

## 要求

- 已登录 Messages 的 macOS。
- OpenClaw + `imsg` 的完全磁盘访问权限（Messages 数据库访问）。
- 发送时的自动化权限。
- `channels.imessage.cliPath` 可指向任何代理 stdin/stdout 的命令（例如，通过 SSH 连接到另一台 Mac 并运行 `imsg rpc` 的包装脚本）。

## 设置（快速路径）

1. 确保此 Mac 上的 Messages 已登录。
2. 配置 iMessage 并启动网关。

### 专用机器人 macOS 用户（用于隔离身份）

如果您希望机器人从 **独立的 iMessage 身份** 发送消息（并保持个人 Messages 的干净），请使用专用 Apple ID + 专用 macOS 用户。

1. 创建专用 Apple ID（示例：`my-cool-bot@icloud.com`）。
   - Apple 可能需要电话号码进行验证 / 2FA。
2. 创建 macOS 用户（示例：`openclawhome`）并登录。
3. 在该 macOS 用户中打开 Messages 并使用机器人 Apple ID 登录 iMessage。
4. 启用远程登录（系统设置 → 通用 → 共享 → 远程登录）。
5. 安装 `imsg`：
   - `brew install steipete/tap/imsg`
6. 设置 SSH 使 `ssh <bot-macos-user>@localhost true` 无需密码即可运行。
7. 将 `channels.imessage.accounts.bot.cliPath` 指向机器人包装脚本。

首次运行时，机器人会自动下载并安装所需依赖项。

## 介质 + 限制

- 通过 `channels.imessage.includeAttachments` 选择性地摄入附件。
- 通过 `channels.imessage.mediaMaxMb` 限制媒体大小。

## 限制

- 发出的文本将被分割为 `channels.imessage.textChunkLimit`（默认 4000）。
- 可选按换行符分割：设置 `channels.imessage.chunkMode="newline"` 以在长度分割前按空白行（段落边界）分割。
- 媒体上传受限于 `channels.imessage.mediaMaxMb`（默认 16）。

## 地址 / 交付目标

优先使用 `chat_id` 以获得稳定的路由：

- `chat_id:123`（推荐）
- `chat_guid:...`
- `chat_identifier:...`
- 直接处理：`imessage:+1555` / `sms:+1555` / `user@example.com`

列出聊天：

```
imsg chats --limit 20
```

## 配置参考（iMessage）

完整配置：[配置](/gateway/configuration)

提供者选项：

- `channels.imessage.enabled`：启用/禁用通道启动。
- `channels.imessage.cliPath`：`imsg` 的路径。
- `channels.imessage.dbPath`：Messages 数据库路径。
- `channels.imessage.remoteHost`：当 `cliPath` 指向远程 Mac 时，用于 SCP 附件传输的 SSH 主机（例如 `user@gateway-host`）。如果未设置，将从 SSH 包装器自动检测。
- `channels.imessage.service`：`imessage | sms | auto`。
- `channels.imessage.region`：短信区域。
- `channels.imessage.dmPolicy`：`pairing | allowlist | open | disabled`（默认：`pairing`）。
- `channels.imessage.allowFrom`：单聊允许列表（处理、电子邮件、E.164 数字或 `chat_id:*`）。`open` 需要 `"*"`。iMessage 没有用户名；使用处理或聊天目标。
- `channels.imessage.groupPolicy`：`open | allowlist | disabled`（默认：`allowlist`）。
- `channels.imessage.groupAllowFrom`：群组发送者允许列表。
- `channels.imessage.historyLimit` / `channels.imessage.accounts.*.historyLimit`：最大包含的群组消息作为上下文（0 禁用）。
- `channels.imessage.dmHistoryLimit`：用户回合中的单聊历史记录限制。用户特定覆盖：`channels.imessage.dms["<handle>"].historyLimit`。
- `channels.imessage.groups`：每组默认值 + 允许列表（使用 `"*"` 表示全局默认值）。
- `channels.imessage.includeAttachments`：将附件摄入上下文。
- `channels.imessage.mediaMaxMb`：入站/出站媒体限制（MB）。
- `channels.imessage.textChunkLimit`：出站分块大小（字符）。
- `channels.imessage.chunkMode`：`length`（